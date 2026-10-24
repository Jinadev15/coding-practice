---
id: c-pattern-toolkit
title: Linear-Time Pattern Toolkit (KMP, Periods, In-Place Word Reversal)
difficulty: Hard
order: 1
tags: KMP, prefix function, string periods, in-place algorithms, rotations
time_limit: 2
---
## Statement
Implement four string algorithms used by a robot's log scanner. All must be **linear time**: the hidden tests include adversarial inputs (a text of 2 million `a`s, and a pattern of 100 000 `a`s ending in `b`) on which naive O(n·m) matching takes minutes.

```c
/* Count ALL occurrences of p (length m) in t (length n), overlapping ones included.
   Store the first min(count, cap) starting positions in out[]. Return the total count. m == 0 → return 0. */
size_t find_all(const char *t, size_t n, const char *p, size_t m, size_t *out, size_t cap);

/* Smallest k >= 1 such that s[i] == s[i + k] for all valid i (k == n if no smaller one); n >= 1. */
size_t shortest_period(const char *s, size_t n);

/* In place, O(1) extra space: reverse all characters, then reverse each maximal run of
   non-space characters back. Words come out in reverse order, and the spacing pattern is mirrored. */
void reverse_words(char *s);

/* 1 if b is a rotation of a (same length, and b occurs in a+a), else 0. Two empty strings are rotations. */
int is_rotation(const char *a, const char *b);
```

The driver commands are:
- `find TEXT PATTERN`
- `period S`
- `rotation A B`
- `words <rest of line>`, which keeps the spacing exactly
- `worst N M`, an adversarial search
- `fuzz SEED K`, random tiny strings checked against brute force

## Starter
```c
#include <stddef.h>
#include <string.h>

size_t find_all(const char *t, size_t n, const char *p, size_t m, size_t *out, size_t cap) {
    size_t count = 0;
    if (m == 0) return 0;
    for (size_t i = 0; i + m <= n; i++)
        if (memcmp(t + i, p, m) == 0) { if (count < cap) out[count] = i; count++; }
    return count;
}
size_t shortest_period(const char *s, size_t n) { (void)s; return n; }
void reverse_words(char *s) { (void)s; }
int is_rotation(const char *a, const char *b) { return strlen(a) == strlen(b); }
```

