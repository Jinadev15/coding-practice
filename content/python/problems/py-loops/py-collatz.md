---
id: py-collatz
title: Collatz Journey
difficulty: Easy
order: 2
tags: while loop, simulation
---
## Statement
The **Collatz** rule: if `n` is even, `n → n / 2`; if odd, `n → 3n + 1`. The (unproven!) conjecture says every positive start reaches 1.

For each starting value, print two numbers: the **number of steps** to reach 1, and the **largest value** reached along the way, including the start.

First line `t`, then `t` lines with `n` (1 ≤ n ≤ 10^6).

## Starter
```python
t = int(input())
for _ in range(t):
    n = int(input())
```

## Tests
=== sample
3
6
1
7
---
8 16
0 1
16 52
=== hidden
3
27
97
2
---
111 9232
118 9232
1 2
=== hidden
2
837799
1000000
---
524 2974984576
152 1000000

## Hints
- You don't know how many steps there will be, so use `while n != 1`.
- Use `//` to halve, so `n` stays an `int`.

## Solution
A `while` loop fits because the iteration count is unknown in advance. Track the step count and running maximum as you go.

```python
t = int(input())
for _ in range(t):
    n = int(input())
    steps, peak = 0, n
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
        if n > peak:
            peak = n
    print(steps, peak)
```

837799 is the start below one million with the longest chain (524 steps, Project Euler 14). Its peak, 2,974,984,576, would overflow a 32-bit signed int in C. That's worth remembering when you solve this in C later.
