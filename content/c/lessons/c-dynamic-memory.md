# Dynamic Memory: malloc, calloc, realloc, free

Stack variables have sizes fixed at compile time and die when their function returns. Real programs need memory whose **size is known only at run time** (a file of unknown length, a point cloud from a LIDAR scan) or whose **lifetime outlives the function** that created it (a linked-list node, a parsed configuration). C gives you the **heap** through four functions in `<stdlib.h>`. There's no garbage collector and no destructor: **every allocation is your responsibility until you `free` it**. This lesson covers the API precisely, the idioms professionals use, and the ownership discipline that keeps large C programs leak-free.

## 1. The four functions

> [!SYNTAX]
> ```c
> void *malloc(size_t size);                  // size bytes, UNINITIALISED; NULL on failure
> void *calloc(size_t count, size_t size);    // count*size bytes, all ZERO; overflow-checked
> void *realloc(void *ptr, size_t new_size);  // resize (may move!); NULL on failure, old block intact
> void  free(void *ptr);                      // release; free(NULL) is a no-op
> ```

```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    size_t n;
    if (scanf("%zu", &n) != 1) return 1;
    int *a = malloc(n * sizeof *a);          // sizeof *a: correct even if a's type changes
    if (a == NULL) {                         // ALWAYS check
        perror("malloc");
        return 1;
    }
    for (size_t i = 0; i < n; i++) a[i] = (int)(i * i);
    printf("%d\n", a[n - 1]);
    free(a);                                 // give it back
    a = NULL;                                // defensive: a dangling pointer can't be reused by accident
    return 0;
}
```

> [!KEY]
> - Write `p = malloc(n * sizeof *p)`, not `malloc(n * sizeof(int))`. The size follows the pointer's type automatically.
> - **Don't cast** the result in C (`(int *)malloc(...)`). `void *` converts implicitly, and the cast can hide a missing `#include <stdlib.h>` in old C. (C++ *requires* the cast, but in C++ you shouldn't use `malloc` at all.)
> - `malloc` returns memory suitably aligned for **any** built-in type (`alignof(max_align_t)`, 16 bytes on x86-64).

## 2. `malloc` vs `calloc`

| | `malloc(n * size)` | `calloc(n, size)` |
|---|---|---|
| Contents | indeterminate garbage | all bits zero |
| Overflow of `n * size` | **silently wraps** → tiny block → heap overflow | detected → returns NULL |
| Speed | fastest | may be just as fast for big blocks (fresh pages from the OS are already zero) |

> [!DANGER]
> `malloc(count * sizeof(T))` with an attacker-controlled `count` can overflow `size_t` and allocate far less than intended. That's a classic exploitable bug class. Use `calloc(count, sizeof(T))`, or check `count > SIZE_MAX / sizeof(T)` first.

## 3. `realloc`: growing and shrinking

`realloc(p, new_size)` returns a pointer to a block of `new_size` bytes whose first `min(old, new)` bytes equal the old contents. It may extend in place **or allocate a new block, copy, and free the old one**. After a successful call, the old pointer is invalid.

```c
// WRONG: if realloc fails it returns NULL, and the only pointer to the old block is lost (a leak)
buf = realloc(buf, new_cap);

// RIGHT: use a temporary
int *tmp = realloc(buf, new_cap * sizeof *buf);
if (tmp == NULL) {
    free(buf);            // or keep using the old buffer, it's still valid
    return -1;
}
buf = tmp;
```

Special cases: `realloc(NULL, n)` behaves like `malloc(n)`. `realloc(p, 0)` is implementation-defined (and declared obsolescent in C23), so don't use it to free.

### The growable array (amortised O(1) append)

```c
typedef struct {
    int *data;
    size_t len, cap;
} IntVec;

int vec_push(IntVec *v, int x) {
    if (v->len == v->cap) {
        size_t new_cap = v->cap ? v->cap * 2 : 8;           // GEOMETRIC growth
        int *tmp = realloc(v->data, new_cap * sizeof *tmp);
        if (!tmp) return -1;
        v->data = tmp;
        v->cap = new_cap;
    }
    v->data[v->len++] = x;
    return 0;
}
```

> [!KEY]
> Grow by a **factor** (×2, or ×1.5), never by a constant (+10). With doubling, n pushes copy at most 1 + 2 + 4 + … + n < 2n elements in total: **amortised O(1)** per push. Growing by a constant makes n pushes cost O(n²). This is exactly how `std::vector` and Python's `list` work.

## 4. `free` rules

1. Free **exactly once** every pointer returned by `malloc`/`calloc`/`realloc`.
2. Pass `free` **the same pointer** you got, not `p + 1`. Pointers into the middle of a block or to stack memory are UB.
3. After `free(p)`, **never** read, write or free `p` again (use-after-free and double free are both UB, and exploitable).
4. `free(NULL)` is safe. That makes cleanup code simpler.

## 5. Ownership: who frees?

