---
id: c-spsc-ring
title: A Lock-Free SPSC Ring Buffer for ISR Data
difficulty: Hard
order: 1
tags: ring buffer, lock-free, C11 atomics, memory ordering, ISR, producer-consumer
time_limit: 6
---
## Statement
An encoder ISR produces 32-bit samples, and the control loop consumes them. Implement the single-producer single-consumer ring buffer between them, **lock-free**, with C11 `<stdatomic.h>`. The judge runs the producer and consumer on two real threads (two cores), so memory ordering must be correct.

```c
typedef struct {
    uint32_t *buf;
    uint32_t mask;              /* capacity - 1 */
    _Atomic uint32_t head;      /* next write position (free-running), producer only */
    _Atomic uint32_t tail;      /* next read position (free-running), consumer only  */
    _Atomic uint32_t dropped;   /* pushes rejected because the buffer was full */
} Spsc;
```

| Function | Behaviour |
|---|---|
| `int spsc_init(Spsc *q, uint32_t *storage, uint32_t capacity)` | Capacity must be a power of two ≥ 2, else return -1. Otherwise reset everything and return 0. All `capacity` slots must be usable. |
| `bool spsc_push(Spsc *q, uint32_t v)` | Producer side. If full, increment `dropped` and return false. |
| `bool spsc_pop(Spsc *q, uint32_t *out)` | Consumer side. False if empty. |
| `uint32_t spsc_size(Spsc *q)` | Number of stored items. |
| `uint32_t spsc_pop_bulk(Spsc *q, uint32_t *out, uint32_t max)` | Pop up to `max` items in FIFO order with a **single** tail update. Returns the count. |

Indices are **free-running**: they're never reduced modulo the capacity, and they wrap naturally at 2³². The judge starts some tests with `head = tail = 0xFFFFFF00` (after `spsc_init`) to check this.

## Starter
```c
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>

typedef struct {
    uint32_t *buf;
    uint32_t mask;
    _Atomic uint32_t head;
    _Atomic uint32_t tail;
    _Atomic uint32_t dropped;
} Spsc;

int spsc_init(Spsc *q, uint32_t *storage, uint32_t capacity) {
    q->buf = storage; q->mask = capacity - 1;
    q->head = 0; q->tail = 0; q->dropped = 0;
    return 0;
}

bool spsc_push(Spsc *q, uint32_t v) {
    if (((q->head + 1) & q->mask) == (q->tail & q->mask)) return false;   /* wastes a slot */
    q->buf[q->head & q->mask] = v;
    q->head++;
    return true;
}

bool spsc_pop(Spsc *q, uint32_t *out) {
    if (q->head == q->tail) return false;
    *out = q->buf[q->tail & q->mask];
    q->tail++;
    return true;
}

uint32_t spsc_size(Spsc *q) { return q->head - q->tail; }

uint32_t spsc_pop_bulk(Spsc *q, uint32_t *out, uint32_t max) {
    uint32_t n = 0;
    while (n < max && spsc_pop(q, &out[n])) n++;
    return n;
}
```

## Driver
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <threads.h>

static Spsc Q;
static uint32_t store[1u << 16];
enum { TOTAL = 3000000 };
static atomic_int go;

static int producer(void *arg) {
    (void)arg;
    while (!atomic_load(&go)) {}
    for (uint32_t i = 1; i <= TOTAL; ) {
        if (spsc_push(&Q, i * 2654435761u)) i++;
    }
    return 0;
}

