---
id: c-safe-arith
title: UB-Free Checked Arithmetic Library
difficulty: Hard
order: 1
tags: undefined behavior, signed overflow, INT_MIN, checked arithmetic, parsing
---
## Statement
Write a small **UB-free** integer library. The judge compiles with `-O2`, where the optimiser assumes signed overflow never happens. So naive checks such as `if (a + b < a)` are not just undefined: GCC deletes them. Every function must detect overflow **without ever performing an overflowing signed operation**. (Using `__builtin_*_overflow` is allowed for one function at most. Write the others with limit comparisons, to learn the technique.)

```c
bool checked_add(int a, int b, int *out);     /* false (and *out untouched) on overflow */
bool checked_sub(int a, int b, int *out);
bool checked_mul(int a, int b, int *out);
int  sat_add(int a, int b);                   /* clamp to INT_MIN / INT_MAX instead of overflowing */
bool safe_abs(int a, int *out);               /* false for INT_MIN */
int  midpoint(int a, int b);                  /* floor((a + b) / 2) for ANY ints, no overflow */
bool parse_int(const char *s, int *out);      /* optional '+'/'-', 1+ decimal digits, nothing else;
                                                 false if malformed or out of int range */
```

The driver prints the result of each call for boundary-heavy inputs.

## Starter
```c
#include <stdbool.h>
#include <limits.h>
#include <stdlib.h>

bool checked_add(int a, int b, int *out) { int r = a + b; if ((b > 0 && r < a) || (b < 0 && r > a)) return false; *out = r; return true; }
bool checked_sub(int a, int b, int *out) { *out = a - b; return true; }
bool checked_mul(int a, int b, int *out) { *out = a * b; return true; }
int  sat_add(int a, int b) { return a + b; }
bool safe_abs(int a, int *out) { *out = abs(a); return true; }
int  midpoint(int a, int b) { return (a + b) / 2; }
bool parse_int(const char *s, int *out) { *out = atoi(s); return true; }
```

## Driver
```c
#include <stdio.h>
#include <string.h>

static void show(const char *what, bool ok, int v) {
    if (ok) printf("%s = %d\n", what, v);
    else printf("%s = OVERFLOW\n", what);
}

int main(void) {
    char op[16];
    while (scanf("%15s", op) == 1) {
        char buf[128];
        if (!strcmp(op, "parse")) {
            char s[64];
            if (scanf("%63s", s) != 1) return 1;
            if (!strcmp(s, "EMPTY")) s[0] = '\0';
            int v = 12345;
            bool ok = parse_int(s, &v);
            snprintf(buf, sizeof buf, "parse(\"%s\")", s);
            if (ok) printf("%s = %d\n", buf, v); else printf("%s = INVALID\n", buf);
            continue;
        }
        long long la, lb;
        if (!strcmp(op, "abs")) {
            if (scanf("%lld", &la) != 1) return 1;
            int v = 777;
            bool ok = safe_abs((int)la, &v);
            snprintf(buf, sizeof buf, "abs(%lld)", la);
            show(buf, ok, v);
            continue;
        }
        if (scanf("%lld %lld", &la, &lb) != 2) return 1;
        int a = (int)la, b = (int)lb, v = 777;
        snprintf(buf, sizeof buf, "%s(%d, %d)", op, a, b);
        if (!strcmp(op, "add")) { bool ok = checked_add(a, b, &v); show(buf, ok, v); if (!ok && v != 777) puts("  (out was modified!)"); }
        else if (!strcmp(op, "sub")) { bool ok = checked_sub(a, b, &v); show(buf, ok, v); }
        else if (!strcmp(op, "mul")) { bool ok = checked_mul(a, b, &v); show(buf, ok, v); }
        else if (!strcmp(op, "sat")) printf("%s = %d\n", buf, sat_add(a, b));
        else if (!strcmp(op, "mid")) printf("%s = %d\n", buf, midpoint(a, b));
    }
    return 0;
}
```

## Tests
=== sample
add 2147483647 1
add 5 -7
sub -2147483648 1
mul 46341 46341
sat 2147483000 1000
abs -2147483648
mid 2147483647 2147483645
parse 123
parse 2147483648
---
add(2147483647, 1) = OVERFLOW
add(5, -7) = -2
sub(-2147483648, 1) = OVERFLOW
mul(46341, 46341) = OVERFLOW
sat(2147483000, 1000) = 2147483647
abs(-2147483648) = OVERFLOW
mid(2147483647, 2147483645) = 2147483646
parse("123") = 123
parse("2147483648") = INVALID
=== hidden
add -2147483648 -1
add -2147483648 2147483647
add 2147483647 0
sub 0 -2147483648
sub -1 -2147483648
sub 2147483647 -1
mul -2147483648 -1
mul -2147483648 1
mul 65536 32768
mul -65536 32768
mul 46340 46340
mul -46341 46341
mul 0 -2147483648
mul -1 2147483647
sat -2147483000 -1000
sat -5 3
sat 2147483647 -2147483648
abs 2147483647
abs -5
abs 0
mid -2147483648 2147483647
mid -2147483648 -2147483648
mid -3 0
mid 7 8
mid -7 -8
parse -2147483648
parse +42
parse -0
parse 00017
parse -2147483649
parse 99999999999999999999
parse 12a
parse -
parse +
parse EMPTY
parse 1-2
parse  -17
---
add(-2147483648, -1) = OVERFLOW
add(-2147483648, 2147483647) = -1
add(2147483647, 0) = 2147483647
sub(0, -2147483648) = OVERFLOW
sub(-1, -2147483648) = 2147483647
sub(2147483647, -1) = OVERFLOW
mul(-2147483648, -1) = OVERFLOW
mul(-2147483648, 1) = -2147483648
mul(65536, 32768) = OVERFLOW
mul(-65536, 32768) = -2147483648
mul(46340, 46340) = 2147395600
mul(-46341, 46341) = OVERFLOW
mul(0, -2147483648) = 0
mul(-1, 2147483647) = -2147483647
sat(-2147483000, -1000) = -2147483648
sat(-5, 3) = -2
sat(2147483647, -2147483648) = -1
abs(2147483647) = 2147483647
abs(-5) = 5
abs(0) = 0
mid(-2147483648, 2147483647) = -1
mid(-2147483648, -2147483648) = -2147483648
mid(-3, 0) = -2
mid(7, 8) = 7
mid(-7, -8) = -8
parse("-2147483648") = -2147483648
parse("+42") = 42
parse("-0") = 0
parse("00017") = 17
parse("-2147483649") = INVALID
parse("99999999999999999999") = INVALID
parse("12a") = INVALID
parse("-") = INVALID
parse("+") = INVALID
parse("") = INVALID
parse("1-2") = INVALID
parse("-17") = -17

