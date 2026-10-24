---
id: c-fix-link-error
title: Fix the Undefined Reference
difficulty: Easy
order: 2
tags: declarations, definitions, linker
---
## Statement
This program **compiles** but fails to **link** with `undefined reference to 'cube'`: the function is declared (prototype) but never defined. Add the **definition** of `cube` so the program reads an integer `n` and prints `n^3`. Use `long long` to avoid overflow for |n| ≤ 10^6.

## Starter
```c
#include <stdio.h>

long long cube(long long x);   /* declaration only */

int main(void) {
    long long n;
    scanf("%lld", &n);
    printf("%lld\n", cube(n));
    return 0;
}
```

## Tests
=== sample
3
---
27
=== hidden
-4
---
-64
=== hidden
1000000
---
1000000000000000000
=== hidden
0
---
0

## Solution
The prototype satisfies the **compiler**; the **linker** still needs a body. Add the definition (before or after `main`, since the prototype covers calls that come first):

```c
#include <stdio.h>

long long cube(long long x);

int main(void) {
    long long n;
    scanf("%lld", &n);
    printf("%lld\n", cube(n));
    return 0;
}

long long cube(long long x) {
    return x * x * x;
}
```

With `int` instead of `long long`, the `1000000` test overflows (10^18 > 2^31 − 1), and signed overflow is **undefined behaviour** in C. `%lld` is the matching `printf`/`scanf` specifier for `long long`.
