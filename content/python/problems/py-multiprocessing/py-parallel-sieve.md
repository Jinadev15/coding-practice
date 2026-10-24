---
id: py-parallel-sieve
title: Parallel Prime Counting with Processes
difficulty: Medium
order: 1
tags: multiprocessing, ProcessPoolExecutor, pickling, chunking, __main__ guard
time_limit: 6
---
## Statement
Count primes in many large ranges using **worker processes**, so the CPU-bound work runs outside the main interpreter:

```python
def count_primes(lo: int, hi: int) -> tuple[int, int]
    # number of primes p with lo <= p < hi (a segmented sieve), and os.getpid() of the process that did the work
def parallel_counts(ranges: list[tuple[int, int]], workers: int) -> list[int]
    # counts for each range IN INPUT ORDER, computed in a process pool; must verify that no range
    # was computed in the main process (raise RuntimeError otherwise)
```

Rules:
- `count_primes` must be a **top-level** function (so it can be pickled and sent to workers).
- Use `concurrent.futures.ProcessPoolExecutor(max_workers=workers)` or `multiprocessing.Pool`.
- Ranges are up to 2 000 000 wide, with `hi` ≤ 10⁸. Use a segmented sieve: sieve the primes up to √hi, then mark their multiples inside `[lo, hi)` in a `bytearray`. Trial division would be far too slow.
- The driver runs your code under `if __name__ == "__main__":`. Your module must not start any processes at import time.

## Starter
```python
import os

def count_primes(lo, hi):
    def is_prime(n):
        if n < 2:
            return False
        return all(n % d for d in range(2, int(n ** 0.5) + 1))
    return sum(is_prime(n) for n in range(lo, hi)), os.getpid()

def parallel_counts(ranges, workers):
    return [count_primes(lo, hi)[0] for lo, hi in ranges]
```

## Driver
```python
import sys

if __name__ == "__main__":
    data = sys.stdin.read().split()
    workers, n = int(data[0]), int(data[1])
    ranges = [(int(data[2 + 2 * i]), int(data[3 + 2 * i])) for i in range(n)]
    counts = parallel_counts(ranges, workers)
    for (lo, hi), c in zip(ranges, counts):
        print(f"[{lo}, {hi}): {c}")
    print("total", sum(counts))
```

## Tests
=== sample
2 4
0 10
10 100
100 1000
0 2
---
[0, 10): 4
[10, 100): 21
[100, 1000): 143
[0, 2): 0
total 168
=== hidden
4 3
0 1
2 3
999983 999984
---
[0, 1): 0
[2, 3): 1
[999983, 999984): 1
total 2
=== hidden
4 8
0 2000000
2000000 4000000
50000000 52000000
98000000 100000000
1 2
7 8
90 97
13 13
---
[0, 2000000): 148933
[2000000, 4000000): 134213
[50000000, 52000000): 112709
[98000000, 100000000): 108459
[1, 2): 0
[7, 8): 1
[90, 97): 0
[13, 13): 0
total 504315

## Hints
- Simple sieve up to √hi: `small = bytearray([1]) * (r + 1)`, then cross out multiples.
- Segment: `seg = bytearray([1]) * (hi - lo)`. For each small prime p, start at `max(p * p, ((lo + p - 1) // p) * p)` and set `seg[start - lo :: p] = bytes(len(range(start, hi, p)))`. That's slice assignment, done in C. Remember to clear 0 and 1 if they're in range.
- `with ProcessPoolExecutor(workers) as ex: results = list(ex.map(count_primes, los, his))`. `map` keeps the input order.
- Compare each returned pid with `os.getpid()` in the parent.

## Solution
```python
import os
import math
from concurrent.futures import ProcessPoolExecutor

def count_primes(lo, hi):
    lo = max(lo, 0)
    if hi <= lo:
        return 0, os.getpid()
    r = math.isqrt(hi - 1) if hi > 1 else 0
    small = bytearray([1]) * (r + 1)
    small[0:2] = b"\x00\x00"[: min(2, r + 1)]
    for i in range(2, math.isqrt(r) + 1):
        if small[i]:
            small[i * i :: i] = bytes(len(range(i * i, r + 1, i)))
    seg = bytearray([1]) * (hi - lo)
    for p in range(2, r + 1):
        if small[p]:
            start = max(p * p, ((lo + p - 1) // p) * p)
            if start < hi:
                seg[start - lo :: p] = bytes(len(range(start, hi, p)))
    for v in (0, 1):                          # 0 and 1 are not prime
        if lo <= v < hi:
            seg[v - lo] = 0
    return sum(seg), os.getpid()

def parallel_counts(ranges, workers):
    with ProcessPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(count_primes, [lo for lo, _ in ranges], [hi for _, hi in ranges]))
    main = os.getpid()
    if any(pid == main for _, pid in results):
        raise RuntimeError("work ran in the main process")
    return [c for c, _ in results]
```

- **Processes sidestep the GIL:** each worker is a separate interpreter, so CPU-bound sieving runs truly in parallel on multiple cores, which threads can't do on a standard build.
- **Pickling defines the interface:** only the function *name* and two integers go to each worker, and one small tuple comes back. Sending millions of numbers instead would make IPC the bottleneck.
- **Order preservation:** `ex.map` returns results in input order even though workers finish in any order.
- **Algorithm first:** the segmented sieve with C-level slice assignment is about 100× faster than trial division. Parallelism multiplies a good algorithm, it doesn't rescue a bad one (the starter would time out even with many cores).
- The driver's `__main__` guard is essential: with the spawn/forkserver start methods, workers re-import the main module.
