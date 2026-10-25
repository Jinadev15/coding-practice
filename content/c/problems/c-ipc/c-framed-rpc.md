---
id: c-framed-rpc
title: Length-Prefixed RPC Between Processes
difficulty: Hard
order: 1
tags: IPC, socketpair, fork, framing, partial reads, protocol design
time_limit: 4
---
## Statement
A perception process and a planner talk over a Unix-domain `socketpair`. Since a stream socket has no message boundaries, implement **length-prefixed framing** and a small request/response server:

```c
int  send_msg(int fd, const void *data, uint32_t len);
    /* 4-byte BIG-ENDIAN length, then the payload. 0 on success, -1 on error. Loop over short writes. */
long recv_msg(int fd, void *buf, uint32_t cap);
    /* payload length; 0 = clean EOF before a header; -1 on error, a truncated message, or len > cap
       (when len > cap, return -1 without reading the payload). Loop over short reads. */
void serve(int fd);
    /* child-side server loop until EOF or "quit". Requests (payload text, not NUL-terminated):
       "upper <text>"  -> the text uppercased
       "sum <ints...>" -> decimal sum (as long long)
       "rev <text>"    -> the text reversed
       "quit"          -> reply "bye" and return
       anything else   -> "error: unknown command" */
```

The parent side (the driver) forks a child running your `serve`, sends requests with your `send_msg`, and reads replies with `recv_msg`. Payloads go up to 4 MB, far beyond the socket buffer, so partial reads and writes are guaranteed. The driver also sends one hand-made frame **byte by byte** with pauses, and one frame claiming 2 GB.

## Starter
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h>
#include <unistd.h>
#include <errno.h>

int send_msg(int fd, const void *data, uint32_t len) {
    if (write(fd, &len, 4) != 4) return -1;          /* host byte order and no short-write loop */
    return write(fd, data, len) == (ssize_t)len ? 0 : -1;
}
long recv_msg(int fd, void *buf, uint32_t cap) {
    uint32_t len;
    if (read(fd, &len, 4) != 4) return 0;
    (void)cap;
    return read(fd, buf, len);
}
void serve(int fd) { (void)fd; }
```

## Driver
```c
#include <sys/socket.h>
#include <sys/wait.h>
#include <time.h>

static char reply[5 << 20];

static void request(int fd, const char *text, size_t len) {
    if (send_msg(fd, text, (uint32_t)len) != 0) { printf("send failed\n"); return; }
    long n = recv_msg(fd, reply, sizeof reply);
    if (n < 0) { printf("recv error\n"); return; }
    if (n > 60) printf("reply (%ld bytes): %.20s...%.20s\n", n, reply, reply + n - 20);
    else printf("reply: %.*s\n", (int)n, reply);
}

