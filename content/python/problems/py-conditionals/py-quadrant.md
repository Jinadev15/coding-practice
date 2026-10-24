---
id: py-quadrant
title: Which Quadrant?
difficulty: Easy
order: 1
tags: if/elif/else, boundaries
---
## Statement
For each point `(x, y)` print where it lies:

- `origin` if both are 0
- `x-axis` if only `y` is 0, or `y-axis` if only `x` is 0
- otherwise `Q1`, `Q2`, `Q3` or `Q4` (counter-clockwise from the top right: Q1 has x>0, y>0; Q2 has x<0, y>0; and so on)

First line `t`, then `t` lines of `x y`.

## Starter
```python
t = int(input())
for _ in range(t):
    x, y = map(int, input().split())
```

## Tests
=== sample
5
3 4
-3 4
-3 -4
3 -4
0 0
---
Q1
Q2
Q3
Q4
origin
=== hidden
4
0 5
5 0
0 -1
-1 0
---
y-axis
x-axis
y-axis
x-axis
=== hidden
2
-1000000000 1
1 -1000000000
---
Q2
Q4

## Solution
Handle the special zero cases first (specific before general). After that, both coordinates are non-zero, so the signs pick the quadrant.

```python
t = int(input())
for _ in range(t):
    x, y = map(int, input().split())
    if x == 0 and y == 0:
        print("origin")
    elif y == 0:
        print("x-axis")
    elif x == 0:
        print("y-axis")
    elif x > 0:
        print("Q1" if y > 0 else "Q4")
    else:
        print("Q2" if y > 0 else "Q3")
```

Reaching `elif y == 0` already implies "not both zero", so it means "only y is 0". Each branch relies on the ones above it having failed.
