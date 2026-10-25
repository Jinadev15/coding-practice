# Inter-Process Communication

Separate processes don't share memory by default, which is good for isolation and fault containment. A crashing perception node shouldn't take the motor controller down with it. But processes still need to exchange data. Unix offers a toolbox of **IPC** mechanisms, each with different trade-offs in speed, structure and complexity:
- pipes and FIFOs
- Unix-domain sockets and `socketpair`
- shared memory (`mmap`, POSIX `shm_open`)
- message queues
- semaphores
- signals (for notification only)

This lesson explains when to use each, and how to frame messages over byte streams correctly.

## 1. The landscape

| Mechanism | Data model | Related processes only? | Speed | Typical use |
|---|---|---|---|---|
| anonymous pipe (`pipe`) | byte stream, one direction | yes (inherited) | fast | shell pipelines, parent ↔ child |
| FIFO (`mkfifo`) | byte stream | no (named in the filesystem) | fast | simple local services |
| `socketpair` / Unix-domain socket | stream or datagram, bidirectional, can pass fds | socketpair: yes; named: no | fast | local daemons (X11, Docker, systemd), ROS 2 local transport |
| shared memory (`mmap`, `shm_open`) | raw memory | no | fastest (zero copy) | images, point clouds, large buffers |
| POSIX message queue (`mq_open`) | discrete messages with priorities | no | medium | small commands |
| TCP/UDP sockets | stream / datagrams | no (even across machines) | network | distributed systems |
| signals | a number only | no | notification | events, shutdown |

## 2. Pipes in depth

```c
int p[2];
if (pipe(p) < 0) { perror("pipe"); exit(1); }
pid_t pid = fork();
if (pid == 0) {                              /* child: producer */
    close(p[0]);
    const char msg[] = "pose 1.0 2.0 0.5\n";
    write_all(p[1], msg, sizeof msg - 1);
    close(p[1]);                             /* EOF for the reader */
    _exit(0);
}
close(p[1]);                                 /* parent: consumer */
char buf[256];
ssize_t n;
while ((n = read(p[0], buf, sizeof buf)) > 0) fwrite(buf, 1, (size_t)n, stdout);
close(p[0]);
waitpid(pid, NULL, 0);
```

Key facts:
- The kernel buffer is finite (64 KB by default on Linux). A writer blocks when it's full, which gives natural backpressure.
- Writes of ≤ `PIPE_BUF` (4096 on Linux) bytes are **atomic**: concurrent writers' small messages don't interleave.
- Reading returns 0 (EOF) only when **all** write ends are closed.
- Writing to a pipe with no readers raises `SIGPIPE`, or fails with `EPIPE` if the signal is ignored.

## 3. Framing: streams have no message boundaries

Pipes and stream sockets deliver a **byte stream**. Two `write`s of 10 bytes may arrive as one `read` of 20, or as reads of 3 and 17. You must impose message boundaries yourself:

| Framing | Pros | Cons |
|---|---|---|
| delimiter (`\n`) | human readable, simple | the payload can't contain the delimiter (or needs escaping) |
| length prefix (4-byte big-endian length + payload) | binary-safe, efficient | must handle partial headers |
| fixed-size records | trivial | wasteful or inflexible |
| self-describing (protobuf, CBOR, msgpack) | schema evolution | needs a library |

```c
/* length-prefixed send/receive over any stream fd */
int send_msg(int fd, const void *data, uint32_t len) {
    unsigned char hdr[4] = { len >> 24, len >> 16, len >> 8, len };   /* big-endian: portable */
    if (write_all(fd, hdr, 4) < 0) return -1;
    return write_all(fd, data, len) < 0 ? -1 : 0;
}

/* returns the payload length, 0 on clean EOF, -1 on error or truncation */
long recv_msg(int fd, void *buf, uint32_t cap) {
    unsigned char hdr[4];
    ssize_t n = read_full(fd, hdr, 4);
    if (n == 0) return 0;
    if (n != 4) return -1;
    uint32_t len = (uint32_t)hdr[0] << 24 | (uint32_t)hdr[1] << 16 | (uint32_t)hdr[2] << 8 | hdr[3];
    if (len > cap) return -1;                         /* never trust a length from the wire blindly */
    return read_full(fd, buf, len) == (ssize_t)len ? (long)len : -1;
}
```

