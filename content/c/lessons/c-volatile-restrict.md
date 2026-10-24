# volatile, restrict and inline

Three keywords communicate facts to the compiler that it can't work out on its own:
- `volatile`: "this memory can change, or be observed, behind your back. Don't optimise accesses away."
- `restrict`: "this pointer is the only way this memory is accessed here. Optimise aggressively."
- `inline`: "make this function's definition available for inlining, and here are the linkage rules."

Used correctly, they're essential in embedded systems and high-performance code. Misused, they cause subtle bugs. `volatile` in particular is widely misunderstood as a threading tool, which it isn't.

## 1. Why the optimiser needs to be told

The compiler reasons about a single thread of execution with no outside interference. Under that model, it may:
- keep a variable in a register instead of re-reading memory
- remove stores whose value is never read again
- merge, reorder or delete repeated loads

```c
int ready;                       /* set by an interrupt handler */
void wait(void) {
    while (!ready) { }           /* may compile to: if (!ready) for (;;) {} — reads ONCE */
}
```

## 2. `volatile`: every access is an observable side effect

```c
volatile int ready;              /* now every read of ready really reads memory */
```

Each read and write of a volatile object must happen, in program order relative to other volatile accesses, exactly as written. Legitimate uses:

| Use | Example |
|---|---|
| memory-mapped hardware registers | `#define UART_DR (*(volatile uint32_t *)0x4000C000u)` |
| variables shared with an interrupt handler (single core) | `volatile bool data_ready;` |
| variables modified by a signal handler | `volatile sig_atomic_t stop;` |
| variables that must survive `longjmp` | locals modified between `setjmp` and `longjmp` |
| defeating optimisation in benchmarks or secure wipes | `volatile` stores to clear secrets (or `memset_explicit` in C23) |

```c
#include <stdint.h>
#define GPIO_BASE   0x48000000u
#define GPIO_ODR    (*(volatile uint32_t *)(GPIO_BASE + 0x14u))   /* output data register */

void blink(void) {
    GPIO_ODR |= (1u << 5);      /* read-modify-write: a real read AND a real write */
    GPIO_ODR &= ~(1u << 5);
}
```

> [!DANGER]
> **`volatile` is not for thread synchronisation.** It doesn't make operations atomic: `counter++` on a volatile is still load, add, store, and two threads can lose updates. It also doesn't order *non-volatile* accesses around it, and it emits no memory barriers on multicore CPUs. A data race on a volatile variable is still UB. For threads, use C11 `<stdatomic.h>` (`atomic_int`, `atomic_fetch_add`) or mutexes. (Java's and C#'s `volatile` are different: they have acquire/release semantics. C's doesn't.)

### Interrupt-shared data on a microcontroller

```c
volatile uint32_t ticks;              /* incremented in the timer ISR */

uint32_t get_ticks(void) {
    /* on an 8/16-bit MCU a 32-bit read isn't atomic: an ISR could fire halfway through */
    uint32_t t;
    __disable_irq();                  /* platform-specific critical section */
    t = ticks;
    __enable_irq();
    return t;
}
```

`volatile` guarantees the read happens. It doesn't guarantee the read is *atomic*.

## 3. `restrict` (C99): a promise about aliasing

```c
void add_arrays(float *restrict out, const float *restrict a, const float *restrict b, size_t n) {
    for (size_t i = 0; i < n; i++)
        out[i] = a[i] + b[i];
}
```

`restrict` promises that during the pointer's lifetime, the object it points to is accessed **only through that pointer** (or pointers derived from it). With it, the compiler knows a store to `out[i]` can't change `a[j]` or `b[j]`, so it can vectorise with SIMD and reorder loads freely. Without it, it must assume overlap and either emit a slower loop or add runtime overlap checks.

| Function | Signature | Why |
|---|---|---|
| `memcpy` | `void *memcpy(void *restrict d, const void *restrict s, size_t n);` | overlap is UB, so it's fast |
| `memmove` | `void *memmove(void *d, const void *s, size_t n);` | overlap allowed, so it handles both directions |
| `printf` | `int printf(const char *restrict fmt, ...);` | |

