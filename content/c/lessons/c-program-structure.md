# Program Structure, main and printf

Every C program has the same skeleton: includes, (optional) declarations, and a `main` function where execution starts. This lesson dissects that skeleton line by line, so nothing in a C file is mysterious: what `#include` really does, why `main` returns `int`, what `void` means in `main(void)`, how statements and blocks work, and how `printf` prints.

## 1. The anatomy of a C program

```c
#include <stdio.h>          /* 1. preprocessor directive: bring in declarations */

#define LIMIT 3             /* 2. macro constant (replaced before compilation) */

int square(int x);          /* 3. function prototype (declaration) */

int main(void) {            /* 4. entry point */
    for (int i = 1; i <= LIMIT; i++) {
        printf("%d squared is %d\n", i, square(i));
    }
    return 0;               /* 5. exit status: 0 = success */
}

int square(int x) {         /* 6. function definition */
    return x * x;
}
```

```output
1 squared is 1
2 squared is 4
3 squared is 9
```

| Part | What it is |
|---|---|
| `#include <stdio.h>` | pastes the **declarations** of standard I/O functions (`printf`, `scanf`…) into the file. The code itself is linked from libc. |
| `#define LIMIT 3` | text substitution by the preprocessor; no type, no memory |
| `int square(int x);` | a **prototype**: tells the compiler `square`'s signature before its definition appears |
| `int main(void)` | where execution starts; returns an `int` to the OS |
| `{ ... }` | a **block** (compound statement): groups statements and creates a scope |
| `;` | ends every statement (not after `}` of a function or block) |
| `return 0;` | the exit status |

## 2. `main`

> [!SYNTAX]
> The two standard signatures:
> ```c
> int main(void) { ... }                       /* no command-line arguments */
> int main(int argc, char *argv[]) { ... }     /* with arguments (later lesson) */
> ```

- `main` must return `int`. `void main()` is non-standard and wrong in portable C.
- `(void)` means "takes **no** arguments". In C (before C23) an empty list `()` meant "unspecified arguments", which is older and less safe. Write `(void)`.
- Reaching the closing `}` of `main` without `return` returns 0 (since C99), but write `return 0;` explicitly.
- `EXIT_SUCCESS` and `EXIT_FAILURE` from `<stdlib.h>` are portable names for the exit codes.

## 3. Statements, blocks and whitespace

- C is **free-form**: whitespace and newlines don't matter to the compiler (unlike Python's indentation). Indentation is for humans, so use it consistently (4 spaces is common).
- Every simple statement ends with `;`. A missing `;` is the most common beginner error, and the compiler often reports it on the *next* line.
- `{ }` groups statements into a block. Variables declared inside a block exist only inside it.

```c
if (x > 0)
    printf("positive\n");
    printf("always printed!\n");    /* NOT part of the if: indentation lies */
```

> [!DANGER]
> Without braces, an `if`/`for`/`while` controls exactly **one** statement. Misleading indentation like the example above has caused real security bugs (Apple's "goto fail"). Many style guides require braces always.

## 4. Comments

```c
/* block comment: can span
   several lines; cannot be nested */
// line comment (C99 and later)
```

## 5. printf: formatted output

> [!SYNTAX]
> `int printf(const char *format, ...);`
>
> Prints `format`, replacing each **conversion specification** (`%d`, `%s`…) with the next argument. Returns the number of characters printed.

| Specifier | Type | Example → output |
|---|---|---|
| `%d` / `%i` | `int` | `printf("%d", 42)` → `42` |
| `%u` | `unsigned int` | |
| `%ld`, `%lld` | `long`, `long long` | |
| `%f` | `double` (`float` is promoted) | `printf("%.2f", 3.14159)` → `3.14` |
| `%e`, `%g` | scientific / shortest form | |
| `%c` | `char` | `printf("%c", 'A')` → `A` |
| `%s` | string (`char *`) | `printf("%s", "hi")` → `hi` |
| `%x`, `%X`, `%o` | hex, octal | `printf("%x", 255)` → `ff` |
| `%p` | pointer address | |
| `%zu` | `size_t` (e.g. `sizeof`) | |
| `%%` | a literal `%` | |

Width and precision work like Python's format spec: `%5d` (width 5, right-aligned), `%-5d` (left-aligned), `%05d` (zero-padded), `%.3f` (3 decimals), `%8.2f`.

```c
printf("[%5d] [%-5d] [%05d]\n", 42, 42, 42);   /* [   42] [42   ] [00042] */
printf("%.3f %e\n", 3.14159, 12345.678);       /* 3.142 1.234568e+04 */
printf("%s has %zu chars\n", "abc", sizeof("abc") - 1);
```

> [!DANGER]
> printf **does not check types at run time**. `printf("%d", 3.5)` or `printf("%s", 42)` is **undefined behaviour**: garbage output or a crash. The compiler warns about mismatches with `-Wall` (`-Wformat`). Read those warnings.

Escape sequences: `\n` newline, `\t` tab, `\\` backslash, `\"` quote, `\0` the null character.

## 6. Headers you'll need early

| Header | Provides |
|---|---|
| `<stdio.h>` | `printf`, `scanf`, `puts`, `getchar`, file I/O |
| `<stdlib.h>` | `malloc`, `free`, `exit`, `atoi`, `rand`, `qsort` |
| `<string.h>` | `strlen`, `strcpy`, `strcmp`, `memcpy` |
| `<math.h>` | `sqrt`, `pow`, `sin` (link with `-lm`) |
| `<stdbool.h>` | `bool`, `true`, `false` (C99–C17; built in since C23) |
| `<stdint.h>` | `int32_t`, `uint8_t`… |
| `<limits.h>` | `INT_MAX`, `CHAR_BIT`… |

`#include <file>` searches the system include directories; `#include "file.h"` searches the current directory first (used for your own headers).

## 7. Exam-ready answers

> [!EXAM]
> **Structure of a C program.** A C program typically consists of preprocessor directives (such as `#include` for header files and `#define` for macros), global declarations and function prototypes, the `main` function, and other function definitions. Execution begins at `main`, which returns an integer exit status to the operating system: 0 indicates success. Statements are terminated by semicolons and grouped into blocks with braces; whitespace is not significant. Header files contain declarations of library functions, whose definitions are supplied by the linker from libraries such as the C standard library.

> [!EXAM]
> **`printf`.** `printf` writes formatted output to standard output. Its first argument is a format string containing ordinary characters and conversion specifications beginning with `%` (`%d` for int, `%f` for double, `%c` for char, `%s` for strings, `%x` for hexadecimal, `%p` for pointers), optionally with flags, a field width and a precision. The remaining arguments must match the conversions in number and type; mismatches cause undefined behaviour. It returns the number of characters written.

## 8. Cheat sheet

| Need | Code |
|---|---|
| skeleton | `#include <stdio.h>` then `int main(void) { ...; return 0; }` |
| print an int | `printf("%d\n", n);` |
| print a double with 2 decimals | `printf("%.2f\n", x);` |
| print a string | `printf("%s\n", s);` or `puts(s);` (adds `\n`) |
| print a char | `printf("%c", c);` / `putchar(c);` |
| print a size | `printf("%zu\n", sizeof x);` |
| compile | `gcc -Wall -Wextra main.c -o main` |

> [!INTERVIEW]
> **"What's the difference between `int main()` and `int main(void)` in C?"** Before C23, an empty parameter list in a definition meant the function takes no arguments, but in a **declaration** it meant "unspecified parameters", so the compiler couldn't check calls. `(void)` explicitly means no parameters, everywhere. C23 finally makes `()` mean `(void)`. In C++, `()` has always meant no parameters.
