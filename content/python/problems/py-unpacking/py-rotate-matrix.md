---
id: py-rotate-matrix
title: Rotate the Image
difficulty: Medium
order: 3
tags: zip, unpacking, matrices, leetcode-48
---
## Statement
Rotate an `n × n` matrix **90° clockwise** `k` times (`k` may be 0 and up to 10^9) and print the result.

```text
1 2 3        7 4 1
4 5 6   →    8 5 2
7 8 9        9 6 3
```

## Starter
```python
def rotate_cw(m):
    # return a NEW matrix rotated 90° clockwise
    pass
```

## Driver
```python
n, k = map(int, input().split())
m = [list(map(int, input().split())) for _ in range(n)]
for _ in range(k % 4):
    m = rotate_cw(m)
for row in m:
    print(*row)
```

## Tests
=== sample
3 1
1 2 3
4 5 6
7 8 9
---
7 4 1
8 5 2
9 6 3
=== sample
2 2
1 2
3 4
---
4 3
2 1
=== hidden
1 7
5
---
5
=== hidden
3 3
1 2 3
4 5 6
7 8 9
---
3 6 9
2 5 8
1 4 7
=== hidden
2 1000000000
1 2
3 4
---
1 2
3 4

## Hints
- Clockwise rotation = reverse the rows, then transpose.
- `zip(*rows)` transposes. `m[::-1]` reverses the row order.

## Solution
Reversing the row order and then transposing rotates the matrix clockwise. With `zip(*...)` the whole thing is one line. Each tuple from `zip` is converted back to a list.

```python
def rotate_cw(m):
    return [list(row) for row in zip(*m[::-1])]
```

Trace it: `m[::-1]` is `[[7,8,9],[4,5,6],[1,2,3]]`, and zipping the columns gives `(7,4,1)`, `(8,5,2)`, `(9,6,3)`. Four rotations are the identity, which is why the driver applies only `k % 4` of them. LeetCode 48 requires **in-place** rotation (transpose by swapping `m[i][j]` with `m[j][i]`, then reverse each row). Try that version too.
