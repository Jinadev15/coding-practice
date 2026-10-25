---
id: c-libc-from-scratch
title: The libc Functions Every Interview Asks For
difficulty: Medium
order: 1
tags: interview, strings, memmove, strtok_r, atoi, itoa, overflow
time_limit: 3
---
## Statement
Implement these classic functions **without calling their library equivalents** (no `<string.h>` string or memory functions, `strto*`, `ato*` or `printf` family inside them). The judge fuzzes them against libc behaviour.

| Function | Behaviour |
|---|---|
| `size_t my_strlen(const char *s)` | Like `strlen`. |
| `void *my_memmove(void *dst, const void *src, size_t n)` | Like `memmove`. It must be correct for **overlapping** regions in both directions. Returns `dst`. |
| `char *my_strtok_r(char *s, const char *delim, char **save)` | Like POSIX `strtok_r`: skips leading delimiters, terminates the token with `'\0'`, and saves the position. Returns NULL when no tokens are left. Pass `s = NULL` to continue. |
| `int my_atoi(const char *s, int *status)` | Skips leading whitespace (`' '`, `\t`, `\n`, `\v`, `\f`, `\r`), then an optional `+`/`-`, then decimal digits, stopping at the first non-digit. Status 0 means ok. **1** means there were no digits (returns 0). **2** means overflow, and the result **saturates** to `INT_MAX`/`INT_MIN`. Must not use signed overflow (UB) internally. |
| `char *my_itoa(int value, char *buf, int base)` | Writes `value` in `base` 2–36 (digits `0-9a-z`, a leading `-` for negatives in any base) into `buf`, and returns `buf`. **`INT_MIN` must work.** An invalid base writes an empty string. |

## Starter
```c
#define _POSIX_C_SOURCE 200809L   /* keep: the judge's tests use POSIX strtok_r */
#include <stddef.h>
#include <limits.h>

size_t my_strlen(const char *s) { size_t n = 0; while (s[n]) n++; return n; }

void *my_memmove(void *dst, const void *src, size_t n) {
    char *d = dst; const char *s = src;
    for (size_t i = 0; i < n; i++) d[i] = s[i];
    return dst;
}

char *my_strtok_r(char *s, const char *delim, char **save) { (void)s; (void)delim; (void)save; return NULL; }

int my_atoi(const char *s, int *status) {
    int v = 0, sign = 1;
    if (*s == '-') { sign = -1; s++; }
    while (*s >= '0' && *s <= '9') v = v * 10 + (*s++ - '0');
    *status = 0;
    return sign * v;
}

char *my_itoa(int value, char *buf, int base) {
    char tmp[40]; int i = 0, neg = value < 0;
    if (neg) value = -value;
    do { tmp[i++] = "0123456789abcdefghijklmnopqrstuvwxyz"[value % base]; value /= base; } while (value);
    int j = 0; if (neg) buf[j++] = '-';
    while (i) buf[j++] = tmp[--i];
    buf[j] = 0;
    return buf;
}
```

## Driver
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

static unsigned long long rs = 0x9E3779B97F4A7C15ull;
static unsigned rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return (unsigned)rs; }

