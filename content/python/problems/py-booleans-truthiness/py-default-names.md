---
id: py-default-names
title: Default Names
difficulty: Easy
order: 1
tags: truthiness, or, strip
---
## Statement
A sign-up form collects a display name. The first line has `n`, followed by `n` lines, each the raw text a user typed. It may be empty or only spaces.

For each line, print the name with surrounding whitespace removed, or `Anonymous` if nothing remains.

Solve it with the `or` idiom from the lesson. No `if` needed.

## Starter
```python
n = int(input())
for _ in range(n):
    raw = input()
```

## Tests
=== sample
4
Ada
   Linus  

Grace Hopper
---
Ada
Linus
Anonymous
Grace Hopper
=== hidden
3
0
 
False
---
0
Anonymous
False

## Hints
- `"   ".strip()` is `""`, which is falsy.
- `x or "Anonymous"` returns `x` if it is truthy, else the default.

## Solution
`strip()` removes surrounding whitespace. An all-space or empty input becomes `""`, which is falsy, so `or` falls through to the default.

```python
n = int(input())
for _ in range(n):
    print(input().strip() or "Anonymous")
```

The hidden test includes the names `0` and `False`. They are **non-empty strings**, so they are truthy, and the users keep those names. The string `"0"` is not the integer `0`.
