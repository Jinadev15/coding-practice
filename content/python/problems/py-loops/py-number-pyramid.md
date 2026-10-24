---
id: py-number-pyramid
title: Number Pyramid
difficulty: Medium
order: 4
tags: nested loops, patterns, string building
---
## Statement
Given `n` (1 ≤ n ≤ 9), print a centred pyramid of `n` rows. Row `i` (1-based) has `n - i` leading spaces, then the digits counting **up** from 1 to `i`, then back **down** to 1, with no spaces between digits. **No trailing spaces.**

```text
n = 4
   1
  121
 12321
1234321
```

## Starter
```python
n = int(input())
```

## Tests
=== sample
4
---
   1
  121
 12321
1234321
=== hidden
1
---
1
=== hidden
2
---
 1
121
=== hidden
9
---
        1
       121
      12321
     1234321
    123454321
   12345654321
  1234567654321
 123456787654321
12345678987654321

## Hints
- Build each row as a string: spaces, then the rising digits, then the falling digits.
- Rising: `range(1, i + 1)`. Falling: `range(i - 1, 0, -1)`.
- The judge ignores trailing spaces, but it's good practice not to produce them.

## Solution
Each row is three pieces: padding, the ascending run and the descending run. Nested loops (or `join` over a range) build them.

```python
n = int(input())
for i in range(1, n + 1):
    row = " " * (n - i)
    for d in range(1, i + 1):
        row += str(d)
    for d in range(i - 1, 0, -1):
        row += str(d)
    print(row)
```

A compact version: `print(" " * (n - i) + "".join(map(str, range(1, i + 1))) + "".join(map(str, range(i - 1, 0, -1))))`. Pattern printing trains you to compute exact counts (here, `n - i` spaces and `2i - 1` digits), which is the same skill as getting array bounds right.
