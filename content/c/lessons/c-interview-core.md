# C Interview Deep Dive I

Embedded, systems and robotics interviews probe C at the level of **what the compiler and machine actually do**. This lesson collects the classic questions, each with the precise answer an interviewer expects and the reasoning behind it: arrays vs pointers, `sizeof` traps, `static`, `const` and `volatile`, struct padding, integer promotion, strings, macros, and the code exercises that always appear. Every output shown was produced by GCC 15 on x86-64 Linux (LP64: `int` 4 bytes, pointers 8 bytes).

## 1. Arrays vs pointers

```c
int arr[10]; int *p = arr;
printf("%zu %zu %zu\n", sizeof arr, sizeof p, sizeof arr / sizeof arr[0]);   /* 40 8 10 */
void f(int a[10]) { printf("%zu\n", sizeof a); }                           /* 8: a is int* */
```

> [!INTERVIEW] Is an array a pointer?
> No. An array is a contiguous object of N elements, and `sizeof` gives the whole object. In most expressions it **decays** to a pointer to its first element. The exceptions are the operands of `sizeof`, `&`, and a string literal initialising a char array. A function parameter declared `int a[10]` *is* an `int *`: the 10 is ignored, which is why array sizes must be passed separately.

| Expression | Type | Meaning |
|---|---|---|
| `arr` | decays to `int *` | address of `arr[0]` |
| `&arr` | `int (*)[10]` | the same address, but `&arr + 1` skips 40 bytes |
| `arr[i]` | `int` | exactly `*(arr + i)`, so `i[arr]` is legal too (`3["abcd"] == 'd'`) |
| `int (*pa)[10]` | pointer to an array of 10 ints | |
| `int *ap[10]` | array of 10 pointers | |

**Strings:** `char s1[] = "hello";` is a 6-byte modifiable array (the terminator is included: `sizeof` 6, `strlen` 5). `const char *s2 = "hello";` points to a string literal in read-only memory. Writing through it is undefined behaviour, which is why it should always be `const char *`.

**2-D arrays:** with `int a[3][4]`, `sizeof a[0]` is 16 and `sizeof a` is 48. `a` decays to `int (*)[4]`, so functions take `int a[][4]` or `int (*a)[4]`. An `int **` is a different thing: an array of row pointers.

## 2. `sizeof` traps

- `sizeof` is an **operator**, evaluated at compile time (except for VLAs). Its operand is **not evaluated**: `sizeof(x++)` leaves `x` unchanged.
- `sizeof('a')` is **4** in C, because character constants have type `int`. In C++ it's 1.
- `sizeof` gives `size_t`, so print it with `%zu`.
- `sizeof(struct)` includes padding, as explained next.

## 3. Struct padding and alignment

```c
struct A { char c; int i; char d; };   /* 12 bytes: c, 3 pad, i, d, 3 pad */
struct B { int i; char c; char d; };   /* 8 bytes: members ordered big to small */
struct C { char c; double d; };        /* 16 bytes: double aligned to 8 */
```

Each member is placed at an offset that's a multiple of its alignment, and the struct's size is rounded up to a multiple of its largest alignment, so arrays of structs stay aligned. **Ordering members from largest to smallest** minimises padding. `offsetof(struct A, i)` is 4.

- `__attribute__((packed))` removes padding, for wire formats, but misaligned access is slow on x86 and can **fault** on some ARM cores. Prefer serialising field by field.
- Never `memcmp` structs: padding bytes are indeterminate.
- Never send raw structs over a network or into a file. Padding, endianness and sizes differ between platforms.

## 4. `static`, `extern` and storage

| Where `static` appears | Effect |
|---|---|
| a local variable | **static storage duration**: initialised once (to 0 by default), keeps its value between calls |
| a global variable or function | **internal linkage**: visible only in this translation unit (encapsulation in C) |
| inside array parameter brackets (`int a[static 10]`) | promises at least 10 elements |

`extern int g;` declares without defining. Exactly one `.c` file defines `int g;`, which is the One Definition Rule in C. Memory regions: `.text` (code), `.rodata` (literals and const globals), `.data` (initialised globals), `.bss` (zero-initialised globals, taking no file space), the heap (`malloc`) and the stack (locals).

## 5. `const`: read right to left

```c
const int *a;        /* pointer to const int: *a = 1 is an error; a = &y is fine */
int const *b;        /* same as a */
int *const c = &x;   /* const pointer to int: *c = 1 is fine; c = &y is an error */
const int *const d;  /* neither can change */
```

