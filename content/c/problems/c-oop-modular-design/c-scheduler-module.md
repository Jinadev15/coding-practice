---
id: c-scheduler-module
title: A Cooperative Task Scheduler Module (Multi-File)
difficulty: Hard
order: 1
tags: modular design, opaque types, callbacks, void* context, re-entrancy, time wrap, multi-file
time_limit: 3
---
## Statement
Firmware runs periodic jobs: a 100 Hz control loop, a 10 Hz telemetry sender, a 1 Hz battery check. Implement the reusable **scheduler module** behind the given header. It knows nothing about its clients: they register callbacks with a `void *ctx` (dependency inversion in C).

```c
typedef struct Scheduler Scheduler;
typedef void (*TaskFn)(void *ctx, uint32_t now_ms);
```

| Function | Contract |
|---|---|
| `sched_create(max_tasks)` | NULL if `max_tasks == 0` or allocation fails. |
| `sched_destroy(s)` | Accepts NULL. |
| `sched_add(s, period_ms, first_ms, fn, ctx)` | Registers a task that is first due at absolute time `first_ms`, then every `period_ms`. Returns its id: ids start at 0 and **increase, never reused**. Returns -1 if the scheduler is full, `period_ms == 0`, or `fn` is NULL. |
| `sched_cancel(s, id)` | 0, or -1 if there's no such active task. It may be called **from inside a callback**, including on the running task itself. |
| `sched_tick(s, now_ms)` | Runs every task that is due (`now - due >= 0`, compared **wrap-safely** as a signed 32-bit difference), ordered by due time, then id, each **at most once** per tick. Returns the number of callbacks run. |
| `sched_overruns(s, id)`, `sched_count(s)` | See the rules below. |

Rules for `sched_tick`:
- After a task runs, its next due time advances by whole periods until it's **after** `now`. The number of periods skipped beyond the one just served adds to that task's **overrun** counter.
- Tasks **added** during a tick don't run in that tick.
- Tasks **cancelled** during a tick before their turn don't run.
- `sched_overruns(s, id)` returns the overrun count, or 0 for unknown ids. `sched_count(s)` returns the number of active tasks.

## Starter: scheduler.h
```c
#ifndef SCHEDULER_H
#define SCHEDULER_H
#include <stdint.h>

typedef struct Scheduler Scheduler;
typedef void (*TaskFn)(void *ctx, uint32_t now_ms);

Scheduler *sched_create(unsigned max_tasks);
void       sched_destroy(Scheduler *s);
int        sched_add(Scheduler *s, uint32_t period_ms, uint32_t first_ms, TaskFn fn, void *ctx);
int        sched_cancel(Scheduler *s, int id);
unsigned   sched_tick(Scheduler *s, uint32_t now_ms);
unsigned   sched_overruns(const Scheduler *s, int id);
unsigned   sched_count(const Scheduler *s);
#endif
```

## Starter: scheduler.c
```c
#include "scheduler.h"
#include <stdlib.h>

typedef struct { uint32_t period, due; TaskFn fn; void *ctx; } Task;
struct Scheduler { Task t[64]; unsigned n; };

Scheduler *sched_create(unsigned max_tasks) { (void)max_tasks; return calloc(1, sizeof(Scheduler)); }
void sched_destroy(Scheduler *s) { free(s); }
int sched_add(Scheduler *s, uint32_t period_ms, uint32_t first_ms, TaskFn fn, void *ctx) {
    s->t[s->n] = (Task){ period_ms, first_ms, fn, ctx };
    return (int)s->n++;
}
int sched_cancel(Scheduler *s, int id) { (void)s; (void)id; return -1; }
unsigned sched_tick(Scheduler *s, uint32_t now_ms) {
    unsigned ran = 0;
    for (unsigned i = 0; i < s->n; i++)
        if (now_ms >= s->t[i].due) { s->t[i].fn(s->t[i].ctx, now_ms); s->t[i].due += s->t[i].period; ran++; }
    return ran;
}
unsigned sched_overruns(const Scheduler *s, int id) { (void)s; (void)id; return 0; }
unsigned sched_count(const Scheduler *s) { return s->n; }
```

