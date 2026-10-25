---
id: c-q16-dsp
title: A Bit-Exact Fixed-Point DSP Kernel
difficulty: Hard
order: 1
tags: fixed point, Q16.16, Q15, saturation, rounding, FIR, integer sqrt
time_limit: 2
---
## Statement
Your motor controller's MCU has no FPU. Implement a small fixed-point library whose results are **bit-exact**: the judge compares integers, not approximations. **No floating point is allowed** in any of these functions.

`typedef int32_t q16_t;` is Q16.16, and Q15 values are `int16_t`. "Saturate" means clamp to the type's range.

| Function | Exact definition |
|---|---|
| `q16_t q16_add_sat(q16_t a, q16_t b)` | `a + b`, saturated to int32. |
| `q16_t q16_mul(q16_t a, q16_t b)` | `floor((a·b + 2¹⁵) / 2¹⁶)`, computed exactly in 64 bits, then saturated. |
| `q16_t q16_div(q16_t a, q16_t b)` | `a·2¹⁶ / b` **rounded to nearest, ties away from zero**, then saturated. `b == 0` gives INT32_MAX if `a >= 0`, else INT32_MIN. |
| `q16_t q16_sqrt(q16_t a)` | `floor(sqrt(a / 2¹⁶) · 2¹⁶)`, which is `floor(sqrt(a · 2¹⁶))` over the integers. Returns 0 for `a <= 0`. |
| `int16_t fir_q15(const int16_t *h, const int16_t *x, int n)` | `Σ h[k]·x[k]` accumulated exactly (64-bit), then `floor((acc + 2¹⁴) / 2¹⁵)`, saturated to int16. |
| `int16_t ema_q15(int16_t prev, int16_t sample, int16_t alpha)` | `prev + alpha·(sample − prev)` in Q15: `d = sample − prev` (as int32), `prev + floor((alpha·d + 2¹⁴) / 2¹⁵)`, saturated to int16. |

`floor(v / 2^k)` of a signed 64-bit value is the arithmetic right shift `v >> k`, which GCC guarantees.

The hidden tests include INT32_MIN/MAX, `-1`, `0`, large random values and 100,000-sample filters.

## Starter
```c
#include <stdint.h>
typedef int32_t q16_t;

q16_t q16_add_sat(q16_t a, q16_t b) { return a + b; }
q16_t q16_mul(q16_t a, q16_t b) { return (a * b) >> 16; }
q16_t q16_div(q16_t a, q16_t b) { return b ? (a / b) << 16 : 0; }
q16_t q16_sqrt(q16_t a) { (void)a; return 0; }
int16_t fir_q15(const int16_t *h, const int16_t *x, int n) {
    int32_t acc = 0;
    for (int k = 0; k < n; k++) acc += (h[k] * x[k]) >> 15;
    return (int16_t)acc;
}
int16_t ema_q15(int16_t prev, int16_t sample, int16_t alpha) {
    return (int16_t)(prev + ((alpha * (sample - prev)) >> 15));
}
```

