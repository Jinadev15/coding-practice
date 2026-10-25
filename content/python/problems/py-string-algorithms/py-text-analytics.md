---
id: py-text-analytics
title: "Text Analytics: Repeats, Distinct Substrings, Shortest Palindrome, Palindrome Count"
difficulty: Hard
order: 1
tags: rolling hash, suffix array, LCP, KMP, Manacher
time_limit: 6
---
## Statement
```python
def longest_repeat(s):
    """Length of the longest substring occurring at least twice (occurrences may overlap). n <= 100 000."""

def distinct_substrings(s):
    """Number of distinct non-empty substrings. n <= 20 000 (suffix array + LCP, or hashing per length)."""

def shortest_palindrome(s):
    """Shortest palindrome formed by adding characters only at the FRONT of s. O(n) with KMP."""

def count_palindromes(s):
    """Number of palindromic substrings counted by position (s[i:j] for distinct (i, j)). O(n) Manacher."""
```

Test lines are `(function_name, args)` literals or `gen NAME SEED N`.

## Starter
```python
def longest_repeat(s):
    best = 0
    for L in range(1, len(s)):
        seen = set()
        for i in range(len(s) - L + 1):
            if s[i:i + L] in seen:
                best = L
                break
            seen.add(s[i:i + L])
    return best

def distinct_substrings(s):
    return len({s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1)})

def shortest_palindrome(s):
    for k in range(len(s), -1, -1):
        if s[:k] == s[:k][::-1]:
            return s[k:][::-1] + s
    return s

def count_palindromes(s):
    return sum(1 for i in range(len(s)) for j in range(i + 1, len(s) + 1) if s[i:j] == s[i:j][::-1])
```

## Driver
```python
import ast
import random
import sys

FUNCS = {f.__name__: f for f in (longest_repeat, distinct_substrings, shortest_palindrome, count_palindromes)}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        s = "".join(rng.choice("acgt") for _ in range(n))
        if name == "longest_repeat":
            print(name, n, longest_repeat(s), longest_repeat("ab" * (n // 2)))
        elif name == "distinct_substrings":
            print(name, n, distinct_substrings(s), distinct_substrings("a" * n))
        elif name == "shortest_palindrome":
            r = shortest_palindrome("a" * n + "b" + "a" * n)
            r2 = shortest_palindrome("a" * n + "c" + "b" * 3)
            print(name, n, len(r), len(r2), r2[:5])
        else:
            print(name, n, count_palindromes(s), count_palindromes("a" * n))
        continue
    name, args = ast.literal_eval(line)
    print(name, "->", repr(FUNCS[name](*args)))
```

## Tests
=== sample
("longest_repeat", ("banana",))
("distinct_substrings", ("abab",))
("shortest_palindrome", ("aacecaaa",))
("count_palindromes", ("aaa",))
---
longest_repeat -> 3
distinct_substrings -> 7
shortest_palindrome -> 'aaacecaaa'
count_palindromes -> 6
=== hidden
("longest_repeat", ("",))
("longest_repeat", ("abc",))
("longest_repeat", ("aaaa",))
("longest_repeat", ("abcabcabc",))
("distinct_substrings", ("",))
("distinct_substrings", ("a",))
("distinct_substrings", ("banana",))
("shortest_palindrome", ("",))
("shortest_palindrome", ("abcd",))
("shortest_palindrome", ("racecar",))
("count_palindromes", ("",))
("count_palindromes", ("abc",))
("count_palindromes", ("abba",))
---
longest_repeat -> 0
longest_repeat -> 0
longest_repeat -> 3
longest_repeat -> 6
distinct_substrings -> 0
distinct_substrings -> 1
distinct_substrings -> 15
shortest_palindrome -> ''
shortest_palindrome -> 'dcbabcd'
shortest_palindrome -> 'racecar'
count_palindromes -> 0
count_palindromes -> 3
count_palindromes -> 6
=== hidden
gen longest_repeat 1 100000
gen shortest_palindrome 3 100000
---
longest_repeat 100000 15 99998
shortest_palindrome 100000 200001 100008 bbbca
=== hidden
gen distinct_substrings 2 20000
gen count_palindromes 4 100000
---
distinct_substrings 20000 199883262 20000
count_palindromes 100000 166106 5000050000