C has no destructors, so every API must **document who owns each pointer**:

| Pattern | Who frees | Example |
|---|---|---|
| function returns newly allocated memory | the **caller** | `strdup`, `getline`, `my_parse_file()` |
| caller provides the buffer | the caller (often on the stack) | `snprintf(buf, sizeof buf, ...)`, `fgets` |
| constructor/destructor pair | call the matching `_free`/`_destroy` | `vec_new()`/`vec_free()`, `fopen`/`fclose` |
| borrowed pointer | nobody: you mustn't free it | `getenv()`, `strerror()` results |

```c
char *read_line_copy(FILE *f) {             // "returns a malloc'd string; caller must free()"
    char buf[256];
    if (!fgets(buf, sizeof buf, f)) return NULL;
    size_t n = strlen(buf);
    char *s = malloc(n + 1);                // +1 for '\0'
    if (s) memcpy(s, buf, n + 1);
    return s;
}
```

### Structs that own memory: the constructor/destructor convention

```c
typedef struct { char *name; double *samples; size_t n; } Sensor;

Sensor *sensor_new(const char *name, size_t n) {
    Sensor *s = malloc(sizeof *s);
    if (!s) return NULL;
    s->name = malloc(strlen(name) + 1);
    s->samples = calloc(n, sizeof *s->samples);
    if (!s->name || !s->samples) {          // partial failure: undo everything
        free(s->name);
        free(s->samples);
        free(s);
        return NULL;
    }
    strcpy(s->name, name);
    s->n = n;
    return s;
}

void sensor_free(Sensor *s) {
    if (!s) return;                          // like free(NULL)
    free(s->name);                           // inner allocations first
    free(s->samples);
    free(s);                                 // then the struct itself
}
```

That's RAII written by hand. The Master OOP in C module builds whole designs on this convention.

## 6. Heap vs stack

| | Stack (automatic) | Heap (dynamic) |
|---|---|---|
| Allocate / free | automatic, at block entry and exit | manual: `malloc` / `free` |
| Speed | ~free (move the stack pointer) | allocator bookkeeping, possibly a syscall |
| Size limit | small (8 MB by default on Linux: `ulimit -s`) | up to available RAM |
| Lifetime | until the function returns | until `free` |
| Failure mode | stack overflow → crash (SIGSEGV) | `malloc` returns NULL |

> [!WARNING]
> Never return a pointer to a local variable: `int *f(void) { int x = 5; return &x; }` gives the caller a dangling pointer to a dead stack frame. Return by value, use a caller-supplied buffer, or allocate on the heap.

Variable-length arrays (`int a[n];`) put run-time-sized arrays on the stack. A large `n` silently overflows the stack. They're optional since C11, and banned in many style guides (Linux kernel, MISRA). Use `malloc` for anything sized by input.

## 7. Exam-ready answers

> [!EXAM]
> **Dynamic memory allocation in C.** C provides dynamic allocation on the heap through `<stdlib.h>`: `malloc(size)` allocates an uninitialised block of `size` bytes; `calloc(n, size)` allocates zero-initialised storage for `n` objects of `size` bytes, checking the multiplication for overflow; `realloc(ptr, size)` changes the size of a block, possibly moving it and copying its contents, and returns NULL on failure while leaving the original block valid; and `free(ptr)` releases a block (freeing a null pointer has no effect). The allocation functions return `void *` suitably aligned for any object type, or NULL on failure, which must always be checked. Dynamically allocated memory persists until explicitly freed; failing to free it causes memory leaks, while using it after freeing or freeing it twice is undefined behaviour.

> [!EXAM]
> **`malloc` vs `calloc`.** `malloc` takes a single byte count and leaves the memory uninitialised, while `calloc` takes an element count and an element size, guards against overflow of their product, and initialises all bytes to zero.

## 8. Cheat sheet

| Need | Code |
|---|---|
| array of n | `T *a = malloc(n * sizeof *a); if (!a) ...` |
| zeroed array, overflow-safe | `T *a = calloc(n, sizeof *a);` |
| grow safely | `tmp = realloc(a, m * sizeof *a); if (tmp) a = tmp;` |
| release | `free(a); a = NULL;` |
| string copy | `char *s = malloc(strlen(src) + 1); strcpy(s, src);` (or POSIX/C23 `strdup`) |
| amortised append | double the capacity when full |
| owning struct | `x_new()` checks every allocation; `x_free()` frees inner → outer |

> [!INTERVIEW]
> **"What's wrong with `p = realloc(p, n);`?"** If `realloc` fails it returns NULL but **doesn't free** the original block. Assigning straight to `p` overwrites the only pointer to that block, which leaks it, and the program then continues with `p == NULL`. Always assign to a temporary, check it, then commit. Follow-up: realloc may **move** the block, so any other pointers into the old block are dangling afterwards. That's the same reason `std::vector` invalidates iterators on reallocation.
