---
id: py-spiral-matrix
title: Spiral Order
difficulty: Medium
order: 4
tags: 2D lists, simulation, boundaries, leetcode-54
---
## Statement
Given an `r × c` matrix, return its elements in **clockwise spiral order**, starting at the top-left.

```text
1 2 3
4 5 6      →  1 2 3 6 9 8 7 4 5
7 8 9
```

## Starter
```python
def spiral_order(matrix):
    # return a list
    pass
```

## Driver
```python
r, c = map(int, input().split())
matrix = [list(map(int, input().split())) for _ in range(r)]
print(*spiral_order(matrix))
```

## Tests
=== sample
3 3
1 2 3
4 5 6
7 8 9
---
1 2 3 6 9 8 7 4 5
=== sample
3 4
1 2 3 4
5 6 7 8
9 10 11 12
---
1 2 3 4 8 12 11 10 9 5 6 7
=== hidden
1 1
5
---
5
=== hidden
1 4
1 2 3 4
---
1 2 3 4
=== hidden
4 1
1
2
3
4
---
1 2 3 4
=== hidden
2 3
1 2 3
4 5 6
---
1 2 3 6 5 4
=== hidden
4 4
1 2 3 4
5 6 7 8
9 10 11 12
13 14 15 16
---
1 2 3 4 8 12 16 15 14 13 9 5 6 7 11 10

## Hints
- Keep four boundaries: `top`, `bottom`, `left`, `right`.
- Walk the top row left→right, then `top += 1`; the right column top→bottom, then `right -= 1`; and so on.
- After moving the top and right boundaries, re-check `top <= bottom` and `left <= right` before walking the bottom row and left column. Single rows and columns break naive code.

## Solution
Peel the matrix layer by layer with four shrinking boundaries. The guards before the third and fourth walks stop a single remaining row or column from being visited twice.

```python
def spiral_order(matrix):
    res = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    while top <= bottom and left <= right:
        for j in range(left, right + 1):
            res.append(matrix[top][j])
        top += 1
        for i in range(top, bottom + 1):
            res.append(matrix[i][right])
        right -= 1
        if top <= bottom:
            for j in range(right, left - 1, -1):
                res.append(matrix[bottom][j])
            bottom -= 1
        if left <= right:
            for i in range(bottom, top - 1, -1):
                res.append(matrix[i][left])
            left += 1
    return res
```

**Time** O(r·c), each element visited once. **Space** O(1) besides the output. The `1 × 4`, `4 × 1` and `2 × 3` hidden tests exist precisely to catch a missing guard.