`const` means "read-only through this name", not "constant": another non-const pointer, or hardware, may still change the object. A `const` global in C has external linkage, unlike C++.

## 6. `volatile`

Use it for memory-mapped registers, variables modified by an ISR or a signal handler, and `setjmp` locals. It forces every access to happen as written. It does **not** provide atomicity or inter-thread ordering. For threads, use `_Atomic` and mutexes (see the register and ISR lessons). A classic question: can a variable be both `const` and `volatile`? Yes, for example a read-only status register: `volatile const uint32_t *SR`.

## 7. Integer promotion and conversions

```c
unsigned u = 1; int i = -1;
printf("%d\n", i < u);          /* 0: i converts to unsigned 4294967295 */
char c = 200; printf("%d\n", c); /* -56 on x86 (char is signed); 200 on ARM Linux (unsigned char) */
uint8_t b = 0xF0; printf("%d\n", (b << 4) > 0xFF);   /* 1: b is promoted to int before shifting */
printf("%d %d %d\n", 7 / -2, 7 % -2, -7 % 2);           /* -3 1 -1: division truncates toward zero */
```

- **Integer promotion**: `char`, `short` and `uint8_t` operands become `int` in arithmetic.
- **Usual arithmetic conversions**: when signed meets unsigned of the same rank, the signed value converts to unsigned. That makes comparisons like `if (len - 1 < n)` with `size_t len = 0` catastrophic.
- Whether plain `char` is signed is **implementation-defined**. Use `unsigned char` or `uint8_t` for bytes.

## 8. Macros and the preprocessor

```c
#define SQUARE(x) x * x
SQUARE(1 + 2)            /* 1 + 2 * 1 + 2 = 5, not 9: parenthesise everything */
#define SQUARE2(x) ((x) * (x))
SQUARE2(i++)             /* i++ evaluated twice: UB. Prefer static inline functions */
#define SWAP(a, b) do { int t_ = (a); (a) = (b); (b) = t_; } while (0)    /* safe in if/else */
#define STR(x) #x        /* stringize */
#define CAT(a, b) a##b   /* token pasting */
```

The `do { … } while (0)` idiom makes a multi-statement macro behave as one statement, so `if (c) SWAP(x, y); else …` compiles correctly. Include guards (`#ifndef H / #define H / #endif`, or `#pragma once`) prevent double inclusion.

## 9. Order of evaluation: unspecified or undefined

```c
static int counter(void) { static int n; return ++n; }
printf("%d %d %d\n", counter(), counter(), counter());     /* printed "3 2 1" with GCC */
```

The order in which function arguments are evaluated is **unspecified**, and GCC on x86-64 often goes right to left. Worse, `i = i++ + 1;`, `a[i] = i++;` and `printf("%d %d", *q++, *q)` modify and read the same object without sequencing, which is **undefined behaviour**. Write separate statements.

## 10. The coding questions that always come up

```c
/* reverse a singly linked list in place: O(n) time, O(1) space */
struct Node { int v; struct Node *next; };
struct Node *reverse(struct Node *head) {
    struct Node *prev = NULL;
    while (head) { struct Node *next = head->next; head->next = prev; prev = head; head = next; }
    return prev;
}

/* count set bits: Kernighan, one iteration per set bit */
int popcount(uint32_t x) { int n = 0; while (x) { x &= x - 1; n++; } return n; }

/* is x a power of two? */
int is_pow2(uint32_t x) { return x && !(x & (x - 1)); }

/* swap without a temporary: a cute trick, but it fails when a and b alias. Use a temporary */
```

Other staples include implementing `strlen`, `strcpy`, `memcpy` and `memmove` (overlap!), `atoi` with overflow detection, detecting a cycle (Floyd), endianness detection, and a circular buffer. This module's problems cover them.

> [!EXAM]
> **What is the difference between `char *p = "abc";` and `char a[] = "abc";`?**
> `a` is an array of 4 modifiable chars initialised from the literal: `sizeof a` is 4, the storage is automatic or static, and `a` can't be reassigned. `p` is a pointer (`sizeof p` is 8 on 64-bit) to a string literal stored in read-only memory. Modifying `*p` is undefined behaviour (it usually segfaults), but `p` itself can be re-pointed. It should be declared `const char *`.
