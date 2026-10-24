---
id: c-pool-alloc
title: Fixed-Size Pool with a Free List
difficulty: Hard
order: 2
tags: pool allocator, free list, O(1), unions
time_limit: 1
---
## Statement
Implement a pool allocator for fixed-size blocks, **without any `malloc` after `pool_init`**:

```c
typedef struct Pool Pool;     /* you define the struct */

Pool *pool_create(size_t block_size, size_t count);  /* the ONLY place that calls malloc */
void *pool_alloc(Pool *p);                           /* O(1); NULL when exhausted */
void  pool_free(Pool *p, void *block);               /* O(1) */
size_t pool_index(const Pool *p, const void *block); /* slot number of a block: 0..count-1 */
size_t pool_available(const Pool *p);                /* free blocks left, O(1) */
void  pool_destroy(Pool *p);
```

Exact reuse order is part of the specification, so the output is deterministic:
- Initially the free list hands out slots in order 0, 1, 2, ….
- `pool_free` pushes the block onto the **front** of the free list, so the most recently freed block is the next one returned (LIFO).

Blocks must be aligned for any type (`_Alignof(max_align_t)`), and each block must hold at least a pointer, so round `block_size` up to a multiple of the alignment.

The driver runs a script (`a` = alloc and print the slot, `f K` = free the K-th currently held block) and then a stress test of up to 2·10⁶ operations. An O(n) search for a free slot will time out.

## Starter
```c
#include <stddef.h>
#include <stdlib.h>

struct Pool {
    unsigned char *mem;
    size_t block, count;
    unsigned char *used;   /* one flag per slot */
};
typedef struct Pool Pool;

Pool *pool_create(size_t block_size, size_t count) {
    Pool *p = malloc(sizeof *p);
    p->block = block_size;
    p->count = count;
    p->mem = malloc(block_size * count);
    p->used = calloc(count, 1);
    return p;
}

void *pool_alloc(Pool *p) {
    for (size_t i = 0; i < p->count; i++)      /* O(n) scan: too slow, and the wrong order */
        if (!p->used[i]) { p->used[i] = 1; return p->mem + i * p->block; }
    return NULL;
}

void pool_free(Pool *p, void *block) {
    p->used[((unsigned char *)block - p->mem) / p->block] = 0;
}

size_t pool_index(const Pool *p, const void *block) {
    return (size_t)((const unsigned char *)block - p->mem) / p->block;
}

size_t pool_available(const Pool *p) {
    size_t n = 0;
    for (size_t i = 0; i < p->count; i++) n += !p->used[i];
    return n;
}

void pool_destroy(Pool *p) { free(p->mem); free(p->used); free(p); }
```

## Driver
```c
#include <stdio.h>
#include <stdint.h>
#include <string.h>

int main(void) {
    size_t bsize, count;
    int script;
    if (scanf("%zu %zu %d", &bsize, &count, &script) != 3) return 1;
    Pool *p = pool_create(bsize, count);
    void **held = malloc(count * sizeof *held);
    size_t nheld = 0;
    for (int s = 0; s < script; s++) {
        char op;
        if (scanf(" %c", &op) != 1) return 1;
        if (op == 'a') {
            void *b = pool_alloc(p);
            if (!b) { printf("empty\n"); continue; }
            if ((uintptr_t)b % _Alignof(max_align_t)) { printf("MISALIGNED\n"); return 0; }
            memset(b, 0x5A, bsize);
            held[nheld++] = b;
            printf("slot %zu (avail %zu)\n", pool_index(p, b), pool_available(p));
        } else {
            size_t k;
            if (scanf("%zu", &k) != 1) return 1;
            pool_free(p, held[k]);
            held[k] = held[--nheld];       /* swap-remove */
            printf("freed (avail %zu)\n", pool_available(p));
        }
    }
    /* stress: R rounds of allocating everything then freeing in a scrambled order */
    long long rounds;
    if (scanf("%lld", &rounds) == 1 && rounds > 0) {
        for (size_t i = 0; i < nheld; i++) pool_free(p, held[i]);
        nheld = 0;
        unsigned long long checksum = 0, x = 88172645463325252ULL;
        for (long long r = 0; r < rounds; r++) {
            void *b;
            while ((b = pool_alloc(p)) != NULL) held[nheld++] = b;
            for (size_t i = nheld; i > 1; i--) {             /* Fisher-Yates with xorshift */
                x ^= x << 13; x ^= x >> 7; x ^= x << 17;
                size_t j = (size_t)(x % i);
                void *t = held[i - 1]; held[i - 1] = held[j]; held[j] = t;
            }
            while (nheld > count / 2) pool_free(p, held[--nheld]);
            b = pool_alloc(p);
            checksum = checksum * 1000003ULL + pool_index(p, b);
            pool_free(p, b);
            while (nheld > 0) pool_free(p, held[--nheld]);
        }
        printf("stress checksum %llu avail %zu\n", checksum, pool_available(p));
    }
    free(held);
    pool_destroy(p);
    return 0;
}
```

