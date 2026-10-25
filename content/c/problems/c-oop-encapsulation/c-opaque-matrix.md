---
id: c-opaque-matrix
title: An Opaque Matrix Type (Multi-File)
difficulty: Medium
order: 1
tags: OOP in C, opaque types, encapsulation, error codes, ownership, multi-file
time_limit: 4
---
## Statement
Implement `matrix.c` behind the published header `matrix.h`, which declares an **opaque** `Mat`. The judge's `main.c` uses only the header and can't see your struct, so every interaction goes through your functions. Matrices are row-major `double`s.

| Function | Contract |
|---|---|
| `mat_create(rows, cols)` | Zero-filled. Returns NULL if either dimension is 0, if `rows * cols` overflows `size_t`, if the element count exceeds `MAT_MAX_ELEMS`, or if allocation fails. |
| `mat_identity(n)`, `mat_copy(m)` | New objects (NULL on failure, or for a NULL source). |
| `mat_destroy(m)` | Frees everything. Accepts NULL. |
| `mat_rows`, `mat_cols` | Dimensions (0 for NULL). |
| `mat_get(m, r, c, &out)`, `mat_set(m, r, c, v)` | `MAT_EINVAL` for a NULL pointer, `MAT_ERANGE` for out-of-range indices (`out` untouched), else `MAT_OK`. |
| `mat_mul(a, b, &err)` | A new matrix `a·b`. A NULL operand gives `MAT_EINVAL`, and `a.cols != b.rows` gives `MAT_EDIM` (return NULL). `err` may be NULL. On success, `*err = MAT_OK`. |
| `mat_transpose(m)` | A new matrix, or NULL. |
| `mat_add_inplace(a, b)` | `a += b`. `MAT_EINVAL` or `MAT_EDIM` leaves `a` unchanged. |
| `mat_equal(a, b, tol)` | 1 if the dimensions match and every element differs by at most `tol`, else 0 (also 0 if either is NULL). |
| `mat_strerror(s)` | `"ok"`, `"invalid argument"`, `"out of range"`, `"dimension mismatch"`, `"out of memory"`, or `"unknown"` for anything else. |

## Starter: matrix.h
```c
#ifndef MATRIX_H
#define MATRIX_H
#include <stddef.h>

#define MAT_MAX_ELEMS ((size_t)50000000)

typedef struct Mat Mat;
typedef enum { MAT_OK = 0, MAT_EINVAL, MAT_ERANGE, MAT_EDIM, MAT_ENOMEM } MatStatus;

Mat *mat_create(size_t rows, size_t cols);
Mat *mat_identity(size_t n);
Mat *mat_copy(const Mat *m);
void mat_destroy(Mat *m);
size_t mat_rows(const Mat *m);
size_t mat_cols(const Mat *m);
MatStatus mat_get(const Mat *m, size_t r, size_t c, double *out);
MatStatus mat_set(Mat *m, size_t r, size_t c, double v);
Mat *mat_mul(const Mat *a, const Mat *b, MatStatus *err);
Mat *mat_transpose(const Mat *m);
MatStatus mat_add_inplace(Mat *a, const Mat *b);
int mat_equal(const Mat *a, const Mat *b, double tol);
const char *mat_strerror(MatStatus s);
#endif
```

## Starter: matrix.c
```c
#include "matrix.h"
#include <stdlib.h>

struct Mat { size_t r, c; double *d; };

Mat *mat_create(size_t rows, size_t cols) {
    Mat *m = malloc(sizeof *m);
    m->r = rows; m->c = cols; m->d = calloc(rows * cols, sizeof(double));
    return m;
}
Mat *mat_identity(size_t n) { Mat *m = mat_create(n, n); for (size_t i = 0; i < n; i++) m->d[i * n + i] = 1; return m; }
Mat *mat_copy(const Mat *m) { return mat_create(m->r, m->c); }
void mat_destroy(Mat *m) { free(m); }
size_t mat_rows(const Mat *m) { return m->r; }
size_t mat_cols(const Mat *m) { return m->c; }
MatStatus mat_get(const Mat *m, size_t r, size_t c, double *out) { *out = m->d[r * m->c + c]; return MAT_OK; }
MatStatus mat_set(Mat *m, size_t r, size_t c, double v) { m->d[r * m->c + c] = v; return MAT_OK; }
Mat *mat_mul(const Mat *a, const Mat *b, MatStatus *err) { (void)a; (void)b; *err = MAT_OK; return NULL; }
Mat *mat_transpose(const Mat *m) { return mat_copy(m); }
MatStatus mat_add_inplace(Mat *a, const Mat *b) { for (size_t i = 0; i < a->r * a->c; i++) a->d[i] += b->d[i]; return MAT_OK; }
int mat_equal(const Mat *a, const Mat *b, double tol) { (void)tol; return a->r == b->r; }
const char *mat_strerror(MatStatus s) { (void)s; return "ok"; }
```

