---
id: py-digit-stats
title: Digit Statistics
difficulty: Easy
order: 1
tags: integer arithmetic, % and //
---
## Statement
Read an integer `n` (it may be negative, and may have up to 1000 digits). Print three lines:

1. the number of digits of `|n|`
2. the sum of the digits of `|n|`
3. the last digit of `|n|`

`0` has one digit.

**Try it two ways:** with string operations, and with pure arithmetic (`% 10` and `// 10` in a loop). Both are accepted; the arithmetic version is what C forces you to write.

## Starter
```python
n = int(input())
```

## Tests
=== sample
12345
---
5
15
5
=== sample
-907
---
3
16
7
=== hidden
0
---
1
0
0
=== hidden
9
---
1
9
9
=== hidden
-1000000000000000000000000000000
---
31
1
0
=== hidden
99999999999999999999999999999999999999999999999999
---
50
450
9

## Hints
- Work with `abs(n)` so the sign doesn't get in the way.
- Arithmetic loop: `while m > 0: digit = m % 10; m //= 10`. What happens for `m == 0`?

## Solution
**String approach:** `str(abs(n))` gives the digits directly.

```python
n = abs(int(input()))
s = str(n)
print(len(s))
print(sum(int(ch) for ch in s))
print(n % 10)
```

**Arithmetic approach** (what you'd write in C), with zero handled separately:

```python
n = abs(int(input()))
count, total, m = 0, 0, n
while True:
    total += m % 10
    count += 1
    m //= 10
    if m == 0:
        break
print(count)
print(total)
print(n % 10)
```

The `while True ... break` loop is a do-while, so it runs at least once. That is exactly what makes `0` count as one digit. A plain `while m > 0` would report zero digits for `0`.
