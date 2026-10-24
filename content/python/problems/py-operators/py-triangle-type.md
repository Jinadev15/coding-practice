---
id: py-triangle-type
title: Triangle Classifier
difficulty: Easy
order: 3
tags: chained comparisons, logical operators
---
## Statement
For each of `t` lines with three positive integers `a b c` (side lengths), print:

- `invalid` if they cannot form a triangle with positive area (some side is ≥ the sum of the other two)
- otherwise `equilateral` (all equal), `isosceles` (exactly two equal) or `scalene` (all different)

Use **chained comparisons** where they make the code clearer (`a == b == c`).

## Starter
```python
t = int(input())
for _ in range(t):
    a, b, c = map(int, input().split())
```

## Tests
=== sample
4
3 3 3
3 4 5
2 2 3
1 2 3
---
equilateral
scalene
isosceles
invalid
=== hidden
3
10 1 1
5 5 9
5 9 5
---
invalid
isosceles
isosceles
=== hidden
3
1000000000000 1000000000000 1000000000000
7 10 5
1 1 2
---
equilateral
scalene
invalid
=== hidden
2
2 3 4
4 4 7
---
scalene
isosceles

## Hints
- Sort the sides first. Then only one inequality matters: `x + y > z` where `z` is the largest.
- "Exactly two equal" means at least two are equal but not all three, so check equilateral first.

## Solution
After sorting, `x ≤ y ≤ z`, and the triangle inequality reduces to `x + y > z`. A degenerate "triangle" like 1 2 3 (zero area) is invalid. Then classify, testing the most specific case first.

```python
t = int(input())
for _ in range(t):
    x, y, z = sorted(map(int, input().split()))
    if x + y <= z:
        print("invalid")
    elif x == y == z:
        print("equilateral")
    elif x == y or y == z:
        print("isosceles")
    else:
        print("scalene")
```

Once the sides are sorted, equal sides must be adjacent, so `x == y or y == z` covers every isosceles case. `x == y == z` is a chained comparison meaning `x == y and y == z`.
