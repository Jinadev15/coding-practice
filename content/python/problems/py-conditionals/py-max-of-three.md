---
id: py-max-of-three
title: Median of Three
difficulty: Medium
order: 3
tags: comparisons, conditionals
---
## Statement
For each line of three integers `a b c`, print the **median**, the middle value. **Do not use** `sorted`, `sort`, `max`, `min` or lists. Use comparisons and conditionals only.

This is the "median-of-three" step that real quicksort implementations use to choose a pivot.

## Starter
```python
def median3(a, b, c):
    pass
```

## Driver
```python
t = int(input())
for _ in range(t):
    a, b, c = map(int, input().split())
    print(median3(a, b, c))
```

## Tests
=== sample
3
1 2 3
9 4 7
5 5 1
---
2
7
5
=== hidden
6
3 2 1
2 3 1
1 3 2
3 1 2
2 1 3
7 7 7
---
2
2
2
2
2
7
=== hidden
3
-5 0 5
100 -100 0
1 1 2
---
0
0
1

## Hints
- `b` is the median if `a ≤ b ≤ c` or `c ≤ b ≤ a`. Chained comparisons express that directly.
- Check `a` and `b` that way; if neither is the median, it must be `c`.

## Solution
A value is the median when it lies between the other two, in either order. Chained comparisons make each test read like the maths. If neither `a` nor `b` qualifies, `c` must be the median.

```python
def median3(a, b, c):
    if a <= b <= c or c <= b <= a:
        return b
    if b <= a <= c or c <= a <= b:
        return a
    return c
```

The hidden tests cover **all six orderings** of 1, 2, 3, plus duplicates. That's the standard way to test a comparison-based function exhaustively for three inputs.