int main(void) {
    char cmd[32];
    while (scanf("%31s", cmd) == 1) {
        if (!strcmp(cmd, "strings")) {
            printf("%zu %zu %zu\n", my_strlen(""), my_strlen("robot"), my_strlen("a\0b"));
            char buf[] = "0123456789";
            my_memmove(buf + 2, buf, 5); printf("%s\n", buf);
            char buf2[] = "0123456789";
            my_memmove(buf2, buf2 + 3, 6); printf("%s\n", buf2);
            char buf3[] = "abc"; printf("%s %d\n", (char *)my_memmove(buf3, buf3, 3), my_memmove(buf3, "x", 0) == buf3);
            char line[] = ",,move  x=1,y=2;;speed=0.5,,";
            char *save = NULL, *tok = my_strtok_r(line, ",; ", &save);
            while (tok) { printf("[%s]", tok); tok = my_strtok_r(NULL, ",; ", &save); }
            printf("\n");
            char empty[] = ";;;"; save = NULL;
            printf("%s\n", my_strtok_r(empty, ";", &save) ? "token" : "none");
            char a[] = "a b", b[] = "c d"; char *sa, *sb;
            char *t1 = my_strtok_r(a, " ", &sa), *t2 = my_strtok_r(b, " ", &sb);
            char *t3 = my_strtok_r(NULL, " ", &sa), *t4 = my_strtok_r(NULL, " ", &sb);
            printf("interleaved %s %s %s %s\n", t1, t2, t3, t4);
        } else if (!strcmp(cmd, "atoi")) {
            const char *cases[] = {"42", "   -17xyz", "+0", "\t\n 2147483647", "2147483648", "-2147483648", "-2147483649",
                                   "99999999999999999999", "-", "abc", "", "  +", "007", "-0", " 12 34", "+-3"};
            for (size_t i = 0; i < sizeof cases / sizeof *cases; i++) {
                int st = -1, v = my_atoi(cases[i], &st);
                printf("\"%s\" -> %d (status %d)\n", cases[i][0] == '\t' ? "<ws>2147483647" : cases[i], v, st);
            }
        } else if (!strcmp(cmd, "itoa")) {
            char buf[80];
            int vals[] = {0, 255, -255, INT_MAX, INT_MIN, 35, -1};
            int bases[] = {10, 16, 2, 36, 8};
            for (int i = 0; i < 7; i++) {
                for (int j = 0; j < 5; j++) printf("%s ", my_itoa(vals[i], buf, bases[j]));
                printf("\n");
            }
            printf("[%s] [%s]\n", my_itoa(5, buf, 1), my_itoa(5, buf, 37));
        } else if (!strcmp(cmd, "fuzz")) {
            int bad = 0;
            static char a[4096], b[4096];
            for (int it = 0; it < 20000; it++) {
                size_t n = rnd() % 300, so = rnd() % 1500, dof = rnd() % 1500;
                for (int k = 0; k < 2048; k++) a[k] = b[k] = (char)rnd();
                memmove(b + dof, b + so, n);
                if (my_memmove(a + dof, a + so, n) != a + dof || memcmp(a, b, 2048)) bad |= 1;
            }
            char num[64];
            for (int it = 0; it < 200000; it++) {
                long long v = (long long)(int)rnd();
                if (rnd() % 8 == 0) v = v * 7919LL * (rnd() % 3 ? 1 : 100000LL);
                int ws = rnd() % 3;
                int len = snprintf(num, sizeof num, "%.*s%s%lld%s", ws, "  \t", rnd() % 5 == 0 && v >= 0 ? "+" : "", v, rnd() % 4 ? "" : "zz");
                (void)len;
                errno = 0; char *end; long long ref = strtoll(num, &end, 10);
                int exp_st = 0; long long exp = ref;
                if (ref > INT_MAX) { exp = INT_MAX; exp_st = 2; }
                if (ref < INT_MIN) { exp = INT_MIN; exp_st = 2; }
                if (errno == ERANGE) exp_st = 2;
                int st; int got = my_atoi(num, &st);
                if (got != exp || st != exp_st) bad |= 2;
                int x = (int)rnd(), base = 2 + (int)(rnd() % 35);
                char out[80]; my_itoa(x, out, base);
                errno = 0; long long back = strtoll(out, NULL, base);
                if (back != x) bad |= 4;
                if (my_strlen(out) != strlen(out)) bad |= 8;
            }
            for (int it = 0; it < 3000; it++) {
                char s1[200], s2[200]; int n = (int)(rnd() % 199);
                for (int k = 0; k < n; k++) s1[k] = " ,;ab1"[rnd() % 6];
                s1[n] = 0; memcpy(s2, s1, (size_t)n + 1);
                char *p1, *p2, *t1 = my_strtok_r(s1, " ,;", &p1), *t2 = strtok_r(s2, " ,;", &p2);
                while (t1 || t2) {
                    if (!t1 || !t2 || strcmp(t1, t2) || t1 - s1 != t2 - s2) { bad |= 16; break; }
                    t1 = my_strtok_r(NULL, " ,;", &p1); t2 = strtok_r(NULL, " ,;", &p2);
                }
            }
            printf("fuzz bad mask = %d\n", bad);
        }
    }
    return 0;
}
```

## Tests
=== sample
strings
atoi
---
0 5 1
0101234789
3456786789
abc 1
[move][x=1][y=2][speed=0.5]
none
interleaved a c b d
"42" -> 42 (status 0)
"   -17xyz" -> -17 (status 0)
"+0" -> 0 (status 0)
"<ws>2147483647" -> 2147483647 (status 0)
"2147483648" -> 2147483647 (status 2)
"-2147483648" -> -2147483648 (status 0)
"-2147483649" -> -2147483648 (status 2)
"99999999999999999999" -> 2147483647 (status 2)
"-" -> 0 (status 1)
"abc" -> 0 (status 1)
"" -> 0 (status 1)
"  +" -> 0 (status 1)
"007" -> 7 (status 0)
"-0" -> 0 (status 0)
" 12 34" -> 12 (status 0)
"+-3" -> 0 (status 1)
=== hidden
itoa
---
0 0 0 0 0 
255 ff 11111111 73 377 
-255 -ff -11111111 -73 -377 
2147483647 7fffffff 1111111111111111111111111111111 zik0zj 17777777777 
-2147483648 -80000000 -10000000000000000000000000000000 -zik0zk -20000000000 
35 23 100011 z 43 
-1 -1 -1 -1 -1 
[] []
=== hidden
fuzz
---
fuzz bad mask = 0

## Hints
- `memmove`: if `dst < src` (or the regions don't overlap), copy forwards, otherwise copy backwards from the end. Compare as `unsigned char *` (or `uintptr_t`).
- `strtok_r`: write a helper `in(c, delim)`. Skip delimiters, and if you reach `'\0'`, store the position and return NULL. Otherwise scan to the next delimiter, write `'\0'` there, and save the position just after it.
- `atoi` without UB: accumulate the **magnitude** in an `unsigned long long` and stop growing once it exceeds `2147483648`. Then decide: positive values above `INT_MAX` saturate, and negative magnitudes above `2147483648` saturate. Negate through `unsigned` arithmetic or `-(long long)m`.
- `itoa`: convert `(unsigned)value` (or `0u - (unsigned)value` for negatives) to digits. That's how `INT_MIN` works without overflow.

## Solution
```c
#define _POSIX_C_SOURCE 200809L   /* keep: the judge's tests use POSIX strtok_r */
#include <stddef.h>
#include <limits.h>

