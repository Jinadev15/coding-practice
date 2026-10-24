# Dynamic Programming III: Strings

Comparing, aligning and transforming strings is a central DP application. It's behind `diff` and `git merge`, spell checkers, DNA sequence alignment, speech recognition and plagiarism detection. The standard shape is a table `dp[i][j]` over a **prefix of each string**, where each cell considers what happens to the last characters. This lesson covers the longest common subsequence, edit distance, longest palindromic subsequence and substring, distinct subsequences, regular-expression and wildcard matching, and how to reconstruct the actual alignment.

## 1. The prefix-table pattern

For strings `s` (length n) and `t` (length m), define `dp[i][j]` over `s[:i]` and `t[:j]`. The table has (n+1)·(m+1) cells, and row 0 / column 0 are the empty-prefix base cases. Each transition looks at `s[i-1]` and `t[j-1]`.

## 2. Longest common subsequence (LCS)

```
dp[i][j] = dp[i-1][j-1] + 1               if s[i-1] == t[j-1]
         = max(dp[i-1][j], dp[i][j-1])    otherwise
```

```python
def lcs(s, t):
    n, m = len(s), len(t)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s[i - 1] == t[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    # reconstruct by walking back from the corner
    out, i, j = [], n, m
    while i and j:
        if s[i - 1] == t[j - 1]:
            out.append(s[i - 1]); i -= 1; j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return dp[n][m], "".join(reversed(out))

lcs("ABCBDAB", "BDCABA")     # (4, 'BCBA')
```

