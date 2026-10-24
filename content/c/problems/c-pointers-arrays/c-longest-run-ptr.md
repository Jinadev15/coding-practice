---
id: c-longest-run-ptr
title: Longest Increasing Run
difficulty: Medium
order: 1
tags: pointers and arrays, output parameters
---
## Statement
Implement `const int *longest_run(const int *a, size_t n, size_t *len)`, which returns a pointer to the **start** of the longest strictly increasing contiguous run, and writes its length through `len` (the first such run on ties). For `n == 0`, return `NULL` and set `*len = 0`.

The driver then prints the run **using only the returned pointer and the length**.

## Starter
```c
#include <stddef.h>

const int *longest_run(const int *a, size_t n, size_t *len) {
    *len = 0;
    return NULL;
}
```

## Driver
```c
#include <stdio.h>
int main(void) {
    size_t n;
    scanf("%zu", &n);
    static int a[200000];
    for (size_t i = 0; i < n; i++) scanf("%d", &a[i]);
    size_t len;
    const int *start = longest_run(a, n, &len);
    if (!start) { printf("empty\n"); return 0; }
    printf("start=%td len=%zu:", start - a, len);
    for (const int *p = start; p < start + len; p++) printf(" %d", *p);
    printf("\n");
    return 0;
}
```

## Tests
=== sample
8
5 1 2 3 2 4 6 8
---
start=4 len=4: 2 4 6 8
=== hidden
3
3 2 1
---
start=0 len=1: 3
=== hidden
0

---
empty
=== hidden
6
1 2 2 3 4 5
---
start=2 len=4: 2 3 4 5

## Solution
One pass tracks the start of the current run. Whenever the run breaks (or the array ends), compare its length with the best so far.

```c
#include <stddef.h>

const int *longest_run(const int *a, size_t n, size_t *len) {
    if (n == 0) { *len = 0; return NULL; }
    const int *best = a, *cur = a;
    size_t best_len = 1;
    for (size_t i = 1; i <= n; i++) {
        if (i == n || a[i] <= a[i - 1]) {
            size_t run = (size_t)((a + i) - cur);
            if (run > best_len) { best_len = run; best = cur; }
            cur = a + i;
        }
    }
    *len = best_len;
    return best;
}
```

Returning a pointer **into the caller's array** (instead of copying the run) is zero-copy and idiomatic C. `strchr` and `strstr` work the same way. The `const` on the return type matters: since the input was `const int *`, the function mustn't hand back a non-const pointer to the same data.
