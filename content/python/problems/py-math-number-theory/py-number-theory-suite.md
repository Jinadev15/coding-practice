---
id: py-number-theory-suite
title: "Number Theory Suite: Primes, Binomials mod p, Fibonacci 10^18, Convex Hull Area"
difficulty: Hard
order: 1
tags: sieve, modular inverse, fast doubling, combinatorics, convex hull
time_limit: 4
---
## Statement
```python
def count_primes(n):
    """Number of primes < n (n up to 10**7). Use a bytearray sieve with slice assignment."""

def binomials_mod(queries):
    """queries: list of (n, k) with 0 <= n <= 10**6. Return [C(n, k) mod 1_000_000_007] (0 if k < 0 or k > n).
    Precompute factorials and inverse factorials once: O(max_n + q)."""

def fib_mod(n):
    """The n-th Fibonacci number mod 1_000_000_007 (F0 = 0, F1 = 1), n up to 10**18. O(log n)."""

def hull_area2(points):
    """Twice the area of the convex hull of integer points (an exact integer). Fewer than 3 hull points -> 0."""
```

Test lines are `(function_name, args)` literals or `gen NAME SEED N`.

## Starter
```python
from math import comb

def count_primes(n):
    return sum(1 for x in range(2, n) if all(x % d for d in range(2, int(x ** 0.5) + 1)))

def binomials_mod(queries):
    return [comb(n, k) % 1_000_000_007 if 0 <= k <= n else 0 for n, k in queries]

def fib_mod(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, (a + b) % 1_000_000_007
    return a

def hull_area2(points):
    return 0
```

## Driver
```python
import ast
import random
import sys

FUNCS = {f.__name__: f for f in (count_primes, binomials_mod, fib_mod, hull_area2)}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        if name == "count_primes":
            print(name, n, count_primes(n))
        elif name == "binomials_mod":
            qs = [(m, rng.randrange(-2, m + 3)) for m in (rng.randrange(10**6 + 1) for _ in range(n))]
            r = binomials_mod(qs)
            print(name, n, sum(r) % 1_000_000_007, r[:3])
        elif name == "fib_mod":
            print(name, [fib_mod(x) for x in (10**18, 10**18 + 1, 123456789123456789, 2**60)])
        else:
            pts = [(rng.randrange(-10**9, 10**9), rng.randrange(-10**9, 10**9)) for _ in range(n)]
            print(name, n, hull_area2(pts))
        continue
    name, args = ast.literal_eval(line)
    print(name, "->", FUNCS[name](*args))
```

## Tests
=== sample
("count_primes", (10,))
("binomials_mod", ([(5, 2), (10, 0), (3, 4), (1000000, 500000)],))
("fib_mod", (10,))
("hull_area2", ([(0, 0), (4, 0), (4, 3), (0, 3), (2, 1)],))
---
count_primes -> 4
binomials_mod -> [10, 1, 0, 996692777]
fib_mod -> 55
hull_area2 -> 24
=== hidden
("count_primes", (0,))
("count_primes", (2,))
("count_primes", (3,))
("count_primes", (100,))
("binomials_mod", ([(0, 0), (1, -1), (7, 7), (52, 5)],))
("fib_mod", (0,))
("fib_mod", (1,))
("fib_mod", (2,))
("fib_mod", (100,))
("hull_area2", ([],))
("hull_area2", ([(1, 1), (2, 2), (3, 3)],))
("hull_area2", ([(0, 0), (0, 0), (5, 0), (0, 5)],))
("hull_area2", ([(0, 0), (2, 0), (2, 2), (0, 2), (1, 1), (1, 0)],))
---
count_primes -> 0
count_primes -> 0
count_primes -> 1
count_primes -> 25
binomials_mod -> [1, 0, 1, 2598960]
fib_mod -> 0
fib_mod -> 1
fib_mod -> 1
fib_mod -> 687995182
hull_area2 -> 0
hull_area2 -> 0
hull_area2 -> 25
hull_area2 -> 8
=== hidden
gen count_primes 1 10000000
gen fib_mod 3 0
---
count_primes 10000000 664579
fib_mod [209783453, 680057396, 210677523, 172833444]
=== hidden
gen binomials_mod 2 200000
gen hull_area2 4 200000
---
binomials_mod 200000 662566244 [57188333, 291496622, 989732629]
hull_area2 200000 7998520489399525898

