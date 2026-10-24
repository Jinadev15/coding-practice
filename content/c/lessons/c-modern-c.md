# Modern C: C11, C17, C23

C isn't frozen in 1989. C99, C11, C17 and C23 added features that make C safer, more expressive and properly concurrent:
- designated initialisers and compound literals
- `_Static_assert` for compile-time checks
- `_Generic` for type-generic macros
- anonymous structs and unions
- `_Alignas`
- a standard threads library and atomics with a real memory model
- and in C23: `nullptr`, `constexpr`, `typeof`, `bool` as a keyword, `[[attributes]]`, `#embed`, checked integer arithmetic, and binary literals

Knowing them separates "1990s C" from modern embedded and systems code.

## 1. The timeline

| Standard | Notable additions |
|---|---|
| C89/C90 | the baseline ANSI C |
| C99 | `//` comments, `<stdint.h>`, `<stdbool.h>`, declarations anywhere, `for (int i…)`, VLAs, designated initialisers, compound literals, `inline`, `restrict`, `long long`, flexible array members, `snprintf` |
| C11 | `_Static_assert`, `_Generic`, `_Alignas`/`_Alignof`, `_Noreturn`, anonymous structs/unions, `<threads.h>`, `<stdatomic.h>`, the memory model, `_Thread_local`, `aligned_alloc`, VLAs made optional, `gets` removed |
| C17 | a bug-fix release of C11 (no new features) |
| C23 | `bool`/`true`/`false`/`nullptr`/`static_assert`/`alignas`/`thread_local` as keywords, `constexpr` objects, `typeof`, `auto` inference, `[[nodiscard]]`/`[[maybe_unused]]`/`[[deprecated]]`/`[[fallthrough]]`, `0b1010` literals and `1'000'000` digit separators, `<stdbit.h>`, `<stdckdint.h>`, `#embed`, `memset_explicit`, `unreachable()`, empty initialiser `= {}`, enums with fixed underlying types, two's complement mandated |

Compile with `-std=c17` (or `-std=c23` on GCC 13+ / Clang 16+). The judge on this platform uses C17.

## 2. Initialisation done right (C99)

```c
struct Pose { double x, y, theta; };
struct Pose p = { .x = 1.0, .theta = 0.5 };       /* designated: y is zero-initialised */

int lut[256] = { ['a'] = 1, ['e'] = 1, ['i'] = 1, ['o'] = 1, ['u'] = 1 };   /* sparse array init */

void draw(struct Pose p);
draw((struct Pose){ .x = 2, .y = 3 });            /* compound literal: an unnamed object */

int *tmp = (int[]){ 3, 1, 2 };                    /* array compound literal (automatic storage) */
```

Designated initialisers survive struct reordering and document intent, which makes them the standard style for configuration tables and driver structs (e.g. Linux `file_operations`).

## 3. Compile-time checks: `_Static_assert`

```c
#include <assert.h>                      /* defines static_assert as a macro in C11/C17 */
_Static_assert(sizeof(int) == 4, "int must be 32-bit");
static_assert(sizeof(struct Packet) == 16, "wire format layout changed");
static_assert(offsetof(struct Packet, crc) == 12, "crc offset");
```

These cost nothing at run time and catch ABI and layout drift at build time, which is essential for wire protocols and memory-mapped structs.

## 4. Type-generic programming: `_Generic`

`_Generic` selects an expression **at compile time** based on the type of its controlling expression:

```c
#include <math.h>
#include <stdio.h>

#define abs_any(x) _Generic((x), \
    int: abs, long: labs, long long: llabs, \
    float: fabsf, double: fabs, long double: fabsl)(x)

#define print_val(x) _Generic((x), \
    int: print_int, double: print_double, const char *: print_str, char *: print_str, \
    default: print_unknown)(x)

static void print_int(int v) { printf("int %d\n", v); }
static void print_double(double v) { printf("double %g\n", v); }
static void print_str(const char *s) { printf("str %s\n", s); }
static void print_unknown(...) { puts("?"); }      /* C23 allows a variadic function without named params */
```

`<tgmath.h>` uses this to make `sqrt(x)` call `sqrtf`, `sqrt` or `sqrtl` automatically. Notes:
- The controlling expression isn't evaluated.
- Arrays decay and qualifiers are dropped (lvalue conversion), so `const int` matches `int`.
- `char`, `signed char` and `unsigned char` are three distinct types.

## 5. Anonymous structs and unions (C11)

```c
typedef struct {
    enum { CMD_MOVE, CMD_STOP, CMD_GRIP } kind;
    union {                                   /* anonymous union: members accessed directly */
        struct { float vx, vy; };             /* anonymous struct */
        struct { int force; };
    };
} Command;

Command c = { .kind = CMD_MOVE, .vx = 0.5f, .vy = 0.0f };
if (c.kind == CMD_MOVE) printf("%f\n", c.vx);   /* not c.u.s.vx */
```

