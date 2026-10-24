---
id: c-sort-records
title: Stable Multi-Key Merge Sort and LSD Radix Sort
difficulty: Hard
order: 1
tags: merge sort, stability, radix sort, counting sort, performance
time_limit: 3
---
## Statement
Implement two production-grade sorts.

```c
typedef struct { char name[12]; int team; int score; unsigned id; } Rec;   /* keep this typedef */

void stable_sort_records(Rec *r, size_t n);   /* team ascending, then score DESCENDING; equal keys keep input order */
void radix_sort_u32(uint32_t *a, size_t n);   /* ascending */
```

Requirements:
- `stable_sort_records` must be **stable**. Records with the same team and score keep their original relative order. Use a merge sort with an O(n) temporary buffer. (`qsort` isn't stable, so it isn't acceptable here.)
- `radix_sort_u32` must be an **LSD radix sort**: 4 stable counting-sort passes on 8-bit digits, O(n) per pass. The hidden tests sort several million integers with a 3-second limit for the whole run, so an O(n²) sort times out.
- Both must handle `n = 0` and `n = 1`. You may `malloc` scratch space and must `free` it.

The driver generates the data itself (from a seed), runs your functions, and compares the result with a reference sort. It prints `ok` plus the first few records, or the first index where your output differs.

## Starter
```c
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct { char name[12]; int team; int score; unsigned id; } Rec;

void stable_sort_records(Rec *r, size_t n) {
    (void)r; (void)n;
}

void radix_sort_u32(uint32_t *a, size_t n) {
    (void)a; (void)n;
}
```

## Driver
```c
#include <stdio.h>

static uint64_t drv_st;
static uint32_t drv_rnd(void) {
    drv_st = drv_st * 6364136223846793005ULL + 1442695040888963407ULL;
    return (uint32_t)(drv_st >> 33);
}
static int drv_cmp_rec(const void *pa, const void *pb) {
    const Rec *a = pa, *b = pb;
    if (a->team != b->team) return (a->team > b->team) - (a->team < b->team);
    if (a->score != b->score) return (a->score < b->score) - (a->score > b->score);
    return (a->id > b->id) - (a->id < b->id);          /* original index: makes the reference stable */
}
static int drv_cmp_u32(const void *pa, const void *pb) {
    uint32_t a = *(const uint32_t *)pa, b = *(const uint32_t *)pb;
    return (a > b) - (a < b);
}

int main(void) {
    char cmd[32];
    while (scanf("%31s", cmd) == 1) {
        size_t n; unsigned long long seed;
        if (!strcmp(cmd, "records")) {
            unsigned teams, scores;
            if (scanf("%zu %llu %u %u", &n, &seed, &teams, &scores) != 4) return 1;
            drv_st = seed;
            Rec *a = calloc(n ? n : 1, sizeof *a), *b = calloc(n ? n : 1, sizeof *b);
            for (size_t i = 0; i < n; i++) {
                a[i].team = (int)(drv_rnd() % teams) - (int)(teams / 2);
                a[i].score = (int)(drv_rnd() % scores);
                a[i].id = (unsigned)i;
                snprintf(a[i].name, sizeof a[i].name, "r%zu", i);
            }
            memcpy(b, a, n * sizeof *a);
            stable_sort_records(a, n);
            qsort(b, n, sizeof *b, drv_cmp_rec);
            size_t bad = n;
            for (size_t i = 0; i < n; i++)
                if (memcmp(&a[i], &b[i], sizeof *a)) { bad = i; break; }
            if (bad == n) {
                printf("records %zu: ok", n);
                for (size_t i = 0; i < n && i < 4; i++)
                    printf(" [%s t=%d s=%d]", a[i].name, a[i].team, a[i].score);
                printf("\n");
            } else {
                printf("records %zu: WRONG at index %zu (got %s t=%d s=%d, want %s t=%d s=%d)\n", n, bad,
                       a[bad].name, a[bad].team, a[bad].score, b[bad].name, b[bad].team, b[bad].score);
            }
            free(a); free(b);
        } else if (!strcmp(cmd, "radix")) {
            unsigned mask;
            if (scanf("%zu %llu %x", &n, &seed, &mask) != 3) return 1;
            drv_st = seed;
            uint32_t *a = malloc((n ? n : 1) * sizeof *a), *b = malloc((n ? n : 1) * sizeof *b);
            for (size_t i = 0; i < n; i++) a[i] = ((drv_rnd() << 16) ^ drv_rnd()) & mask;
            memcpy(b, a, n * sizeof *a);
            radix_sort_u32(a, n);
            qsort(b, n, sizeof *b, drv_cmp_u32);
            size_t bad = n;
            for (size_t i = 0; i < n; i++)
                if (a[i] != b[i]) { bad = i; break; }
            if (bad == n) {
                if (n) printf("radix %zu: ok min=%u median=%u max=%u\n", n, a[0], a[n / 2], a[n - 1]);
                else printf("radix 0: ok\n");
            } else {
                printf("radix %zu: WRONG at index %zu (got %u, want %u)\n", n, bad, a[bad], b[bad]);
            }
            free(a); free(b);
        }
    }
    return 0;
}
```