int main(void) {
    char cmd[64];
    int sv[2];
    if (socketpair(AF_UNIX, SOCK_STREAM, 0, sv) < 0) return 1;
    fflush(stdout);
    pid_t kid = fork();
    if (kid == 0) { close(sv[0]); serve(sv[1]); close(sv[1]); _exit(0); }
    close(sv[1]);
    int fd = sv[0];
    while (scanf("%63s", cmd) == 1) {
        if (!strcmp(cmd, "req")) {
            char line[4096];
            if (!fgets(line, sizeof line, stdin)) break;
            line[strcspn(line, "\n")] = '\0';
            request(fd, line + 1, strlen(line + 1));
        } else if (!strcmp(cmd, "big")) {
            size_t n; if (scanf("%zu", &n) != 1) return 1;
            char *b = malloc(n + 6);
            memcpy(b, "upper ", 6);
            for (size_t i = 0; i < n; i++) b[6 + i] = (char)('a' + i % 26);
            request(fd, b, n + 6);
            free(b);
        } else if (!strcmp(cmd, "dribble")) {          /* a frame written one byte at a time */
            const char *msg = "rev slowly";
            uint32_t len = (uint32_t)strlen(msg);
            unsigned char frame[64] = { len >> 24, len >> 16, len >> 8, len };
            memcpy(frame + 4, msg, len);
            struct timespec ts = {0, 5000000};
            for (uint32_t i = 0; i < len + 4; i++) { write(fd, frame + i, 1); nanosleep(&ts, NULL); }
            long n = recv_msg(fd, reply, sizeof reply);
            printf("dribble reply: %.*s\n", (int)(n > 0 ? n : 0), reply);
        } else if (!strcmp(cmd, "oversize")) {         /* local check of recv_msg's cap handling */
            int p[2]; socketpair(AF_UNIX, SOCK_STREAM, 0, p);
            unsigned char hdr[4] = {0x80, 0, 0, 0};    /* 2 GB claimed */
            write(p[1], hdr, 4);
            char small[16];
            long r = recv_msg(p[0], small, sizeof small);
            close(p[1]);
            long e = recv_msg(p[0], small, sizeof small);
            close(p[0]);
            printf("oversize: recv=%ld then=%ld\n", r, e);
        } else if (!strcmp(cmd, "truncated")) {
            int p[2]; socketpair(AF_UNIX, SOCK_STREAM, 0, p);
            unsigned char hdr[4] = {0, 0, 0, 10};
            write(p[1], hdr, 4); write(p[1], "abc", 3);
            close(p[1]);
            char small[16];
            printf("truncated: recv=%ld\n", recv_msg(p[0], small, sizeof small));
            close(p[0]);
        }
        fflush(stdout);
    }
    close(fd);
    int st; waitpid(kid, &st, 0);
    printf("server exited: %d\n", WIFEXITED(st) ? WEXITSTATUS(st) : -1);
    return 0;
}
```

## Tests
=== sample
req upper hello robot
req sum 10 20 -5
req rev abc
req quit
---
reply: HELLO ROBOT
reply: 25
reply: cba
reply: bye
server exited: 0
=== hidden
req upper
req sum
req sum 9223372036854775000 7
req frobnicate now
req rev a
dribble
big 4000000
oversize
truncated
req sum 1 2 3 4 5 6 7 8 9 10
req quit
---
reply: 
reply: 0
reply: 9223372036854775007
reply: error: unknown command
reply: a
dribble reply: ylwols
reply (4000000 bytes): ABCDEFGHIJKLMNOPQRST...KLMNOPQRSTUVWXYZABCD
oversize: recv=-1 then=0
truncated: recv=-1
reply: 55
reply: bye
server exited: 0

## Hints
- `send_msg`: build the header as `{len >> 24, len >> 16, len >> 8, len}` bytes, then `write_all` the header and the payload. Write the loop helpers yourself (`write_all` / `read_full`) with `EINTR` handling.
- `recv_msg`: `read_full` 4 bytes. If 0 bytes arrived, it's EOF (return 0); if 1–3 arrived, it's truncated (return −1). Decode big-endian. If `len > cap`, return −1. Then `read_full` exactly `len` bytes.
- `serve`: allocate a buffer (say 5 MB) on the heap. Loop on `recv_msg`. Match commands with `strncmp`, NUL-terminating a copy of the payload for parsing. `sum` with `strtoll` in a loop, and `"upper"` alone (no text) replies with an empty payload.

## Solution
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h>
#include <unistd.h>
#include <errno.h>

static int write_all(int fd, const void *buf, size_t len) {
    const char *p = buf;
    while (len) {
        ssize_t n = write(fd, p, len);
        if (n < 0) { if (errno == EINTR) continue; return -1; }
        p += n; len -= (size_t)n;
    }
    return 0;
}

static ssize_t read_full(int fd, void *buf, size_t len) {
    char *p = buf;
    size_t got = 0;
    while (got < len) {
        ssize_t n = read(fd, p + got, len - got);
        if (n == 0) break;
        if (n < 0) { if (errno == EINTR) continue; return -1; }
        got += (size_t)n;
    }
    return (ssize_t)got;
}

int send_msg(int fd, const void *data, uint32_t len) {
    unsigned char hdr[4] = { (unsigned char)(len >> 24), (unsigned char)(len >> 16),
                             (unsigned char)(len >> 8), (unsigned char)len };
    if (write_all(fd, hdr, 4) < 0) return -1;
    return write_all(fd, data, len);
}

long recv_msg(int fd, void *buf, uint32_t cap) {
    unsigned char hdr[4];
    ssize_t n = read_full(fd, hdr, 4);
    if (n == 0) return 0;                       /* clean EOF between messages */
    if (n != 4) return -1;                      /* truncated header */
    uint32_t len = (uint32_t)hdr[0] << 24 | (uint32_t)hdr[1] << 16 | (uint32_t)hdr[2] << 8 | hdr[3];
    if (len > cap) return -1;                   /* never trust the peer's length */
    return read_full(fd, buf, len) == (ssize_t)len ? (long)len : -1;
}

static void reply_str(int fd, const char *s) { send_msg(fd, s, (uint32_t)strlen(s)); }

void serve(int fd) {
    const uint32_t CAP = 5u << 20;
    char *in = malloc(CAP + 1), *out = malloc(CAP + 1);
    long n;
    while ((n = recv_msg(fd, in, CAP)) > 0) {
        in[n] = '\0';
        if (!strcmp(in, "quit")) { reply_str(fd, "bye"); break; }
        if (!strncmp(in, "upper", 5) && (in[5] == ' ' || in[5] == '\0')) {
            const char *t = in[5] ? in + 6 : in + 5;
            size_t L = strlen(t);
            for (size_t i = 0; i < L; i++) out[i] = (char)toupper((unsigned char)t[i]);
            send_msg(fd, out, (uint32_t)L);
        } else if (!strncmp(in, "rev ", 4)) {
            const char *t = in + 4;
            size_t L = strlen(t);
            for (size_t i = 0; i < L; i++) out[i] = t[L - 1 - i];
            send_msg(fd, out, (uint32_t)L);
        } else if (!strncmp(in, "sum", 3) && (in[3] == ' ' || in[3] == '\0')) {
            long long total = 0;
            char *p = in + 3, *end;
            for (;;) {
                long long v = strtoll(p, &end, 10);
                if (end == p) break;
                total += v;
                p = end;
            }
            char num[32];
            snprintf(num, sizeof num, "%lld", total);
            reply_str(fd, num);
        } else {
            reply_str(fd, "error: unknown command");
        }
    }
    free(in);
    free(out);
}
```

- **Framing** gives a byte stream message boundaries. The header is a fixed 4 bytes in big-endian order, so both sides agree regardless of CPU endianness, and the receiver always knows exactly how many bytes to wait for. The byte-by-byte `dribble` and the 4 MB message prove the loops work: `read` returns whatever has arrived, sometimes 1 byte, sometimes 200 KB.
- **Validation before allocation**: a peer claiming a 2 GB message is rejected *before* any payload is read. Checking lengths from outside the process is the first line of defence against memory exhaustion and buffer overflows.
- **EOF semantics**: a clean EOF *between* frames returns 0 (the peer closed normally), while EOF *inside* a frame returns −1 (the message was truncated). The server loop uses this to exit when the parent closes its end.
