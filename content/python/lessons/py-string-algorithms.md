# String Algorithms

Text processing is everywhere: log scanning, search engines, DNA analysis, plagiarism detection, intrusion detection, autocomplete. Python's `str.find` and the `in` operator are fast in practice (CPython uses a hybrid of Boyer–Moore–Horspool and the Two-Way algorithm), but interviews and advanced problems need the algorithms themselves:
- **KMP** prefix functions
- the **Z-function**
- **rolling hashes** (Rabin–Karp)
- **Manacher** for palindromes
- **Aho–Corasick** for many patterns
- **suffix arrays** for substring queries over one text

## 1. Prefix function and KMP

`pi[i]` = the length of the longest proper prefix of `s[:i+1]` that is also a suffix of it.

```python
def prefix_function(s):
    pi = [0] * len(s)
    for i in range(1, len(s)):
        k = pi[i - 1]
        while k and s[i] != s[k]:
            k = pi[k - 1]               # fall back to the next shorter border
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    return pi

def kmp_find_all(text, pat):
    if not pat:
        return []
    s = pat + "\0" + text               # a separator that occurs in neither string
    pi = prefix_function(s)
    m = len(pat)
    return [i - 2 * m for i in range(len(s)) if pi[i] == m]

kmp_find_all("abababa", "aba")           # [0, 2, 4]
```

The cost is O(n + m): k increases at most once per character, and every fallback decreases it. Extras: the shortest period of s is `n - pi[-1]`; the number of occurrences of each prefix; building the KMP automaton.

## 2. Z-function

`z[i]` = the length of the longest common prefix of s and `s[i:]`:

```python
def z_function(s):
    n = len(s)
    z = [0] * n
    if n:
        z[0] = n
    l = r = 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])          # reuse the known match window [l, r)
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z
```

Pattern search: compute the Z-function of `pat + sep + text`, and every position with `z == len(pat)` is a match. It's often simpler to reason about than KMP.

## 3. Rolling hash (Rabin–Karp)

Polynomial hash `h(s) = Σ s[i]·Bⁿ⁻¹⁻ⁱ mod M`. With prefix hashes, **any substring's hash** is O(1):

```python
class StrHash:
    MOD = (1 << 61) - 1                  # a Mersenne prime: few collisions
    B = 131

    def __init__(self, s):
        n = len(s)
        self.h = [0] * (n + 1)
        self.p = [1] * (n + 1)
        for i, ch in enumerate(s):
            self.h[i + 1] = (self.h[i] * self.B + ord(ch)) % self.MOD
            self.p[i + 1] = self.p[i] * self.B % self.MOD

    def get(self, l, r):                 # hash of s[l:r]
        return (self.h[r] - self.h[l] * self.p[r - l]) % self.MOD
```

Applications:
- substring equality in O(1)
- the **longest repeated substring** (binary search on the length + a set of hashes, O(n log n))
- the longest common substring of two strings
- counting distinct substrings of a given length
- finding duplicate DNA sequences

> [!WARNING]
> Hashes can collide. With a modulus around 2⁶¹ and random inputs, collisions are astronomically unlikely, but adversarial inputs (on competitive-programming sites) can break a fixed base. Randomise the base at runtime, or use two moduli. When correctness is critical, verify candidate matches by direct comparison.

## 4. Manacher: all palindromes in O(n)

Insert separators (`#a#b#a#`) so every palindrome has odd length, then reuse the mirror inside the rightmost known palindrome:

```python
def manacher(s):
    t = "#" + "#".join(s) + "#"
    n = len(t)
    d = [0] * n                          # radius around each centre in t
    c = r = 0
    for i in range(n):
        if i < r:
            d[i] = min(r - i, d[2 * c - i])
        while i - d[i] - 1 >= 0 and i + d[i] + 1 < n and t[i - d[i] - 1] == t[i + d[i] + 1]:
            d[i] += 1
        if i + d[i] > r:
            c, r = i, i + d[i]
    best = max(range(n), key=lambda i: d[i])
    start = (best - d[best]) // 2
    return s[start:start + d[best]]      # the longest palindromic substring

manacher("babad")    # 'bab'
```

