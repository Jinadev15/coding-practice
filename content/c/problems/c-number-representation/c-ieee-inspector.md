---
id: c-ieee-inspector
title: IEEE-754 Inspector and Safe Numeric Conversions
difficulty: Hard
order: 1
tags: IEEE-754, two's complement, floating point, ULP, saturation, Kahan summation
---
## Statement
Write a command-line numeric inspector of the kind used to debug sensor pipelines. Commands, one per line:

| Command | Output |
|---|---|
| `bits D` | the 64-bit pattern of double D: `sign=S exp=E (unbiased U) frac=0xFFFFFFFFFFFFF class=C`, where C is one of `zero`, `subnormal`, `normal`, `inf`, `nan`; for zero, subnormal, inf and nan, print `unbiased -` |
| `fbits F` | the same for a 32-bit float: `frac` is 6 hex digits (23 bits) |
| `twos N W` | the W-bit two's complement pattern of integer N (−2^(W−1) ≤ N < 2^(W−1), W ≤ 64) as binary, and its unsigned reading: `bits=… unsigned=…` |
| `ulps A B` | the number of representable doubles between A and B (the ULP distance, ≥ 0); A and B are finite |
| `near A B` | `true`/`false` using the relative tolerance 1e-9 and absolute tolerance 1e-12 |
| `to16 D` | convert double D to `int16_t` safely: round to nearest (ties away from zero), saturate to [−32768, 32767], NaN → 0; print the value and `(saturated)` or `(nan)` when applicable |
| `sum N V` | add V to itself N times in **float**, naively and with Kahan compensation (accumulating in float); print both with `%.6f` |

Parse D with `strtod` (it accepts `inf`, `-inf`, `nan` and hex floats like `0x1p-1074`). Every conversion must avoid undefined behaviour: read bit patterns with `memcpy`, never cast an out-of-range double to an integer, and never shift negative values.

## Starter
```c
#include <stdio.h>
#include <string.h>

int main(void) {
    char cmd[16];
    while (scanf("%15s", cmd) == 1) {
        /* TODO */
    }
    return 0;
}
```

## Tests
=== sample
bits 1.0
bits -0.0
fbits 0.1
twos -5 8
ulps 1.0 1.0000000000000004
near 0.30000000000000004 0.3
to16 40000.7
sum 1000000 0.1
---
bits 1.0: sign=0 exp=1023 (unbiased 0) frac=0x0000000000000 class=normal
bits -0.0: sign=1 exp=0 (unbiased -) frac=0x0000000000000 class=zero
fbits 0.1: sign=0 exp=123 (unbiased -4) frac=0x4CCCCD class=normal
twos -5 8: bits=11111011 unsigned=251
ulps 1.0 1.0000000000000004: 2
near 0.30000000000000004 0.3: true
to16 40000.7: 32767 (saturated)
sum 1000000 x 0.1: naive=100958.343750 kahan=100000.000000
=== hidden
bits 0.1
bits inf
bits -inf
bits nan
bits 0x1p-1074
bits 0x1.fffffffffffffp+1023
bits 2.2250738585072014e-308
fbits 1.0
fbits -2.5
fbits 0x1p-149
fbits 16777217
twos 0 4
twos -1 64
twos 127 8
twos -128 8
twos -9223372036854775808 64
ulps 0.0 -0.0
ulps 0x1p-1074 -0x1p-1074
ulps 1.0 2.0
ulps -1.0 1.0
near 0.0 1e-13
near 1e9 1000000000.5
near 1e9 1000002000
near inf inf
to16 -32768.4
to16 -32768.6
to16 2.5
to16 -2.5
to16 nan
to16 -1e300
to16 32766.5
sum 10 0.1
sum 16777217 1.0
---
bits 0.1: sign=0 exp=1019 (unbiased -4) frac=0x999999999999A class=normal
bits inf: sign=0 exp=2047 (unbiased -) frac=0x0000000000000 class=inf
bits -inf: sign=1 exp=2047 (unbiased -) frac=0x0000000000000 class=inf
bits nan: sign=0 exp=2047 (unbiased -) frac=0x8000000000000 class=nan
bits 0x1p-1074: sign=0 exp=0 (unbiased -) frac=0x0000000000001 class=subnormal
bits 0x1.fffffffffffffp+1023: sign=0 exp=2046 (unbiased 1023) frac=0xFFFFFFFFFFFFF class=normal
bits 2.2250738585072014e-308: sign=0 exp=1 (unbiased -1022) frac=0x0000000000000 class=normal
fbits 1.0: sign=0 exp=127 (unbiased 0) frac=0x000000 class=normal
fbits -2.5: sign=1 exp=128 (unbiased 1) frac=0x200000 class=normal
fbits 0x1p-149: sign=0 exp=0 (unbiased -) frac=0x000001 class=subnormal
fbits 16777217: sign=0 exp=151 (unbiased 24) frac=0x000000 class=normal
twos 0 4: bits=0000 unsigned=0
twos -1 64: bits=1111111111111111111111111111111111111111111111111111111111111111 unsigned=18446744073709551615
twos 127 8: bits=01111111 unsigned=127
twos -128 8: bits=10000000 unsigned=128
twos -9223372036854775808 64: bits=1000000000000000000000000000000000000000000000000000000000000000 unsigned=9223372036854775808
ulps 0.0 -0.0: 0
ulps 0x1p-1074 -0x1p-1074: 2
ulps 1.0 2.0: 4503599627370496
ulps -1.0 1.0: 9214364837600034816
near 0.0 1e-13: true
near 1e9 1000000000.5: true
near 1e9 1000002000: false
near inf inf: true
to16 -32768.4: -32768
to16 -32768.6: -32768 (saturated)
to16 2.5: 3
to16 -2.5: -3
to16 nan: 0 (nan)
to16 -1e300: -32768 (saturated)
to16 32766.5: 32767
sum 10 x 0.1: naive=1.000000 kahan=1.000000
sum 16777217 x 1: naive=16777216.000000 kahan=16777216.000000

