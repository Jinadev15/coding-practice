---
id: py-palindrome-check
title: Palindrome Check
difficulty: Easy
order: 2
tags: strings, reversal
---
## Statement
A phrase is a **palindrome** if it reads the same forwards and backwards **after removing every non-letter character and ignoring case**.

The first line has `t`. Each of the next `t` lines is a phrase. For each, print `YES` or `NO`.

## Starter
```python
t = int(input())
for _ in range(t):
    phrase = input()
```

## Tests
=== sample
3
Racecar
A man, a plan, a canal: Panama!
Python
---
YES
YES
NO
=== hidden
2
a
ab
---
YES
NO
=== hidden
2
No 'x' in Nixon
Was it a car or a cat I saw?
---
YES
YES
=== hidden
2
12321
!!..
---
YES
YES
=== hidden
1
Step on no pets.  ok
---
NO

## Hints
- `ch.isalpha()` tests whether a character is a letter.
- Build a cleaned, lowercased string, then compare it with its reverse `[::-1]`.
- A phrase with no letters at all cleans to the empty string, which *is* a palindrome.

## Solution
Keep only the letters, lowercase them, and compare the result with its reverse.

```python
t = int(input())
for _ in range(t):
    phrase = input()
    cleaned = "".join(ch.lower() for ch in phrase if ch.isalpha())
    print("YES" if cleaned == cleaned[::-1] else "NO")
```

`"12321"` and `"!!.."` contain no letters, so both clean to `""`. The empty string equals its reverse, so both are palindromes. **Time:** O(n) per phrase. An interview follow-up asks for O(1) extra space, which needs two pointers walking inward and skipping non-letters (the Two Pointers topic).
