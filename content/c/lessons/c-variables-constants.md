# Variables, Constants and Literals

A C variable is a **named region of memory** with a fixed type: exactly the "box" model that Python *doesn't* use. Declaring it reserves storage; assigning copies a value into the box. This lesson covers declaration vs initialisation, the danger of uninitialised variables, the kinds of constants (`const`, `#define`, `enum`), and how to write literals of every type correctly.

## 1. Declaring and initialising

> [!SYNTAX]
> ```c
> type name;                 /* declaration (and definition): storage reserved, value indeterminate */
> type name = value;         /* declaration with initialisation */
> type a = 1, b, c = 3;      /* several of the same type */
> ```

```c
int count = 0;
double ratio = 0.75;
char grade = 'A';
int x, y = 5;               /* x is uninitialised; only y = 5 */
```

C is **statically typed**: a variable's type is fixed at compile time and never changes. Since C99 you can declare variables anywhere in a block, including inside `for (int i = 0; ...)`. Declare them close to first use.

### Assignment copies the value

```c
int a = 5;
int b = a;      /* b gets a COPY of 5 */
b = 10;         /* a is still 5: separate boxes */
```

<div class="figure">
<svg viewBox="0 0 460 110" width="460" xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace, monospace" font-size="14">
  <rect x="30" y="35" width="90" height="45" fill="none" stroke="#2f81f7" stroke-width="2"/><text x="70" y="64" fill="currentColor">5</text><text x="62" y="25" fill="currentColor">a</text>
  <rect x="190" y="35" width="90" height="45" fill="none" stroke="#2f81f7" stroke-width="2"/><text x="225" y="64" fill="currentColor">10</text><text x="222" y="25" fill="currentColor">b</text>
  <text x="300" y="64" fill="currentColor" font-family="sans-serif" font-size="12" fill-opacity=".7">each variable owns its bytes</text>
</svg>
<figcaption>In C a variable is storage. In Python a name refers to an object. Same syntax, different model.</figcaption>
</div>

## 2. Uninitialised variables

> [!DANGER]
> A local (automatic) variable that isn't initialised has an **indeterminate** value: whatever bytes were in that memory before. Reading it is a bug, and for some types undefined behaviour. `gcc -Wall` warns (`'x' is used uninitialized`). **Initialise every variable at declaration.**

Global and `static` variables are different: they're zero-initialised automatically (Storage Classes lesson).

## 3. Constants

| Mechanism | Example | Type-checked? | Has an address? | Notes |
|---|---|---|---|---|
| `const` variable | `const double PI = 3.14159;` | yes | yes | read-only variable; preferred |
| `#define` macro | `#define MAX 100` | no (text substitution) | no | handled by the preprocessor; usable in `#if` |
| `enum` constant | `enum { MAX_SENSORS = 8 };` | yes (an int) | no | good for named integer constants |

```c
#define BUFFER_SIZE 256          /* no semicolon, no = */
const int max_retries = 3;
enum { LEFT, RIGHT };            /* LEFT = 0, RIGHT = 1 */

max_retries = 4;                 /* compile error: assignment of read-only variable */
```

> [!WARNING]
> In C (unlike C++), a `const int` is **not** a constant expression, so it can't size a static array at file scope or be used in a `switch` `case`. Use `#define` or `enum` for those. C23 adds `constexpr` for objects.

## 4. Literals

| Kind | Examples | Type |
|---|---|---|
| decimal integer | `42`, `-7` | `int` (or wider if it doesn't fit) |
| hex / octal / binary | `0x2A`, `052`, `0b101010` (C23; a GCC extension before) | `int` |
| suffixes | `42u`, `42L`, `42LL`, `42ULL` | unsigned / long / long long |
| floating | `3.14`, `1e-3`, `2.5f` | `double` (`float` with `f`) |
| character | `'A'`, `'\n'`, `'\0'`, `'\x41'` | **`int`** in C! |
| string | `"hello"` | array of `char`, ending in `'\0'` |

> [!DANGER]
> A leading zero makes an **octal** literal: `int code = 010;` is **8**, not 10. And `sizeof('a')` is 4 in C (character constants have type `int`), but 1 in C++.

Large-number gotcha:

```c
long long big = 1000000 * 1000000;     /* OVERFLOW: computed in int first, then converted */
long long ok  = 1000000LL * 1000000;   /* correct: one operand is long long */
```

## 5. Identifiers and naming

Rules: letters, digits and `_`; can't start with a digit; case-sensitive; can't be a keyword (`int`, `return`, `static`…). Names starting with `_` + uppercase, or `__`, are reserved for the implementation, so avoid them. Common C style: `snake_case` for variables and functions, `UPPER_CASE` for macros and enum constants.

## 6. Scope preview

A variable declared inside `{ }` exists only from its declaration to the closing brace. Inner blocks can **shadow** outer names (legal, but confusing; `-Wshadow` warns). The Storage Classes lesson covers lifetime and linkage fully.

## 7. Exam-ready answers

> [!EXAM]
> **Variables in C.** A variable is a named storage location whose type, fixed at compile time, determines its size, the values it can hold and the operations allowed on it. A declaration specifies the type and name; a definition additionally allocates storage; an initialisation gives an initial value. Automatic (local) variables that are not initialised have indeterminate values, whereas variables with static storage duration (globals and `static` locals) are initialised to zero. Assignment copies a value into the variable's storage.

> [!EXAM]
> **`const` vs `#define`.** `#define NAME value` creates a preprocessor macro: the text is substituted before compilation, with no type, no scope and no storage. A `const`-qualified variable is a typed, scoped object whose value cannot be modified after initialisation. It is checked by the compiler and visible in debuggers, but in C it is not a constant expression. Enumeration constants provide typed integer constant expressions.

## 8. Cheat sheet

| Need | Code |
|---|---|
| declare and initialise | `int n = 0;` |
| read-only value | `const double G = 9.81;` |
| compile-time constant | `#define N 100` / `enum { N = 100 };` |
| long long literal | `10000000000LL` |
| float literal | `1.5f` |
| hex | `0xFF` |
| avoid | uninitialised locals; leading-zero decimals |

> [!INTERVIEW]
> **"Why is `#define SQUARE(x) x*x` dangerous, and why is `const` often better than `#define` for constants?"** Macros are blind text substitution: `SQUARE(1+2)` becomes `1+2*1+2 = 5`. They also have no type and no scope, and they're invisible to debuggers. `const` variables are typed, scoped and debuggable. Macros remain useful for conditional compilation and true compile-time constants (Preprocessor module).
