# math, random, statistics

Numerical work in pure Python rests on three standard modules: **`math`** (fast C implementations of real functions, plus exact integer number theory), **`random`** (pseudo-random numbers for simulation, sampling and testing) and **`statistics`** (descriptive statistics). Before NumPy, you need to know them well. They also hide important traps: float rounding, banker's rounding, floor division of negatives, and reproducibility of random experiments.

## 1. `math`: floats and real functions

```python
import math
math.sqrt(2), math.exp(1), math.log(100, 10), math.log2(8), math.log10(1e-3)
math.sin(math.pi / 2), math.atan2(1, 1), math.degrees(math.pi)    # 1.0 0.785... 180.0
math.hypot(3, 4), math.dist((0, 0), (3, 4))                       # 5.0 5.0
math.floor(-2.5), math.ceil(-2.5), math.trunc(-2.5)               # -3 -2 -2
math.inf, -math.inf, math.nan
math.isfinite(x), math.isnan(x)
```

> [!KEY]
> Use `math.atan2(y, x)`, not `atan(y / x)`. It handles `x == 0` and returns the correct **quadrant** in (−π, π]. That's essential for robot headings and angles between vectors. Normalise an angle into (−π, π] with `math.atan2(math.sin(a), math.cos(a))`.

### Floating point equality

```python
0.1 + 0.2 == 0.3                   # False: 0.1 has no exact binary representation
math.isclose(0.1 + 0.2, 0.3)       # True (default rel_tol=1e-09)
math.isclose(x, 0.0, abs_tol=1e-12)   # comparing to zero needs abs_tol!
math.fsum([0.1] * 10)              # 1.0: exactly rounded summation
```

`sum()` of floats uses compensated (Neumaier) summation since Python 3.12, so `sum([0.1] * 10)` is also `1.0` now. `fsum` is still the exactly rounded reference. `nan` isn't equal to anything, itself included: `math.nan == math.nan` is `False`.

## 2. Rounding and division traps

```python
round(2.5), round(3.5)     # 2 4: ROUND HALF TO EVEN ("banker's rounding")
round(0.125, 2)            # 0.12: 0.125 is stored as 0.12499999...
int(-2.5)                  # -2: truncates toward zero
-7 // 2, -7 % 2            # -4 1: floor division, and % has the sign of the divisor
math.fmod(-7, 2)           # -1.0: C-style remainder (sign of the dividend)
```

> [!WARNING]
> `round()` uses banker's rounding to avoid statistical bias, which surprises everyone who expects "half up". For money, use `decimal.Decimal` with `ROUND_HALF_UP`. Never use binary floats for currency.

## 3. Exact integer math

Python integers have arbitrary precision, and `math` has exact integer functions:

```python
math.isqrt(10**20 + 1)          # 10000000000: exact floor sqrt (math.sqrt would lose precision)
math.gcd(12, 18, 27), math.lcm(4, 6)       # 3 12
math.comb(5, 2), math.perm(5, 2)           # 10 20: nCr, nPr
math.factorial(20), math.prod([1, 2, 3, 4])    # 2432902008176640000 24
pow(3, 10**18, 10**9 + 7)       # built-in modular exponentiation, O(log e)
pow(3, -1, 7)                   # 5: modular inverse (3.8+)
```

> [!TIP]
> In competitive programming and crypto-style problems, use `pow(b, e, m)`, never `b ** e % m`, which computes a gigantic number first. Perfect-square test: `math.isqrt(n) ** 2 == n` (exact, unlike `int(math.sqrt(n))`, which fails for large n).

## 4. `random`: pseudo-random numbers

```python
import random
random.seed(42)                 # reproducible sequence
random.random()                 # float in [0.0, 1.0): 0.6394267984578837 after seed(42)
random.randint(1, 6)            # int in [1, 6]: BOTH ends inclusive
random.randrange(0, 10, 2)      # like range(): end exclusive
random.uniform(-1.0, 1.0)
random.gauss(0.0, 0.1)          # normal distribution, for sensor-noise simulation
random.choice(seq)              # one element
random.choices(seq, weights=[...], k=5)   # with replacement, weighted
random.sample(seq, k=3)         # without replacement
random.shuffle(lst)             # in place, returns None
```

| Need | Use |
|---|---|
| reproducible experiments and tests | `random.seed(n)`, or an independent `rng = random.Random(n)` |
| security tokens, passwords | **`secrets`** module (`secrets.token_hex(16)`), never `random` |
| large numeric arrays | `numpy.random.default_rng(seed)` |

> [!DANGER]
> `random` is a Mersenne Twister: fast and statistically good, but **predictable**. After observing 624 outputs, an attacker can reconstruct its state and predict every future value. Use `secrets` for anything security-related.

`random.Random(seed)` instances have independent state. Give each simulation component its own generator so adding a random call in one place doesn't change the results elsewhere (important for reproducible ML and robotics experiments).

## 5. `statistics`

```python
import statistics as st
data = [2, 4, 4, 4, 5, 5, 7, 9]
st.mean(data), st.median(data), st.mode(data)     # 5 4.5 4
st.pstdev(data)     # 2.0: POPULATION standard deviation (divide by n)
st.stdev(data)      # 2.138...: SAMPLE standard deviation (divide by n - 1)
st.quantiles([1, 2, 3, 4, 5, 6, 7, 8], n=4)       # [2.25, 4.5, 6.75]
st.correlation(xs, ys), st.linear_regression(xs, ys)   # 3.10+
```

> [!KEY]
> `stdev` (sample, n−1, Bessel's correction) estimates the spread of a larger population from a sample. `pstdev` (population, n) describes exactly the data you have. That's a classic exam question.

## 6. Exam-ready answers

> [!EXAM]
> **Numeric modules.** The `math` module provides mathematical functions on floats (trigonometric, logarithmic and exponential functions, `floor`, `ceil`, `isclose`, `fsum`) and exact integer functions (`gcd`, `lcm`, `isqrt`, `comb`, `perm`, `factorial`). Floating-point values are binary approximations, so equality tests should use `math.isclose` with suitable tolerances. Python's `round` uses round-half-to-even. The `random` module generates pseudo-random numbers with the Mersenne Twister; `seed` makes sequences reproducible, and functions such as `randint`, `choice`, `sample` and `shuffle` support sampling, but the module is unsuitable for cryptography, for which `secrets` is used. The `statistics` module computes measures such as `mean`, `median`, `mode`, and the population (`pstdev`) and sample (`stdev`) standard deviations.

## 7. Cheat sheet

| Need | Code |
|---|---|
| compare floats | `math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-12)` |
| angle from a vector | `math.atan2(y, x)` |
| exact integer sqrt | `math.isqrt(n)` |
| nCr | `math.comb(n, r)` |
| modular power / inverse | `pow(b, e, m)` / `pow(a, -1, m)` |
| half-up rounding | `Decimal(x).quantize(Decimal("0.01"), ROUND_HALF_UP)` |
| reproducible randomness | `rng = random.Random(42)` |
| secure token | `secrets.token_urlsafe(16)` |
| sample vs population std | `stdev` vs `pstdev` |

> [!INTERVIEW]
> **"Why does `round(2.5)` return 2 in Python?"** Python 3 uses round-half-to-even (banker's rounding): ties go to the nearest even number, so rounding errors don't accumulate in one direction over many operations, which matters in statistics and finance. Add that many "ties" aren't actually ties in binary (`round(2.675, 2) == 2.67`, because 2.675 is stored as 2.67499999…), and that `decimal` gives exact decimal rounding with selectable modes.