## Hints
- **add**: overflow iff `b > 0 && a > INT_MAX - b`, or `b < 0 && a < INT_MIN - b`. Check *before* adding.
- **sub**: `a - b` overflows iff `b < 0 && a > INT_MAX + b`, or `b > 0 && a < INT_MIN + b`.
- **mul**: compare against `INT_MAX / b` or `INT_MIN / b`, with case analysis on the signs. Watch `-1 * INT_MIN` and `INT_MIN / -1` (itself UB!). The simplest UB-free approach is `long long p = (long long)a * b` and a range check (a 64-bit product of two 32-bit values can't overflow).
- **midpoint** without overflow: `(a & b) + ((a ^ b) >> 1)` gives the floor for two's complement (arithmetic right shift of a negative value is implementation-defined, and GCC defines it as arithmetic). Alternatively, use 64-bit: `(int)(((long long)a + b) >> 1)`, which is also floor. Note that C's `/` truncates toward zero, so `(-7 + -8) / 2 == -7`, but the floor is −8.
- **parse_int**: accumulate digits as a *negative* number (the negative range is larger), checking `acc < (INT_MIN + d) / 10` before each step. Or accumulate in `long long` and stop as soon as the value exceeds 2³¹. Reject empty strings, a lone sign, and any non-digit.

## Solution
```c
#include <stdbool.h>
#include <limits.h>
#include <stdlib.h>

bool checked_add(int a, int b, int *out) {
    if ((b > 0 && a > INT_MAX - b) || (b < 0 && a < INT_MIN - b)) return false;
    *out = a + b;
    return true;
}

bool checked_sub(int a, int b, int *out) {
    if ((b < 0 && a > INT_MAX + b) || (b > 0 && a < INT_MIN + b)) return false;
    *out = a - b;
    return true;
}

bool checked_mul(int a, int b, int *out) {
    long long p = (long long)a * b;               /* exact: |p| <= 2^62 */
    if (p > INT_MAX || p < INT_MIN) return false;
    *out = (int)p;
    return true;
}

int sat_add(int a, int b) {
    if (b > 0 && a > INT_MAX - b) return INT_MAX;
    if (b < 0 && a < INT_MIN - b) return INT_MIN;
    return a + b;
}

bool safe_abs(int a, int *out) {
    if (a == INT_MIN) return false;               /* -INT_MIN isn't representable */
    *out = a < 0 ? -a : a;
    return true;
}

int midpoint(int a, int b) {
    return (a & b) + ((a ^ b) >> 1);              /* common bits + half the differing bits: floor */
}

bool parse_int(const char *s, int *out) {
    int neg = 0;
    if (*s == '+' || *s == '-') neg = (*s++ == '-');
    if (*s < '0' || *s > '9') return false;       /* empty or a lone sign */
    int acc = 0;                                  /* accumulated as a NEGATIVE number */
    for (; *s; s++) {
        if (*s < '0' || *s > '9') return false;
        int d = *s - '0';
        if (acc < (INT_MIN + d) / 10) return false;   /* acc * 10 - d would go below INT_MIN */
        acc = acc * 10 - d;
    }
    if (!neg) {
        if (acc == INT_MIN) return false;         /* +2147483648 doesn't fit */
        acc = -acc;
    }
    *out = acc;
    return true;
}
```

Every check is done **before** the operation, using only operations that can't overflow:
- For addition, `INT_MAX − b` can't overflow when `b > 0`, and `INT_MIN − b` can't when `b < 0`. That's why the condition splits on the sign of b.
- Multiplication widens to 64 bits, the simplest correct technique. A pure-int version needs four sign cases with divisions, and must avoid `INT_MIN / −1`.
- `midpoint` uses the identity a + b = 2·(a & b) + (a ^ b). Halving the differing bits never overflows and rounds towards −∞.
- `parse_int` accumulates in the negative range, because −2147483648 has no positive counterpart. It checks `acc < (INT_MIN + d) / 10` before multiplying, which is the same technique the C library's `strtol` uses internally.