`diff` is LCS on **lines**: the lines not in the LCS are the deletions and insertions. (Real `diff` uses Myers' O(ND) algorithm, which is fast when files are similar.) The shortest common supersequence has length n + m − LCS.

## 3. Edit distance (Levenshtein)

The minimum number of insertions, deletions and substitutions turning `s` into `t`:

```
dp[i][0] = i, dp[0][j] = j
dp[i][j] = dp[i-1][j-1]                                   if s[i-1] == t[j-1]
         = 1 + min(dp[i-1][j],      # delete s[i-1]
                   dp[i][j-1],      # insert t[j-1]
                   dp[i-1][j-1])    # substitute
```

```python
def edit_distance(s, t):
    prev = list(range(len(t) + 1))
    for i in range(1, len(s) + 1):
        cur = [i] + [0] * len(t)
        for j in range(1, len(t) + 1):
            if s[i - 1] == t[j - 1]:
                cur[j] = prev[j - 1]
            else:
                cur[j] = 1 + min(prev[j], cur[j - 1], prev[j - 1])
        prev = cur
    return prev[-1]

edit_distance("kitten", "sitting")   # 3
```

Variants:
- **Weighted costs** (substitution costs by keyboard distance, or by amino-acid similarity, as in the Needleman–Wunsch alignment).
- **Damerau** adds transposition of adjacent characters.
- **Banded DP**: only cells with |i − j| ≤ k, giving O(nk), to answer "is the distance ≤ k?".

## 4. Palindromes

**Longest palindromic subsequence** = LCS(s, reversed(s)), or the interval DP `dp[i][j]` over `s[i..j]`:

```python
def lps(s):
    n = len(s)
    dp = [0] * n                                    # dp[j] for the current i (rolling over i descending)
    for i in range(n - 1, -1, -1):
        new = [0] * n
        new[i] = 1
        for j in range(i + 1, n):
            if s[i] == s[j]:
                new[j] = dp[j - 1] + 2              # dp[j-1] is the old row: s[i+1..j-1]
            else:
                new[j] = max(dp[j], new[j - 1])
        dp = new
    return dp[n - 1] if n else 0
```

**Longest palindromic substring** (contiguous): expand around each of the 2n−1 centres in O(n²) time and O(1) space, or use Manacher in O(n). **Minimum cuts for palindrome partitioning**: precompute `is_pal[i][j]`, then `cuts[j] = min(cuts[i-1] + 1)` over palindromic `s[i..j]`.

## 5. Counting: distinct subsequences

The number of times `t` occurs as a subsequence of `s`:

```python
def num_distinct(s, t):
    dp = [1] + [0] * len(t)                         # dp[j]: ways to form t[:j]
    for ch in s:
        for j in range(len(t), 0, -1):              # descending: each s character used once per position
            if t[j - 1] == ch:
                dp[j] += dp[j - 1]
    return dp[len(t)]

num_distinct("rabbbit", "rabbit")   # 3
```

## 6. Pattern matching: wildcards and regex

**Wildcard** (`?` matches one character, `*` any sequence):

```python
def wildcard(s, p):
    dp = [True] + [False] * len(p)                  # dp[j]: does s[:i] match p[:j]?
    for j in range(1, len(p) + 1):
        dp[j] = dp[j - 1] and p[j - 1] == "*"
    for ch in s:
        new = [False] * (len(p) + 1)
        for j in range(1, len(p) + 1):
            if p[j - 1] == "*":
                new[j] = new[j - 1] or dp[j]        # * matches empty, or one more char
            elif p[j - 1] in ("?", ch):
                new[j] = dp[j - 1]
        dp = new
    return dp[-1]
```

**Regex with `.` and `*`** (where `*` repeats the previous element):
- If `p[j-1] == '*'`, then `dp[i][j] = dp[i][j-2]` (zero copies) or (`match(s[i-1], p[j-2])` and `dp[i-1][j]`) (one more copy).
- Otherwise, `dp[i][j] = match(s[i-1], p[j-1])` and `dp[i-1][j-1]`.

The base row must handle patterns like `a*b*` matching the empty string.

## 7. Complexity and memory

All of these are O(n·m) time. Rolling rows give O(min(n, m)) memory when only the value is needed. Reconstruction needs the full table, or **Hirschberg's algorithm**, which recovers an LCS or alignment in O(n·m) time and O(m) space by divide and conquer. In Python, 5000 × 5000 = 2.5·10⁷ cell updates take a few seconds. Use rolling rows, hoist attribute lookups, or offload to NumPy or C for bigger inputs.

## 8. Exam-ready answers

> [!EXAM]
> **Edit distance.** The Levenshtein distance between strings s and t is the minimum number of single-character insertions, deletions and substitutions transforming s into t. Dynamic programming computes `D[i][j]` for the prefixes `s[:i]` and `t[:j]`: `D[i][0] = i`, `D[0][j] = j`, and `D[i][j]` equals `D[i−1][j−1]` if the last characters match, and otherwise 1 plus the minimum of `D[i−1][j]` (deletion), `D[i][j−1]` (insertion) and `D[i−1][j−1]` (substitution). This takes O(nm) time and, when only the distance is needed, O(min(n, m)) space by keeping two rows; tracing back through the full table recovers an optimal edit script.

## 9. Cheat sheet

| Problem | Match | Mismatch |
|---|---|---|
| LCS | `dp[i-1][j-1] + 1` | `max(up, left)` |
| edit distance | `dp[i-1][j-1]` | `1 + min(up, left, diag)` |
| distinct subsequences | `dp[j] += dp[j-1]` (j descending) | unchanged |
| palindromic subsequence | `inner + 2` | `max(drop left, drop right)` |
| wildcard `*` | `left or up` | |
| regex `x*` | `dp[i][j-2] or (match and dp[i-1][j])` | |

> [!INTERVIEW]
> **"Implement `diff` for two files."** Treat each line as a symbol (hash the lines) and compute the LCS of the line sequences. Lines outside the LCS are deletions (from the old file) or insertions (from the new file), found by walking back through the table. Mention that O(nm) is too slow for big files, and that production tools use Myers' O((n+m)·D) algorithm (D = edit size), plus heuristics like patience diff for readability.
