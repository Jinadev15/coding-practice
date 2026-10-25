---
id: c-blocking-queue
title: Bounded Blocking Queue and a Parallel Worker Pool
difficulty: Hard
order: 1
tags: pthreads, mutex, condition variables, producer-consumer, shutdown, parallelism
time_limit: 4
---
## Statement
Build the concurrency core of a sensor-processing pipeline with POSIX threads.

```c
typedef struct BQueue BQueue;                 /* keep this typedef; you define the struct */
BQueue *bq_create(int capacity);
void bq_destroy(BQueue *q);
int  bq_push(BQueue *q, long item);           /* blocks while full; returns 0, or -1 if the queue is closed */
int  bq_pop(BQueue *q, long *item);           /* blocks while empty; returns 0, or -1 once closed AND empty */
void bq_close(BQueue *q);                     /* wake everyone: pushes fail, pops drain what's left, then fail */

long long parallel_prime_sum(long lo, long hi, int threads);
    /* sum of all primes in [lo, hi), computed by `threads` worker threads that pull chunks of
       1000 numbers from a BQueue fed by the calling thread */
```

Requirements:
- **No busy waiting**: use `pthread_cond_wait` in `while` loops.
- `bq_close` must wake **all** blocked producers and consumers (use `pthread_cond_broadcast`).
- No data races (the reference passes `-fsanitize=thread`). Items are delivered exactly once, and a single consumer sees a single producer's items in FIFO order.

The driver runs many producers and consumers at once and checks sums, counts, ordering, shutdown behaviour and real parallel speed-up.

## Starter
```c
#define _POSIX_C_SOURCE 200809L
#include <pthread.h>
#include <stdlib.h>
#include <stdio.h>

typedef struct BQueue BQueue;
struct BQueue { long *buf; int cap, head, count; };

BQueue *bq_create(int capacity) {
    BQueue *q = calloc(1, sizeof *q);
    q->buf = malloc(sizeof(long) * capacity);
    q->cap = capacity;
    return q;
}
void bq_destroy(BQueue *q) { free(q->buf); free(q); }
int bq_push(BQueue *q, long item) {
    if (q->count == q->cap) return -1;
    q->buf[(q->head + q->count++) % q->cap] = item;
    return 0;
}
int bq_pop(BQueue *q, long *item) {
    if (q->count == 0) return -1;
    *item = q->buf[q->head];
    q->head = (q->head + 1) % q->cap;
    q->count--;
    return 0;
}
void bq_close(BQueue *q) { (void)q; }
long long parallel_prime_sum(long lo, long hi, int threads) { (void)threads; long long s = 0;
    for (long n = lo; n < hi; n++) { int p = n > 1; for (long d = 2; d * d <= n && p; d++) if (n % d == 0) p = 0; if (p) s += n; } return s; }
```