## Driver
```c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

static uint64_t s = 88172645463325252ull;
static uint32_t rnd(void) { s ^= s << 13; s ^= s >> 7; s ^= s << 17; return (uint32_t)s; }
static int32_t pick(void) {
    static const int32_t edge[] = {0, 1, -1, 65536, -65536, 32768, -32768, INT32_MAX, INT32_MIN, INT32_MAX - 1, INT32_MIN + 1, 3, -3};
    uint32_t r = rnd() % 10;
    if (r == 0) return edge[rnd() % 13];
    if (r < 4) return (int32_t)(rnd() % 0x00FFFFFFu) - 0x007FFFFF;
    return (int32_t)rnd();
}
#define MIX(h, v) ((h) = ((h) ^ (uint32_t)(v)) * 1099511628211ull)

int main(void) {
    char cmd[32];
    while (scanf("%31s", cmd) == 1) {
        if (!strcmp(cmd, "basic")) {
            printf("add %d %d %d\n", q16_add_sat(65536, 98304), q16_add_sat(INT32_MAX, 1), q16_add_sat(INT32_MIN, -5));
            printf("mul %d %d %d %d %d\n", q16_mul(98304, -147456), q16_mul(1, 32768), q16_mul(-1, 32768),
                   q16_mul(INT32_MAX, INT32_MAX), q16_mul(INT32_MIN, 65536));
            printf("div %d %d %d %d %d %d\n", q16_div(65536, 196608), q16_div(-65536, 196608), q16_div(1, 131072),
                   q16_div(-1, 131072), q16_div(5, 0), q16_div(INT32_MIN, -1));
            printf("sqrt %d %d %d %d %d\n", q16_sqrt(65536 * 4), q16_sqrt(131072), q16_sqrt(1), q16_sqrt(-7), q16_sqrt(INT32_MAX));
        } else if (!strcmp(cmd, "fuzz")) {
            uint64_t h1 = 1469598103934665603ull, h2 = h1, h3 = h1, h4 = h1;
            for (int i = 0; i < 300000; i++) {
                int32_t a = pick(), b = pick();
                MIX(h1, q16_add_sat(a, b)); MIX(h2, q16_mul(a, b)); MIX(h3, q16_div(a, b)); MIX(h4, q16_sqrt(a));
            }
            printf("add %016llx\nmul %016llx\ndiv %016llx\nsqrt %016llx\n", (unsigned long long)h1, (unsigned long long)h2,
                   (unsigned long long)h3, (unsigned long long)h4);
        } else if (!strcmp(cmd, "fir")) {
            int16_t h[3] = {16384, 8192, 8192}, x[3] = {32767, -32768, 1000};
            int16_t hs[2] = {32767, 32767}, xs[2] = {32767, 32767}, xn[2] = {-32768, -32768};
            printf("fir %d %d %d\n", fir_q15(h, x, 3), fir_q15(hs, xs, 2), fir_q15(hs, xn, 2));
            enum { N = 100000, T = 31 };
            int16_t *sig = malloc(N * sizeof *sig), taps[T];
            for (int k = 0; k < T; k++) taps[k] = (int16_t)(1057 + (k < 16 ? k : 30 - k) * 37);
            for (int i = 0; i < N; i++) sig[i] = (int16_t)((int32_t)(rnd() % 65536) - 32768);
            uint64_t hh = 1469598103934665603ull; int32_t mx = -40000;
            for (int i = 0; i + T <= N; i++) { int16_t y = fir_q15(taps, sig + i, T); MIX(hh, y); if (y > mx) mx = y; }
            printf("stream %016llx max %d\n", (unsigned long long)hh, mx);
            free(sig);
        } else if (!strcmp(cmd, "ema")) {
            int16_t y = 0;
            for (int i = 0; i < 8; i++) { y = ema_q15(y, 32767, 8192); printf("%d ", y); }
            printf("\n%d %d %d\n", ema_q15(-32768, 32767, 32767), ema_q15(32767, -32768, 32767), ema_q15(100, -100, 16384));
            uint64_t hh = 1469598103934665603ull; y = 0;
            for (int i = 0; i < 200000; i++) { y = ema_q15(y, (int16_t)rnd(), (int16_t)(rnd() & 0x7FFF)); MIX(hh, y); }
            printf("ema %016llx\n", (unsigned long long)hh);
        }
    }
    return 0;
}
```

## Tests
=== sample
basic
---
add 163840 2147483647 -2147483648
mul -221184 1 0 2147483647 -2147483648
div 21845 -21845 1 -1 2147483647 2147483647
sqrt 131072 92681 256 0 11863283
=== hidden
fuzz
---
add 7447a6d061d0a405
mul 448a58d98597fc41
div ce3000ac4eaaed70
sqrt 90e715020b9ba511
=== hidden
fir
---
fir 8442 32767 -32768
stream ebdc46c9a1d4b622 max 17477
=== hidden
ema
---
8192 14336 18944 22400 24992 26936 28394 29487 
32765 -32766 0
ema c73a4d174b0cdae2