## Driver: main.c
```c
#include "matrix.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static void show(const char *label, const Mat *m) {
    printf("%s %zux%zu:", label, mat_rows(m), mat_cols(m));
    for (size_t r = 0; r < mat_rows(m); r++) {
        printf(" [");
        for (size_t c = 0; c < mat_cols(m); c++) { double v; mat_get(m, r, c, &v); printf("%s%g", c ? " " : "", v + 0.0); }
        printf("]");
    }
    printf("\n");
}

int main(void) {
    char cmd[32];
    while (scanf("%31s", cmd) == 1) {
        if (!strcmp(cmd, "basic")) {
            Mat *a = mat_create(2, 3);
            for (size_t i = 0; i < 6; i++) mat_set(a, i / 3, i % 3, (double)(i + 1));
            show("a", a);
            Mat *t = mat_transpose(a); show("t", t);
            MatStatus e = MAT_EINVAL;
            Mat *p = mat_mul(a, t, &e); show("a*t", p); printf("err=%s\n", mat_strerror(e));
            Mat *bad = mat_mul(a, a, &e); printf("a*a -> %s, %s\n", bad ? "matrix" : "NULL", mat_strerror(e));
            printf("null err ok: %s\n", mat_mul(a, a, NULL) ? "matrix" : "NULL");
            Mat *i3 = mat_identity(3), *q = mat_mul(a, i3, NULL);
            printf("a*I == a: %d, copy equal: %d\n", mat_equal(q, a, 0), mat_equal(mat_copy(a), a, 0) );
            double v = -1;
            MatStatus g1 = mat_get(a, 2, 0, &v), s1 = mat_set(a, 0, 3, 1), g2 = mat_get(NULL, 0, 0, &v);
            printf("get oob: %s v=%g, set oob: %s, null get: %s\n", mat_strerror(g1), v, mat_strerror(s1), mat_strerror(g2));
            printf("add dim: %s, add null: %s\n", mat_strerror(mat_add_inplace(a, t)), mat_strerror(mat_add_inplace(a, NULL)));
            show("a unchanged", a);
            Mat *c = mat_copy(a); mat_set(c, 0, 0, 100); mat_add_inplace(a, c); show("a+=c", a); show("c", c);
            printf("equal tol: %d %d\n", mat_equal(a, a, 0), mat_equal(c, a, 1e9) );
            printf("strerror: %s|%s|%s|%s\n", mat_strerror(MAT_ERANGE), mat_strerror(MAT_EDIM), mat_strerror(MAT_ENOMEM), mat_strerror((MatStatus)42));
            mat_destroy(a); mat_destroy(t); mat_destroy(p); mat_destroy(i3); mat_destroy(q); mat_destroy(c); mat_destroy(NULL);
        } else if (!strcmp(cmd, "limits")) {
            printf("0x3: %s, 3x0: %s\n", mat_create(0, 3) ? "matrix" : "NULL", mat_create(3, 0) ? "matrix" : "NULL");
            printf("overflow: %s\n", mat_create(SIZE_MAX / 2, 4) ? "matrix" : "NULL");
            printf("too big: %s\n", mat_create(10000, 10000) ? "matrix" : "NULL");
            Mat *ok = mat_create(5000, 10000); printf("max ok: %s\n", ok ? "matrix" : "NULL"); mat_destroy(ok);
            printf("null dims: %zu %zu, null copy: %s, null transpose: %s, eq null: %d\n", mat_rows(NULL), mat_cols(NULL),
                   mat_copy(NULL) ? "?" : "NULL", mat_transpose(NULL) ? "?" : "NULL", mat_equal(NULL, NULL, 1));
            MatStatus e = MAT_OK; Mat *mn = mat_mul(NULL, NULL, &e); printf("mul null: %s %s\n", mn ? "?" : "NULL", mat_strerror(e));
            printf("identity(0): %s\n", mat_identity(0) ? "?" : "NULL");
        } else if (!strcmp(cmd, "big")) {
            size_t n = 300; unsigned x = 7;
            Mat *a = mat_create(n, n), *b = mat_create(n, n);
            for (size_t r = 0; r < n; r++) for (size_t c = 0; c < n; c++) {
                x = x * 1103515245u + 12345u; mat_set(a, r, c, (double)(x >> 16 & 1023) / 512.0 - 1.0);
                x = x * 1103515245u + 12345u; mat_set(b, r, c, (double)(x >> 16 & 1023) / 512.0 - 1.0);
            }
            Mat *ab = mat_mul(a, b, NULL), *bt = mat_transpose(b), *at = mat_transpose(a);
            Mat *btat = mat_mul(bt, at, NULL), *abt = mat_transpose(ab);
            printf("(AB)^T == B^T A^T: %d\n", mat_equal(abt, btat, 1e-9));
            double tr = 0, v; for (size_t i = 0; i < n; i++) { mat_get(ab, i, i, &v); tr += v; }
            printf("trace %.6f\n", tr);
            mat_destroy(a); mat_destroy(b); mat_destroy(ab); mat_destroy(bt); mat_destroy(at); mat_destroy(btat); mat_destroy(abt);
        }
    }
    return 0;
}
```

