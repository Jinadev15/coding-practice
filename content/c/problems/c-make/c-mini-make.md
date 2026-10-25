---
id: c-mini-make
title: Make's Rebuild Algorithm
difficulty: Hard
order: 1
tags: make, dependency graph, DFS, timestamps, phony targets, cycle detection
time_limit: 3
---
## Statement
Implement the heart of GNU Make: given the dependency graph, file timestamps and phony targets, decide **which recipes run, and in what order**, to bring a goal up to date.

```c
typedef struct {
    const char *name;
    long mtime;          /* modification time; -1 = the file does not exist */
    bool has_rule;       /* the Makefile has a rule (recipe) for it */
    bool phony;          /* listed in .PHONY (always has a rule) */
    int ndeps;
    const int *deps;     /* prerequisite indices, in Makefile order */
} Node;

int make_plan(const Node *nodes, int n, int goal, int *order, int *bad);
```

Algorithm, a depth-first post-order walk from `goal`:
- Visit each node **at most once**. Prerequisites are visited in listed order, before the target is decided.
- Reaching a node that's still being visited is a **cycle**: set `*bad` to that node and return **-1**.
- A node **without a rule** is a source file. If it doesn't exist, set `*bad` to it and return **-2** ("no rule to make target"). Otherwise it's never rebuilt.
- A node with a rule is **rebuilt** if any of these hold:
  - it's phony;
  - it doesn't exist;
  - any prerequisite is phony;
  - any prerequisite's (current) mtime is newer than its own.
- Rebuilding appends the node to `order`. A non-phony rebuilt node gets a new mtime from a clock that starts at `1 + (largest mtime in the input)` and increments by 1 per rebuild. Its dependants then see it as newer. Phony nodes have no timestamp.
- Stop at the **first** error. On success, return the number of entries in `order`.

Don't modify `nodes`. Keep your own arrays (up to 300,000 nodes, dependency depth up to a few thousand).

## Starter
```c
#include <stdbool.h>
#include <stdlib.h>

typedef struct {
    const char *name;
    long mtime;
    bool has_rule;
    bool phony;
    int ndeps;
    const int *deps;
} Node;

int make_plan(const Node *nodes, int n, int goal, int *order, int *bad) {
    /* rebuild everything that has a rule, in index order */
    (void)goal; (void)bad;
    int k = 0;
    for (int i = n - 1; i >= 0; i--) if (nodes[i].has_rule) order[k++] = i;
    return k;
}
```

