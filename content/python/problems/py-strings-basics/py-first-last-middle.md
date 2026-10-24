---
id: py-first-last-middle
title: First, Last and Middle
difficulty: Easy
order: 1
tags: indexing, len, slicing
---
## Statement
Read a word `s` of length at least 1. Print three lines:

1. its first character
2. its last character
3. its **middle**: the single middle character if the length is odd, or the two middle characters if it is even

## Starter
```python
s = input().strip()
```

## Tests
=== sample
python
---
p
n
th
=== sample
level
---
l
l
v
=== hidden
a
---
a
a
a
=== hidden
ab
---
a
b
ab
=== hidden
abcdefghij
---
a
j
ef

## Hints
- Length 6 → middle indices are 2 and 3. Length 5 → index 2.
- `len(s) // 2` is useful in both cases.

## Solution
Let `n = len(s)` and `m = n // 2`. For odd `n` the middle is `s[m]`. For even `n` it's the slice `s[m-1:m+1]` (indices `m-1` and `m`).

```python
s = input().strip()
n = len(s)
m = n // 2
print(s[0])
print(s[-1])
if n % 2 == 1:
    print(s[m])
else:
    print(s[m - 1:m + 1])
```

Check "python": n = 6, m = 3, and `s[2:4]` is `"th"`.
