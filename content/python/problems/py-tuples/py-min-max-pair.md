---
id: py-min-max-pair
title: Min and Max in One Pass
difficulty: Easy
order: 1
tags: tuples, returning multiple values
---
## Statement
Write `min_max(nums)` that returns a **tuple** `(smallest, largest)` in a **single pass**, without using `min`, `max` or `sorted`. The list is non-empty.

The driver unpacks your tuple: `lo, hi = min_max(nums)`.

## Starter
```python
def min_max(nums):
    pass
```

## Driver
```python
n = int(input())
nums = list(map(int, input().split()))
result = min_max(nums)
assert isinstance(result, tuple), "return a tuple"
lo, hi = result
print(lo, hi)
```

## Tests
=== sample
5
3 9 -2 7 0
---
-2 9
=== hidden
1
42
---
42 42
=== hidden
4
-5 -5 -5 -5
---
-5 -5
=== hidden
6
1000000000000 -1000000000000 3 4 5 6
---
-1000000000000 1000000000000

## Solution
Start both trackers at the first element (never at 0, which might not be in the list), then update them as you scan.

```python
def min_max(nums):
    lo = hi = nums[0]
    for x in nums[1:]:
        if x < lo:
            lo = x
        elif x > hi:
            hi = x
    return lo, hi
```

`return lo, hi` packs a tuple. The `elif` is safe because a value can't be both a new minimum and a new maximum, unless it's the first element, which initialises both. (A tournament method does about 1.5n comparisons instead of 2n. That's a classic algorithms exam question.)