## Driver: main.c
```c
#include "scheduler.h"
#include <stdio.h>
#include <string.h>

static char logbuf[1 << 16];
static size_t logn;
static void logf_(const char *s) { size_t k = strlen(s); if (logn + k < sizeof logbuf) { memcpy(logbuf + logn, s, k); logn += k; logbuf[logn] = 0; } }

typedef struct { const char *name; int count; } Counter;
static void count_task(void *ctx, uint32_t now) {
    Counter *c = ctx; char b[64]; c->count++;
    snprintf(b, sizeof b, "%s@%u ", c->name, (unsigned)now); logf_(b);
}

static Scheduler *G; static int victim_id, self_id, spawned = 0;
static void killer(void *ctx, uint32_t now) { (void)ctx; char b[64]; snprintf(b, sizeof b, "killer@%u ", (unsigned)now); logf_(b); sched_cancel(G, victim_id); }
static void victim(void *ctx, uint32_t now) { (void)ctx; char b[64]; snprintf(b, sizeof b, "victim@%u ", (unsigned)now); logf_(b); }
static void once(void *ctx, uint32_t now) { (void)ctx; char b[64]; snprintf(b, sizeof b, "once@%u ", (unsigned)now); logf_(b); sched_cancel(G, self_id); }
static void spawner(void *ctx, uint32_t now) {
    static Counter child = { "child", 0 };
    (void)ctx; char b[64]; snprintf(b, sizeof b, "spawner@%u ", (unsigned)now); logf_(b);
    if (!spawned) { spawned = 1; sched_add(G, 5, now, count_task, &child); }   /* due now, but must wait for the next tick */
}

int main(void) {
    char cmd[32];
    while (scanf("%31s", cmd) == 1) {
        logn = 0; logbuf[0] = 0;
        if (!strcmp(cmd, "basic")) {
            Scheduler *s = sched_create(4);
            Counter fast = { "fast", 0 }, slow = { "slow", 0 }, late = { "late", 0 };
            int a = sched_add(s, 10, 0, count_task, &fast), b = sched_add(s, 25, 5, count_task, &slow), c = sched_add(s, 7, 30, count_task, &late);
            int bad1 = sched_add(s, 0, 0, count_task, &fast), bad2 = sched_add(s, 5, 0, NULL, NULL);
            printf("ids %d %d %d invalid %d %d\n", a, b, c, bad1, bad2);
            for (uint32_t t = 0; t <= 60; t += 5) { unsigned r = sched_tick(s, t); if (r) { char x[32]; snprintf(x, sizeof x, "[t=%u ran %u] ", (unsigned)t, r); logf_(x); } }
            printf("%s\n", logbuf);
            printf("counts %d %d %d active %u\n", fast.count, slow.count, late.count, sched_count(s));
            int d = sched_add(s, 1, 0, count_task, &fast);
            int full = sched_add(s, 1, 0, count_task, &fast);
            printf("4th id %d, full: %d\n", d, full);
            int c1 = sched_cancel(s, b), c2 = sched_cancel(s, b), c3 = sched_cancel(s, 99);
            unsigned act = sched_count(s);
            int readd = sched_add(s, 3, 0, count_task, &slow);
            printf("cancel %d %d %d, active %u, re-add id %d\n", c1, c2, c3, act, readd);
            sched_destroy(s); sched_destroy(NULL);
            printf("create(0): %s\n", sched_create(0) ? "?" : "NULL");
        } else if (!strcmp(cmd, "overrun")) {
            Scheduler *s = sched_create(8);
            Counter c10 = { "c10", 0 }, c3 = { "c3", 0 };
            int i10 = sched_add(s, 10, 0, count_task, &c10), i3 = sched_add(s, 3, 1, count_task, &c3);
            uint32_t times[] = {0, 1, 4, 35, 36, 40, 100};
            for (int k = 0; k < 7; k++) sched_tick(s, times[k]);
            printf("%s\noverruns c10=%u c3=%u unknown=%u\n", logbuf, sched_overruns(s, i10), sched_overruns(s, i3), sched_overruns(s, 77));
            sched_destroy(s);
        } else if (!strcmp(cmd, "reentrant")) {
            G = sched_create(8);
            Counter dummy = { "dummy", 0 };
            sched_add(G, 10, 0, killer, NULL);
            victim_id = sched_add(G, 10, 0, victim, NULL);
            self_id = sched_add(G, 4, 2, once, NULL);
            sched_add(G, 100, 0, spawner, NULL);
            sched_add(G, 10, 0, count_task, &dummy);
            for (uint32_t t = 0; t <= 20; t += 2) sched_tick(G, t);
            printf("%s\nactive %u\n", logbuf, sched_count(G));
            sched_destroy(G);
        } else if (!strcmp(cmd, "wrap")) {
            Scheduler *s = sched_create(4);
            Counter w = { "w", 0 };
            sched_add(s, 1000, 4294966000u, count_task, &w);
            uint32_t t = 4294965000u;
            for (int k = 0; k < 8; k++, t += 700) sched_tick(s, t);
            printf("%s\ncount %d\n", logbuf, w.count);
            sched_destroy(s);
        } else if (!strcmp(cmd, "load")) {
            Scheduler *s = sched_create(500);
            static Counter cs[500];
            for (int i = 0; i < 500; i++) { cs[i].name = "x"; sched_add(s, 1 + (unsigned)i % 50, (unsigned)i % 13, count_task, &cs[i]); }
            unsigned long total = 0;
            for (uint32_t t = 0; t < 20000; t += 1 + t % 3) { total += sched_tick(s, t); logn = 0; }
            unsigned long ov = 0; for (int i = 0; i < 500; i++) ov += sched_overruns(s, i);
            printf("runs %lu overruns %lu c0 %d c499 %d\n", total, ov, cs[0].count, cs[499].count);
            sched_destroy(s);
        }
    }
    return 0;
}
```

