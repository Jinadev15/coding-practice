# String Algorithms in C

C strings are raw `char` arrays ending in `'\0'`. There's no string class to hide the cost of operations, so you design string algorithms with the memory model in front of you: in-place edits, explicit lengths, buffer bounds. This lesson covers the core algorithmic toolkit:
- in-place reversal and word reversal
- palindromes
- naive search and why it's quadratic
- **KMP**, linear-time matching through the prefix function
- the **Z-algorithm**
- **Rabin–Karp** rolling hashes

These appear in parsers, log scanners, intrusion detection, DNA analysis and interviews.

## 1. Ground rules for C string code

> [!KEY]
> - `strlen` is **O(n)**: it walks to the `'\0'`. Calling it in a loop condition (`for (i = 0; i < strlen(s); i++)`) makes the loop O(n²). Compute it once.
> - Know whether you own the buffer and its capacity. String literals are **read-only**: `char *s = "abc"; s[0] = 'x';` is UB. Use `char s[] = "abc";` for a modifiable copy.
> - `char` may be signed. Before passing to `<ctype.h>` functions or using a character as an array index, cast it: `isalpha((unsigned char)c)`, `count[(unsigned char)c]++`.
> - Many algorithms work on `(const char *s, size_t n)` pairs rather than NUL-terminated strings. That makes them work on substrings, binary data and buffers that may contain `'\0'`.

## 2. Reversal, in place

```c
void reverse_range(char *s, size_t i, size_t j) {     /* reverse s[i..j), j exclusive */
    while (i + 1 < j) {                               /* careful: j-- on size_t 0 wraps */
        char t = s[i]; s[i] = s[--j]; s[j] = t;
        i++;
    }
}

void reverse(char *s) { reverse_range(s, 0, strlen(s)); }
```

### Reverse the order of words, in place, in O(n)

Reverse the whole string, then reverse each word back:

```
"the robot moves"  →  "sevom tobor eht"  →  "moves robot the"
```

```c
void reverse_words(char *s) {
    size_t n = strlen(s);
    reverse_range(s, 0, n);
    size_t i = 0;
    while (i < n) {
        while (i < n && s[i] == ' ') i++;
        size_t start = i;
        while (i < n && s[i] != ' ') i++;
        reverse_range(s, start, i);
    }
}
```

That's two passes, O(1) extra space. The same trick does **array rotation** by k: reverse all, reverse the first k, reverse the rest.

## 3. Palindromes

```c
#include <ctype.h>
#include <stdbool.h>

/* ignore non-alphanumerics and case: "A man, a plan, a canal: Panama" → true */
bool is_palindrome(const char *s) {
    size_t i = 0, j = strlen(s);
    while (i < j) {
        if (!isalnum((unsigned char)s[i])) { i++; continue; }
        if (!isalnum((unsigned char)s[j - 1])) { j--; continue; }
        if (tolower((unsigned char)s[i]) != tolower((unsigned char)s[j - 1])) return false;
        i++; j--;
    }
    return true;
}
```

The **longest palindromic substring** can be found by expanding around each of the 2n − 1 centres in O(n²) time and O(1) space, or by Manacher's algorithm in O(n).

## 4. Naive pattern search, and its worst case

```c
/* first index of pattern p (length m) in text t (length n), or -1 */
ptrdiff_t naive_find(const char *t, size_t n, const char *p, size_t m) {
    if (m == 0) return 0;
    for (size_t i = 0; i + m <= n; i++) {
        size_t j = 0;
        while (j < m && t[i + j] == p[j]) j++;
        if (j == m) return (ptrdiff_t)i;
    }
    return -1;
}
```

