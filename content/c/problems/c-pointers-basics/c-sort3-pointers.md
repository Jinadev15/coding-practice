---
id: c-sort3-pointers
title: Sort Three Through Pointers
difficulty: Easy
order: 1
tags: pointers, swap, output parameters
---
## Statement
Implement:

- `void swap(int *a, int *b)` swaps the two ints
- `void sort3(int *a, int *b, int *c)` reorders so that `*a <= *b <= *c`, using only `swap` (at most 3 swaps)
- `void divmod(int a, int b, int *q, int *r)` writes C's quotient and remainder (b ≠ 0)

## Starter
```c
void swap(int *a, int *b) {
}

void sort3(int *a, int *b, int *c) {
}

void divmod(int a, int b, int *q, int *r) {
}
```

## Driver
```c
#include <stdio.h>
int main(void) {
    int x, y, z;
    while (scanf("%d %d %d", &x, &y, &z) == 3) {
        sort3(&x, &y, &z);
        int q, r;
        divmod(z, x == 0 ? 1 : x, &q, &r);
        printf("%d %d %d | %d %d\n", x, y, z, q, r);
    }
    return 0;
}
```

## Tests
=== sample
3 1 2
---
1 2 3 | 3 0
=== hidden
5 5 1
-1 -7 4
0 0 0
9 8 7
---
1 5 5 | 5 0
-7 -1 4 | 0 4
0 0 0 | 0 0
7 8 9 | 1 2

## Solution
Three compare-and-swap steps form a tiny sorting network: the first two put the minimum in `*a`, and the last one orders the remaining pair.

```c
void swap(int *a, int *b) {
    int t = *a;
    *a = *b;
    *b = t;
}

void sort3(int *a, int *b, int *c) {
    if (*a > *b) swap(a, b);
    if (*a > *c) swap(a, c);
    if (*b > *c) swap(b, c);
}

void divmod(int a, int b, int *q, int *r) {
    *q = a / b;
    *r = a % b;
}
```

Note that inside `sort3`, `a`, `b` and `c` are **already pointers**, so they're passed to `swap` directly. Writing `swap(&a, &b)` would pass `int **`, which is a compiler warning and wrong behaviour. Fixed compare-swap sequences like this are called sorting networks, and GPUs and SIMD code use them because they have no data-dependent branches in the overall structure.