## Tests
=== sample
basic
---
ids 0 1 2 invalid -1 -1
fast@0 [t=0 ran 1] slow@5 [t=5 ran 1] fast@10 [t=10 ran 1] fast@20 [t=20 ran 1] fast@30 slow@30 late@30 [t=30 ran 3] late@40 fast@40 [t=40 ran 2] late@45 [t=45 ran 1] fast@50 [t=50 ran 1] late@55 slow@55 [t=55 ran 2] late@60 fast@60 [t=60 ran 2] 
counts 7 3 5 active 3
4th id 3, full: -1
cancel 0 -1 -1, active 3, re-add id 4
create(0): NULL
=== hidden
overrun
---
c10@0 c3@1 c3@4 c3@35 c10@35 c3@40 c10@40 c3@100 c10@100 
overruns c10=7 c3=29 unknown=0
=== hidden
reentrant
---
killer@0 spawner@0 dummy@0 child@2 once@2 child@6 killer@10 dummy@10 child@10 child@16 killer@20 dummy@20 child@20 
active 4
=== hidden
wrap
---
w@4294966400 w@4294967100 w@1204 w@1904 
count 4
=== hidden
load
---
runs 833145 overruns 66641 c0 13334 c499 400

## Hints
- Store tasks in an array of `max_tasks` slots, each with an `active` flag, its id, period, due time, overruns, fn and ctx. Look slots up by id.
- `sched_tick`: first collect the **indices of the due, active tasks** into a temporary array (tasks added later aren't in it), and sort them by `(due, id)` with a wrap-safe comparison: `(int32_t)(a - b)`. Then run them one by one, **re-checking `active`** just before each call.
- Re-check the slot's id too, because a cancelled slot could be reused by an `add` inside a callback.
- Advancing: `uint32_t late = now - due; uint32_t k = late / period + 1; due += k * period; overruns += k - 1;`.

## Solution: scheduler.h
```c
#ifndef SCHEDULER_H
#define SCHEDULER_H
#include <stdint.h>

typedef struct Scheduler Scheduler;
typedef void (*TaskFn)(void *ctx, uint32_t now_ms);

Scheduler *sched_create(unsigned max_tasks);
void       sched_destroy(Scheduler *s);
int        sched_add(Scheduler *s, uint32_t period_ms, uint32_t first_ms, TaskFn fn, void *ctx);
int        sched_cancel(Scheduler *s, int id);
unsigned   sched_tick(Scheduler *s, uint32_t now_ms);
unsigned   sched_overruns(const Scheduler *s, int id);
unsigned   sched_count(const Scheduler *s);
#endif
```

## Solution: scheduler.c
```c
#include "scheduler.h"
#include <stdlib.h>

typedef struct {
    int active, id;
    uint32_t period, due;
    unsigned overruns;
    TaskFn fn;
    void *ctx;
} Task;

struct Scheduler {
    Task *tasks;
    unsigned cap;
    int next_id;
    unsigned *due_idx;            /* scratch array for one tick */
};

Scheduler *sched_create(unsigned max_tasks) {
    if (max_tasks == 0) return NULL;
    Scheduler *s = calloc(1, sizeof *s);
    if (!s) return NULL;
    s->tasks = calloc(max_tasks, sizeof *s->tasks);
    s->due_idx = calloc(max_tasks, sizeof *s->due_idx);
    if (!s->tasks || !s->due_idx) { free(s->tasks); free(s->due_idx); free(s); return NULL; }
    s->cap = max_tasks;
    return s;
}

void sched_destroy(Scheduler *s) {
    if (!s) return;
    free(s->tasks);
    free(s->due_idx);
    free(s);
}

static Task *find(const Scheduler *s, int id) {
    for (unsigned i = 0; i < s->cap; i++)
        if (s->tasks[i].active && s->tasks[i].id == id) return &s->tasks[i];
    return NULL;
}

int sched_add(Scheduler *s, uint32_t period_ms, uint32_t first_ms, TaskFn fn, void *ctx) {
    if (!s || period_ms == 0 || !fn) return -1;
    for (unsigned i = 0; i < s->cap; i++) {
        if (!s->tasks[i].active) {
            s->tasks[i] = (Task){ 1, s->next_id++, period_ms, first_ms, 0, fn, ctx };
            return s->tasks[i].id;
        }
    }
    return -1;
}

int sched_cancel(Scheduler *s, int id) {
    Task *t = s ? find(s, id) : NULL;
    if (!t) return -1;
    t->active = 0;
    return 0;
}

static int is_due(uint32_t now, uint32_t due) { return (int32_t)(now - due) >= 0; }   /* wrap-safe */

static int earlier(const Task *a, const Task *b) {
    int32_t d = (int32_t)(a->due - b->due);
    return d < 0 || (d == 0 && a->id < b->id);
}

unsigned sched_tick(Scheduler *s, uint32_t now_ms) {
    unsigned n = 0;
    for (unsigned i = 0; i < s->cap; i++)                       /* snapshot: later additions excluded */
        if (s->tasks[i].active && is_due(now_ms, s->tasks[i].due)) s->due_idx[n++] = i;
    for (unsigned i = 1; i < n; i++) {                          /* insertion sort by (due, id) */
        unsigned v = s->due_idx[i], j = i;
        while (j > 0 && earlier(&s->tasks[v], &s->tasks[s->due_idx[j - 1]])) { s->due_idx[j] = s->due_idx[j - 1]; j--; }
        s->due_idx[j] = v;
    }
    unsigned ran = 0;
    for (unsigned k = 0; k < n; k++) {
        Task *t = &s->tasks[s->due_idx[k]];
        if (!t->active) continue;                               /* cancelled earlier in this tick */
        const int id = t->id;
        uint32_t late = now_ms - t->due;
        uint32_t periods = late / t->period + 1;                /* first due time strictly after now */
        t->overruns += periods - 1;
        t->due += periods * t->period;
        t->fn(t->ctx, now_ms);                                  /* may cancel or add tasks */
        ran++;
        (void)id;
    }
    return ran;
}

unsigned sched_overruns(const Scheduler *s, int id) {
    const Task *t = s ? find(s, id) : NULL;
    return t ? t->overruns : 0;
}

unsigned sched_count(const Scheduler *s) {
    unsigned c = 0;
    if (s) for (unsigned i = 0; i < s->cap; i++) c += (unsigned)s->tasks[i].active;
    return c;
}
```

## Solution
- **Dependency inversion in C**: the scheduler stores `(fn, ctx)` pairs and never learns its clients' types. A control loop passes its own struct as `ctx`, and `scheduler.c` stays reusable across every product.
- **The opaque `Scheduler`** hides the slot array and scratch buffer. Clients can't corrupt task state, and the storage could become a heap or timer wheel without touching a single caller.
- **Re-entrancy by construction**: the due set is snapshotted *before* any callback runs, so tasks added mid-tick wait for the next tick. Each slot's `active` flag is re-checked at its turn, so cancellations (including self-cancellation) take effect immediately. The bookkeeping (`due`, `overruns`) is updated *before* calling out, so a callback that cancels its own task leaves no stale state.
- **Wrap-safe time**: every comparison uses the signed 32-bit difference, so a device running past 2³² ms (49.7 days) keeps scheduling correctly. The `wrap` test crosses the boundary.
- **Overrun accounting** skips missed periods instead of running a task several times in a burst, which is the usual policy for control loops (stale samples are useless) while still recording that deadlines were missed.
