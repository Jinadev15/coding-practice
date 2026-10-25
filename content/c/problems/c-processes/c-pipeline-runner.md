---
id: c-pipeline-runner
title: A Shell Pipeline Runner (fork, exec, pipe, dup2, wait)
difficulty: Hard
order: 1
tags: fork, execvp, pipe, dup2, waitpid, redirection, exit status
time_limit: 4
---
## Statement
Implement the core of a Unix shell: run a pipeline of commands with optional input/output redirection.

```c
int run_pipeline(char **cmds[], int n, const char *in_path, const char *out_path);
```

- `cmds[i]` is a NULL-terminated argv array for stage i (looked up in `PATH`, e.g. `{"tr", "a-z", "A-Z", NULL}`).
- Stage i's stdout feeds stage i+1's stdin through a pipe.
- If `in_path` isn't NULL, stage 0 reads from that file. If `out_path` isn't NULL, the last stage writes to it (create/truncate, mode 0644). Otherwise they inherit the parent's stdin/stdout.
- Wait for **all** stages. Return the last stage's status like a shell does: its exit code, `128 + signal` if it was killed by a signal, and `127` if it couldn't be executed (the child prints `name: command not found` to stderr, then calls `_exit(127)`). If `in_path` can't be opened, return 1 without running anything.
- No descriptor leaks: after `run_pipeline` returns, the parent must have closed every pipe end it created.

The driver parses lines like `cat < words.txt | sort | uniq -c > out.txt`, runs them through your function, and prints the status and the output file.

## Starter
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>

int run_pipeline(char **cmds[], int n, const char *in_path, const char *out_path) {
    (void)in_path; (void)out_path;
    int status = 0;
    for (int i = 0; i < n; i++) {               /* runs each stage separately: no pipes, no redirection */
        pid_t pid = fork();
        if (pid == 0) { execvp(cmds[i][0], cmds[i]); _exit(127); }
        waitpid(pid, &status, 0);
    }
    return WIFEXITED(status) ? WEXITSTATUS(status) : 1;
}
```

## Driver
```c
#include <sys/stat.h>

static int count_open_fds(void) {
    int c = 0;
    for (int fd = 0; fd < 256; fd++) if (fcntl(fd, F_GETFD) != -1) c++;
    return c;
}

