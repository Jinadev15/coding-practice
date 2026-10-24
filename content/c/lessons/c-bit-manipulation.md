# Bit Manipulation

At the hardware level everything is bits. Device registers pack a dozen flags into one 32-bit word, network protocols pack fields into headers, compression and cryptography operate on bit streams, and chess engines and robot occupancy grids store whole boards as bitsets. C gives you direct, portable access through six operators. Using them correctly requires knowing the integer rules: which shifts are undefined, why you should use unsigned types, and how to stay portable across endianness.

## 1. The operators

| Operator | Name | Example (8-bit) |
|---|---|---|
| `&` | AND | `1100 & 1010 = 1000` |
| `\|` | OR | `1100 \| 1010 = 1110` |
| `^` | XOR | `1100 ^ 1010 = 0110` |
| `~` | NOT (complement) | `~1100 = 0011` (upper bits flipped too!) |
| `<<` | left shift | `0011 << 2 = 1100` |
| `>>` | right shift | `1100 >> 2 = 0011` |

> [!DANGER]
> Shift rules, from the C standard:
> - Shifting by a count `< 0` or `>= the width` of the (promoted) type is **undefined**: `1u << 32` on a 32-bit `unsigned` is UB. x86 masks the count to 5 bits, giving 1, while ARM gives 0.
> - Left-shifting a **negative** signed value, or shifting a 1 into or past the sign bit (`1 << 31` with 32-bit `int`), is UB (before C23's two's-complement guarantee, and still UB for overflow).
> - Right-shifting a negative signed value is **implementation-defined**: usually arithmetic (sign-extending), but not guaranteed.
>
> **Rule:** do bit manipulation on **unsigned** types (`uint32_t`, `uint64_t`), and write `1u << n` or `UINT64_C(1) << n`, never `1 << n`.

> [!WARNING]
> Integer promotion: `uint8_t x = 0x0F; ~x` is computed as an `int`, giving `0xFFFFFFF0`, not `0xF0`. Mask or cast back: `(uint8_t)~x`. Likewise `x << 4` on a `uint8_t` yields an `int` that can exceed 255.

## 2. The four single-bit idioms

```c
#include <stdint.h>
#include <stdbool.h>

static inline uint32_t bit_set(uint32_t x, unsigned n)    { return x |  (1u << n); }
static inline uint32_t bit_clear(uint32_t x, unsigned n)  { return x & ~(1u << n); }
static inline uint32_t bit_toggle(uint32_t x, unsigned n) { return x ^  (1u << n); }
static inline bool     bit_test(uint32_t x, unsigned n)   { return (x >> n) & 1u; }

/* set bit n to value v (0 or 1) without branching */
static inline uint32_t bit_assign(uint32_t x, unsigned n, unsigned v) {
    return (x & ~(1u << n)) | ((uint32_t)(v & 1u) << n);
}
```

## 3. Multi-bit fields: the register pattern

A peripheral's control register might pack `MODE` into bits 4–6 and `EN` into bit 0:

```c
#define CTRL_EN         (1u << 0)
#define CTRL_MODE_SHIFT 4u
#define CTRL_MODE_MASK  (0x7u << CTRL_MODE_SHIFT)        /* 3 bits: 0b0111_0000 */

static inline uint32_t field_get(uint32_t reg, uint32_t mask, unsigned shift) {
    return (reg & mask) >> shift;
}
static inline uint32_t field_set(uint32_t reg, uint32_t mask, unsigned shift, uint32_t v) {
    return (reg & ~mask) | ((v << shift) & mask);          /* & mask keeps oversized v from spilling */
}

uint32_t ctrl = 0;
ctrl = field_set(ctrl, CTRL_MODE_MASK, CTRL_MODE_SHIFT, 5);   /* MODE = 5 */
ctrl |= CTRL_EN;
```

This **read–modify–write** is how every embedded HAL works (Embedded module). A mask of `w` bits starting at `s` is `((1u << w) - 1) << s`. Watch out for `w == 32`: `1u << 32` is UB, so handle the full width separately (`~0u`).

## 4. Tricks with `x & (x - 1)` and `x & -x`

Subtracting 1 flips the lowest set bit and every zero below it. That gives a family of O(1) tricks:

