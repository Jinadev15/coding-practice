---
id: py-rotate-array
title: Rotate Array
difficulty: Medium
order: 3
tags: arrays, reversal trick, leetcode-189
---
## Statement
Rotate the list `nums` to the **right** by `k` steps, **in place**. `k` may be larger than the list length.

```text
nums = [1, 2, 3, 4, 5, 6, 7], k = 3  →  [5, 6, 7, 1, 2, 3, 4]
```

Aim for O(n) time and O(1) extra space.

## Starter
```python
def rotate(nums, k):
    # modify nums in place
    pass
```

## Driver
```python
n, k = map(int, input().split())
nums = list(map(int, input().split()))
rotate(nums, k)
print(*nums)
```

## Tests
=== sample
7 3
1 2 3 4 5 6 7
---
5 6 7 1 2 3 4
=== sample
4 2
-1 -100 3 99
---
3 99 -1 -100
=== hidden
1 5
42
---
42
=== hidden
5 0
1 2 3 4 5
---
1 2 3 4 5
=== hidden
5 12
1 2 3 4 5
---
4 5 1 2 3
=== hidden
6 1000000000
1 2 3 4 5 6
---
3 4 5 6 1 2

## Hints
- Only `k % n` matters.
- Reversal trick: reverse the whole list, then reverse the first `k` elements, then reverse the rest.
- Write a helper `rev(nums, i, j)` that reverses `nums[i..j]` in place with two pointers.

## Solution
**Reversal trick:** reversing the whole array puts the last `k` elements at the front, but backwards. Reversing each of the two parts fixes their internal order.

```text
[1 2 3 4 5 6 7]  reverse all  → [7 6 5 4 3 2 1]
                 reverse 0..2 → [5 6 7 4 3 2 1]
                 reverse 3..6 → [5 6 7 1 2 3 4]
```

```python
def rotate(nums, k):
    n = len(nums)
    k %= n

    def rev(i, j):
        while i < j:
            nums[i], nums[j] = nums[j], nums[i]
            i += 1
            j -= 1

    rev(0, n - 1)
    rev(0, k - 1)
    rev(k, n - 1)
```

**Time** O(n), **space** O(1). The Pythonic one-liner `nums[:] = nums[-k:] + nums[:-k]` is also correct (with `k %= n` first; note that `k = 0` needs care because `nums[-0:]` is the whole list) but uses O(n) extra memory. Interviewers asking this question want the reversal trick.