## Driver
```c
#include <stdio.h>
#include <stdlib.h>

static unsigned long long drv_st;
static unsigned drv_rnd(void) {
    drv_st = drv_st * 6364136223846793005ULL + 1442695040888963407ULL;
    return (unsigned)(drv_st >> 33);
}
static size_t drv_count(const char *t, size_t n, const char *p, size_t m) {
    size_t c = 0;
    if (!m) return 0;
    for (size_t i = 0; i + m <= n; i++) if (!memcmp(t + i, p, m)) c++;
    return c;
}
static size_t drv_period(const char *s, size_t n) {
    for (size_t k = 1; k < n; k++) {
        size_t i = 0;
        while (i + k < n && s[i] == s[i + k]) i++;
        if (i + k == n) return k;
    }
    return n;
}
static int drv_rot(const char *a, const char *b) {
    size_t n = strlen(a);
    if (strlen(b) != n) return 0;
    if (!n) return 1;
    for (size_t r = 0; r < n; r++) {
        size_t i = 0;
        while (i < n && a[(i + r) % n] == b[i]) i++;
        if (i == n) return 1;
    }
    return 0;
}

static char line[1 << 16];

int main(void) {
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\n")] = '\0';
        char cmd[16] = {0};
        sscanf(line, "%15s", cmd);
        if (!strcmp(cmd, "find")) {
            char t[8192], p[8192];
            if (sscanf(line, "%*s %8191s %8191s", t, p) != 2) continue;
            size_t out[10];
            size_t c = find_all(t, strlen(t), p, strlen(p), out, 10);
            printf("find %s in %s: %zu [", p, t, c);
            for (size_t i = 0; i < c && i < 10; i++) printf(i ? " %zu" : "%zu", out[i]);
            printf("]\n");
        } else if (!strcmp(cmd, "period")) {
            char s[8192];
            if (sscanf(line, "%*s %8191s", s) != 1) continue;
            printf("period %s: %zu\n", s, shortest_period(s, strlen(s)));
        } else if (!strcmp(cmd, "rotation")) {
            char a[8192] = "", b[8192] = "";
            int k = sscanf(line, "%*s %8191s %8191s", a, b);
            if (k < 2) b[0] = '\0';
            if (k < 1) a[0] = '\0';
            printf("rotation %s %s: %s\n", a, b, is_rotation(a, b) ? "yes" : "no");
        } else if (!strcmp(cmd, "words")) {
            char *rest = line + 5;
            if (*rest == ' ') rest++;
            reverse_words(rest);
            printf("words: [%s]\n", rest);
        } else if (!strcmp(cmd, "worst")) {
            size_t n, m;
            if (sscanf(line, "%*s %zu %zu", &n, &m) != 2) continue;
            char *t = malloc(n + 1), *p = malloc(m + 1);
            memset(t, 'a', n); t[n] = '\0';
            memset(p, 'a', m); p[m] = '\0';
            size_t out[3];
            size_t full = find_all(t, n, p, m, out, 3);
            p[m - 1] = 'b';
            size_t none = find_all(t, n, p, m, out, 3);
            size_t per = shortest_period(t, n);
            char *u = malloc(n + 1);                      /* "aaa...ab" period test: no proper period */
            memcpy(u, t, n + 1); u[n - 1] = 'b';
            size_t per2 = shortest_period(u, n);
            printf("worst n=%zu m=%zu: all-a matches=%zu, a..ab matches=%zu, period(a^n)=%zu, period(a^(n-1)b)=%zu\n",
                   n, m, full, none, per, per2);
            free(t); free(p); free(u);
        } else if (!strcmp(cmd, "fuzz")) {
            unsigned long long seed; unsigned k;
            if (sscanf(line, "%*s %llu %u", &seed, &k) != 2) continue;
            drv_st = seed;
            unsigned bad = 0;
            for (unsigned it = 0; it < k && !bad; it++) {
                char t[40], p[8], a[12], b[12];
                size_t n = drv_rnd() % 40, m = 1 + drv_rnd() % 7, an = drv_rnd() % 12;
                for (size_t i = 0; i < n; i++) t[i] = (char)('a' + drv_rnd() % 2);
                for (size_t i = 0; i < m; i++) p[i] = (char)('a' + drv_rnd() % 2);
                for (size_t i = 0; i < an; i++) a[i] = (char)('a' + drv_rnd() % 2);
                a[an] = '\0';
                size_t r = an ? drv_rnd() % an : 0;
                for (size_t i = 0; i < an; i++) b[i] = a[(i + r) % an];
                b[an] = '\0';
                if (drv_rnd() % 3 == 0 && an) b[drv_rnd() % an] ^= 3;    /* corrupt: 'a'<->'b' */
                size_t out[40];
                if (find_all(t, n, p, m, out, 40) != drv_count(t, n, p, m)) bad = 1;
                if (n && shortest_period(t, n) != drv_period(t, n)) bad = 2;
                if (is_rotation(a, b) != drv_rot(a, b)) bad = 3;
            }
            printf("fuzz %u: %s\n", k, bad == 0 ? "ok" : bad == 1 ? "find_all WRONG" : bad == 2 ? "shortest_period WRONG" : "is_rotation WRONG");
        }
    }
    return 0;
}
```

## Tests
=== sample
find abababa aba
find aaaa b
period abcabcab
period abcd
rotation robot botro
rotation robot torob
words the robot moves
words   lead and  trail 
---
find aba in abababa: 3 [0 2 4]
find b in aaaa: 0 []
period abcabcab: 3
period abcd: 4
rotation robot botro: yes
rotation robot torob: no
words: [moves robot the]
words: [ trail  and lead  ]
=== hidden
find a a
find abc abcd
find aaaaaaaaaaaaaa aa
period a
period aaaa
period abaababaab
period aabaa
rotation a a
rotation ab ab
rotation ab abc
rotation aab aba
rotation aab bba
words x
words 
words ab  cd
fuzz 7 20000
---
find a in a: 1 [0]
find abcd in abc: 0 []
find aa in aaaaaaaaaaaaaa: 13 [0 1 2 3 4 5 6 7 8 9]
period a: 1
period aaaa: 1
period abaababaab: 5
period aabaa: 3
rotation a a: yes
rotation ab ab: yes
rotation ab abc: no
rotation aab aba: yes
rotation aab bba: no
words: [x]
words: []
words: [cd  ab]
fuzz 20000: ok
=== hidden
worst 2000000 100000
worst 1000000 999999
fuzz 8 50000
---
worst n=2000000 m=100000: all-a matches=1900001, a..ab matches=0, period(a^n)=1, period(a^(n-1)b)=2000000
worst n=1000000 m=999999: all-a matches=2, a..ab matches=0, period(a^n)=1, period(a^(n-1)b)=1000000
fuzz 50000: ok

