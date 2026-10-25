# Math and Number Theory

Many algorithmic problems reduce to arithmetic facts:
- gcd and lcm, primes and factorisation
- modular arithmetic with large results ("answer modulo 10⁹+7")
- fast exponentiation and modular inverses
- combinatorics (n choose k), and geometry on integer lattices

These tools also underpin cryptography (RSA, Diffie–Hellman), hashing, random number generation and checksums. Python helps a lot: arbitrary-precision ints, `math.gcd`, `math.comb`, and three-argument `pow(base, exp, mod)`, including negative exponents for modular inverses (3.8+).

## 1. GCD and LCM

```python
import math

def gcd(a, b):                     # Euclid: gcd(a, b) = gcd(b, a mod b), O(log min(a, b)) steps
    while b:
        a, b = b, a % b
    return abs(a)

math.gcd(48, 18)                   # 6
math.lcm(4, 6)                     # 12 (3.9+): a // gcd(a, b) * b, which avoids a big intermediate
math.gcd(12, 18, 30)               # 6 (several arguments, 3.9+)
```

**Extended Euclid** finds x, y with `a·x + b·y = gcd(a, b)` (Bézout), which is needed for modular inverses and linear Diophantine equations:

```python
def ext_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x, y = ext_gcd(b, a % b)
    return g, y, x - (a // b) * y

ext_gcd(240, 46)       # (2, -9, 47): 240·(-9) + 46·47 = 2
```

Uses: reducing fractions, the "water jug" problem (measurable iff target % gcd == 0), and cycles in modular sequences (rotating an array by k splits it into gcd(n, k) cycles).

## 2. Primes

```python
def is_prime(n):                   # trial division: O(√n)
    if n < 2: return False
    if n % 2 == 0: return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0: return False
        i += 2
    return True

def sieve(n):                      # Eratosthenes: all primes <= n in O(n log log n)
    is_p = bytearray([1]) * (n + 1)
    is_p[0] = is_p[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if is_p[i]:
            is_p[i * i::i] = bytes(len(range(i * i, n + 1, i)))   # slice assignment at C speed
    return [i for i in range(n + 1) if is_p[i]]

def factorize(n):                  # trial division, O(√n)
    f, d = {}, 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f

factorize(360)    # {2: 3, 3: 2, 5: 1}
```

For many factorisations up to N, precompute the **smallest prime factor** (SPF) with a sieve, after which each factorisation is O(log n). For huge n (around 10¹⁸), use **Miller–Rabin** (deterministic bases exist for 64-bit) plus **Pollard's rho**.

From the factorisation p₁^e₁ ⋯ p_k^e_k:
- the number of divisors is Π(eᵢ + 1)
- the sum of divisors is Π(pᵢ^(eᵢ+1) − 1)/(pᵢ − 1)
- **Euler's totient** is φ(n) = n·Π(1 − 1/pᵢ)

## 3. Modular arithmetic

Results are often requested **mod M = 10⁹ + 7** (a prime), which keeps numbers small and makes division possible via inverses.

