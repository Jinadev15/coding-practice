---
id: py-swap-names
title: Swap Without a Temporary
difficulty: Easy
order: 1
tags: tuple unpacking, assignment
---
## Statement
Two words `a` and `b` are given on one line. Swap them **using tuple unpacking (no third variable)** and print `a` then `b` on one line, separated by a space.

## Starter
```python
a, b = input().split()
# swap here, in one line, without a temporary variable

print(a, b)
```

## Tests
=== sample
left right
---
right left
=== sample
x x
---
x x
=== hidden
Python C++
---
C++ Python
=== hidden
1 2
---
2 1

## Solution
The right-hand side `b, a` is evaluated into a tuple first, then unpacked into the names on the left.

```python
a, b = input().split()
a, b = b, a
print(a, b)
```

In C you need `int t = a; a = b; b = t;` (or XOR tricks for integers). Python's unpacking is the idiomatic swap.
