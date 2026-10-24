---
id: py-python-vs-c-division
title: Python vs C Division
difficulty: Medium
order: 2
tags: floor division, modulo, truncation
---
## Statement
Integers `a` and `b` (`b ≠ 0`, possibly negative) are given on one line. Print **two lines**:

1. Python's results: `a // b` and `a % b`, separated by a space
2. C's results for `a / b` and `a % b` on integers, separated by a space. C **truncates the quotient toward zero**, and its remainder satisfies `a == q*b + r`.

**Do not use floating point.** The values can be up to 10^30, beyond what a float represents exactly.

## Starter
```python
a, b = map(int, input().split())
```

## Tests
=== sample
7 2
---
3 1
3 1
=== sample
-7 2
---
-4 1
-3 -1
=== hidden
7 -2
---
-4 -1
-3 1
=== hidden
-7 -2
---
3 -1
3 -1
=== hidden
6 -3
---
-2 0
-2 0
=== hidden
0 5
---
0 0
0 0
=== hidden
-1000000000000000000000000000001 1000000000000000000000000000000
---
-2 999999999999999999999999999999
-1 -1
=== hidden
1 -1000000000000000000000000000000
---
-1 -999999999999999999999999999999
0 1

## Hints
- Truncation equals floor when the exact quotient is non-negative or when the division is exact.
- When signs differ and there is a remainder, the truncated quotient is the floor quotient **plus one**.
- Once you have the C quotient `q`, the C remainder is just `a - q*b`.

## Solution
Compute the floor quotient with `//`. C's truncated quotient differs from it exactly when the true quotient is negative and not an integer, i.e. the signs of `a` and `b` differ and `a % b != 0`. In that case the floor went one step further toward −∞ than truncation, so add one back.

```python
a, b = map(int, input().split())
fq, fr = a // b, a % b
print(fq, fr)

cq = fq
if fr != 0 and (a < 0) != (b < 0):
    cq += 1
cr = a - cq * b
print(cq, cr)
```

Using `int(a / b)` would also truncate toward zero, but `/` produces a float, and for 30-digit numbers the float has already lost digits. The two large hidden tests exist to catch that.