| Rule | Holds mod M? |
|---|---|
| (a + b) mod M = ((a mod M) + (b mod M)) mod M | ✓ |
| (a · b) mod M = ((a mod M)·(b mod M)) mod M | ✓ |
| (a − b) mod M | ✓ (Python's `%` is always non-negative for M > 0) |
| (a / b) mod M | ✗ — multiply by the inverse b⁻¹ instead |

```python
MOD = 10**9 + 7
pow(3, 10**18, MOD)          # fast exponentiation: O(log exponent) multiplications
pow(5, -1, MOD)              # modular inverse (3.8+): 5 * inv ≡ 1 (mod MOD); requires gcd(5, MOD) = 1
pow(5, MOD - 2, MOD)         # the same via Fermat's little theorem (MOD prime)

def power(base, exp, mod):   # what pow does: square-and-multiply
    result = 1
    base %= mod
    while exp:
        if exp & 1:
            result = result * base % mod
        base = base * base % mod
        exp >>= 1
    return result
```

> [!KEY]
> **Fermat's little theorem**: for a prime p and a not divisible by p, a^(p−1) ≡ 1 (mod p), so a^(p−2) is a's inverse. For a non-prime modulus, use the extended gcd (the inverse exists iff gcd(a, m) = 1). **Euler's theorem** generalises: a^φ(m) ≡ 1 (mod m) when gcd(a, m) = 1.

**Matrix exponentiation**: linear recurrences (Fibonacci, tiling counts, path counts of length k in a graph) in O(d³ log n), e.g. the n-th Fibonacci number mod M for n = 10¹⁸.

## 4. Combinatorics mod a prime

```python
MOD = 10**9 + 7
N = 10**6
fact = [1] * (N + 1)
for i in range(1, N + 1):
    fact[i] = fact[i - 1] * i % MOD
inv_fact = [1] * (N + 1)
inv_fact[N] = pow(fact[N], MOD - 2, MOD)
for i in range(N, 0, -1):
    inv_fact[i - 1] = inv_fact[i] * i % MOD          # all the inverses in O(N)

def nCr(n, r):
    if r < 0 or r > n: return 0
    return fact[n] * inv_fact[r] % MOD * inv_fact[n - r] % MOD
```

Exact (non-modular) values: `math.comb(n, k)` and `math.perm(n, k)`. Useful identities:
- **lattice paths** in an a×b grid: C(a+b, a)
- **stars and bars** (k non-negative ints summing to n): C(n+k−1, k−1)
- **Catalan numbers** (balanced parentheses, BST shapes, triangulations): C(2n, n)/(n+1)
- **inclusion–exclusion** for "at least one" counting
- **Lucas's theorem** for C(n, k) mod a small prime p

## 5. Integer geometry

- Points on a segment between lattice points: `gcd(|dx|, |dy|) + 1`.
- Twice the polygon area (**shoelace**): `|Σ (xᵢ·yᵢ₊₁ − xᵢ₊₁·yᵢ)|`, which is exact in integers.
- **Pick's theorem**: A = I + B/2 − 1.
- **Orientation** (cross product) of three points decides left/right turns. That's the core of convex hulls (Andrew's monotone chain, O(n log n)) and segment intersection.

```python
def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

def convex_hull(points):
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts
    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and cross(h[-2], h[-1], p) <= 0:   # pop non-left turns
                h.pop()
            h.append(p)
        return h
    lower, upper = half(pts), half(reversed(pts))
    return lower[:-1] + upper[:-1]          # counter-clockwise, no repeated endpoints
```

## 6. Exam-ready answers

> [!EXAM]
> **Modular exponentiation and inverses.** Fast modular exponentiation computes a^e mod m in O(log e) multiplications by repeated squaring, multiplying the result by the current power whenever the corresponding bit of e is set and reducing modulo m after each step. A modular inverse of a modulo m exists exactly when gcd(a, m) = 1, and can be computed with the extended Euclidean algorithm, which finds x and y with ax + my = 1, or, when m is prime, as a^(m−2) mod m by Fermat's little theorem. Inverses allow division in modular arithmetic, for example computing binomial coefficients modulo a prime from precomputed factorials and inverse factorials.

## 7. Cheat sheet

| Need | Python |
|---|---|
| gcd / lcm | `math.gcd`, `math.lcm` |
| a^e mod m | `pow(a, e, m)` |
| inverse mod m | `pow(a, -1, m)` |
| primes ≤ n | bytearray sieve |
| factorise many | an SPF sieve |
| nCr exact | `math.comb` |
| nCr mod p, many | fact + inv_fact tables |
| integer sqrt | `math.isqrt(n)` |
| convex hull | monotone chain with cross products |

> [!INTERVIEW]
> **"Compute C(n, k) mod 10⁹+7 for many queries with n ≤ 10⁶."** Precompute the factorials mod p in O(n), the inverse of fact[n] with one Fermat exponentiation, then all the inverse factorials backwards with `inv_fact[i-1] = inv_fact[i]·i`. Each query is then O(1). Mention the conditions: p must be prime and greater than n (otherwise the factorials contain p, so use Lucas's theorem), and division only works through inverses.
