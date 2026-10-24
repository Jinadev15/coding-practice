---
id: py-water-and-pairs
title: Trapping Rain Water and Counting Pairs
difficulty: Hard
order: 1
tags: two pointers, sorting, invariants
---
## Statement
Implement three two-pointer algorithms, each in O(n) (after sorting, where noted) with O(1) extra space beyond the input/sort.

```python
def trap(heights):
    """Units of water trapped between bars of the given heights (elevation map)."""

def count_pairs_less(nums, target):
    """Number of index pairs i < j with nums[i] + nums[j] < target. You may sort a copy: O(n log n)."""

def three_sum_closest(nums, target):
    """The sum of three distinct-index elements closest to target; on ties, the SMALLER sum. len(nums) >= 3."""
```

Test lines are `(function_name, args)` literals or `gen NAME SEED N` for large inputs.

## Starter
```python
def trap(heights):
    total = 0
    for i in range(len(heights)):
        left = max(heights[:i + 1])
        right = max(heights[i:])
        total += min(left, right) - heights[i]
    return total

def count_pairs_less(nums, target):
    n = len(nums)
    return sum(1 for i in range(n) for j in range(i + 1, n) if nums[i] + nums[j] < target)

def three_sum_closest(nums, target):
    return sum(sorted(nums)[:3])
```

## Driver
```python
import ast
import random
import sys

FUNCS = {f.__name__: f for f in (trap, count_pairs_less, three_sum_closest)}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        if name == "trap":
            h = [rng.randrange(10000) for _ in range(n)]
            print(name, n, trap(h))
        elif name == "count_pairs_less":
            a = [rng.randrange(-10**6, 10**6) for _ in range(n)]
            print(name, n, count_pairs_less(a, 12345))
        elif name == "three_sum_closest":
            a = [rng.randrange(-10**5, 10**5) for _ in range(n)]
            print(name, n, three_sum_closest(a, 777777))
        continue
    name, args = ast.literal_eval(line)
    print(name, "->", FUNCS[name](*args))
```

## Tests
=== sample
("trap", ([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],))
("trap", ([4, 2, 0, 3, 2, 5],))
("count_pairs_less", ([-1, 1, 2, 3, 1], 2))
("three_sum_closest", ([-1, 2, 1, -4], 1))
---
trap -> 6
trap -> 9
count_pairs_less -> 3
three_sum_closest -> 2
=== hidden
("trap", ([],))
("trap", ([5],))
("trap", ([1, 2, 3, 4],))
("trap", ([4, 3, 2, 1],))
("trap", ([3, 0, 3, 0, 3],))
("count_pairs_less", ([], 0))
("count_pairs_less", ([5, 5, 5], 10))
("count_pairs_less", ([5, 5, 5], 11))
("three_sum_closest", ([0, 0, 0], 1))
("three_sum_closest", ([1, 1, 1, 0], -100))
("three_sum_closest", ([1, 2, 4, 8, 16], 10))
("three_sum_closest", ([-3, -1, 1, 3], 0))
---
trap -> 0
trap -> 0
trap -> 0
trap -> 0
trap -> 6
count_pairs_less -> 0
count_pairs_less -> 0
count_pairs_less -> 3
three_sum_closest -> 0
three_sum_closest -> 2
three_sum_closest -> 11
three_sum_closest -> -1
=== hidden
gen trap 1 300000
gen count_pairs_less 2 200000
gen three_sum_closest 3 1000
---
trap 300000 1499150798
count_pairs_less 200000 10100793818
three_sum_closest 1000 297662

## Hints
- **trap**: keep `l`, `r`, `left_max` and `right_max`. Always advance the side with the smaller max: the water above that bar is fully determined by its own side's max, because the other side has a wall at least as high.
- **count_pairs_less**: sort. If `a[i] + a[j] < target`, then every j' in `(i, j]` also works with i. Add `j - i` and move i right; otherwise move j left.
- **three_sum_closest**: sort, then anchor k with two pointers on the rest. Compare by `(abs(s - target), s)` so ties prefer the smaller sum.

## Solution
```python
def trap(heights):
    l, r = 0, len(heights) - 1
    left_max = right_max = water = 0
    while l < r:
        if heights[l] <= heights[r]:          # the left side is the bottleneck
            left_max = max(left_max, heights[l])
            water += left_max - heights[l]
            l += 1
        else:
            right_max = max(right_max, heights[r])
            water += right_max - heights[r]
            r -= 1
    return water

def count_pairs_less(nums, target):
    a = sorted(nums)
    i, j, count = 0, len(a) - 1, 0
    while i < j:
        if a[i] + a[j] < target:
            count += j - i                     # a[i] pairs with every index in (i, j]
            i += 1
        else:
            j -= 1
    return count

def three_sum_closest(nums, target):
    a = sorted(nums)
    best = a[0] + a[1] + a[2]
    for k in range(len(a) - 2):
        i, j = k + 1, len(a) - 1
        while i < j:
            s = a[k] + a[i] + a[j]
            if (abs(s - target), s) < (abs(best - target), best):
                best = s
            if s == target:
                return s
            if s < target:
                i += 1
            else:
                j -= 1
    return best
```

Each algorithm rests on a **discard argument**:
- **trap**: when `heights[l] <= heights[r]`, the right side already has a bar at least as tall as `heights[l]`. So the water level at `l` is limited only by `left_max`, and it can be settled immediately. That's O(n) time, O(1) space.
- **count_pairs_less**: in sorted order, a successful pair `(i, j)` implies success for every smaller partner of i, so `j − i` pairs are counted at once.
- **three_sum_closest**: for a fixed anchor, moving the pointers inwards explores every sum that could improve the answer, giving O(n²) total. The tuple comparison `(distance, sum)` encodes the tie-break rule in one expression.
