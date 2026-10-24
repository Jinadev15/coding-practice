# Pointer Arithmetic

Adding an integer to a pointer moves it by **whole elements**, not bytes. That rule is what makes arrays, strings and buffers work in C: `p + 1` is "the next int" or "the next char". It's also the foundation of fast string and buffer code (walking with a pointer instead of an index), and of the pointer-difference trick for lengths. And it's precisely bounded: arithmetic outside an array is undefined behaviour.

## 1. The scaling rule

> [!KEY]
> If `p` has type `T *`, then `p + n` points `n × sizeof(T)` **bytes** further on, which is the n-th element after `*p`.

```c
int a[5] = {10, 20, 30, 40, 50};
int *p = a;                 /* &a[0] */
printf("%d\n", *(p + 2));   /* 30 */
double d[3];
printf("%td\n", (char *)(d + 1) - (char *)d);   /* 8: one double is 8 bytes */
```

<div class="figure">
<svg viewBox="0 0 560 120" width="560" xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace, monospace" font-size="13">
  <g fill="none" stroke="currentColor" stroke-opacity=".6"><rect x="40" y="40" width="90" height="40"/><rect x="130" y="40" width="90" height="40"/><rect x="220" y="40" width="90" height="40"/><rect x="310" y="40" width="90" height="40"/><rect x="400" y="40" width="90" height="40"/></g>
  <g fill="currentColor"><text x="72" y="65">10</text><text x="162" y="65">20</text><text x="252" y="65">30</text><text x="342" y="65">40</text><text x="432" y="65">50</text></g>
  <g fill="#2f81f7" font-size="12"><text x="65" y="30">p</text><text x="150" y="30">p+1</text><text x="240" y="30">p+2</text><text x="330" y="30">p+3</text><text x="420" y="30">p+4</text><text x="495" y="30">p+5 ✓(end)</text></g>
  <g fill="currentColor" fill-opacity=".7" font-size="11"><text x="45" y="100">+0 B</text><text x="135" y="100">+4 B</text><text x="225" y="100">+8 B</text><text x="315" y="100">+12 B</text><text x="405" y="100">+16 B</text></g>
</svg>
<figcaption>Each step of <code>p + 1</code> advances 4 bytes for an <code>int *</code>. A pointer one past the end (<code>p + 5</code>) may be formed and compared, but never dereferenced.</figcaption>
</div>

## 2. The allowed operations

| Operation | Meaning | Result type |
|---|---|---|
| `p + n`, `p - n`, `p++`, `p--`, `p += n` | move by n elements | `T *` |
| `q - p` | number of elements between them (same array) | `ptrdiff_t` (`%td`) |
| `p < q`, `p == q` | position comparison (same array) | `int` |
| `p + q`, `p * 2`, `p / q` | **not allowed** (compile error) | |

```c
int *begin = a, *end = a + 5;       /* end = "one past the last" */
for (int *it = begin; it != end; it++)
    printf("%d ", *it);             /* 10 20 30 40 50 */
printf("%td\n", end - begin);       /* 5 */
```

This begin/end ("half-open range") style is exactly what C++ iterators formalise.

## 3. Rules that keep it defined

> [!DANGER]
> Pointer arithmetic is only defined **within one array object, or one past its end**:
> - `a + 6` for a 5-element array is UB even if you never dereference it.
> - Dereferencing `a + 5` (one past the end) is UB.
> - Subtracting or comparing pointers into **different** arrays is UB.
> - Arithmetic on `void *` isn't standard C (gcc allows it as an extension, treating the size as 1).

## 4. `*p++` and friends: precedence

Postfix `++` binds tighter than unary `*`:

| Expression | Means | Effect |
|---|---|---|
| `*p++` | `*(p++)` | read `*p`, then advance `p` |
| `(*p)++` | | increment the pointed-to value |
| `*++p` | `*(++p)` | advance `p`, then read |
| `++*p` | `++(*p)` | increment the value |

The classic idioms built on `*p++`:

```c
size_t my_strlen(const char *s) {
    const char *p = s;
    while (*p) p++;
    return (size_t)(p - s);            /* pointer difference = count */
}

void my_strcpy(char *dst, const char *src) {
    while ((*dst++ = *src++) != '\0')  /* copy each char, including the '\0', then stop */
        ;
}
```

## 5. Index vs pointer style

```c
long long sum_index(const int *a, size_t n) {
    long long s = 0;
    for (size_t i = 0; i < n; i++) s += a[i];
    return s;
}

long long sum_pointer(const int *a, size_t n) {
    long long s = 0;
    for (const int *p = a, *end = a + n; p < end; p++) s += *p;
    return s;
}
```

With optimisation on, both compile to essentially the same machine code. Use whichever is clearer: indices usually read better for arrays, and pointers for scanning strings and buffers.

## 6. Exam-ready answers

> [!EXAM]
> **Pointer arithmetic.** Adding an integer n to a pointer of type `T *` produces a pointer to the element n positions further, that is, the address advanced by `n * sizeof(T)` bytes; subtraction moves backwards. Subtracting two pointers into the same array yields the number of elements between them, as a value of type `ptrdiff_t`. Pointers into the same array can be compared with relational operators. Arithmetic is defined only for pointers into an array object or one past its last element; forming any other pointer, or dereferencing the one-past-the-end pointer, is undefined behaviour. Pointers cannot be added, multiplied or divided.

## 7. Cheat sheet

| Need | Code |
|---|---|
| element i | `*(p + i)` ≡ `p[i]` |
| walk an array | `for (T *it = a; it != a + n; it++)` |
| length from pointers | `end - begin` (`%td`) |
| read and advance | `*p++` |
| increment the value | `(*p)++` |
| walk a string | `while (*s) { ...; s++; }` |

> [!INTERVIEW]
> **"Given `int a[5]; int *p = a + 2;`, what are `p[-1]` and `p - a`?"** `p[-1]` is `*(p - 1)`, which is `a[1]` (legal, since it's still inside the array). `p - a` is `2` (a `ptrdiff_t`), the number of elements between them, not 8 bytes. Negative subscripts are fine as long as the result stays inside the array.
