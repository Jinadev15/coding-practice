---
id: c-m1-argv-split
title: Shell-Style Command Splitter
difficulty: Hard
order: 4
tags: strings, pointers, dynamic memory, state machines
---
## Statement
Implement the word splitting a shell performs before running a command. For each input line, split it into **commands separated by unquoted `|`**, and each command into **arguments**:

- Unquoted spaces and tabs separate arguments. Several in a row count as one separator.
- `'single quotes'` preserve everything literally (no escapes inside).
- `"double quotes"` preserve everything except that `\"` and `\\` are escapes for `"` and `\`. Any other backslash stays literal.
- Outside quotes, a backslash escapes the next character (`\ ` is a literal space, `\|` a literal pipe).
- Quotes can be adjacent to other text, forming **one** argument: `a"b c"'d'` → `ab cd`. An empty quoted string `""` is an empty argument.
- An unquoted `|` ends the current command, even without spaces around it.

Output, for each line: `N command(s)`, then for each command `  [i] argc=K: <arg1> <arg2> ...`, with each argument wrapped in angle brackets. Errors: `error: unterminated quote`, `error: empty command` (a pipe with no arguments on one side, e.g. `| a`, `a ||`), or `error: trailing backslash`. A blank line gives `0 command(s)`.

Build each command's `argv` as a dynamically allocated, NULL-terminated `char **` (exactly what `execvp` expects), and free everything.

## Starter
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    char line[4096];
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\n")] = '\0';
        /* TODO */
    }
    return 0;
}
```

## Tests
=== sample
ls -la /tmp
echo "hello world" | grep 'o w' | wc -l
a"b c"'d' "" x
printf "say \"hi\" \\ \n"
echo 'unterminated
cat file | | wc
---
1 command(s)
  [0] argc=3: <ls> <-la> </tmp>
3 command(s)
  [0] argc=2: <echo> <hello world>
  [1] argc=2: <grep> <o w>
  [2] argc=2: <wc> <-l>
1 command(s)
  [0] argc=3: <ab cd> <> <x>
1 command(s)
  [0] argc=2: <printf> <say "hi" \ \n>
error: unterminated quote
error: empty command
=== hidden

   
one
a\ b c\|d|e
"|"|'|'
x |y| z
'' '' ''
"a\b"  'a\b'  a\\b
end\
|start
trail |
	tab	separated		args
"multi word" 'and "nested"' "it's"
---
0 command(s)
0 command(s)
1 command(s)
  [0] argc=1: <one>
2 command(s)
  [0] argc=2: <a b> <c|d>
  [1] argc=1: <e>
2 command(s)
  [0] argc=1: <|>
  [1] argc=1: <|>
3 command(s)
  [0] argc=1: <x>
  [1] argc=1: <y>
  [2] argc=1: <z>
1 command(s)
  [0] argc=3: <> <> <>
1 command(s)
  [0] argc=3: <a\b> <a\b> <a\b>
error: trailing backslash
error: empty command
error: empty command
1 command(s)
  [0] argc=3: <tab> <separated> <args>
1 command(s)
  [0] argc=3: <multi word> <and "nested"> <it's>

## Hints
- Scan character by character with a small **state machine**: `NORMAL`, `IN_SINGLE`, `IN_DOUBLE`. Track whether the current argument has "started", so that `""` produces an empty argument but plain spaces produce none.
- Build the current argument in a growable `char` buffer. When it ends, `strdup` it into the current command's growable `char **` (keep one spare slot for the terminating NULL).
- A command is a struct `{char **argv; int argc;}`. Keep a growable array of those for the line.
- Write a single `free_line()` that releases everything, and call it on the error paths too.

## Solution
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct { char **argv; int argc, cap; } Cmd;
typedef struct { Cmd *cmds; int n, cap; } Line;
typedef struct { char *s; size_t len, cap; } Buf;

