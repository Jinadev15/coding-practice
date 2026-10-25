---
id: c-const-words
title: Const-Correct Word Scanner
difficulty: Medium
order: 1
tags: const correctness, pointers into strings
---
## Statement
Write const-correct functions that **never copy** the input. They return pointers into it:

- `const char *skip_spaces(const char *s)`: the first non-space character (or the terminating `'\0'`)
- `const char *next_word(const char *s, size_t *len)`: skips spaces, then returns the start of the next word and its length through `len`, or `NULL` if there are no more words
- `size_t count_vowels(const char *s, size_t len)`: counts `aeiou` (case-insensitive) in the first `len` characters

The driver prints each word with `%.*s` (a slice, with no copying), plus its vowel count, and finally the longest word.

## Starter
```c
#include <stddef.h>
#include <ctype.h>

const char *skip_spaces(const char *s) {
    return s;
}

const char *next_word(const char *s, size_t *len) {
    *len = 0;
    return NULL;
}

size_t count_vowels(const char *s, size_t len) {
    return 0;
}
```

## Driver
```c
#include <stdio.h>
#include <string.h>
int main(void) {
    char line[512];
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\n")] = '\0';
        const char *p = line, *best = NULL;
        size_t len, best_len = 0;
        while ((p = next_word(p, &len)) != NULL) {
            printf("[%.*s:%zu] ", (int)len, p, count_vowels(p, len));
            if (len > best_len) { best_len = len; best = p; }
            p += len;
        }
        if (best) printf("longest=%.*s\n", (int)best_len, best);
        else printf("no words\n");
    }
    return 0;
}
```

## Tests
=== sample
the quick  brown FOX
---
[the:1] [quick:2] [brown:1] [FOX:1] longest=quick
=== hidden
   
Robotics
a e  i
---
no words
[Robotics:3] longest=Robotics
[a:1] [e:1] [i:1] longest=a

## Hints
- `const char *` means you may read the characters but not modify them; returning a pointer *into* the input avoids any copying.
- `skip_spaces`: advance the pointer while `*s` is a space (use `isspace((unsigned char)*s)`).
- `next_word`: skip spaces, remember the start, walk to the next space, and store `end - start` through `len`; return `NULL` at the end of the string.

## Solution
Every function takes `const char *` and returns `const char *`: it promises not to modify the text and doesn't let callers modify it through the returned pointer either.

```c
#include <stddef.h>
#include <ctype.h>

const char *skip_spaces(const char *s) {
    while (*s && isspace((unsigned char)*s)) s++;
    return s;
}

const char *next_word(const char *s, size_t *len) {
    s = skip_spaces(s);
    if (*s == '\0') { *len = 0; return NULL; }
    const char *e = s;
    while (*e && !isspace((unsigned char)*e)) e++;
    *len = (size_t)(e - s);
    return s;
}

size_t count_vowels(const char *s, size_t len) {
    size_t c = 0;
    for (size_t i = 0; i < len; i++) {
        int ch = tolower((unsigned char)s[i]);
        if (ch == 'a' || ch == 'e' || ch == 'i' || ch == 'o' || ch == 'u') c++;
    }
    return c;
}
```

A pointer + length pair (a "string view") lets you process words without allocating or modifying the line. That's the idea behind C++17's `std::string_view` and Rust's `&str`. If `next_word` returned `char *` from a `const char *` input, it would silently strip the const promise, which `strchr` in the C standard library famously does (C23 fixes it with generic overloads).
