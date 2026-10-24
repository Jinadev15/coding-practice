---
id: c-vector-module
title: A Multi-File Vector Module
difficulty: Medium
order: 1
tags: headers, include guards, static, separate compilation
---
## Statement
Split a 2D-geometry module across files (the tabs are already created):

- `vec.h`: include guard; `typedef struct { double x, y; } Vec2;` and the prototypes below
- `vec.c`: the definitions, plus a **private** `static` helper `sq`
- `main.c`: provided. Reads commands and calls the module.

Functions:

| Function | Returns |
|---|---|
| `Vec2 vec_make(double x, double y)` | the vector |
| `Vec2 vec_add(Vec2 a, Vec2 b)` | a + b |
| `Vec2 vec_scale(Vec2 v, double k)` | k·v |
| `double vec_dot(Vec2 a, Vec2 b)` | the dot product |
| `double vec_length(Vec2 v)` | √(x² + y²), using `sq` |
| `Vec2 vec_normalize(Vec2 v)` | v / ‖v‖, or (0, 0) if the length is 0 |

`main.c` also includes `vec.h` twice (indirectly, through `util.h`) to check your include guard.

## Starter: main.c
```c
#include <stdio.h>
#include "vec.h"
#include "util.h"

int main(void) {
    double ax, ay, bx, by, k;
    while (scanf("%lf %lf %lf %lf %lf", &ax, &ay, &bx, &by, &k) == 5) {
        Vec2 a = vec_make(ax, ay), b = vec_make(bx, by);
        Vec2 s = vec_add(a, vec_scale(b, k));
        Vec2 n = vec_normalize(s);
        print_vec("s", s);
        printf("dot=%.2f len=%.3f ", vec_dot(a, b), vec_length(s));
        print_vec("n", n);
    }
    return 0;
}
```

## Starter: util.h
```c
#ifndef UTIL_H
#define UTIL_H
#include <stdio.h>
#include "vec.h"

static inline void print_vec(const char *name, Vec2 v) {
    printf("%s=(%.3f, %.3f)\n", name, v.x, v.y);
}

#endif
```

## Starter: vec.h
```c
/* add an include guard, the Vec2 type and the prototypes */
```

## Starter: vec.c
```c
#include "vec.h"
#include <math.h>
```

## Tests
=== sample
3 0 0 4 1
---
s=(3.000, 4.000)
dot=0.00 len=5.000 n=(0.600, 0.800)
=== hidden
1 1 1 1 -1
2 0 1 0 2
---
s=(0.000, 0.000)
dot=2.00 len=0.000 n=(0.000, 0.000)
s=(4.000, 0.000)
dot=2.00 len=4.000 n=(1.000, 0.000)

## Solution
The header declares the type and the interface. The implementation defines the functions and keeps `sq` private with `static`. The include guard makes the double inclusion through `util.h` harmless.

## Solution: vec.h
```c
#ifndef VEC_H
#define VEC_H

typedef struct {
    double x, y;
} Vec2;

Vec2 vec_make(double x, double y);
Vec2 vec_add(Vec2 a, Vec2 b);
Vec2 vec_scale(Vec2 v, double k);
double vec_dot(Vec2 a, Vec2 b);
double vec_length(Vec2 v);
Vec2 vec_normalize(Vec2 v);

#endif
```

## Solution: vec.c
```c
#include "vec.h"
#include <math.h>

static double sq(double v) {
    return v * v;
}

Vec2 vec_make(double x, double y) {
    Vec2 v = {x, y};
    return v;
}

Vec2 vec_add(Vec2 a, Vec2 b) {
    return vec_make(a.x + b.x, a.y + b.y);
}

Vec2 vec_scale(Vec2 v, double k) {
    return vec_make(v.x * k, v.y * k);
}

double vec_dot(Vec2 a, Vec2 b) {
    return a.x * b.x + a.y * b.y;
}

double vec_length(Vec2 v) {
    return sqrt(sq(v.x) + sq(v.y));
}

Vec2 vec_normalize(Vec2 v) {
    double len = vec_length(v);
    if (len == 0.0) return vec_make(0.0, 0.0);
    return vec_scale(v, 1.0 / len);
}
```

## Solution: main.c
```c
#include <stdio.h>
#include "vec.h"
#include "util.h"

int main(void) {
    double ax, ay, bx, by, k;
    while (scanf("%lf %lf %lf %lf %lf", &ax, &ay, &bx, &by, &k) == 5) {
        Vec2 a = vec_make(ax, ay), b = vec_make(bx, by);
        Vec2 s = vec_add(a, vec_scale(b, k));
        Vec2 n = vec_normalize(s);
        print_vec("s", s);
        printf("dot=%.2f len=%.3f ", vec_dot(a, b), vec_length(s));
        print_vec("n", n);
    }
    return 0;
}
```

## Solution: util.h
```c
#ifndef UTIL_H
#define UTIL_H
#include <stdio.h>
#include "vec.h"

static inline void print_vec(const char *name, Vec2 v) {
    printf("%s=(%.3f, %.3f)\n", name, v.x, v.y);
}

#endif
```
