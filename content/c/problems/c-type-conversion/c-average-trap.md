---
id: c-average-trap
title: The Average and Unsigned Traps
difficulty: Medium
order: 1
tags: casts, usual arithmetic conversions, size_t
---
## Statement
Fix **three** classic conversion bugs in the given program (the logic is right; only the types and casts are wrong):

1. the mean is computed with integer division
2. a backwards loop over a `size_t` index never terminates
3. a "longer than 5 characters" check uses unsigned subtraction that wraps

For each input line (a word), the program prints the word reversed, its length, whether it's `long` (more than 5 characters) or `short`, and at the end the mean word length with 2 decimals.

## Starter
```c
#include <stdio.h>
#include <string.h>

int main(void) {
    char w[101];
    int total = 0, count = 0;
    while (scanf("%100s", w) == 1) {
        size_t n = strlen(w);
        for (size_t i = n - 1; i >= 0; i--)      /* bug 2 */
            putchar(w[i]);
        printf(" %zu %s\n", n, (n - 5 > 0) ? "long" : "short");   /* bug 3 */
        total += (int)n;
        count++;
    }
    double mean = total / count;                  /* bug 1 */
    printf("mean %.2f\n", count ? mean : 0.0);
    return 0;
}
```

## Tests
=== sample
robotics
arm
---
scitobor 8 long
mra 3 short
mean 5.50
=== hidden
abcde
abcdef
x
---
edcba 5 short
fedcba 6 long
x 1 short
mean 4.00

## Hints
- Bug 1: `(double)total / count`. But `count` might be zero, so guard it before dividing.
- Bug 2: `for (size_t i = n; i-- > 0; )`.
- Bug 3: compare directly, `n > 5`. Never subtract unsigned values to compare them.

## Solution
```c
#include <stdio.h>
#include <string.h>

int main(void) {
    char w[101];
    int total = 0, count = 0;
    while (scanf("%100s", w) == 1) {
        size_t n = strlen(w);
        for (size_t i = n; i-- > 0; )
            putchar(w[i]);
        printf(" %zu %s\n", n, (n > 5) ? "long" : "short");
        total += (int)n;
        count++;
    }
    double mean = count ? (double)total / count : 0.0;
    printf("mean %.2f\n", mean);
    return 0;
}
```

All three bugs compile. Two of them even pass a quick test sometimes. With `-Wall -Wextra`, gcc warns about bug 2 ("comparison of unsigned expression in '>= 0' is always true"). `n - 5 > 0` for `n = 3` computes `3 - 5`, which wraps to 18446744073709551614 as a `size_t`, so short words are reported as long.
