---
id: py-group-anagrams
title: Group Anagrams
difficulty: Medium
order: 2
tags: hash map, grouping, canonical key, leetcode-49
---
## Statement
Group the words that are **anagrams** of each other (same letters, same counts, any order).

Output format, so there's a single correct answer: inside each group, sort the words alphabetically; then sort the groups by their first word. Print one group per line, words separated by spaces.

Input: `n`, then `n` lowercase words (one per line; a word may be empty, shown as an empty line).

## Starter
```python
def group_anagrams(words):
    # return a list of groups (lists of words)
    pass
```

## Driver
```python
n = int(input())
words = [input().strip() for _ in range(n)]
groups = [sorted(g) for g in group_anagrams(words)]
groups.sort(key=lambda g: g[0])
for g in groups:
    print(" ".join(g))
```

## Tests
=== sample
6
eat
tea
tan
ate
nat
bat
---
ate eat tea
bat
nat tan
=== hidden
1
a
---
a
=== hidden
4
abc
cab
bca
abcd
---
abc bca cab
abcd
=== hidden
5
listen
silent
enlist
google
gooegl
---
enlist listen silent
gooegl google
=== hidden
3
aab
aba
abb
---
aab aba
abb

## Hints
- Anagrams become identical when their letters are sorted: `"".join(sorted("tea")) == "aet"`.
- Use that sorted string (or a tuple of 26 letter counts) as a dict key, and group words under it.

## Solution
Give each word a **canonical key** that is equal for exactly the anagrams of one another: its sorted letters. Then group with a dict from key to list of words.

```python
def group_anagrams(words):
    groups = {}
    for w in words:
        key = "".join(sorted(w))
        groups.setdefault(key, []).append(w)
    return list(groups.values())
```

**Time** O(n · k log k) for n words of length k. An O(n·k) variant uses `tuple(count_of_each_letter)` as the key. `"aab"` and `"abb"` contain the same *set* of letters but different counts, so they aren't anagrams; sorting the letters keeps the counts and separates them. (LeetCode 49.)
