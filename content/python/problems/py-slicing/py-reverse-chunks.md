---
id: py-reverse-chunks
title: Reverse in Chunks
difficulty: Easy
order: 2
tags: slicing, step, leetcode-541
---
## Statement
Given a string `s` and an integer `k`, reverse the first `k` characters of every block of `2k` characters, counting from the start.

- If fewer than `k` characters remain, reverse all of them.
- If between `k` and `2k` remain, reverse the first `k` and leave the rest as they are.

```text
s = "abcdefg", k = 2  →  "bacdfeg"
blocks: [ab|cd] [ef|g]  → reverse "ab"→"ba", "ef"→"fe"
```

Input: `s` on the first line, `k` on the second.

## Starter
```python
def reverse_str(s, k):
    pass
```

## Driver
```python
s = input().strip()
k = int(input())
print(reverse_str(s, k))
```

## Tests
=== sample
abcdefg
2
---
bacdfeg
=== sample
abcd
2
---
bacd
=== hidden
a
5
---
a
=== hidden
abcdefgh
3
---
cbadefhg
=== hidden
abcdef
1
---
abcdef
=== hidden
abcdefghij
10
---
jihgfedcba

## Hints
- Loop `i` over `range(0, len(s), 2 * k)`.
- Each block contributes `s[i:i+k][::-1] + s[i+k:i+2*k]`. Slices clip at the end automatically, so the edge cases need no special code.

## Solution
Walk the string in steps of `2k`. In each block, reverse the first `k` characters with a slice and keep the next `k`. Slice clipping handles short final blocks for free.

```python
def reverse_str(s, k):
    parts = []
    for i in range(0, len(s), 2 * k):
        parts.append(s[i:i + k][::-1])
        parts.append(s[i + k:i + 2 * k])
    return "".join(parts)
```

`s[i:i+k][::-1]` (slice, then reverse) is much clearer than one negative-step slice like `s[i+k-1:i-1:-1]`, which also **breaks at i = 0**: `s[k-1:-1:-1]` is empty, because `-1` means the last index. Prefer two simple slices over one clever one. (LeetCode 541.)
