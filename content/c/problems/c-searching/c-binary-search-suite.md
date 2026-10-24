---
id: c-binary-search-suite
title: Binary Search Suite with Search-on-the-Answer
difficulty: Hard
order: 1
tags: binary search, lower_bound, rotated array, binary search on answer, invariants
time_limit: 3
---
## Statement
Implement four binary-search functions. Every one must run in O(log n), except `max_min_gap`, which is O(n log range). The hidden tests make millions of queries on arrays of millions of elements, so linear scans time out.

```c
size_t lower_bound_i(const int *a, size_t n, int key);   /* first i with a[i] >= key, or n */
size_t upper_bound_i(const int *a, size_t n, int key);   /* first i with a[i] >  key, or n */

/* a: strictly increasing values, rotated left by an unknown amount (e.g. 40 50 10 20 30).
   Return the index of key, or n if absent. */
size_t search_rotated(const int *a, size_t n, int key);

/* pos: sorted ascending (duplicates allowed), 2 <= k <= n. Choose k of the positions for sensors
   so the smallest distance between any two chosen sensors is as LARGE as possible; return that distance. */
long long max_min_gap(const int *pos, size_t n, int k);
```

Values can be anywhere in the `int` range, so differences such as `pos[n-1] - pos[0]` overflow `int`. Use `long long`.

The driver runs these commands:
- `small n key v1 … vn` prints the bounds.
- `bounds`, `rotated` and `gap` generate large random inputs from a seed and check every answer against a reference.

## Starter
```c
#include <stddef.h>

size_t lower_bound_i(const int *a, size_t n, int key) { (void)a; (void)key; return n; }
size_t upper_bound_i(const int *a, size_t n, int key) { (void)a; (void)key; return n; }
size_t search_rotated(const int *a, size_t n, int key) {
    for (size_t i = 0; i < n; i++) if (a[i] == key) return i;
    return n;
}
long long max_min_gap(const int *pos, size_t n, int k) { (void)pos; (void)n; (void)k; return 0; }
```

## Driver
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned long long drv_st;
static unsigned drv_rnd(void) {
    drv_st = drv_st * 6364136223846793005ULL + 1442695040888963407ULL;
    return (unsigned)(drv_st >> 33);
}
static int drv_cmp(const void *pa, const void *pb) {
    int a = *(const int *)pa, b = *(const int *)pb;
    return (a > b) - (a < b);
}
static size_t drv_lb(const int *a, size_t n, int key) {
    size_t lo = 0, hi = n;
    while (lo < hi) { size_t m = lo + (hi - lo) / 2; if (a[m] < key) lo = m + 1; else hi = m; }
    return lo;
}
static int drv_ok(const int *pos, size_t n, int k, long long d) {
    int c = 1; long long last = pos[0];
    for (size_t i = 1; i < n && c < k; i++) if ((long long)pos[i] - last >= d) { c++; last = pos[i]; }
    return c >= k;
}
static long long drv_gap(const int *pos, size_t n, int k) {
    long long lo = 0, hi = (long long)pos[n - 1] - pos[0];
    while (lo < hi) { long long m = lo + (hi - lo + 1) / 2; if (drv_ok(pos, n, k, m)) lo = m; else hi = m - 1; }
    return lo;
}

