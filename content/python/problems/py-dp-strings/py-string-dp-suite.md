---
id: py-string-dp-suite
title: "String DP Suite: LCS, Edit Script, Regex Matching, Palindrome Cuts"
difficulty: Hard
order: 1
tags: dynamic programming, LCS, edit distance, regex, palindromes
time_limit: 4
---
## Statement
```python
def lcs_string(s, t):
    """One longest common subsequence. Build the standard table dp[i][j] over prefixes, then walk back
    from (len(s), len(t)): on equal characters take it and move diagonally; otherwise move UP (i-1)
    if dp[i-1][j] >= dp[i][j-1], else LEFT. Return the subsequence."""

def edit_ops(s, t):
    """Return (distance, ops) for Levenshtein distance. ops is the edit count per kind as a dict
    {"insert": a, "delete": b, "substitute": c}, read off ONE optimal script found by walking back from
    (n, m) preferring, in this order: match/substitute (diagonal), delete (up), insert (left)."""

def regex_match(s, p):
    """Full match of s against pattern p with '.' (any char) and '*' (zero or more of the previous element)."""

def min_palindrome_cuts(s):
    """Fewest cuts so that every piece is a palindrome. O(n^2)."""
```

Test lines are `(function_name, args)` literals or `gen NAME SEED N`.

## Starter
```python
import re

def lcs_string(s, t):
    return ""

def edit_ops(s, t):
    return (abs(len(s) - len(t)), {"insert": 0, "delete": 0, "substitute": 0})

def regex_match(s, p):
    return re.fullmatch(p, s) is not None

def min_palindrome_cuts(s):
    return max(0, len(s) - 1)
```

## Driver
```python
import ast
import random
import sys

FUNCS = {f.__name__: f for f in (lcs_string, edit_ops, regex_match, min_palindrome_cuts)}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        s = "".join(rng.choice("ACGT") for _ in range(n))
        t = "".join(rng.choice("ACGT") for _ in range(n))
        if name == "lcs_string":
            r = lcs_string(s, t)
            print(name, n, len(r), r[:20])
        elif name == "edit_ops":
            print(name, n, edit_ops(s, t))
        elif name == "regex_match":
            print(name, n, regex_match("a" * n, "a*" * 30 + "a" * 10), regex_match("a" * n, "a*" * 30 + "b"))
        else:
            pal = "".join(rng.choice("ab") for _ in range(n))
            print(name, n, min_palindrome_cuts(pal))
        continue
    name, args = ast.literal_eval(line)
    print(name, "->", repr(FUNCS[name](*args)))
```

## Tests
=== sample
("lcs_string", ("ABCBDAB", "BDCABA"))
("edit_ops", ("kitten", "sitting"))
("regex_match", ("aab", "c*a*b"))
("min_palindrome_cuts", ("aab",))
---
lcs_string -> 'BCBA'
edit_ops -> (3, {'insert': 1, 'delete': 0, 'substitute': 2})
regex_match -> True
min_palindrome_cuts -> 1
=== hidden
("lcs_string", ("", "abc"))
("lcs_string", ("abc", "def"))
("lcs_string", ("abcde", "ace"))
("lcs_string", ("aaaa", "aa"))
("edit_ops", ("", ""))
("edit_ops", ("", "abc"))
("edit_ops", ("abc", ""))
("edit_ops", ("intention", "execution"))
("edit_ops", ("horse", "ros"))
("regex_match", ("", ""))
("regex_match", ("", "a*"))
("regex_match", ("aa", "a"))
("regex_match", ("ab", ".*"))
("regex_match", ("mississippi", "mis*is*p*."))
("regex_match", ("mississippi", "mis*is*ip*."))
("regex_match", ("aaa", "ab*a*c*a"))
("min_palindrome_cuts", ("",))
("min_palindrome_cuts", ("a",))
("min_palindrome_cuts", ("abccbc",))
("min_palindrome_cuts", ("racecarannakayak",))
---
lcs_string -> ''
lcs_string -> ''
lcs_string -> 'ace'
lcs_string -> 'aa'
edit_ops -> (0, {'insert': 0, 'delete': 0, 'substitute': 0})
edit_ops -> (3, {'insert': 3, 'delete': 0, 'substitute': 0})
edit_ops -> (3, {'insert': 0, 'delete': 3, 'substitute': 0})
edit_ops -> (5, {'insert': 0, 'delete': 0, 'substitute': 5})
edit_ops -> (3, {'insert': 0, 'delete': 2, 'substitute': 1})
regex_match -> True
regex_match -> True
regex_match -> False
regex_match -> True
regex_match -> False
regex_match -> True
regex_match -> True
min_palindrome_cuts -> 0
min_palindrome_cuts -> 0
min_palindrome_cuts -> 2
min_palindrome_cuts -> 2
=== hidden
gen lcs_string 1 1500
gen edit_ops 2 1500
---
lcs_string 1500 972 CGATTTTTTTTGGAATCTCT
edit_ops 1500 (789, {'insert': 148, 'delete': 148, 'substitute': 493})
=== hidden
gen regex_match 3 2000
gen min_palindrome_cuts 4 1500
---
regex_match 2000 True False
min_palindrome_cuts 1500 221

