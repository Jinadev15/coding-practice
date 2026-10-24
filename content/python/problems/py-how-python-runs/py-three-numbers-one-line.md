---
id: py-three-numbers-one-line
title: Three Numbers, One Line
difficulty: Easy
order: 3
tags: stdin, split, map
---
## Statement
The input is a **single line** containing three integers separated by spaces. Print three lines:

1. their sum
2. their product
3. the largest of them

## Starter
```python
line = input()
```

## Tests
=== sample
1 2 3
---
6
6
3
=== sample
-4 10 2
---
8
-80
10
=== hidden
0 0 0
---
0
0
0
=== hidden
-1 -2 -3
---
-6
-6
-1
=== hidden
1000000 1000000 1000000
---
3000000
1000000000000000000
1000000
=== hidden
7   -7    7
---
7
-343
7

## Hints
- `"1 2 3".split()` gives `['1', '2', '3']`. `split()` with no argument also collapses repeated spaces.
- `map(int, ...)` converts every item; you can unpack it: `a, b, c = map(int, input().split())`.

## Solution
`str.split()` with **no argument** splits on any run of whitespace and ignores leading and trailing spaces, so it handles the hidden test with irregular spacing. (`split(" ")` would produce empty strings there and crash `int()`.)

```python
a, b, c = map(int, input().split())
print(a + b + c)
print(a * b * c)
print(max(a, b, c))
```

`map(int, ...)` applies `int` to each piece lazily, and the unpacking `a, b, c = ...` demands exactly three values. A different count raises `ValueError`, which is a useful safety check.
