---
id: py-min-window
title: Minimum Window Substring and Longest K-Distinct
difficulty: Hard
order: 1
tags: sliding window, Counter, two pointers, amortised analysis
---
## Statement
A robot's log scanner looks for the shortest stretch of a log that mentions every required event code. Implement three sliding-window functions, all O(n) (plus O(|t|) where relevant):

```python
def min_window(s, t):
    """Shortest substring of s containing every character of t WITH multiplicity.
    Ties: the leftmost. Return "" if none exists or t is empty."""

def longest_k_distinct(s, k):
    """Length of the longest substring with at most k distinct characters (k >= 0)."""

def count_exactly_k_distinct(a, k):
    """Number of non-empty subarrays of list a with exactly k distinct values (k >= 1)."""
```

Test lines are `(function_name, args)` literals or `gen NAME SEED N`.

## Starter
```python
from collections import Counter

def min_window(s, t):
    need = Counter(t)
    best = ""
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            if not need - Counter(s[i:j]):
                if not best or j - i < len(best):
                    best = s[i:j]
                break
    return best if t else ""

def longest_k_distinct(s, k):
    return max((j - i for i in range(len(s)) for j in range(i, len(s) + 1) if len(set(s[i:j])) <= k), default=0)

def count_exactly_k_distinct(a, k):
    return sum(1 for i in range(len(a)) for j in range(i + 1, len(a) + 1) if len(set(a[i:j])) == k)
```

## Driver
```python
import ast
import random
import sys

FUNCS = {f.__name__: f for f in (min_window, longest_k_distinct, count_exactly_k_distinct)}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        if name == "min_window":
            s = "".join(rng.choice("abcdefghij") for _ in range(n))
            r = min_window(s, "abcdefghijjihgf")
            print(name, n, len(r), r[:12])
        elif name == "longest_k_distinct":
            s = "".join(rng.choice("abcdefgh") for _ in range(n))
            print(name, n, [longest_k_distinct(s, k) for k in (0, 1, 3, 5, 8)])
        else:
            a = [rng.randrange(12) for _ in range(n)]
            print(name, n, [count_exactly_k_distinct(a, k) for k in (1, 4, 12)])
        continue
    name, args = ast.literal_eval(line)
    print(name, "->", repr(FUNCS[name](*args)))
```

## Tests
=== sample
("min_window", ("ADOBECODEBANC", "ABC"))
("min_window", ("a", "aa"))
("longest_k_distinct", ("eceba", 2))
("count_exactly_k_distinct", ([1, 2, 1, 2, 3], 2))
---
min_window -> 'BANC'
min_window -> ''
longest_k_distinct -> 3
count_exactly_k_distinct -> 7
=== hidden
("min_window", ("", "a"))
("min_window", ("abc", ""))
("min_window", ("aa", "aa"))
("min_window", ("bba", "ab"))
("min_window", ("abcabdebac", "cda"))
("min_window", ("xyzzyx", "zx"))
("longest_k_distinct", ("", 2))
("longest_k_distinct", ("abc", 0))
("longest_k_distinct", ("aaaa", 1))
("longest_k_distinct", ("abaccc", 2))
("count_exactly_k_distinct", ([1, 2, 1, 3, 4], 3))
("count_exactly_k_distinct", ([1, 1, 1], 1))
("count_exactly_k_distinct", ([1, 2], 3))
---
min_window -> ''
min_window -> ''
min_window -> 'aa'
min_window -> 'ba'
min_window -> 'cabd'
min_window -> 'xyz'
longest_k_distinct -> 0
longest_k_distinct -> 0
longest_k_distinct -> 4
longest_k_distinct -> 4
count_exactly_k_distinct -> 3
count_exactly_k_distinct -> 6
count_exactly_k_distinct -> 0
=== hidden
gen min_window 1 200000
gen longest_k_distinct 2 200000
gen count_exactly_k_distinct 3 100000
---
min_window 200000 15 agfhjcfbjhde
longest_k_distinct 200000 [0, 6, 16, 32, 200000]
count_exactly_k_distinct 100000 [109056, 149584, 4996452402]

## Hints
- **min_window**: keep `need = Counter(t)` and `missing = len(t)`. When `s[r]` enters and `need[s[r]] > 0`, decrement `missing`; always decrement `need[s[r]]` (it can go negative for surplus characters). While `missing == 0`, record the window, then remove `s[l]`. If `need[s[l]]` becomes positive again, increment `missing`.
- Record the best window as index pairs and slice once at the end. Slicing inside the loop makes the solution O(n²).
- **exactly k** = at_most(k) − at_most(k − 1), where at_most adds `r − l + 1` for each r.

## Solution
```python
from collections import Counter, defaultdict

def min_window(s, t):
    if not t:
        return ""
    need = Counter(t)
    missing = len(t)
    best_l, best_r = 0, -1                    # empty
    l = 0
    for r, c in enumerate(s):
        if need[c] > 0:
            missing -= 1
        need[c] -= 1
        while missing == 0:                   # valid: shrink as much as possible
            if best_r < 0 or r - l < best_r - best_l:
                best_l, best_r = l, r
            need[s[l]] += 1
            if need[s[l]] > 0:
                missing += 1
            l += 1
    return s[best_l:best_r + 1]

def longest_k_distinct(s, k):
    cnt = defaultdict(int)
    l = best = 0
    for r, c in enumerate(s):
        cnt[c] += 1
        while len(cnt) > k:
            cnt[s[l]] -= 1
            if cnt[s[l]] == 0:
                del cnt[s[l]]
            l += 1
        best = max(best, r - l + 1)
    return best

def _at_most(a, k):
    if k <= 0:
        return 0
    cnt = defaultdict(int)
    l = total = 0
    for r, x in enumerate(a):
        cnt[x] += 1
        while len(cnt) > k:
            cnt[a[l]] -= 1
            if cnt[a[l]] == 0:
                del cnt[a[l]]
            l += 1
        total += r - l + 1                     # every window ending at r and starting in [l, r]
    return total

def count_exactly_k_distinct(a, k):
    return _at_most(a, k) - _at_most(a, k - 1)
```

All three use the expand-right, shrink-left template. The left pointer only moves forward, so the total work is O(n).
- **min_window** keeps a single integer, `missing`, that says whether the window is valid, so it never compares whole Counters (which would cost O(alphabet) per step). Surplus characters drive `need` negative, which is how multiplicity is tracked. Recording strictly shorter windows gives the leftmost-tie rule for free.
- **exactly k** isn't monotone, but "at most k" is. Counting `r − l + 1` windows per right endpoint and subtracting the two counts gives the exact count in O(n).
