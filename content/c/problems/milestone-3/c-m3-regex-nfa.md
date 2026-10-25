---
id: c-m3-regex-nfa
title: A Linear-Time Regex Engine (Thompson NFA)
difficulty: Expert
order: 3
tags: parsing, recursive descent, automata, NFA simulation, dynamic memory, algorithms
time_limit: 4
---
## Statement
Backtracking regex engines (PCRE, Python's `re`, Perl) can take **exponential** time: matching `(a?){30}a{30}` against `aaaa…a` takes many seconds. Ken Thompson's 1968 construction compiles a regex into an NFA and simulates all paths simultaneously, matching in **O(pattern × text)**. RE2, Go's `regexp` and Rust's `regex` work this way. Implement it.

**Syntax**
- Literals are any printable character except `.*+?|()\`. `\c` escapes any character `c`.
- `.` matches any character.
- `*`, `+` and `?` apply postfix to the preceding atom, and may be stacked (`a*?` means `(a*)?`).
- `|` is alternation (lowest precedence), concatenation is implicit, and parentheses group.
- An **empty pattern** matches only the empty string.

**Syntax errors** (compile returns -1):
- unbalanced parentheses;
- a quantifier with nothing before it (`*a`, `(+a)`, `a|*b`);
- an empty alternative or empty group (`a|`, `|a`, `a||b`, `()`);
- a trailing backslash.

**API**
- `int re_compile(const char *pattern, Regex **out)`: 0 on success.
- `int re_match(const Regex *re, const char *text)`: 1 if the **entire** text matches.
- `void re_free(Regex *re)` accepts NULL.

Patterns reach 1,000 characters and texts reach 100,000.

## Starter
```c
#include <stdlib.h>
#include <string.h>

typedef struct Regex { char *pat; } Regex;

static int match_here(const char *p, const char *t) {          /* backtracking: exponential, no | or () */
    if (!*p) return !*t;
    if (p[1] == '*') { do { if (match_here(p + 2, t)) return 1; } while (*t && (*t++ == *p || *p == '.')); return 0; }
    if (*t && (*p == '.' || *p == *t)) return match_here(p + 1, t + 1);
    return 0;
}
int re_compile(const char *pattern, Regex **out) {
    *out = malloc(sizeof **out);
    (*out)->pat = malloc(strlen(pattern) + 1);
    strcpy((*out)->pat, pattern);
    return 0;
}
int re_match(const Regex *re, const char *text) { return match_here(re->pat, text); }
void re_free(Regex *re) { if (re) { free(re->pat); free(re); } }
```

## Driver
```c
#include <stdio.h>

static void check(const char *pat, const char *const *texts, int n) {
    Regex *re = NULL;
    if (re_compile(pat, &re) != 0) { printf("%-16s syntax error\n", pat); return; }
    printf("%-16s", pat);
    for (int i = 0; i < n; i++) printf(" %s:%d", texts[i][0] ? texts[i] : "''", re_match(re, texts[i]));
    printf("\n");
    re_free(re);
}

int main(void) {
    char cmd[16];
    while (scanf("%15s", cmd) == 1) {
        if (!strcmp(cmd, "basic")) {
            const char *t1[] = {"abc", "ab", "abcd", ""};
            check("abc", t1, 4);
            const char *t2[] = {"", "a", "aaaa", "b"};
            check("a*", t2, 4); check("a+", t2, 4); check("a?", t2, 4);
            const char *t3[] = {"cat", "dog", "cow", "catdog", ""};
            check("cat|dog", t3, 5); check("(cat|dog)+", t3, 5); check("c(a|o)(t|w)", t3, 5);
            const char *t4[] = {"x.y", "xzy", "x", "x.yz"};
            check("x\\.y", t4, 4); check("x.y", t4, 4); check("x.*", t4, 4);
            const char *t5[] = {"", "a", "ab"};
            check("", t5, 3); check("a**", t5, 3); check("(a|b)*?", t5, 3);
        } else if (!strcmp(cmd, "errors")) {
            const char *pats[] = {"(ab", "ab)", "*a", "a|", "|a", "a||b", "()", "a\\", "(+a)", "a|*b", "((a)", "\\(\\)"};
            const char *t[] = {"()", "a"};
            for (int i = 0; i < 12; i++) check(pats[i], t, 2);
        } else if (!strcmp(cmd, "robot")) {
            const char *topics[] = {"/robot1/scan", "/robot12/odom", "/robot/scan", "/robotX/cmd_vel", "/robot7/camera/image_raw"};
            check("/robot(0|1|2|3|4|5|6|7|8|9)+/(scan|odom)", topics, 5);
            check("/robot.*/camera/.*", topics, 5);
            const char *nums[] = {"3.14", "-0.5", "10", "1.", ".5", "+7.25e"};
            check("(\\+|-)?(0|1|2|3|4|5|6|7|8|9)+(\\.(0|1|2|3|4|5|6|7|8|9)+)?", nums, 6);
        } else if (!strcmp(cmd, "evil")) {
            int n; if (scanf("%d", &n) != 1) return 1;
            char *pat = malloc((size_t)n * 3 + (size_t)n + 1), *txt = malloc((size_t)n + 2);
            char *p = pat;
            for (int i = 0; i < n; i++) { *p++ = 'a'; *p++ = '?'; }
            for (int i = 0; i < n; i++) *p++ = 'a';
            *p = 0;
            memset(txt, 'a', (size_t)n); txt[n] = 0;
            Regex *re; re_compile(pat, &re);
            int m1 = re_match(re, txt);
            txt[n - 1] = 0; int m2 = re_match(re, txt);
            printf("(a?)^%d a^%d: full=%d short=%d\n", n, n, m1, m2);
            re_free(re); free(pat); free(txt);
        } else if (!strcmp(cmd, "long")) {
            Regex *re; re_compile("(a|b)*abb(a|b)*", &re);
            size_t n = 100000; char *t = malloc(n + 1);
            unsigned x = 1; for (size_t i = 0; i < n; i++) { x = x * 1103515245u + 12345u; t[i] = ((x >> 16) & 1) ? 'a' : 'b'; }
            t[n] = 0;
            int a = re_match(re, t);
            for (size_t i = 0; i < n; i++) t[i] = (i % 2) ? 'a' : 'b';
            int b = re_match(re, t);
            re_free(re);
            re_compile("(x+x+)+y", &re);
            memset(t, 'x', 5000); t[5000] = 0;
            int c = re_match(re, t);
            t[4999] = 'y'; int d = re_match(re, t);
            printf("random has abb: %d, alternating: %d, (x+x+)+y no: %d yes: %d\n", a, b, c, d);
            re_free(re); free(t); re_free(NULL);
        }
    }
    return 0;
}
```

## Tests
=== sample
basic
---
abc              abc:1 ab:0 abcd:0 '':0
a*               '':1 a:1 aaaa:1 b:0
a+               '':0 a:1 aaaa:1 b:0
a?               '':1 a:1 aaaa:0 b:0
cat|dog          cat:1 dog:1 cow:0 catdog:0 '':0
(cat|dog)+       cat:1 dog:1 cow:0 catdog:1 '':0
c(a|o)(t|w)      cat:1 dog:0 cow:1 catdog:0 '':0
x\.y             x.y:1 xzy:0 x:0 x.yz:0
x.y              x.y:1 xzy:1 x:0 x.yz:0
x.*              x.y:1 xzy:1 x:1 x.yz:1
                 '':1 a:0 ab:0
a**              '':1 a:1 ab:0
(a|b)*?          '':1 a:1 ab:1
=== hidden
errors
---
(ab              syntax error
ab)              syntax error
*a               syntax error
a|               syntax error
|a               syntax error
a||b             syntax error
()               syntax error
a\               syntax error
(+a)             syntax error
a|*b             syntax error
((a)             syntax error
\(\)             ():1 a:0
=== hidden
robot
---
/robot(0|1|2|3|4|5|6|7|8|9)+/(scan|odom) /robot1/scan:1 /robot12/odom:1 /robot/scan:0 /robotX/cmd_vel:0 /robot7/camera/image_raw:0
/robot.*/camera/.* /robot1/scan:0 /robot12/odom:0 /robot/scan:0 /robotX/cmd_vel:0 /robot7/camera/image_raw:1
(\+|-)?(0|1|2|3|4|5|6|7|8|9)+(\.(0|1|2|3|4|5|6|7|8|9)+)? 3.14:1 -0.5:1 10:1 1.:0 .5:0 +7.25e:0
=== hidden
evil 1000
---
(a?)^1000 a^1000: full=1 short=0
=== hidden
long
---
random has abb: 1, alternating: 0, (x+x+)+y no: 0 yes: 1

## Hints
- Write a recursive-descent parser. `alt := concat ('|' concat)*`, `concat := repeat+`, `repeat := atom ('*' | '+' | '?')*`, and `atom := literal | '.' | '\' c | '(' alt ')'`. Each function returns an NFA **fragment**: a start state plus a list of dangling exits to patch later.
- The states needed are `CHAR c`, `ANY`, `SPLIT(out, out1)` and `MATCH`. A pattern of length m needs at most about 2m+2 states, so allocate the array once and never `realloc` (dangling-exit pointers would be invalidated).
- Simulation: keep a current and a next list of states. `addstate` follows `SPLIT`s recursively, and a per-state "last added in step k" stamp prevents duplicates. After the whole text, the match succeeds if `MATCH` is in the list.
- Stacked quantifiers like `a**` produce `SPLIT` loops with no input in between. The duplicate stamp makes `addstate` terminate.

## Solution
```c
#include <stdlib.h>
#include <string.h>

enum { S_CHAR, S_ANY, S_SPLIT, S_MATCH };
typedef struct { int type, c, out, out1, mark; } State;

typedef struct Regex {
    State *st;
    int nst, start;
    int *clist, *nlist;
} Regex;

void re_free(Regex *re);

typedef struct { int start; int *holes; int nholes; } Frag;   /* holes: indices of int fields to patch, encoded state*2+which */

typedef struct { const char *p; State *st; int nst, cap, err; } Parser;

static int new_state(Parser *ps, int type, int c, int out, int out1) {
    if (ps->nst >= ps->cap) { ps->err = 1; return 0; }
    ps->st[ps->nst] = (State){ type, c, out, out1, -1 };
    return ps->nst++;
}

static Frag frag(int start, int hole) {
    Frag f = { start, malloc(sizeof(int)), 1 };
    f.holes[0] = hole;
    return f;
}

static void patch(Parser *ps, Frag *f, int target) {
    for (int i = 0; i < f->nholes; i++) {
        State *s = &ps->st[f->holes[i] / 2];
        if (f->holes[i] % 2) s->out1 = target; else s->out = target;
    }
    free(f->holes);
    f->holes = NULL; f->nholes = 0;
}

static Frag merge_holes(Frag a, Frag b, int start) {          /* union of exits */
    Frag f = { start, realloc(a.holes, sizeof(int) * (size_t)(a.nholes + b.nholes)), a.nholes + b.nholes };
    memcpy(f.holes + a.nholes, b.holes, sizeof(int) * (size_t)b.nholes);
    free(b.holes);
    return f;
}

static Frag parse_alt(Parser *ps);

static Frag parse_atom(Parser *ps) {
    Frag bad = { -1, NULL, 0 };
    char ch = *ps->p;
    if (ch == '(') {
        ps->p++;
        if (*ps->p == ')') { ps->err = 1; return bad; }         /* empty group */
        Frag f = parse_alt(ps);
        if (ps->err) return f;
        if (*ps->p != ')') { ps->err = 1; return f; }
        ps->p++;
        return f;
    }
    if (ch == '\0' || ch == ')' || ch == '|' || ch == '*' || ch == '+' || ch == '?') { ps->err = 1; return bad; }
    ps->p++;
    if (ch == '\\') {
        if (*ps->p == '\0') { ps->err = 1; return bad; }
        ch = *ps->p++;
        int s = new_state(ps, S_CHAR, (unsigned char)ch, -1, -1);
        return frag(s, s * 2);
    }
    int s = ch == '.' ? new_state(ps, S_ANY, 0, -1, -1) : new_state(ps, S_CHAR, (unsigned char)ch, -1, -1);
    return frag(s, s * 2);
}

static Frag parse_repeat(Parser *ps) {
    Frag f = parse_atom(ps);
    while (!ps->err && (*ps->p == '*' || *ps->p == '+' || *ps->p == '?')) {
        char q = *ps->p++;
        int s = new_state(ps, S_SPLIT, 0, f.start, -1);
        if (ps->err) break;
        if (q == '*') {                    /* s -> f -> back to s; exit via s.out1 */
            patch(ps, &f, s);
            f = frag(s, s * 2 + 1);
        } else if (q == '+') {             /* f -> s -> back to f; exit via s.out1 */
            patch(ps, &f, s);
            f = (Frag){ f.start, NULL, 0 };
            Frag e = frag(s, s * 2 + 1);
            e.start = f.start;
            f = e;
        } else {                           /* s -> f | skip */
            Frag skip = frag(s, s * 2 + 1);
            f = merge_holes(f, skip, s);
        }
    }
    return f;
}

static Frag parse_concat(Parser *ps) {
    Frag f = parse_repeat(ps);
    while (!ps->err && *ps->p && *ps->p != '|' && *ps->p != ')') {
        Frag g = parse_repeat(ps);
        if (ps->err) { free(g.holes); break; }
        patch(ps, &f, g.start);
        f.holes = g.holes; f.nholes = g.nholes;
    }
    return f;
}

static Frag parse_alt(Parser *ps) {
    Frag f = parse_concat(ps);
    while (!ps->err && *ps->p == '|') {
        ps->p++;
        Frag g = parse_concat(ps);
        if (ps->err) { free(g.holes); break; }
        int s = new_state(ps, S_SPLIT, 0, f.start, g.start);
        f = merge_holes(f, g, s);
    }
    return f;
}

int re_compile(const char *pattern, Regex **out) {
    *out = NULL;
    size_t len = strlen(pattern);
    Parser ps = { pattern, malloc(sizeof(State) * (2 * len + 4)), 0, (int)(2 * len + 4), 0 };
    if (!ps.st) return -1;
    int start;
    if (len == 0) {
        start = new_state(&ps, S_MATCH, 0, -1, -1);
    } else {
        Frag f = parse_alt(&ps);
        if (!ps.err && *ps.p != '\0') ps.err = 1;              /* e.g. unmatched ')' */
        if (ps.err) { free(f.holes); free(ps.st); return -1; }
        int m = new_state(&ps, S_MATCH, 0, -1, -1);
        patch(&ps, &f, m);
        start = f.start;
    }
    Regex *re = malloc(sizeof *re);
    if (!re) { free(ps.st); return -1; }
    re->st = ps.st; re->nst = ps.nst; re->start = start;
    re->clist = malloc(sizeof(int) * (size_t)ps.nst);
    re->nlist = malloc(sizeof(int) * (size_t)ps.nst);
    if (!re->clist || !re->nlist) { re_free(re); return -1; }
    *out = re;
    return 0;
}

static void addstate(State *st, int *list, int *n, int s, int gen) {
    if (s < 0 || st[s].mark == gen) return;
    st[s].mark = gen;
    if (st[s].type == S_SPLIT) {
        addstate(st, list, n, st[s].out, gen);
        addstate(st, list, n, st[s].out1, gen);
    } else {
        list[(*n)++] = s;
    }
}

int re_match(const Regex *re, const char *text) {
    State *st = re->st;
    for (int i = 0; i < re->nst; i++) st[i].mark = -1;
    int *cl = re->clist, *nl = re->nlist, cn = 0, gen = 0;
    addstate(st, cl, &cn, re->start, gen);
    for (const unsigned char *t = (const unsigned char *)text; *t && cn; t++) {
        int nn = 0;
        gen++;
        for (int i = 0; i < cn; i++) {
            const State *s = &st[cl[i]];
            if ((s->type == S_CHAR && s->c == *t) || s->type == S_ANY) addstate(st, nl, &nn, s->out, gen);
        }
        int *tmp = cl; cl = nl; nl = tmp; cn = nn;
    }
    for (int i = 0; i < cn; i++) if (st[cl[i]].type == S_MATCH) return 1;
    return 0;
}

void re_free(Regex *re) {
    if (!re) return;
    free(re->st); free(re->clist); free(re->nlist);
    free(re);
}
```

- **Thompson's construction** turns each operator into a small fragment wired with `SPLIT` states. The NFA has O(m) states, and each text character advances the whole set of live states at once.
- **No backtracking, so no blowup**: the simulation is O(m·n) in the worst case. `(a?){1000}a{1000}` and the catastrophic `(x+x+)+y` finish instantly, where a backtracking engine would effectively never finish. Only a constant-time "already in this set" check per state is needed, using a generation stamp instead of clearing an array every step.
- **Recursive descent** mirrors the grammar's precedence directly (alternation < concatenation < postfix quantifiers) and makes precise syntax errors easy.
- **Pre-sized state storage** (at most about 2m+2 states) means patch locations never move, so fragments can hold their dangling exits as indices.
- **Full-match semantics**: the text must end with `MATCH` in the live set. Search mode would add an implicit `.*` at both ends.
