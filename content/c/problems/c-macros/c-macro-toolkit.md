---
id: c-macro-toolkit
title: A Safe Macro Toolkit
difficulty: Medium
order: 1
tags: macros, stringification, token pasting, X-macros, do-while(0)
---
## Statement
Define the following macros (the driver, appended after your code, uses them in tricky ways):

| Macro | Requirement |
|---|---|
| `SQUARE(x)` | the square of x; correct for `SQUARE(1 + 2)` and inside other expressions like `100 / SQUARE(2)` |
| `ARRAY_LEN(a)` | the number of elements of an array |
| `CLAMP(x, lo, hi)` | x limited to [lo, hi]; may evaluate its arguments more than once, but must be fully parenthesised |
| `SWAP_INT(a, b)` | swaps two int lvalues. It must work as **one statement** in an unbraced `if`/`else` |
| `STRINGIFY(x)` | the literal text of the argument, e.g. `STRINGIFY(a + b)` → `"a + b"` |
| `TO_STRING(x)` | the **expanded** value as a string, e.g. with `#define LIMIT 42`, `TO_STRING(LIMIT)` → `"42"` |
| `MAKE_GETTER(field)` | defines a function `int get_<field>(const struct Config *c) { return c->field; }` |
| `COLOR_LIST(X)` | an X-macro list with `X(RED, 0xFF0000) X(GREEN, 0x00FF00) X(BLUE, 0x0000FF) X(GOLD, 0xFFD700)` |

The driver uses `COLOR_LIST` to generate an enum, a name table and a value table, so all four colours must be listed in exactly that order. It also defines `struct Config` before using `MAKE_GETTER`, so your getter macro just has to expand correctly.

## Starter
```c
#include <stdio.h>

#define SQUARE(x) x * x
#define ARRAY_LEN(a) sizeof(a)
#define CLAMP(x, lo, hi) x < lo ? lo : x > hi ? hi : x
#define SWAP_INT(a, b) int t = a; a = b; b = t;
#define STRINGIFY(x) x
#define TO_STRING(x) x
#define MAKE_GETTER(field)
#define COLOR_LIST(X)
```

## Driver
```c
#include <string.h>

#define LIMIT 42

struct Config { int width; int height; };
MAKE_GETTER(width)
MAKE_GETTER(height)

#define AS_ENUM(name, value) COLOR_##name,
#define AS_NAME(name, value) #name,
#define AS_VALUE(name, value) value,
enum Color { COLOR_LIST(AS_ENUM) COLOR_COUNT };
static const char *color_names[] = { COLOR_LIST(AS_NAME) };
static const unsigned color_values[] = { COLOR_LIST(AS_VALUE) };

int main(void) {
    int tests;
    if (scanf("%d", &tests) != 1) return 1;
    for (int t = 0; t < tests; t++) {
        int a, b;
        if (scanf("%d %d", &a, &b) != 2) return 1;
        printf("SQUARE(a+b)=%d  100/SQUARE(b)=%d\n", SQUARE(a + b), b ? 100 / SQUARE(b) : 0);
        printf("CLAMP=%d %d %d\n", CLAMP(a, 0, 10), 2 * CLAMP(b, -5, 5), CLAMP(a - b, a, b));
        int x = a, y = b;
        if (x > y)
            SWAP_INT(x, y);
        else
            x = x;
        printf("sorted=%d %d\n", x, y);
    }
    int arr[17];
    double darr[5];
    printf("ARRAY_LEN=%zu %zu\n", ARRAY_LEN(arr), ARRAY_LEN(darr));
    printf("STRINGIFY=%s | TO_STRING=%s | %s\n", STRINGIFY(a + b), TO_STRING(LIMIT), STRINGIFY(LIMIT));
    struct Config c = {640, 480};
    printf("getters=%d %d\n", get_width(&c), get_height(&c));
    printf("colors=%d:", COLOR_COUNT);
    for (int i = 0; i < COLOR_COUNT; i++) printf(" %s=%06X", color_names[i], color_values[i]);
    printf("\nGOLD index=%d\n", COLOR_GOLD);
    return 0;
}
```

## Tests
=== sample
2
1 2
5 3
---
SQUARE(a+b)=9  100/SQUARE(b)=25
CLAMP=1 4 1
sorted=1 2
SQUARE(a+b)=64  100/SQUARE(b)=11
CLAMP=5 6 5
sorted=3 5
ARRAY_LEN=17 5
STRINGIFY=a + b | TO_STRING=42 | LIMIT
getters=640 480
colors=4: RED=FF0000 GREEN=00FF00 BLUE=0000FF GOLD=FFD700
GOLD index=3
=== hidden
3
-4 20
10 10
0 -7
---
SQUARE(a+b)=256  100/SQUARE(b)=0
CLAMP=0 10 -4
sorted=-4 20
SQUARE(a+b)=400  100/SQUARE(b)=1
CLAMP=10 10 10
sorted=10 10
SQUARE(a+b)=49  100/SQUARE(b)=2
CLAMP=0 -10 -7
sorted=-7 0
ARRAY_LEN=17 5
STRINGIFY=a + b | TO_STRING=42 | LIMIT
getters=640 480
colors=4: RED=FF0000 GREEN=00FF00 BLUE=0000FF GOLD=FFD700
GOLD index=3

## Hints
- Parenthesise every use of a parameter **and** the whole expression.
- `ARRAY_LEN(a)` is `(sizeof(a) / sizeof((a)[0]))`.
- `SWAP_INT`: `do { int swap_tmp_ = (a); (a) = (b); (b) = swap_tmp_; } while (0)`. The starter's version breaks the `if`/`else` (a compile error).
- `TO_STRING(x)` must call `STRINGIFY(x)`, so the argument is macro-expanded before `#` is applied.
- `MAKE_GETTER(field)`: `int get_##field(const struct Config *c) { return c->field; }`.

## Solution
```c
#include <stdio.h>

#define SQUARE(x) ((x) * (x))
#define ARRAY_LEN(a) (sizeof(a) / sizeof((a)[0]))
#define CLAMP(x, lo, hi) ((x) < (lo) ? (lo) : (x) > (hi) ? (hi) : (x))
#define SWAP_INT(a, b) do { int swap_tmp_ = (a); (a) = (b); (b) = swap_tmp_; } while (0)
#define STRINGIFY(x) #x
#define TO_STRING(x) STRINGIFY(x)
#define MAKE_GETTER(field) int get_##field(const struct Config *c) { return c->field; }
#define COLOR_LIST(X)      \
    X(RED, 0xFF0000)       \
    X(GREEN, 0x00FF00)     \
    X(BLUE, 0x0000FF)      \
    X(GOLD, 0xFFD700)
```

Each macro shows one rule:
- **Parentheses** around parameters and the whole body make `SQUARE(1 + 2)` give 9, and `100 / SQUARE(2)` give 25 rather than `100 / 2 * 2 = 100`.
- **`sizeof` arithmetic** gives array lengths at compile time, but only for real arrays, never pointers.
- **`do { } while (0)`** turns several statements into one, so `if (...) SWAP_INT(x, y); else ...` parses correctly. The temporary's unusual name avoids capturing a caller variable called `t`.
- **`#` doesn't expand its argument**, so `STRINGIFY(LIMIT)` is `"LIMIT"`. The extra indirection in `TO_STRING` expands `LIMIT` to `42` first.
- **`##` pastes tokens** to generate identifiers like `get_width`, which is code generation by the preprocessor.
- **X-macros** keep the enum, the name table and the value table in sync from one list. Adding a colour updates all three.