## Hints
- `find_all`: build the KMP prefix function of p (O(m)), then scan t keeping k = the number of matched characters. On a full match, record `i + 1 - m` and set `k = pi[m - 1]` so overlapping matches are found.
- `shortest_period(s) = n - pi[n - 1]`, where `pi` is the prefix function of s itself.
- `is_rotation` without allocating: run KMP for b over the *virtual* text `a[i % n]` for i in `[0, 2n - 1)`.
- `reverse_words`: write `rev(s, i, j)` that reverses `s[i..j)`. Reverse `[0, n)`, then scan for runs of non-spaces and reverse each one.

## Solution
```c
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

static size_t *prefix_function(const char *p, size_t m) {
    size_t *pi = malloc(m * sizeof *pi);
    if (!pi) return NULL;
    pi[0] = 0;
    for (size_t i = 1; i < m; i++) {
        size_t k = pi[i - 1];
        while (k > 0 && p[i] != p[k]) k = pi[k - 1];
        if (p[i] == p[k]) k++;
        pi[i] = k;
    }
    return pi;
}

size_t find_all(const char *t, size_t n, const char *p, size_t m, size_t *out, size_t cap) {
    if (m == 0 || m > n) return 0;
    size_t *pi = prefix_function(p, m);
    if (!pi) return 0;
    size_t count = 0, k = 0;
    for (size_t i = 0; i < n; i++) {
        while (k > 0 && t[i] != p[k]) k = pi[k - 1];
        if (t[i] == p[k]) k++;
        if (k == m) {
            if (count < cap) out[count] = i + 1 - m;
            count++;
            k = pi[k - 1];
        }
    }
    free(pi);
    return count;
}

size_t shortest_period(const char *s, size_t n) {
    size_t *pi = prefix_function(s, n);
    if (!pi) return n;
    size_t per = n - pi[n - 1];
    free(pi);
    return per;
}

static void rev(char *s, size_t i, size_t j) {          /* reverse s[i..j) */
    while (i + 1 < j) {
        char c = s[i]; s[i] = s[--j]; s[j] = c;
        i++;
    }
}

void reverse_words(char *s) {
    size_t n = strlen(s);
    rev(s, 0, n);
    for (size_t i = 0; i < n; ) {
        while (i < n && s[i] == ' ') i++;
        size_t start = i;
        while (i < n && s[i] != ' ') i++;
        rev(s, start, i);
    }
}

int is_rotation(const char *a, const char *b) {
    size_t n = strlen(a);
    if (strlen(b) != n) return 0;
    if (n == 0) return 1;
    size_t *pi = prefix_function(b, n);
    if (!pi) return 0;
    size_t k = 0;
    int found = 0;
    for (size_t i = 0; i + 1 < 2 * n && !found; i++) {   /* virtual text a+a without its last char */
        char c = a[i % n];
        while (k > 0 && c != b[k]) k = pi[k - 1];
        if (c == b[k]) k++;
        if (k == n) found = 1;
    }
    free(pi);
    return found;
}
```

All four functions share one tool, the **prefix function**:
- **Matching**: KMP never moves backwards in the text. After a mismatch or a full match, it continues from the longest border, so overlapping matches cost nothing extra and the total work is O(n + m) even on `aaaa…` inputs.
- **Periods**: if the longest proper border of s has length b, then s[i] = s[i + (n − b)] for every valid i, and no smaller shift works. That's because a smaller period would imply a longer border.
- **Rotations**: b is a rotation of a exactly when b occurs in a + a. Scanning `a[i % n]` avoids allocating the 2n-byte concatenation.
- **Word reversal**: two reversal passes give the in-place O(n), O(1)-space result.