## Tests
=== sample
24 4 9
a
a
a
f 0
a
a
a
f 1
a
0
---
slot 0 (avail 3)
slot 1 (avail 2)
slot 2 (avail 1)
freed (avail 2)
slot 0 (avail 1)
slot 3 (avail 0)
empty
freed (avail 1)
slot 1 (avail 0)
=== hidden
1 3 8
a
a
a
a
f 2
f 0
a
a
0
---
slot 0 (avail 2)
slot 1 (avail 1)
slot 2 (avail 0)
empty
freed (avail 1)
freed (avail 2)
slot 0 (avail 1)
slot 2 (avail 0)
=== hidden
40 5 12
a
a
a
a
a
f 4
f 3
f 2
a
a
a
a
0
---
slot 0 (avail 4)
slot 1 (avail 3)
slot 2 (avail 2)
slot 3 (avail 1)
slot 4 (avail 0)
freed (avail 1)
freed (avail 2)
freed (avail 3)
slot 2 (avail 2)
slot 3 (avail 1)
slot 4 (avail 0)
empty
=== hidden
16 200000 0
10
---
stress checksum 14568330376749832778 avail 200000
=== hidden
8 1000 3
a
a
f 0
900
---
slot 0 (avail 999)
slot 1 (avail 998)
freed (avail 999)
stress checksum 12050430839079574964 avail 1000

## Hints
- Store the free-list link **inside** each free block: `*(void **)block = head; head = block;`. That needs no extra memory.
- Round the block size up: `size_t a = _Alignof(max_align_t); size_t bs = (block_size < sizeof(void *) ? sizeof(void *) : block_size); bs = (bs + a - 1) / a * a;`
- Allocate the block memory with `aligned_alloc(a, bs * count)` (C11), or with `malloc`, which is already aligned to `max_align_t`.
- Keep a counter for `pool_available` instead of counting.

## Solution
```c
#include <stddef.h>
#include <stdlib.h>

struct Pool {
    unsigned char *mem;
    void *free_head;
    size_t block, count, avail;
};
typedef struct Pool Pool;

Pool *pool_create(size_t block_size, size_t count) {
    size_t a = _Alignof(max_align_t);
    size_t bs = block_size < sizeof(void *) ? sizeof(void *) : block_size;
    bs = (bs + a - 1) / a * a;
    Pool *p = malloc(sizeof *p);
    if (!p) return NULL;
    p->mem = malloc(bs * count);            /* malloc's result is max_align_t-aligned */
    if (!p->mem) { free(p); return NULL; }
    p->block = bs;
    p->count = p->avail = count;
    p->free_head = NULL;
    for (size_t i = count; i-- > 0;) {      /* push in reverse so slot 0 is handed out first */
        void *b = p->mem + i * bs;
        *(void **)b = p->free_head;
        p->free_head = b;
    }
    return p;
}

void *pool_alloc(Pool *p) {
    void *b = p->free_head;
    if (!b) return NULL;
    p->free_head = *(void **)b;             /* pop */
    p->avail--;
    return b;
}

void pool_free(Pool *p, void *block) {
    *(void **)block = p->free_head;         /* push: LIFO */
    p->free_head = block;
    p->avail++;
}

size_t pool_index(const Pool *p, const void *block) {
    return (size_t)((const unsigned char *)block - p->mem) / p->block;
}

size_t pool_available(const Pool *p) { return p->avail; }

void pool_destroy(Pool *p) {
    if (!p) return;
    free(p->mem);
    free(p);
}
```

The free list is **intrusive**: the link lives in the first bytes of each free block, so the pool needs no bookkeeping array. That's why every block must be at least `sizeof(void *)` bytes. `alloc` and `free` are a pointer pop and push, O(1) with no loops, which is what real-time code needs. Building the initial list back to front makes slot 0 the head. Rounding the block size to `_Alignof(max_align_t)` keeps *every* block aligned, not just the first. For production use you'd add debug checks (poisoning freed blocks, detecting a double free by scanning the list, or checking that the pointer is inside `mem` and on a block boundary), which the Linux kernel's slab allocator does in debug mode.
