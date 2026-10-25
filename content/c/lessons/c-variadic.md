# Variadic Functions

`printf` accepts any number of arguments of different types. How? It's a **variadic function**: a function declared with `...` that walks its extra arguments at run time using the `<stdarg.h>` macros. Writing your own (a logging function, a `sum` of n values, a mini-printf) shows how C calling conventions work, and why `printf` can't check types without compiler help.

## 1. Declaring and using

> [!SYNTAX]
> ```c
> #include <stdarg.h>
> type name(fixed_params, ...);         /* at least one named parameter, then ... */
>
> va_list ap;                          /* the argument cursor */
> va_start(ap, last_named_param);      /* initialise it after the last named parameter */
> T x = va_arg(ap, T);                 /* fetch the next argument as type T */
> va_end(ap);                          /* clean up (required) */
> ```

```c
#include <stdarg.h>
#include <stdio.h>

int sum(int count, ...) {
    va_list ap;
    va_start(ap, count);
    int total = 0;
    for (int i = 0; i < count; i++)
        total += va_arg(ap, int);
    va_end(ap);
    return total;
}

int main(void) {
    printf("%d\n", sum(4, 10, 20, 30, 40));   /* 100 */
    return 0;
}
```

## 2. The function must be told how many arguments there are, and their types

> [!KEY]
> A variadic function has **no way to know** how many arguments were passed or what their types are. You must encode that yourself:
> - a **count** parameter (`sum(int count, ...)`)
> - a **format string** describing them (`printf`)
> - a **sentinel** terminating the list (`execl(path, arg0, ..., (char *)NULL)`)
>
> Reading more arguments than were passed, or reading one with the wrong type in `va_arg`, is **undefined behaviour**.

```mermaid
flowchart LR
    C["call: sum(3, 5, 6, 7)"] --> R["registers/stack: 3 | 5 | 6 | 7"]
    R --> V["va_start: cursor after 'count'"]
    V --> A1["va_arg(ap, int) → 5"] --> A2["→ 6"] --> A3["→ 7"]
    A3 --> X["4th va_arg → garbage (UB)"]
```

## 3. Default argument promotions

Arguments matching `...` undergo the **default promotions**: `char`, `short` and `bool` become `int`; `float` becomes `double`. So you must write `va_arg(ap, int)` for a `char` and `va_arg(ap, double)` for a `float`. `va_arg(ap, char)` and `va_arg(ap, float)` are wrong (UB), and gcc warns.

## 4. A mini printf

```c
#include <stdarg.h>
#include <stdio.h>

void mini_printf(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    for (const char *p = fmt; *p; p++) {
        if (*p != '%') { putchar(*p); continue; }
        switch (*++p) {                      /* the character after % */
        case 'd': printf("%d", va_arg(ap, int)); break;
        case 's': fputs(va_arg(ap, const char *), stdout); break;
        case 'c': putchar(va_arg(ap, int)); break;      /* char was promoted to int */
        case 'f': printf("%g", va_arg(ap, double)); break;
        case '%': putchar('%'); break;
        default:  putchar('?');
        }
    }
    va_end(ap);
}
```

## 5. Forwarding: `vprintf` and friends

To wrap printf (for a logger, say), pass the `va_list` to the `v` versions:

```c
#include <stdarg.h>
#include <stdio.h>

void log_msg(const char *level, const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    fprintf(stderr, "[%s] ", level);
    vfprintf(stderr, fmt, ap);          /* vprintf / vfprintf / vsnprintf take a va_list */
    fputc('\n', stderr);
    va_end(ap);
}
```

Give your wrapper the gcc attribute `__attribute__((format(printf, 2, 3)))` and the compiler type-checks its calls like printf's. `va_copy(dst, src)` duplicates a cursor if you need to walk the list twice.

## 6. Pitfalls and alternatives

