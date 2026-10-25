# Study guide: Special quiz 1

Quiz 1 tests C fundamentals under pressure: strings, pointers, `malloc`/`free` and careful parsing. In C, *every* byte is your responsibility.

## 1. Shell-style command splitter — state machines

Splitting `echo "hello world" 'a b' c\ d` into words isn't `strtok`. Quotes and backslashes change the meaning of a space. Model it as a **finite state machine**:

```text
state NORMAL:   space → end word;  '"' → DQUOTE;  '\'' → SQUOTE;  '\\' → take next char literally
state DQUOTE:   '"' → NORMAL;      '\\' → escape next;   anything else → append
state SQUOTE:   '\'' → NORMAL;     anything else → append (no escapes)
```

```c
enum state { NORMAL, DQ, SQ };
enum state st = NORMAL;
for (const char *p = line; *p; p++) {
    switch (st) {
    case NORMAL:
        if (*p == ' ') { finish_word(); }
        else if (*p == '"') { st = DQ; in_word = 1; }
        /* ... */
        break;
    /* ... */
    }
}
if (st != NORMAL) { /* error: unterminated quote */ }
```

Grow each word in a dynamic buffer (see `realloc` below). Note that `""` is a real, empty word. Track "am I inside a word" separately from "is the buffer empty".

## 2. Arbitrary-precision integers — schoolbook arithmetic

Store a big number as an array of digits, **least significant first**, so that position i means 10^i. Addition is what you did at school:

```c
int carry = 0;
for (size_t i = 0; i < n; i++) {
    int s = a[i] + b[i] + carry;     /* treat missing digits as 0 */
    out[i] = s % 10; carry = s / 10;
}
if (carry) out[n++] = carry;
```

Multiplication: `out[i + j] += a[i] * b[j]`, then propagate the carries in one pass. Remember to strip leading zeros, and to handle signs and `0` (never print `-0`).

**Growing a buffer safely:**

```c
size_t cap = 16, len = 0;
char *buf = malloc(cap);
if (!buf) return NULL;
/* ... when full: */
if (len + 1 >= cap) {
    char *nb = realloc(buf, cap * 2);
    if (!nb) { free(buf); return NULL; }   /* don't lose the old pointer */
    buf = nb; cap *= 2;
}
```

Doubling gives amortised O(1) appends.

## 3. Recursive-descent calculator

This uses the same grammar as Python's quiz 1 (expr → term → factor), with C details:

- Keep a cursor `const char **pp` and pass it to every function, so they all advance the same position.
- Report errors through a flag or return code (for example `int *err`), because C has no exceptions.
- Skip whitespace at the start of every rule.

```c
static long expr(const char **p, int *err);
static long factor(const char **p, int *err) {
    skip_ws(p);
    if (**p == '(') { (*p)++; long v = expr(p, err); skip_ws(p);
                      if (**p != ')') { *err = 1; return 0; } (*p)++; return v; }
    if (**p == '-') { (*p)++; return -factor(p, err); }
    if (!isdigit((unsigned char)**p)) { *err = 1; return 0; }
    return strtol(*p, (char **)p, 10);
}
```

Check for division by zero **before** dividing. Dividing by zero in C is undefined behaviour, not a catchable error.

## 4. Word frequency report — hash or sort, then `qsort`

1. Read words with a manual loop over `getchar()` and lowercase each one with `tolower((unsigned char)c)`. The `unsigned char` cast matters: passing a negative `char` to `<ctype.h>` functions is undefined.
2. Count the words, either with a hash table or by collecting them all, sorting, and counting runs.
3. Sort the results with `qsort` and a comparator:

```c
struct wc { char *word; int count; };
static int cmp(const void *a, const void *b) {
    const struct wc *x = a, *y = b;
    if (x->count != y->count) return y->count - x->count;   /* count desc */
    return strcmp(x->word, y->word);                          /* word asc   */
}
qsort(arr, n, sizeof arr[0], cmp);
```

> [!DANGER]
> Free every `malloc`ed word before exiting, and test with `-fsanitize=address` on your own machine. Leaks and out-of-bounds writes are the usual hidden-test failures.
