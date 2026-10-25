---
id: c-signal-supervisor
title: A Signal-Aware Process Supervisor
difficulty: Hard
order: 1
tags: signals, sigaction, sig_atomic_t, timeouts, kill, waitpid, SIGCHLD
time_limit: 4
---
## Statement
A robot's launch supervisor must run helper programs with **timeouts**, count **control signals**, and shut down **gracefully**. Implement:

```c
int run_with_timeout(char *const argv[], int timeout_ms, int *timed_out);
    /* fork + execvp argv. If the child hasn't finished after timeout_ms, send SIGTERM, wait up to 100 ms more,
       then SIGKILL; always reap it. Set *timed_out to 1 if a timeout occurred, else 0.
       Return the exit code, 128+signal if it was killed by a signal, or 127 if exec failed. */
void install_handlers(void);
    /* SIGUSR1 increments a counter; SIGUSR2 adds 10; SIGTERM sets a "stop requested" flag.
       Use sigaction with SA_RESTART. Handlers may only touch volatile sig_atomic_t variables. */
int usr_count(void);          /* current counter value */
int stop_requested(void);     /* 1 once SIGTERM has been received */
```

Never call `printf`, `malloc` or similar inside a handler. The driver sends signals to the process with `kill(getpid(), …)`, starts children that sleep, exit or ignore SIGTERM, and measures that timeouts are honoured (not `sleep(timeout)` for the full duration when the child finishes early).

## Starter
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>
#include <sys/wait.h>

int run_with_timeout(char *const argv[], int timeout_ms, int *timed_out) {
    (void)timeout_ms;
    *timed_out = 0;
    pid_t pid = fork();
    if (pid == 0) { execvp(argv[0], argv); _exit(127); }
    int st;
    waitpid(pid, &st, 0);
    return WIFEXITED(st) ? WEXITSTATUS(st) : 1;
}
static int count;
void install_handlers(void) { }
int usr_count(void) { return count; }
int stop_requested(void) { return 0; }
```

## Driver
```c
#include <sys/stat.h>

static void make_script(const char *name, const char *body) {
    FILE *f = fopen(name, "w");
    fprintf(f, "#!/bin/sh\n%s\n", body);
    fclose(f);
    chmod(name, 0755);
}

static long now_ms(void) {
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000L + ts.tv_nsec / 1000000L;
}

