---
id: py-phone-letters
title: Phone Keypad Combinations
difficulty: Medium
order: 1
tags: itertools.product, combinatorics, leetcode-17
---
## Statement
On a phone keypad, `2`=abc, `3`=def, `4`=ghi, `5`=jkl, `6`=mno, `7`=pqrs, `8`=tuv, `9`=wxyz. Given a string of digits from 2 to 9 (length 0–8), print every letter combination it could represent, in **lexicographic order**, space-separated. An empty input prints an empty line.

## Starter
```python
from itertools import product

KEYS = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl",
        "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}

def letter_combinations(digits):
    pass
```

## Driver
```python
print(" ".join(letter_combinations(input().strip())))
```

## Tests
=== sample
23
---
ad ae af bd be bf cd ce cf
=== hidden
7
---
p q r s
=== hidden

---

=== hidden
99

## Hints
- The answer is the Cartesian product of the letter groups: `product(*(KEYS[d] for d in digits))`.
- `product` yields tuples. Join each one into a string.
- Watch out: `product()` with **no** arguments yields one empty tuple, but an empty input must give **no** combinations.

## Solution
Each digit contributes one choice from its letters, so all the combinations are the Cartesian product of the groups. `product` iterates them in lexicographic order when every group is itself in order.

```python
from itertools import product

KEYS = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl",
        "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}

def letter_combinations(digits):
    if not digits:
        return []
    return ["".join(combo) for combo in product(*(KEYS[d] for d in digits))]
```

The output size is up to 4⁸ = 65,536. In interviews you're usually asked to also write the **backtracking** version (build the string character by character, recursing per digit). `product` is exactly that recursion, implemented in C. (LeetCode 17.)
