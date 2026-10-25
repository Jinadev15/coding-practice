---
id: c-sensor-vtables
title: Sensor Drivers with Hand-Built vtables
difficulty: Hard
order: 1
tags: OOP in C, polymorphism, vtables, function pointers, overriding, super calls, NVI
time_limit: 3
---
## Statement
Build a polymorphic sensor layer in C, the way device drivers and HALs do it: a base struct whose first member points to a `static const` operations table (a vtable), concrete "classes" that embed the base, and one class that **extends another and calls its parent's implementation**.

The base types are given:

```c
typedef struct Sensor Sensor;
typedef struct {
    const char *kind;
    int    (*read)(Sensor *self, double *out);   /* required */
    double (*max_range)(const Sensor *self);     /* optional: may be NULL */
    void   (*destroy)(Sensor *self);             /* required */
} SensorOps;
struct Sensor { const SensorOps *ops; const char *name; int id; unsigned reads, failures; };
enum { SENSOR_OK = 0, SENSOR_EINVAL = -1, SENSOR_EIO = -2, SENSOR_ERANGE = -3 };
double world_distance(int id, unsigned tick);    /* provided by the judge: the simulated world */
```

**The non-virtual interface (base functions):**
- `int sensor_read(Sensor *s, double *out)`:
  - NULL `s` or `out` returns `SENSOR_EINVAL` and counts nothing.
  - Otherwise it dispatches to `ops->read` into a temporary, and increments `reads`.
  - If the read succeeded but the value is negative or above `sensor_max_range(s)`, the result becomes `SENSOR_ERANGE`.
  - Any non-OK result increments `failures` and leaves `*out` untouched. On success, store the value.
- `double sensor_max_range(const Sensor *s)` returns `ops->max_range(s)`, or a **default of 10.0** when the entry is NULL.
- `const char *sensor_kind(const Sensor *s)` and `void sensor_destroy(Sensor *s)` (which accepts NULL).

**The classes** (each has its own `static const SensorOps`):
- `Sensor *lidar_create(name, id, scale)`: each read returns `world_distance(id, tick) * scale` with a per-object `tick` starting at 0 and incrementing on every read. `max_range` is 30. `kind` is `"lidar"`.
- `Sensor *sonar_create(name, id)`: same tick scheme, but a world value **> 5.0** fails with `SENSOR_EIO`. The `max_range` entry is **NULL**, so it uses the default. `kind` is `"sonar"`.
- `Sensor *filtered_lidar_create(name, id, scale, alpha)`: **extends lidar** (it embeds a `Lidar` as its first member). Its `read` calls **the lidar implementation** to get the raw value (so the tick advances), then applies an exponential moving average: `state = raw` on the first success, else `state = alpha*raw + (1-alpha)*state`. It returns `state`. Lidar failures (none in practice) pass through. It inherits lidar's `max_range`, and its `kind` is `"filtered-lidar"`.

## Starter
```c
#include <stdlib.h>

typedef struct Sensor Sensor;
typedef struct {
    const char *kind;
    int    (*read)(Sensor *self, double *out);
    double (*max_range)(const Sensor *self);
    void   (*destroy)(Sensor *self);
} SensorOps;
struct Sensor { const SensorOps *ops; const char *name; int id; unsigned reads, failures; };
enum { SENSOR_OK = 0, SENSOR_EINVAL = -1, SENSOR_EIO = -2, SENSOR_ERANGE = -3 };
double world_distance(int id, unsigned tick);

int sensor_read(Sensor *s, double *out) { return s->ops->read(s, out); }
double sensor_max_range(const Sensor *s) { return s->ops->max_range(s); }
const char *sensor_kind(const Sensor *s) { return s->ops->kind; }
void sensor_destroy(Sensor *s) { s->ops->destroy(s); }

Sensor *lidar_create(const char *name, int id, double scale) { (void)name; (void)id; (void)scale; return NULL; }
Sensor *sonar_create(const char *name, int id) { (void)name; (void)id; return NULL; }
Sensor *filtered_lidar_create(const char *name, int id, double scale, double alpha) { (void)name; (void)id; (void)scale; (void)alpha; return NULL; }
```