static void *xrealloc(void *p, size_t n) {
    void *q = realloc(p, n);
    if (!q) { perror("realloc"); exit(1); }
    return q;
}
static void buf_put(Buf *b, char c) {
    if (b->len + 1 >= b->cap) { b->cap = b->cap ? b->cap * 2 : 32; b->s = xrealloc(b->s, b->cap); }
    b->s[b->len++] = c;
}
static Cmd *new_cmd(Line *l) {
    if (l->n == l->cap) { l->cap = l->cap ? l->cap * 2 : 4; l->cmds = xrealloc(l->cmds, (size_t)l->cap * sizeof *l->cmds); }
    Cmd *c = &l->cmds[l->n++];
    c->cap = 4;
    c->argc = 0;
    c->argv = xrealloc(NULL, (size_t)c->cap * sizeof *c->argv);
    c->argv[0] = NULL;
    return c;
}
static void push_arg(Cmd *c, Buf *b) {
    if (c->argc + 2 > c->cap) { c->cap *= 2; c->argv = xrealloc(c->argv, (size_t)c->cap * sizeof *c->argv); }
    char *s = malloc(b->len + 1);
    if (!s) { perror("malloc"); exit(1); }
    memcpy(s, b->s, b->len);
    s[b->len] = '\0';
    c->argv[c->argc++] = s;
    c->argv[c->argc] = NULL;            /* always NULL-terminated, like execvp wants */
    b->len = 0;
}
static void free_line(Line *l) {
    for (int i = 0; i < l->n; i++) {
        for (int j = 0; j < l->cmds[i].argc; j++) free(l->cmds[i].argv[j]);
        free(l->cmds[i].argv);
    }
    free(l->cmds);
    l->cmds = NULL;
    l->n = l->cap = 0;
}

/* returns NULL on success, or an error message */
static const char *split(const char *s, Line *l) {
    enum { NORMAL, SQ, DQ } st = NORMAL;
    Buf b = {0};
    int started = 0;
    const char *errmsg = NULL;
    Cmd *cur = NULL;
    int saw_pipe = 0;
    for (;; s++) {
        char c = *s;
        if (st == SQ) {
            if (c == '\0') { errmsg = "unterminated quote"; break; }
            if (c == '\'') st = NORMAL; else buf_put(&b, c);
            continue;
        }
        if (st == DQ) {
            if (c == '\0') { errmsg = "unterminated quote"; break; }
            if (c == '"') st = NORMAL;
            else if (c == '\\' && (s[1] == '"' || s[1] == '\\')) buf_put(&b, *++s);
            else buf_put(&b, c);
            continue;
        }
        /* NORMAL */
        if (c == '\0' || c == ' ' || c == '\t' || c == '|') {
            if (started) {
                if (!cur) cur = new_cmd(l);
                push_arg(cur, &b);
                started = 0;
            }
            if (c == '|') {
                if (!cur) { errmsg = "empty command"; break; }
                cur = NULL;
                saw_pipe = 1;
            }
            if (c == '\0') {
                if (saw_pipe && !cur) errmsg = "empty command";
                break;
            }
            continue;
        }
        started = 1;
        if (c == '\'') st = SQ;
        else if (c == '"') st = DQ;
        else if (c == '\\') {
            if (s[1] == '\0') { errmsg = "trailing backslash"; break; }
            buf_put(&b, *++s);
        } else buf_put(&b, c);
    }
    free(b.s);
    return errmsg;
}

int main(void) {
    char line[4096];
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\n")] = '\0';
        Line l = {0};
        const char *e = split(line, &l);
        if (e) {
            printf("error: %s\n", e);
        } else {
            printf("%d command(s)\n", l.n);
            for (int i = 0; i < l.n; i++) {
                printf("  [%d] argc=%d:", i, l.cmds[i].argc);
                for (char **a = l.cmds[i].argv; *a; a++) printf(" <%s>", *a);
                putchar('\n');
            }
        }
        free_line(&l);
    }
    return 0;
}
```

**Key ideas:**
- **An explicit state machine** (`NORMAL`, `SQ`, `DQ`) makes the quoting rules readable and complete. Every character is handled by exactly one state.
- **A `started` flag** separates "no argument" from "an empty argument": `""` sets it without adding characters.
- **NULL-terminated `argv`** with one spare slot is the exact contract of `execvp(argv[0], argv)`, which you'll use in the Processes lesson to actually run these commands.
- **One `free_line`** for both the success and error paths prevents leaks. `free(NULL)` and an empty line make it safe in every state.
