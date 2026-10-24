---
id: py-number-toolkit
title: Exact Number Toolkit
difficulty: Medium
order: 1
tags: math, isqrt, comb, gcd, pow, fractions
---
## Statement
Answer queries **exactly**: no floating-point errors allowed, and numbers can have up to 200 digits. Each line is one query:

| Query | Output |
|---|---|
| `isqrt N` | ⌊√N⌋ |
| `square N` | `yes` if N is a perfect square, else `no` |
| `comb N K` | C(N, K) mod 1 000 000 007 (N ≤ 10⁶; 0 if K > N) |
| `gcd A B C ...` / `lcm A B C ...` | of all the arguments |
| `powmod B E M` | Bᴱ mod M (E up to 200 digits) |
| `inv A M` | the modular inverse of A mod M, or `none` |
| `mean X1 X2 ...` | the exact arithmetic mean of the integers, as a reduced fraction `p/q`, or just `p` if whole |
| `round X D` | the decimal number X (like `2.675`) rounded **half up** to D decimals, exactly as written (use `decimal`) |

## Starter
```python
import sys, math

for line in sys.stdin.read().splitlines():
    cmd, *args = line.split()
```

## Tests
=== sample
isqrt 99
square 144
comb 5 2
gcd 12 18 27
lcm 4 6 10
powmod 3 200 1000000007
inv 3 7
inv 4 8
mean 1 2 4
round 2.675 2
---
9
yes
10
3
60
136318165
5
none
7/3
2.68
=== hidden
isqrt 10000000000000000000000000000000000000001
isqrt 0
square 99999999999999999999999999999999999999980000000000000000000000000000000000000001
square 99999999999999999999999999999999999999980000000000000000000000000000000000000002
comb 1000000 500000
comb 10 11
comb 0 0
gcd 0 5
lcm 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20
powmod 2 123456789012345678901234567890123456789 1000000007
inv 1 1
inv 999999937 1000000007
mean 7
mean -1 2
mean 3 3 3 4
round 0.125 2
round 1.005 2
round -2.5 0
round 9.9999 3
---
100000000000000000000
0
yes
no
996692777
0
1
5
232792560
488999979
0
185714287
7
1/2
13/4
0.13
1.01
-3
10.000

## Hints
- `math.isqrt` is exact for any size of int. `math.sqrt` isn't (it converts to a float).
- `math.comb(10**6, 5 * 10**5)` is exact but has ~300 000 digits, so taking it mod p at the end works, but it's slow. Precomputing factorials mod p and using `pow(x, -1, p)` (Fermat) is the scalable way.
- `math.gcd` and `math.lcm` accept any number of arguments (3.9+).
- `pow(a, -1, m)` raises `ValueError` when no inverse exists.
- `fractions.Fraction(sum(xs), len(xs))` reduces automatically.
- `Decimal(text).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)`. Construct the Decimal from the **string**, not from a float.

## Solution
```python
import sys, math
from fractions import Fraction
from decimal import Decimal, ROUND_HALF_UP

MOD = 10**9 + 7
LIMIT = 10**6
fact = [1] * (LIMIT + 1)
for i in range(1, LIMIT + 1):
    fact[i] = fact[i - 1] * i % MOD

def comb_mod(n, k):
    if k < 0 or k > n:
        return 0
    return fact[n] * pow(fact[k], -1, MOD) % MOD * pow(fact[n - k], -1, MOD) % MOD

out = []
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    cmd, *args = line.split()
    if cmd == "isqrt":
        out.append(str(math.isqrt(int(args[0]))))
    elif cmd == "square":
        n = int(args[0])
        out.append("yes" if math.isqrt(n) ** 2 == n else "no")
    elif cmd == "comb":
        out.append(str(comb_mod(int(args[0]), int(args[1]))))
    elif cmd == "gcd":
        out.append(str(math.gcd(*map(int, args))))
    elif cmd == "lcm":
        out.append(str(math.lcm(*map(int, args))))
    elif cmd == "powmod":
        b, e, m = map(int, args)
        out.append(str(pow(b, e, m)))
    elif cmd == "inv":
        a, m = map(int, args)
        try:
            out.append(str(pow(a, -1, m)))
        except ValueError:
            out.append("none")
    elif cmd == "mean":
        xs = list(map(int, args))
        f = Fraction(sum(xs), len(xs))
        out.append(str(f.numerator) if f.denominator == 1 else f"{f.numerator}/{f.denominator}")
    elif cmd == "round":
        x, d = Decimal(args[0]), int(args[1])
        out.append(str(x.quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)))
print("\n".join(out))
```

Python's arbitrary-precision `int` makes exact number theory straightforward, as long as you **never pass through `float`**:
- `isqrt` instead of `sqrt` for exact roots.
- Three-argument `pow` does modular exponentiation in O(log E) multiplications, even for a 200-digit exponent. `pow(a, -1, m)` is the extended-Euclid inverse.
- `Fraction` keeps the mean exact.
- `Decimal` built from the **string** `"2.675"` is exactly 2.675. `round(2.675, 2)` on the float gives `2.67`, because the float is really 2.67499999…

Precomputing factorials mod p makes each `comb` query O(log p), the standard technique in competitive programming.