## Tests
=== sample
basic
---
a 2x3: [1 2 3] [4 5 6]
t 3x2: [1 4] [2 5] [3 6]
a*t 2x2: [14 32] [32 77]
err=ok
a*a -> NULL, dimension mismatch
null err ok: NULL
a*I == a: 1, copy equal: 1
get oob: out of range v=-1, set oob: out of range, null get: invalid argument
add dim: dimension mismatch, add null: invalid argument
a unchanged 2x3: [1 2 3] [4 5 6]
a+=c 2x3: [101 4 6] [8 10 12]
c 2x3: [100 2 3] [4 5 6]
equal tol: 1 1
strerror: out of range|dimension mismatch|out of memory|unknown
=== hidden
limits
---
0x3: NULL, 3x0: NULL
overflow: NULL
too big: NULL
max ok: matrix
null dims: 0 0, null copy: NULL, null transpose: NULL, eq null: 0
mul null: NULL invalid argument
identity(0): NULL
=== hidden
big
---
(AB)^T == B^T A^T: 1
trace -56.510078

## Hints
- Validate at the boundary: every public function checks for NULL and for ranges before touching memory.
- Overflow check: `if (cols > SIZE_MAX / rows)` before multiplying, then compare with `MAT_MAX_ELEMS`.
- Allocate the header and the data separately, and free both (and the header if the data allocation fails).
- `mat_mul`: loop order i, k, j (`out[i][j] += a[i][k] * b[k][j]`) walks memory sequentially and is much faster than i, j, k on large matrices.

## Solution: matrix.h
```c
#ifndef MATRIX_H
#define MATRIX_H
#include <stddef.h>

#define MAT_MAX_ELEMS ((size_t)50000000)

typedef struct Mat Mat;
typedef enum { MAT_OK = 0, MAT_EINVAL, MAT_ERANGE, MAT_EDIM, MAT_ENOMEM } MatStatus;

Mat *mat_create(size_t rows, size_t cols);
Mat *mat_identity(size_t n);
Mat *mat_copy(const Mat *m);
void mat_destroy(Mat *m);
size_t mat_rows(const Mat *m);
size_t mat_cols(const Mat *m);
MatStatus mat_get(const Mat *m, size_t r, size_t c, double *out);
MatStatus mat_set(Mat *m, size_t r, size_t c, double v);
Mat *mat_mul(const Mat *a, const Mat *b, MatStatus *err);
Mat *mat_transpose(const Mat *m);
MatStatus mat_add_inplace(Mat *a, const Mat *b);
int mat_equal(const Mat *a, const Mat *b, double tol);
const char *mat_strerror(MatStatus s);
#endif
```

