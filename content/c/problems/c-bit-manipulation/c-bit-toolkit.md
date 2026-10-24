---
id: c-bit-toolkit
title: Bit-Twiddling Toolkit (UB-Free)
difficulty: Medium
order: 1
tags: bit manipulation, masks, shifts, undefined behaviour, Gray code
---
## Statement
Implement a small, **undefined-behaviour-free** bit library. The edge cases are the point: shift counts of 0 and 32, full-width fields, and zero inputs. On x86, `1u << 32` silently evaluates to `1` (the CPU masks the count), so the obvious one-liners give wrong answers exactly at the boundaries.

```c
unsigned popcount32(uint32_t x);                   /* number of set bits */
uint32_t reverse_bits32(uint32_t x);               /* bit 0 <-> bit 31, bit 1 <-> bit 30, ... */
uint32_t rotl32(uint32_t x, unsigned k);           /* rotate left by k mod 32 (any k, including 0 and 32) */
uint32_t next_pow2(uint32_t x);                    /* smallest power of two >= x; next_pow2(0) = 1; 0 if none fits */
int lowest_set_index(uint32_t x);                  /* index of the lowest set bit, -1 if x == 0 */
uint32_t gray_encode(uint32_t x);                  /* binary-reflected Gray code */
uint32_t gray_decode(uint32_t g);                  /* inverse of gray_encode */
uint32_t field_get(uint32_t reg, unsigned shift, unsigned width);              /* 1 <= width <= 32, shift + width <= 32 */
uint32_t field_set(uint32_t reg, unsigned shift, unsigned width, uint32_t v);  /* v truncated to width bits */
```

Write them with portable C. Compiler built-ins are allowed, but make sure you handle the inputs where they're undefined (`__builtin_ctz(0)`).

The driver accepts one-off calls (`popcount 0xF0`, `field_set 0xFFFFFFFF 4 3 5`, …) and `fuzz SEED N`, which compares every function against a slow bit-by-bit reference on N random inputs, edge values included.

## Starter
```c
#include <stdint.h>

unsigned popcount32(uint32_t x) { unsigned c = 0; while (x) { c += x & 1u; x >>= 1; } return c; }
uint32_t reverse_bits32(uint32_t x) { return x; }
uint32_t rotl32(uint32_t x, unsigned k) { return (x << k) | (x >> (32 - k)); }
uint32_t next_pow2(uint32_t x) { uint32_t p = 1; while (p < x) p <<= 1; return p; }
int lowest_set_index(uint32_t x) { return __builtin_ctz(x); }
uint32_t gray_encode(uint32_t x) { return x ^ (x >> 1); }
uint32_t gray_decode(uint32_t g) { return g ^ (g >> 1); }
uint32_t field_get(uint32_t reg, unsigned shift, unsigned width) {
    return (reg >> shift) & ((1u << width) - 1);
}
uint32_t field_set(uint32_t reg, unsigned shift, unsigned width, uint32_t v) {
    uint32_t mask = ((1u << width) - 1) << shift;
    return (reg & ~mask) | (v << shift);
}
```

