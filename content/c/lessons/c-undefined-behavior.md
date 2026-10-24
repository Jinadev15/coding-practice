# Undefined Behavior

C was designed to map directly onto hardware and to let compilers generate the fastest possible code. The price is a long list of operations whose meaning the standard leaves **undefined**: the standard imposes no requirements at all on a program that performs them. Undefined behaviour (UB) is the source of the worst C bugs, from security holes (buffer overflows) to code that works at `-O0` and silently breaks at `-O2`. A professional C programmer must know the categories, understand how optimisers exploit them, and use tools that catch them.

## 1. Four kinds of "it depends"

| Term | Meaning | Example |
|---|---|---|
| **well-defined** | exactly one behaviour | `1 + 2` |
| **implementation-defined** | the compiler picks a behaviour and **documents** it | `sizeof(int)`, right-shifting a negative value, `char` signedness |
| **unspecified** | one of several allowed outcomes, not necessarily documented, may vary per call | the evaluation order of function arguments `f(a(), b())` |
| **undefined** | no requirements: anything may happen, including nothing visible | `INT_MAX + 1`, `*NULL`, `a[10]` on an `int a[10]` |

A portable program may rely on implementation-defined behaviour only if it checks it (`static_assert(sizeof(int) == 4, "...")`). It must never rely on unspecified results, and it must never execute UB.

## 2. The UB you will actually meet

| Category | Example | Notes |
|---|---|---|
| signed integer overflow | `int x = INT_MAX; x + 1` | **unsigned** overflow is defined: it wraps modulo 2ⁿ |
| out-of-bounds access | `a[n]`, reading past `'\0'`, `memcpy` too far | forming a pointer more than one past the end is itself UB |
| null / dangling pointer dereference | use after `free`, returning `&local` | |
| uninitialised read | `int x; printf("%d", x);` | automatic variables start indeterminate |
| invalid shifts | `1 << 32`, `1 << 31` (int), `-1 << 1` | use unsigned types |
| strict aliasing violation | `*(int *)&some_float` | access objects only through compatible types or `char` |
| misaligned access | `*(uint32_t *)(buf + 1)` | x86 tolerates it; the compiler may still assume alignment |
| unsequenced modification | `i = i++ + 1;`, `a[i] = i++;` | two side effects on one object without a sequence point |
| modifying a string literal | `char *s = "hi"; s[0] = 'H';` | literals may be in read-only memory |
| division by zero / `INT_MIN / -1` | | the latter overflows |
| data race | two threads, one writing, no synchronisation | C11 memory model |
| calling a function through an incompatible pointer type | casting `int(*)(int)` to `void(*)(void)` and calling it | |
| `free` of a non-heap pointer, double `free` | | heap corruption |
| missing `return` in a non-void function whose value is used | | |

## 3. How optimisers exploit UB

Compilers assume UB never happens and derive facts from that assumption:

```c
int always_true(int x) {
    return x + 1 > x;              /* signed overflow is UB → compiler folds this to 1 */
}

void clear(int *p) {
    int v = *p;                    /* p dereferenced here … */
    if (p == NULL) return;         /* … so this check may be DELETED */
    *p = 0;
}

int table[4];
int in_table(int v) {
    for (int i = 0; i <= 4; i++)   /* reading table[4] is UB → GCC may turn this into "return 1" */
        if (table[i] == v) return 1;
    return 0;
}
```

A real case: the Linux kernel had a null-check deleted exactly like `clear` above (CVE-2009-1897). The kernel is now built with `-fno-delete-null-pointer-checks`.

> [!DANGER]
> UB isn't localised. Once a program executes UB, the *whole* execution has no meaning, including output produced before the faulty line, because the compiler may have reordered or removed code based on reasoning that started from the UB. "I added a printf and the bug went away" is a classic UB symptom.

## 4. Sequence points and unsequenced evaluation

Between two **sequence points** (C11 calls them "sequenced before" relations), an object may be modified at most once, and if it's modified, it may be read only to determine the new value.

Sequence points occur:
- at the end of a full expression (`;`)
- after the first operand of `&&`, `||`, `?:` and `,` (the comma operator, not the commas between function arguments)
- before a function call (after the arguments are evaluated)

```c
i = i + 1;          /* fine */
i = ++i + 1;        /* UB: i modified twice without a sequence point */
a[i] = i++;         /* UB: i read (index) and modified, unsequenced */
f(i++, i++);        /* UB: argument evaluations are unsequenced */
x = (i++, i++);     /* fine: the comma operator is a sequence point */
```

