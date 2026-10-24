---
id: py-primes-upto
title: Primes up to N
difficulty: Medium
order: 3
tags: nested loops, loop-else, trial division
---
## Statement
Print all primes `≤ n` on one line, separated by spaces, then on the next line how many there are. If there are none, print an empty line and then `0`.

`1 ≤ n ≤ 20000`. Use **trial division** with the loop `else` clause. Test divisors only up to `√p`. (A faster algorithm, the Sieve of Eratosthenes, comes in the Number Theory topic.)

## Starter
```python
n = int(input())
```

## Tests
=== sample
20
---
2 3 5 7 11 13 17 19
8
=== sample
1
---

0
=== hidden
2
---
2
1
=== hidden
100
---
2 3 5 7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97
25
=== hidden
20000
=== hidden
7919

## Hints
- A number `p ≥ 2` is prime if no `d` with `2 ≤ d ≤ √p` divides it.
- `for d in range(2, int(p ** 0.5) + 1): if p % d == 0: break` and then `else:` means "no divisor found".
- Why √p? If `p = a·b` with `a ≤ b`, then `a ≤ √p`.

## Solution
For each candidate, search for a divisor up to `√p`. The loop's `else` runs only when no `break` happened, i.e. no divisor exists, so that's exactly where we record the prime.

```python
n = int(input())
primes = []
for p in range(2, n + 1):
    for d in range(2, int(p ** 0.5) + 1):
        if p % d == 0:
            break
    else:
        primes.append(p)
print(" ".join(map(str, primes)))
print(len(primes))
```

**Complexity:** O(n√n) in the worst case, which is fine for 20000. For p = 2 and 3, `range(2, 2)` is empty, so the inner loop does nothing and the `else` runs: they're correctly prime. Some hidden tests have no `---` expected output, so the judge computes it from this reference solution. There are 2262 primes up to 20000.

`math.isqrt(p)` is the exact integer square root. Prefer it to `int(p ** 0.5)` for very large numbers, where float rounding can be off by one.