int main(void) {
    char line[512];
    make_script("exit7.sh", "exit 7");
    make_script("ignoreterm.sh", "trap '' TERM; while :; do :; done");
    install_handlers();
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\n")] = '\0';
        if (!strncmp(line, "run ", 4)) {
            int timeout; char *rest;
            timeout = (int)strtol(line + 4, &rest, 10);
            char *args[32]; int na = 0;
            for (char *t = strtok(rest, " "); t && na < 31; t = strtok(NULL, " ")) args[na++] = t;
            args[na] = NULL;
            int to = -1;
            long t0 = now_ms();
            int status = run_with_timeout(args, timeout, &to);
            long el = now_ms() - t0;
            const char *speed = el < timeout + 400 ? "prompt" : "SLOW";
            printf("run %s (timeout %d ms): status=%d timed_out=%d %s\n", args[0], timeout, status, to, speed);
        } else if (!strncmp(line, "signal ", 7)) {
            int n1, n2; sscanf(line + 7, "%d %d", &n1, &n2);
            int before = usr_count();
            for (int i = 0; i < n1; i++) kill(getpid(), SIGUSR1);
            for (int i = 0; i < n2; i++) kill(getpid(), SIGUSR2);
            printf("signals: +%d (expected %d) stop=%d\n", usr_count() - before, n1 + 10 * n2, stop_requested());
        } else if (!strcmp(line, "term")) {
            kill(getpid(), SIGTERM);
            printf("after SIGTERM: alive=1 stop=%d\n", stop_requested());
        } else if (!strcmp(line, "readpipe")) {      /* SA_RESTART: a blocked read survives a signal */
            int p[2]; pipe(p);
            pid_t kid = fork();
            if (kid == 0) {
                struct timespec ts = {0, 100000000}; nanosleep(&ts, NULL);
                kill(getppid(), SIGUSR1);
                nanosleep(&ts, NULL);
                write(p[1], "ok", 2);
                _exit(0);
            }
            close(p[1]);
            char buf[4] = {0};
            ssize_t r = read(p[0], buf, 2);
            waitpid(kid, NULL, 0);
            close(p[0]);
            printf("read across signal: r=%zd data=%s errno_eintr=%d\n", r, r > 0 ? buf : "-", r < 0 && errno == EINTR);
        }
        fflush(stdout);
    }
    return 0;
}
```

## Tests
=== sample
run 1000 true
run 1000 ./exit7.sh
run 300 sleep 5
signal 3 1
---
run true (timeout 1000 ms): status=0 timed_out=0 prompt
run ./exit7.sh (timeout 1000 ms): status=7 timed_out=0 prompt
run sleep (timeout 300 ms): status=143 timed_out=1 prompt
signals: +13 (expected 13) stop=0
=== hidden
run 1000 false
run 500 no_such_program_qq
run 2000 sleep 0.2
run 300 ./ignoreterm.sh
run 250 sleep 10
signal 0 0
signal 50 2
term
readpipe
signal 1 0
---
run false (timeout 1000 ms): status=1 timed_out=0 prompt
run no_such_program_qq (timeout 500 ms): status=127 timed_out=0 prompt
run sleep (timeout 2000 ms): status=0 timed_out=0 prompt
run ./ignoreterm.sh (timeout 300 ms): status=137 timed_out=1 prompt
run sleep (timeout 250 ms): status=143 timed_out=1 prompt
signals: +0 (expected 0) stop=0
signals: +70 (expected 70) stop=0
after SIGTERM: alive=1 stop=1
read across signal: r=2 data=ok errno_eintr=0
signals: +1 (expected 1) stop=1

## Hints
- Install handlers with `sigaction`, `sa_flags = SA_RESTART`, and an empty `sa_mask`. In each handler, only modify `static volatile sig_atomic_t` variables.
- Timeout loop: poll `waitpid(pid, &st, WNOHANG)` every few milliseconds (`nanosleep`) until it returns the pid or the deadline passes (`clock_gettime(CLOCK_MONOTONIC)`). Then `kill(pid, SIGTERM)`, poll for up to 100 ms more, then `kill(pid, SIGKILL)` and a blocking `waitpid`.
- Status: `WIFEXITED` → `WEXITSTATUS`, `WIFSIGNALED` → `128 + WTERMSIG`.
- A blocking `read` interrupted by a handled signal fails with `EINTR` unless the handler was installed with `SA_RESTART`.

## Solution
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>
#include <sys/wait.h>

static volatile sig_atomic_t g_count = 0;
static volatile sig_atomic_t g_stop = 0;

static void on_usr1(int s) { (void)s; g_count = g_count + 1; }
static void on_usr2(int s) { (void)s; g_count = g_count + 10; }
static void on_term(int s) { (void)s; g_stop = 1; }

void install_handlers(void) {
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;
    sa.sa_handler = on_usr1; sigaction(SIGUSR1, &sa, NULL);
    sa.sa_handler = on_usr2; sigaction(SIGUSR2, &sa, NULL);
    sa.sa_handler = on_term; sigaction(SIGTERM, &sa, NULL);
}

int usr_count(void) { return g_count; }
int stop_requested(void) { return g_stop; }

static long now_ms_(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000L + ts.tv_nsec / 1000000L;
}

static int wait_until(pid_t pid, long deadline, int *status) {   /* 1 if reaped before the deadline */
    struct timespec nap = {0, 2000000};                         /* 2 ms */
    for (;;) {
        pid_t r = waitpid(pid, status, WNOHANG);
        if (r == pid) return 1;
        if (r < 0 && errno != EINTR) return 1;
        if (now_ms_() >= deadline) return 0;
        nanosleep(&nap, NULL);
    }
}

int run_with_timeout(char *const argv[], int timeout_ms, int *timed_out) {
    *timed_out = 0;
    fflush(stdout);
    pid_t pid = fork();
    if (pid < 0) return -1;
    if (pid == 0) {
        signal(SIGTERM, SIG_DFL);                   /* the child shouldn't inherit our handler semantics */
        execvp(argv[0], argv);
        _exit(127);
    }
    int st = 0;
    if (!wait_until(pid, now_ms_() + timeout_ms, &st)) {
        *timed_out = 1;
        kill(pid, SIGTERM);                         /* polite first */
        if (!wait_until(pid, now_ms_() + 100, &st)) {
            kill(pid, SIGKILL);                     /* can't be caught or ignored */
            while (waitpid(pid, &st, 0) < 0 && errno == EINTR) { }
        }
    }
    if (WIFEXITED(st)) return WEXITSTATUS(st);
    if (WIFSIGNALED(st)) return 128 + WTERMSIG(st);
    return -1;
}
```

- **Handlers do the minimum**: each one updates a `volatile sig_atomic_t`, the only shared type C guarantees can be written safely from a handler. The main program reads the counters whenever it wants. `kill(getpid(), sig)` delivers the signal before `kill` returns (it isn't blocked), so the counts are exact.
- **`SA_RESTART`** makes the blocked `read` in `readpipe` resume after the SIGUSR1 handler runs instead of failing with `EINTR`. That's why it returns "ok".
- **The timeout ladder** is SIGTERM, a grace period, then SIGKILL. Well-behaved programs get a chance to clean up (a robot node stops its motors), and programs that ignore SIGTERM (the `ignoreterm.sh` test, which runs `trap '' TERM`) still die because SIGKILL can't be caught. Polling `waitpid(..., WNOHANG)` with short sleeps returns promptly when the child finishes early, and the child is always reaped, so no zombies are left behind.
