---
id: py-hanoi
title: Towers of Hanoi
difficulty: Medium
order: 2
tags: recursion, divide and conquer, recurrences
---
## Statement
Move `n` disks from peg `A` to peg `C`, using `B` as a spare. Only one disk moves at a time, and a larger disk may never sit on a smaller one.

- If `n ≤ 12`: print every move as `A C` (from, to), in order, then the move count.
- If `n > 12` (up to 10^5): print only the total number of moves **modulo 10^9 + 7**.

Your recursive move generator must produce the **optimal** (minimum) sequence.

## Starter
```python
def hanoi(n, src, via, dst, moves):
    # append (src, dst) pairs to moves
    pass
```

## Driver
```python
n = int(input())
if n <= 12:
    moves = []
    hanoi(n, "A", "B", "C", moves)
    for a, b in moves:
        print(a, b)
    print(len(moves))
else:
    print((pow(2, n, 10**9 + 7) - 1) % (10**9 + 7))
```

## Tests
=== sample
2
---
A B
A C
B C
3
=== sample
3
---
A C
A B
C B
A C
B A
B C
A C
7
=== hidden
1
---
A C
1
=== hidden
0
---
0
=== hidden
12
=== hidden
100000

## Hints
- To move `n` disks from `src` to `dst`: move `n − 1` from `src` to `via`, move the largest disk, then move `n − 1` from `via` to `dst`.
- The base case is `n == 0`: nothing to move.

## Solution
The largest disk has to move from `src` to `dst` exactly once, and at that moment the other `n − 1` disks must all be on `via`. That forces the recursive structure.

```python
def hanoi(n, src, via, dst, moves):
    if n == 0:
        return
    hanoi(n - 1, src, dst, via, moves)
    moves.append((src, dst))
    hanoi(n - 1, via, src, dst, moves)
```

The move count satisfies T(n) = 2·T(n−1) + 1, T(0) = 0, so T(n) = 2ⁿ − 1. That's provably optimal, and it's why the driver uses modular exponentiation for huge `n`: 2^100000 has about 30,000 digits. The recursion depth is only `n` (≤ 12 here) even though the number of calls is exponential.
