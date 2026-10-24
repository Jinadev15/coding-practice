---
id: py-move-zeroes
title: Move Zeroes
difficulty: Easy
order: 2
tags: two pointers, in-place, leetcode-283
---
## Statement
Given a list `nums`, move all `0`s to the end **in place** while keeping the relative order of the non-zero elements.

You must modify the list itself (the driver prints the same list object afterwards) and use O(1) extra space. Don't create a new list.

```text
[0, 1, 0, 3, 12]  →  [1, 3, 12, 0, 0]
```

## Starter
```python
def move_zeroes(nums):
    # modify nums in place; return nothing
    pass
```

## Driver
```python
n = int(input())
nums = list(map(int, input().split())) if n else []
ret = move_zeroes(nums)
print(*nums)
```

## Tests
=== sample
5
0 1 0 3 12
---
1 3 12 0 0
=== sample
1
0
---
0
=== hidden
6
4 2 4 0 0 3
---
4 2 4 3 0 0
=== hidden
4
0 0 0 1
---
1 0 0 0
=== hidden
3
1 2 3
---
1 2 3
=== hidden
8
-1 0 0 -2 0 5 0 -3
---
-1 -2 5 -3 0 0 0 0

## Hints
- Keep a write pointer `w`: the next position where a non-zero element should go.
- Scan with `r`. Whenever `nums[r] != 0`, swap `nums[w]` and `nums[r]`, then advance `w`.

## Solution
A **two-pointer** pass. `w` marks the boundary of the processed non-zero prefix. Every non-zero value found by `r` is swapped down to `w`, so the order of the non-zeros is preserved and the zeros drift to the end.

```python
def move_zeroes(nums):
    w = 0
    for r in range(len(nums)):
        if nums[r] != 0:
            nums[w], nums[r] = nums[r], nums[w]
            w += 1
```

**Time** O(n), **space** O(1). A tempting wrong answer is `nums = [x for x in nums if x] + [0] * k`. That **rebinds the local name** `nums` to a new list, and the caller's list is untouched. This is the same rebind-vs-mutate distinction from the Variables lesson. (`nums[:] = ...` would mutate in place, but it uses O(n) extra space.)
