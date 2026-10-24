---
id: c-rotate-dedupe
title: In-Place Array Operations
difficulty: Medium
order: 1
tags: arrays, two pointers, in-place
---
## Statement
Implement three in-place array functions (no extra arrays):

- `void reverse_range(int *a, size_t lo, size_t hi)` reverses `a[lo..hi]` inclusive (for `lo <= hi`)
- `void rotate_right(int *a, size_t n, size_t k)` rotates right by `k` (k may exceed n) using three reversals
- `size_t dedupe_sorted(int *a, size_t n)` removes duplicates from a **sorted** array, keeping the first occurrences at the front, and returns the new length

## Starter
```c
#include <stddef.h>

void reverse_range(int *a, size_t lo, size_t hi) {
}

void rotate_right(int *a, size_t n, size_t k) {
}

size_t dedupe_sorted(int *a, size_t n) {
    return n;
}
```

## Driver
```c
#include <stdio.h>
int main(void) {
    size_t n, k;
    scanf("%zu %zu", &n, &k);
    int a[200005];
    for (size_t i = 0; i < n; i++) scanf("%d", &a[i]);
    rotate_right(a, n, k);
    for (size_t i = 0; i < n; i++) printf("%d ", a[i]);
    printf("\n");
    size_t m;
    scanf("%zu", &m);
    for (size_t i = 0; i < m; i++) scanf("%d", &a[i]);
    size_t len = dedupe_sorted(a, m);
    printf("%zu:", len);
    for (size_t i = 0; i < len; i++) printf(" %d", a[i]);
    printf("\n");
    return 0;
}
```

## Tests
=== sample
5 2
1 2 3 4 5
6
1 1 2 3 3 3
---
4 5 1 2 3 
3: 1 2 3
=== hidden
1 100
7
1
4
---
7 
1: 4
=== hidden
4 0
9 8 7 6
5
-2 -2 -2 -2 -2
---
9 8 7 6 
1: -2
=== hidden
6 13
1 2 3 4 5 6
0

---
6 1 2 3 4 5 
0:

## Hints
- `rotate_right`: `k %= n`; reverse everything, then the first `k`, then the rest. Guard `n == 0` and `k == 0` (the range `[0, k-1]` would underflow for `size_t`).
- `dedupe_sorted`: write pointer `w`; copy `a[r]` to `a[w++]` whenever it differs from `a[w-1]`.

## Solution
```c
#include <stddef.h>

void reverse_range(int *a, size_t lo, size_t hi) {
    while (lo < hi) {
        int t = a[lo];
        a[lo] = a[hi];
        a[hi] = t;
        lo++;
        hi--;
    }
}

void rotate_right(int *a, size_t n, size_t k) {
    if (n == 0) return;
    k %= n;
    if (k == 0) return;
    reverse_range(a, 0, n - 1);
    reverse_range(a, 0, k - 1);
    reverse_range(a, k, n - 1);
}

size_t dedupe_sorted(int *a, size_t n) {
    if (n == 0) return 0;
    size_t w = 1;
    for (size_t r = 1; r < n; r++)
        if (a[r] != a[w - 1])
            a[w++] = a[r];
    return w;
}
```

With `size_t` indices, `k - 1` for `k == 0` wraps to 18446744073709551615, which is why the `k == 0` guard is essential. That's the unsigned trap from the Type Conversion lesson again. Inside `reverse_range`, `hi--` when `hi == 0` can't happen, because the loop requires `lo < hi`.
