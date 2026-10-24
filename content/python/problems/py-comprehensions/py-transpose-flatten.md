---
id: py-transpose-flatten
title: Transpose and Flatten
difficulty: Easy
order: 1
tags: comprehensions, matrices
---
## Statement
Given an `r × c` matrix, print:

1. its **transpose** (`c × r`), one row per line
2. then a line with all of the original matrix's elements **flattened** row by row, keeping only the **even** ones (print `none` if there are no even elements)

Write each part as a single comprehension.

## Starter
```python
r, c = map(int, input().split())
m = [list(map(int, input().split())) for _ in range(r)]
```

## Tests
=== sample
2 3
1 2 3
4 5 6
---
1 4
2 5
3 6
2 4 6
=== hidden
1 1
7
---
7
none
=== hidden
3 2
2 4
6 8
1 3
---
2 6 1
4 8 3
2 4 6 8
=== hidden
1 4
-2 -1 0 1
---
-2
-1
0
1
-2 0

## Hints
- Transpose: `[[m[i][j] for i in range(r)] for j in range(c)]`, or `[list(col) for col in zip(*m)]`.
- Flatten and filter: `[x for row in m for x in row if x % 2 == 0]`.

## Solution
The transpose is a **nested** comprehension (an inner one per output row). The flatten is a **two-clause** comprehension with a filter. The difference between those two shapes is the lesson.

```python
r, c = map(int, input().split())
m = [list(map(int, input().split())) for _ in range(r)]
t = [[m[i][j] for i in range(r)] for j in range(c)]
for row in t:
    print(*row)
evens = [x for row in m for x in row if x % 2 == 0]
print(*evens if evens else ["none"])
```

`zip(*m)` unpacks the rows as separate arguments to `zip`, which pairs up their first elements, then their second, and so on. That's the transpose in one call. `0` is even (`0 % 2 == 0`), and so is `-2`.