> [!DANGER]
> Validate lengths received from another process or the network before using them. An unchecked length is the classic buffer overflow and memory-exhaustion vulnerability.

## 4. `socketpair`: bidirectional parent ↔ child

```c
int sv[2];
socketpair(AF_UNIX, SOCK_STREAM, 0, sv);     /* two connected endpoints, both readable and writable */
if (fork() == 0) { close(sv[0]); /* child talks on sv[1] */ }
else             { close(sv[1]); /* parent talks on sv[0] */ }
```

One `socketpair` replaces two pipes for request/response protocols. Unix-domain sockets can also pass **open file descriptors** between processes (`SCM_RIGHTS`), which is how privilege-separated servers hand over connections.

## 5. Shared memory: zero-copy for big data

```c
#include <sys/mman.h>
/* anonymous shared mapping inherited across fork: the simplest shared memory */
int *shared = mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);
if (shared == MAP_FAILED) { perror("mmap"); exit(1); }
if (fork() == 0) { shared[0] = 42; _exit(0); }
wait(NULL);
printf("%d\n", shared[0]);                   /* 42: the child's write is visible */
munmap(shared, 4096);

/* unrelated processes: shm_open("/robot_map", O_CREAT | O_RDWR, 0600) + ftruncate + mmap */
```

Shared memory gives **no synchronisation**: you need process-shared mutexes (`pthread_mutexattr_setpshared`), semaphores, atomics in the shared region, or a lock-free ring buffer. Image pipelines and ROS 2 zero-copy transports (iceoryx) use shared memory, because copying a 4K camera frame (24 MB/s at 30 fps per stream) through a socket wastes CPU.

## 6. Choosing

- A parent feeding or collecting from a child: **pipe** or **socketpair**.
- Request/response with a local daemon: a **Unix-domain socket**.
- Large, frequently updated data (frames, maps): **shared memory** plus a synchronisation primitive or a lock-free ring.
- Across machines: **TCP/UDP** (next lesson), or middleware (DDS in ROS 2, ZeroMQ, gRPC).

## 7. Exam-ready answers

> [!EXAM]
> **Pipes and message framing.** A pipe is a unidirectional kernel buffer connecting a write descriptor to a read descriptor, typically created before `fork` so that related processes share it; readers receive end-of-file only after every write descriptor has been closed, and writers block when the buffer is full, providing flow control. Because pipes and stream sockets transport an unstructured byte stream, a single read may return part of a message or several messages, so applications must define framing, such as delimiters or length prefixes, and loop over partial reads and writes. Shared memory avoids copying by mapping the same physical pages into several processes, but requires explicit synchronisation.

## 8. Cheat sheet

| Need | Use |
|---|---|
| one-way parent → child | `pipe` |
| two-way parent ↔ child | `socketpair(AF_UNIX, SOCK_STREAM, 0, sv)` |
| messages over streams | length prefix + `read_full`/`write_all` |
| local service | Unix-domain socket |
| big data, zero copy | `mmap(MAP_SHARED)` / `shm_open` |
| sync in shared memory | process-shared mutex, semaphore, or atomics |
| atomic small pipe writes | ≤ `PIPE_BUF` bytes |

> [!INTERVIEW]
> **"Your parent process reads from a child's pipe and hangs forever after the child exits. Why?"** The parent still holds the pipe's **write** end (it forgot `close(p[1])` after fork), so the kernel sees a live writer and never delivers EOF. Fix it by closing every unused end in every process right after `fork`. Also mention `O_CLOEXEC`/`pipe2`, so other exec'd children don't inherit the write end and keep the pipe open accidentally.
