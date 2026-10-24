---
id: c-generic-values
title: Type-Generic Values with _Generic and Tagged Unions
difficulty: Hard
order: 1
tags: _Generic, C11, anonymous unions, tagged unions, integer promotions, static_assert
---
## Statement
Build a small dynamically typed value system in **standard C17**, the way scripting-language runtimes and config parsers do it, and use `_Generic` to expose a type-aware API.

1. **`TYPE_NAME(x)`**: a macro that expands to a string literal naming the type of expression x. Support `_Bool`, `char`, `signed char`, `unsigned char`, `short`, `unsigned short`, `int`, `unsigned int`, `long`, `unsigned long`, `long long`, `unsigned long long`, `float`, `double`, `long double` and `char *`, plus `"other"` for anything else. Spell them exactly like that (e.g. `"unsigned long"`). The driver uses it to expose C's **integer promotions** and usual arithmetic conversions.

2. **A tagged union** `Value`, with an anonymous union inside:

```c
typedef enum { V_INT, V_DBL, V_STR } Kind;
typedef struct { Kind kind; union { long long i; double d; const char *s; }; } Value;
```

3. **`VALUE(x)`**: a `_Generic` macro that builds a `Value` from any integer type up to `long long` (signed or unsigned, char types and `_Bool` included) → `V_INT`, from `float`/`double` → `V_DBL`, and from `char *`/`const char *` → `V_STR`.

4. Functions:

```c
void value_print(Value v);          /* "int 42" | "double 2.5" (printf %g) | "str \"text\"" , then newline */
Value value_add(Value a, Value b);   /* int+int -> int; int/double mixes -> double;
                                        any string operand -> V_STR "<type error>" */
```

The driver also checks `static_assert(sizeof(Value) == 16)`, so the union must overlap its members.

## Starter
```c
#include <stdio.h>

typedef enum { V_INT, V_DBL, V_STR } Kind;
typedef struct { Kind kind; long long i; double d; const char *s; } Value;

#define TYPE_NAME(x) "other"
#define VALUE(x) value_from_int((long long)(x))

static Value value_from_int(long long i) { Value v = { .kind = V_INT, .i = i }; return v; }

void value_print(Value v) { printf("int %lld\n", v.i); }
Value value_add(Value a, Value b) { return value_from_int(a.i + b.i); }
```

## Driver
```c
#include <assert.h>
#include <string.h>
#include <stdbool.h>

static_assert(sizeof(Value) == 16, "Value must overlap its members in a union (16 bytes)");

int main(void) {
    char cmd[16];
    while (scanf("%15s", cmd) == 1) {
        if (!strcmp(cmd, "types")) {
            char c = 'x'; unsigned char uc = 200; short sh = 3; unsigned short us = 4;
            unsigned u = 1; long l = 2; float f = 1.5f; bool b = true; char *str = "s";
            printf("'a'          -> %s\n", TYPE_NAME('a'));
            printf("c            -> %s\n", TYPE_NAME(c));
            printf("c + c        -> %s\n", TYPE_NAME(c + c));
            printf("uc * 2       -> %s\n", TYPE_NAME(uc * 2));
            printf("sh + us      -> %s\n", TYPE_NAME(sh + us));
            printf("u + 1        -> %s\n", TYPE_NAME(u + 1));
            printf("u + l        -> %s\n", TYPE_NAME(u + l));
            printf("-1 < 0u      -> %s\n", TYPE_NAME(-1 < 0u));
            printf("1 + 2.0f     -> %s\n", TYPE_NAME(1 + 2.0f));
            printf("f * 2.0      -> %s\n", TYPE_NAME(f * 2.0));
            printf("sizeof(int)  -> %s\n", TYPE_NAME(sizeof(int)));
            printf("b            -> %s\n", TYPE_NAME(b));
            printf("true         -> %s\n", TYPE_NAME(true));
            printf("str          -> %s\n", TYPE_NAME(str));
            printf("&u           -> %s\n", TYPE_NAME(&u));
            printf("10LL / 3     -> %s\n", TYPE_NAME(10LL / 3));
            printf("1.0L         -> %s\n", TYPE_NAME(1.0L));
            printf("(signed char)1 -> %s\n", TYPE_NAME((signed char)1));
            printf("0xFFFFFFFF   -> %s\n", TYPE_NAME(0xFFFFFFFF));
            printf("2147483648   -> %s\n", TYPE_NAME(2147483648));
        } else if (!strcmp(cmd, "values")) {
            const char *cs = "robot";
            unsigned short us = 7;
            value_print(VALUE(42));
            value_print(VALUE(-3LL));
            value_print(VALUE(us));
            value_print(VALUE('A'));
            value_print(VALUE((bool)1));
            value_print(VALUE(2.5));
            value_print(VALUE(0.25f));
            value_print(VALUE(cs));
            value_print(VALUE("lit"));
            value_print(value_add(VALUE(40), VALUE(2)));
            value_print(value_add(VALUE(1), VALUE(0.5)));
            value_print(value_add(VALUE(1.5), VALUE(1.5)));
            value_print(value_add(VALUE(cs), VALUE(1)));
            value_print(value_add(VALUE(3000000000LL), VALUE(3000000000LL)));
            Value v = VALUE(9);
            printf("kind=%d i=%lld\n", (int)v.kind, v.i);
        }
    }
    return 0;
}
```

