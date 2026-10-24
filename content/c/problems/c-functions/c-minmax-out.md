---
id: c-minmax-out
title: Output Parameters
difficulty: Easy
order: 1
tags: pass by pointer, output parameters, arrays
---
## Statement
Implement:

```c
int stats(const int *a, size_t n, int *min, int *max, double *mean);
```

It returns `0` and writes the minimum, maximum and mean through the pointers when `n > 0`. It returns `-1` and writes **nothing** when `n == 0`. Also implement `void scale(int *a, size_t n, int k)`, which multiplies every element **in place**.

## Starter
```c
#include <stddef.h>

int stats(const int *a, size_t n, int *min, int *max, double *mean) {
    return -1;
}

void scale(int *a, size_t n, int k) {
}
```

## Driver
```c
#include <stdio.h>
int main(void) {
    size_t n; int k;
    if (scanf("%zu %d", &n, &k) != 2) return 1;
    int a[1000];
    for (size_t i = 0; i < n; i++) scanf("%d", &a[i]);
    int mn = 12345, mx = 12345; double mean = 99.0;
    int rc = stats(a, n, &mn, &mx, &mean);
    printf("rc=%d min=%d max=%d mean=%.2f\n", rc, mn, mx, mean);
    scale(a, n, k);
    for (size_t i = 0; i < n; i++) printf("%d ", a[i]);
    printf("\n");
    return 0;
}
```

## Tests
=== sample
4 2
3 -1 7 0
---
rc=0 min=-1 max=7 mean=2.25
6 -2 14 0 
=== hidden
0 5

---
rc=-1 min=12345 max=12345 mean=99.00

=== hidden
1 -3
8
---
rc=0 min=8 max=8 mean=8.00
-24 

## Solution
The caller passes addresses, and the function writes results through them. `const int *a` documents (and enforces) that `stats` doesn't modify the array.

```c
#include <stddef.h>

int stats(const int *a, size_t n, int *min, int *max, double *mean) {
    if (n == 0) return -1;
    int lo = a[0], hi = a[0];
    long long sum = 0;
    for (size_t i = 0; i < n; i++) {
        if (a[i] < lo) lo = a[i];
        if (a[i] > hi) hi = a[i];
        sum += a[i];
    }
    *min = lo;
    *max = hi;
    *mean = (double)sum / (double)n;
    return 0;
}

void scale(int *a, size_t n, int k) {
    for (size_t i = 0; i < n; i++)
        a[i] *= k;
}
```

Returning a status code and passing results through pointers is **the** standard C API shape (look at `scanf`, `pthread_create`, `strtol`). The `n == 0` case leaves the outputs untouched, which the driver checks with its sentinel values.
