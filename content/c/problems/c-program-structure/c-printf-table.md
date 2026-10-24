---
id: c-printf-table
title: printf Formatting Table
difficulty: Easy
order: 1
tags: printf, width, precision
---
## Statement
Read an integer `n` and a real number `x`. Print exactly these lines:

1. `n` right-aligned in a field of width 8, between brackets: `[      42]`
2. `n` left-aligned in width 8: `[42      ]`
3. `n` zero-padded to width 8: `[00000042]`
4. `n` in hexadecimal (lowercase) and octal, separated by a space
5. `x` with exactly 3 decimals
6. `x` in scientific notation with 2 decimals (`%.2e`)
7. the text `100%` (a literal percent sign)

## Starter
```c
#include <stdio.h>

int main(void) {
    int n;
    double x;
    scanf("%d %lf", &n, &x);

    return 0;
}
```

## Tests
=== sample
42 3.14159
---
[      42]
[42      ]
[00000042]
2a 52
3.142
3.14e+00
100%
=== hidden
255 12345.6789
---
[     255]
[255     ]
[00000255]
ff 377
12345.679
1.23e+04
100%
=== hidden
-7 -0.0005
---
[      -7]
[-7      ]
[-0000007]
fffffff9 37777777771
-0.001
-5.00e-04
100%

## Hints
- Width: `%8d`, left-align with `%-8d`, zero-pad with `%08d`.
- `%x` and `%o` print the bits of the value as **unsigned**, so negative numbers show their two's-complement bit pattern.
- `%%` prints a single `%`.

## Solution
```c
#include <stdio.h>

int main(void) {
    int n;
    double x;
    scanf("%d %lf", &n, &x);
    printf("[%8d]\n", n);
    printf("[%-8d]\n", n);
    printf("[%08d]\n", n);
    printf("%x %o\n", (unsigned)n, (unsigned)n);
    printf("%.3f\n", x);
    printf("%.2e\n", x);
    printf("100%%\n");
    return 0;
}
```

`%lf` in `scanf` reads a `double`. In `printf`, `%f` already means double (a float argument is promoted to double automatically). That asymmetry trips up many students. The cast to `unsigned` matches what `%x`/`%o` expect: `-7` as a 32-bit unsigned value is `0xfffffff9`, its two's-complement pattern.