## Tests
=== sample
records 10 1 3 5
radix 10 7 ffffffff
records 0 1 1 1
radix 1 3 ff
---
records 10: ok [r5 t=-1 s=2] [r4 t=-1 s=1] [r1 t=-1 s=0] [r2 t=-1 s=0]
radix 10: ok min=183736479 median=2413321105 max=3993832767
records 0: ok
radix 1: ok min=251 median=251 max=251
=== hidden
records 1 2 1 1
records 17 3 2 2
records 1000 5 2 3
records 5000 6 1 1
radix 1000 9 ff
radix 100000 11 ffffffff
---
records 1: ok [r0 t=0 s=0]
records 17: ok [r2 t=-1 s=1] [r6 t=-1 s=1] [r7 t=-1 s=1] [r0 t=0 s=1]
records 1000: ok [r0 t=-1 s=2] [r6 t=-1 s=2] [r19 t=-1 s=2] [r21 t=-1 s=2]
records 5000: ok [r0 t=0 s=0] [r1 t=0 s=0] [r2 t=0 s=0] [r3 t=0 s=0]
radix 1000: ok min=0 median=119 max=255
radix 100000: ok min=14729 median=2150979939 max=4294942847
=== hidden
records 400000 13 50 100
radix 4000000 17 ffffffff
radix 3000000 19 ffff0000
---
records 400000: ok [r7146 t=-25 s=99] [r11921 t=-25 s=99] [r12217 t=-25 s=99] [r15103 t=-25 s=99]
radix 4000000: ok min=919 median=2145648881 max=4294967079
radix 3000000: ok min=0 median=2147483648 max=4294901760

## Hints
- Merge step: take from the **right** run only when its element is strictly *before* the left one (`before(right, left)`). On ties, the left element goes first, and that's what makes the sort stable.
- Write `before(a, b)` returning `a->team < b->team || (a->team == b->team && a->score > b->score)`.
- Speed-ups: switch to insertion sort for runs of ≤ 16, and skip the merge when `!before(&a[mid], &a[mid-1])` (the halves are already in order).
- Radix: `cnt[d + 1]++`, then prefix sums give each digit's first output slot, then scatter `dst[cnt[d]++] = src[i]`. Swap `src`/`dst` after each pass. After 4 passes (an even number), the data is back in the original array.

## Solution
```c
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct { char name[12]; int team; int score; unsigned id; } Rec;

static int before(const Rec *a, const Rec *b) {          /* strict: a must come before b */
    if (a->team != b->team) return a->team < b->team;
    return a->score > b->score;
}

static void msort(Rec *a, Rec *tmp, size_t n) {
    if (n <= 16) {                                       /* insertion sort: stable, fast on tiny runs */
        for (size_t i = 1; i < n; i++) {
            Rec key = a[i];
            size_t j = i;
            while (j > 0 && before(&key, &a[j - 1])) { a[j] = a[j - 1]; j--; }
            a[j] = key;
        }
        return;
    }
    size_t mid = n / 2;
    msort(a, tmp, mid);
    msort(a + mid, tmp, n - mid);
    if (!before(&a[mid], &a[mid - 1])) return;           /* already ordered */
    size_t i = 0, j = mid, k = 0;
    while (i < mid && j < n)
        tmp[k++] = before(&a[j], &a[i]) ? a[j++] : a[i++];   /* ties take the left: stable */
    while (i < mid) tmp[k++] = a[i++];
    while (j < n) tmp[k++] = a[j++];
    memcpy(a, tmp, n * sizeof *a);
}

void stable_sort_records(Rec *r, size_t n) {
    if (n < 2) return;
    Rec *tmp = malloc(n * sizeof *tmp);
    if (!tmp) return;
    msort(r, tmp, n);
    free(tmp);
}

void radix_sort_u32(uint32_t *a, size_t n) {
    if (n < 2) return;
    uint32_t *tmp = malloc(n * sizeof *tmp);
    if (!tmp) return;
    uint32_t *src = a, *dst = tmp;
    for (unsigned shift = 0; shift < 32; shift += 8) {
        size_t cnt[257] = {0};
        for (size_t i = 0; i < n; i++) cnt[((src[i] >> shift) & 0xFFu) + 1]++;
        for (int d = 0; d < 256; d++) cnt[d + 1] += cnt[d];        /* cnt[d] = first slot of digit d */
        for (size_t i = 0; i < n; i++) dst[cnt[(src[i] >> shift) & 0xFFu]++] = src[i];
        uint32_t *t = src; src = dst; dst = t;
    }
    free(tmp);                                           /* 4 passes: the result is back in a */
}
```

**Merge sort** is O(n log n) in every case and stable because the merge prefers the left run on ties. The two optimisations (an insertion-sort base case and the "already ordered" check) are what library implementations such as Timsort and glibc's merge sort also do.

**LSD radix sort** makes 4 passes of a stable counting sort, from the least significant byte to the most. After pass k, the array is sorted by its low 8(k+1) bits, because each later pass is stable and preserves the order of equal digits. Its cost is 4·(2n + 256) operations, linear and branch-free. On millions of 32-bit keys it typically beats `qsort` by 3–10×, since there are no comparator calls through a function pointer and memory access is sequential except for the scatter.
