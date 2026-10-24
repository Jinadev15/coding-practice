# Conditional Compilation

The preprocessor can **include or exclude code** before the compiler sees it. That's how one codebase builds for Linux and Windows, for x86 and an ARM microcontroller, in debug and release modes, with optional features turned on or off. It's also how **include guards** stop headers from being processed twice. Used with discipline, conditional compilation keeps portable code clean. Used carelessly, it creates untestable `#ifdef` mazes.

## 1. The directives

```c
#if EXPR          // integer constant expression; undefined identifiers count as 0
#elif EXPR
#else
#endif
#ifdef NAME       // the same as #if defined(NAME)
#ifndef NAME      // the same as #if !defined(NAME)
#error "message"  // stop compilation with a message
#warning "msg"    // gcc/clang (and standard in C23)
```

```c
#define VERSION 3
#if VERSION >= 3 && defined(USE_GPU)
    init_gpu();
#elif VERSION >= 3
    init_cpu_fast();
#else
    init_cpu();
#endif
```

> [!KEY]
> `#if` expressions are evaluated by the **preprocessor**, so they can use only macros and integer literals. There's no `sizeof`, no enum constants, and no variables. An undefined macro in `#if` silently evaluates to 0, so `-Wundef` makes gcc warn about it.

## 2. Include guards

A header included twice (directly, or through other headers) would redefine its structs, which is an error. Guard every header:

```c
// motor.h
#ifndef MOTOR_H
#define MOTOR_H

typedef struct Motor Motor;
Motor *motor_create(int id);

#endif /* MOTOR_H */
```

```c
#pragma once      // a non-standard but universally supported alternative: simpler, no name clashes
```

The first time, `MOTOR_H` is undefined, so the content is processed and the macro gets defined. Every later inclusion skips to `#endif`.

## 3. Configuration from the build

Macros can be defined on the compiler command line with `-D`:

```bash
gcc -DDEBUG -DLOG_LEVEL=2 -DBOARD_REV=3 main.c -o main
gcc -DNDEBUG -O2 main.c -o main       # release: disables assert()
```

```c
#ifdef DEBUG
    #define DBG(...) fprintf(stderr, __VA_ARGS__)
#else
    #define DBG(...) ((void)0)        // compiles to nothing in release builds
#endif

#ifndef LOG_LEVEL
    #define LOG_LEVEL 1               // a default when the build doesn't specify one
#endif
```

> [!TIP]
> `assert(expr)` from `<assert.h>` checks invariants in debug builds and **vanishes** when `NDEBUG` is defined. Never put side effects inside `assert` (`assert(init() == 0)` doesn't call `init()` in release!). For compile-time checks, use `_Static_assert(sizeof(Header) == 8, "wire format")` (C11), or `static_assert` in C23, which works at file scope.

## 4. Platform and compiler detection

```c
#if defined(_WIN32)
    #include <windows.h>
    #define SLEEP_MS(ms) Sleep(ms)
#elif defined(__linux__) || defined(__APPLE__)
    #include <unistd.h>
    #define SLEEP_MS(ms) usleep((ms) * 1000)
#else
    #error "Unsupported platform"
#endif

#if defined(__GNUC__)
    #define LIKELY(x) __builtin_expect(!!(x), 1)
#else
    #define LIKELY(x) (x)
#endif

#if __STDC_VERSION__ >= 201112L       // C11 or newer (201710L for C17, 202311L for C23)
    #include <stdatomic.h>
#endif
```

| Macro | Meaning |
|---|---|
| `__STDC_VERSION__` | the C standard in use (`201710L` for C17) |
| `__GNUC__`, `__clang__`, `_MSC_VER` | which compiler |
| `__linux__`, `_WIN32`, `__APPLE__` | which OS |
| `__x86_64__`, `__aarch64__`, `__arm__` | which CPU architecture |
| `__BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__` | endianness (gcc/clang) |
| `NDEBUG` | release mode (disables assert) |

List everything gcc predefines with `gcc -dM -E - < /dev/null`.

## 5. Keeping it maintainable

> [!WARNING]
> Every `#ifdef` doubles the number of program variants, and code inside an inactive branch **isn't compiled**, so it rots silently until someone enables the option. Guidelines:
> - Confine platform differences to a thin **abstraction layer** (`platform_linux.c`, `platform_stm32.c`) with a common header, instead of scattering `#ifdef`s through the logic.
> - Prefer `if (DEBUG_ENABLED)` on a constant over `#ifdef DEBUG` where possible: the compiler still type-checks the dead branch and optimises it away.
> - Build every configuration in CI.

## 6. Exam-ready answers

> [!EXAM]
> **Conditional compilation.** Preprocessor directives `#if`, `#elif`, `#else`, `#endif`, `#ifdef` and `#ifndef` include or exclude source text before compilation based on integer constant expressions and on whether macros are defined (`defined(NAME)`). It is used for include guards, which prevent a header's contents from being processed more than once by defining a unique macro on first inclusion; for platform- and compiler-specific code selected by predefined macros; for build configurations such as debug logging controlled by macros defined on the command line with `-D`; and for disabling assertions with `NDEBUG`. `#error` aborts compilation with a diagnostic. Code in excluded branches is not compiled at all.

## 7. Cheat sheet

| Need | Code |
|---|---|
| header guard | `#ifndef X_H / #define X_H / ... / #endif` or `#pragma once` |
| debug-only code | `#ifdef DEBUG ... #endif` + `-DDEBUG` |
| default config value | `#ifndef N / #define N 8 / #endif` |
| fail the build | `#error "message"` |
| compile-time check | `_Static_assert(cond, "msg")` |
| platform code | `#if defined(_WIN32) ... #elif defined(__linux__)` |
| list predefined macros | `gcc -dM -E - < /dev/null` |
| release asserts off | `-DNDEBUG` |

> [!INTERVIEW]
> **"What problem do include guards solve, and why isn't `#pragma once` standard?"** Without guards, a header included twice in one translation unit (e.g. `a.h` and `b.h` both include `types.h`) has its type definitions processed twice, causing redefinition errors. Guards define a unique macro on first inclusion, and later inclusions skip the content. `#pragma once` asks the compiler to remember the file instead. It's simpler and immune to guard-name collisions, and every major compiler supports it, but it isn't in the ISO standard and can misbehave with the same file reachable through different paths (symlinks, network mounts), where file identity is ambiguous.
