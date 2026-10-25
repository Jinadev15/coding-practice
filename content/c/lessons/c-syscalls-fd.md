# System Calls and File Descriptors

Everything a C program does to the outside world (reading files, writing to the terminal, talking over the network, starting processes) goes through **system calls**: controlled entry points into the operating system kernel. On Unix-like systems (Linux, macOS, the RTOS-like POSIX layers on robots), most I/O is expressed with **file descriptors**: small integers that name open files, pipes, sockets, terminals and devices. `stdio` (`fopen`, `printf`) is a buffered library built *on top of* these calls. This lesson goes one level down, to `open`, `read`, `write`, `close`, `lseek`, `dup2`, `fcntl` and `stat`, with the error handling and partial-I/O rules that real systems code needs.

## 1. User space, kernel space, and the cost of a syscall

A system call switches the CPU from user mode to kernel mode, runs the kernel's handler, and switches back. That costs roughly 50–500 ns, far more than a function call, which is why `stdio` buffers and why you read in large blocks. Tools:
- `strace ./prog` shows every syscall a program makes, with arguments and return values. It's invaluable for debugging.
- `ltrace` shows library calls.

POSIX calls need declarations that strict ISO C modes hide. Put this **before any `#include`**:

```c
#define _POSIX_C_SOURCE 200809L    /* or _GNU_SOURCE for Linux extensions */
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <errno.h>
```

## 2. File descriptors

| fd | Meaning | stdio equivalent |
|---|---|---|
| 0 | standard input | `stdin` |
| 1 | standard output | `stdout` |
| 2 | standard error | `stderr` |

The kernel keeps a per-process **descriptor table**: fd → an *open file description* (current offset, status flags) → the file itself (the inode). `open` returns the **lowest unused** fd number, and that rule is what makes redirection with `close` + `open` (or `dup2`) work.

```c
int fd = open("log.txt", O_WRONLY | O_CREAT | O_APPEND, 0644);   /* mode only matters with O_CREAT */
if (fd < 0) { perror("open"); return 1; }
const char msg[] = "robot started\n";
ssize_t n = write(fd, msg, sizeof msg - 1);
if (n < 0) perror("write");
close(fd);
```

| Flag | Meaning |
|---|---|
| `O_RDONLY`, `O_WRONLY`, `O_RDWR` | access mode (exactly one) |
| `O_CREAT` | create if missing (requires the mode argument) |
| `O_EXCL` | with O_CREAT: fail if it exists (atomic "create new"; lock files) |
| `O_TRUNC` | truncate to length 0 |
| `O_APPEND` | every write goes to the end, atomically (safe for concurrent loggers) |
| `O_CLOEXEC` | close automatically on `exec` (avoids leaking fds to children) |
| `O_NONBLOCK` | non-blocking I/O (pipes, sockets, devices) |

## 3. `read` and `write` return less than you asked

```c
ssize_t read(int fd, void *buf, size_t count);    /* >0 bytes read, 0 = end of file, -1 = error (errno) */
ssize_t write(int fd, const void *buf, size_t count);
```

> [!KEY]
> A **short read** or **short write** is normal, not an error. Pipes, sockets, terminals and signals can all return fewer bytes than requested. Correct code loops until everything is transferred, and retries when interrupted by a signal (`EINTR`):

```c
ssize_t write_all(int fd, const void *buf, size_t len) {
    const char *p = buf;
    size_t left = len;
    while (left > 0) {
        ssize_t n = write(fd, p, left);
        if (n < 0) {
            if (errno == EINTR) continue;        /* interrupted before writing anything: retry */
            return -1;
        }
        p += n;
        left -= (size_t)n;
    }
    return (ssize_t)len;
}

ssize_t read_full(int fd, void *buf, size_t len) {   /* read exactly len bytes unless EOF comes first */
    char *p = buf;
    size_t got = 0;
    while (got < len) {
        ssize_t n = read(fd, p + got, len - got);
        if (n == 0) break;                           /* EOF */
        if (n < 0) { if (errno == EINTR) continue; return -1; }
        got += (size_t)n;
    }
    return (ssize_t)got;
}
```

## 4. Errors: `errno`, `perror`, `strerror`

System calls return −1 (or NULL) on failure and set the thread-local `errno`:

| errno | Meaning |
|---|---|
| `ENOENT` | no such file or directory |
| `EACCES` | permission denied |
| `EEXIST` | file exists (`O_CREAT \| O_EXCL`) |
| `EINTR` | interrupted by a signal; usually retry |
| `EAGAIN` / `EWOULDBLOCK` | non-blocking operation would block |
| `EBADF` | bad file descriptor |
| `EPIPE` | write to a pipe or socket with no reader (also raises SIGPIPE) |
| `EMFILE` | too many open files (descriptor leak!) |

