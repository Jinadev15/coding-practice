---
id: c-prototype-order
title: Prototypes and Program Order
difficulty: Easy
order: 2
tags: prototypes, functions, structure
---
## Statement
Complete the program so that `main` (which comes **first** in the file) can call the functions `max3` and `print_line` that are **defined after** it. Add the missing **prototypes** at the top and write the definitions.

- `int max3(int a, int b, int c)` returns the largest of the three.
- `void print_line(int width)` prints `width` `-` characters followed by a newline.

Input: three integers. Output: a line of dashes as wide as the maximum (assume `0 ≤ max ≤ 80`), then `max = M`, then another line of dashes.

## Starter
```c
#include <stdio.h>

/* add prototypes here */

int main(void) {
    int a, b, c;
    scanf("%d %d %d", &a, &b, &c);
    int m = max3(a, b, c);
    print_line(m);
    printf("max = %d\n", m);
    print_line(m);
    return 0;
}

/* add definitions here */
```

## Tests
=== sample
3 7 5
---
-------
max = 7
-------
=== hidden
0 0 0
---

max = 0

=== hidden
12 4 -9
---
------------
max = 12
------------

## Hints
- C compiles top to bottom: a function must be declared before it is called.
- Put prototypes (`int max3(int a, int b, int c);`) above `main`, and the full definitions after it.
- `print_line` is a loop of `putchar('-')` followed by `putchar('\n')`.

## Solution
```c
#include <stdio.h>

int max3(int a, int b, int c);
void print_line(int width);

int main(void) {
    int a, b, c;
    scanf("%d %d %d", &a, &b, &c);
    int m = max3(a, b, c);
    print_line(m);
    printf("max = %d\n", m);
    print_line(m);
    return 0;
}

int max3(int a, int b, int c) {
    int m = a;
    if (b > m) m = b;
    if (c > m) m = c;
    return m;
}

void print_line(int width) {
    for (int i = 0; i < width; i++)
        putchar('-');
    putchar('\n');
}
```

Without the prototypes, the compiler meets `max3(...)` inside `main` before knowing its signature. In C99 and later that's an error (implicit declaration), and in old C it silently assumed `int max3()`. Prototypes are exactly what header files contain, which is how multi-file programs work (Functions module).