## Driver
```c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

static unsigned long long drv_st;
static uint32_t drv_rnd(void) {
    drv_st = drv_st * 6364136223846793005ULL + 1442695040888963407ULL;
    return (uint32_t)(drv_st >> 32);
}
static uint32_t drv_bit(uint32_t x, unsigned i) { return (x >> i) & 1u; }
static unsigned r_pop(uint32_t x) { unsigned c = 0; for (unsigned i = 0; i < 32; i++) c += drv_bit(x, i); return c; }
static uint32_t r_rev(uint32_t x) { uint32_t r = 0; for (unsigned i = 0; i < 32; i++) r |= drv_bit(x, i) << (31 - i); return r; }
static uint32_t r_rotl(uint32_t x, unsigned k) { uint32_t r = 0; for (unsigned i = 0; i < 32; i++) r |= drv_bit(x, i) << ((i + k) % 32); return r; }
static uint32_t r_np2(uint32_t x) { for (unsigned i = 0; i < 32; i++) if ((1ull << i) >= x) return (uint32_t)(1ull << i); return 0; }
static int r_low(uint32_t x) { for (unsigned i = 0; i < 32; i++) if (drv_bit(x, i)) return (int)i; return -1; }
static uint32_t r_genc(uint32_t x) { return x ^ (x >> 1); }
static uint32_t r_gdec(uint32_t g) { uint32_t b = 0, prev = 0; for (int i = 31; i >= 0; i--) { prev ^= drv_bit(g, (unsigned)i); b |= prev << i; } return b; }
static uint32_t r_fget(uint32_t reg, unsigned s, unsigned w) { uint32_t r = 0; for (unsigned i = 0; i < w; i++) r |= drv_bit(reg, s + i) << i; return r; }
static uint32_t r_fset(uint32_t reg, unsigned s, unsigned w, uint32_t v) {
    for (unsigned i = 0; i < w; i++) { reg &= ~(1u << (s + i)); reg |= drv_bit(v, i) << (s + i); }
    return reg;
}
static uint32_t drv_edge(void) {
    static const uint32_t e[] = {0, 1, 2, 3, 0x80000000u, 0x80000001u, 0x7FFFFFFFu, 0xFFFFFFFFu, 0xFFFFFFFEu, 0x40000000u, 0x40000001u, 0x55555555u};
    unsigned r = drv_rnd();
    if (r % 4 == 0) return e[(r >> 8) % (sizeof e / sizeof e[0])];
    if (r % 4 == 1) return 1u << (drv_rnd() % 32);
    return drv_rnd();
}

int main(void) {
    char cmd[32];
    while (scanf("%31s", cmd) == 1) {
        unsigned long a, b, c, d;
        if (!strcmp(cmd, "fuzz")) {
            unsigned long long seed; unsigned n;
            if (scanf("%llu %u", &seed, &n) != 2) return 1;
            drv_st = seed;
            const char *fail = NULL; uint32_t fx = 0; unsigned fs = 0, fw = 0;
            for (unsigned t = 0; t < n && !fail; t++) {
                uint32_t x = drv_edge(), y = drv_edge();
                unsigned k = drv_rnd() % 70, w = 1 + drv_rnd() % 32, s = drv_rnd() % (33 - w);
                if (t % 7 == 0) { w = 32; s = 0; }
                if (t % 11 == 0) k = 32 * (drv_rnd() % 3);
                fx = x; fs = s; fw = w;
                if (popcount32(x) != r_pop(x)) fail = "popcount32";
                else if (reverse_bits32(x) != r_rev(x)) fail = "reverse_bits32";
                else if (rotl32(x, k) != r_rotl(x, k)) { fail = "rotl32"; fs = k; }
                else if (next_pow2(x) != r_np2(x)) fail = "next_pow2";
                else if (lowest_set_index(x) != r_low(x)) fail = "lowest_set_index";
                else if (gray_encode(x) != r_genc(x)) fail = "gray_encode";
                else if (gray_decode(x) != r_gdec(x)) fail = "gray_decode";
                else if (field_get(x, s, w) != r_fget(x, s, w)) fail = "field_get";
                else if (field_set(x, s, w, y) != r_fset(x, s, w, y)) fail = "field_set";
            }
            if (fail) printf("fuzz: %s WRONG for x=0x%08X (shift/k=%u width=%u)\n", fail, (unsigned)fx, fs, fw);
            else printf("fuzz %u: all functions ok\n", n);
        } else if (!strcmp(cmd, "popcount") && scanf("%lx", &a) == 1) printf("popcount 0x%lX = %u\n", a, popcount32((uint32_t)a));
        else if (!strcmp(cmd, "reverse") && scanf("%lx", &a) == 1) printf("reverse 0x%lX = 0x%08X\n", a, (unsigned)reverse_bits32((uint32_t)a));
        else if (!strcmp(cmd, "rotl") && scanf("%lx %lu", &a, &b) == 2) printf("rotl 0x%lX %lu = 0x%08X\n", a, b, (unsigned)rotl32((uint32_t)a, (unsigned)b));
        else if (!strcmp(cmd, "next_pow2") && scanf("%lx", &a) == 1) printf("next_pow2 0x%lX = 0x%X\n", a, (unsigned)next_pow2((uint32_t)a));
        else if (!strcmp(cmd, "lowest") && scanf("%lx", &a) == 1) printf("lowest 0x%lX = %d\n", a, lowest_set_index((uint32_t)a));
        else if (!strcmp(cmd, "gray") && scanf("%lx", &a) == 1) printf("gray 0x%lX = 0x%X, decoded back = 0x%X\n", a, (unsigned)gray_encode((uint32_t)a), (unsigned)gray_decode(gray_encode((uint32_t)a)));
        else if (!strcmp(cmd, "field_get") && scanf("%lx %lu %lu", &a, &b, &c) == 3) printf("field_get 0x%lX %lu %lu = 0x%X\n", a, b, c, (unsigned)field_get((uint32_t)a, (unsigned)b, (unsigned)c));
        else if (!strcmp(cmd, "field_set") && scanf("%lx %lu %lu %lx", &a, &b, &c, &d) == 4) printf("field_set 0x%lX %lu %lu 0x%lX = 0x%08X\n", a, b, c, d, (unsigned)field_set((uint32_t)a, (unsigned)b, (unsigned)c, (uint32_t)d));
    }
    return 0;
}
```