## 5. Strict aliasing

Compilers assume that pointers of **different, incompatible types** don't point to the same object. That allows keeping values in registers across stores:

```c
int f(int *a, float *b) {
    *a = 1;
    *b = 2.0f;            /* compiler assumes this can't modify *a */
    return *a;            /* … so it returns 1 without reloading */
}
```

Calling `f((int *)&x, &x)` violates aliasing and the result is undefined. Allowed ways to reinterpret bytes:

```c
float f = 1.0f;
uint32_t u;
memcpy(&u, &f, sizeof u);                 /* always correct; compiles to a register move */

union { float f; uint32_t u; } pun = { .f = 1.0f };
uint32_t u2 = pun.u;                      /* allowed in C (C99 TC3 and later), NOT in C++ */

unsigned char *bytes = (unsigned char *)&f;   /* char types may alias anything */
```

`-fno-strict-aliasing` disables the optimisation (the Linux kernel uses it), at some performance cost.

## 6. Writing UB-free arithmetic

```c
#include <limits.h>
#include <stdbool.h>

bool add_overflows(int a, int b) {        /* check BEFORE the operation */
    return (b > 0 && a > INT_MAX - b) || (b < 0 && a < INT_MIN - b);
}

int r;
if (__builtin_add_overflow(a, b, &r)) { /* overflow */ }   /* GCC/Clang; C23: ckd_add(&r, a, b) */
```

- Use `size_t` and unsigned types for sizes and bit operations.
- For midpoints, use `lo + (hi - lo) / 2`.
- Convert to a wider type before multiplying: `(int64_t)a * b`.
- A cast from double to int is UB if the value doesn't fit. Check the range first.

## 7. Tools

| Tool | Flag / command | Catches |
|---|---|---|
| UBSan | `-fsanitize=undefined` | signed overflow, shifts, null, misalignment, bad casts, out-of-bounds (array type known) |
| ASan | `-fsanitize=address` | heap/stack/global overflows, use-after-free, double free, leaks |
| MSan (Clang) | `-fsanitize=memory` | uninitialised reads |
| TSan | `-fsanitize=thread` | data races |
| Valgrind | `valgrind --leak-check=full ./a.out` | memory errors without recompiling |
| warnings | `-Wall -Wextra -Wpedantic -Wconversion -Wshadow -Wnull-dereference -Wstrict-aliasing=2` | many at compile time |
| static analysis | `gcc -fanalyzer`, clang-tidy, Coverity, Frama-C | path-sensitive bugs |
| trapping mode | `-ftrapv` (abort on signed overflow), `-fwrapv` (define wrap-around) | |

> [!TIP]
> Make `-fsanitize=address,undefined -g` your default debug build. Sanitizers find bugs at the exact faulting line with a stack trace, which beats hours of `printf` debugging.

## 8. Exam-ready answers

> [!EXAM]
> **Undefined behaviour in C.** Undefined behaviour is behaviour for which the C standard imposes no requirements, arising from erroneous constructs such as signed integer overflow, out-of-bounds array access, dereferencing null or freed pointers, reading uninitialised automatic variables, modifying an object twice between sequence points, and accessing an object through an lvalue of incompatible type (strict aliasing). Compilers may assume that undefined behaviour never occurs and optimise accordingly, for instance removing overflow or null checks, so its effects can be arbitrary and non-local. It is distinguished from implementation-defined behaviour, which each implementation must document, and from unspecified behaviour, where the standard allows a choice among alternatives.

## 9. Cheat sheet

| Risk | Safe practice |
|---|---|
| signed overflow | check limits first, use `__builtin_*_overflow`, or use wider/unsigned types |
| shifts | `uint32_t` and counts < width |
| type punning | `memcpy` (or a union in C) |
| `i++` twice in one expression | split into statements |
| array indexing | check bounds; `for (i = 0; i < n; i++)` |
| string literals | `const char *` or `char s[] = "..."` |
| debug builds | `-fsanitize=address,undefined -g` |

> [!INTERVIEW]
> **"Why did my overflow check `if (x + 100 < x)` disappear at -O2?"** Because signed overflow is UB, the compiler may assume `x + 100` never wraps, so `x + 100 < x` is always false and the branch is removed. Check before the operation instead (`x > INT_MAX - 100`), use unsigned arithmetic, or use `__builtin_add_overflow`. Mentioning `-fwrapv` and UBSan shows depth.
