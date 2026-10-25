---
id: py-bit-tricks-suite
title: "Bit Tricks: Single Number III-ways, Bit Counts, Reverse Bits, Letter Masks"
difficulty: Hard
order: 1
tags: bit manipulation, XOR, bitmasks, fixed-width emulation
time_limit: 3
---
## Statement
```python
def single_among_triples(nums):
    """Every value appears exactly three times except one, which appears once. Values may be NEGATIVE
    32-bit ints. O(n) time, O(1) extra space (no Counter)."""

def bit_counts(n):
    """List of popcounts of 0..n, computed in O(n) with a DP on bits."""

def reverse_bits32(x):
    """Reverse the bits of an unsigned 32-bit integer."""

def max_disjoint_product(words):
    """Max len(a) * len(b) over pairs of words sharing no letter (lowercase). 0 if none. Use 26-bit masks."""
```

Test lines are `(function_name, args)` literals or `gen NAME SEED N`.

## Starter
```python
from collections import Counter

def single_among_triples(nums):
    return next(v for v, c in Counter(nums).items() if c == 1)

def bit_counts(n):
    return [bin(i).count("1") for i in range(n + 1)]

def reverse_bits32(x):
    return int(bin(x)[2:][::-1], 2)

def max_disjoint_product(words):
    best = 0
    for i, a in enumerate(words):
        for b in words[i + 1:]:
            if not set(a) & set(b):
                best = max(best, len(a) * len(b))
    return best
```

## Driver
```python
import ast
import random
import sys

FUNCS = {f.__name__: f for f in (single_among_triples, bit_counts, reverse_bits32, max_disjoint_product)}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        if name == "single_among_triples":
            vals = [rng.randrange(-2**31, 2**31) for _ in range(n)]
            nums = vals * 3 + [-123456789]
            rng.shuffle(nums)
            print(name, n, single_among_triples(nums))
        elif name == "bit_counts":
            r = bit_counts(n)
            print(name, n, sum(r), r[-5:])
        elif name == "reverse_bits32":
            xs = [rng.randrange(2**32) for _ in range(n)]
            print(name, n, sum(reverse_bits32(x) for x in xs) % 1000003)
        else:
            ws = ["".join(rng.choice("abcdefghijklmnopqrstuvwxyz"[:14]) for _ in range(rng.randrange(1, 12))) for _ in range(n)]
            print(name, n, max_disjoint_product(ws))
        continue
    name, args = ast.literal_eval(line)
    print(name, "->", FUNCS[name](*args))
```

## Tests
=== sample
("single_among_triples", ([2, 2, 3, 2],))
("bit_counts", (5,))
("reverse_bits32", (43261596,))
("max_disjoint_product", (["abcw", "baz", "foo", "bar", "xtfn", "abcdef"],))
---
single_among_triples -> 3
bit_counts -> [0, 1, 1, 2, 1, 2]
reverse_bits32 -> 964176192
max_disjoint_product -> 16
=== hidden
("single_among_triples", ([0, 1, 0, 1, 0, 1, 99],))
("single_among_triples", ([-2, -2, 1, 1, 4, 1, 4, 4, -4, -2],))
("single_among_triples", ([-2147483648],))
("bit_counts", (0,))
("bit_counts", (16,))
("reverse_bits32", (0,))
("reverse_bits32", (1,))
("reverse_bits32", (4294967295,))
("reverse_bits32", (4294967293,))
("max_disjoint_product", (["a", "aa", "aaa", "aaaa"],))
("max_disjoint_product", ([],))
---
single_among_triples -> 99
single_among_triples -> -4
single_among_triples -> -2147483648
bit_counts -> [0]
bit_counts -> [0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4, 1]
reverse_bits32 -> 0
reverse_bits32 -> 2147483648
reverse_bits32 -> 4294967295
reverse_bits32 -> 3221225471
max_disjoint_product -> 0
max_disjoint_product -> 0
=== hidden
gen single_among_triples 1 100000
gen bit_counts 2 1000000
---
single_among_triples 100000 -123456789
bit_counts 1000000 9884999 [10, 11, 11, 12, 7]
=== hidden
gen reverse_bits32 3 200000
gen max_disjoint_product 4 3000
---
reverse_bits32 200000 101704
max_disjoint_product 3000 121

## Hints
- **Triples**: for each of the 32 bit positions, count the set bits mod 3. The leftover bits form the answer's 32-bit pattern. Convert it to signed: `if x >= 2**31: x -= 2**32`. (The `ones`/`twos` state machine also works: `ones = (ones ^ v) & ~twos; twos = (twos ^ v) & ~ones`, masked to 32 bits.)
- **bit_counts**: `bits[i] = bits[i >> 1] + (i & 1)`.
- **reverse_bits32**: swap halves, then bytes, nibbles, pairs and single bits with masks (`0x55555555`, …). Remember `bin(x)` drops leading zeros!
- **Letter masks**: precompute a mask per word, keeping only the longest word per mask (duplicates share masks). Then test pairs with `m1 & m2 == 0`.

## Solution
```python
def single_among_triples(nums):
    ones = twos = 0
    M = 0xFFFFFFFF
    for v in nums:
        v &= M                                    # 32-bit two's complement pattern
        ones = (ones ^ v) & ~twos & M
        twos = (twos ^ v) & ~ones & M
    return ones - (1 << 32) if ones >> 31 else ones

def bit_counts(n):
    bits = [0] * (n + 1)
    for i in range(1, n + 1):
        bits[i] = bits[i >> 1] + (i & 1)
    return bits

def reverse_bits32(x):
    x = ((x >> 1) & 0x55555555) | ((x & 0x55555555) << 1)
    x = ((x >> 2) & 0x33333333) | ((x & 0x33333333) << 2)
    x = ((x >> 4) & 0x0F0F0F0F) | ((x & 0x0F0F0F0F) << 4)
    x = ((x >> 8) & 0x00FF00FF) | ((x & 0x00FF00FF) << 8)
    return ((x >> 16) | (x << 16)) & 0xFFFFFFFF

def max_disjoint_product(words):
    best_len = {}
    for w in words:
        m = 0
        for ch in w:
            m |= 1 << (ord(ch) - 97)
        if len(w) > best_len.get(m, 0):
            best_len[m] = len(w)
    items = list(best_len.items())
    best = 0
    for i, (m1, l1) in enumerate(items):
        for m2, l2 in items[i + 1:]:
            if not m1 & m2 and l1 * l2 > best:
                best = l1 * l2
    return best
```

- **The triples state machine** counts each bit modulo 3 in two variables: a bit sits in `ones` after 1 occurrence, in `twos` after 2, and in neither after 3. Python ints are unbounded, so values are first masked to their 32-bit pattern, and the result's sign is restored at the end. Forgetting this is the classic Python bug with negative inputs.
- **bit_counts**: `i >> 1` drops the last bit, so its popcount is already known. That's O(1) per number.
- **reverse_bits32** swaps groups of 1, 2, 4, 8 and 16 bits in five mask steps, the same divide-and-conquer as the SWAR popcount. A string-based reversal fails because `bin()` drops leading zeros.
- **Letter masks** turn "do these words share a letter?" into one AND. Deduplicating by mask (keeping the longest word) shrinks the pair loop, since there are at most 2¹⁴ distinct masks over the 14-letter alphabet used in the stress test.
