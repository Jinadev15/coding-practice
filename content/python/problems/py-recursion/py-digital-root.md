---
id: py-digital-root
title: Digital Root, Recursively
difficulty: Easy
order: 1
tags: recursion, digits
---
## Statement
The **digital root** of a non-negative integer is obtained by repeatedly summing its digits until one digit remains: `9875 → 29 → 11 → 2`.

Write **two recursive functions**, with no loops and no `str` conversion:

- `digit_sum(n)`: the sum of the digits of `n` (recursive on `n // 10`)
- `digital_root(n)`: built on `digit_sum`, recursing until `n < 10`

## Starter
```python
def digit_sum(n):
    pass

def digital_root(n):
    pass
```

## Driver
```python
t = int(input())
for _ in range(t):
    n = int(input())
    print(digit_sum(n), digital_root(n))
```

## Tests
=== sample
3
9875
0
7
---
29 2
0 0
7 7
=== hidden
3
10
999999999999
123456789123456789
---
1 1
108 9
90 9

## Hints
- `digit_sum(n) = n % 10 + digit_sum(n // 10)`, with base case `n < 10`.
- `digital_root(n) = n if n < 10 else digital_root(digit_sum(n))`.

## Solution
Each function peels off a piece of the problem: `digit_sum` takes one digit per call, and `digital_root` takes one summing round per call.

```python
def digit_sum(n):
    if n < 10:
        return n
    return n % 10 + digit_sum(n // 10)

def digital_root(n):
    if n < 10:
        return n
    return digital_root(digit_sum(n))
```

Number theory gives an O(1) shortcut: for n > 0 the digital root is `1 + (n - 1) % 9`, because 10 ≡ 1 (mod 9), so every number is congruent to its digit sum mod 9. The recursion depth here is at most the number of digits (18), so the recursion limit is never a concern.
