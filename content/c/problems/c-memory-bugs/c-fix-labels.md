---
id: c-fix-labels
title: Fix the Label Maker
difficulty: Medium
order: 1
tags: memory bugs, static buffers, off-by-one, ownership
---
## Statement
A colleague wrote a module that builds labels for robot parts, but the output is wrong and the code has several memory bugs. **Fix the three functions** so that the driver produces the correct output. You may rewrite them completely, but keep the signatures and documented ownership.

```c
/* Returns a NEW malloc'd string "PREFIX-NNNN" (number zero-padded to 4 digits). Caller frees. */
char *make_label(const char *prefix, int number);

/* Returns a NEW malloc'd string: the labels joined with ", ". n may be 0 (returns ""). Caller frees. */
char *join_labels(char **labels, int n);

/* Frees the n labels AND the array itself. */
void free_labels(char **labels, int n);
```

The starter code has:
1. a function returning a **static buffer** (every label ends up identical),
2. an **off-by-one** allocation that forgets the terminator,
3. a `realloc` misuse, and
4. a **double free** / use-after-free in `free_labels`.

The driver reads `PREFIX N` and then `N` part numbers, builds each label, prints the joined string and its length, and frees everything. Your program must also be clean under AddressSanitizer (try `gcc -fsanitize=address` locally).

## Starter
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *make_label(const char *prefix, int number) {
    static char buf[64];
    snprintf(buf, sizeof buf, "%s-%04d", prefix, number);
    return buf;
}

char *join_labels(char **labels, int n) {
    char *out = malloc(1);
    out[0] = '\0';
    for (int i = 0; i < n; i++) {
        out = realloc(out, strlen(out) + strlen(labels[i]) + 2);
        if (i > 0) strcat(out, ", ");
        strcat(out, labels[i]);
    }
    return out;
}

void free_labels(char **labels, int n) {
    free(labels);
    for (int i = 0; i < n; i++) free(labels[i]);
}
```

## Driver
```c
int main(void) {
    char prefix[32];
    int n;
    if (scanf("%31s %d", prefix, &n) != 2) return 1;
    char **labels = malloc((size_t)(n > 0 ? n : 1) * sizeof *labels);
    for (int i = 0; i < n; i++) {
        int num;
        if (scanf("%d", &num) != 1) return 1;
        labels[i] = make_label(prefix, num);
    }
    char *all = join_labels(labels, n);
    printf("%s\n%zu\n", all, strlen(all));
    free(all);
    free_labels(labels, n);
    return 0;
}
```

## Tests
=== sample
ARM 3
7 42 1234
---
ARM-0007, ARM-0042, ARM-1234
28
=== hidden
X 0
---

0
=== hidden
GRIPPER 1
9999
---
GRIPPER-9999
12
=== hidden
LIDAR_FRONT_LEFT 5
1 22 333 4444 0
---
LIDAR_FRONT_LEFT-0001, LIDAR_FRONT_LEFT-0022, LIDAR_FRONT_LEFT-0333, LIDAR_FRONT_LEFT-4444, LIDAR_FRONT_LEFT-0000
113
=== hidden
M 12
1 2 3 4 5 6 7 8 9 10 11 12
---
M-0001, M-0002, M-0003, M-0004, M-0005, M-0006, M-0007, M-0008, M-0009, M-0010, M-0011, M-0012
94

## Hints
- `make_label`: compute the needed size with `snprintf(NULL, 0, ...)`, allocate `size + 1`, then `snprintf` into it.
- `join_labels`: `", "` is 2 characters, plus 1 for the terminator, so the starter's `+ 2` is one byte short whenever a separator is added. Better: compute the total length first and allocate once.
- `free_labels`: free the elements **before** the array that holds the pointers to them.

## Solution
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char *make_label(const char *prefix, int number) {
    int len = snprintf(NULL, 0, "%s-%04d", prefix, number);   /* measure */
    if (len < 0) return NULL;
    char *s = malloc((size_t)len + 1);                        /* +1 for '\0' */
    if (s) snprintf(s, (size_t)len + 1, "%s-%04d", prefix, number);
    return s;
}

char *join_labels(char **labels, int n) {
    size_t total = 1;                                         /* terminator */
    for (int i = 0; i < n; i++) total += strlen(labels[i]) + (i > 0 ? 2 : 0);
    char *out = malloc(total);
    if (!out) return NULL;
    char *p = out;
    for (int i = 0; i < n; i++) {
        if (i > 0) { memcpy(p, ", ", 2); p += 2; }
        size_t l = strlen(labels[i]);
        memcpy(p, labels[i], l);
        p += l;
    }
    *p = '\0';
    return out;
}

void free_labels(char **labels, int n) {
    for (int i = 0; i < n; i++) free(labels[i]);              /* children first */
    free(labels);                                             /* then the container */
}
```

**The bugs, and why each was dangerous:**
1. **Static buffer:** every `make_label` call returned the *same* address, so all stored pointers aliased one buffer holding the last label. Also, `free_labels` then called `free` on a non-heap pointer (UB). Returning a fresh allocation matches the documented ownership ("caller frees").
2. **Off-by-one:** `strlen(out) + strlen(label) + 2` covers the `", "` separator but not the `'\0'`, so `strcat` wrote one byte past the block. That's silent heap corruption that ASan reports as a heap-buffer-overflow.
3. **realloc misuse:** `out = realloc(out, ...)` leaks the old block on failure, and calling `realloc` in a loop with `strcat` (which rescans the string) makes joining O(n²). Measuring first and copying with `memcpy` and a moving pointer is O(total length) with one allocation.
4. **Use-after-free:** reading `labels[i]` after `free(labels)` reads freed memory. Always release children before the container that references them.
