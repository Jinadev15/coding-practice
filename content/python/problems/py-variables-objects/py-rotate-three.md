---
id: py-rotate-three
title: Rotate Three Names
difficulty: Easy
order: 2
tags: tuple unpacking, modulo
---
## Statement
Three integers `a b c` are on the first line and an integer `k` (0 ≤ k ≤ 10^18) is on the second.

One **left rotation** rebinds the names so that `a` gets `b`'s value, `b` gets `c`'s value and `c` gets `a`'s old value:

```text
(a, b, c) = (1, 2, 3)  →  (2, 3, 1)
```

Apply `k` left rotations and print `a b c`.

`k` can be astronomically large, so don't loop `k` times.

## Starter
```python
a, b, c = map(int, input().split())
k = int(input())
```

## Tests
=== sample
1 2 3
1
---
2 3 1
=== sample
1 2 3
2
---
3 1 2
=== hidden
1 2 3
0
---
1 2 3
=== hidden
7 8 9
3
---
7 8 9
=== hidden
5 -5 0
1000000000000000000
---
-5 0 5
=== hidden
4 4 9
999999999999999998
---
9 4 4

## Hints
- After 3 rotations you are back where you started.
- So only `k % 3` rotations matter.

## Solution
Rotations repeat with period 3, so reduce `k` modulo 3 and do at most two simultaneous rebindings.

```python
a, b, c = map(int, input().split())
k = int(input()) % 3
for _ in range(k):
    a, b, c = b, c, a
print(a, b, c)
```

`10^18 % 3 == 1` (since 10 ≡ 1 mod 3), so the third hidden test needs exactly one rotation. Reducing a huge repeat count modulo the cycle length is a pattern you'll use constantly in DSA.