int main(void) {
    char cmd[32];
    while (scanf("%31s", cmd) == 1) {
        if (!strcmp(cmd, "small")) {
            size_t n; int key;
            if (scanf("%zu %d", &n, &key) != 2) return 1;
            int *a = malloc((n ? n : 1) * sizeof *a);
            for (size_t i = 0; i < n; i++) if (scanf("%d", &a[i]) != 1) return 1;
            size_t lb = lower_bound_i(a, n, key), ub = upper_bound_i(a, n, key);
            printf("small key=%d: lower=%zu upper=%zu count=%zu\n", key, lb, ub, ub >= lb ? ub - lb : 0);
            free(a);
        } else if (!strcmp(cmd, "bounds")) {
            size_t n, q; unsigned long long seed; unsigned range;
            if (scanf("%zu %llu %u %zu", &n, &seed, &range, &q) != 4) return 1;
            drv_st = seed;
            int *a = malloc((n ? n : 1) * sizeof *a);
            for (size_t i = 0; i < n; i++) a[i] = (int)(drv_rnd() % range) - (int)(range / 2);
            qsort(a, n, sizeof *a, drv_cmp);
            unsigned long long sum = 0; size_t bad = 0;
            for (size_t i = 0; i < q; i++) {
                int key = (int)(drv_rnd() % (range + 4)) - (int)(range / 2) - 2;
                size_t lb = lower_bound_i(a, n, key), ub = upper_bound_i(a, n, key);
                size_t rl = drv_lb(a, n, key), ru = key == 2147483647 ? n : drv_lb(a, n, key + 1);
                if (lb != rl || ub != ru) { if (!bad) printf("bounds: WRONG for key %d (got %zu,%zu want %zu,%zu)\n", key, lb, ub, rl, ru); bad++; }
                sum += rl * 31 + ru;
            }
            if (!bad) printf("bounds n=%zu q=%zu: ok checksum=%llu\n", n, q, sum);
            free(a);
        } else if (!strcmp(cmd, "rotated")) {
            size_t n, q; unsigned long long seed;
            if (scanf("%zu %llu %zu", &n, &seed, &q) != 3) return 1;
            drv_st = seed;
            int *s = malloc((n ? n : 1) * sizeof *s), *a = malloc((n ? n : 1) * sizeof *a);
            for (size_t i = 0; i < n; i++) s[i] = (int)(3 * i) + (int)(drv_rnd() % 3) - 1000000;
            size_t r = n ? drv_rnd() % n : 0;
            for (size_t i = 0; i < n; i++) a[i] = s[(i + r) % n];
            size_t found = 0, bad = 0;
            for (size_t i = 0; i < q; i++) {
                int key = (int)(drv_rnd() % (3 * n + 6)) - 3 - 1000000;
                size_t got = search_rotated(a, n, key);
                size_t j = drv_lb(s, n, key);
                int present = j < n && s[j] == key;
                if (present) found++;
                if (present ? (got >= n || a[got] != key) : got != n) {
                    if (!bad) printf("rotated: WRONG for key %d (got %zu)\n", key, got);
                    bad++;
                }
            }
            if (!bad) printf("rotated n=%zu q=%zu: ok found=%zu\n", n, q, found);
            free(s); free(a);
        } else if (!strcmp(cmd, "gap")) {
            size_t n; int k; unsigned long long seed; unsigned spread;
            if (scanf("%zu %d %llu %u", &n, &k, &seed, &spread) != 4) return 1;
            drv_st = seed;
            int *p = malloc(n * sizeof *p);
            for (size_t i = 0; i < n; i++) p[i] = (int)(drv_rnd() % spread) - (int)(spread / 2);
            if (spread > 2000000000u) { p[0] = -2147483647 - 1; p[n - 1] = 2147483647; }
            qsort(p, n, sizeof *p, drv_cmp);
            long long got = max_min_gap(p, n, k), want = drv_gap(p, n, k);
            if (got == want) printf("gap n=%zu k=%d: %lld\n", n, k, got);
            else printf("gap n=%zu k=%d: WRONG got %lld want %lld\n", n, k, got, want);
            free(p);
        } else if (!strcmp(cmd, "gapsmall")) {
            size_t n; int k;
            if (scanf("%zu %d", &n, &k) != 2) return 1;
            int *p = malloc(n * sizeof *p);
            for (size_t i = 0; i < n; i++) if (scanf("%d", &p[i]) != 1) return 1;
            printf("gapsmall k=%d: %lld\n", k, max_min_gap(p, n, k));
            free(p);
        }
    }
    return 0;
}
```

## Tests
=== sample
small 5 3 1 3 3 3 7
small 5 0 1 3 3 3 7
small 5 9 1 3 3 3 7
small 0 4
gapsmall 5 3 1 2 4 8 9
rotated 7 1 50
bounds 50 2 10 100
---
small key=3: lower=1 upper=4 count=3
small key=0: lower=0 upper=0 count=0
small key=9: lower=5 upper=5 count=0
small key=4: lower=0 upper=0 count=0
gapsmall k=3: 3
rotated n=7 q=50: ok found=7
bounds n=50 q=100: ok checksum=62955
=== hidden
small 1 5 5
small 3 -2147483648 -2147483648 0 2147483647
small 3 2147483647 -2147483648 0 2147483647
small 6 2 2 2 2 2 2 2
gapsmall 2 2 -2147483648 2147483647
gapsmall 4 4 0 0 0 0
gapsmall 6 2 1 1 1 1 1 9
rotated 1 3 10
rotated 2 4 20
rotated 1000 5 5000
gap 1000 2 6 100000
gap 1000 1000 7 1000000000
gap 5000 37 8 4000000000
---
small key=5: lower=0 upper=1 count=1
small key=-2147483648: lower=0 upper=1 count=1
small key=2147483647: lower=2 upper=3 count=1
small key=2: lower=0 upper=6 count=6
gapsmall k=2: 4294967295
gapsmall k=4: 0
gapsmall k=2: 8
rotated n=1 q=10: ok found=1
rotated n=2 q=20: ok found=5
rotated n=1000 q=5000: ok found=1669
gap n=1000 k=2: 99862
gap n=1000 k=1000: 198
gap n=5000 k=37: 62794748
=== hidden
bounds 2000000 21 100000 2000000
rotated 2000000 22 2000000
bounds 1000000 23 4000000000 1000000
gap 1000000 1000 24 1000000000
gap 500000 250000 25 4000000000
---
bounds n=2000000 q=2000000: ok checksum=64012487511481
rotated n=2000000 q=2000000: ok found=667050
bounds n=1000000 q=1000000: ok checksum=16019682456741
gap n=1000000 k=1000: 1000020
gap n=500000 k=250000: 4292

## Hints
- Use the half-open `[lo, hi)` invariant and `mid = lo + (hi - lo) / 2`. `lower_bound` moves `lo = mid + 1` when `a[mid] < key`; `upper_bound` does it when `a[mid] <= key`.
- Rotated search: first find the index `r` of the minimum with a binary search comparing `a[mid]` against `a[hi]`. Then do an ordinary lower_bound on the *virtual* sorted array `v[i] = a[(i + r) % n]`.
- Gap: `feasible(d)` greedily places a sensor at the first position, then at each next position ≥ last + d. It's monotone (if d works, every smaller d works), so binary search for the **largest** feasible d with `mid = lo + (hi - lo + 1) / 2`. Round up, or `lo = mid` loops forever.
- `max_min_gap` for `INT_MIN` and `INT_MAX` is 4294967295. That's why the function returns `long long`.

## Solution
```c
#include <stddef.h>

