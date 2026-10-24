---
id: c-trunc-vs-floor
title: Truncation vs Floor Division
difficulty: Medium
order: 2
tags: integer division, modulo, negative numbers
---
## Statement
C's `/` truncates toward zero, but many algorithms (time wrapping, circular buffers, grid coordinates) need **floor** division and a **non-negative** modulo, as in Python. Implement:

- `long long floor_div(long long a, long long b)`: ⌊a / b⌋
- `long long floor_mod(long long a, long long b)`: `a - b * floor_div(a, b)` (it has the sign of `b`)
- `long long wrap(long long i, long long n)`: an index into a circular buffer of size `n > 0`, always in `[0, n)`

Inputs satisfy `b != 0` and |values| ≤ 10^18. Don't use floating point.

## Starter
```c
#include <stdio.h>

long long floor_div(long long a, long long b) {
    return 0;
}

long long floor_mod(long long a, long long b) {
    return 0;
}

long long wrap(long long i, long long n) {
    return 0;
}
```

## Driver
```c
#include <stdio.h>
int main(void) {
    long long a, b;
    while (scanf("%lld %lld", &a, &b) == 2) {
        printf("C: %lld %lld | floor: %lld %lld", a / b, a % b, floor_div(a, b), floor_mod(a, b));
        if (b > 0) printf(" | wrap: %lld", wrap(a, b));
        printf("\n");
    }
    return 0;
}
```

## Tests
=== sample
7 2
-7 2
---
C: 3 1 | floor: 3 1 | wrap: 1
C: -3 -1 | floor: -4 1 | wrap: 1
=== hidden
7 -2
-7 -2
-1 5
-10 5
0 3
---
C: -3 1 | floor: -4 -1
C: 3 -1 | floor: 3 -1
C: 0 -1 | floor: -1 4 | wrap: 4
C: -2 0 | floor: -2 0 | wrap: 0
C: 0 0 | floor: 0 0 | wrap: 0
=== hidden
-1000000000000000000 7
---
C: -142857142857142857 -1 | floor: -142857142857142858 6 | wrap: 6

## Hints
- Start from C's truncated quotient `q = a / b` and remainder `r = a % b`.
- If `r != 0` and `r` has a different sign from `b`, then `q` is one too large: subtract 1.
- `wrap(i, n)` is just `floor_mod(i, n)` with `n > 0`.

## Solution
```c
#include <stdio.h>

long long floor_div(long long a, long long b) {
    long long q = a / b, r = a % b;
    if (r != 0 && ((r < 0) != (b < 0)))
        q -= 1;
    return q;
}

long long floor_mod(long long a, long long b) {
    return a - b * floor_div(a, b);
}

long long wrap(long long i, long long n) {
    return floor_mod(i, n);
}
```

This is the exact mirror of the Python problem *Python vs C Division*. A common shortcut, `((i % n) + n) % n`, also works for `wrap` but can overflow when `i` is near the type's limits. In a ring buffer, `wrap(head - 1, n)` must give `n - 1` when `head == 0`, and plain C `%` would give `-1` and index out of bounds.
