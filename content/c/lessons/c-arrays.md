# Arrays

A C array is a **fixed-size, contiguous block of elements of one type**. It's the most basic data structure there is: no length field, no bounds checking, no automatic growth. That gives you raw speed and cache-friendly memory, and it also gives you the buffer overflow, the most exploited bug in computing history. Python's `list` is built on top of exactly this (a C array of pointers, resized when full).

## 1. Declaring and initialising

> [!SYNTAX]
> ```c
> type name[SIZE];                     /* SIZE: a positive integer constant (or a VLA, see below) */
> type name[SIZE] = {v0, v1, ...};     /* missing elements are zero-initialised */
> type name[] = {v0, v1, v2};          /* size deduced: 3 */
> type name[SIZE] = {[i] = v};         /* designated initialiser (C99) */
> ```

```c
int scores[5];                       /* local: 5 indeterminate ints */
int zeros[100] = {0};                /* all 100 elements zero */
int a[5] = {1, 2};                   /* {1, 2, 0, 0, 0} */
int primes[] = {2, 3, 5, 7, 11};     /* size 5 */
int sparse[6] = {[2] = 7, [5] = 9};  /* {0, 0, 7, 0, 0, 9} */
```

> [!KEY]
> An uninitialised **local** array holds garbage. A global or `static` array is zeroed. `= {0}` zeroes every element of a local array.

## 2. Memory layout and indexing

```c
int a[4] = {10, 20, 30, 40};
```

<div class="figure">
<svg viewBox="0 0 560 130" width="560" xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace, monospace" font-size="13">
  <g fill="none" stroke="currentColor" stroke-opacity=".6"><rect x="60" y="40" width="90" height="40"/><rect x="150" y="40" width="90" height="40"/><rect x="240" y="40" width="90" height="40"/><rect x="330" y="40" width="90" height="40"/></g>
  <g fill="currentColor"><text x="92" y="65">10</text><text x="182" y="65">20</text><text x="272" y="65">30</text><text x="362" y="65">40</text></g>
  <g fill="#2f81f7" font-size="12"><text x="85" y="30">a[0]</text><text x="175" y="30">a[1]</text><text x="265" y="30">a[2]</text><text x="355" y="30">a[3]</text></g>
  <g fill="currentColor" fill-opacity=".7" font-size="11"><text x="62" y="98">0x1000</text><text x="152" y="98">0x1004</text><text x="242" y="98">0x1008</text><text x="332" y="98">0x100C</text></g>
  <rect x="420" y="40" width="90" height="40" fill="none" stroke="#f85149" stroke-dasharray="4 3"/><text x="430" y="65" fill="#f85149" font-size="11">a[4]: NOT yours</text>
</svg>
<figcaption>Elements are adjacent. The address of <code>a[i]</code> is <code>base + i × sizeof(int)</code>, which is why indexing is O(1).</figcaption>
</div>

Valid indices are `0` to `SIZE - 1`. **C doesn't check bounds**:

```c
int a[4];
a[4] = 99;     /* UNDEFINED BEHAVIOUR: writes past the end, maybe over another variable or a return address */
```

> [!DANGER]
> Out-of-bounds access is the root of buffer overflows. It might seem to work, corrupt another variable silently, crash later somewhere unrelated, or be exploited. Compile tests with `-fsanitize=address`, which reports `stack-buffer-overflow` at the exact line.

## 3. The length of an array

```c
int primes[] = {2, 3, 5, 7, 11};
size_t n = sizeof primes / sizeof primes[0];      /* 20 / 4 = 5 */
#define ARRAY_LEN(a) (sizeof(a) / sizeof((a)[0]))
```

This works **only where the array itself is visible**. Once passed to a function, it decays to a pointer (next section), and `sizeof` gives the pointer size.

## 4. Array decay

In almost every expression an array **decays to a pointer to its first element**: `a` becomes `&a[0]`. The exceptions are `sizeof a`, `&a`, and string literals initialising char arrays. Consequences:

