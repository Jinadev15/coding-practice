# Processes: fork, exec, wait

A **process** is a running program: an address space (code, data, heap, stack), a set of open file descriptors, credentials, and one or more threads of execution. Unix creates processes with a uniquely elegant pair of calls: `fork` duplicates the current process, and `exec` replaces a process's program with a new one. Combined with `wait`, `pipe` and `dup2`, they're how every shell, init system, robot launch system (ROS 2 `launch`, systemd) and build tool starts and supervises other programs.

## 1. `fork`: one call, two returns

```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>

int main(void) {
    pid_t pid = fork();
    if (pid < 0) { perror("fork"); return 1; }
    if (pid == 0) {                       /* child: fork returned 0 */
        printf("child: pid=%d parent=%d\n", (int)getpid(), (int)getppid());
        _exit(7);                         /* exit status 7 */
    }
    int status;                           /* parent: fork returned the child's pid */
    waitpid(pid, &status, 0);
    if (WIFEXITED(status)) printf("child exited with %d\n", WEXITSTATUS(status));
}
```

After `fork`, the child is a **copy** of the parent: the same code, a copy of memory (implemented copy-on-write, so it's cheap), copies of all file descriptors (sharing offsets), and the same signal handlers. They diverge from the return value onward.

> [!WARNING]
> **Buffered output is duplicated too.** If `printf("hello")` (no newline, so it's still in stdio's buffer) runs before `fork`, both processes flush it later and "hello" prints twice. Call `fflush(stdout)` before forking. In the child, use `_exit` rather than `exit` after a failed exec, so the parent's stdio buffers and `atexit` handlers aren't run twice.

## 2. `exec`: replace the program

```c
char *argv[] = {"ls", "-l", "/tmp", NULL};
execvp("ls", argv);                       /* only returns on failure */
perror("execvp");                         /* e.g. ENOENT: command not found */
_exit(127);                               /* shell convention for "command not found" */
```

| Function | Path lookup | Arguments | Environment |
|---|---|---|---|
| `execv(path, argv)` | no | array | inherited |
| `execvp(file, argv)` | searches `PATH` | array | inherited |
| `execve(path, argv, envp)` | no | array | explicit (the real syscall) |
| `execl`/`execlp`/`execle` | as above | variadic list ending in `NULL` | |

`exec` keeps the pid, the open descriptors (except those with `FD_CLOEXEC`), the current directory and signal masks, and resets caught signals to their defaults.

## 3. `wait` and process status

```c
int status;
pid_t done = waitpid(-1, &status, 0);         /* any child */
waitpid(pid, &status, WNOHANG);               /* don't block: returns 0 if still running */

if (WIFEXITED(status))   printf("exit %d\n", WEXITSTATUS(status));
if (WIFSIGNALED(status)) printf("killed by signal %d\n", WTERMSIG(status));
```

**Zombies**: a child that has exited but hasn't been waited for keeps a process-table entry, shown as `<defunct>`. Long-running supervisors must reap children: loop `waitpid(-1, &st, WNOHANG)` in the main loop or after a SIGCHLD. **Orphans**: if the parent dies first, the child is re-parented to init (pid 1) or a subreaper, which reaps it.

## 4. The shell pattern: fork + redirect + exec + wait

```c
/* run: sort < in.txt > out.txt */
pid_t pid = fork();
if (pid == 0) {
    int in = open("in.txt", O_RDONLY);
    int out = open("out.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (in < 0 || out < 0) { perror("open"); _exit(1); }
    dup2(in, STDIN_FILENO);
    dup2(out, STDOUT_FILENO);
    close(in); close(out);
    execlp("sort", "sort", (char *)NULL);
    perror("execlp");
    _exit(127);
}
waitpid(pid, NULL, 0);
```

The redirection happens **in the child, between fork and exec**, so it affects only the new program. That separation is why Unix doesn't need a "spawn with options" call. (POSIX does offer `posix_spawn`, which is faster for huge parents and works where `fork` is expensive.)

### Pipelines: `ls | wc -l`

```c
int p[2];
pipe(p);                                  /* p[0] read end, p[1] write end */
if (fork() == 0) {                        /* writer: ls */
    dup2(p[1], STDOUT_FILENO);
    close(p[0]); close(p[1]);
    execlp("ls", "ls", (char *)NULL); _exit(127);
}
if (fork() == 0) {                        /* reader: wc -l */
    dup2(p[0], STDIN_FILENO);
    close(p[0]); close(p[1]);
    execlp("wc", "wc", "-l", (char *)NULL); _exit(127);
}
close(p[0]); close(p[1]);                 /* the parent MUST close both ends… */
while (wait(NULL) > 0) { }                /* …or wc never sees EOF and hangs */
```

> [!KEY]
> A pipe's reader gets EOF only when **every** write end is closed, in every process. Forgetting to close an unused write end (in the parent or in the reader child itself) is the classic cause of hanging pipelines.

## 5. Process attributes

| Call | Purpose |
|---|---|
| `getpid`, `getppid` | ids |
| `getenv`, `setenv` | environment variables (inherited by children) |
| `chdir`, `getcwd` | working directory |
| `nice`, `setpriority` | scheduling priority |
| `setsid` | new session (daemons, detaching from the terminal) |
| `setpgid`, `tcsetpgrp` | process groups / job control |
| `getrusage`, `wait4` | CPU time and memory used by children |
| `prctl(PR_SET_PDEATHSIG, SIGTERM)` (Linux) | kill the child when its parent dies (robot node supervision) |

## 6. Exam-ready answers

> [!EXAM]
> **fork and exec.** `fork` creates a new process that is a near-identical copy of the caller: the child receives copies of the parent's address space (implemented copy-on-write), open file descriptors and signal dispositions, and the call returns the child's process ID in the parent and 0 in the child. `exec` replaces the calling process's program image with a new executable while keeping its process ID and open descriptors not marked close-on-exec. Separating creation from program loading lets a child adjust its environment (for example redirecting standard input and output with `dup2`, or closing descriptors) before calling exec. A parent collects a child's termination status with `wait` or `waitpid`; unreaped terminated children remain as zombies.

## 7. Cheat sheet

| Need | Code |
|---|---|
| spawn | `fork()`, then `execvp()` in the child |
| exit in a child after a failed exec | `_exit(127)` |
| wait for one child | `waitpid(pid, &st, 0)` |
| decode the status | `WIFEXITED`/`WEXITSTATUS`, `WIFSIGNALED`/`WTERMSIG` |
| reap without blocking | `waitpid(-1, &st, WNOHANG)` loop |
| redirect | `dup2` in the child before exec |
| pipeline | `pipe` + two forks; **close all unused ends** |
| avoid duplicated output | `fflush(stdout)` before `fork` |

> [!INTERVIEW]
> **"How many times does this print?"** `for (int i = 0; i < 3; i++) fork(); printf("x\n");` gives 8. Each fork doubles the number of processes (2³). Follow-up: `printf("x"); fork(); printf("\n");` prints "x" twice, because the unflushed buffer is copied into the child. Explain copy-on-write, and why `fflush` before `fork` matters.