## Driver
```c
#include <stdio.h>
#include <string.h>

static char names[400000][16];
static Node N[400000];
static int pool[2000000], order[400000];

static int find(int n, const char *s) { for (int i = 0; i < n; i++) if (!strcmp(names[i], s)) return i; return -1; }

static void report(int n, int goal, int show) {
    int bad = -7;
    int r = make_plan(N, n, goal, order, &bad);
    if (r == -1) { printf("error: circular dependency at %s\n", names[bad]); return; }
    if (r == -2) { printf("error: no rule to make target '%s'\n", names[bad]); return; }
    if (show) {
        if (r == 0) printf("'%s' is up to date.\n", names[goal]);
        for (int i = 0; i < r; i++) printf("run %s\n", names[order[i]]);
    } else {
        unsigned long long h = 1469598103934665603ull;
        for (int i = 0; i < r; i++) h = (h ^ (unsigned)order[i]) * 1099511628211ull;
        printf("%d recipes, hash %016llx, first %s, last %s\n", r, h, r ? names[order[0]] : "-", r ? names[order[r - 1]] : "-");
    }
}

int main(void) {
    char cmd[16];
    while (scanf("%15s", cmd) == 1) {
        if (!strcmp(cmd, "graph")) {
            int n, used = 0; if (scanf("%d", &n) != 1) return 1;
            int dl[64][32], dc[64];
            for (int i = 0; i < n; i++) {
                char flags[8];
                if (scanf("%15s %ld %7s %d", names[i], &N[i].mtime, flags, &dc[i]) != 4) return 1;
                N[i].name = names[i];
                N[i].has_rule = strchr(flags, 'r') != NULL;
                N[i].phony = strchr(flags, 'p') != NULL;
                for (int k = 0; k < dc[i]; k++) { char d[16]; if (scanf("%15s", d) != 1) return 1; dl[i][k] = -1; strcpy((char *)&pool[1900000 + 4 * (i * 32 + k)], d); }
            }
            for (int i = 0; i < n; i++) {
                N[i].deps = &pool[used]; N[i].ndeps = dc[i];
                for (int k = 0; k < dc[i]; k++) pool[used++] = find(n, (char *)&pool[1900000 + 4 * (i * 32 + k)]);
                (void)dl;
            }
            int q; if (scanf("%d", &q) != 1) return 1;
            while (q--) { char g[16]; if (scanf("%15s", g) != 1) return 1; printf("$ make %s\n", g); report(n, find(n, g), 1); }
        } else if (!strcmp(cmd, "gen")) {
            int n; unsigned seed, cyc; if (scanf("%d %u %u", &n, &seed, &cyc) != 3) return 1;
            unsigned x = seed; int used = 0;
#define R() (x ^= x << 13, x ^= x >> 17, x ^= x << 5, x)
            const int W = 100, layers = (n - 1 + W - 1) / W;
            for (int i = 1; i < n; i++) {
                int layer = (i - 1) / W;
                snprintf(names[i], 16, "f%d", i);
                N[i].name = names[i];
                N[i].deps = &pool[used];
                if (layer == layers - 1) { N[i].has_rule = false; N[i].phony = false; N[i].ndeps = 0; N[i].mtime = 1000 + (long)(R() % 5000); continue; }
                N[i].has_rule = true; N[i].phony = R() % 50 == 0;
                N[i].mtime = R() % 7 == 0 ? -1 : 1000 + (long)(R() % 6000);
                int k = 1 + (int)(R() % 4);
                for (int j = 0; j < k; j++) {
                    int lo = 1 + (layer + 1) * W, hi = lo + W - 1; if (hi > n - 1) hi = n - 1; if (lo > hi) break;
                    pool[used++] = lo + (int)(R() % (unsigned)(hi - lo + 1));
                }
                if (cyc && R() % 20000 == 0 && layer > 0) pool[used++] = 1 + (int)(R() % (unsigned)(layer * W));
                N[i].ndeps = (int)(&pool[used] - N[i].deps);
            }
            strcpy(names[0], "all"); N[0].name = names[0]; N[0].has_rule = N[0].phony = true; N[0].mtime = -1;
            N[0].deps = &pool[used]; N[0].ndeps = 0;
            for (int i = 1; i <= W && i < n; i++) { pool[used++] = i; N[0].ndeps++; }
            report(n, 0, 0);
        }
    }
    return 0;
}
```

## Tests
=== sample
graph 6
robot 100 r 2 main.o motor.o
main.o 90 r 2 main.c motor.h
motor.o 50 r 2 motor.c motor.h
main.c 80 - 0
motor.c 60 - 0
motor.h 40 - 0
3 robot main.o motor.c
---
$ make robot
run motor.o
run robot
$ make main.o
'main.o' is up to date.
$ make motor.c
'motor.c' is up to date.
=== hidden
graph 9
all -1 rp 2 robot test
robot 500 r 2 a.o b.o
a.o 400 r 1 a.c
b.o -1 r 1 b.c
a.c 300 - 0
b.c 450 - 0
test -1 rp 1 robot
clean -1 rp 0
docs 999 r 1 robot
4 all robot docs clean
---
$ make all
run b.o
run robot
run test
run all
$ make robot
run b.o
run robot
$ make docs
run b.o
run robot
run docs
$ make clean
run clean
=== hidden
graph 8
app 10 r 2 x.o y.o
x.o 10 r 1 gen.h
y.o 10 r 1 y.c
gen.h 10 r 1 x.o
y.c 5 - 0
lib 10 r 1 missing.c
z 10 r 2 y.o lib
missing.c -1 - 0
4 app y.o lib z
---
$ make app
error: circular dependency at x.o
$ make y.o
'y.o' is up to date.
$ make lib
error: no rule to make target 'missing.c'
$ make z
error: no rule to make target 'missing.c'
=== hidden
gen 300000 7 0
gen 250000 99 0
---
267595 recipes, hash 3d0c421bf61aef12, first f299838, last all
223183 recipes, hash 6b6472c269153b4a, first f249727, last all
=== hidden
gen 300000 4242 1
---
error: circular dependency at f51778