int main(void) {
    FILE *w = fopen("words.txt", "w");
    const char *words[] = {"pear", "apple", "fig", "apple", "kiwi", "fig", "apple", "banana"};
    for (int i = 0; i < 8; i++) fprintf(w, "%s\n", words[i]);
    fclose(w);
    FILE *k = fopen("selfkill.sh", "w");
    fprintf(k, "#!/bin/sh\nkill -9 $$\n");
    fclose(k);
    chmod("selfkill.sh", 0755);
    char line[1024];
    int baseline = count_open_fds();
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\n")] = '\0';
        if (!line[0]) continue;
        char *tokens[128]; int nt = 0;
        for (char *t = strtok(line, " "); t && nt < 127; t = strtok(NULL, " ")) tokens[nt++] = t;
        char *in = NULL, *out = NULL;
        char **stages[16]; char *argvs[16][32]; int ns = 0, na = 0;
        for (int i = 0; i < nt; i++) {
            if (!strcmp(tokens[i], "<")) { in = tokens[++i]; continue; }
            if (!strcmp(tokens[i], ">")) { out = tokens[++i]; continue; }
            if (!strcmp(tokens[i], "|")) { argvs[ns][na] = NULL; stages[ns] = argvs[ns]; ns++; na = 0; continue; }
            argvs[ns][na++] = tokens[i];
        }
        argvs[ns][na] = NULL; stages[ns] = argvs[ns]; ns++;
        const char *target = out ? out : "result.txt";
        remove(target);
        fflush(stdout);
        int status = run_pipeline(stages, ns, in, target);
        printf("status=%d leaked_fds=%d output:", status, count_open_fds() - baseline);
        FILE *f = fopen(target, "r");
        if (!f) printf(" <no file>\n");
        else {
            int c; printf(" [");
            while ((c = fgetc(f)) != EOF) putchar(c == '\n' ? '/' : c);
            printf("]\n");
            fclose(f);
        }
        fflush(stdout);
    }
    return 0;
}
```

## Tests
=== sample
echo hello world
echo hello world | tr a-z A-Z
sort < words.txt | uniq -c | sort -rn | head -n 2
---
status=0 leaked_fds=0 output: [hello world/]
status=0 leaked_fds=0 output: [HELLO WORLD/]
status=0 leaked_fds=0 output: [      3 apple/      2 fig/]
=== hidden
cat < words.txt
cat < missing.txt
false
true
no_such_command_xyz arg
echo one | no_such_command_xyz
echo x | false
./selfkill.sh
seq 1 20000 | grep 7 | wc -l
cat < words.txt | sort | uniq | tr a-z A-Z | rev | sort
seq 5 > custom.txt
---
status=0 leaked_fds=0 output: [pear/apple/fig/apple/kiwi/fig/apple/banana/]
status=1 leaked_fds=0 output: <no file>
status=1 leaked_fds=0 output: []
status=0 leaked_fds=0 output: []
status=127 leaked_fds=0 output: []
status=127 leaked_fds=0 output: []
status=1 leaked_fds=0 output: []
status=137 leaked_fds=0 output: []
status=0 leaked_fds=0 output: [6878/]
status=0 leaked_fds=0 output: [ANANAB/ELPPA/GIF/IWIK/RAEP/]
status=0 leaked_fds=0 output: [1/2/3/4/5/]

## Hints
- Create the `n − 1` pipes up front (or as you go). In child i: `dup2(prev_read, 0)` if i > 0 (or the input file for i = 0), and `dup2(pipe_i_write, 1)` if i < n−1 (or the output file for the last stage). Then **close every pipe fd** the child holds before calling `execvp`.
- In the parent, close each pipe end as soon as no later stage needs it. `yes | head -n 3` only terminates if `yes` gets SIGPIPE, which requires that nobody else (including the parent) holds the pipe's read end once `head` exits.
- Wait for every child with `waitpid`, keeping the status of the last stage's pid.
- Decode: `WIFEXITED` → `WEXITSTATUS`; `WIFSIGNALED` → `128 + WTERMSIG`.

## Solution
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/wait.h>

int run_pipeline(char **cmds[], int n, const char *in_path, const char *out_path) {
    int in_fd = -1, out_fd = -1;
    if (in_path && (in_fd = open(in_path, O_RDONLY)) < 0) { perror(in_path); return 1; }
    if (out_path && (out_fd = open(out_path, O_WRONLY | O_CREAT | O_TRUNC, 0644)) < 0) {
        perror(out_path);
        if (in_fd >= 0) close(in_fd);
        return 1;
    }
    fflush(stdout);
    pid_t pids[64];
    int prev_read = in_fd;                        /* what stage i reads from (-1 = inherit) */
    for (int i = 0; i < n; i++) {
        int p[2] = {-1, -1};
        if (i < n - 1 && pipe(p) < 0) { perror("pipe"); return 1; }
        pids[i] = fork();
        if (pids[i] == 0) {
            if (prev_read >= 0) { dup2(prev_read, STDIN_FILENO); close(prev_read); }
            if (i < n - 1) { dup2(p[1], STDOUT_FILENO); close(p[1]); close(p[0]); }
            else if (out_fd >= 0) dup2(out_fd, STDOUT_FILENO);
            if (out_fd >= 0) close(out_fd);
            execvp(cmds[i][0], cmds[i]);
            fprintf(stderr, "%s: command not found\n", cmds[i][0]);
            _exit(127);
        }
        if (prev_read >= 0) close(prev_read);     /* the parent no longer needs the previous read end */
        if (i < n - 1) { close(p[1]); prev_read = p[0]; }   /* keep only the read end for the next stage */
        else prev_read = -1;
    }
    if (out_fd >= 0) close(out_fd);
    int status = 0, last = 0;
    for (int i = 0; i < n; i++) {
        waitpid(pids[i], &status, 0);
        if (i == n - 1) last = status;
    }
    if (WIFEXITED(last)) return WEXITSTATUS(last);
    if (WIFSIGNALED(last)) return 128 + WTERMSIG(last);
    return 1;
}
```

Each child wires its stdin and stdout with `dup2`, then **closes every inherited pipe descriptor** before `exec`. The parent closes each pipe end the moment no future stage needs it.
- **Why the closing discipline matters**: a reader sees EOF only when *all* write ends are closed. `yes | head -n 3` terminates only because, after `head` exits, no process holds the read end, so `yes` receives SIGPIPE.
- **The exit status** follows shell conventions: a pipeline's status is its last stage's; death by a signal is 128 + the signal number (137 for SIGKILL); and 127 means "couldn't execute".
- `fflush(stdout)` before forking prevents buffered parent output from being duplicated into the children.