## Driver
```c
#include <stdio.h>
#include <string.h>

double world_distance(int id, unsigned tick) {
    static const double pattern[] = {2.0, 3.5, 6.0, 1.25, 40.0, 4.75, 8.5, 0.5};
    return pattern[(tick + (unsigned)id) % 8] + (id == 9 ? -10.0 : 0.0);
}

static void run(Sensor *s, int n) {
    printf("%-8s %-14s max=%-4g:", s->name, sensor_kind(s), sensor_max_range(s));
    for (int i = 0; i < n; i++) {
        double v = -99;
        int rc = sensor_read(s, &v);
        if (rc == SENSOR_OK) printf(" %.3f", v); else printf(" E%d", -rc);
    }
    printf(" | reads=%u failures=%u\n", s->reads, s->failures);
}

int main(void) {
    char cmd[32];
    while (scanf("%31s", cmd) == 1) {
        if (!strcmp(cmd, "basic")) {
            Sensor *l = lidar_create("front", 0, 1.0), *s = sonar_create("rear", 0), *f = filtered_lidar_create("top", 0, 1.0, 0.5);
            run(l, 8); run(s, 8); run(f, 8);
            printf("distinct vtables: %d %d, base at offset 0: %d\n", l->ops != s->ops, l->ops != f->ops, (void *)f == (void *)&f->ops);
            double v = 7;
            printf("null checks: %d %d, v=%g, reads=%u\n", sensor_read(NULL, &v), sensor_read(l, NULL), v, l->reads);
            sensor_destroy(l); sensor_destroy(s); sensor_destroy(f); sensor_destroy(NULL);
        } else if (!strcmp(cmd, "scaled")) {
            Sensor *arr[] = { lidar_create("half", 3, 0.5), filtered_lidar_create("smooth", 2, 2.0, 0.25), sonar_create("near", 5), lidar_create("broken", 9, 1.0) };
            for (int i = 0; i < 4; i++) run(arr[i], 10);
            for (int i = 0; i < 4; i++) sensor_destroy(arr[i]);
        } else if (!strcmp(cmd, "fleet")) {
            enum { N = 3000 };
            static Sensor *fleet[N];
            for (int i = 0; i < N; i++) {
                switch (i % 3) {
                case 0: fleet[i] = lidar_create("l", i, 1.0 + (i % 5) * 0.1); break;
                case 1: fleet[i] = sonar_create("s", i); break;
                default: fleet[i] = filtered_lidar_create("f", i, 1.0, 0.1 + (i % 9) * 0.1); break;
                }
            }
            double sum = 0; unsigned long fails = 0, reads = 0;
            for (int round = 0; round < 100; round++)
                for (int i = 0; i < N; i++) { double v; if (sensor_read(fleet[i], &v) == SENSOR_OK) sum += v; }
            for (int i = 0; i < N; i++) { fails += fleet[i]->failures; reads += fleet[i]->reads; sensor_destroy(fleet[i]); }
            printf("reads %lu failures %lu sum %.4f\n", reads, fails, sum);
        }
    }
    return 0;
}
```

## Tests
=== sample
basic
---
front    lidar          max=30  : 2.000 3.500 6.000 1.250 E3 4.750 8.500 0.500 | reads=8 failures=1
rear     sonar          max=10  : 2.000 3.500 E2 1.250 E2 4.750 E2 0.500 | reads=8 failures=3
top      filtered-lidar max=30  : 2.000 2.750 4.375 2.812 21.406 13.078 10.789 5.645 | reads=8 failures=0
distinct vtables: 1 1, base at offset 0: 1
null checks: -1 -1, v=7, reads=8
=== hidden
scaled
---
half     lidar          max=30  : 0.625 20.000 2.375 4.250 0.250 1.000 1.750 3.000 0.625 20.000 | reads=10 failures=0
smooth   filtered-lidar max=30  : 12.000 9.625 27.219 22.789 21.342 16.256 13.192 11.644 11.733 9.425 | reads=10 failures=0
near     sonar          max=10  : 4.750 E2 0.500 2.000 3.500 E2 1.250 E2 4.750 E2 | reads=10 failures=4
broken   lidar          max=30  : E3 E3 E3 30.000 E3 E3 E3 E3 E3 E3 | reads=10 failures=9
=== hidden
fleet
---
reads 300000 failures 54334 sum 1224217.8798

## Hints
- `typedef struct { Sensor base; unsigned tick; double scale; } Lidar;` and `typedef struct { Lidar lidar; double alpha, state; int primed; } FilteredLidar;`. Because each embeds its parent first, all three pointers coincide.
- Implementation functions are `static` and take `Sensor *self`. Inside, downcast: `Lidar *l = (Lidar *)self;`.
- The super call: `int rc = LIDAR_OPS.read(self, &raw);`. Declare `static const SensorOps LIDAR_OPS` before the filtered class.
- The constructor fills the whole object with a compound literal, so the counters start at 0: `*l = (Lidar){ .base = { .ops = &LIDAR_OPS, .name = name, .id = id }, .scale = scale };`.

