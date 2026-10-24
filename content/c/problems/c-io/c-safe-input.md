---
id: c-safe-input
title: Robust Number Reader
difficulty: Medium
order: 1
tags: fgets, sscanf, strtol, input validation
---
## Statement
Read the input **line by line** with `fgets`. Each line should contain exactly one integer (surrounding spaces allowed). For each line print:

- `ok N` if the line is a valid integer in the range of `long`
- `bad: TEXT` otherwise, where TEXT is the line with its newline removed (empty lines included)

At the end print `sum S` of the valid numbers (as a `long long`).

Use `strtol` and check its `end` pointer: the whole line (except whitespace) must be consumed. `scanf("%d")` would happily accept `12abc` as 12.

## Starter
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <errno.h>

int main(void) {
    char line[256];
    long long sum = 0;
    while (fgets(line, sizeof line, stdin)) {

    }
    printf("sum %lld\n", sum);
    return 0;
}
```

## Tests
=== sample
42
  -7  
12abc

3
---
ok 42
ok -7
bad: 12abc
bad: 
ok 3
sum 38
=== hidden
+5
0x10
99999999999999999999
- 4
---
ok 5
bad: 0x10
bad: 99999999999999999999
bad: - 4
sum 5

## Hints
- Strip the newline: `line[strcspn(line, "\n")] = '\0';`.
- `errno = 0; long v = strtol(line, &end, 10);` gives an error if `end == line` (no digits), if `errno == ERANGE` (out of range), or if anything other than whitespace remains after `end`.
- `strtol` with base 10 rejects `0x10` at the `x`, leaving `end` pointing there.

## Solution
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <errno.h>

int main(void) {
    char line[256];
    long long sum = 0;
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\n")] = '\0';
        char *end;
        errno = 0;
        long v = strtol(line, &end, 10);
        int ok = end != line && errno != ERANGE;
        while (ok && *end) {
            if (!isspace((unsigned char)*end)) ok = 0;
            end++;
        }
        if (ok) {
            printf("ok %ld\n", v);
            sum += v;
        } else {
            printf("bad: %s\n", line);
        }
    }
    printf("sum %lld\n", sum);
    return 0;
}
```

`strtol` skips leading whitespace and accepts an optional sign, then stops at the first non-digit and reports where in `end`. Checking `end` is what makes the parse strict. The `(unsigned char)` cast before `isspace` matters: passing a negative `char` to the `<ctype.h>` functions is undefined behaviour. This is how production C code parses numbers from config files and serial input.