```c
void zero(int *a, size_t n);      /* exactly equivalent to: void zero(int a[], size_t n); */
zero(primes, 5);                  /* passes &primes[0]: the function modifies the caller's array */

int b[5];
/* b = primes;      error: arrays aren't assignable */
memcpy(b, primes, sizeof b);      /* copy element bytes explicitly */
/* if (b == primes) compares ADDRESSES, not contents; use memcmp */
```

| You want | C |
|---|---|
| copy an array | `memcpy(dst, src, n * sizeof *src)` or a loop |
| compare contents | `memcmp(a, b, n * sizeof *a) == 0` or a loop |
| pass to a function | pass the pointer **and** the length |
| return from a function | you can't return an array: fill a caller-provided array, or return a struct wrapping it |

## 5. Variable-length arrays (VLAs)

C99 allows a size known only at run time: `int buf[n];`. It's allocated on the **stack**, so a big `n` overflows the stack with no error reporting, and VLAs became optional in C11. Use them only for small, bounded sizes. Otherwise allocate with `malloc` (Memory module).

## 6. Common array algorithms

```c
/* linear search */
int find(const int *a, size_t n, int key) {
    for (size_t i = 0; i < n; i++)
        if (a[i] == key) return (int)i;
    return -1;
}

/* insertion sort (fast for small n, stable) */
void insertion_sort(int *a, size_t n) {
    for (size_t i = 1; i < n; i++) {
        int key = a[i];
        size_t j = i;
        while (j > 0 && a[j - 1] > key) {
            a[j] = a[j - 1];
            j--;
        }
        a[j] = key;
    }
}

/* prefix sums: then sum of a[l..r] = pre[r+1] - pre[l] */
long long pre[101] = {0};
for (size_t i = 0; i < n; i++) pre[i + 1] = pre[i] + a[i];
```

## 7. Arrays vs Python lists

| | C array | Python list |
|---|---|---|
| size | fixed at creation | grows and shrinks |
| element types | one type, stored inline | references to any objects |
| bounds checked | **no** | yes (`IndexError`) |
| length stored | no | yes (`len` is O(1)) |
| memory | exactly `n × sizeof(T)` | ~8 bytes per pointer + the objects + spare capacity |
| cache friendliness | excellent (values adjacent) | poorer (pointer chasing) |

## 8. Exam-ready answers

> [!EXAM]
> **Arrays in C.** An array is a fixed-size collection of elements of the same type stored in contiguous memory locations, declared as `type name[size]`. Elements are accessed by zero-based index; `a[i]` is located at the base address plus `i * sizeof(type)`, giving constant-time access. C performs no bounds checking, so accessing outside `0 … size-1` is undefined behaviour. An initialiser list may be shorter than the array, in which case the remaining elements are zero. In most expressions an array name is converted to a pointer to its first element; therefore arrays cannot be assigned or compared directly, and when passed to a function only the address is passed, so the length must be passed separately.

## 9. Cheat sheet

| Need | Code |
|---|---|
| zero a local array | `int a[N] = {0};` |
| length in scope | `sizeof a / sizeof a[0]` |
| pass to a function | `f(a, n)` with `void f(int *a, size_t n)` |
| read-only parameter | `const int *a` |
| copy | `memcpy(dst, src, sizeof src)` |
| compare | `memcmp(a, b, sizeof a) == 0` |
| catch overflows | `gcc -g -fsanitize=address` |

> [!INTERVIEW]
> **"What's the difference between `a` and `&a` for `int a[10]`?"** Both have the same address value, but their types differ. `a` decays to `int *`, a pointer to the first element, so `a + 1` advances 4 bytes. `&a` is `int (*)[10]`, a pointer to the whole array, so `&a + 1` advances 40 bytes. `sizeof a` is 40 because the array doesn't decay inside `sizeof`.
