---
id: py-file-tail
title: Tail of a Huge File
difficulty: Medium
order: 2
tags: files, deque, streaming
---
## Statement
Implement `tail(path, n)`, which returns the **last `n` lines** of a text file as a list of strings without newlines, like Unix `tail -n`. Files can be large, so keep only O(n) lines in memory. Don't use `readlines()` or `read()`.

The driver generates a file of `m` numbered lines and queries several `n`.

## Starter
```python
from collections import deque

def tail(path, n):
    pass
```

## Driver
```python
m, q = map(int, input().split())
with open("big.txt", "w", encoding="utf-8") as f:
    for i in range(1, m + 1):
        f.write(f"line {i}\n")
for _ in range(q):
    n = int(input())
    print(tail("big.txt", n))
```

## Tests
=== sample
5 3
2
0
10
---
['line 4', 'line 5']
[]
['line 1', 'line 2', 'line 3', 'line 4', 'line 5']
=== hidden
1000000 2
3
1
---
['line 999998', 'line 999999', 'line 1000000']
['line 1000000']

## Hints
- `deque(iterable, maxlen=n)` keeps only the last `n` items it was fed.
- `n == 0` should return `[]`. `deque(..., maxlen=0)` stays empty.

## Solution
A bounded deque streams the file and automatically drops old lines, so memory stays O(n) however large the file is.

```python
from collections import deque

def tail(path, n):
    with open(path, encoding="utf-8") as f:
        return [line.rstrip("\n") for line in deque(f, maxlen=n)]
```

This still reads the whole file (O(file size) time). The real `tail` is faster: it `seek`s to the end in **binary** mode and reads backwards block by block until it has counted `n` newlines. Try that version too.
