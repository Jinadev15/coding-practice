---
id: c-mini-preprocessor
title: Build a Mini Preprocessor
difficulty: Hard
order: 1
tags: conditional compilation, macros, parsing, stacks, recursion
---
## Statement
The best way to understand the preprocessor is to write one. Read a source file from stdin and output what the compiler would see, supporting:

- `#define NAME` and `#define NAME VALUE` (VALUE is the rest of the line, trimmed; object-like macros only), and `#undef NAME`.
- `#ifdef NAME`, `#ifndef NAME`, `#if EXPR`, `#elif EXPR`, `#else`, `#endif`, nested to any depth.
- `#error MESSAGE` in an active region prints `error: MESSAGE` and stops immediately (no further output).
- Directive lines may have spaces before and after the `#`. They're **removed** from the output, and lines in inactive regions are removed too. In inactive regions, directives are not evaluated (a `#define` there has no effect), but nesting must still be tracked.
- Other lines in active regions are printed with **macro expansion**: every identifier (`[A-Za-z_][A-Za-z0-9_]*`) that names a macro is replaced by its value, recursively, except that a macro is never expanded inside its own expansion (so `#define X X+1` turns `X` into `X+1`). Identifiers inside double-quoted strings aren't expanded.

`#if` expressions use C precedence over: decimal integers; `defined(NAME)` and `defined NAME`; identifiers (a macro whose value is itself an expression is evaluated recursively; an undefined identifier, or one defined with no value, is `0`); unary `!` and `-`; `* / %`; `+ -`; `< <= > >=`; `== !=`; `&&`; `||`; and parentheses. Division or modulo by zero is treated as 0.

Errors (print the message and stop):
- `error: line N: unexpected #else` (likewise `#elif` and `#endif`): no open `#if`, or `#else`/`#elif` after an `#else` at the same level.
- `error: unterminated #if` at the end of input.

## Starter
```c
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdlib.h>

int main(void) {
    char line[1024];
    while (fgets(line, sizeof line, stdin)) {
        fputs(line, stdout);
    }
    return 0;
}
```

## Tests
=== sample
#define VERSION 3
#define DEBUG
#define GREETING "hello"
#if VERSION >= 3 && defined(DEBUG)
log("v3 debug: VERSION");
#elif VERSION >= 3
log("v3");
#else
log("old");
#endif
#ifndef DEBUG
never();
#endif
int size = VERSION * 2;
puts(GREETING);
---
log("v3 debug: VERSION");
int size = 3 * 2;
puts("hello");
=== hidden
#define A B
#define B C
#define C 7
x = A + B + C;
#define X X+1
y = X;
#undef C
z = A;
#if 0
#define HIDDEN 1
#if 1
also_hidden();
#endif
#else
  #  ifdef HIDDEN
bad();
  #  else
shown();
  # endif
#endif
#if (2 + 3) * 4 == 20 && !(1 > 2) || 0
math_ok();
#endif
#if 7 / 0 == 0 && -3 < 0 && 10 % 3 == 1
div_ok();
#endif
---
x = 7 + 7 + 7;
y = X+1;
z = C;
shown();
math_ok();
div_ok();
=== hidden
#define LEVEL 2
#if LEVEL == 1
one
#elif LEVEL == 2
two
#elif LEVEL == 2
two_again
#else
other
#endif
#if UNDEFINED_THING
nope
#endif
#define EXPR (LEVEL + 1) * 2
#if EXPR == 6
expr_six
#endif
#ifdef LEVEL
#error stop here
#endif
after_error
---
two
expr_six
error: stop here
=== hidden
#if 1
a
#else
b
#else
c
#endif
---
a
error: line 5: unexpected #else
=== hidden
#ifdef X
x
---
error: unterminated #if
=== hidden
ok
#endif
---
ok
error: line 2: unexpected #endif

## Hints
- Keep a stack of conditional frames: `{ parent_active, this_branch_active, any_branch_taken, seen_else }`. A line is active only if every frame on the stack is active.
- `#elif` and `#else`: if the parent isn't active, everything stays inactive. Otherwise the new branch is active only if no earlier branch was taken (and, for `#elif`, its expression is true).
- Expression evaluation: a recursive-descent parser over the expression string, one function per precedence level. For an identifier, look up the macro and evaluate its value text recursively, with a depth limit.
- Expansion: copy characters, toggling an "in string" flag at unescaped `"`. When you meet an identifier that's a macro and isn't on the "currently expanding" stack, push it, recursively expand its value into the output, and pop it.

