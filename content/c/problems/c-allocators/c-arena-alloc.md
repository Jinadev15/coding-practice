---
id: c-arena-alloc
title: Aligned Arena Allocator
difficulty: Medium
order: 1
tags: arena, bump allocator, alignment, uintptr_t
---
## Statement
Implement an arena (bump) allocator on top of a buffer **supplied by the caller**:

```c
typedef struct {
    unsigned char *base;
    size_t cap;
    size_t used;
} Arena;

void   arena_init(Arena *a, void *buffer, size_t cap);
void  *arena_alloc(Arena *a, size_t size, size_t align);  /* align: a power of two >= 1.
                                                             NULL (and no change) if it doesn't fit */
size_t arena_mark(const Arena *a);                        /* current offset */
void   arena_release(Arena *a, size_t mark);              /* roll back to a previous mark */
void   arena_reset(Arena *a);                             /* free everything */
```

`arena_alloc` places the object at the **lowest offset ≥ `used`** whose address is a multiple of `align`, and sets `used` to just past the object. A request with `size == 0` succeeds and returns the aligned position without consuming space. The size check must not overflow, even for `size` close to `SIZE_MAX`.

The driver gives you a 64-byte-aligned buffer and processes commands: `alloc SIZE ALIGN` (prints the offset or `fail`), `mark`, `release M`, `reset`, and `fill`, which allocates `int`s until the arena is full and prints how many fit. It also writes through every returned pointer to check that the memory is usable.

## Starter
```c
#include <stddef.h>
#include <stdint.h>

typedef struct {
    unsigned char *base;
    size_t cap;
    size_t used;
} Arena;

void arena_init(Arena *a, void *buffer, size_t cap) {
    a->base = buffer;
    a->cap = cap;
    a->used = 0;
}

void *arena_alloc(Arena *a, size_t size, size_t align) {
    void *p = a->base + a->used;
    a->used += size;
    return p;
}

size_t arena_mark(const Arena *a) { return a->used; }
void arena_release(Arena *a, size_t mark) { }
void arena_reset(Arena *a) { }
```

## Driver
```c
#include <stdio.h>
#include <string.h>

static _Alignas(64) unsigned char memory[1024];

int main(void) {
    size_t cap;
    if (scanf("%zu", &cap) != 1 || cap > sizeof memory) return 1;
    Arena a;
    arena_init(&a, memory, cap);
    char cmd[16];
    while (scanf("%15s", cmd) == 1) {
        if (strcmp(cmd, "alloc") == 0) {
            size_t size, align;
            if (scanf("%zu %zu", &size, &align) != 2) return 1;
            unsigned char *p = arena_alloc(&a, size, align);
            if (!p) { printf("fail (used %zu)\n", arena_mark(&a)); continue; }
            if ((uintptr_t)p % align != 0) { printf("MISALIGNED\n"); return 0; }
            memset(p, 0xAB, size);
            printf("at %zu (used %zu)\n", (size_t)(p - memory), arena_mark(&a));
        } else if (strcmp(cmd, "mark") == 0) {
            printf("mark %zu\n", arena_mark(&a));
        } else if (strcmp(cmd, "release") == 0) {
            size_t m;
            if (scanf("%zu", &m) != 1) return 1;
            arena_release(&a, m);
            printf("released to %zu\n", arena_mark(&a));
        } else if (strcmp(cmd, "reset") == 0) {
            arena_reset(&a);
            printf("reset\n");
        } else if (strcmp(cmd, "fill") == 0) {
            int count = 0;
            int *ip;
            while ((ip = arena_alloc(&a, sizeof(int), _Alignof(int))) != NULL) { *ip = count++; }
            printf("filled %d ints (used %zu)\n", count, arena_mark(&a));
        } else if (strcmp(cmd, "huge") == 0) {
            void *p = arena_alloc(&a, SIZE_MAX - 3, 8);
            printf("huge %s (used %zu)\n", p ? "allocated?!" : "rejected", arena_mark(&a));
        }
    }
    return 0;
}
```

## Tests
=== sample
64
alloc 1 1
alloc 8 8
alloc 3 4
alloc 16 16
alloc 32 1
alloc 0 64
mark
---
at 0 (used 1)
at 8 (used 16)
at 16 (used 19)
at 32 (used 48)
fail (used 48)
at 64 (used 64)
mark 64
=== hidden
128
alloc 5 1
mark
alloc 10 32
alloc 1 1
release 5
alloc 1 2
reset
alloc 128 64
alloc 0 1
alloc 1 1
huge
---
at 0 (used 5)
mark 5
at 32 (used 42)
at 42 (used 43)
released to 5
at 6 (used 7)
reset
at 0 (used 128)
at 128 (used 128)
fail (used 128)
huge rejected (used 128)
=== hidden
100
alloc 3 1
fill
reset
fill
huge
alloc 0 4
---
at 0 (used 3)
filled 24 ints (used 100)
reset
filled 25 ints (used 100)
huge rejected (used 100)
at 100 (used 100)
=== hidden
1024
alloc 1 1
alloc 1 2
alloc 1 4
alloc 1 8
alloc 1 16
alloc 1 32
alloc 1 64
alloc 1000 1
alloc 900 1
huge
---
at 0 (used 1)
at 2 (used 3)
at 4 (used 5)
at 8 (used 9)
at 16 (used 17)
at 32 (used 33)
at 64 (used 65)
fail (used 65)
at 65 (used 965)
huge rejected (used 965)

## Hints
- Do the alignment on **addresses**, not offsets, so the code stays correct even if the buffer isn't aligned: `uintptr_t cur = (uintptr_t)(a->base + a->used); uintptr_t al = (cur + align - 1) & ~(uintptr_t)(align - 1);`
- Overflow-safe fit check: with `start` as the aligned offset, test `start > cap || size > cap - start`. Never write `start + size > cap`, because that sum can wrap around.
- `release(mark)` just sets `used = mark`. Everything allocated after the mark is gone in O(1).

## Solution
```c
#include <stddef.h>
#include <stdint.h>

typedef struct {
    unsigned char *base;
    size_t cap;
    size_t used;
} Arena;

void arena_init(Arena *a, void *buffer, size_t cap) {
    a->base = buffer;
    a->cap = cap;
    a->used = 0;
}

void *arena_alloc(Arena *a, size_t size, size_t align) {
    uintptr_t base = (uintptr_t)a->base;
    uintptr_t cur = base + a->used;
    uintptr_t aligned = (cur + (align - 1)) & ~(uintptr_t)(align - 1);
    size_t start = (size_t)(aligned - base);
    if (start > a->cap || size > a->cap - start) return NULL;   /* no overflow possible */
    a->used = start + size;
    return a->base + start;
}

size_t arena_mark(const Arena *a) { return a->used; }
void arena_release(Arena *a, size_t mark) { if (mark <= a->used) a->used = mark; }
void arena_reset(Arena *a) { a->used = 0; }
```

Each allocation is a handful of integer operations, with no headers, no searching and no system calls. The `(x + a - 1) & ~(a - 1)` rounding works because alignments are powers of two. Notice the subtle points the tests check:
- **Padding is consumed:** after a 1-byte object, an 8-aligned request starts at offset 8, not 1.
- **The bounds check can't overflow:** `size > cap - start` is safe because `start <= cap` was checked first. The naive `start + size > cap` wraps around for `size = SIZE_MAX - 3` and "succeeds", handing out a pointer to memory you don't own.
- **A failed request changes nothing**, so the arena stays usable for smaller requests.
- **Marks** give scoped temporary memory: take a mark, do scratch work, release back to it.
