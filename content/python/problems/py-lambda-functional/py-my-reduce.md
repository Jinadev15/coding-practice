---
id: py-my-reduce
title: Implement reduce
difficulty: Medium
order: 3
tags: higher-order functions, iterators, edge cases
---
## Statement
Implement `my_reduce(func, iterable, *initial)` with exactly the semantics of `functools.reduce`, without importing it:

- With an initial value: fold starting from it.
- Without one: the first item is the starting accumulator.
- An empty iterable with no initial value raises `TypeError`.
- `iterable` may be **any iterable**, including a one-shot generator, so don't index it or call `len` on it.

The driver runs named operations and prints the results (or `TypeError`).

## Starter
```python
def my_reduce(func, iterable, *initial):
    pass
```

## Driver
```python
ops = {
    "sum": lambda a, b: a + b,
    "max": lambda a, b: a if a >= b else b,
    "digits": lambda a, b: a * 10 + b,
    "list": lambda a, b: a + [b],
}
t = int(input())
for _ in range(t):
    parts = input().split()
    op, rest = parts[0], parts[1:]
    if "|" in rest:
        i = rest.index("|")
        items, init = rest[:i], rest[i + 1:]
        init_val = [] if op == "list" else int(init[0])
        gen = (int(x) for x in items)          # a one-shot generator
        args = (init_val,)
    else:
        gen = (int(x) for x in rest)
        args = ()
    try:
        print(my_reduce(ops[op], gen, *args))
    except TypeError:
        print("TypeError")
```

## Tests
=== sample
4
sum 1 2 3 4
digits 4 0 2
sum | 100
max
---
10
402
100
TypeError
=== hidden
4
list 1 2 3 | x
max 7
sum 5 | 10
digits 9 9 | 1
---
[1, 2, 3]
7
15
199
=== hidden
2
max -5 -2 -9
list | x
---
-2
[]

## Hints
- Get an iterator with `it = iter(iterable)`.
- No initial value: take the first element with `next(it)`. An empty iterator raises `StopIteration`, which you must convert into `TypeError`.
- Then loop over the **rest** of the same iterator.

## Solution
Work through an explicit iterator so it works on any iterable, including generators. `next(it, sentinel)` detects emptiness without catching an exception.

```python
def my_reduce(func, iterable, *initial):
    it = iter(iterable)
    if initial:
        acc = initial[0]
    else:
        sentinel = object()
        acc = next(it, sentinel)
        if acc is sentinel:
            raise TypeError("reduce() of empty iterable with no initial value")
    for item in it:
        acc = func(acc, item)
    return acc
```

`object()` creates a unique sentinel that can't be confused with any real element, even `None` or `0`. That's a standard idiom. Using `iterable[0]` would fail on generators, which have no indexing, and the driver deliberately passes generators to catch exactly that.
