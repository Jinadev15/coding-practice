# Strings and string.h

C has **no string type**. A string is a `char` array whose end is marked by the **null character** `'\0'`. Every string function relies on that terminator. Forget it, or overflow the array, and you get the bugs that fill security advisories. This lesson covers the representation exactly, literals vs arrays, the `<string.h>` functions with their traps, and the safe alternatives.

## 1. Representation: null-terminated char arrays

```c
char s[] = "hi";        /* {'h', 'i', '\0'}: 3 bytes */
```

<div class="figure">
<svg viewBox="0 0 420 100" width="420" xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace, monospace" font-size="15">
  <g fill="none" stroke="currentColor" stroke-opacity=".6"><rect x="40" y="30" width="70" height="40"/><rect x="110" y="30" width="70" height="40"/><rect x="180" y="30" width="70" height="40" stroke="#d29922" stroke-opacity="1" stroke-width="2"/></g>
  <g fill="currentColor"><text x="68" y="56">'h'</text><text x="138" y="56">'i'</text><text x="200" y="56" fill="#d29922">'\0'</text></g>
  <text x="270" y="56" fill="currentColor" font-family="sans-serif" font-size="12" fill-opacity=".75">terminator: value 0</text>
</svg>
<figcaption><code>strlen(s)</code> is 2 (characters before the terminator), while <code>sizeof s</code> is 3 (bytes in the array).</figcaption>
</div>

> [!KEY]
> - Length is found by **scanning for `'\0'`**, so `strlen` is O(n), not O(1).
> - A buffer for a string of up to n characters needs **n + 1** bytes.
> - `'\0'` (the value 0) is different from `'0'` (the character zero, value 48).

## 2. String literals vs char arrays

```c
char arr[] = "robot";       /* a modifiable ARRAY initialised with a copy: 6 bytes on the stack */
const char *lit = "robot";  /* a POINTER to a string literal in read-only memory */

arr[0] = 'R';               /* fine */
/* lit[0] = 'R';            UB: string literals must not be modified (usually a segfault) */
printf("%zu %zu\n", sizeof arr, sizeof lit);   /* 6 8 */
```

Always point to literals with `const char *`, so the compiler stops accidental writes.

## 3. The core `<string.h>` functions

| Function | Does | Trap |
|---|---|---|
| `strlen(s)` | length, not counting `'\0'` | O(n); returns `size_t` |
| `strcpy(d, s)` | copy s, including `'\0'`, into d | **no bounds check**: overflows d |
| `strncpy(d, s, n)` | copy at most n chars | **may not terminate d**; pads with zeros |
| `strcat(d, s)` | append s to d | no bounds check |
| `strcmp(a, b)` | <0, 0, >0 by lexicographic byte order | returns 0 when **equal** |
| `strncmp(a, b, n)` | compare the first n chars | |
| `strchr(s, c)` / `strrchr` | pointer to the first / last c, or NULL | |
| `strstr(h, n)` | pointer to the first occurrence of substring n, or NULL | |
| `strspn` / `strcspn` | length of the prefix made of / free of a char set | `strcspn(s, "\n")` finds the newline |
| `strtok(s, delims)` | split into tokens | **modifies s**, has hidden static state, and skips empty fields |
| `memcpy` / `memmove` / `memset` / `memcmp` | raw byte operations | `memmove` handles overlap, `memcpy` doesn't |

```c
char t[10];
strcpy(t, "abc");
strcat(t, "de");                      /* "abcde" */
if (strcmp(t, "abcde") == 0) puts("equal");      /* NOT if (t == "abcde"): that compares addresses */
printf("%s\n", strstr("robotics", "bot"));       /* botics */
```

> [!DANGER]
> - **`==` on strings compares pointers**, not contents. Use `strcmp(a, b) == 0`.
> - **`if (strcmp(a, b))` means "if DIFFERENT"**: a non-zero result is true.
> - **`strcpy`, `strcat` and `sprintf` can't know the destination size.** Overflowing a stack buffer can overwrite the return address. That's the classic exploit.

## 4. Safe string handling

```c
char buf[16];
snprintf(buf, sizeof buf, "%s-%d", name, id);   /* never overflows; always terminates (if size > 0) */

/* bounded copy that always terminates */
void copy_str(char *dst, size_t size, const char *src) {
    if (size == 0) return;
    size_t n = strlen(src);
    if (n >= size) n = size - 1;
    memcpy(dst, src, n);
    dst[n] = '\0';
}
```

`snprintf` returns the length the output *would* have had, so `if (snprintf(...) >= (int)sizeof buf)` detects truncation. BSD's `strlcpy` and `strlcat` (added to glibc in 2.38) are other bounded options.

## 5. Writing string functions yourself

The classic implementations teach the pointer idioms used everywhere in C:

```c
size_t my_strlen(const char *s) {
    const char *p = s;
    while (*p) p++;                /* stop at '\0' (false) */
    return (size_t)(p - s);        /* pointer difference = count */
}

void reverse(char *s) {
    size_t n = strlen(s);
    for (size_t i = 0, j = n ? n - 1 : 0; i < j; i++, j--) {
        char t = s[i]; s[i] = s[j]; s[j] = t;
    }
}

int my_strcmp(const char *a, const char *b) {
    while (*a && *a == *b) { a++; b++; }
    return (unsigned char)*a - (unsigned char)*b;   /* compare as unsigned bytes */
}
```

## 6. Arrays of strings

```c
const char *names[] = {"left", "right", "up"};        /* array of pointers to literals */
char grid[3][6] = {"left", "right", "up"};            /* 2D char array: each row a fixed buffer */
for (size_t i = 0; i < 3; i++) puts(names[i]);
```

## 7. Strings and encodings

A C string is **bytes**. `strlen("é")` is 2 in UTF-8, so C's string functions count bytes, not characters. For Unicode-aware processing, use a library (ICU) or decode UTF-8 yourself (recall the Python UTF-8 Byte Counter problem).

## 8. Exam-ready answers

> [!EXAM]
> **Strings in C.** C has no built-in string type; a string is a sequence of characters stored in a `char` array and terminated by the null character `'\0'`. A string of n characters therefore requires n + 1 bytes. String literals are stored in static, read-only storage and must not be modified; initialising a `char` array with a literal copies it into modifiable storage. The `<string.h>` library provides functions such as `strlen` (length excluding the terminator), `strcpy`/`strncpy` (copy), `strcat` (concatenate), `strcmp` (compare, returning zero for equal strings), `strchr` and `strstr` (search). Functions like `strcpy`, `strcat` and `gets` perform no bounds checking and can cause buffer overflows; bounded alternatives such as `snprintf` should be preferred.

## 9. Cheat sheet

| Need | Code |
|---|---|
| length | `strlen(s)` |
| equal? | `strcmp(a, b) == 0` |
| safe build or copy | `snprintf(buf, sizeof buf, "%s", src)` |
| find a char / substring | `strchr(s, 'x')`, `strstr(s, "sub")` |
| strip the newline | `s[strcspn(s, "\n")] = '\0';` |
| literal pointer | `const char *p = "text";` |
| char ↔ digit | `c - '0'`, `'0' + d` |

> [!INTERVIEW]
> **"What's wrong with `char *s = "hello"; s[0] = 'H';`?"** `s` points to a string literal, which lives in read-only storage. Modifying it is undefined behaviour, and on Linux it typically segfaults. Use `char s[] = "hello";` to get a modifiable copy, and declare literal pointers as `const char *`, so the compiler rejects the write.
