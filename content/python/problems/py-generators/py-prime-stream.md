---
id: py-prime-stream
title: Infinite Prime Stream
difficulty: Hard
order: 2
time_limit: 4
tags: generators, sieve, dictionaries, infinite sequences
---
## Statement
Write an **infinite generator** `primes()` yielding 2, 3, 5, 7, 11, …, quickly enough to produce the first **200,000 primes** in a couple of seconds.

The driver answers queries "what is the n-th prime?" (1-indexed, n ≤ 200,000) and "how many primes are ≤ x?" (x ≤ 2,750,000) by consuming your generator.

Trial division for every candidate is too slow for the largest tests. Use an **incremental sieve**.

## Starter
```python
def primes():
    pass
```

## Driver
```python
import inspect, itertools, bisect
assert inspect.isgeneratorfunction(primes)
queries = [input().split() for _ in range(int(input()))]
need_n = max([int(v) for k, v in queries if k == "nth"], default=0)
need_x = max([int(v) for k, v in queries if k == "count"], default=0)
got = []
for p in primes():
    if len(got) >= need_n and p > need_x:
        break
    got.append(p)
for k, v in queries:
    v = int(v)
    print(got[v - 1] if k == "nth" else bisect.bisect_right(got, v))
```

## Tests
=== sample
3
nth 1
nth 10
count 100
---
2
29
25
=== hidden
3
nth 1000
count 1000000
nth 78498
---
7919
78498
999983
=== hidden
2
nth 200000
count 2750000
---
2750159
199993

## Hints
- Keep a dict `composites` mapping each upcoming composite number to the list of primes that "hit" it.
- For each candidate `q` from 2 upwards: if `q` isn't in the dict, it's prime. Yield it and record `q*q` (the first composite it needs to mark). If it is in the dict, move each witness prime `p` forward to `q + p`, then delete `q`.
- This is the "Sieve of Eratosthenes, lazily", with memory proportional to the number of primes found so far.

## Solution
**Incremental sieve.** Instead of crossing off multiples in a fixed array, each prime `p` keeps a "next multiple to mark" in a dict. When the candidate counter reaches a number in the dict, it's composite: advance its witnesses to their next multiples. Otherwise it's a new prime.

```python
def primes():
    composites = {}          # next composite number -> primes that divide it
    q = 2
    while True:
        if q not in composites:
            yield q
            composites[q * q] = [q]
        else:
            for p in composites[q]:
                composites.setdefault(q + p, []).append(p)
            del composites[q]
        q += 1
```

Starting each prime at `p*p` is the classic optimisation: smaller multiples of `p` have a smaller prime factor that already marked them. The total work is about O(n log log n), as for the array sieve, but with no upper bound needed in advance. That's exactly what an infinite generator allows. This algorithm is due to David Mertz and Alex Martelli (Python Cookbook).
