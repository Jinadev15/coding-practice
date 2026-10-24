# Pointers to Pointers

A pointer is a variable, so it has an address too, and a pointer can point to it: `int **pp`. Double pointers appear in three essential situations: a **function that must change the caller's pointer** (allocate a buffer, insert at the head of a linked list), **arrays of strings** (`char **argv`), and **dynamically allocated 2D arrays** (arrays of row pointers). Each extra `*` is one more hop.

## 1. Two levels of indirection

```c
int x = 5;
int *p = &x;        /* p → x */
int **pp = &p;      /* pp → p → x */
**pp = 99;          /* follows two hops: writes x */
printf("%d %d %d\n", x, *p, **pp);   /* 99 99 99 */
```

<div class="figure">
<svg viewBox="0 0 580 110" width="580" xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace, monospace" font-size="13">
  <defs><marker id="ppa" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <rect x="20" y="40" width="120" height="40" fill="none" stroke="#a371f7" stroke-width="2"/><text x="40" y="65" fill="currentColor">&amp;p</text><text x="65" y="30" fill="#a371f7">pp</text>
  <rect x="230" y="40" width="120" height="40" fill="none" stroke="#2f81f7" stroke-width="2"/><text x="250" y="65" fill="currentColor">&amp;x</text><text x="282" y="30" fill="#2f81f7">p</text>
  <rect x="440" y="40" width="120" height="40" fill="none" stroke="#3fb950" stroke-width="2"/><text x="490" y="65" fill="currentColor">99</text><text x="492" y="30" fill="#3fb950">x</text>
  <line x1="142" y1="60" x2="226" y2="60" stroke="currentColor" marker-end="url(#ppa)"/><line x1="352" y1="60" x2="436" y2="60" stroke="currentColor" marker-end="url(#ppa)"/>
  <text x="160" y="100" fill="currentColor" font-size="11">*pp is p</text><text x="370" y="100" fill="currentColor" font-size="11">**pp is x</text>
</svg>
<figcaption>Each <code>*</code> follows one arrow.</figcaption>
</div>

## 2. Use 1: a function that changes the caller's pointer

Pass-by-value means a function gets a **copy** of a pointer. To change which address the caller's pointer holds, pass the pointer's address:

```c
#include <stdlib.h>

/* WRONG: assigns to a local copy; the caller's pointer stays NULL and the memory leaks */
void alloc_bad(int *p, size_t n) {
    p = malloc(n * sizeof *p);
}

/* RIGHT: receives the address of the caller's pointer */
int alloc_ints(int **out, size_t n) {
    *out = malloc(n * sizeof **out);
    return *out ? 0 : -1;
}

int *buf = NULL;
if (alloc_ints(&buf, 100) == 0) {     /* &buf has type int ** */
    buf[0] = 1;
    free(buf);
}
```

The same pattern inserts at the head of a linked list, where the head pointer itself changes:

```c
typedef struct Node { int val; struct Node *next; } Node;

void push_front(Node **head, int v) {
    Node *n = malloc(sizeof *n);
    n->val = v;
    n->next = *head;     /* old first node */
    *head = n;           /* caller's head now points to the new node */
}
```

> [!KEY]
> Rule: **to modify a `T` in a function, pass `T *`**. If `T` is itself `int *`, pass `int **`.

## 3. Use 2: arrays of strings and `argv`

```c
int main(int argc, char **argv) {          /* same as char *argv[] */
    for (int i = 0; i < argc; i++)
        printf("argv[%d] = %s\n", i, argv[i]);
    return 0;
}
```

`argv` points to an array of `char *`, each pointing to one argument string, and the array ends with `argv[argc] == NULL`. Walking it with a double pointer:

```c
for (char **a = argv; *a != NULL; a++)
    puts(*a);
```

## 4. Use 3: dynamic jagged 2D arrays

```c
int **make_grid(int rows, int cols) {
    int **g = malloc(rows * sizeof *g);            /* array of row pointers */
    if (!g) return NULL;
    for (int i = 0; i < rows; i++) {
        g[i] = calloc(cols, sizeof **g);           /* each row separately */
        if (!g[i]) {                               /* clean up on failure */
            while (i--) free(g[i]);
            free(g);
            return NULL;
        }
    }
    return g;
}

void free_grid(int **g, int rows) {
    for (int i = 0; i < rows; i++) free(g[i]);     /* rows first */
    free(g);                                       /* then the spine */
}
```

`g[i][j]` works (two dereferences), and rows may have different lengths. But it costs `rows + 1` allocations, the rows aren't contiguous (worse for cache), and freeing is more involved. For rectangular data, prefer the flat `malloc(rows * cols)` layout from the 2D Arrays lesson.

## 5. Common mistakes

> [!DANGER]
> - Passing `&array2d` where `int **` is expected: a true 2D array isn't an array of pointers.
> - Freeing the spine before the rows: the row pointers are then lost and the memory leaks.
> - Confusing levels: `*pp = malloc(...)` allocates for the caller, while `pp = malloc(...)` only changes the local parameter.

## 6. Exam-ready answers

> [!EXAM]
> **Pointer to pointer.** A pointer to a pointer stores the address of another pointer variable and is declared with two asterisks, e.g. `int **pp`. Dereferencing once (`*pp`) yields the pointed-to pointer, and twice (`**pp`) the final object. Double pointers are used to let a function modify a pointer belonging to its caller (for example allocating memory or updating the head of a linked list), to represent arrays of strings such as `char **argv`, and to build dynamically allocated two-dimensional arrays as arrays of row pointers.

## 7. Cheat sheet

| Need | Code |
|---|---|
| change the caller's pointer | `void f(T **out) { *out = ...; }` called as `f(&ptr)` |
| linked-list head insert | `push_front(Node **head, int v)` |
| program arguments | `int main(int argc, char **argv)` |
| jagged grid | `int **g` + per-row `malloc`; free the rows, then `g` |
| prefer for rectangles | flat `malloc(r * c)` |

> [!INTERVIEW]
> **"Why does `void init(char *s) { s = malloc(10); }` not work, and how do you fix it?"** `s` is a copy of the caller's pointer. Assigning to it changes only the copy, so the caller's pointer is unchanged and the allocated block leaks. Either return the pointer (`char *init(void)`) or take `char **s` and assign `*s = malloc(10)`, calling it as `init(&p)`.