## Hints
- `uint64_t u; memcpy(&u, &d, 8);`, then sign = `u >> 63`, exponent = `(u >> 52) & 0x7FF`, fraction = `u & ((1ULL << 52) - 1)`. An exponent of all ones is inf/nan, and 0 is zero/subnormal. For floats, the fields are 1/8/23 with bias 127.
- `twos`: do the arithmetic in `uint64_t` (`(uint64_t)N` is well defined modulo 2⁶⁴), then mask to W bits (careful: `1ULL << 64` is UB, so handle W = 64 separately).
- ULP distance: map each double's bits to a *monotonic* integer: for non-negative values use `u`, for negative ones use `-(u & ~sign)`, in a signed 64-bit type, which is fine since |u| < 2⁶³. Then take the absolute difference. +0 and −0 then both map to 0.
- `to16`: `if (isnan(d))`, then compare with the limits **as doubles** before converting. `lround`'s ties go away from zero.
- Kahan: `y = v - c; t = sum + y; c = (t - sum) - y; sum = t;` with every variable a `float`. Compile without `-ffast-math`, which would optimise the compensation away.

## Solution
```c
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <inttypes.h>

static const char *dclass(uint64_t e, uint64_t f, uint64_t emax) {
    if (e == emax) return f ? "nan" : "inf";
    if (e == 0) return f ? "subnormal" : "zero";
    return "normal";
}

static int64_t ordered(double d) {               /* monotonic mapping of doubles to integers */
    uint64_t u;
    memcpy(&u, &d, sizeof u);
    if (u >> 63) return -(int64_t)(u & ~(1ULL << 63));
    return (int64_t)u;
}

int main(void) {
    char cmd[16], a[128], b[128];
    while (scanf("%15s", cmd) == 1) {
        if (!strcmp(cmd, "bits")) {
            if (scanf("%127s", a) != 1) return 1;
            double d = strtod(a, NULL);
            uint64_t u;
            memcpy(&u, &d, sizeof u);
            uint64_t s = u >> 63, e = (u >> 52) & 0x7FF, f = u & ((1ULL << 52) - 1);
            const char *c = dclass(e, f, 0x7FF);
            printf("bits %s: sign=%" PRIu64 " exp=%" PRIu64, a, s, e);
            if (!strcmp(c, "normal")) printf(" (unbiased %d)", (int)e - 1023);
            else printf(" (unbiased -)");
            printf(" frac=0x%013" PRIX64 " class=%s\n", f, c);
        } else if (!strcmp(cmd, "fbits")) {
            if (scanf("%127s", a) != 1) return 1;
            float x = strtof(a, NULL);
            uint32_t u;
            memcpy(&u, &x, sizeof u);
            uint32_t s = u >> 31, e = (u >> 23) & 0xFF, f = u & 0x7FFFFF;
            const char *c = dclass(e, f, 0xFF);
            printf("fbits %s: sign=%u exp=%u", a, (unsigned)s, (unsigned)e);
            if (!strcmp(c, "normal")) printf(" (unbiased %d)", (int)e - 127);
            else printf(" (unbiased -)");
            printf(" frac=0x%06X class=%s\n", (unsigned)f, c);
        } else if (!strcmp(cmd, "twos")) {
            long long n; int w;
            if (scanf("%lld %d", &n, &w) != 2) return 1;
            uint64_t u = (uint64_t)n;                         /* well defined: modulo 2^64 */
            if (w < 64) u &= (1ULL << w) - 1;
            printf("twos %lld %d: bits=", n, w);
            for (int i = w - 1; i >= 0; i--) putchar((u >> i) & 1 ? '1' : '0');
            printf(" unsigned=%" PRIu64 "\n", u);
        } else if (!strcmp(cmd, "ulps")) {
            if (scanf("%127s %127s", a, b) != 2) return 1;
            int64_t x = ordered(strtod(a, NULL)), y = ordered(strtod(b, NULL));
            uint64_t d = x > y ? (uint64_t)x - (uint64_t)y : (uint64_t)y - (uint64_t)x;
            printf("ulps %s %s: %" PRIu64 "\n", a, b, d);
        } else if (!strcmp(cmd, "near")) {
            if (scanf("%127s %127s", a, b) != 2) return 1;
            double x = strtod(a, NULL), y = strtod(b, NULL);
            int ok = x == y;
            if (!ok) {
                double diff = fabs(x - y);
                ok = diff <= 1e-12 || diff <= 1e-9 * fmax(fabs(x), fabs(y));
            }
            printf("near %s %s: %s\n", a, b, ok ? "true" : "false");
        } else if (!strcmp(cmd, "to16")) {
            if (scanf("%127s", a) != 1) return 1;
            double d = strtod(a, NULL);
            if (isnan(d)) { printf("to16 %s: 0 (nan)\n", a); continue; }
            double r = round(d);                              /* ties away from zero */
            if (r > 32767.0) printf("to16 %s: 32767 (saturated)\n", a);
            else if (r < -32768.0) printf("to16 %s: -32768 (saturated)\n", a);
            else printf("to16 %s: %d\n", a, (int)(int16_t)r);
        } else if (!strcmp(cmd, "sum")) {
            long n; float v;
            if (scanf("%ld %f", &n, &v) != 2) return 1;
            float naive = 0.0f, sum = 0.0f, c = 0.0f;
            for (long i = 0; i < n; i++) {
                naive += v;
                float y = v - c;
                float t = sum + y;
                c = (t - sum) - y;
                sum = t;
            }
            printf("sum %ld x %g: naive=%.6f kahan=%.6f\n", n, (double)v, (double)naive, (double)sum);
        }
    }
    return 0;
}
```

What the tool demonstrates:
- **Bit patterns** are read with `memcpy`, the aliasing-safe way. `0.1` shows the repeating fraction `0x999999999999A`, the binary analogue of 1/3 = 0.333….
- **Two's complement** falls out of unsigned arithmetic: converting to `uint64_t` is defined modulo 2⁶⁴, and masking gives any narrower width.
- **ULP distance** uses the fact that IEEE-754 bit patterns, read as sign-magnitude integers, are ordered like the values they represent. The mapping makes +0 and −0 the same point and counts every subnormal in between. That's the robust way to write floating-point equality tests with a tolerance in units of precision.
- **Saturating conversion** checks the range in floating point *before* converting, because an out-of-range double-to-integer conversion is undefined behaviour (the Ariane 5 failure mode).
- **Kahan summation** recovers the 0.1s that naive float accumulation loses. The naive sum of a million 0.1f drifts to about 100958, and at 2²⁴ adding 1.0f stops changing the sum at all.