## Solution
```c
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdlib.h>

#define MAXM 256
typedef struct { char name[64]; char value[256]; } Macro;
static Macro macros[MAXM];
static int nmacros;

static Macro *lookup(const char *name, size_t len) {
    for (int i = 0; i < nmacros; i++)
        if (strlen(macros[i].name) == len && strncmp(macros[i].name, name, len) == 0) return &macros[i];
    return NULL;
}
static void define(const char *name, const char *value) {
    Macro *m = lookup(name, strlen(name));
    if (!m) m = &macros[nmacros++];
    snprintf(m->name, sizeof m->name, "%s", name);
    snprintf(m->value, sizeof m->value, "%s", value);
}
static void undef(const char *name) {
    Macro *m = lookup(name, strlen(name));
    if (m) *m = macros[--nmacros];
}

/* ---------- #if expression evaluator (recursive descent) ---------- */
static const char *ep;
static int edepth;
static long e_or(void);
static void ews(void) { while (*ep == ' ' || *ep == '\t') ep++; }
static int eat(const char *op) {
    ews();
    size_t n = strlen(op);
    if (strncmp(ep, op, n) == 0) { ep += n; return 1; }
    return 0;
}
static long eval_text(const char *text) {
    if (edepth > 32) return 0;
    const char *save = ep;
    edepth++;
    ep = text;
    long v = e_or();
    edepth--;
    ep = save;
    return v;
}
static long e_primary(void) {
    ews();
    if (*ep == '(') { ep++; long v = e_or(); eat(")"); return v; }
    if (isdigit((unsigned char)*ep)) return strtol(ep, (char **)&ep, 10);
    if (isalpha((unsigned char)*ep) || *ep == '_') {
        const char *s = ep;
        while (isalnum((unsigned char)*ep) || *ep == '_') ep++;
        size_t len = (size_t)(ep - s);
        if (len == 7 && strncmp(s, "defined", 7) == 0) {
            int paren = eat("(");
            ews();
            const char *n = ep;
            while (isalnum((unsigned char)*ep) || *ep == '_') ep++;
            long r = lookup(n, (size_t)(ep - n)) != NULL;
            if (paren) eat(")");
            return r;
        }
        Macro *m = lookup(s, len);
        return (m && m->value[0]) ? eval_text(m->value) : 0;
    }
    return 0;
}
static long e_unary(void) {
    if (eat("!")) return !e_unary();
    if (eat("-")) return -e_unary();
    return e_primary();
}
static long e_mul(void) {
    long v = e_unary();
    for (;;) {
        if (eat("*")) v *= e_unary();
        else if (eat("/")) { long r = e_unary(); v = r ? v / r : 0; }
        else if (eat("%")) { long r = e_unary(); v = r ? v % r : 0; }
        else return v;
    }
}
static long e_add(void) {
    long v = e_mul();
    for (;;) {
        if (eat("+")) v += e_mul();
        else if (eat("-")) v -= e_mul();
        else return v;
    }
}
static long e_rel(void) {
    long v = e_add();
    for (;;) {
        if (eat("<=")) v = v <= e_add();
        else if (eat(">=")) v = v >= e_add();
        else if (eat("<")) v = v < e_add();
        else if (eat(">")) v = v > e_add();
        else return v;
    }
}
static long e_eq(void) {
    long v = e_rel();
    for (;;) {
        if (eat("==")) v = v == e_rel();
        else if (eat("!=")) v = v != e_rel();
        else return v;
    }
}
static long e_and(void) {
    long v = e_eq();
    while (eat("&&")) { long r = e_eq(); v = v && r; }
    return v;
}
static long e_or(void) {
    long v = e_and();
    while (eat("||")) { long r = e_and(); v = v || r; }
    return v;
}

/* ---------- macro expansion of ordinary lines ---------- */
static const Macro *active_stack[64];
static int nactive;

static int is_expanding(const Macro *m) {
    for (int i = 0; i < nactive; i++) if (active_stack[i] == m) return 1;
    return 0;
}
static void expand(const char *s, FILE *out) {
    int in_str = 0;
    char prev = '\0';
    while (*s) {
        if (*s == '"' && prev != '\\') { in_str = !in_str; prev = *s; fputc(*s++, out); continue; }
        if (!in_str && (isalpha((unsigned char)*s) || *s == '_')) {
            const char *b = s;
            while (isalnum((unsigned char)*s) || *s == '_') s++;
            Macro *m = lookup(b, (size_t)(s - b));
            if (m && !is_expanding(m) && nactive < 64) {
                active_stack[nactive++] = m;
                expand(m->value, out);
                nactive--;
            } else {
                fwrite(b, 1, (size_t)(s - b), out);
            }
            prev = s[-1];
            continue;
        }
        prev = *s;
        fputc(*s++, out);
    }
}

/* ---------- driver ---------- */
typedef struct { int parent_active, active, taken, seen_else; } Frame;

int main(void) {
    char line[1024];
    Frame st[128];
    int depth = 0, lineno = 0;
    while (fgets(line, sizeof line, stdin)) {
        lineno++;
        line[strcspn(line, "\r\n")] = '\0';
        int active = depth == 0 || st[depth - 1].active;
        char *p = line;
        while (*p == ' ' || *p == '\t') p++;
        if (*p != '#') {
            if (active) { expand(line, stdout); putchar('\n'); }
            continue;
        }
        p++;
        while (*p == ' ' || *p == '\t') p++;
        char word[16] = {0};
        int wl = 0;
        while (isalpha((unsigned char)*p) && wl < 15) word[wl++] = *p++;
        while (*p == ' ' || *p == '\t') p++;
        char *arg = p;
        for (char *e = arg + strlen(arg); e > arg && isspace((unsigned char)e[-1]);) *--e = '\0';

        if (!strcmp(word, "if") || !strcmp(word, "ifdef") || !strcmp(word, "ifndef")) {
            int cond = 0;
            if (active) {
                if (!strcmp(word, "if")) { edepth = 0; cond = eval_text(arg) != 0; }
                else {
                    int def = lookup(arg, strlen(arg)) != NULL;
                    cond = !strcmp(word, "ifdef") ? def : !def;
                }
            }
            st[depth++] = (Frame){active, active && cond, active && cond, 0};
        } else if (!strcmp(word, "elif") || !strcmp(word, "else")) {
            if (depth == 0 || st[depth - 1].seen_else) {
                printf("error: line %d: unexpected #%s\n", lineno, word);
                return 0;
            }
            Frame *f = &st[depth - 1];
            int cond = 1;
            if (!strcmp(word, "elif")) {
                cond = 0;
                if (f->parent_active && !f->taken) { edepth = 0; cond = eval_text(arg) != 0; }
            } else {
                f->seen_else = 1;
            }
            f->active = f->parent_active && !f->taken && cond;
            if (f->active) f->taken = 1;
        } else if (!strcmp(word, "endif")) {
            if (depth == 0) { printf("error: line %d: unexpected #endif\n", lineno); return 0; }
            depth--;
        } else if (!active) {
            continue;                                   /* other directives are ignored when inactive */
        } else if (!strcmp(word, "define")) {
            char name[64] = {0};
            int nl = 0;
            while ((isalnum((unsigned char)*arg) || *arg == '_') && nl < 63) name[nl++] = *arg++;
            while (*arg == ' ' || *arg == '\t') arg++;
            define(name, arg);
        } else if (!strcmp(word, "undef")) {
            undef(arg);
        } else if (!strcmp(word, "error")) {
            printf("error: %s\n", arg);
            return 0;
        }
    }
    if (depth > 0) printf("error: unterminated #if\n");
    return 0;
}
```

**How it mirrors the real preprocessor:**
- **A stack of conditional frames.** Each `#if` pushes the parent's activity, whether this branch is active, whether any branch has been taken, and whether `#else` was seen. `#elif`/`#else` flip the activity using those flags, and `#endif` pops. Inactive regions still push and pop frames, so nesting stays correct, but nothing inside them is evaluated.
- **`#if` evaluation** is a precedence-climbing recursive-descent parser. Undefined identifiers become 0, which is the source of the silent-misconfiguration bugs that `-Wundef` exists to catch.
- **Expansion with a "currently expanding" stack** implements C's rule that a macro isn't re-expanded inside its own replacement, which prevents infinite recursion for `#define X X+1`.
- Real preprocessors add function-like macros with argument pre-expansion, `#`/`##`, `#include` and line markers, but the control structure is exactly this.