Check `errno` **only** after a call reports failure, since successful calls may leave garbage in it. Use `strerror(errno)` or `perror("context")` for messages.

## 5. Offsets: `lseek` and `pread`/`pwrite`

```c
off_t size = lseek(fd, 0, SEEK_END);     /* move to the end: returns the file size */
lseek(fd, 0, SEEK_SET);                  /* rewind */
pread(fd, buf, 512, 4096);               /* read 512 bytes at offset 4096 WITHOUT moving the offset */
```

`pread`/`pwrite` are thread-safe for concurrent positioned I/O on one fd (databases use them). Pipes and sockets aren't seekable (`lseek` fails with `ESPIPE`).

## 6. Duplicating descriptors: `dup`, `dup2` and redirection

```c
int saved = dup(STDOUT_FILENO);                   /* keep a copy of the terminal */
int fd = open("out.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
dup2(fd, STDOUT_FILENO);                          /* fd 1 now refers to out.txt */
close(fd);                                        /* fd 1 keeps the file open */
printf("goes to the file\n");
fflush(stdout);                                   /* flush stdio's buffer BEFORE switching back */
dup2(saved, STDOUT_FILENO);                       /* restore */
close(saved);
```

This is exactly how a shell implements `cmd > file`, `2>&1` and pipelines (next lessons). Duplicated descriptors share **one** open file description: the same offset and the same flags.

> [!WARNING]
> Mixing `stdio` with raw `write` on the same fd reorders output, because `printf` data sits in a user-space buffer until it's flushed, while `write` goes to the kernel immediately. Call `fflush` before switching levels or redirecting.

## 7. Metadata and control: `stat`, `fstat`, `fcntl`

```c
struct stat st;
if (fstat(fd, &st) == 0)
    printf("size=%lld mode=%o regular=%d\n", (long long)st.st_size, st.st_mode & 0777, S_ISREG(st.st_mode));

int flags = fcntl(fd, F_GETFL);
fcntl(fd, F_SETFL, flags | O_NONBLOCK);           /* make an existing fd non-blocking */
fcntl(fd, F_SETFD, FD_CLOEXEC);                   /* close-on-exec */
```

## 8. stdio vs raw syscalls

| | `stdio` (`FILE*`) | raw fd |
|---|---|---|
| buffering | yes (full, line or none) | no |
| formatting | `printf`/`scanf` | none |
| portability | ISO C | POSIX |
| control | limited | full (flags, non-blocking, sockets, `poll`) |
| bridging | `fileno(fp)` → fd | `fdopen(fd, "r")` → FILE* |

Use stdio for text files and formatting, and raw descriptors for pipes, sockets, devices, or precise control. On embedded Linux robots, device files (`/dev/ttyUSB0` for a serial motor controller, `/dev/i2c-1`, GPIO character devices) are opened and read with these same calls.

## 9. Exam-ready answers

> [!EXAM]
> **File descriptors.** A file descriptor is a small non-negative integer that indexes a process's table of open files, pipes, sockets and devices; descriptors 0, 1 and 2 are standard input, output and error. Each entry refers to an open file description holding the file offset and status flags, which is shared after `dup`, `dup2` or `fork`. The system calls `open`, `read`, `write`, `lseek` and `close` operate on descriptors; `read` and `write` may transfer fewer bytes than requested and may fail with `EINTR`, so robust code loops until all data has been transferred. `dup2(old, new)` makes `new` refer to the same open file as `old`, which shells use to implement I/O redirection.

## 10. Cheat sheet

| Need | Call |
|---|---|
| open/create | `open(path, O_WRONLY \| O_CREAT \| O_TRUNC, 0644)` |
| append safely | `O_APPEND` |
| create only if new | `O_CREAT \| O_EXCL` |
| read/write everything | loop on short counts and `EINTR` |
| file size | `fstat(fd, &st); st.st_size` or `lseek(fd, 0, SEEK_END)` |
| positioned I/O | `pread`/`pwrite` |
| redirect | `dup2(fd, STDOUT_FILENO)` (flush stdio first) |
| don't leak to children | `O_CLOEXEC` |
| debug | `strace -f ./prog` |

> [!INTERVIEW]
> **"Why can `write(fd, buf, 1000)` return 300, and what do you do?"** The kernel may accept only part of the data: a pipe or socket buffer is nearly full, a signal arrived after some bytes were copied, or the disk quota was reached. It isn't an error. Loop, advancing the buffer pointer by the returned count, until all 1000 bytes are written, retrying on `EINTR` and treating −1 with other errno values as failure. The same applies to `read`, where 0 additionally means end of file.
