---
id: py-batched
title: Batched Generator
difficulty: Easy
order: 1
tags: generators, islice, streaming
---
## Statement
Write a **generator function** `batched(iterable, k)` that yields **tuples** of `k` consecutive items. The last batch may be shorter. It must work on **infinite** iterables, so it may never try to read everything.

The driver feeds it an infinite counter and takes only a few batches, then feeds it finite word lists.

## Starter
```python
from itertools import islice

def batched(iterable, k):
    pass
```

## Driver
```python
import itertools, inspect
assert inspect.isgeneratorfunction(batched), "batched must be a generator function (use yield)"
n, k = map(int, input().split())
print(list(itertools.islice(batched(itertools.count(1), k), n)))
words = input().split()
k2 = int(input())
print(list(batched(words, k2)))
```

## Tests
=== sample
2 3
a b c d e
2
---
[(1, 2, 3), (4, 5, 6)]
[('a', 'b'), ('c', 'd'), ('e',)]
=== hidden
1 1
x
5
---
[(1,)]
[('x',)]
=== hidden
3 4

1
---
[(1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12)]
[]

## Hints
- Turn the input into an iterator **once**: `it = iter(iterable)`.
- Loop: `batch = tuple(islice(it, k))`. If it's empty, stop (`return`); otherwise `yield batch`.

## Solution
`islice(it, k)` pulls at most `k` items from the shared iterator. An empty batch means the source is exhausted.

```python
from itertools import islice

def batched(iterable, k):
    it = iter(iterable)
    while True:
        batch = tuple(islice(it, k))
        if not batch:
            return
        yield batch
```

`iter(iterable)` must be outside the loop: calling `islice(iterable, k)` on a **list** each time would restart from the beginning forever. Python 3.12 added `itertools.batched` with exactly this behaviour. ML data loaders batch training samples the same way.