## Hints
- **Sieve**: `is_p = bytearray([1]) * n`; for each prime i ≤ √n, `is_p[i*i::i] = bytes(len(range(i*i, n, i)))`; the answer is `sum(is_p)` after clearing 0 and 1.
- **Binomials**: `fact` up to max n; `inv_fact[N] = pow(fact[N], MOD-2, MOD)`, then `inv_fact[i-1] = inv_fact[i] * i % MOD`.
- **Fibonacci fast doubling**: F(2k) = F(k)·(2F(k+1) − F(k)) and F(2k+1) = F(k)² + F(k+1)², processing the bits of n from the top.
- **Hull**: Andrew's monotone chain on sorted unique points (pop while the cross product ≤ 0), then the shoelace formula on the hull vertices.

## Solution
```python
MOD = 1_000_000_007

def count_primes(n):
    if n < 3:
        return 0
    is_p = bytearray([1]) * n
    is_p[0] = is_p[1] = 0
    i = 2
    while i * i < n:
        if is_p[i]:
            is_p[i * i::i] = bytes(len(range(i * i, n, i)))
        i += 1
    return sum(is_p)

def binomials_mod(queries):
    N = max((n for n, _ in queries), default=0)
    fact = [1] * (N + 1)
    for i in range(1, N + 1):
        fact[i] = fact[i - 1] * i % MOD
    inv = [1] * (N + 1)
    inv[N] = pow(fact[N], MOD - 2, MOD)
    for i in range(N, 0, -1):
        inv[i - 1] = inv[i] * i % MOD
    return [fact[n] * inv[k] % MOD * inv[n - k] % MOD if 0 <= k <= n else 0 for n, k in queries]

def fib_mod(n):
    a, b = 0, 1                                  # (F(k), F(k+1)) with k = the prefix of n's bits
    for bit in bin(n)[2:]:
        c = a * ((2 * b - a) % MOD) % MOD        # F(2k)
        d = (a * a + b * b) % MOD                # F(2k+1)
        a, b = (d, (c + d) % MOD) if bit == "1" else (c, d)
    return a

def _cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

def hull_area2(points):
    pts = sorted(set(map(tuple, points)))
    if len(pts) < 3:
        return 0
    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and _cross(h[-2], h[-1], p) <= 0:
                h.pop()
            h.append(p)
        return h
    hull = half(pts)[:-1] + half(pts[::-1])[:-1]
    if len(hull) < 3:
        return 0
    area2 = 0
    for i in range(len(hull)):
        x1, y1 = hull[i]
        x2, y2 = hull[(i + 1) % len(hull)]
        area2 += x1 * y2 - x2 * y1
    return abs(area2)
```

- **The sieve** marks the multiples of each prime p starting from p², because smaller multiples already have a smaller prime factor. Slice assignment on a `bytearray` runs in C, so 10⁷ takes well under a second, where a Python loop would take tens of seconds.
- **Binomials mod p**: one Fermat inverse (`pow(x, p−2, p)`) plus the backward recurrence gives every inverse factorial in O(N), so each query is three multiplications.
- **Fast doubling** walks the bits of n, so F(10¹⁸) needs 60 steps instead of 10¹⁸ additions. It's matrix exponentiation of [[1,1],[1,0]] in a cheaper form.
- **Monotone chain** sorts the points once and builds the lower and upper hulls with cross-product turn tests, all in exact integer arithmetic (Python ints never overflow, even for 10⁹ coordinates). The shoelace formula then gives twice the area exactly.