## Solution
```c
#include <stdlib.h>

typedef struct Sensor Sensor;
typedef struct {
    const char *kind;
    int    (*read)(Sensor *self, double *out);
    double (*max_range)(const Sensor *self);
    void   (*destroy)(Sensor *self);
} SensorOps;
struct Sensor { const SensorOps *ops; const char *name; int id; unsigned reads, failures; };
enum { SENSOR_OK = 0, SENSOR_EINVAL = -1, SENSOR_EIO = -2, SENSOR_ERANGE = -3 };
double world_distance(int id, unsigned tick);

/* ---- base: non-virtual interface ---- */
double sensor_max_range(const Sensor *s) {
    return s->ops->max_range ? s->ops->max_range(s) : 10.0;   /* default for optional entry */
}

int sensor_read(Sensor *s, double *out) {
    if (!s || !out) return SENSOR_EINVAL;
    double v;
    int rc = s->ops->read(s, &v);                               /* dynamic dispatch */
    s->reads++;
    if (rc == SENSOR_OK && (v < 0 || v > sensor_max_range(s))) rc = SENSOR_ERANGE;
    if (rc != SENSOR_OK) { s->failures++; return rc; }
    *out = v;
    return SENSOR_OK;
}

const char *sensor_kind(const Sensor *s) { return s->ops->kind; }
void sensor_destroy(Sensor *s) { if (s) s->ops->destroy(s); }

static void free_sensor(Sensor *self) { free(self); }          /* shared "destructor" */

/* ---- Lidar ---- */
typedef struct { Sensor base; unsigned tick; double scale; } Lidar;

static int lidar_read(Sensor *self, double *out) {
    Lidar *l = (Lidar *)self;
    *out = world_distance(self->id, l->tick++) * l->scale;
    return SENSOR_OK;
}
static double lidar_range(const Sensor *self) { (void)self; return 30.0; }
static const SensorOps LIDAR_OPS = { "lidar", lidar_read, lidar_range, free_sensor };

Sensor *lidar_create(const char *name, int id, double scale) {
    Lidar *l = malloc(sizeof *l);
    if (!l) return NULL;
    *l = (Lidar){ .base = { .ops = &LIDAR_OPS, .name = name, .id = id }, .scale = scale };
    return &l->base;
}

/* ---- Sonar: no max_range entry -> base default ---- */
typedef struct { Sensor base; unsigned tick; } Sonar;

static int sonar_read(Sensor *self, double *out) {
    Sonar *s = (Sonar *)self;
    double d = world_distance(self->id, s->tick++);
    if (d > 5.0) return SENSOR_EIO;
    *out = d;
    return SENSOR_OK;
}
static const SensorOps SONAR_OPS = { "sonar", sonar_read, NULL, free_sensor };

Sensor *sonar_create(const char *name, int id) {
    Sonar *s = malloc(sizeof *s);
    if (!s) return NULL;
    *s = (Sonar){ .base = { .ops = &SONAR_OPS, .name = name, .id = id } };
    return &s->base;
}

/* ---- FilteredLidar extends Lidar ---- */
typedef struct { Lidar lidar; double alpha, state; int primed; } FilteredLidar;

static int filtered_read(Sensor *self, double *out) {
    FilteredLidar *f = (FilteredLidar *)self;
    double raw;
    int rc = LIDAR_OPS.read(self, &raw);                        /* "super" call: parent's implementation */
    if (rc != SENSOR_OK) return rc;
    f->state = f->primed ? f->alpha * raw + (1.0 - f->alpha) * f->state : raw;
    f->primed = 1;
    *out = f->state;
    return SENSOR_OK;
}
static const SensorOps FILTERED_OPS = { "filtered-lidar", filtered_read, lidar_range, free_sensor };

Sensor *filtered_lidar_create(const char *name, int id, double scale, double alpha) {
    FilteredLidar *f = malloc(sizeof *f);
    if (!f) return NULL;
    *f = (FilteredLidar){ .lidar = { .base = { .ops = &FILTERED_OPS, .name = name, .id = id }, .scale = scale },
                          .alpha = alpha };
    return &f->lidar.base;
}
```

- **The vtable** is `static const`: one table per class, which can live in flash, and each object carries just its `ops` pointer. That's exactly C++'s vptr/vtable layout, written out by hand.
- **The non-virtual interface**: clients call `sensor_read`, which validates arguments, dispatches, counts reads and failures, and enforces the range invariant for *every* class. A subclass can't forget to count or bypass range checking.
- **Optional entries with defaults**: the sonar leaves `max_range` NULL, and the base supplies 10.0. That's a default implementation in C++ terms.
- **Overriding with a super call**: `FilteredLidar` embeds `Lidar`, so it can call `LIDAR_OPS.read(self, ...)` directly, reusing the parent's behaviour (including advancing its `tick`) and adding filtering on top.
- **Open/closed**: the 3,000-sensor loop calls one function and never mentions a concrete type. New sensor classes need no changes to it.
