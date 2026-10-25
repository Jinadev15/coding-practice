---
id: c-fd-utils
title: Robust File-Descriptor Utilities
difficulty: Hard
order: 1
tags: system calls, read, write, short I/O, dup2, lseek, pread
time_limit: 3
---
## Statement
Write the low-level I/O helpers every systems project ends up needing. Keep the first line of the starter (`#define _POSIX_C_SOURCE 200809L`), which exposes the POSIX declarations under `-std=c17`.

```c
ssize_t write_all(int fd, const void *buf, size_t len);   /* loop over short writes and EINTR; len or -1 */
ssize_t read_full(int fd, void *buf, size_t len);         /* read until len bytes or EOF; count or -1 */
long copy_fd(int in, int out);                            /* copy everything until EOF; total or -1 */
long capture_stdout(void (*fn)(void), char *buf, size_t cap);
    /* run fn() with stdout (fd 1) redirected into a temporary file or pipe, restore stdout,
       copy up to cap-1 captured bytes into buf (NUL-terminated); return the TOTAL captured length.
       fn may mix printf and write(1, ...): capture ALL of it. Raw writes reach the file at once, while printf
       bytes arrive when stdio flushes, exactly as with a real shell redirect. */
int tail_lines(const char *path, int n, char *out, size_t cap);
    /* the last n lines of the file (a trailing newline doesn't start an extra empty line),
       copied into out (NUL-terminated, truncated to cap-1); return the number of lines produced, -1 on error.
       Read backwards with lseek/pread in blocks: files may be far larger than memory. */
```

The driver pushes megabytes through pipes whose reader consumes data in small, delayed chunks (so reads come back short), captures mixed `printf`/`write` output, and tails files.

## Starter
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

ssize_t write_all(int fd, const void *buf, size_t len) { return write(fd, buf, len); }
ssize_t read_full(int fd, void *buf, size_t len) { return read(fd, buf, len); }
long copy_fd(int in, int out) {
    char b[4096];
    ssize_t n = read(in, b, sizeof b);
    if (n > 0) write(out, b, (size_t)n);
    return n;
}
long capture_stdout(void (*fn)(void), char *buf, size_t cap) { fn(); if (cap) buf[0] = '\0'; return 0; }
int tail_lines(const char *path, int n, char *out, size_t cap) { (void)path; (void)n; if (cap) out[0] = '\0'; return 0; }
```

## Driver
```c
#include <sys/wait.h>
#include <time.h>

static void pause_us(long us) { struct timespec ts = { 0, us * 1000 }; nanosleep(&ts, NULL); }

static void producer_mixed(void) {
    printf("alpha ");                   /* buffered */
    write(STDOUT_FILENO, "beta ", 5);   /* unbuffered */
    printf("gamma %d", 42);
    for (int i = 0; i < 2000; i++) printf("%c", 'a' + i % 26);
    printf("\nend\n");
}
static void producer_empty(void) { }

