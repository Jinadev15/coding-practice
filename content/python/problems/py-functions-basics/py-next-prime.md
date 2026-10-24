---
id: py-next-prime
title: Prime Helpers
difficulty: Easy
order: 3
tags: functions, composition, primes
---
## Statement
Write:

- `is_prime(n)`: `True` if `n` is prime (n can be any integer, including negatives, 0 and 1)
- `next_prime(n)`: the smallest prime **strictly greater** than `n`, built on `is_prime`
- `prime_gap(n)`: `next_prime(n) - n`, built on `next_prime`

For each query `n`, the driver prints `is_prime(n) next_prime(n) prime_gap(n)`.

`|n| ≤ 10^9`. Trial division up to `√n` is fast enough for single numbers.

## Starter
```python
import math

def is_prime(n):
    pass

def next_prime(n):
    pass

def prime_gap(n):
    pass
```

## Driver
```python
t = int(input())
for _ in range(t):
    n = int(input())
    print(is_prime(n), next_prime(n), prime_gap(n))
```

## Tests
=== sample
3
7
10
1
---
True 11 4
False 11 1
False 2 1
=== hidden
4
-5
0
2
13
---
False 2 7
False 2 2
True 3 1
True 17 4
=== hidden
2
1000000000
999999937
---
False 1000000007 7
True 1000000007 70

## Hints
- `n < 2` → not prime. Check 2 separately, then only odd divisors up to `math.isqrt(n)`.
- `next_prime`: start at `n + 1` and step until `is_prime` says yes.

## Solution
Three tiny functions, each built on the previous one. `math.isqrt` gives the exact integer square root, with no float rounding issues near 10^9.

```python
import math

def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    for d in range(3, math.isqrt(n) + 1, 2):
        if n % d == 0:
            return False
    return True

def next_prime(n):
    candidate = max(n + 1, 2)
    while not is_prime(candidate):
        candidate += 1
    return candidate

def prime_gap(n):
    return next_prime(n) - n
```

Skipping even divisors halves the work: about 15,800 checks for n ≈ 10^9. `max(n + 1, 2)` handles negative inputs. Notice how `prime_gap` stays a one-liner because the lower-level functions already exist. Composition is the main payoff of small functions.
