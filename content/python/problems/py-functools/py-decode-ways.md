---
id: py-decode-ways
title: Decode Ways
difficulty: Medium
order: 2
tags: memoization, functools.cache, dynamic programming, leetcode-91
---
## Statement
A message of letters A–Z is encoded as numbers: `A → 1`, …, `Z → 26`. Given a digit string, count the ways to decode it. For example, `"226"` → `BZ` (2,26), `VF` (22,6), `BBF` (2,2,6), so 3 ways.

A part may not have a leading zero (`"06"` is invalid), and `0` alone maps to nothing. Print the count modulo 10^9 + 7. Strings have length up to 500.

Write it **recursively** and memoize with `functools.cache`.

## Starter
```python
from functools import cache

def num_decodings(s):
    pass
```

## Driver
```python
for _ in range(int(input())):
    print(num_decodings(input().strip()))
```

## Tests
=== sample
4
12
226
06
10
---
2
3
0
1
=== hidden
4
0
27
11106
1111111111
---
0
1
2
89
=== hidden
1
1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

## Hints
- Let `ways(i)` = the number of decodings of the suffix `s[i:]`. `ways(len(s)) = 1` (the empty suffix).
- If `s[i] == "0"`, `ways(i) = 0`. Otherwise `ways(i) = ways(i + 1)`, plus `ways(i + 2)` if `s[i:i+2]` is between 10 and 26.
- Define the recursive helper **inside** `num_decodings` and decorate it with `@cache`, so each test gets a fresh cache.

## Solution
Each position chooses to read one digit or two. Without a memo, the "all ones" string explodes like Fibonacci. With `@cache` each suffix is solved once, so the whole thing is O(n).

```python
from functools import cache

MOD = 10**9 + 7

def num_decodings(s):
    @cache
    def ways(i):
        if i == len(s):
            return 1
        if s[i] == "0":
            return 0
        total = ways(i + 1)
        if i + 1 < len(s) and 10 <= int(s[i:i + 2]) <= 26:
            total += ways(i + 2)
        return total % MOD

    return ways(0)
```

`"1111111111"` (ten ones) has 89 decodings, the 11th Fibonacci number. With 500 ones the uncached recursion would need about 10^104 calls. The recursion depth is at most 500, below the limit of 1000. For longer inputs, convert to a bottom-up loop with two variables: O(n) time, O(1) space. (LeetCode 91.)