int main(void) {
    char cmd[32];
    while (scanf("%31s", cmd) == 1) {
        if (!strcmp(cmd, "pipe")) {                  /* write_all + read_full through a slow reader */
            size_t total; if (scanf("%zu", &total) != 1) return 1;
            int p[2]; if (pipe(p) < 0) return 1;
            char *data = malloc(total), *back = malloc(total);
            for (size_t i = 0; i < total; i++) data[i] = (char)(i * 131 + 7);
            pid_t pid = fork();
            if (pid == 0) {                          /* child: writes everything at once */
                close(p[0]);
                ssize_t w = write_all(p[1], data, total);
                _exit(w == (ssize_t)total ? 0 : 3);
            }
            close(p[1]);
            size_t got = 0;
            while (got < total) {                    /* parent: read_full in odd-sized chunks */
                size_t want = total - got < 7777 ? total - got : 7777;
                ssize_t r = read_full(p[0], back + got, want);
                if (r <= 0) break;
                got += (size_t)r;
                if (got % 3 == 0) pause_us(50);
            }
            char extra;
            ssize_t eof = read_full(p[0], &extra, 1);
            int st; waitpid(pid, &st, 0);
            close(p[0]);
            printf("pipe %zu: received=%zu identical=%d writer_ok=%d eof=%zd\n", total, got,
                   got == total && !memcmp(data, back, total), WIFEXITED(st) && WEXITSTATUS(st) == 0, eof);
            free(data); free(back);
        } else if (!strcmp(cmd, "copy")) {           /* copy_fd from a dribbling pipe into a file */
            size_t total; if (scanf("%zu", &total) != 1) return 1;
            int p[2]; if (pipe(p) < 0) return 1;
            pid_t pid = fork();
            if (pid == 0) {
                close(p[0]);
                char chunk[1000];
                for (size_t sent = 0; sent < total; ) {
                    size_t k = total - sent < 997 ? total - sent : 997;
                    for (size_t i = 0; i < k; i++) chunk[i] = (char)('A' + (sent + i) % 26);
                    if (write(p[1], chunk, k) < 0) _exit(2);
                    sent += k;
                    if (sent % 9970 == 0) pause_us(100);
                }
                _exit(0);
            }
            close(p[1]);
            int out = open("copy.out", O_WRONLY | O_CREAT | O_TRUNC, 0644);
            long n = copy_fd(p[0], out);
            close(out); close(p[0]); waitpid(pid, NULL, 0);
            FILE *f = fopen("copy.out", "rb");
            long sz = 0, bad = 0; int c;
            while ((c = fgetc(f)) != EOF) { if (c != 'A' + sz % 26) bad++; sz++; }
            fclose(f);
            printf("copy %zu: returned=%ld file_size=%ld mismatches=%ld\n", total, n, sz, bad);
        } else if (!strcmp(cmd, "capture")) {
            char buf[4096];
            long n = capture_stdout(producer_mixed, buf, sizeof buf);
            size_t L = strlen(buf);
            printf("capture: total=%ld head=\"%.20s\" tail=\"%s\" stored=%zu\n", n, buf,
                   L >= 5 ? buf + L - 5 : buf, L);
            char small[16];
            n = capture_stdout(producer_mixed, small, sizeof small);
            printf("capture small: total=%ld stored=\"%s\"\n", n, small);
            n = capture_stdout(producer_empty, small, sizeof small);
            printf("capture empty: total=%ld stored=\"%s\"\n", n, small);
            printf("stdout still works\n");
        } else if (!strcmp(cmd, "tail")) {
            int lines, n, trailing; if (scanf("%d %d %d", &lines, &n, &trailing) != 3) return 1;
            FILE *f = fopen("tail.txt", "w");
            for (int i = 1; i <= lines; i++) fprintf(f, "line %d%s", i, (i < lines || trailing) ? "\n" : "");
            fclose(f);
            char out[256];
            int got = tail_lines("tail.txt", n, out, sizeof out);
            for (char *p = out; *p; p++) if (*p == '\n') *p = '|';
            printf("tail %d of %d (trailing=%d): count=%d text=\"%s\"\n", n, lines, trailing, got, out);
        } else if (!strcmp(cmd, "tailmissing")) {
            char out[16];
            printf("tail missing: %d\n", tail_lines("no_such_file.txt", 3, out, sizeof out));
        }
        fflush(stdout);
    }
    return 0;
}
```

## Tests
=== sample
pipe 100000
capture
tail 10 3 1
---
pipe 100000: received=100000 identical=1 writer_ok=1 eof=0
capture: total=2024 head="beta alpha gamma 42a" tail="
end
" stored=2024
capture small: total=2024 stored="beta alpha gamm"
capture empty: total=0 stored=""
stdout still works
tail 3 of 10 (trailing=1): count=3 text="line 8|line 9|line 10"
=== hidden
pipe 1
pipe 3000000
copy 0
copy 123457
---
pipe 1: received=1 identical=1 writer_ok=1 eof=0
pipe 3000000: received=3000000 identical=1 writer_ok=1 eof=0
copy 0: returned=0 file_size=0 mismatches=0
copy 123457: returned=123457 file_size=123457 mismatches=0
=== hidden
copy 5000000
tail 1 1 0
tail 5 10 1
tail 5 0 1
tail 200000 4 0
tail 3 2 0
tailmissing
---
copy 5000000: returned=5000000 file_size=5000000 mismatches=0
tail 1 of 1 (trailing=0): count=1 text="line 1"
tail 10 of 5 (trailing=1): count=5 text="line 1|line 2|line 3|line 4|line 5"
tail 0 of 5 (trailing=1): count=0 text=""
tail 4 of 200000 (trailing=0): count=4 text="line 199997|line 199998|line 199999|line 200000"
tail 2 of 3 (trailing=0): count=2 text="line 2|line 3"
tail missing: -1

## Hints
- `write_all`/`read_full`: loop and advance the pointer. Retry on `EINTR`. For `read_full`, stop at EOF (0) and return what you have.
- `capture_stdout`: `fflush(stdout)` first, `saved = dup(1)`, then open a temp file (`O_RDWR | O_CREAT | O_TRUNC`) and `dup2` it onto fd 1. Run `fn()`, `fflush(stdout)` again (printf's buffer!), restore with `dup2(saved, 1)`, then `lseek` the temp file to 0 and read it back. A file avoids the deadlock a pipe causes when the output exceeds the pipe buffer.
- `tail_lines`: get the size with `lseek(fd, 0, SEEK_END)`. Read 4096-byte blocks backwards with `pread`, counting `'\n'`s (ignoring a final trailing newline) until you've passed n of them, then copy forward from that position.

## Solution
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

ssize_t write_all(int fd, const void *buf, size_t len) {
    const char *p = buf;
    size_t left = len;
    while (left > 0) {
        ssize_t n = write(fd, p, left);
        if (n < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        p += n;
        left -= (size_t)n;
    }
    return (ssize_t)len;
}

ssize_t read_full(int fd, void *buf, size_t len) {
    char *p = buf;
    size_t got = 0;
    while (got < len) {
        ssize_t n = read(fd, p + got, len - got);
        if (n == 0) break;
        if (n < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        got += (size_t)n;
    }
    return (ssize_t)got;
}

long copy_fd(int in, int out) {
    char b[65536];
    long total = 0;
    for (;;) {
        ssize_t n = read(in, b, sizeof b);
        if (n == 0) return total;
        if (n < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        if (write_all(out, b, (size_t)n) < 0) return -1;
        total += n;
    }
}

long capture_stdout(void (*fn)(void), char *buf, size_t cap) {
    fflush(stdout);
    int saved = dup(STDOUT_FILENO);
    int tmp = open("capture.tmp", O_RDWR | O_CREAT | O_TRUNC, 0600);
    if (saved < 0 || tmp < 0) return -1;
    dup2(tmp, STDOUT_FILENO);
    fn();
    fflush(stdout);                               /* push printf's buffered bytes into the file */
    dup2(saved, STDOUT_FILENO);
    close(saved);
    off_t total = lseek(tmp, 0, SEEK_END);
    lseek(tmp, 0, SEEK_SET);
    size_t want = cap ? cap - 1 : 0;
    if ((size_t)total < want) want = (size_t)total;
    ssize_t n = read_full(tmp, buf, want);
    if (cap) buf[n > 0 ? n : 0] = '\0';
    close(tmp);
    unlink("capture.tmp");
    return (long)total;
}

int tail_lines(const char *path, int n, char *out, size_t cap) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) return -1;
    off_t size = lseek(fd, 0, SEEK_END);
    if (cap) out[0] = '\0';
    if (n <= 0 || size <= 0) { close(fd); return 0; }
    char last;
    pread(fd, &last, 1, size - 1);
    off_t end = last == '\n' ? size - 1 : size;   /* ignore the final newline */
    off_t pos = end, start = 0;
    int newlines = 0;
    char blk[4096];
    while (pos > 0) {                              /* scan backwards block by block */
        off_t from = pos >= (off_t)sizeof blk ? pos - (off_t)sizeof blk : 0;
        ssize_t got = pread(fd, blk, (size_t)(pos - from), from);
        if (got <= 0) break;
        for (ssize_t i = got - 1; i >= 0; i--) {
            if (blk[i] == '\n' && ++newlines == n) { start = from + i + 1; goto found; }
        }
        pos = from;
    }
    start = 0;
found:;
    int lines = 1;
    size_t written = 0;
    char c;
    for (off_t p = start; p < end; p++) {
        if (pread(fd, &c, 1, p) != 1) break;
        if (c == '\n') lines++;
        if (written + 1 < cap) out[written++] = c;
    }
    if (cap) out[written] = '\0';
    close(fd);
    return lines;
}
```

- **Short I/O is the norm** on pipes and sockets. The writer child dumps megabytes at once while the parent reads in odd-sized chunks, so `read` keeps returning fewer bytes than asked. Only code that loops gets every byte, and in order.
- **Capturing stdout** needs `fflush` on both sides of the redirection. Otherwise `printf` output still sitting in stdio's buffer lands in the wrong place, or after the raw `write` output. A temporary file (rather than a pipe) avoids deadlock when `fn` prints more than a pipe buffer holds.
- **`tail` reads backwards** with `pread`, touching only the end of the file, so it's O(size of the last n lines) whatever the file size. That's how `tail -n` works on multi-gigabyte robot logs.
