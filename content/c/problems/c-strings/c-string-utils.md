---
id: c-string-utils
title: Write string.h Yourself
difficulty: Medium
order: 1
tags: strings, pointers, null terminator
---
## Statement
Implement these without calling **any** `<string.h>` function:

| Function | Behaviour |
|---|---|
| `size_t my_strlen(const char *s)` | length |
| `int my_strcmp(const char *a, const char *b)` | <0, 0, >0 like strcmp (compare bytes as `unsigned char`) |
| `void my_strrev(char *s)` | reverse in place |
| `size_t my_strlcpy(char *dst, const char *src, size_t size)` | copy at most `size-1` chars, **always** terminate (if size > 0), and return `strlen(src)` (so the caller can detect truncation) |
| `int count_words(const char *s)` | count maximal runs of non-space characters (spaces only) |

## Starter
```c
#include <stddef.h>

size_t my_strlen(const char *s) { return 0; }
int my_strcmp(const char *a, const char *b) { return 0; }
void my_strrev(char *s) { }
size_t my_strlcpy(char *dst, const char *src, size_t size) { return 0; }
int count_words(const char *s) { return 0; }
```

## Driver
```c
#include <stdio.h>
#include <string.h>
int main(void) {
    char a[256], b[256];
    while (fgets(a, sizeof a, stdin) && fgets(b, sizeof b, stdin)) {
        a[strcspn(a, "\n")] = 0; b[strcspn(b, "\n")] = 0;
        int c = my_strcmp(a, b);
        printf("len=%zu,%zu cmp=%d words=%d,%d\n", my_strlen(a), my_strlen(b),
               (c > 0) - (c < 0), count_words(a), count_words(b));
        char small[6];
        size_t need = my_strlcpy(small, a, sizeof small);
        my_strrev(b);
        printf("copy=[%s] truncated=%s rev=[%s]\n", small, need >= sizeof small ? "yes" : "no", b);
    }
    return 0;
}
```

## Tests
=== sample
hello world
hello
---
len=11,5 cmp=1 words=2,1
copy=[hello] truncated=yes rev=[olleh]
=== hidden
abc
abd
  spaced   out  
x
---
len=3,3 cmp=-1 words=1,1
copy=[abc] truncated=no rev=[dba]
len=16,1 cmp=-1 words=2,1
copy=[  spa] truncated=yes rev=[x]
=== hidden

same
---
len=0,4 cmp=-1 words=0,1
copy=[] truncated=no rev=[emas]

## Hints
- A C string ends at the byte `'\0'`; `my_strlen` walks until it finds it.
- In `my_strcmp`, advance while the characters are equal and not `'\0'`, then return the difference of the current bytes cast to `unsigned char`.
- `my_strlcpy`: copy at most `size - 1` characters, always write the terminating `'\0'` when `size > 0`, and return the full source length so the caller can detect truncation.

## Solution
```c
#include <stddef.h>

size_t my_strlen(const char *s) {
    const char *p = s;
    while (*p) p++;
    return (size_t)(p - s);
}

int my_strcmp(const char *a, const char *b) {
    while (*a && *a == *b) { a++; b++; }
    return (unsigned char)*a - (unsigned char)*b;
}

void my_strrev(char *s) {
    size_t n = my_strlen(s);
    if (n < 2) return;
    for (size_t i = 0, j = n - 1; i < j; i++, j--) {
        char t = s[i]; s[i] = s[j]; s[j] = t;
    }
}

size_t my_strlcpy(char *dst, const char *src, size_t size) {
    size_t len = my_strlen(src);
    if (size > 0) {
        size_t n = len < size - 1 ? len : size - 1;
        for (size_t i = 0; i < n; i++) dst[i] = src[i];
        dst[n] = '\0';
    }
    return len;
}

int count_words(const char *s) {
    int words = 0, in_word = 0;
    for (; *s; s++) {
        if (*s == ' ') in_word = 0;
        else if (!in_word) { in_word = 1; words++; }
    }
    return words;
}
```

`my_strcmp` compares as `unsigned char` because the C standard specifies `strcmp` that way. With signed chars, bytes ≥ 128 would sort *before* ASCII. `strlcpy` returns the source length, so `ret >= size` signals truncation, the same contract as `snprintf`. The `n < 2` guard in `my_strrev` avoids `n - 1` underflowing for the empty string.