## Hints
- Keep a per-node state array: 0 unvisited, 1 on the DFS stack, 2 done. Also keep a `long cur[n]` initialised from `mtime`.
- Recursive DFS is fine here: the depth is bounded by the number of layers, a few thousand. Real Make is recursive too.
- Decide after the prerequisites: `rebuild = phony || cur[t] < 0 || any(phony[d] || cur[d] > cur[t])`.
- Allocate the arrays with `calloc` and free them on every return path. Errors return early.

## Solution
```c
#include <stdbool.h>
#include <stdlib.h>

typedef struct {
    const char *name;
    long mtime;
    bool has_rule;
    bool phony;
    int ndeps;
    const int *deps;
} Node;

typedef struct {
    const Node *nodes;
    unsigned char *state;      /* 0 new, 1 visiting, 2 done */
    long *cur;                 /* current timestamps */
    long clock;
    int *order, count, *bad;
} Ctx;

static int visit(Ctx *c, int t) {
    if (c->state[t] == 2) return 0;
    if (c->state[t] == 1) { *c->bad = t; return -1; }          /* back edge: cycle */
    c->state[t] = 1;
    const Node *nd = &c->nodes[t];
    for (int k = 0; k < nd->ndeps; k++) {
        int r = visit(c, nd->deps[k]);
        if (r) return r;
    }
    c->state[t] = 2;
    if (!nd->has_rule) {
        if (c->cur[t] < 0) { *c->bad = t; return -2; }          /* source file missing */
        return 0;
    }
    bool rebuild = nd->phony || c->cur[t] < 0;
    for (int k = 0; k < nd->ndeps && !rebuild; k++) {
        int d = nd->deps[k];
        rebuild = c->nodes[d].phony || c->cur[d] > c->cur[t];
    }
    if (rebuild) {
        c->order[c->count++] = t;
        if (!nd->phony) c->cur[t] = c->clock++;                 /* freshly built: newest file */
    }
    return 0;
}

int make_plan(const Node *nodes, int n, int goal, int *order, int *bad) {
    Ctx c = { nodes, calloc((size_t)n, 1), malloc((size_t)n * sizeof(long)), 0, order, 0, bad };
    if (!c.state || !c.cur) { free(c.state); free(c.cur); return -3; }
    long mx = 0;
    for (int i = 0; i < n; i++) { c.cur[i] = nodes[i].mtime; if (nodes[i].mtime > mx) mx = nodes[i].mtime; }
    c.clock = mx + 1;
    int r = visit(&c, goal);
    free(c.state);
    free(c.cur);
    return r ? r : c.count;
}
```

- **Post-order DFS** builds prerequisites before dependants, the same order Make prints recipes in with `-j1`. Independent subtrees could run in parallel (`-j`) as soon as their own prerequisites finish.
- **Memoisation** (state 2) means each node is decided once, even though `motor.h` is a prerequisite of many objects. That keeps the walk O(V + E).
- **Three-colour marking** detects cycles. A grey (on-stack) node reached again is a back edge. GNU Make warns "Circular … dependency dropped". This exercise reports it as an error.
- **New timestamps** propagate staleness: rebuilding `motor.o` gives it the newest time, which forces `robot` to relink in the same run.
- **Phony targets** have no file, so they always run, and anything that depends on them always runs. That's why `docs` reruns whenever `robot` is in the plan, and why real Makefiles never make file targets depend on phony ones.
