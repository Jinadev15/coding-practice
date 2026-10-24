---
id: py-fast-power-mod
title: Fast Modular Exponentiation
difficulty: Medium
order: 4
tags: divide and conquer, recursion, number theory
---
## Statement
Compute `b^e mod m` for `0 ≤ b < 10^18`, `0 ≤ e ≤ 10^18`, `1 ≤ m ≤ 10^18` **recursively**, without `pow()` and without `**` on huge exponents.

Multiplying `b` by itself `e` times is impossible for `e = 10^18`. You need O(log e) multiplications.

## Starter
```python
def power_mod(b, e, m):
    pass
```

## Driver
```python
t = int(input())
for _ in range(t):
    b, e, m = map(int, input().split())
    print(power_mod(b, e, m))
```

## Tests
=== sample
3
2 10 1000
3 0 7
5 3 13
---
24
1
8
=== hidden
3
2 1000000000000000000 1000000007
123456789 987654321 1000000007
7 5 1
---
719476260
652541198
0
=== hidden
2
999999999999999999 999999999999999999 1000000000000000000
0 0 5
---
999999999999999999
1
## Hints
- If `e` is even, `b^e = (b^(e/2))²`. If odd, `b^e = (b^(e//2))² × b`.
- Reduce modulo `m` after **every** multiplication to keep the numbers small.
- What is `b^0 mod 1`? Everything mod 1 is 0.

## Solution
Recurse on `e // 2` once, square the result, and multiply in one extra `b` when `e` is odd. Reducing mod `m` at each step keeps the intermediate values below m², and the depth is about log₂(e) ≤ 60.

```python
def power_mod(b, e, m):
    if e == 0:
        return 1 % m
    half = power_mod(b, e // 2, m)
    result = half * half % m
    if e % 2:
        result = result * b % m
    return result
```

`1 % m` (rather than `1`) correctly gives 0 when m = 1. By convention `0^0 = 1`, which Python's `pow(0, 0, 5)` also returns. This algorithm (square-and-multiply) is the workhorse of RSA encryption, Diffie–Hellman and modular combinatorics in competitive programming. The expected outputs of the hidden tests are generated from this reference.