## Solution: matrix.c
```c
#include "matrix.h"
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

struct Mat {
    size_t rows, cols;
    double *data;                 /* row-major, rows * cols elements */
};

static double *at(const Mat *m, size_t r, size_t c) { return &m->data[r * m->cols + c]; }

Mat *mat_create(size_t rows, size_t cols) {
    if (rows == 0 || cols == 0 || cols > SIZE_MAX / rows || rows * cols > MAT_MAX_ELEMS) return NULL;
    Mat *m = malloc(sizeof *m);
    if (!m) return NULL;
    m->data = calloc(rows * cols, sizeof(double));
    if (!m->data) { free(m); return NULL; }
    m->rows = rows;
    m->cols = cols;
    return m;
}

Mat *mat_identity(size_t n) {
    Mat *m = mat_create(n, n);
    if (m) for (size_t i = 0; i < n; i++) *at(m, i, i) = 1.0;
    return m;
}

Mat *mat_copy(const Mat *src) {
    if (!src) return NULL;
    Mat *m = mat_create(src->rows, src->cols);
    if (m) memcpy(m->data, src->data, src->rows * src->cols * sizeof(double));
    return m;
}

void mat_destroy(Mat *m) {
    if (!m) return;
    free(m->data);
    free(m);
}

size_t mat_rows(const Mat *m) { return m ? m->rows : 0; }
size_t mat_cols(const Mat *m) { return m ? m->cols : 0; }

MatStatus mat_get(const Mat *m, size_t r, size_t c, double *out) {
    if (!m || !out) return MAT_EINVAL;
    if (r >= m->rows || c >= m->cols) return MAT_ERANGE;
    *out = *at(m, r, c);
    return MAT_OK;
}

MatStatus mat_set(Mat *m, size_t r, size_t c, double v) {
    if (!m) return MAT_EINVAL;
    if (r >= m->rows || c >= m->cols) return MAT_ERANGE;
    *at(m, r, c) = v;
    return MAT_OK;
}

Mat *mat_mul(const Mat *a, const Mat *b, MatStatus *err) {
    MatStatus st = MAT_OK;
    Mat *out = NULL;
    if (!a || !b) st = MAT_EINVAL;
    else if (a->cols != b->rows) st = MAT_EDIM;
    else if (!(out = mat_create(a->rows, b->cols))) st = MAT_ENOMEM;
    else {
        for (size_t i = 0; i < a->rows; i++)
            for (size_t k = 0; k < a->cols; k++) {          /* i-k-j: sequential access to b and out */
                const double aik = *at(a, i, k);
                const double *brow = at(b, k, 0);
                double *orow = at(out, i, 0);
                for (size_t j = 0; j < b->cols; j++) orow[j] += aik * brow[j];
            }
    }
    if (err) *err = st;
    return out;
}

Mat *mat_transpose(const Mat *m) {
    if (!m) return NULL;
    Mat *t = mat_create(m->cols, m->rows);
    if (t)
        for (size_t r = 0; r < m->rows; r++)
            for (size_t c = 0; c < m->cols; c++) *at(t, c, r) = *at(m, r, c);
    return t;
}

MatStatus mat_add_inplace(Mat *a, const Mat *b) {
    if (!a || !b) return MAT_EINVAL;
    if (a->rows != b->rows || a->cols != b->cols) return MAT_EDIM;
    const size_t n = a->rows * a->cols;
    for (size_t i = 0; i < n; i++) a->data[i] += b->data[i];
    return MAT_OK;
}

int mat_equal(const Mat *a, const Mat *b, double tol) {
    if (!a || !b || a->rows != b->rows || a->cols != b->cols) return 0;
    const size_t n = a->rows * a->cols;
    for (size_t i = 0; i < n; i++)
        if (!(fabs(a->data[i] - b->data[i]) <= tol)) return 0;
    return 1;
}

const char *mat_strerror(MatStatus s) {
    switch (s) {
    case MAT_OK: return "ok";
    case MAT_EINVAL: return "invalid argument";
    case MAT_ERANGE: return "out of range";
    case MAT_EDIM: return "dimension mismatch";
    case MAT_ENOMEM: return "out of memory";
    default: return "unknown";
    }
}
```

## Solution
- **The opaque type** means the judge's `main.c` *cannot* reach `data` or `rows`. Every access goes through functions that validate, so a bad index returns `MAT_ERANGE` instead of corrupting the heap.
- **Construction is all-or-nothing**: dimensions and the overflow check come first (`cols > SIZE_MAX / rows`), and a failed data allocation frees the header. A caller never gets a half-built object.
- **Ownership is explicit**: every `Mat *` returned by `create`, `copy`, `mul`, `transpose` or `identity` belongs to the caller, who must call `mat_destroy`, which accepts NULL so cleanup code stays simple.
- **Errors are values**: status enums plus `mat_strerror` give exception-free, testable error reporting. `mat_mul`'s optional `err` out-parameter returns both an object and a reason.
- **Performance stays an implementation detail**: switching the multiply loop to i-k-j order (or to blocked or BLAS calls) changed nothing for clients. That's the payoff of encapsulation.
