---
id: py-sign-counts
title: Sign Counts
difficulty: Easy
order: 2
tags: bool as int, sum, generator expressions
---
## Statement
Read `n` and then `n` integers on one line. Print three numbers on one line: how many are **positive**, how many are **negative** and how many are **zero**.

Use the fact that `True == 1`: `sum(x > 0 for x in nums)` counts the positives.

## Starter
```python
n = int(input())
nums = list(map(int, input().split()))
```

## Tests
=== sample
6
3 -1 0 0 8 -5
---
2 2 2
=== hidden
1
0
---
0 0 1
=== hidden
5
-1 -2 -3 -4 -5
---
0 5 0
=== hidden
4
1000000000 1 2 3
---
4 0 0

## Hints
- Read the numbers with `list(map(int, input().split()))`.
- A comparison like `x > 0` is a `bool`, and `True` counts as 1, so `sum(x > 0 for x in nums)` counts the positives.
- Zeros don't need their own loop: `zeros = n - positives - negatives`.

## Solution
Each comparison produces a `bool`, and `sum` treats `True` as 1 and `False` as 0.

```python
n = int(input())
nums = list(map(int, input().split()))
pos = sum(x > 0 for x in nums)
neg = sum(x < 0 for x in nums)
print(pos, neg, n - pos - neg)
```

The zero count follows by subtraction, which saves a third pass.