## Tests
=== sample
popcount F0F0
reverse 1
rotl 80000001 1
next_pow2 11
lowest 28
gray 6
field_get ABCD1234 8 8
field_set FFFFFFFF 4 3 5
---
popcount 0xF0F0 = 8
reverse 0x1 = 0x80000000
rotl 0x80000001 1 = 0x00000003
next_pow2 0x11 = 0x20
lowest 0x28 = 3
gray 0x6 = 0x5, decoded back = 0x6
field_get 0xABCD1234 8 8 = 0x12
field_set 0xFFFFFFFF 4 3 0x5 = 0xFFFFFFDF
=== hidden
popcount 0
popcount FFFFFFFF
reverse 80000000
reverse 12345678
rotl DEADBEEF 0
rotl DEADBEEF 32
rotl DEADBEEF 36
next_pow2 0
next_pow2 1
next_pow2 80000000
next_pow2 80000001
lowest 0
lowest 80000000
gray FFFFFFFF
field_get DEADBEEF 0 32
field_set 12345678 0 32 CAFEBABE
field_set 0 28 4 FF
---
popcount 0x0 = 0
popcount 0xFFFFFFFF = 32
reverse 0x80000000 = 0x00000001
reverse 0x12345678 = 0x1E6A2C48
rotl 0xDEADBEEF 0 = 0xDEADBEEF
rotl 0xDEADBEEF 32 = 0xDEADBEEF
rotl 0xDEADBEEF 36 = 0xEADBEEFD
next_pow2 0x0 = 0x1
next_pow2 0x1 = 0x1
next_pow2 0x80000000 = 0x80000000
next_pow2 0x80000001 = 0x0
lowest 0x0 = -1
lowest 0x80000000 = 31
gray 0xFFFFFFFF = 0x80000000, decoded back = 0xFFFFFFFF
field_get 0xDEADBEEF 0 32 = 0xDEADBEEF
field_set 0x12345678 0 32 0xCAFEBABE = 0xCAFEBABE
field_set 0x0 28 4 0xFF = 0xF0000000
=== hidden
fuzz 1 200000
fuzz 99 200000
---
fuzz 200000: all functions ok
fuzz 200000: all functions ok