## Hints
- **LCS walk-back**: follow the stated tie rule exactly, so the returned string is deterministic.
- **edit_ops**: fill the full `(n+1) × (m+1)` table. Walking back: if i, j > 0 and `dp[i][j] == dp[i-1][j-1] + (s[i-1] != t[j-1])`, move diagonally (count a substitution if the characters differ); elif `i > 0 and dp[i][j] == dp[i-1][j] + 1`, it's a delete; else an insert.
- **regex**: `dp[i][j]` = whether `s[:i]` matches `p[:j]`. Initialise `dp[0][j]` for patterns like `a*b*`. For `p[j-1] == '*'`, use `dp[i][j-2] or (first_match and dp[i-1][j])`.
- **Palindrome cuts**: expand around every centre to mark palindromic `s[l..r]`, or fill `pal[l][r]` by length. Then `cuts[r] = 0` if `s[0..r]` is a palindrome, else `min(cuts[l-1] + 1)` over palindromic `s[l..r]`.

## Solution
```python
def lcs_string(s, t):
    n, m = len(s), len(t)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        si, row, prev = s[i - 1], dp[i], dp[i - 1]
        for j in range(1, m + 1):
            row[j] = prev[j - 1] + 1 if si == t[j - 1] else max(prev[j], row[j - 1])
    out, i, j = [], n, m
    while i and j:
        if s[i - 1] == t[j - 1]:
            out.append(s[i - 1]); i -= 1; j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return "".join(reversed(out))

def edit_ops(s, t):
    n, m = len(s), len(t)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s[i - 1] == t[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j - 1], dp[i - 1][j], dp[i][j - 1])
    ops = {"insert": 0, "delete": 0, "substitute": 0}
    i, j = n, m
    while i or j:
        if i and j and dp[i][j] == dp[i - 1][j - 1] + (s[i - 1] != t[j - 1]):
            if s[i - 1] != t[j - 1]:
                ops["substitute"] += 1
            i -= 1; j -= 1
        elif i and dp[i][j] == dp[i - 1][j] + 1:
            ops["delete"] += 1; i -= 1
        else:
            ops["insert"] += 1; j -= 1
    return dp[n][m], ops

def regex_match(s, p):
    n, m = len(s), len(p)
    dp = [[False] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = True
    for j in range(2, m + 1):
        dp[0][j] = p[j - 1] == "*" and dp[0][j - 2]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if p[j - 1] == "*":
                first = p[j - 2] in (s[i - 1], ".")
                dp[i][j] = dp[i][j - 2] or (first and dp[i - 1][j])
            else:
                dp[i][j] = p[j - 1] in (s[i - 1], ".") and dp[i - 1][j - 1]
    return dp[n][m]

def min_palindrome_cuts(s):
    n = len(s)
    if n == 0:
        return 0
    cuts = list(range(-1, n))              # cuts[k] = min cuts for s[:k]; cuts[0] = -1 sentinel
    for center in range(n):
        for l, r in ((center, center), (center, center + 1)):   # odd and even palindromes
            while l >= 0 and r < n and s[l] == s[r]:
                if cuts[l] + 1 < cuts[r + 1]:
                    cuts[r + 1] = cuts[l] + 1
                l -= 1; r += 1
    return cuts[n]
```

- **LCS and edit distance** fill prefix tables. The **walk-back rules** turn the tables into concrete answers, and fixing the tie order makes that answer reproducible. It's the same idea `diff` uses to emit a specific patch among many equally short ones.
- **Regex matching** handles `x*` as two options: drop the `x*` entirely (`dp[i][j-2]`), or let it consume one more matching character and stay on the same pattern position (`dp[i-1][j]`). Backtracking regex engines take exponential time on patterns like `a*a*a*…b`; this DP is always O(n·m).
- **Palindrome cuts** combine centre expansion with a 1-D DP. Every palindrome `s[l..r]` discovered while expanding offers the candidate `cuts[l] + 1` for the prefix ending at r. The `−1` sentinel makes a whole-prefix palindrome cost 0 cuts.
