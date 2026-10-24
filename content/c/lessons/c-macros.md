# Macros

The **C preprocessor** runs before the compiler proper. It performs textual transformations: including files, defining **macros**, and selecting code conditionally. Macros are powerful: zero-cost abstractions, compile-time configuration, logging that records file and line, and generic code before `_Generic` existed. But they operate on **tokens, not values**, ignore scope and types, and produce some of the most notorious bugs in C. This lesson teaches how macros expand, the rules that make them safe, and the advanced operators `#` and `##`.

## 1. Object-like macros

```c
#define BUFFER_SIZE 4096
#define PI 3.14159265358979
char buf[BUFFER_SIZE];          // the compiler sees: char buf[4096];
#undef BUFFER_SIZE              // remove the definition
```

Seeing the preprocessed output is the best way to debug macros: `gcc -E file.c`.

> [!TIP]
> Prefer `enum` or `static const` for integer constants when you can (`enum { BUFFER_SIZE = 4096 };`). They have scope, a type, and a name in the debugger. `#define` is necessary for constants used in `#if`, and for non-integer compile-time constants in older C. C23 adds `constexpr` objects.

## 2. Function-like macros and their traps

```c
#define SQ(x) x * x
SQ(1 + 2)          // expands to 1 + 2 * 1 + 2 = 5, not 9!
```

**Rule 1: parenthesise every parameter, and the whole body:**

```c
#define SQ(x) ((x) * (x))
SQ(1 + 2)          // ((1 + 2) * (1 + 2)) = 9
```

**Rule 2: beware arguments with side effects.** They're evaluated as many times as the parameter appears:

```c
#define MAX(a, b) ((a) > (b) ? (a) : (b))
int i = 1;
int m = MAX(i++, 0);   // ((i++) > (0) ? (i++) : (0)): i is incremented TWICE → m = 2, i = 3
```

A `static inline` function has no such problem, and is type-checked:

```c
static inline int max_int(int a, int b) { return a > b ? a : b; }
```

**Rule 3: multi-statement macros need `do { ... } while (0)`:**

```c
#define SWAP_BAD(a, b) int t = a; a = b; b = t;
if (x > y) SWAP_BAD(x, y);       // only the first statement is inside the if!

#define SWAP(a, b) do { int t_ = (a); (a) = (b); (b) = t_; } while (0)
if (x > y) SWAP(x, y); else ...  // behaves exactly like one statement, and needs its semicolon
```

> [!KEY]
> Macro checklist: parenthesise parameters **and** the result; wrap statement macros in `do { } while (0)`; never pass arguments with side effects; use UPPER_CASE names so readers know it's a macro; and prefer `static inline` functions unless you need something only macros can do (the next sections).

## 3. Things only macros can do

### Stringification `#` and token pasting `##`

```c
#define STR(x) #x                 // turns the argument TOKENS into a string literal
STR(a + b)                        // "a + b"

#define CAT(a, b) a##b            // glues two tokens into one
int CAT(my, var) = 7;             // int myvar = 7;

#define VERSION 3
#define XSTR(x) STR(x)            // two-level trick: expand the argument FIRST, then stringify
STR(VERSION)                      // "VERSION"
XSTR(VERSION)                     // "3"
```

### Assertion and logging macros with location

```c
#define LOG(fmt, ...) fprintf(stderr, "%s:%d %s: " fmt "\n", __FILE__, __LINE__, __func__, __VA_ARGS__)
LOG("speed=%d", 42);              // main.c:17 control_loop: speed=42

#define CHECK(cond) do { if (!(cond)) { \
        fprintf(stderr, "check failed: %s (%s:%d)\n", #cond, __FILE__, __LINE__); abort(); } } while (0)
CHECK(ptr != NULL);
```

`__FILE__`, `__LINE__` and `__func__` must be expanded **at the call site**, which a function can't do. That's why `assert` is a macro. `__VA_ARGS__` (C99) forwards variadic arguments, and C23's `__VA_OPT__(,)` handles the zero-argument case.

### Array size

```c
#define ARRAY_LEN(a) (sizeof(a) / sizeof((a)[0]))
int xs[10];
ARRAY_LEN(xs);                    // 10, but WRONG if passed a pointer (it gives sizeof(int *) / sizeof(int))
```

## 4. X-macros: one list, many uses

Keep a single list and expand it several ways, so enums, name tables and switch cases can never drift apart:

```c
#define STATES(X) \
    X(IDLE)       \
    X(MOVING)     \
    X(CHARGING)   \
    X(ERROR)

#define AS_ENUM(name) STATE_##name,
#define AS_STRING(name) #name,

typedef enum { STATES(AS_ENUM) STATE_COUNT } State;            // STATE_IDLE, STATE_MOVING, ...
static const char *state_names[] = { STATES(AS_STRING) };      // "IDLE", "MOVING", ...
```

Add a state in one place and every table updates. Large C codebases (the Linux kernel, CPython's opcode tables, LLVM) use this pattern heavily.

## 5. Generic selection: `_Generic` (C11)

```c
#define abs_any(x) _Generic((x), \
    int: abs,                    \
    long: labs,                  \
    double: fabs,                \
    float: fabsf)(x)

abs_any(-3);      // calls abs
abs_any(-2.5);    // calls fabs
```

`_Generic` picks an expression by the **type** of its controlling argument at compile time. It's how `<tgmath.h>` makes `sqrt` work for float, double and long double.

## 6. Exam-ready answers

> [!EXAM]
> **Macros.** The preprocessor replaces macro names with their definitions before compilation. Object-like macros define constants; function-like macros take parameters that are substituted textually into the replacement list. Because expansion is textual, parameters and the entire replacement should be parenthesised to avoid operator-precedence errors, arguments with side effects may be evaluated more than once, and multi-statement macros should be wrapped in `do { ... } while (0)` to behave as a single statement. The `#` operator converts a macro argument into a string literal and `##` concatenates tokens; predefined macros such as `__FILE__`, `__LINE__` and `__func__` (an identifier) supply source locations. Inline functions are generally preferred for computations because they are type-checked and evaluate arguments exactly once.

## 7. Cheat sheet

| Need | Code |
|---|---|
| safe expression macro | `#define SQ(x) ((x) * (x))` |
| statement macro | `#define M(...) do { ... } while (0)` |
| stringify | `#x` (and `XSTR(x)` → `STR(x)` to expand first) |
| paste tokens | `a##b` |
| variadic | `#define LOG(fmt, ...) printf(fmt, __VA_ARGS__)` |
| location | `__FILE__`, `__LINE__`, `__func__` |
| one list, many tables | X-macros |
| dispatch on type | `_Generic` |
| see the expansion | `gcc -E` |

> [!INTERVIEW]
> **"Why does `#define MAX(a,b) ((a)>(b)?(a):(b))` still have a bug even though it's fully parenthesised?"** Each argument appears twice in the expansion, so arguments with side effects are evaluated twice. `MAX(i++, j)` may increment `i` twice, and `MAX(read_sensor(), limit)` may read the sensor twice and return a value that was never compared. The fix is a `static inline` function, or in GNU C a statement expression with `__typeof__` temporaries. This question tests understanding that macros are textual substitution, not function calls.
