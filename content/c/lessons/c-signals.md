# Signals

A **signal** is an asynchronous notification delivered to a process: Ctrl-C (`SIGINT`), a child exiting (`SIGCHLD`), a timer expiring (`SIGALRM`), an invalid memory access (`SIGSEGV`), a write to a closed pipe (`SIGPIPE`), or `kill` from another process (`SIGTERM`, `SIGKILL`). Handling signals correctly is notoriously subtle, because a handler can interrupt your program **at any instruction**. This lesson covers the signal model, `sigaction`, async-signal-safety, the self-pipe and `signalfd` patterns, masking, and graceful shutdown. A robot controller must stop its motors cleanly when it receives SIGTERM, so these are practical skills.

## 1. Signals and default actions

| Signal | Typical cause | Default |
|---|---|---|
| `SIGINT` | Ctrl-C | terminate |
| `SIGTERM` | `kill pid`, a polite shutdown request (systemd, docker stop) | terminate |
| `SIGKILL` | `kill -9` | terminate (**can't be caught or ignored**) |
| `SIGSTOP` / `SIGCONT` | stop/continue (job control) | stop/continue (STOP can't be caught) |
| `SIGCHLD` | a child stopped or exited | ignore |
| `SIGALRM` | `alarm()` / timers | terminate |
| `SIGSEGV`, `SIGBUS`, `SIGFPE`, `SIGILL` | faults (bad pointer, misalignment, divide by zero, bad instruction) | core dump |
| `SIGPIPE` | write to a pipe/socket with no reader | terminate |
| `SIGUSR1`, `SIGUSR2` | application defined | terminate |
| `SIGHUP` | terminal hang-up; by convention "reload config" for daemons | terminate |

Send signals with `kill(pid, sig)`, `raise(sig)` (to yourself) or `kill -TERM <pid>` from the shell.

## 2. Installing handlers with `sigaction`

```c
#define _POSIX_C_SOURCE 200809L
#include <signal.h>
#include <stdio.h>
#include <unistd.h>

static volatile sig_atomic_t stop_requested = 0;

static void on_term(int sig) {
    (void)sig;
    stop_requested = 1;                      /* the ONLY kind of thing a handler should usually do */
}

int main(void) {
    struct sigaction sa = {0};
    sa.sa_handler = on_term;
    sigemptyset(&sa.sa_mask);                /* signals blocked while the handler runs (plus sig itself) */
    sa.sa_flags = SA_RESTART;                /* restart slow syscalls (read/write) instead of failing with EINTR */
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGINT, &sa, NULL);

    while (!stop_requested) {
        /* control loop: read sensors, compute, command motors */
        sleep(1);
    }
    /* graceful shutdown: stop motors, flush logs, close devices */
    puts("shutting down cleanly");
}
```

> [!KEY]
> Use `sigaction`, not `signal()`. `signal`'s semantics vary between systems (whether the handler resets to default, whether syscalls restart). `sigaction` makes every aspect explicit: the handler, the mask during the handler, and the flags (`SA_RESTART`, `SA_SIGINFO`, `SA_NOCLDSTOP`).

## 3. Async-signal-safety: the hard rule

A handler interrupts the main program **anywhere**, possibly in the middle of `malloc`, `printf` or a mutex lock. If the handler then calls `malloc` or `printf`, it can deadlock or corrupt their internal state.

> [!DANGER]
> Inside a signal handler, call **only async-signal-safe functions**: `write`, `_exit`, `kill`, `sigaction`, `read`, `close`, `signal`-safe atomics, and a few dozen others listed in `man 7 signal-safety`. **Not** `printf`, `malloc`, `free`, `exit`, `syslog`, or anything taking a lock. The only shared data a handler may write portably is a `volatile sig_atomic_t` variable (or a lock-free C11 atomic).

```c
static void on_segv(int sig) {
    static const char msg[] = "fatal: segmentation fault\n";
    write(STDERR_FILENO, msg, sizeof msg - 1);     /* write is async-signal-safe; fprintf isn't */
    signal(sig, SIG_DFL);
    raise(sig);                                    /* re-raise with the default action → core dump */
}
```

The robust design is to **do almost nothing in the handler**: set a flag, or write a byte to a pipe, and handle the event in the main loop.

## 4. The self-pipe trick and `signalfd`

A main loop blocked in `poll`/`select` won't notice a flag set by a handler until it wakes up. The **self-pipe trick** turns signals into readable events:

```c
static int sigpipe_fds[2];

static void on_signal(int sig) {
    unsigned char b = (unsigned char)sig;
    int saved = errno;                             /* handlers must preserve errno */
    write(sigpipe_fds[1], &b, 1);                  /* non-blocking write end */
    errno = saved;
}
/* main loop: poll() on sigpipe_fds[0] together with sockets and devices; read the signal numbers there */
```

On Linux, **`signalfd`** does this directly: block the signals with `sigprocmask`, then read `struct signalfd_siginfo` records from a descriptor in your event loop. For threaded programs, a dedicated thread calling `sigwait()` on a blocked signal set is the cleanest model.

## 5. Masks, blocking and races

```c
sigset_t block, old;
sigemptyset(&block);
sigaddset(&block, SIGINT);
sigprocmask(SIG_BLOCK, &block, &old);     /* SIGINT now stays PENDING instead of being delivered */
/* critical section: update data structures that the handler also touches */
sigprocmask(SIG_SETMASK, &old, NULL);     /* a pending SIGINT is delivered now */
```

- Blocked signals stay pending (at most one instance per standard signal; they don't queue).
- `pthread_sigmask` sets per-thread masks.
- `sigsuspend(&mask)` atomically unblocks and waits, which avoids the race in "check the flag, then pause()" where a signal arriving between the two calls would be lost.

## 6. SIGCHLD and reaping

```c
static void on_child(int sig) {
    (void)sig;
    int saved = errno;
    while (waitpid(-1, NULL, WNOHANG) > 0) { }     /* reap ALL exited children: signals don't queue */
    errno = saved;
}
```

Setting `SIGCHLD` to `SIG_IGN` (or `SA_NOCLDWAIT`) makes the kernel reap children automatically, at the cost of not knowing their exit status.

## 7. SIGPIPE and EINTR in servers

- Writing to a socket whose peer closed raises `SIGPIPE`, which kills the process by default. Servers ignore it (`signal(SIGPIPE, SIG_IGN)`, or `send(..., MSG_NOSIGNAL)`) and handle the `EPIPE` error from the call instead.
- Without `SA_RESTART`, blocking calls such as `read`, `accept` and `sleep` fail with `EINTR` when a signal is handled. Retry them, or deliberately use the interruption as a wake-up.

## 8. Timeouts with `alarm` and timers

```c
alarm(2);                                  /* SIGALRM in 2 s (one per process; alarm(0) cancels) */
/* finer and multiple timers: timer_create/timer_settime (POSIX), or timerfd on Linux */
```

## 9. Exam-ready answers

> [!EXAM]
> **Signal handling.** Signals are asynchronous notifications delivered to a process by the kernel or by other processes, each with a default action such as terminating, stopping or ignoring. A process can install a handler with `sigaction`, specifying the handler, a mask of signals blocked during its execution, and flags such as `SA_RESTART`. Because a handler may interrupt the program at any point, it must call only async-signal-safe functions and should limit itself to setting a `volatile sig_atomic_t` flag or writing to a pipe, deferring real work to the main program. `SIGKILL` and `SIGSTOP` can't be caught or ignored. Signals can be blocked with `sigprocmask`, remaining pending until unblocked, and standard signals don't queue, so for example a SIGCHLD handler must reap all exited children in a loop.

## 10. Cheat sheet

| Need | Technique |
|---|---|
| install a handler | `sigaction` with `sa_mask` and `SA_RESTART` |
| shared flag | `volatile sig_atomic_t` |
| print from a handler | `write(2, msg, len)` only |
| integrate with poll | self-pipe or `signalfd` |
| threads | block in all threads, one thread calls `sigwait` |
| reap children | loop `waitpid(-1, 0, WNOHANG)` |
| servers | ignore SIGPIPE, handle EPIPE |
| avoid the check/pause race | `sigsuspend` |

> [!INTERVIEW]
> **"Why is calling `printf` in a signal handler dangerous?"** `printf` uses a shared buffer protected by an internal lock. If the signal interrupts the main program while it's inside `printf` (holding that lock), the handler's `printf` tries to take the same lock: deadlock. Or, without a lock, it corrupts the buffer. Only async-signal-safe functions (like `write`) may be called, and the recommended pattern is to set a `sig_atomic_t` flag and act on it in the main loop.