That's a clean **tagged union**, C's version of a variant type.

## 6. Alignment: `_Alignas`, `_Alignof`, `aligned_alloc`

```c
#include <stdalign.h>
#include <stdlib.h>
alignas(64) static float samples[1024];               /* cache-line aligned (DMA, SIMD) */
float *buf = aligned_alloc(32, 32 * 100);             /* size must be a multiple of the alignment */
free(buf);
printf("%zu\n", alignof(double));
```

## 7. Concurrency: `<threads.h>` and `<stdatomic.h>` (C11)

```c
#include <threads.h>
#include <stdatomic.h>
#include <stdio.h>

static atomic_long hits = 0;

static int worker(void *arg) {
    int n = *(int *)arg;
    for (int i = 0; i < n; i++)
        atomic_fetch_add_explicit(&hits, 1, memory_order_relaxed);   /* a counter needs no ordering */
    return 0;
}

int main(void) {
    thrd_t t[4];
    int n = 100000;
    for (int i = 0; i < 4; i++) thrd_create(&t[i], worker, &n);
    for (int i = 0; i < 4; i++) thrd_join(t[i], NULL);
    printf("%ld\n", atomic_load(&hits));    /* always 400000 */
}
```

| C11 feature | Purpose |
|---|---|
| `thrd_create/join`, `mtx_t`, `cnd_t`, `call_once` | portable threads, mutexes, condition variables |
| `_Thread_local` / `thread_local` | per-thread storage |
| `_Atomic T`, `atomic_int`, `atomic_flag` | lock-free atomic objects |
| `memory_order_relaxed/acquire/release/seq_cst` | the same memory model as C++11 |
| `atomic_compare_exchange_weak/strong` | CAS loops for lock-free structures |

In practice, POSIX `pthreads` remains more widely used on Linux. glibc implements `<threads.h>` on top of it. The atomics and the memory model are the important part.

## 8. C23 highlights

```c
/* compile with -std=c23 */
#include <stdbit.h>
#include <stdckdint.h>

constexpr int N = 16;                       /* a true compile-time constant object */
int *p = nullptr;                           /* typed null pointer constant */
typeof(N) copy = N;                         /* standardised typeof */
auto ratio = 0.75;                          /* type inference (double) */

[[nodiscard]] int open_port(int id);
unsigned flags = 0b1010'0001;               /* binary literal with digit separators */

int r;
if (ckd_add(&r, INT_MAX, 1)) puts("overflow detected");   /* checked arithmetic, no UB */
unsigned bits = stdc_count_ones(flags);                    /* portable popcount */

static const unsigned char firmware[] = {
#embed "firmware.bin"                       /* include binary data at compile time */
};
```

C23 also mandates two's complement representation for signed integers (signed overflow is still UB), defines `= {}` as zero initialisation, and makes `unreachable()` (in `<stddef.h>`) standard.

## 9. Exam-ready answers

> [!EXAM]
> **Major features of C11.** C11 introduced compile-time assertions (`_Static_assert`), type-generic selection (`_Generic`) enabling macros that dispatch on argument type, explicit alignment control (`_Alignas`, `_Alignof`, `aligned_alloc`), anonymous structures and unions, the `_Noreturn` specifier, and, most significantly, a memory model for multithreaded programs with the `<threads.h>` library (threads, mutexes, condition variables, thread-local storage) and `<stdatomic.h>` (atomic types and operations with explicit memory orderings). It also removed the unsafe `gets` function and made variable-length arrays optional. C17 corrected defects without adding features, and C23 later added `nullptr`, `constexpr`, `typeof`, standard attributes and checked integer arithmetic.

## 10. Cheat sheet

| Need | Modern C |
|---|---|
| clear struct init | `{ .field = value }` |
| temporary struct argument | `(struct T){ ... }` |
| compile-time check | `static_assert(cond, "msg")` |
| type-generic macro | `_Generic` |
| tagged union | anonymous union inside a struct |
| aligned memory | `alignas(N)`, `aligned_alloc` |
| atomic counter | `atomic_long`, `atomic_fetch_add` |
| overflow-safe add (C23) | `ckd_add(&r, a, b)` |
| popcount (C23) | `stdc_count_ones` |

> [!INTERVIEW]
> **"How would you write a type-safe `max` in C?"** A macro like `#define MAX(a,b) ((a)>(b)?(a):(b))` evaluates its arguments twice and has no type safety. Better: `static inline` functions per type, dispatched with `_Generic` (`#define max(a,b) _Generic((a), int: max_i, double: max_d)(a, b)`). Or use the GCC statement-expression and `typeof` trick, which C23 standardises the `typeof` part of.
