---
id: py-sum-two-lines
title: Sum of Two Lines
difficulty: Easy
order: 2
tags: stdin, int conversion
---
## Statement
Read two integers `a` and `b`, **each on its own line**, and print their sum.

The numbers can be very large (up to 100 digits) or negative. Python integers have arbitrary precision, so no special handling is needed.

**Constraints**
- `-10^100 <= a, b <= 10^100`

## Starter
```python
a = input()
b = input()
# input() always returns a str. Convert, add, print.
```

## Tests
=== sample
3
4
---
7
=== sample
-10
25
---
15
=== hidden
0
0
---
0
=== hidden
99999999999999999999999999999999999999
1
---
100000000000000000000000000000000000000
=== hidden
-5
-7
---
-12
=== hidden
123456789012345678901234567890
-123456789012345678901234567890
---
0

## Hints
- `input()` returns text. `"3" + "4"` is `"34"`.
- `int("  42 ")` tolerates surrounding whitespace.

## Solution
`input()` reads one line from stdin **as a string**, without the trailing newline. Adding two strings concatenates them, so you must convert with `int()` first.

```python
a = int(input())
b = int(input())
print(a + b)
```

Python's `int` grows to any size (it is a *bignum*), so the 100-digit test passes without overflow. In C or C++ you would need a big-integer library or string arithmetic for this.

**Complexity:** O(d) where d is the number of digits.