## Hints
- **longest_repeat**: binary search the length L. For each L, check with a rolling hash whether some window repeats (a set of window hashes, verifying a hit by comparing the actual substrings). Repeat existence is monotone in L.
- **distinct_substrings**: build the suffix array (prefix doubling), then the LCP array with Kasai's algorithm. The answer is `n(n+1)/2 − Σ LCP`.
- **shortest_palindrome**: compute the prefix function of `s + "#" + reversed(s)`. The last value is the length of the longest palindromic prefix of s; prepend the reverse of the rest.
- **count_palindromes**: Manacher on `#`-interleaved text; the answer is `Σ (d[i] + 1) // 2`.

## Solution
```python
def longest_repeat(s):
    n = len(s)
    MOD, B = (1 << 61) - 1, 911382323
    h, p = [0] * (n + 1), [1] * (n + 1)
    for i, ch in enumerate(s):
        h[i + 1] = (h[i] * B + ord(ch)) % MOD
        p[i + 1] = p[i] * B % MOD

    def repeats(L):
        seen = {}
        for i in range(n - L + 1):
            x = (h[i + L] - h[i] * p[L]) % MOD
            j = seen.get(x)
            if j is not None and s[j:j + L] == s[i:i + L]:
                return True
            seen.setdefault(x, i)
        return False

    lo, hi = 0, n                               # largest L with repeats(L); repeats(0) is True
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if repeats(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo

def _suffix_array(s):
    n = len(s)
    rank = [ord(c) for c in s]
    sa = list(range(n))
    k = 1
    while n > 1:
        key = [(rank[i], rank[i + k] if i + k < n else -1) for i in range(n)]
        sa.sort(key=key.__getitem__)
        new = [0] * n
        for j in range(1, n):
            new[sa[j]] = new[sa[j - 1]] + (key[sa[j]] != key[sa[j - 1]])
        rank = new
        if rank[sa[-1]] == n - 1:
            break
        k *= 2
    return sa

def distinct_substrings(s):
    n = len(s)
    if n == 0:
        return 0
    sa = _suffix_array(s)
    rank = [0] * n
    for i, x in enumerate(sa):
        rank[x] = i
    lcp_total, h = 0, 0                        # Kasai: O(n)
    for i in range(n):
        if rank[i] > 0:
            j = sa[rank[i] - 1]
            while i + h < n and j + h < n and s[i + h] == s[j + h]:
                h += 1
            lcp_total += h
            if h:
                h -= 1
        else:
            h = 0
    return n * (n + 1) // 2 - lcp_total

def shortest_palindrome(s):
    t = s + "#" + s[::-1]
    pi = [0] * len(t)
    for i in range(1, len(t)):
        k = pi[i - 1]
        while k and t[i] != t[k]:
            k = pi[k - 1]
        if t[i] == t[k]:
            k += 1
        pi[i] = k
    k = pi[-1] if t else 0                     # longest palindromic prefix of s
    return s[k:][::-1] + s

def count_palindromes(s):
    t = "#" + "#".join(s) + "#"
    n = len(t)
    d = [0] * n
    c = r = 0
    for i in range(n):
        if i < r:
            d[i] = min(r - i, d[2 * c - i])
        while i - d[i] - 1 >= 0 and i + d[i] + 1 < n and t[i - d[i] - 1] == t[i + d[i] + 1]:
            d[i] += 1
        if i + d[i] > r:
            c, r = i, i + d[i]
    return sum((x + 1) // 2 for x in d) if s else 0
```

- **Longest repeat** combines a monotone property with fast checking: if a length-L repeat exists, so does every shorter one. Binary search over L with an O(n) rolling-hash check gives O(n log n). Verifying each hash hit with a real comparison makes the answer exact even if hashes collide.
- **Distinct substrings**: every substring is a prefix of some suffix. In sorted suffix order, adjacent suffixes share exactly LCP prefixes that were already counted, so the total is n(n+1)/2 − ΣLCP. Kasai computes all the LCPs in O(n), because h drops by at most 1 per step.
- **Shortest palindrome**: the prefix function of `s + '#' + reverse(s)` finds the longest prefix of s that equals a suffix of its reverse, which is the longest palindromic prefix. Only the remainder needs mirroring in front.
- **Manacher** reuses mirror information inside the rightmost palindrome, so the radii of all 2n+1 centres cost O(n) in total. In the `#`-interleaved string, a radius of d corresponds to ⌈d/2⌉ palindromes in the original.
