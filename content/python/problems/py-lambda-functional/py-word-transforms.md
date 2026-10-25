---
id: py-word-transforms
title: Word Transformations
difficulty: Easy
order: 2
tags: map, filter, reduce, lambda
---
## Statement
Given an integer `k` and a line of words, print four lines. Use `map`, `filter` and `reduce` (one for each part), not explicit loops:

1. the length of every word (space-separated)
2. the words with **more than** `k` letters, upper-cased (or `none`)
3. the longest word, using `reduce` (on ties, the **first** one)
4. the initials of all the words concatenated, upper-cased

## Starter
```python
from functools import reduce
k = int(input())
words = input().split()
```

## Tests
=== sample
4
the quick brown fox jumps
---
3 5 5 3 5
QUICK BROWN JUMPS
quick
TQBFJ
=== hidden
10
a bb ccc
---
1 2 3
none
ccc
ABC
=== hidden
0
solo
---
4
SOLO
solo
S

## Hints
- `map(len, words)` gives the lengths; `print(*iterable)` prints them separated by spaces.
- `filter(lambda w: len(w) > k, words)` keeps the long words; wrap it in `map(str.upper, ...)`.
- `functools.reduce(f, words)` folds the list pairwise: for the longest word, `f = lambda a, b: b if len(b) > len(a) else a` keeps the first one on ties.

## Solution
Each line is one functional tool: `map` transforms, `filter` selects, and `reduce` combines pairwise.

```python
from functools import reduce
k = int(input())
words = input().split()
print(*map(len, words))
long_words = list(map(str.upper, filter(lambda w: len(w) > k, words)))
print(*long_words if long_words else ["none"])
print(reduce(lambda a, b: b if len(b) > len(a) else a, words))
print(reduce(lambda acc, w: acc + w[0].upper(), words, ""))
```

The longest-word reducer keeps `a` unless `b` is **strictly** longer, which gives "first on ties". `str.upper` is an **unbound method** used as a plain function: `str.upper("x") == "X"`, so it can be passed to `map` directly with no lambda.