## Hints
- **rotl**: reduce `k &= 31` first; then `k == 0` must return `x` (otherwise `x >> 32` is UB). The idiom `(x << k) | (x >> (-k & 31))` works for every k without a branch.
- **Masks of width w**: `w == 32 ? 0xFFFFFFFFu : (1u << w) - 1u`. Or the trick `0xFFFFFFFFu >> (32 - w)`, which is valid for 1 ≤ w ≤ 32.
- **field_set**: mask `v` too (`(v << shift) & mask`) so oversized values don't spill into neighbouring fields.
- **next_pow2**: return 0 if `x > 0x80000000`. Otherwise smear the bits: `x--; x |= x >> 1; x |= x >> 2; … x |= x >> 16; x++`, with `x == 0` handled separately.
- **gray_decode**: the prefix XOR of all higher bits, `g ^= g >> 1; g ^= g >> 2; g ^= g >> 4; g ^= g >> 8; g ^= g >> 16;`.

## Solution
```c
#include <stdint.h>

unsigned popcount32(uint32_t x) {                       /* SWAR: no loop, no built-in needed */
    x = x - ((x >> 1) & 0x55555555u);
    x = (x & 0x33333333u) + ((x >> 2) & 0x33333333u);
    x = (x + (x >> 4)) & 0x0F0F0F0Fu;
    return (x * 0x01010101u) >> 24;
}

uint32_t reverse_bits32(uint32_t x) {
    x = ((x >> 1) & 0x55555555u) | ((x & 0x55555555u) << 1);
    x = ((x >> 2) & 0x33333333u) | ((x & 0x33333333u) << 2);
    x = ((x >> 4) & 0x0F0F0F0Fu) | ((x & 0x0F0F0F0Fu) << 4);
    x = ((x >> 8) & 0x00FF00FFu) | ((x & 0x00FF00FFu) << 8);
    return (x >> 16) | (x << 16);
}

uint32_t rotl32(uint32_t x, unsigned k) {
    k &= 31u;
    return (x << k) | (x >> (-k & 31u));                 /* k == 0: x | x, no shift by 32 */
}

uint32_t next_pow2(uint32_t x) {
    if (x <= 1) return 1;
    if (x > 0x80000000u) return 0;
    x--;
    x |= x >> 1; x |= x >> 2; x |= x >> 4; x |= x >> 8; x |= x >> 16;
    return x + 1;
}

int lowest_set_index(uint32_t x) {
    return x ? __builtin_ctz(x) : -1;
}

uint32_t gray_encode(uint32_t x) { return x ^ (x >> 1); }

uint32_t gray_decode(uint32_t g) {
    g ^= g >> 1; g ^= g >> 2; g ^= g >> 4; g ^= g >> 8; g ^= g >> 16;
    return g;
}

static uint32_t low_mask(unsigned width) {               /* 1 <= width <= 32 */
    return 0xFFFFFFFFu >> (32u - width);
}

uint32_t field_get(uint32_t reg, unsigned shift, unsigned width) {
    return (reg >> shift) & low_mask(width);
}

uint32_t field_set(uint32_t reg, unsigned shift, unsigned width, uint32_t v) {
    uint32_t mask = low_mask(width) << shift;
    return (reg & ~mask) | ((v << shift) & mask);
}
```

Every function is branch-light and stays inside the C standard's rules:
- **Shift counts** never reach 32. `rotl32` uses `-k & 31`, which is 0 when k is 0, and `low_mask` shifts right by `32 - width`, which is at most 31.
- **`__builtin_ctz`** is called only for non-zero input.
- **SWAR popcount and bit reversal** work on all 32 bits in parallel in O(log w) steps. Compilers recognise the rotate idiom and emit a single `ROL`/`ROR` instruction.
- **Gray code decoding** is a prefix XOR: binary bit i is the XOR of Gray bits i…31, computed by doubling the shift. That's the same parallel-prefix structure as the popcount.
