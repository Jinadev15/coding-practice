---
id: py-is-rotation
title: String Rotation
difficulty: Easy
order: 1
tags: slicing, strings, leetcode-796
---
## Statement
String `b` is a **rotation** of `a` if you can move some prefix of `a` to its end and get `b`: `"waterbottle"` → `"erbottlewat"`.

For each of `t` lines containing `a b`, print the **smallest** shift `k` (0 ≤ k < len(a)) such that `a[k:] + a[:k] == b`, or `-1` if `b` is not a rotation. Both strings are non-empty.

## Starter
```python
t = int(input())
for _ in range(t):
    a, b = input().split()
```

## Tests
=== sample
3
waterbottle erbottlewat
abc abc
abc acb
---
3
0
-1
=== hidden
3
aaaa aaaa
abab baba
ab abc
---
0
1
-1
=== hidden
2
x x
rotation tionrota
---
0
4

## Hints
- Try every `k` and compare `a[k:] + a[:k]` with `b`. That's O(n²), fine for this input size.
- A neat test for *whether* it's a rotation: `len(a) == len(b) and b in a + a`. The index of `b` in `a + a` is the smallest shift.

## Solution
Every rotation of `a` appears as a substring of `a + a`. So `b` is a rotation exactly when the lengths match and `b` occurs in `a + a`, and the position of its first occurrence is the smallest shift.

```python
t = int(input())
for _ in range(t):
    a, b = input().split()
    if len(a) == len(b) and b in a + a:
        print((a + a).index(b))
    else:
        print(-1)
```

The length check matters: `"ab"` and `"abc"` would otherwise match, since `"abc"` isn't in `"abab"`, but `"a"` would be. The brute-force `for k in range(n): if a[k:] + a[:k] == b` is equivalent and shows the slicing more directly. (LeetCode 796.)
