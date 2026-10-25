---
id: c-hello-judge
title: Hello from C
difficulty: Easy
order: 1
tags: printf, main, exit status
---
## Statement
Write a complete C program that prints exactly:

```text
Hello, C!
Compiled, assembled, linked.
```

Use `printf` (or `puts`) and return `0` from `main`.

## Starter
```c
#include <stdio.h>

int main(void) {

}
```

## Tests
=== sample

---
Hello, C!
Compiled, assembled, linked.

## Hints
- A complete C program needs `#include <stdio.h>` and `int main(void) { ... return 0; }`.
- `printf` needs an explicit `\n`; `puts` adds the newline itself.

## Solution
```c
#include <stdio.h>

int main(void) {
    printf("Hello, C!\n");
    puts("Compiled, assembled, linked.");
    return 0;
}
```

`puts` writes its string followed by a newline. With `printf` you add `\n` yourself. Without `#include <stdio.h>`, modern gcc refuses the call (implicit function declaration is an error in C99 and later). Compiling, assembling and linking all happen in the single `gcc` command the judge runs.