> [!DANGER]
> - No type safety: `sum(3, 1.5, 2, 3)` reads the double's bits as an int (UB).
> - Passing `NULL` as a sentinel: write `(char *)NULL`, because `NULL` may be a plain `0` int, which differs in size from a pointer on 64-bit systems.
> - Forgetting `va_end`: undefined behaviour on some platforms.
>
> Prefer non-variadic designs when you can: pass an array and a length (`sum_array(const int *a, size_t n)`). C++ replaces C varargs with type-safe variadic templates.

## 7. Exam-ready answers

> [!EXAM]
> **Variadic functions.** A variadic function accepts a variable number of arguments, declared with an ellipsis after at least one named parameter, for example `int printf(const char *fmt, ...)`. Inside the function, the macros from `<stdarg.h>` access the extra arguments: `va_start` initialises a `va_list` after the last named parameter, `va_arg(ap, type)` retrieves the next argument as the given type, and `va_end` releases the list. The function cannot determine the number or types of the arguments itself, so they must be conveyed by a count, a format string or a sentinel value. Extra arguments undergo default argument promotions (`char` and `short` to `int`, `float` to `double`), and retrieving an argument with the wrong type is undefined behaviour.

## 8. Cheat sheet

| Need | Code |
|---|---|
| declare | `int f(int n, ...)` |
| start | `va_list ap; va_start(ap, n);` |
| next int | `va_arg(ap, int)` (also for char and short) |
| next double | `va_arg(ap, double)` (also for float) |
| finish | `va_end(ap);` |
| wrap printf | `vfprintf(stream, fmt, ap)` |
| compiler checking | `__attribute__((format(printf, i, j)))` |

> [!INTERVIEW]
> **"Why does `printf("%d\n", 3.0)` print garbage instead of 3?"** printf is variadic: the double 3.0 is passed (in a floating-point register on x86-64), but `%d` makes printf read an `int` (from an integer register or stack slot) with `va_arg(ap, int)`. The types disagree, which is undefined behaviour. Only the compiler's `-Wformat` warning catches it, because the function itself can't know what was passed.

## Worked example: a typed sum with a count

```c
#include <stdarg.h>
#include <stdio.h>

static double average(int count, ...) {
    va_list ap;
    va_start(ap, count);                 /* start after the last named parameter */
    double total = 0;
    for (int i = 0; i < count; i++)
        total += va_arg(ap, double);     /* caller must really pass doubles */
    va_end(ap);
    return count ? total / count : 0.0;
}

static void log_msg(const char *level, const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    printf("[%s] ", level);
    vprintf(fmt, ap);                    /* forward the whole list */
    va_end(ap);
    putchar('\n');
}

int main(void) {
    printf("%.2f\n", average(3, 1.0, 2.0, 4.5));
    log_msg("WARN", "battery %d%% on robot %s", 14, "R2");
    return 0;
}
```

```output
2.50
[WARN] battery 14% on robot R2
```

**The function can't discover how many arguments it got, or their types.** Something has to tell it: a count (`average`), a format string (`printf`), or a sentinel value (`NULL` at the end).

**Default promotions:** in the `...` part, a `float` is passed as a `double`, and a `char` or `short` as an `int`. That's why `va_arg(ap, float)` is always wrong.

## Common mistakes

- **Passing an `int` where the function reads a `double`** (`average(2, 1, 2)`). That is undefined behaviour, and it often prints garbage. Write `1.0, 2.0`.
- **Reusing a `va_list` after passing it to `vprintf`.** Use `va_copy` if you need it twice.
- **Forgetting `va_end`.** On most platforms it does nothing, but the standard requires it.

## Check your understanding

1. Why can't `va_arg(ap, char)` work?
2. How does `printf` know the type of each argument?

<details><summary>Answers</summary>

1. A `char` argument is promoted to `int` when passed through `...`. Read it with `va_arg(ap, int)`.
2. From the format string: `%d` means read an `int`, `%f` means read a `double`, and so on. Compilers warn about mismatches with `-Wformat`.

</details>