| Expression | Result | Example `x = 0b1011_0100` |
|---|---|---|
| `x & (x - 1)` | clear the lowest set bit | `1011_0000` |
| `x & -x` (unsigned) | isolate the lowest set bit | `0000_0100` |
| `x \| (x - 1)` | set all bits below the lowest set bit | `1011_0111` |
| `x && !(x & (x - 1))` | is `x` a power of two? | false |
| `~x & (x + 1)` | isolate the lowest **clear** bit | `0000_0001` |

```c
/* Kernighan's popcount: one iteration per SET bit */
unsigned popcount_k(uint32_t x) {
    unsigned c = 0;
    while (x) { x &= x - 1; c++; }
    return c;
}

/* iterate over the set bits of a mask (e.g. the active sensors) */
for (uint32_t m = mask; m; m &= m - 1) {
    unsigned i = (unsigned)__builtin_ctz(m);      /* index of the lowest set bit */
    handle_sensor(i);
}
```

## 5. Built-ins and C23 `<stdbit.h>`

Compilers map these to single instructions (`POPCNT`, `TZCNT`/`BSF`, `LZCNT`/`BSR` on x86; `CLZ` and `RBIT` on ARM):

| GCC/Clang built-in | C23 `<stdbit.h>` | Meaning | Undefined for |
|---|---|---|---|
| `__builtin_popcount(x)` | `stdc_count_ones(x)` | number of 1 bits | — |
| `__builtin_ctz(x)` | `stdc_trailing_zeros(x)` | trailing zeros | **x == 0** (built-in) |
| `__builtin_clz(x)` | `stdc_leading_zeros(x)` | leading zeros | **x == 0** (built-in) |
| `__builtin_parity(x)` | — | popcount mod 2 | — |
| `__builtin_bswap32(x)` | — | reverse the byte order | — |
| — | `stdc_bit_width(x)` | bits needed: `⌊log₂x⌋ + 1` | — |
| — | `stdc_has_single_bit(x)` | power of two? | — |
| — | `stdc_bit_ceil(x)` | next power of two ≥ x | — |

The `ll` suffix variants (`__builtin_popcountll`) take 64-bit values. ⌊log₂ x⌋ for `x > 0` is `31 - __builtin_clz(x)`. Remember the x == 0 trap: the built-ins are UB there, while the C23 functions define the result (the width).

### Portable popcount without built-ins (SWAR)

```c
unsigned popcount32(uint32_t x) {
    x = x - ((x >> 1) & 0x55555555u);                  /* 2-bit sums */
    x = (x & 0x33333333u) + ((x >> 2) & 0x33333333u);  /* 4-bit sums */
    x = (x + (x >> 4)) & 0x0F0F0F0Fu;                  /* 8-bit sums */
    return (x * 0x01010101u) >> 24;                    /* add the four bytes */
}
```

## 6. XOR's algebra

XOR is addition without carry (addition in GF(2)): `x ^ x = 0`, `x ^ 0 = x`, and it's commutative, associative and its own inverse.

- **Find the unique element** when every other appears twice: XOR everything, and the pairs cancel.
- **Swap without a temporary**: `a ^= b; b ^= a; a ^= b;`. It's a party trick: it fails when `a` and `b` alias the same object (the result is 0) and is slower than a temporary on modern CPUs.
- **Parity, checksums, RAID-5 parity, Gray codes**: `g = x ^ (x >> 1)` gives a code where consecutive values differ in one bit. Rotary encoders use it, so a misread during a transition is off by at most one step.
- **Toggle a set of flags**: `flags ^= mask`.

## 7. Bitsets: compact boolean arrays

```c
#include <limits.h>
#define WORD_BITS (sizeof(uint64_t) * CHAR_BIT)
#define WORDS(n)  (((n) + WORD_BITS - 1) / WORD_BITS)

typedef struct { size_t n; uint64_t *w; } Bitset;

static inline void bs_set(Bitset *b, size_t i)   { b->w[i / WORD_BITS] |=  (UINT64_C(1) << (i % WORD_BITS)); }
static inline void bs_clear(Bitset *b, size_t i) { b->w[i / WORD_BITS] &= ~(UINT64_C(1) << (i % WORD_BITS)); }
static inline bool bs_test(const Bitset *b, size_t i) { return (b->w[i / WORD_BITS] >> (i % WORD_BITS)) & 1u; }
```

