---
id: py-pangram
title: Pangram Checker
difficulty: Easy
order: 3
tags: set difference, strings
---
## Statement
A **pangram** uses every letter of the English alphabet at least once (case-insensitive). For each of `t` sentences, print `PANGRAM` if it is one; otherwise print `MISSING` followed by the missing letters in alphabetical order, with no spaces between them.

## Starter
```python
import string          # string.ascii_lowercase == "abcdefghijklmnopqrstuvwxyz"
t = int(input())
for _ in range(t):
    sentence = input()
```

## Tests
=== sample
3
The quick brown fox jumps over the lazy dog
Hello, World!
Pack my box with five dozen liquor jugs.
---
PANGRAM
MISSING abcfgijkmnpqstuvxyz
PANGRAM
=== hidden
1

---
MISSING abcdefghijklmnopqrstuvwxyz
=== hidden
1
abcdefghijklmnopqrstuvwxy
---
MISSING z
=== hidden
1
ZYXWVUTSRQPONMLKJIHGFEDCBA 123
---
PANGRAM

## Hints
- `string.ascii_lowercase` is all 26 letters; turn it into a set.
- Set difference does the work: `set(ascii_lowercase) - set(sentence.lower())` is the set of missing letters.
- Print the missing letters with `"".join(sorted(missing))`.

## Solution
The missing letters are exactly the set difference *alphabet − letters used*.

```python
import string
t = int(input())
for _ in range(t):
    sentence = input()
    missing = set(string.ascii_lowercase) - set(sentence.lower())
    if missing:
        print("MISSING", "".join(sorted(missing)))
    else:
        print("PANGRAM")
```

Characters that aren't letters (spaces, digits, punctuation) end up in `set(sentence.lower())`, but subtracting from the alphabet ignores them, so no filtering step is needed. Sets are unordered, so `sorted` is required for deterministic output.