## Driver
```c
#include <time.h>
#include <string.h>

typedef struct { BQueue *q; int id, count, ok; long long sum; } Arg;

static void *producer(void *p) {
    Arg *a = p;
    for (int i = 0; i < a->count; i++)
        if (bq_push(a->q, (long)a->id * 1000000 + i) == 0) a->sum += (long)a->id * 1000000 + i;
    return NULL;
}
static void *consumer(void *p) {
    Arg *a = p; long v; long last[16]; for (int i = 0; i < 16; i++) last[i] = -1;
    a->ok = 1;
    while (bq_pop(a->q, &v) == 0) {
        int pid = (int)(v / 1000000); long seq = v % 1000000;
        if (pid >= 0 && pid < 16) { if (seq <= last[pid]) a->ok = 0; last[pid] = seq; }   /* per-producer FIFO */
        a->sum += v; a->count++;
    }
    return NULL;
}
static double secs(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + t.tv_nsec / 1e9; }
static void *blocked_push(void *p) { Arg *a = p; a->ok = bq_push(a->q, 99); return NULL; }
static void *blocked_pop(void *p) { Arg *a = p; long v; a->ok = bq_pop(a->q, &v); return NULL; }

int main(void) {
    char cmd[32];
    while (scanf("%31s", cmd) == 1) {
        if (!strcmp(cmd, "pc")) {
            int np, nc, per, cap; if (scanf("%d %d %d %d", &np, &nc, &per, &cap) != 4) return 1;
            BQueue *q = bq_create(cap);
            pthread_t pt[16], ct[16]; Arg pa[16] = {0}, ca[16] = {0};
            for (int i = 0; i < nc; i++) { ca[i].q = q; pthread_create(&ct[i], NULL, consumer, &ca[i]); }
            for (int i = 0; i < np; i++) { pa[i] = (Arg){q, i, per, 1, 0}; pthread_create(&pt[i], NULL, producer, &pa[i]); }
            for (int i = 0; i < np; i++) pthread_join(pt[i], NULL);
            bq_close(q);
            for (int i = 0; i < nc; i++) pthread_join(ct[i], NULL);
            long long ps = 0, cs = 0; long got = 0; int fifo = 1;
            for (int i = 0; i < np; i++) ps += pa[i].sum;
            for (int i = 0; i < nc; i++) { cs += ca[i].sum; got += ca[i].count; fifo &= ca[i].ok; }
            printf("pc %dx%d per=%d cap=%d: delivered=%ld sums_match=%d fifo_per_consumer=%d\n", np, nc, per, cap, got, ps == cs, fifo);
            bq_destroy(q);
        } else if (!strcmp(cmd, "close")) {
            BQueue *q = bq_create(1);
            bq_push(q, 5);                                  /* now full */
            pthread_t a, b; Arg pa = {q, 0, 0, 7, 0}, ca = {0};
            pthread_create(&a, NULL, blocked_push, &pa);     /* blocks: full */
            struct timespec ts = {0, 100000000}; nanosleep(&ts, NULL);
            bq_close(q);
            pthread_join(a, NULL);
            long v; int r1 = bq_pop(q, &v); int r2 = bq_pop(q, &v);
            BQueue *e = bq_create(4);
            ca.q = e; pthread_create(&b, NULL, blocked_pop, &ca);   /* blocks: empty */
            nanosleep(&ts, NULL);
            bq_close(e);
            pthread_join(b, NULL);
            printf("close: blocked_push_returned=%d drain_pop=%d value=%ld then_pop=%d blocked_pop_returned=%d push_after_close=%d\n",
                   pa.ok, r1, v, r2, ca.ok, bq_push(e, 1));
            bq_destroy(q); bq_destroy(e);
        } else if (!strcmp(cmd, "primes")) {
            long lo, hi; int t; if (scanf("%ld %ld %d", &lo, &hi, &t) != 3) return 1;
            double t0 = secs(); long long s1 = parallel_prime_sum(lo, hi, 1); double d1 = secs() - t0;
            t0 = secs(); long long s4 = parallel_prime_sum(lo, hi, t); double d4 = secs() - t0;
            printf("primes [%ld,%ld) threads=%d: sum=%lld agree=%d faster=%d\n", lo, hi, t, s4, s1 == s4, d4 < d1 * 0.9 || d1 < 0.05);
        }
        fflush(stdout);
    }
    return 0;
}
```

## Tests
=== sample
pc 1 1 1000 4
close
primes 0 100 2
---
pc 1x1 per=1000 cap=4: delivered=1000 sums_match=1 fifo_per_consumer=1
close: blocked_push_returned=-1 drain_pop=0 value=5 then_pop=-1 blocked_pop_returned=-1 push_after_close=-1
primes [0,100) threads=2: sum=1060 agree=1 faster=1
=== hidden
pc 4 4 50000 8
pc 8 2 20000 1
pc 2 8 30000 1024
pc 16 16 5000 3
---
pc 4x4 per=50000 cap=8: delivered=200000 sums_match=1 fifo_per_consumer=1
pc 8x2 per=20000 cap=1: delivered=160000 sums_match=1 fifo_per_consumer=1
pc 2x8 per=30000 cap=1024: delivered=60000 sums_match=1 fifo_per_consumer=1
pc 16x16 per=5000 cap=3: delivered=80000 sums_match=1 fifo_per_consumer=1
=== hidden
primes 1 2000000 4
primes 999990 1000000 3
---
primes [1,2000000) threads=4: sum=142913828922 agree=1 faster=1
primes [999990,1000000) threads=3: sum=0 agree=1 faster=1

