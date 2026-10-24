---
id: py-single-number
title: Single Number
difficulty: Easy
order: 1
tags: xor, bit manipulation, leetcode-136
---
## Statement
Every number in a list appears **exactly twice** except one, which appears once. Find that one.

Your solution must use **O(1) extra memory**, so no sets, dicts or counting lists. One pass is enough.

Input: `n` (odd) on the first line, then `n` integers on the second line.

## Starter
```python
def single_number(nums):
    # return the element that appears once
    pass
```

## Driver
```python
n = int(input())
nums = list(map(int, input().split()))
print(single_number(nums))
```

## Tests
=== sample
5
4 1 2 1 2
---
4
=== sample
1
7
---
7
=== hidden
7
-3 9 -3 0 9 5 5
---
0
=== hidden
9
1000000000 -1 2 -1 2 1000000000 77 -50 -50
---
77
=== hidden
3
-8 -9 -9
---
-8

## Hints
- `x ^ x == 0` and `x ^ 0 == x`.
- XOR is commutative and associative, so order doesn't matter.

## Solution
XOR all the numbers. Every pair cancels (`a ^ a == 0`), the order doesn't matter (XOR is commutative and associative), and XOR with 0 changes nothing, so only the unpaired number is left.

```python
def single_number(nums):
    result = 0
    for x in nums:
        result ^= x
    return result
```

**Time** O(n), **space** O(1). Negative numbers work because Python XORs their two's-complement representations. A `Counter` solution is also O(n) time but uses O(n) memory, which is exactly what the constraint forbids. (LeetCode 136.)
