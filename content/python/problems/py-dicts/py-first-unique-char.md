---
id: py-first-unique-char
title: First Unique Character
difficulty: Easy
order: 3
tags: counting, hash map, leetcode-387
---
## Statement
Return the index of the first character in `s` that appears **exactly once**, or `-1` if there is none. `s` has only lowercase letters and length up to 10^5, so O(n²) is too slow.

## Starter
```python
def first_uniq_char(s):
    pass
```

## Driver
```python
print(first_uniq_char(input().strip()))
```

## Tests
=== sample
leetcode
---
0
=== sample
loveleetcode
---
2
=== hidden
aabb
---
-1
=== hidden
z
---
0
=== hidden
aabbccddeeffg
---
12

## Hints
- First pass: count each character in a dict.
- Second pass: walk the **string** again and return the first index whose count is 1.

## Solution
Two linear passes: count everything, then find the first character whose count is 1 by walking the string in order.

```python
def first_uniq_char(s):
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    for i, ch in enumerate(s):
        if counts[ch] == 1:
            return i
    return -1
```

**Time** O(n), **space** O(1), because at most 26 distinct keys exist. The naive `s.count(ch) == 1` inside a loop is O(n²): each `count` call is itself a full scan.
