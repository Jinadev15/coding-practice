---
id: py-k-subset-sum
title: Subsets of Size k with Target Sum
difficulty: Medium
order: 2
tags: itertools.combinations, brute force, counting
---
## Statement
Given `n` integers (n ≤ 18), count how many **index subsets of size exactly `k`** have sum equal to `target`. Then print the **lexicographically smallest** such subset as values sorted ascending, or `none`.

Two subsets using different positions count separately even if their values are equal.

Input: `n k target`, then the numbers.

## Starter
```python
from itertools import combinations
n, k, target = map(int, input().split())
nums = list(map(int, input().split()))
```

## Tests
=== sample
5 2 5
1 2 3 4 0
---
2
1 4
=== sample
4 2 4
2 2 2 1
---
3
2 2
=== hidden
3 3 10
1 2 3
---
0
none
=== hidden
6 3 0
-1 0 1 2 -2 -1
---
4
-2 0 2
=== hidden
18 9 0
1 -1 2 -2 3 -3 4 -4 5 -5 6 -6 7 -7 8 -8 9 -9
=== hidden
1 1 7
7
---
1
7

## Hints
- `combinations(nums, k)` yields value tuples by position, so equal values at different positions count as different subsets.
- For the smallest one: sort each matching tuple and keep the minimum, since tuples compare lexicographically.
- C(18, 9) = 48,620 combinations. Brute force is fine.

## Solution
`combinations` enumerates every k-subset by position. Count the ones that hit the target, and keep the lexicographically smallest sorted tuple.

```python
from itertools import combinations
n, k, target = map(int, input().split())
nums = list(map(int, input().split()))
count, best = 0, None
for combo in combinations(nums, k):
    if sum(combo) == target:
        count += 1
        cand = tuple(sorted(combo))
        if best is None or cand < best:
            best = cand
print(count)
print(*best if best else ["none"])
```

With n = 18 this enumerates at most 2^18 subsets across all k. Beyond about n = 40, you'd use **meet-in-the-middle** (split in half, enumerate each half, and match sums with a hash map), which is O(2^(n/2)). That's a classic technique for hard subset-sum interview problems.