size_t lower_bound_i(const int *a, size_t n, int key) {
    size_t lo = 0, hi = n;
    while (lo < hi) {
        size_t mid = lo + (hi - lo) / 2;
        if (a[mid] < key) lo = mid + 1; else hi = mid;
    }
    return lo;
}

size_t upper_bound_i(const int *a, size_t n, int key) {
    size_t lo = 0, hi = n;
    while (lo < hi) {
        size_t mid = lo + (hi - lo) / 2;
        if (a[mid] <= key) lo = mid + 1; else hi = mid;
    }
    return lo;
}

size_t search_rotated(const int *a, size_t n, int key) {
    if (n == 0) return 0;
    size_t lo = 0, hi = n - 1;                 /* find the minimum: the rotation offset */
    while (lo < hi) {
        size_t mid = lo + (hi - lo) / 2;
        if (a[mid] > a[hi]) lo = mid + 1; else hi = mid;
    }
    size_t r = lo;
    lo = 0; hi = n;                            /* lower_bound on v[i] = a[(i + r) % n] */
    while (lo < hi) {
        size_t mid = lo + (hi - lo) / 2;
        if (a[(mid + r) % n] < key) lo = mid + 1; else hi = mid;
    }
    if (lo < n && a[(lo + r) % n] == key) return (lo + r) % n;
    return n;
}

static int feasible(const int *pos, size_t n, int k, long long d) {
    int placed = 1;
    long long last = pos[0];
    for (size_t i = 1; i < n && placed < k; i++)
        if ((long long)pos[i] - last >= d) { placed++; last = pos[i]; }
    return placed >= k;
}

long long max_min_gap(const int *pos, size_t n, int k) {
    long long lo = 0, hi = (long long)pos[n - 1] - pos[0];   /* d = 0 is always feasible */
    while (lo < hi) {
        long long mid = lo + (hi - lo + 1) / 2;              /* round UP: we move lo = mid */
        if (feasible(pos, n, k, mid)) lo = mid; else hi = mid - 1;
    }
    return lo;
}
```

The same invariant discipline makes all four functions correct:
- **Bounds**: the half-open range shrinks every iteration and ends at the boundary of a monotone predicate.
- **Rotated array**: comparing with `a[hi]` (not `a[lo]`) tells you which side holds the minimum, without special cases for unrotated input. After that, modular indexing turns the array back into a sorted one.
- **Search on the answer**: the greedy check is correct because placing the first sensor as early as possible never hurts. When the loop moves `lo = mid`, `mid` must round **up**, or a two-element range never shrinks.