> [!WARNING]
> Breaking the promise is UB. Calling `add_arrays(x, x, y, n)` with `out` and `a` aliasing violates `restrict`, and the vectorised code may read stale values. Use `restrict` only when you control every call site, and document it.

`restrict` doesn't exist in C++ (compilers offer `__restrict` as an extension).

## 4. `inline`

`inline` suggests inlining and, more importantly, changes the **linkage rules** so that a function definition can live in a header.

| Form | Meaning in C99 and later | Typical use |
|---|---|---|
| `static inline` | internal linkage: every translation unit gets its own private copy (if one is needed at all) | **the safe default in headers** |
| `inline` (alone) | an *inline definition*: it provides no external symbol by itself | a header plus one `.c` with `extern inline` |
| `extern inline` (in exactly one `.c`) | emits the single external definition | pairs with the above |

```c
/* vec.h */
static inline float dot3(const float *a, const float *b) {
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}
```

> [!KEY]
> C's `inline` rules differ from C++'s. In C, a plain `inline` function in a header without an `extern inline` declaration somewhere gives "undefined reference" at link time when the compiler decides *not* to inline it (e.g. at `-O0`). That's why `static inline` is the common idiom in C headers. Compilers inline based on their own heuristics either way. `__attribute__((always_inline))` and `noinline` override them.

### Inline functions vs function-like macros

| | `static inline` function | macro |
|---|---|---|
| type checking | ✓ | ✗ |
| arguments evaluated once | ✓ | ✗ (`MAX(i++, j)` evaluates twice) |
| debuggable, has an address | ✓ | ✗ |
| generic over types | ✗ (use `_Generic`) | ✓ |
| performance | the same when inlined | the same |

## 5. `const` vs `volatile` together

`const volatile` is meaningful: the program may not write it, but it can change underneath (a read-only status register):

```c
#define STATUS (*(const volatile uint32_t *)0x40001000u)
while (!(STATUS & READY_BIT)) { }      /* polls the hardware every iteration */
```

## 6. Exam-ready answers

> [!EXAM]
> **The volatile qualifier.** Declaring an object `volatile` tells the compiler that its value may change, or its accesses may have effects, in ways not visible in the program, for example memory-mapped hardware registers, variables modified by interrupt or signal handlers, or objects used across `setjmp`/`longjmp`. Every read and write of a volatile object must therefore be performed as written and not cached in registers, merged or eliminated. `volatile` provides neither atomicity nor inter-thread memory ordering, so it's not a substitute for atomics or locks in multithreaded code.

> [!EXAM]
> **The restrict qualifier.** `restrict` qualifies a pointer to declare that, for the pointer's lifetime, the object it designates is accessed only through it or pointers based on it. This lets the compiler assume no aliasing between restrict-qualified pointers and generate more efficient code, such as vectorised loops; violating the assertion is undefined behaviour. It's used in standard functions such as `memcpy`, whose arguments must not overlap, in contrast with `memmove`.

## 7. Cheat sheet

| Need | Use |
|---|---|
| hardware register | `*(volatile uint32_t *)ADDR` |
| ISR flag (single core) | `volatile bool`, plus a critical section for multi-word values |
| signal handler flag | `volatile sig_atomic_t` |
| thread communication | `<stdatomic.h>` or a mutex, **not** `volatile` |
| no-alias guarantee | `T *restrict p` |
| small function in a header | `static inline` |
| read-only hardware status | `const volatile` |

> [!INTERVIEW]
> **"Is `volatile int counter; counter++` thread-safe?"** No. It's a read-modify-write of three steps, and volatile makes each step happen but doesn't make them indivisible. Two threads can both read 5 and both write 6. Use `atomic_int counter; atomic_fetch_add(&counter, 1);` or a mutex. Volatile is for hardware and interrupt visibility on a single core, not for inter-thread synchronisation.