## Tests
=== sample
values
---
int 42
int -3
int 7
int 65
int 1
double 2.5
double 0.25
str "robot"
str "lit"
int 42
double 1.5
double 3
str "<type error>"
int 6000000000
kind=0 i=9
=== hidden
types
---
'a'          -> int
c            -> char
c + c        -> int
uc * 2       -> int
sh + us      -> int
u + 1        -> unsigned int
u + l        -> long
-1 < 0u      -> int
1 + 2.0f     -> float
f * 2.0      -> double
sizeof(int)  -> unsigned long
b            -> _Bool
true         -> int
str          -> char *
&u           -> other
10LL / 3     -> long long
1.0L         -> long double
(signed char)1 -> signed char
0xFFFFFFFF   -> unsigned int
2147483648   -> long

## Hints
- `TYPE_NAME`: a `_Generic` with one association per type, plus `default: "other"`. `char`, `signed char` and `unsigned char` are three distinct types, and so are `char *` and `const char *`.
- Integer promotions: in C, `'a'` already has type `int`, and `c + c`, `uc * 2` and `sh + us` are all `int`. `u + l` is `long` on LP64 (long can represent every unsigned value), `sizeof` yields `size_t` (`unsigned long` on Linux x86-64), and `0xFFFFFFFF` is `unsigned int`, but the decimal constant `2147483648` is `long`.
- `VALUE(x)`: `_Generic((x), char *: value_str, const char *: value_str, float: value_dbl, double: value_dbl, default: value_int)(x)`, where `value_int` takes `long long`. A string literal has type `char [N]`, which decays to `char *` in `_Generic`'s controlling expression.
- Put `i`, `d` and `s` in an anonymous union so `sizeof(Value)` is 16 (a 4-byte enum, 4 bytes of padding, then an 8-byte union).

## Solution
```c
#include <stdio.h>

typedef enum { V_INT, V_DBL, V_STR } Kind;
typedef struct {
    Kind kind;
    union {                      /* anonymous: v.i, v.d, v.s share storage */
        long long i;
        double d;
        const char *s;
    };
} Value;

#define TYPE_NAME(x) _Generic((x),                                          \
    _Bool: "_Bool", char: "char", signed char: "signed char",               \
    unsigned char: "unsigned char", short: "short",                         \
    unsigned short: "unsigned short", int: "int", unsigned int: "unsigned int", \
    long: "long", unsigned long: "unsigned long", long long: "long long",    \
    unsigned long long: "unsigned long long", float: "float",               \
    double: "double", long double: "long double", char *: "char *",         \
    default: "other")

static Value value_int(long long i) { return (Value){ .kind = V_INT, .i = i }; }
static Value value_dbl(double d) { return (Value){ .kind = V_DBL, .d = d }; }
static Value value_str(const char *s) { return (Value){ .kind = V_STR, .s = s }; }

#define VALUE(x) _Generic((x),                     \
    char *: value_str, const char *: value_str,    \
    float: value_dbl, double: value_dbl,           \
    default: value_int)(x)

void value_print(Value v) {
    switch (v.kind) {
    case V_INT: printf("int %lld\n", v.i); break;
    case V_DBL: printf("double %g\n", v.d); break;
    case V_STR: printf("str \"%s\"\n", v.s); break;
    }
}

static double as_double(Value v) { return v.kind == V_INT ? (double)v.i : v.d; }

Value value_add(Value a, Value b) {
    if (a.kind == V_STR || b.kind == V_STR) return value_str("<type error>");
    if (a.kind == V_INT && b.kind == V_INT) return value_int(a.i + b.i);
    return value_dbl(as_double(a) + as_double(b));
}
```

**`_Generic`** picks an expression at compile time from the static type of its operand. That makes it the C11 tool for overloading-like APIs (`<tgmath.h>` is built on it). The selected expression can be a function designator, so `VALUE(x)` becomes "pick a constructor, then call it with x".

The `types` output is a tour of C's conversion rules:
- Character constants are `int`, and arithmetic on anything narrower than `int` is promoted to `int`.
- Mixing `unsigned int` with `long` gives `long` on LP64, because `long` can hold every `unsigned` value.
- A comparison always has type `int`, and C17's `true` is just the macro `1`.
- Unsuffixed decimal constants pick the first signed type that fits (`2147483648` → `long`), while hex constants may become unsigned (`0xFFFFFFFF` → `unsigned int`).

These rules are why `-1 < 0u` is false. **The tagged union** with an anonymous member gives variant-like data in 16 bytes, where a struct with three separate fields would take 32.