int main(void) {
    char cmd[32];
    while (scanf("%31s", cmd) == 1) {
        if (!strcmp(cmd, "init")) {
            uint32_t caps[] = {0, 1, 2, 3, 4, 6, 8, 1024, 1000, 65536, 0x80000000u};
            for (int i = 0; i < 11; i++) printf("%d ", spsc_init(&Q, store, caps[i]));
            printf("\n");
        } else if (!strcmp(cmd, "basic") || !strcmp(cmd, "wrap")) {
            spsc_init(&Q, store, 4);
            if (!strcmp(cmd, "wrap")) { atomic_store(&Q.head, 0xFFFFFFFEu); atomic_store(&Q.tail, 0xFFFFFFFEu); }
            uint32_t v;
            for (uint32_t i = 10; i < 16; i++) printf("%d", spsc_push(&Q, i));
            printf(" size=%u dropped=%u |", spsc_size(&Q), atomic_load(&Q.dropped));
            for (int i = 0; i < 3; i++) { if (spsc_pop(&Q, &v)) printf(" %u", v); }
            printf(" | size=%u", spsc_size(&Q));
            for (uint32_t i = 20; i < 23; i++) printf(" %d", spsc_push(&Q, i));
            uint32_t out[8]; uint32_t n = spsc_pop_bulk(&Q, out, 8);
            printf(" | bulk %u:", n);
            for (uint32_t i = 0; i < n; i++) printf(" %u", out[i]);
            printf(" | empty pop %d size=%u dropped=%u\n", spsc_pop(&Q, &v), spsc_size(&Q), atomic_load(&Q.dropped));
        } else if (!strcmp(cmd, "model")) {
            /* single-threaded random ops against a reference model, starting near the wrap */
            spsc_init(&Q, store, 64);
            atomic_store(&Q.head, 0xFFFFFF00u); atomic_store(&Q.tail, 0xFFFFFF00u);
            uint32_t model[64], mh = 0, mt = 0, mdrop = 0, x = 12345, ok = 1, next = 1;
            for (int it = 0; it < 2000000 && ok; it++) {
                x ^= x << 13; x ^= x >> 17; x ^= x << 5;
                uint32_t op = x % 10;
                if (op < 6) {
                    bool r = spsc_push(&Q, next);
                    bool mr = (mh - mt) < 64;
                    if (mr) model[mh++ & 63] = next; else mdrop++;
                    next++;
                    ok &= r == mr;
                } else if (op < 9) {
                    uint32_t v = 0; bool r = spsc_pop(&Q, &v);
                    bool mr = mh != mt;
                    ok &= r == mr && (!mr || v == model[mt++ & 63]);
                } else {
                    uint32_t out[16], want = x % 5, n = spsc_pop_bulk(&Q, out, want);
                    uint32_t mn = (mh - mt) < want ? (mh - mt) : want;
                    ok &= n == mn;
                    for (uint32_t i = 0; i < n && ok; i++) ok &= out[i] == model[mt++ & 63];
                }
                ok &= spsc_size(&Q) == mh - mt && atomic_load(&Q.dropped) == mdrop;
            }
            printf("model %s, dropped %u, final size %u\n", ok ? "match" : "MISMATCH", mdrop, mh - mt);
        } else if (!strcmp(cmd, "threads")) {
            unsigned cap; if (scanf("%u", &cap) != 1) return 1;
            spsc_init(&Q, store, cap);
            atomic_store(&Q.head, 0xFFFFF000u); atomic_store(&Q.tail, 0xFFFFF000u);
            atomic_store(&go, 0);
            thrd_t t; thrd_create(&t, producer, NULL);
            atomic_store(&go, 1);
            uint32_t expect = 1, bad = 0, got = 0, chunk[64];
            while (got < TOTAL) {
                uint32_t n = (got & 1) ? spsc_pop_bulk(&Q, chunk, 64) : (spsc_pop(&Q, chunk) ? 1u : 0u);
                for (uint32_t i = 0; i < n; i++, expect++) bad += chunk[i] != expect * 2654435761u;
                got += n;
            }
            thrd_join(t, NULL);
            printf("threads cap=%u received %u in order, errors %u, size %u\n", cap, got, bad, spsc_size(&Q));
        }
    }
    return 0;
}
```

## Tests
=== sample
init
basic
---
-1 -1 0 -1 0 -1 0 0 -1 0 0 
111100 size=4 dropped=2 | 10 11 12 | size=1 1 1 1 | bulk 4: 13 20 21 22 | empty pop 0 size=0 dropped=2
=== hidden
wrap
model
---
111100 size=4 dropped=2 | 10 11 12 | size=1 1 1 1 | bulk 4: 13 20 21 22 | empty pop 0 size=0 dropped=2
model match, dropped 810, final size 5
=== hidden
threads 2
---
threads cap=2 received 3000000 in order, errors 0, size 0
=== hidden
threads 1024
---
threads cap=1024 received 3000000 in order, errors 0, size 0

## Hints
- Count = `head - tail` in `uint32_t`, correct across the wrap. Full means `count == capacity`, so no slot is wasted.
- Power of two: `cap >= 2 && (cap & (cap - 1)) == 0`.
- Producer: load your own `head` relaxed and the other side's `tail` with **acquire**. Write the slot, then store `head + 1` with **release**.
- Consumer, mirrored: load `head` with acquire, read the slot(s), then store `tail` with release.
- `dropped` is only modified by the producer, but it's read by others, so use `atomic_fetch_add_explicit(..., memory_order_relaxed)`.

## Solution
```c
#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>

