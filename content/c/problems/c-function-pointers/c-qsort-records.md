---
id: c-qsort-records
title: Sorting Records with qsort
difficulty: Medium
order: 1
tags: qsort, comparators, function pointers, structs
---
## Statement
Read `n` robot records `name battery distance` (the name has no spaces, at most 15 chars; battery is an int 0–100; distance is a double). Then a sort key: `battery`, `distance` or `name`.

Sort with `qsort` using a comparator chosen through a **table of function pointers** (no `if`/`switch` around the `qsort` call itself):

- `battery`: descending; ties by name ascending
- `distance`: ascending; ties by name ascending
- `name`: ascending

Print the records as `name battery distance(2 decimals)`.

## Starter
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char name[16];
    int battery;
    double distance;
} Robot;

int main(void) {
    int n;
    scanf("%d", &n);
    Robot *r = malloc(sizeof *r * (size_t)n);
    for (int i = 0; i < n; i++) scanf("%15s %d %lf", r[i].name, &r[i].battery, &r[i].distance);
    char key[16];
    scanf("%15s", key);

    free(r);
    return 0;
}
```

## Tests
=== sample
4
ada 50 3.5
bo 90 1.0
cy 50 0.5
dee 90 7.25
battery
---
bo 90 1.00
dee 90 7.25
ada 50 3.50
cy 50 0.50
=== hidden
3
z 1 2.0
y 1 2.0
x 9 0.1
distance
---
x 9 0.10
y 1 2.00
z 1 2.00
=== hidden
3
mid 5 1
alpha 5 1
zulu 5 1
name
---
alpha 5 1.00
mid 5 1.00
zulu 5 1.00

## Hints
- Comparators take `const void *`: `const Robot *a = pa, *b = pb;`.
- Compare doubles with `(x > y) - (x < y)`, never by subtracting and casting to int.
- `struct { const char *key; int (*cmp)(const void *, const void *); } table[] = {...};`.

## Solution
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char name[16];
    int battery;
    double distance;
} Robot;

static int by_name(const void *pa, const void *pb) {
    const Robot *a = pa, *b = pb;
    return strcmp(a->name, b->name);
}

static int by_battery(const void *pa, const void *pb) {
    const Robot *a = pa, *b = pb;
    if (a->battery != b->battery) return (b->battery > a->battery) - (b->battery < a->battery);
    return by_name(pa, pb);
}

static int by_distance(const void *pa, const void *pb) {
    const Robot *a = pa, *b = pb;
    int c = (a->distance > b->distance) - (a->distance < b->distance);
    return c ? c : by_name(pa, pb);
}

static const struct {
    const char *key;
    int (*cmp)(const void *, const void *);
} SORTS[] = {{"battery", by_battery}, {"distance", by_distance}, {"name", by_name}};

int main(void) {
    int n;
    scanf("%d", &n);
    Robot *r = malloc(sizeof *r * (size_t)n);
    for (int i = 0; i < n; i++) scanf("%15s %d %lf", r[i].name, &r[i].battery, &r[i].distance);
    char key[16];
    scanf("%15s", key);
    int (*cmp)(const void *, const void *) = by_name;
    for (size_t i = 0; i < sizeof SORTS / sizeof SORTS[0]; i++)
        if (strcmp(SORTS[i].key, key) == 0) cmp = SORTS[i].cmp;
    qsort(r, (size_t)n, sizeof *r, cmp);
    for (int i = 0; i < n; i++) printf("%s %d %.2f\n", r[i].name, r[i].battery, r[i].distance);
    free(r);
    return 0;
}
```

`qsort` isn't stable, so every comparator must break ties completely (here, by name) to make the output deterministic. The table turns "which sort?" into data: adding a new key is one new row.