size_t my_strlen(const char *s) {
    const char *p = s;
    while (*p) p++;
    return (size_t)(p - s);
}

void *my_memmove(void *dst, const void *src, size_t n) {
    unsigned char *d = dst;
    const unsigned char *s = src;
    if (d == s || n == 0) return dst;
    if (d < s) {                                  /* forward copy is safe */
        for (size_t i = 0; i < n; i++) d[i] = s[i];
    } else {                                      /* dst after src: copy backwards */
        for (size_t i = n; i-- > 0;) d[i] = s[i];
    }
    return dst;
}

static int is_delim(char c, const char *delim) {
    for (; *delim; delim++) if (*delim == c) return 1;
    return 0;
}

char *my_strtok_r(char *s, const char *delim, char **save) {
    if (s == NULL) s = *save;
    if (s == NULL) return NULL;
    while (*s && is_delim(*s, delim)) s++;        /* skip leading delimiters */
    if (*s == '\0') { *save = s; return NULL; }
    char *tok = s;
    while (*s && !is_delim(*s, delim)) s++;
    if (*s) { *s = '\0'; *save = s + 1; }
    else *save = s;
    return tok;
}

static int is_space(char c) { return c == ' ' || c == '\t' || c == '\n' || c == '\v' || c == '\f' || c == '\r'; }

int my_atoi(const char *s, int *status) {
    while (is_space(*s)) s++;
    int neg = 0;
    if (*s == '+' || *s == '-') neg = (*s++ == '-');
    if (*s < '0' || *s > '9') { *status = 1; return 0; }
    const unsigned long long limit = (unsigned long long)INT_MAX + 1;   /* |INT_MIN| */
    unsigned long long mag = 0;
    int over = 0;
    for (; *s >= '0' && *s <= '9'; s++) {
        if (!over) {
            mag = mag * 10 + (unsigned)(*s - '0');
            if (mag > limit) over = 1;            /* stop growing: can't wrap */
        }
    }
    if (!neg && mag > (unsigned long long)INT_MAX) over = 1;
    if (over) { *status = 2; return neg ? INT_MIN : INT_MAX; }
    *status = 0;
    return neg ? (int)(-(long long)mag) : (int)mag;
}

char *my_itoa(int value, char *buf, int base) {
    static const char digits[] = "0123456789abcdefghijklmnopqrstuvwxyz";
    if (base < 2 || base > 36) { buf[0] = '\0'; return buf; }
    unsigned mag = value < 0 ? 0u - (unsigned)value : (unsigned)value;   /* INT_MIN safe */
    char tmp[40];
    int i = 0;
    do { tmp[i++] = digits[mag % (unsigned)base]; mag /= (unsigned)base; } while (mag);
    int j = 0;
    if (value < 0) buf[j++] = '-';
    while (i) buf[j++] = tmp[--i];
    buf[j] = '\0';
    return buf;
}
```

- **`memmove`** picks the copy direction: forwards when the destination starts before the source, backwards otherwise. Overlapping bytes are then always read before they're overwritten. The starter's forward-only loop smears the first bytes across an overlapping right shift.
- **`strtok_r`** keeps its state in the caller's `save` pointer instead of a hidden static like `strtok`, so it's reentrant and thread-safe, and two tokenisers can be interleaved (the "interleaved" test).
- **`atoi` without undefined behaviour** accumulates the magnitude in a wider unsigned type and stops growing past `|INT_MIN|`. `INT_MIN` itself parses correctly, and saturation reports overflow instead of wrapping. The real `atoi` has undefined behaviour on overflow, which is why production code uses `strtol` with `errno`.
- **`itoa` and `INT_MIN`**: `-INT_MIN` overflows `int`, but `0u - (unsigned)value` is well defined modulo 2³² and gives the correct magnitude 2147483648.
