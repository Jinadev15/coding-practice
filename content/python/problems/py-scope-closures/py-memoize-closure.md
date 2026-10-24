---
id: py-memoize-closure
title: Memoize with a Closure
difficulty: Medium
order: 2
tags: closures, caching, higher-order functions
---
## Statement
Write `memoize(func)` that returns a new function behaving like `func` (one hashable argument) but caching results in a dict held in the closure. The returned function must also expose a **`calls`** count: how many times the **original** `func` actually ran. Store it as an attribute on the wrapper: `wrapper.calls`.

The driver memoizes a slow recursive Fibonacci where the recursion goes **through the memoized name**, so caching turns exponential time into linear.

## Starter
```python
def memoize(func):
    pass
```

## Driver
```python
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

fib = memoize(fib)          # recursive calls now hit the cache
t = int(input())
for _ in range(t):
    n = int(input())
    print(fib(n), fib.calls)
```

## Tests
=== sample
2
10
10
---
55 11
55 11
=== hidden
3
1
30
35
---
1 1
832040 31
9227465 36
=== hidden
1
300
---
222232244629420445529739893461909967206666939096499764990979600 301

## Hints
- Keep `cache = {}` in `memoize`'s scope. The inner `wrapper(n)` checks the cache first.
- Functions are objects, so you can set `wrapper.calls = 0` and increment `wrapper.calls += 1` inside (no `nonlocal` needed, because that's an attribute mutation, not a rebinding).
- Why does `fib(300)` not hit the recursion limit? Each `fib(n)` first calls `fib(n-1)`, so the recursion depth is about 300, well under 1000.

## Solution
The cache dict lives in the closure. The wrapper consults it before calling the real function, and counts real calls on a function attribute.

```python
def memoize(func):
    cache = {}

    def wrapper(n):
        if n not in cache:
            wrapper.calls += 1
            cache[n] = func(n)
        return cache[n]

    wrapper.calls = 0
    return wrapper
```

Because the driver rebinds the global name `fib` to the wrapper, the recursive calls `fib(n - 1)` inside the original function look up the global `fib` (LEGB!) and go through the cache. Computing `fib(n)` then needs only n + 1 real calls instead of about 1.6ⁿ. This is exactly what `functools.lru_cache` / `functools.cache` do, plus thread safety and an optional size limit.