## Hints
- Do every intermediate step in `int64_t`. Q16 × Q16 fits in 64 bits, and `INT32_MIN · 2¹⁶` fits too.
- Write a `sat32(int64_t)` helper and use it everywhere.
- For `q16_div`, build the 64-bit numerator `n = (int64_t)a * 65536`. If `n` and `b` have the same sign, add `|b|/2` to `n`'s magnitude, otherwise subtract. Then divide (C truncates toward zero). Or compute `q = n / b`, `r = n % b`, and round up the magnitude when `2·|r| >= |b|`.
- `q16_sqrt`: integer square root of `(uint64_t)a << 16`, by Newton's method or the bit-by-bit method, then check `r*r <= v < (r+1)*(r+1)`.

## Solution
```c
#include <stdint.h>
typedef int32_t q16_t;

static int32_t sat32(int64_t v) { return v > INT32_MAX ? INT32_MAX : v < INT32_MIN ? INT32_MIN : (int32_t)v; }
static int16_t sat16(int64_t v) { return v > INT16_MAX ? INT16_MAX : v < INT16_MIN ? INT16_MIN : (int16_t)v; }

q16_t q16_add_sat(q16_t a, q16_t b) { return sat32((int64_t)a + b); }

q16_t q16_mul(q16_t a, q16_t b) {
    int64_t p = (int64_t)a * b;                 /* |p| <= 2^62: exact */
    return sat32((p + (1LL << 15)) >> 16);      /* round half up, arithmetic shift = floor */
}

q16_t q16_div(q16_t a, q16_t b) {
    if (b == 0) return a >= 0 ? INT32_MAX : INT32_MIN;
    int64_t n = (int64_t)a * 65536, d = b;
    int64_t q = n / d, r = n % d;               /* truncated toward zero */
    int64_t ar = r < 0 ? -r : r, ad = d < 0 ? -d : d;
    if (2 * ar >= ad) q += ((n < 0) == (d < 0)) ? 1 : -1;     /* ties away from zero */
    return sat32(q);
}

q16_t q16_sqrt(q16_t a) {
    if (a <= 0) return 0;
    uint64_t v = (uint64_t)a << 16, res = 0, bit = 1ULL << 62;
    while (bit > v) bit >>= 2;
    while (bit) {                                /* bit-by-bit: exact floor(sqrt(v)) */
        if (v >= res + bit) { v -= res + bit; res = (res >> 1) + bit; }
        else res >>= 1;
        bit >>= 2;
    }
    return (q16_t)res;
}

int16_t fir_q15(const int16_t *h, const int16_t *x, int n) {
    int64_t acc = 0;                             /* Q30 sum with plenty of headroom */
    for (int k = 0; k < n; k++) acc += (int32_t)h[k] * x[k];
    return sat16((acc + (1 << 14)) >> 15);       /* round once at the end */
}

int16_t ema_q15(int16_t prev, int16_t sample, int16_t alpha) {
    int32_t d = (int32_t)sample - prev;          /* can reach ±65535: needs 32 bits */
    int64_t step = ((int64_t)alpha * d + (1 << 14)) >> 15;
    return sat16((int64_t)prev + step);
}
```

- **Widen first.** `a * b` in 32 bits overflows (UB) for almost every input. `(int64_t)a * b` is exact, because |a·b| ≤ 2⁶².
- **Rounding** with `+ half, >> k` gives round-half-up. Truncating instead biases every result downward by ½ LSB on average, and the bias accumulates in filters and integrators.
- **Division** rounds on the remainder, so ties are handled symmetrically for every sign combination. `INT32_MIN / -1` overflows int32, but the 64-bit computation and the final saturation make it well defined.
- **Integer sqrt** with the bit-by-bit method needs no division and runs in 32 iterations with a constant cost: ideal on an MCU.
- **The FIR** keeps all 31 products exact in a 64-bit accumulator and rounds once. The starter rounds each tap (error grows with N), and its 32-bit sum overflows.
- **EMA**: `sample − prev` spans ±65535, which doesn't fit in Q15, so the difference needs 32 bits. Saturation catches the final overshoot.