A bitset uses 64× less memory than `bool[]`, and set operations (union, intersection, difference) work 64 elements per instruction: `a[i] | b[i]`, `a[i] & b[i]`, `a[i] & ~b[i]`. Uses include the sieve of Eratosthenes, occupancy grids, visited sets in BFS over huge state spaces, and Bloom filters.

## 8. Endianness and byte order

**Endianness** is the order in which a multi-byte integer's bytes are stored in memory. `0x11223344` is stored as `44 33 22 11` on **little-endian** machines (x86, almost all ARM configurations) and as `11 22 33 44` on **big-endian** ones (network byte order, some DSPs, older PowerPC).

```c
/* PORTABLE: assemble from bytes with shifts. Correct on every host, regardless of its endianness. */
static inline uint32_t load_be32(const uint8_t *p) {
    return (uint32_t)p[0] << 24 | (uint32_t)p[1] << 16 | (uint32_t)p[2] << 8 | p[3];
}
static inline void store_le16(uint8_t *p, uint16_t v) {
    p[0] = (uint8_t)v;
    p[1] = (uint8_t)(v >> 8);
}

/* NON-PORTABLE: depends on host endianness AND violates alignment/strict aliasing */
uint32_t bad = *(uint32_t *)buf;
```

> [!KEY]
> Shifts operate on **values**, not memory layout. `x >> 8` means the same thing on every machine. Only reinterpreting memory (pointer casts, unions, `memcpy` into an integer) exposes endianness. When decoding a wire format or a sensor frame, assemble from bytes with shifts and the code is portable everywhere. `htonl`/`ntohl` (POSIX) do the same job for network order.

## 9. Exam-ready answers

> [!EXAM]
> **Bitwise operators and masks.** C provides the bitwise operators AND (`&`), OR (`|`), XOR (`^`), complement (`~`) and the shifts `<<` and `>>`, which operate on the individual bits of integer operands after the usual arithmetic conversions. A mask is a value whose set bits select the positions of interest: a bit is set with `x | m`, cleared with `x & ~m`, toggled with `x ^ m` and tested with `x & m`, and a multi-bit field is extracted with `(x & m) >> s` and written with `(x & ~m) | ((v << s) & m)`. Bit manipulation should be performed on unsigned types, because shifting into or past the sign bit, shifting negative values left, or shifting by at least the width of the type is undefined behaviour, and right shifts of negative values are implementation-defined.

> [!EXAM]
> **Endianness.** Endianness is the byte ordering used to store multi-byte values in memory: little-endian stores the least significant byte at the lowest address, big-endian the most significant. It matters when binary data is exchanged between systems, such as files, network protocols (which use big-endian network byte order) and device buffers. Portable code serialises and deserialises integers byte by byte with shifts and masks, which depend only on values, rather than by reinterpreting memory.

## 10. Cheat sheet

| Need | Code |
|---|---|
| set / clear / toggle / test bit n | `x \|= 1u<<n` · `x &= ~(1u<<n)` · `x ^= 1u<<n` · `(x>>n)&1u` |
| low `w` bits mask | `(1u << w) - 1` (w < 32) |
| clear the lowest set bit | `x & (x - 1)` |
| lowest set bit | `x & -x` |
| power of two? | `x && !(x & (x - 1))` |
| count bits | `__builtin_popcount` / `stdc_count_ones` |
| index of the lowest set bit | `__builtin_ctz(x)` (x ≠ 0) |
| ⌊log₂ x⌋ | `31 - __builtin_clz(x)` (x ≠ 0) |
| Gray code | `x ^ (x >> 1)` |
| big-endian load | `p[0]<<24 \| p[1]<<16 \| p[2]<<8 \| p[3]` (cast to uint32_t first) |

> [!INTERVIEW]
> **"Reverse the bits of a 32-bit integer."** Swap progressively larger groups: `x = (x >> 1 & 0x55555555) | (x & 0x55555555) << 1;`, then the same with 2-bit groups (`0x33333333`), nibbles (`0x0F0F0F0F`) and bytes (`0x00FF00FF`), then the halves (`x >> 16 | x << 16`). That's 5 steps, O(log w), with no loop. Mention that ARM has a single `RBIT` instruction, and that a 256-entry lookup table is a valid alternative if memory allows.
