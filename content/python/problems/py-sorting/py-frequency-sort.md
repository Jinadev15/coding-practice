---
id: py-frequency-sort
title: Sort by Frequency
difficulty: Easy
order: 1
tags: sorting, key function, counting, leetcode-1636
---
## Statement
Sort the integers in **increasing order of frequency**. Values with the same frequency go in **decreasing** order of value.

```text
[1, 1, 2, 2, 2, 3]  →  [3, 1, 1, 2, 2, 2]
```

## Starter
```python
def frequency_sort(nums):
    pass
```

## Driver
```python
n = int(input())
nums = list(map(int, input().split()))
print(*frequency_sort(nums))
```

## Tests
=== sample
6
1 1 2 2 2 3
---
3 1 1 2 2 2
=== sample
5
2 3 1 3 2
---
1 3 3 2 2
=== hidden
1
-7
---
-7
=== hidden
8
-1 1 -6 4 5 -6 1 4
---
5 -1 4 4 1 1 -6 -6
=== hidden
4
9 9 9 9
---
9 9 9 9

## Hints
- Count first (a dict).
- Then sort the **original list** with the key `(count[x], -x)`.

## Solution
Count the occurrences, then use a two-part key: frequency ascending, and the negated value to get descending order among ties.

```python
def frequency_sort(nums):
    count = {}
    for x in nums:
        count[x] = count.get(x, 0) + 1
    return sorted(nums, key=lambda x: (count[x], -x))
```

**Time** O(n log n). Negating `x` turns "value descending" into an ascending key component, the standard trick for mixing directions with numeric keys. (LeetCode 1636.)
