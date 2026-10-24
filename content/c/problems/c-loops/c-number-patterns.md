---
id: c-number-patterns
title: Loops: Primes, Digits and Patterns
difficulty: Medium
order: 1
tags: for, while, do-while, nested loops
---
## Statement
Read an integer `n` (1 ≤ n ≤ 30) and print, in order:

1. `primes:` followed by all primes ≤ n×n (trial division up to √k using `i * i <= k`)
2. `digits:` followed by the digit sum of n! **computed exactly**, using an array of decimal digits (n! for n = 30 has 33 digits, far beyond `long long`)
3. a hollow square of side n made of `#` (borders `#`, interior spaces). For n = 1 it's a single `#`.

## Starter
```c
#include <stdio.h>

int main(void) {
    int n;
    scanf("%d", &n);

    return 0;
}
```

## Tests
=== sample
4
---
primes: 2 3 5 7 11 13
digits: 6
####
#  #
#  #
####
=== hidden
1
---
primes:
digits: 1
#
=== hidden
30
=== hidden
10
---
primes: 2 3 5 7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97
digits: 27
##########
#        #
#        #
#        #
#        #
#        #
#        #
#        #
#        #
##########

## Hints
- Big factorial: keep `int d[64]` with the least significant digit first, starting as `[1]`. Multiply every digit by `k`, then propagate carries with `/ 10` and `% 10`.
- Hollow square: print `#` when `row == 0 || row == n-1 || col == 0 || col == n-1`, otherwise a space.
- For "primes:" with no primes (n = 1), print just `primes:`.

## Solution
```c
#include <stdio.h>

int main(void) {
    int n;
    scanf("%d", &n);

    printf("primes:");
    for (int k = 2; k <= n * n; k++) {
        int prime = 1;
        for (int i = 2; i * i <= k; i++) {
            if (k % i == 0) { prime = 0; break; }
        }
        if (prime) printf(" %d", k);
    }
    printf("\n");

    int d[64] = {1}, len = 1;
    for (int k = 2; k <= n; k++) {
        int carry = 0;
        for (int i = 0; i < len; i++) {
            int x = d[i] * k + carry;
            d[i] = x % 10;
            carry = x / 10;
        }
        while (carry) {
            d[len++] = carry % 10;
            carry /= 10;
        }
    }
    int s = 0;
    for (int i = 0; i < len; i++) s += d[i];
    printf("digits: %d\n", s);

    for (int r = 0; r < n; r++) {
        for (int c = 0; c < n; c++)
            putchar(r == 0 || r == n - 1 || c == 0 || c == n - 1 ? '#' : ' ');
        putchar('\n');
    }
    return 0;
}
```

The digit array is **big-integer arithmetic by hand**, the same algorithm you learned at school. Python hides it inside its `int`. `i * i <= k` avoids calling `sqrt` (and float rounding) for the primality bound. This is the kind of loop-heavy code where C is about 50× faster than Python.