In the transformed string, `d[i]` equals the length of the corresponding palindrome in the original. The total number of palindromic substrings is `Σ (d[i] + 1) // 2`.

## 5. Aho–Corasick: many patterns at once

Build a trie of all the patterns, then add **failure links** (the longest proper suffix of the current node's string that is also a trie path, like KMP's prefix function generalised to a trie, computed by BFS). Scanning the text once reports all occurrences of all patterns in O(text + Σ|patterns| + matches). It's used in `grep -F` with many words, antivirus signature matching, and network intrusion detection (Snort).

## 6. Suffix arrays

The **suffix array** is the sorted order of all suffixes. With the **LCP array** (the longest common prefix of adjacent suffixes, computed by Kasai's algorithm in O(n)), it answers:
- whether a pattern occurs (binary search, O(m log n))
- the number of distinct substrings: `n(n+1)/2 − Σ LCP`
- the longest repeated substring (max LCP)
- the longest common substring of two strings (concatenate with a separator)

A simple O(n log² n) construction sorts the suffixes by their first 2ᵏ characters using the ranks from round k − 1:

```python
def suffix_array(s):
    n = len(s)
    rank = [ord(c) for c in s]
    sa = list(range(n))
    k = 1
    while True:
        key = lambda i: (rank[i], rank[i + k] if i + k < n else -1)
        sa.sort(key=key)
        new = [0] * n
        for j in range(1, n):
            new[sa[j]] = new[sa[j - 1]] + (key(sa[j]) != key(sa[j - 1]))
        rank = new
        if rank[sa[-1]] == n - 1:          # all ranks distinct: done
            return sa
        k *= 2
```

(For n = 1, it returns `[0]` after the first round.)

## 7. Choosing a tool

| Task | Tool |
|---|---|
| one pattern in a text (in Python) | `str.find` / `in` (C speed) |
| one pattern, guaranteed linear, or reasoning about borders and periods | KMP / Z |
| substring equality, many queries | rolling hash |
| repeated or common substrings | hash + binary search, or a suffix array + LCP |
| all palindromes | Manacher |
| many patterns, one text | Aho–Corasick |
| many queries on one fixed text | suffix array / automaton |

## 8. Exam-ready answers

> [!EXAM]
> **Rolling hashes and the Rabin–Karp algorithm.** A polynomial rolling hash maps a string to `Σ s[i]·B^(n−1−i)` modulo a large prime, so that the hash of a window can be updated in O(1) as it slides, and the hash of any substring can be obtained in O(1) from precomputed prefix hashes and powers of B. Rabin–Karp compares window hashes against the pattern's hash, verifying candidates by direct comparison, giving expected O(n + m) time; it extends naturally to multiple patterns of equal length and to problems such as finding repeated substrings by binary searching on length. Because distinct strings can collide, implementations use large or multiple moduli, randomised bases, and verification when exactness matters.

## 9. Cheat sheet

| Fact | Formula / code |
|---|---|
| matches via the prefix function | `pi[i] == len(pat)` on `pat + sep + text` |
| shortest period | `n - pi[-1]` |
| substring hash | `(h[r] - h[l] * p[r-l]) % M` |
| palindromes, total | `Σ (d[i] + 1) // 2` (Manacher on `#`-separated) |
| distinct substrings | `n(n+1)/2 - Σ LCP` |

> [!INTERVIEW]
> **"Find the longest repeated substring of a string of length 10⁵."** Binary search the length L. For each L, hash all windows of length L (a rolling hash, O(n)) and check for a repeat with a set, so O(n log n) total. Verify a candidate match directly to rule out collisions. Alternatively, build a suffix array with LCP: the answer is the maximum LCP value. Mention the trade-off: hashing is easier to code, while the suffix array is exact and answers more questions.