On text `aaaa…a` and pattern `aaa…ab`, every alignment matches m − 1 characters before failing, so the cost is Θ(nm). The waste: after a partial match we already *know* the text characters, yet we move by one and re-compare them. (glibc's `strstr` uses the Two-Way algorithm, which is linear, so the naive version is mainly a teaching baseline.)

## 5. KMP: never re-read the text

The **prefix function** (failure function) of the pattern: `pi[i]` = the length of the longest **proper** prefix of `p[0..i]` that is also a suffix of it.

| i | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| p | a | b | a | b | a | c |
| pi | 0 | 0 | 1 | 2 | 3 | 0 |

After matching `ababa` and failing on the next character, the pattern can slide so that its prefix `aba` (`pi[4] = 3`) lines up with the text's suffix `aba`. Those 3 characters are known to match, so we never step backwards in the text.

```c
void prefix_function(const char *p, size_t m, size_t *pi) {
    pi[0] = 0;
    for (size_t i = 1; i < m; i++) {
        size_t k = pi[i - 1];
        while (k > 0 && p[i] != p[k]) k = pi[k - 1];   /* fall back to shorter borders */
        if (p[i] == p[k]) k++;
        pi[i] = k;
    }
}

/* calls report(pos) for every occurrence (overlapping ones included); returns the count */
size_t kmp_search(const char *t, size_t n, const char *p, size_t m, void (*report)(size_t)) {
    if (m == 0) return 0;
    size_t *pi = malloc(m * sizeof *pi);
    if (!pi) return 0;
    prefix_function(p, m, pi);
    size_t count = 0, k = 0;                     /* k = number of pattern chars currently matched */
    for (size_t i = 0; i < n; i++) {
        while (k > 0 && t[i] != p[k]) k = pi[k - 1];
        if (t[i] == p[k]) k++;
        if (k == m) {
            if (report) report(i + 1 - m);
            count++;
            k = pi[k - 1];                       /* continue: allows overlapping matches */
        }
    }
    free(pi);
    return count;
}
```

> [!KEY]
> KMP runs in **O(n + m)**. Amortised argument: `k` increases by at most 1 per text character, and each fallback `k = pi[k-1]` strictly decreases it, so the total number of fallbacks is ≤ n. The prefix function also answers other questions directly:
> - The **shortest period** of a string is `m - pi[m-1]`. If it divides `m`, the string is that block repeated.
> - Searching for `p + '#' + t` gives every match where `pi == m`.

## 6. The Z-algorithm

`z[i]` = the length of the longest substring starting at `i` that matches a prefix of `s` (with `z[0]` defined as `n` or 0). It's computed in O(n) by maintaining the rightmost matched window `[l, r)`:

```c
void z_function(const char *s, size_t n, size_t *z) {
    if (n == 0) return;
    z[0] = n;
    size_t l = 0, r = 0;                         /* s[l..r) matches s[0..r-l) */
    for (size_t i = 1; i < n; i++) {
        z[i] = 0;
        if (i < r) z[i] = (r - i < z[i - l]) ? r - i : z[i - l];   /* reuse what we know */
        while (i + z[i] < n && s[z[i]] == s[i + z[i]]) z[i]++;
        if (i + z[i] > r) { l = i; r = i + z[i]; }
    }
}
```

To search, build `p + '\x01' + t` with a separator that occurs in neither, and report every position whose z-value equals `m`.

## 7. Rabin–Karp: hashing windows in O(1)

Treat a window of m characters as a number in base B modulo a prime M, and slide it in O(1):

`h(t[i+1..i+m]) = ((h - t[i]·B^(m-1)) · B + t[i+m]) mod M`

```c
#define B 257u
#define MOD 1000000007u

ptrdiff_t rk_find(const char *t, size_t n, const char *p, size_t m) {
    if (m == 0) return 0;
    if (m > n) return -1;
    uint64_t hp = 0, ht = 0, pow = 1;                    /* pow = B^(m-1) mod MOD */
    for (size_t i = 0; i < m; i++) {
        hp = (hp * B + (unsigned char)p[i]) % MOD;
        ht = (ht * B + (unsigned char)t[i]) % MOD;
        if (i) pow = pow * B % MOD;
    }
    for (size_t i = 0; ; i++) {
        if (hp == ht && memcmp(t + i, p, m) == 0) return (ptrdiff_t)i;   /* verify: hashes can collide */
        if (i + m >= n) return -1;
        ht = (ht + MOD - (unsigned char)t[i] * pow % MOD) % MOD;         /* remove the old char (stay non-negative) */
        ht = (ht * B + (unsigned char)t[i + m]) % MOD;                    /* add the new char */
    }
}
```

- `uint64_t` arithmetic stays far below overflow, because both factors are < 2³⁰.
- Adding `MOD` before subtracting keeps the value non-negative in unsigned arithmetic.
- Rabin–Karp is O(n + m) expected and O(nm) worst case (if every window collides), which is why the `memcmp` verification is mandatory.
- Its strength is searching **many patterns** of the same length at once (hash them into a set), and finding duplicate substrings (plagiarism detection, `rsync`'s rolling checksum).

## 8. Which matcher when?

| Algorithm | Preprocess | Search | Best for |
|---|---|---|---|
| naive | — | O(nm) worst | tiny patterns, simplicity |
| KMP | O(m) | O(n) | streaming text (never backs up), guaranteed linear time |
| Z-algorithm | O(n + m) | — | prefix questions, simple to code correctly |
| Rabin–Karp | O(m) | O(n) expected | many patterns, 2-D matching, duplicate detection |
| Boyer–Moore(–Horspool) | O(m + σ) | sublinear on average | long patterns, large alphabets (`grep`) |
| Aho–Corasick | O(Σ pattern lengths) | O(n + matches) | a dictionary of patterns (antivirus, IDS) |
| suffix array / automaton | O(n log n) / O(n) | O(m log n) / O(m) | many queries on one fixed text |

## 9. Exam-ready answers

> [!EXAM]
> **The Knuth–Morris–Pratt algorithm.** KMP finds all occurrences of a pattern of length m in a text of length n in O(n + m) time. It preprocesses the pattern into a prefix (failure) function, where `pi[i]` is the length of the longest proper prefix of `p[0..i]` that is also a suffix of it. During the search, when a mismatch occurs after k matched characters, the algorithm doesn't move back in the text; it continues with `k = pi[k-1]` matched characters, reusing the information that the matched text suffix equals that pattern prefix. Because the matched length increases at most once per text character and every fallback decreases it, the total work is linear.

## 10. Cheat sheet

| Need | Technique |
|---|---|
| reverse in place | two indices, swap, move inwards |
| reverse words | reverse all, then each word |
| rotate by k | three reversals |
| palindrome check | two pointers, `(unsigned char)` casts for `ctype` |
| all occurrences, linear | KMP or Z on `p + sep + t` |
| shortest period | `m - pi[m-1]` |
| many same-length patterns | Rabin–Karp with a hash set |
| character counts | `size_t cnt[UCHAR_MAX + 1]` indexed by `(unsigned char)c` |

> [!INTERVIEW]
> **"Is s2 a rotation of s1?"** Check `strlen(s1) == strlen(s2)`, then whether s2 occurs in `s1 + s1` (any rotation of s1 is a substring of s1 concatenated with itself). With KMP that's O(n). Mention allocating 2n + 1 bytes for the concatenation, or matching against `s1[i % n]` virtually so no allocation is needed.
