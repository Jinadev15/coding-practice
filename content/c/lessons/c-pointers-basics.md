# Pointer Basics

A **pointer** is a variable that holds a **memory address**. Pointers are the single most important idea in C: they're how functions modify their callers' data, how arrays are passed, how dynamic memory works, how data structures (linked lists, trees, graphs) are built, and how C talks to hardware. They're also the thing Python hides from you completely. Every Python name is secretly a pointer to an object, and now you get to see and control them directly.

## 1. Memory and addresses

Memory is a huge array of bytes, each with a numeric **address**. A variable occupies some consecutive bytes starting at its address.

```c
int x = 42;
printf("%p\n", (void *)&x);     /* e.g. 0x7ffd3c1a2b4c: where x lives */
```

## 2. Declaring, taking addresses, dereferencing

> [!SYNTAX]
> ```c
> int *p;        /* p is a "pointer to int": it can hold the address of an int */
> p = &x;        /* & = address-of operator: p now points to x */
> *p = 20;       /* * = dereference: "the int that p points to" */
> ```

```c
int x = 10;
int *p = &x;
*p = 20;                       /* writes into x */
printf("%d %d\n", x, *p);      /* 20 20 */
```

<div class="figure">
<svg viewBox="0 0 520 130" width="520" xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace, monospace" font-size="13">
  <defs><marker id="pa" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <rect x="40" y="45" width="130" height="45" fill="none" stroke="#2f81f7" stroke-width="2"/><text x="52" y="73" fill="currentColor">0x7ffd…b4c</text>
  <text x="85" y="35" fill="#2f81f7">p</text><text x="45" y="110" fill="currentColor" fill-opacity=".7" font-size="11">@ 0x7ffd…b50 (8 bytes)</text>
  <rect x="320" y="45" width="130" height="45" fill="none" stroke="#3fb950" stroke-width="2"/><text x="372" y="73" fill="currentColor">20</text>
  <text x="378" y="35" fill="#3fb950">x</text><text x="325" y="110" fill="currentColor" fill-opacity=".7" font-size="11">@ 0x7ffd…b4c (4 bytes)</text>
  <line x1="172" y1="67" x2="316" y2="67" stroke="currentColor" marker-end="url(#pa)"/>
  <text x="215" y="58" fill="currentColor" font-size="12">*p is x</text>
</svg>
<figcaption>p stores x's address. Dereferencing p (<code>*p</code>) reaches x itself.</figcaption>
</div>

> [!KEY]
> The `*` symbol means two different things:
> - in a **declaration** (`int *p`), "p is a pointer"
> - in an **expression** (`*p = 5`), "dereference p"
>
> `int *p, q;` declares a pointer `p` and a plain int `q`: the `*` binds to the name, not the type. Declare one pointer per line.

## 3. The pointer's type matters

A pointer's type tells the compiler **what lives at the address**: how many bytes to read and how to interpret them, and how far `p + 1` moves (next lesson).

```c
double d = 3.5;
double *pd = &d;      /* correct */
/* int *pi = &d;      warning: incompatible pointer types: reading *pi would misinterpret the bytes */
printf("%zu\n", sizeof pd);   /* 8 on 64-bit: every pointer is an address-sized value */
```

## 4. NULL: the pointer to nothing

```c
int *p = NULL;             /* points nowhere; NULL is (void *)0 */
if (p != NULL) { *p = 1; } /* always check before dereferencing a pointer that may be NULL */
```

Dereferencing NULL is undefined behaviour, and on Linux a **segmentation fault**. Functions use NULL to signal "nothing" or "failure" (`malloc` returns NULL when out of memory, `strchr` when not found).

## 5. Pointer bugs: the big three

| Bug | Example | Result |
|---|---|---|
| **uninitialised (wild) pointer** | `int *p; *p = 5;` | writes to a random address: UB, crash or silent corruption |
| **NULL dereference** | `int *p = NULL; *p = 5;` | segfault |
| **dangling pointer** | `int *f(void) { int x; return &x; }` | points to dead memory: UB |

> [!DANGER]
> Initialise every pointer: to a valid address, or to `NULL`. After `free(p)`, set `p = NULL`. Compile with `-Wall -Wextra` and test with `-fsanitize=address`, which reports the exact line of a bad access.

## 6. Pointers as function parameters

This is why pointers matter first: C passes everything by value, so to let a function modify a caller's variable, pass its address:

```c
void read_pair(int *a, int *b) {        /* "output parameters" */
    scanf("%d %d", a, b);               /* a and b are already addresses: no & here */
}

int x, y;
read_pair(&x, &y);
```

That's exactly what `scanf` does, and it's why `scanf("%d", &x)` needs the `&`.

## 7. Printing and comparing pointers

- Print with `%p`, casting to `(void *)`.
- `p == q` asks "same address?". Ordering comparisons (`<`) are only meaningful between pointers into the same array.

## 8. Python's names vs C pointers

| | Python | C |
|---|---|---|
| `b = a` (objects) | both names refer to one object | copies the **value** (unless `a` is a pointer) |
| aliasing | implicit, everywhere | explicit: `int *p = &x;` |
| address visible | `id()`, opaque | `&x`, real memory |
| invalid reference | impossible (GC) | dangling, wild and NULL pointers are all possible |

## 9. Exam-ready answers

> [!EXAM]
> **Pointers.** A pointer is a variable that stores the memory address of another object. It is declared with an asterisk, for example `int *p;` declares a pointer to `int`. The address-of operator `&` yields the address of an object, and the indirection (dereference) operator `*` accesses the object a pointer points to, so after `p = &x;` the expression `*p` refers to `x`. A pointer's type determines how the pointed-to memory is interpreted and how pointer arithmetic scales. The null pointer (`NULL`) points to no object, and dereferencing it, an uninitialised pointer or a dangling pointer to an object whose lifetime has ended is undefined behaviour. Pointers enable call by reference, dynamic memory allocation, efficient array processing and linked data structures.

## 10. Cheat sheet

| Need | Code |
|---|---|
| declare | `int *p = NULL;` |
| point at x | `p = &x;` |
| read / write through it | `*p`, `*p = v;` |
| check | `if (p) ...` / `if (p != NULL)` |
| print | `printf("%p", (void *)p);` |
| modify the caller's variable | `void f(int *out)` called as `f(&x)` |

> [!INTERVIEW]
> **"What's the difference between `int *p = &x;` and `*p = x;`?"** The first declares `p` as a pointer and initialises it with the address of `x`, so `p` now points to `x`. The second (with `p` already declared) dereferences `p` and stores the *value* of `x` into whatever object `p` points to. If `p` is uninitialised, that's undefined behaviour. Same symbol, different roles in a declaration and in an expression.
