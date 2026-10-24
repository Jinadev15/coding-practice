---
id: c-fleet-report
title: Robot Fleet Report
difficulty: Medium
order: 1
tags: structs, nested structs, arrays of structs, qsort, pointers to structs
---
## Statement
Model a robot fleet with structs:

```c
typedef struct { double x, y; } Vec2;
typedef struct {
    char name[16];
    Vec2 pos;
    double battery;      /* 0..100 */
    int trips;
} Robot;
```

Input: `n`, then `n` lines `NAME X Y BATTERY`. Then a list of commands until the end of input:
- `move NAME DX DY`: move the robot by (dx, dy). It costs `distance * 2` battery (clamped at 0) and counts one trip. If the robot's battery is already 0, print `NAME stuck` and don't move it.
- `charge NAME AMOUNT`: add battery (clamped at 100).

Write the update logic as functions taking `Robot *` (and a lookup function returning `Robot *` or `NULL`; unknown names print `unknown NAME`). Then print the report: robots sorted by **distance from the origin ascending**, ties broken by name, as

```
NAME (X, Y) dist=D battery=B trips=T
```

with X, Y, D and B printed with 2 decimals. Finally print `fleet_battery=AVG` (2 decimals) and `farthest=NAME`.

## Starter
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct { double x, y; } Vec2;
typedef struct {
    char name[16];
    Vec2 pos;
    double battery;
    int trips;
} Robot;

int main(void) {
    int n;
    if (scanf("%d", &n) != 1) return 1;
    Robot *fleet = malloc((size_t)n * sizeof *fleet);
    /* TODO */
    free(fleet);
    return 0;
}
```

## Tests
=== sample
3
alpha 0 0 50
beta 3 4 10
gamma -1 1 100
move alpha 6 8
move beta 0 1
move beta 1 0
charge beta 30
move delta 1 1
charge gamma 50
---
unknown delta
gamma (-1.00, 1.00) dist=1.41 battery=100.00 trips=0
beta (4.00, 5.00) dist=6.40 battery=36.00 trips=2
alpha (6.00, 8.00) dist=10.00 battery=30.00 trips=1
fleet_battery=55.33
farthest=alpha
=== hidden
1
solo 0 0 0
move solo 1 0
charge solo 1000
move solo 0.5 0
---
solo stuck
solo (0.50, 0.00) dist=0.50 battery=99.00 trips=1
fleet_battery=99.00
farthest=solo
=== hidden
4
d 1 0 100
c 0 1 100
b -1 0 100
a 0 -1 100
move a 0 0
---
a (0.00, -1.00) dist=1.00 battery=100.00 trips=1
b (-1.00, 0.00) dist=1.00 battery=100.00 trips=0
c (0.00, 1.00) dist=1.00 battery=100.00 trips=0
d (1.00, 0.00) dist=1.00 battery=100.00 trips=0
fleet_battery=100.00
farthest=d

## Hints
- `Robot *find(Robot *fleet, int n, const char *name)` returns `&fleet[i]` or `NULL`. Every command function then works on that pointer with `->`.
- Distance: `hypot(dx, dy)`, which is more accurate than `sqrt(dx*dx + dy*dy)` and avoids overflow.
- The qsort comparator receives `const void *` pointing at two `Robot`s. Compare the distances with `<`/`>` (don't subtract doubles and cast to int), then `strcmp` the names.

## Solution
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct { double x, y; } Vec2;
typedef struct {
    char name[16];
    Vec2 pos;
    double battery;
    int trips;
} Robot;

static double norm(Vec2 v) { return hypot(v.x, v.y); }

static Robot *find(Robot *fleet, int n, const char *name) {
    for (int i = 0; i < n; i++)
        if (strcmp(fleet[i].name, name) == 0) return &fleet[i];
    return NULL;
}

static void move(Robot *r, Vec2 d) {
    if (r->battery <= 0) { printf("%s stuck\n", r->name); return; }
    r->pos.x += d.x;
    r->pos.y += d.y;
    r->battery -= 2 * norm(d);
    if (r->battery < 0) r->battery = 0;
    r->trips++;
}

static void charge(Robot *r, double amount) {
    r->battery += amount;
    if (r->battery > 100) r->battery = 100;
}

static int by_distance(const void *a, const void *b) {
    const Robot *x = a, *y = b;
    double dx = norm(x->pos), dy = norm(y->pos);
    if (dx < dy) return -1;
    if (dx > dy) return 1;
    return strcmp(x->name, y->name);
}

int main(void) {
    int n;
    if (scanf("%d", &n) != 1) return 1;
    Robot *fleet = malloc((size_t)n * sizeof *fleet);
    if (!fleet) return 1;
    for (int i = 0; i < n; i++) {
        Robot *r = &fleet[i];
        scanf("%15s %lf %lf %lf", r->name, &r->pos.x, &r->pos.y, &r->battery);
        r->trips = 0;
    }
    char cmd[16], name[16];
    while (scanf("%15s %15s", cmd, name) == 2) {
        Robot *r = find(fleet, n, name);
        if (strcmp(cmd, "move") == 0) {
            Vec2 d;
            scanf("%lf %lf", &d.x, &d.y);
            if (r) move(r, d); else printf("unknown %s\n", name);
        } else if (strcmp(cmd, "charge") == 0) {
            double amt;
            scanf("%lf", &amt);
            if (r) charge(r, amt); else printf("unknown %s\n", name);
        }
    }
    qsort(fleet, (size_t)n, sizeof *fleet, by_distance);
    double total = 0;
    for (int i = 0; i < n; i++) {
        const Robot *r = &fleet[i];
        printf("%s (%.2f, %.2f) dist=%.2f battery=%.2f trips=%d\n",
               r->name, r->pos.x, r->pos.y, norm(r->pos), r->battery, r->trips);
        total += r->battery;
    }
    printf("fleet_battery=%.2f\nfarthest=%s\n", total / n, fleet[n - 1].name);
    free(fleet);
    return 0;
}
```

Structs bundle each robot's state, and the nested `Vec2` makes position arithmetic read naturally. Functions take `Robot *` because they modify the caller's robot: passing by value would update a copy. `find` returns a pointer into the array, or `NULL` to signal absence (C's version of `optional`). `qsort` sorts the records in place, and the comparator returns −1/0/+1 from explicit comparisons, because `(int)(dx - dy)` would truncate differences smaller than 1 to 0.
