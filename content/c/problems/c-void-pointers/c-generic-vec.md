---
id: c-generic-vec
title: Generic Dynamic Array
difficulty: Hard
order: 1
tags: void pointers, realloc, generic programming, memcpy
---
## Statement
Implement a **type-generic** growable array:

```c
typedef struct { void *data; size_t elem, len, cap; } Vec;

void   vec_init(Vec *v, size_t elem_size);
int    vec_push(Vec *v, const void *item);        /* 0 ok, -1 out of memory; doubling growth */
void  *vec_at(Vec *v, size_t i);                  /* pointer to element i */
void   vec_remove(Vec *v, size_t i);              /* remove i, shifting later elements left */
void  *vec_max(Vec *v, int (*cmp)(const void *, const void *));   /* NULL if empty */
void   vec_free(Vec *v);
```

The driver uses one `Vec` of `int`s and one of `struct Point { double x, y; }`, so your code must not assume any element type.

## Starter
```c
#include <stdlib.h>
#include <string.h>

typedef struct { void *data; size_t elem, len, cap; } Vec;

void vec_init(Vec *v, size_t elem_size) { }
int vec_push(Vec *v, const void *item) { return -1; }
void *vec_at(Vec *v, size_t i) { return NULL; }
void vec_remove(Vec *v, size_t i) { }
void *vec_max(Vec *v, int (*cmp)(const void *, const void *)) { return NULL; }
void vec_free(Vec *v) { }
```

## Driver
```c
#include <stdio.h>
typedef struct { double x, y; } Point;
static int cmp_int(const void *a, const void *b) { int x = *(const int *)a, y = *(const int *)b; return (x > y) - (x < y); }
static int cmp_norm(const void *a, const void *b) {
    const Point *p = a, *q = b;
    double s = p->x * p->x + p->y * p->y, t = q->x * q->x + q->y * q->y;
    return (s > t) - (s < t);
}
int main(void) {
    Vec ints, pts;
    vec_init(&ints, sizeof(int));
    vec_init(&pts, sizeof(Point));
    int n; scanf("%d", &n);
    for (int i = 0; i < n; i++) { int x; scanf("%d", &x); vec_push(&ints, &x); }
    int m; scanf("%d", &m);
    for (int i = 0; i < m; i++) { Point p; scanf("%lf %lf", &p.x, &p.y); vec_push(&pts, &p); }
    int *mx = vec_max(&ints, cmp_int);
    printf("ints len=%zu cap>=len:%d max=%d\n", ints.len, ints.cap >= ints.len, mx ? *mx : -1);
    if (ints.len > 1) vec_remove(&ints, 1);
    for (size_t i = 0; i < ints.len; i++) printf("%d ", *(int *)vec_at(&ints, i));
    printf("\n");
    Point *far = vec_max(&pts, cmp_norm);
    if (far) printf("farthest=(%.1f, %.1f) of %zu\n", far->x, far->y, pts.len);
    else printf("no points\n");
    vec_free(&ints); vec_free(&pts);
    printf("freed: %d\n", ints.data == NULL && ints.len == 0);
    return 0;
}
```

## Tests
=== sample
5
3 9 2 9 1
3
1 1
-3 0
2 2
---
ints len=5 cap>=len:1 max=9
3 2 9 1 
farthest=(-3.0, 0.0) of 3
freed: 1
=== hidden
1
-5
0
---
ints len=1 cap>=len:1 max=-5
-5
no points
freed: 1

## Hints
- Address of element i: `(char *)v->data + i * v->elem`.
- `vec_push`: if `len == cap`, `realloc` to `cap ? cap * 2 : 4` elements, keeping the old pointer if realloc fails. Then `memcpy` the item in.
- `vec_remove`: `memmove` the tail one element left (the regions overlap, so `memcpy` would be wrong).
- `vec_max`: keep a pointer to the best element and call `cmp(cur, best) > 0` (strict, so the first maximum wins).

## Solution
```c
#include <stdlib.h>
#include <string.h>

typedef struct { void *data; size_t elem, len, cap; } Vec;

void vec_init(Vec *v, size_t elem_size) {
    v->data = NULL;
    v->elem = elem_size;
    v->len = v->cap = 0;
}

int vec_push(Vec *v, const void *item) {
    if (v->len == v->cap) {
        size_t ncap = v->cap ? v->cap * 2 : 4;
        void *p = realloc(v->data, ncap * v->elem);
        if (!p) return -1;
        v->data = p;
        v->cap = ncap;
    }
    memcpy((char *)v->data + v->len * v->elem, item, v->elem);
    v->len++;
    return 0;
}

void *vec_at(Vec *v, size_t i) {
    return (char *)v->data + i * v->elem;
}

void vec_remove(Vec *v, size_t i) {
    char *base = v->data;
    memmove(base + i * v->elem, base + (i + 1) * v->elem, (v->len - i - 1) * v->elem);
    v->len--;
}

void *vec_max(Vec *v, int (*cmp)(const void *, const void *)) {
    if (v->len == 0) return NULL;
    void *best = vec_at(v, 0);
    for (size_t i = 1; i < v->len; i++) {
        void *cur = vec_at(v, i);
        if (cmp(cur, best) > 0) best = cur;
    }
    return best;
}

void vec_free(Vec *v) {
    free(v->data);
    v->data = NULL;
    v->len = v->cap = 0;
}
```

`realloc` may move the block, so the result must be assigned only after checking it isn't NULL. Writing `v->data = realloc(v->data, ...)` directly leaks the old block on failure. Pointers returned by `vec_at` become invalid after a push that reallocates, which is exactly C++'s "iterator invalidation" rule for `std::vector`. This one struct is the core of `std::vector`, Python's list and Rust's `Vec`.