typedef struct {
    uint32_t *buf;
    uint32_t mask;
    _Atomic uint32_t head;
    _Atomic uint32_t tail;
    _Atomic uint32_t dropped;
} Spsc;

int spsc_init(Spsc *q, uint32_t *storage, uint32_t capacity) {
    if (capacity < 2u || (capacity & (capacity - 1u)) != 0u) return -1;
    q->buf = storage;
    q->mask = capacity - 1u;
    atomic_init(&q->head, 0u);
    atomic_init(&q->tail, 0u);
    atomic_init(&q->dropped, 0u);
    return 0;
}

bool spsc_push(Spsc *q, uint32_t v) {
    const uint32_t h = atomic_load_explicit(&q->head, memory_order_relaxed);   /* we own head */
    const uint32_t t = atomic_load_explicit(&q->tail, memory_order_acquire);   /* slot freed by consumer */
    if (h - t > q->mask) {                                                      /* count == capacity */
        atomic_fetch_add_explicit(&q->dropped, 1u, memory_order_relaxed);
        return false;
    }
    q->buf[h & q->mask] = v;
    atomic_store_explicit(&q->head, h + 1u, memory_order_release);             /* publish after the write */
    return true;
}

bool spsc_pop(Spsc *q, uint32_t *out) {
    const uint32_t t = atomic_load_explicit(&q->tail, memory_order_relaxed);
    const uint32_t h = atomic_load_explicit(&q->head, memory_order_acquire);
    if (h == t) return false;
    *out = q->buf[t & q->mask];
    atomic_store_explicit(&q->tail, t + 1u, memory_order_release);             /* free the slot after reading */
    return true;
}

uint32_t spsc_size(Spsc *q) {
    const uint32_t t = atomic_load_explicit(&q->tail, memory_order_acquire);
    const uint32_t h = atomic_load_explicit(&q->head, memory_order_acquire);
    return h - t;
}

uint32_t spsc_pop_bulk(Spsc *q, uint32_t *out, uint32_t max) {
    const uint32_t t = atomic_load_explicit(&q->tail, memory_order_relaxed);
    const uint32_t h = atomic_load_explicit(&q->head, memory_order_acquire);
    uint32_t n = h - t;
    if (n > max) n = max;
    for (uint32_t i = 0; i < n; i++) out[i] = q->buf[(t + i) & q->mask];
    atomic_store_explicit(&q->tail, t + n, memory_order_release);              /* one update frees n slots */
    return n;
}
```

- **One writer per index**: only the producer stores `head`, and only the consumer stores `tail`. There's no read-modify-write race, so no lock or CAS is needed. That's why it's safe between an ISR and the main loop, or between two cores.
- **Release/acquire pairs**: the producer writes the slot, then release-stores `head`. A consumer that acquire-loads that `head` is guaranteed to see the slot's contents. The reverse pair (release `tail`, acquire in the producer) stops the producer from overwriting a slot the consumer is still reading.
- **Free-running indices**: `h - t` is the exact count even after either index wraps past 2³², so all `capacity` slots are usable. The starter's "one empty slot" check compares masked indices and loses a slot. With capacity 2 it holds only one item.
- **Bulk pop** reads `head` once and publishes `tail` once, so the producer sees a burst of free space with one cache-line transfer instead of n.
- **Production extras**: pad `head` and `tail` onto separate cache lines (`alignas(64)`) to avoid false sharing, and cache the other side's index locally to cut cross-core traffic further.
