# Bit Manipulation

Python integers are arbitrary-precision, and they support the full set of bitwise operators: `&`, `|`, `^`, `~`, `<<` and `>>`. Bits are used to pack flags, represent subsets for bitmask DP, implement fast sets and Bloom filters, compute parities and checksums, decode binary protocols from sensors and CAN buses, and power a family of O(1) tricks that interviewers love. Python's unbounded integers make some things easier (no overflow) and others subtler (`~x` is `-x - 1`, and there's no fixed width unless you mask).

## 1. Operators and Python specifics

| Operation | Expression | Note |
|---|---|---|
| AND / OR / XOR | `a & b`, `a \| b`, `a ^ b` | |
| NOT | `~a` | equals `-a - 1` (infinite two's complement) |
| shift left | `a << k` | multiply by 2ᵏ, never overflows |
| shift right | `a >> k` | **floor** division by 2ᵏ (arithmetic for negatives) |
| test bit k | `a >> k & 1` | |
| set / clear / toggle bit k | `a \| 1 << k`, `a & ~(1 << k)`, `a ^ 1 << k` | |
| count set bits | `a.bit_count()` (3.10+), or `bin(a).count("1")` | |
| number of bits needed | `a.bit_length()` | `⌊log₂ a⌋ + 1` for a > 0 |
| binary string | `bin(a)`, `f"{a:08b}"` | |
| parse | `int("1011", 2)` | |

> [!KEY]
> Python ints have **no fixed width**. To emulate 32-bit unsigned arithmetic, mask with `& 0xFFFFFFFF`. To interpret a 32-bit pattern as signed, use `x - (1 << 32) if x & (1 << 31) else x`. For fixed-size binary data (files, network, sensors), use the `struct` module or `int.from_bytes(b, "little", signed=True)`.

## 2. The essential tricks

| Trick | Expression | Example (x = 0b1011000) |
|---|---|---|
| clear the lowest set bit | `x & (x - 1)` | `0b1010000` |
| isolate the lowest set bit | `x & -x` | `0b0001000` |
| power of two? | `x > 0 and x & (x - 1) == 0` | False |
| index of the lowest set bit | `(x & -x).bit_length() - 1` | 3 |
| all ones below bit k | `(1 << k) - 1` | |
| swap without a temporary | `a ^= b; b ^= a; a ^= b` | (a curiosity; use tuple swap in Python) |
| sign of x | `(x > 0) - (x < 0)` | |
| absolute value of a fixed-width int | `(x ^ m) - m` with `m = x >> 31` | |

```python
def popcount_kernighan(x):          # one iteration per set bit
    c = 0
    while x:
        x &= x - 1
        c += 1
    return c

def iterate_bits(mask):             # yields the indices of the set bits, low to high
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low
```

## 3. XOR patterns

XOR is addition modulo 2 per bit: `x ^ x = 0`, `x ^ 0 = x`, commutative and associative.

```python
from functools import reduce
from operator import xor

def single_number(nums):            # every value appears twice except one
    return reduce(xor, nums, 0)

def missing_number(nums):           # 0..n with one missing
    n = len(nums)
    return reduce(xor, range(n + 1), 0) ^ reduce(xor, nums, 0)

def two_singles(nums):              # every value twice except TWO values
    x = reduce(xor, nums, 0)        # = a ^ b
    low = x & -x                    # a bit where a and b differ
    a = reduce(xor, (v for v in nums if v & low), 0)
    return sorted((a, x ^ a))
```

**Single number when the others appear three times**: count each bit position mod 3, or use the two-variable state machine (`ones`, `twos`). **XOR of a range** 0..n has the closed form `[n, 1, n + 1, 0][n % 4]`. **Prefix XOR** answers subarray XOR queries like prefix sums do.

## 4. Subsets as bitmasks

```python
items = ["lidar", "camera", "imu"]
n = len(items)
for mask in range(1 << n):                          # all 2^n subsets
    subset = [items[i] for i in range(n) if mask >> i & 1]

# submasks of m, in decreasing order (including m, excluding 0)
s = m = 0b1011
while s:
    print(bin(s))
    s = (s - 1) & m

# Gosper's hack: the next mask with the same number of set bits (k-combinations in order)
def next_same_popcount(x):
    c = x & -x
    r = x + c
    return (((r ^ x) >> 2) // c) | r
```

**Meet in the middle** for subset sum with n = 40: enumerate the 2²⁰ sums of each half, sort one, and match by binary search, O(2^(n/2) · n) instead of 2⁴⁰.

## 5. Big integers as bitsets

A Python int is a fast arbitrary-length bitset, with operations running in C over 30-bit digits:

```python
def subset_sums(nums):
    reach = 1                       # bit s = sum s is achievable
    for x in nums:
        reach |= reach << x
    return reach

def sieve_count(n):                 # bytearray sieve: a simple, fast "bitset"
    is_p = bytearray([1]) * (n + 1)
    is_p[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if is_p[i]:
            is_p[i * i::i] = bytes(len(range(i * i, n + 1, i)))
    return sum(is_p)
```

Use bitsets for reachability matrices (row ORs), Bloom filters, and the Bitset DP for subset sums or knapsack feasibility.

## 6. Bits in robotics and protocols

```python
import struct

frame = bytes([0x34, 0x12, 0xFF, 0x7F])
little_u16, big_u16 = struct.unpack("<H", frame[:2])[0], struct.unpack(">H", frame[:2])[0]  # 0x1234, 0x3412
status = frame[2]
fault = bool(status >> 7 & 1)
mode = (status >> 4) & 0b111                      # extract a 3-bit field
value = int.from_bytes(frame[2:4], "little", signed=True)   # 0x7FFF -> 32767

def set_field(reg, shift, width, v):
    mask = ((1 << width) - 1) << shift
    return (reg & ~mask) | ((v << shift) & mask)
```

Gray codes (`g = n ^ (n >> 1)`) appear in rotary encoders, because consecutive values differ in one bit, so a misread during a transition is off by at most one step.

## 7. Exam-ready answers

> [!EXAM]
> **Bitwise operations.** Bitwise operators act on the binary representations of integers: AND, OR and XOR combine corresponding bits; NOT inverts them; and shifts move bits left (multiplying by powers of two) or right (dividing, rounding down). Masks select bits: a bit k is tested with `(x >> k) & 1`, set with `x | (1 << k)`, cleared with `x & ~(1 << k)` and toggled with `x ^ (1 << k)`. Useful identities include `x & (x − 1)`, which clears the lowest set bit, `x & −x`, which isolates it, and `x ^ x = 0`, which lets XOR find unpaired elements. In Python, integers have unbounded precision, so fixed-width behaviour must be emulated by masking, and `~x` equals `−x − 1`.

## 8. Cheat sheet

| Need | Code |
|---|---|
| bit k | `x >> k & 1` |
| set/clear/toggle | `x \| 1<<k`, `x & ~(1<<k)`, `x ^ 1<<k` |
| popcount | `x.bit_count()` |
| lowest set bit | `x & -x` |
| power of two | `x and not x & (x - 1)` |
| 32-bit wrap | `& 0xFFFFFFFF` |
| signed from 16 bits | `v - (1 << 16) if v >> 15 else v` |
| bytes ↔ int | `int.from_bytes(b, "big")`, `n.to_bytes(4, "little")` |
| all subsets | `for mask in range(1 << n)` |

> [!INTERVIEW]
> **"Count the bits for every number 0..n in O(n)."** Use DP on bits: `bits[i] = bits[i >> 1] + (i & 1)`, or `bits[i] = bits[i & (i - 1)] + 1`. Each reuses a smaller, already computed answer. Mention that `int.bit_count` is O(1) per call for small ints, and that hardware has a POPCNT instruction.