## Hints
- The struct needs a mutex, two condition variables (`not_full`, `not_empty`) and a `closed` flag.
- `bq_push`: lock; `while (count == cap && !closed) wait(not_full)`; if closed, unlock and return −1; store, `signal(not_empty)`, unlock.
- `bq_pop`: `while (count == 0 && !closed) wait(not_empty)`; if `count == 0` (so it's closed and empty), return −1. Otherwise take the item and `signal(not_full)`.
- `bq_close`: set `closed` under the lock and **broadcast** both condition variables.
- Prime sum: the main thread pushes chunk start values, closes the queue, and joins. Each worker pops chunks, tests primality by trial division, and accumulates into its **own** `long long`, summed after joining (no shared counter).

## Solution
```c
#define _POSIX_C_SOURCE 200809L
#include <pthread.h>
#include <stdlib.h>
#include <stdio.h>

typedef struct BQueue BQueue;
struct BQueue {
    long *buf;
    int cap, head, count, closed;
    pthread_mutex_t m;
    pthread_cond_t not_full, not_empty;
};

BQueue *bq_create(int capacity) {
    BQueue *q = calloc(1, sizeof *q);
    q->buf = malloc(sizeof(long) * (size_t)capacity);
    q->cap = capacity;
    pthread_mutex_init(&q->m, NULL);
    pthread_cond_init(&q->not_full, NULL);
    pthread_cond_init(&q->not_empty, NULL);
    return q;
}

void bq_destroy(BQueue *q) {
    pthread_mutex_destroy(&q->m);
    pthread_cond_destroy(&q->not_full);
    pthread_cond_destroy(&q->not_empty);
    free(q->buf);
    free(q);
}

int bq_push(BQueue *q, long item) {
    pthread_mutex_lock(&q->m);
    while (q->count == q->cap && !q->closed)
        pthread_cond_wait(&q->not_full, &q->m);
    if (q->closed) { pthread_mutex_unlock(&q->m); return -1; }
    q->buf[(q->head + q->count) % q->cap] = item;
    q->count++;
    pthread_cond_signal(&q->not_empty);
    pthread_mutex_unlock(&q->m);
    return 0;
}

int bq_pop(BQueue *q, long *item) {
    pthread_mutex_lock(&q->m);
    while (q->count == 0 && !q->closed)
        pthread_cond_wait(&q->not_empty, &q->m);
    if (q->count == 0) { pthread_mutex_unlock(&q->m); return -1; }   /* closed and drained */
    *item = q->buf[q->head];
    q->head = (q->head + 1) % q->cap;
    q->count--;
    pthread_cond_signal(&q->not_full);
    pthread_mutex_unlock(&q->m);
    return 0;
}

void bq_close(BQueue *q) {
    pthread_mutex_lock(&q->m);
    q->closed = 1;
    pthread_cond_broadcast(&q->not_full);
    pthread_cond_broadcast(&q->not_empty);
    pthread_mutex_unlock(&q->m);
}

typedef struct { BQueue *q; long hi; long long sum; } Worker;

static int is_prime(long n) {
    if (n < 2) return 0;
    if (n % 2 == 0) return n == 2;
    for (long d = 3; d * d <= n; d += 2) if (n % d == 0) return 0;
    return 1;
}

static void *prime_worker(void *p) {
    Worker *w = p;
    long start;
    while (bq_pop(w->q, &start) == 0) {
        long end = start + 1000 < w->hi ? start + 1000 : w->hi;
        for (long n = start; n < end; n++) if (is_prime(n)) w->sum += n;   /* private accumulator */
    }
    return NULL;
}

long long parallel_prime_sum(long lo, long hi, int threads) {
    BQueue *q = bq_create(64);
    pthread_t th[64];
    Worker w[64];
    for (int i = 0; i < threads; i++) {
        w[i] = (Worker){q, hi, 0};
        pthread_create(&th[i], NULL, prime_worker, &w[i]);
    }
    for (long s = lo; s < hi; s += 1000) bq_push(q, s);
    bq_close(q);
    long long total = 0;
    for (int i = 0; i < threads; i++) { pthread_join(th[i], NULL); total += w[i].sum; }
    bq_destroy(q);
    return total;
}
```

- **The bounded queue** is the canonical mutex + two-condition-variable monitor. Producers sleep on `not_full`, consumers on `not_empty`, and each operation signals the other side. The `while` loops re-check the predicate, because wakeups can be spurious or stolen by another thread.
- **Shutdown** is part of the protocol. `closed` turns blocked pushes into failures and lets pops drain the remaining items before failing. A *broadcast* wakes every blocked thread, where a single `signal` would wake only one and leave the others asleep forever.
- **The worker pool** gets its speed-up from dynamic load balancing (fast workers simply take more chunks) and from **private accumulators** combined after `pthread_join`. Join is a synchronisation point, so no lock or atomic is needed for the results.
