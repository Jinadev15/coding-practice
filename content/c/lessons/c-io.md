# Formatted I/O: printf and scanf

Reading input correctly in C is harder than in Python, because C makes you manage types, buffers and whitespace yourself. Most "my C program works on my input but fails the judge" bugs are I/O bugs: unchecked `scanf` return values, leftover newlines eaten by `%c`, buffer overflows with `%s`. This lesson gives you safe, idiomatic patterns for every common input shape.

## 1. `scanf` basics

> [!SYNTAX]
> `int scanf(const char *format, ...);`
>
> Reads from stdin according to `format` and stores the converted values through the **pointers** you pass. Returns the **number of items successfully converted**, or `EOF` if input ended before the first conversion.

```c
int age;
double height;
scanf("%d %lf", &age, &height);    /* & passes the ADDRESS, so scanf can write into the variable */
```

| Specifier | Reads into | Note |
|---|---|---|
| `%d` | `int *` | skips leading whitespace |
| `%ld` / `%lld` | `long *` / `long long *` | |
| `%u` | `unsigned *` | |
| `%f` | **`float *`** | |
| `%lf` | **`double *`** | ← different from printf! |
| `%c` | `char *` | does **not** skip whitespace |
| `%s` | `char *` (array) | reads one whitespace-delimited word; **give it a width** |
| `%[^\n]` | `char *` | reads up to a newline (a scanset) |

> [!DANGER]
> The three classic `scanf` bugs:
> 1. **Forgetting `&`**: `scanf("%d", n)` passes the *value* of `n` as an address, which is undefined behaviour and usually a crash. (Arrays are the exception: `scanf("%99s", name)`, because an array name already converts to a pointer.)
> 2. **`%f` for a `double`**: you must use `%lf` in scanf. (In printf, `%f` is the double.)
> 3. **`%s` without a width**: `scanf("%s", buf)` with a 16-byte buffer overflows on longer input, a security hole. Always use `scanf("%15s", buf)` (width = size − 1, for the `'\0'`).

## 2. Always check the return value

```c
int x;
if (scanf("%d", &x) != 1) {
    fprintf(stderr, "expected an integer\n");
    return 1;
}
```

On input `abc`, `scanf("%d")` returns 0, leaves `x` **unchanged** (possibly uninitialised), and leaves `abc` in the input stream. A loop that ignores the return value can spin forever.

### Reading until end of input

```c
int v;
long long sum = 0;
while (scanf("%d", &v) == 1)     /* stops at EOF (returns -1) or on bad input (returns 0) */
    sum += v;
```

Reading characters until EOF:

```c
int ch;                           /* int, not char: EOF is a value outside char's range */
while ((ch = getchar()) != EOF)
    putchar(ch);
```

> [!WARNING]
> `getchar()` returns `int`, not `char`. Storing it in a `char` breaks the EOF test: with signed char, byte 0xFF equals −1 and stops early; with unsigned char, the loop never ends.

## 3. Whitespace and `%c`

All conversions except `%c`, `%[` and `%n` skip leading whitespace (spaces, tabs, newlines). `%c` reads the very next character, **including the newline left over from the previous line**:

```c
int n;
char c;
scanf("%d", &n);      /* input "3\nZ": reads 3, leaves '\n' */
scanf("%c", &c);      /* c == '\n' (10), not 'Z'! */
scanf(" %c", &c);     /* the SPACE in the format skips any whitespace → c == 'Z' */
```

A space in a scanf format means "skip any amount of whitespace, including none".

## 4. Reading whole lines: `fgets`

```c
char line[256];
if (fgets(line, sizeof line, stdin) != NULL) {
    line[strcspn(line, "\n")] = '\0';     /* strip the trailing newline, if present */
    printf("[%s]\n", line);
}
```

- `fgets(buf, size, stream)` reads at most `size - 1` characters, **keeps the newline**, always adds `'\0'`, and returns `NULL` at EOF.
- It's the **safe** way to read text. Then parse the line with `sscanf` or `strtol`.
- **Never use `gets`**: it can't limit the input length, and it was removed from the language in C11.

### Line-then-parse: the robust pattern

```c
char line[128];
while (fgets(line, sizeof line, stdin)) {
    int a, b;
    if (sscanf(line, "%d %d", &a, &b) == 2)
        printf("%d\n", a + b);
    else
        printf("bad line\n");
}
```

Mixing `scanf("%d")` with `fgets` leads to the leftover-newline problem. Reading every line with `fgets` and parsing it with `sscanf` avoids it entirely.

## 5. Other I/O functions

| Function | Does |
|---|---|
| `putchar(c)` / `getchar()` | one character |
| `puts(s)` | a string plus a newline |
| `fputs(s, stdout)` | a string without a newline |
| `fprintf(stderr, ...)` | print errors (not compared by judges) |
| `sprintf` / **`snprintf(buf, size, ...)`** | format into a buffer. Use `snprintf`: `sprintf` can overflow |
| `sscanf(str, fmt, ...)` | parse from a string |
| `strtol(s, &end, 10)` | robust integer parsing with error detection |

## 6. Buffering

`stdout` is line-buffered on a terminal but **fully buffered when redirected** (as in a judge). If your program crashes, buffered output may never appear. When debugging crashes, print to `stderr` (unbuffered) or call `fflush(stdout)`.

## 7. Exam-ready answers

> [!EXAM]
> **`scanf`.** `scanf` reads formatted input from standard input. Its format string contains conversion specifications such as `%d`, `%f` (float), `%lf` (double), `%c` and `%s`, and the corresponding arguments must be pointers to variables of matching types (hence the address-of operator `&`). It returns the number of input items successfully assigned, or `EOF` on end of input before any conversion, and this value should always be checked. Most conversions skip leading whitespace, but `%c` does not; a space in the format skips whitespace. `%s` reads a whitespace-delimited word and must be given a maximum field width to prevent buffer overflow. For line-oriented input, `fgets` followed by `sscanf` is the safer approach.

## 8. Cheat sheet

| Input shape | Pattern |
|---|---|
| two ints | `scanf("%d %d", &a, &b)` |
| a double | `scanf("%lf", &x)` |
| a word | `char w[64]; scanf("%63s", w);` |
| a char after a number | `scanf(" %c", &c)` |
| until EOF | `while (scanf("%d", &v) == 1)` |
| a full line | `fgets(line, sizeof line, stdin)` + strip `\n` |
| a line, then parse | `fgets` + `sscanf` |
| characters | `int ch; while ((ch = getchar()) != EOF)` |

> [!INTERVIEW]
> **"Why is `gets()` considered so dangerous that it was removed from C?"** It writes input into a buffer with no way to specify the buffer's size, so any line longer than the buffer overwrites adjacent memory: a classic stack buffer overflow, exploited by the 1988 Morris worm. `fgets` takes the buffer size. The same reasoning applies to `%s` without a width, and to `strcpy`/`sprintf` versus their bounded alternatives.
