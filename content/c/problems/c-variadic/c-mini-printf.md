---
id: c-mini-printf
title: Write a Mini printf
difficulty: Hard
order: 1
tags: stdarg, variadic, formatting
---
## Statement
Implement `int my_printf(const char *fmt, ...)`, a small printf supporting:

| Directive | Prints |
|---|---|
| `%d` | an `int` in decimal (including negatives and `INT_MIN`) |
| `%u` | an `unsigned int` |
| `%x` | an `unsigned int` in lowercase hex |
| `%s` | a string (`(null)` for a NULL pointer) |
| `%c` | a character |
| `%%` | a literal `%` |

Output characters with `putchar` only. **Don't call** `printf`, `sprintf` or any other formatting function. Convert numbers to digits yourself. Return the number of characters written. An unknown directive `%q` prints `%q` unchanged.

## Starter
```c
#include <stdarg.h>
#include <stdio.h>

int my_printf(const char *fmt, ...) {
    return 0;
}
```

## Driver
```c
#include <limits.h>
int main(void) {
    int n;
    n = my_printf("int %d, neg %d, min %d\n", 42, -7, INT_MIN); my_printf("[%d]\n", n);
    n = my_printf("u=%u x=%x zero=%d\n", 4294967295u, 255u, 0); my_printf("[%d]\n", n);
    n = my_printf("%s|%c|%s|100%%|%q\n", "robot", 'Z', (char *)0); my_printf("[%d]\n", n);
    int a, b;
    while (scanf("%d %d", &a, &b) == 2)
        my_printf("%d + %d = %d (0x%x)\n", a, b, a + b, (unsigned)(a + b));
    return 0;
}
```

## Tests
=== sample
2 3
---
int 42, neg -7, min -2147483648
[32]
u=4294967295 x=ff zero=0
[25]
robot|Z|(null)|100%|%q
[23]
2 + 3 = 5 (0x5)
=== hidden
-10 4
1000000 1000000
---
int 42, neg -7, min -2147483648
[32]
u=4294967295 x=ff zero=0
[25]
robot|Z|(null)|100%|%q
[23]
-10 + 4 = -6 (0xfffffffa)
1000000 + 1000000 = 2000000 (0x1e8480)

## Hints
- Write a helper `int put_unsigned(unsigned long long v, unsigned base)` that fills a small digit buffer **backwards** (`v % base`, `v /= base`), then prints it. Handle `v == 0`.
- `%d`: for a negative value, print `-` and then the magnitude computed as `-(long long)v`. That handles `INT_MIN`, whose magnitude doesn't fit in an `int`.
- `%c`: fetch with `va_arg(ap, int)`, because of default promotion.

## Solution
```c
#include <stdarg.h>
#include <stdio.h>

static int put_unsigned(unsigned long long v, unsigned base) {
    char buf[32];
    int len = 0;
    do {
        buf[len++] = "0123456789abcdef"[v % base];
        v /= base;
    } while (v);
    for (int i = len - 1; i >= 0; i--) putchar(buf[i]);
    return len;
}

int my_printf(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    int count = 0;
    for (const char *p = fmt; *p; p++) {
        if (*p != '%') { putchar(*p); count++; continue; }
        p++;
        switch (*p) {
        case 'd': {
            long long v = va_arg(ap, int);
            if (v < 0) { putchar('-'); count++; v = -v; }
            count += put_unsigned((unsigned long long)v, 10);
            break;
        }
        case 'u': count += put_unsigned(va_arg(ap, unsigned), 10); break;
        case 'x': count += put_unsigned(va_arg(ap, unsigned), 16); break;
        case 's': {
            const char *s = va_arg(ap, const char *);
            if (!s) s = "(null)";
            while (*s) { putchar(*s++); count++; }
            break;
        }
        case 'c': putchar(va_arg(ap, int)); count++; break;
        case '%': putchar('%'); count++; break;
        case '\0': p--; break;
        default: putchar('%'); putchar(*p); count += 2;
        }
    }
    va_end(ap);
    return count;
}
```

Widening to `long long` before negating is the classic `INT_MIN` fix: `-INT_MIN` overflows an `int`, but it fits in a `long long`. The `do … while` prints `0` correctly. The `case '\0'` guard handles a format string ending in a lone `%`. Real printf implementations (glibc, musl) follow this structure, with flags, widths and precision added on top.
