---
id: py-largest-number
title: Largest Number
difficulty: Medium
order: 3
tags: sorting, cmp_to_key, greedy, leetcode-179
---
## Statement
Arrange a list of non-negative integers so that, concatenated, they form the **largest possible number**. Print it as a string, without leading zeros (all zeros → `0`).

```text
[3, 30, 34, 5, 9]  →  "9534330"
```

## Starter
```python
def largest_number(nums):
    # return a string
    pass
```

## Driver
```python
n = int(input())
nums = list(map(int, input().split()))
print(largest_number(nums))
```

## Tests
=== sample
5
3 30 34 5 9
---
9534330
=== sample
2
10 2
---
210
=== hidden
3
0 0 0
---
0
=== hidden
1
7
---
7
=== hidden
4
121 12 0 1
---
1212110
=== hidden
6
824 938 1399 5607 6973 5703
---
9388246973570356071399
=== hidden
2
432 43243
---
43243432

## Hints
- Sorting the strings descending fails: `"30" > "3"`, but `"3"` should come first, because `"330" > "303"`.
- Compare two strings `a`, `b` by checking which concatenation is bigger: `a + b` vs `b + a`. Use `functools.cmp_to_key`.
- Handle the all-zeros case.

## Solution
Put `a` before `b` exactly when `a + b > b + a`. This pairwise rule is a valid total order (it's transitive, which can be proved), so sorting with it gives the optimal arrangement.

```python
from functools import cmp_to_key

def largest_number(nums):
    strs = list(map(str, nums))

    def cmp(a, b):
        if a + b > b + a:
            return -1
        if a + b < b + a:
            return 1
        return 0

    strs.sort(key=cmp_to_key(cmp))
    result = "".join(strs)
    return "0" if result[0] == "0" else result
```

The ordering depends on **both** elements at once, so it can't be written as a plain key function. That's the textbook case for `cmp_to_key`. If the largest element starts with `0`, every number is 0, hence the special case. (LeetCode 179.)
