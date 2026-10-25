---
id: c-debug-channel-log
title: Debug the Telemetry Channel Log
difficulty: Medium
order: 1
tags: debugging, gdb, sanitizers, off-by-one, realloc, qsort comparator, memmove
time_limit: 3
---
## Statement
A teammate wrote this telemetry module for the robot's logger. It compiles cleanly with `-Wall -Wextra`, yet it **crashes, corrupts memory and returns wrong statistics**. The specification below is correct, and the code is not. Find and fix every bug **without changing the API**.

Work the way you would on a real codebase:
- Copy the starter into a file, add a `main` that exercises it, and build with `gcc -g -O0 -fsanitize=address,undefined`.
- Use GDB (`bt`, `print`, `watch`) on whatever crashes.
- The judge's hidden tests also hammer the module with hundreds of thousands of operations.

**Specification**
- `void log_init(Log *l)` / `void log_free(Log *l)`: an empty log, and freeing every allocation (leaving an empty, reusable log).
- `int log_add(Log *l, const char *name, double v)`: appends `v` to the channel called `name`, creating the channel (at the end of the list) if needed. Names are 1–15 characters. Return the channel's index, or **-1** for an invalid name (NULL, empty, or longer than 15).
- `const Channel *log_find(const Log *l, const char *name)`: the channel, or NULL.
- `double channel_mean(const Channel *c)`, `channel_min`, `channel_max`: statistics over all values. Each returns 0.0 for a channel with no values.
- `double channel_median(const Channel *c)`: the middle of the sorted values, or the average of the two middle values for an even count. **Must not reorder** `c->vals`, which keeps arrival order.
- `int log_remove(Log *l, const char *name)`: deletes the channel and keeps the others in order. Returns 0, or -1 if it isn't found.

## Starter
```c
#include <stdlib.h>
#include <string.h>

typedef struct {
    char name[16];
    double *vals;
    int count, cap;
    double sum, min, max;
} Channel;

typedef struct {
    Channel *ch;
    int n, cap;
} Log;

void log_init(Log *l) { l->ch = NULL; l->n = 0; l->cap = 0; }

void log_free(Log *l) {
    for (int i = 0; i < l->n; i++) free(l->ch[i].vals);
    free(l->ch);
}

const Channel *log_find(const Log *l, const char *name) {
    for (int i = 0; i <= l->n; i++)
        if (strcmp(l->ch[i].name, name) == 0) return &l->ch[i];
    return NULL;
}

int log_add(Log *l, const char *name, double v) {
    if (name == NULL || strlen(name) > 16) return -1;
    int idx = -1;
    for (int i = 0; i < l->n; i++) if (strcmp(l->ch[i].name, name) == 0) idx = i;
    if (idx < 0) {
        if (l->n == l->cap) {
            l->cap = l->cap * 2;
            l->ch = realloc(l->ch, l->cap * sizeof(Channel));
        }
        idx = l->n++;
        Channel *c = &l->ch[idx];
        strcpy(c->name, name);
        c->vals = NULL; c->count = 0; c->cap = 0;
        c->sum = 0; c->min = 0; c->max = 0;
    }
    Channel *c = &l->ch[idx];
    if (c->count == c->cap) {
        c->cap = c->cap ? c->cap * 2 : 4;
        c->vals = realloc(c->vals, c->cap);
    }
    c->vals[c->count++] = v;
    c->sum += v;
    if (v < c->min) c->min = v;
    if (v > c->max) c->max = v;
    return idx;
}

double channel_mean(const Channel *c) { return c->sum / c->count; }
double channel_min(const Channel *c) { return c->min; }
double channel_max(const Channel *c) { return c->max; }

static int cmp_double(const void *a, const void *b) {
    return (int)(*(const double *)a - *(const double *)b);
}

double channel_median(const Channel *c) {
    if (c->count == 0) return 0.0;
    double *v = c->vals;
    qsort(v, (size_t)c->count, sizeof *v, cmp_double);
    int n = c->count;
    return n % 2 ? v[n / 2] : (v[n / 2] + v[n / 2 + 1]) / 2;
}

int log_remove(Log *l, const char *name) {
    for (int i = 0; i < l->n; i++) {
        if (strcmp(l->ch[i].name, name) == 0) {
            free(l->ch[i].vals);
            memmove(&l->ch[i], &l->ch[i + 1], (size_t)(l->n - i) * sizeof(Channel));
            l->n--;
            return 0;
        }
    }
    return -1;
}
```

## Driver
```c
#include <stdio.h>

static unsigned rs = 99;
static unsigned rnd(void) { rs ^= rs << 13; rs ^= rs >> 17; rs ^= rs << 5; return rs; }
static void stats(const Log *l, const char *nm) {
    const Channel *c = log_find(l, nm);
    if (!c) { printf("%s: missing\n", nm); return; }
    printf("%s: n=%d mean=%.3f min=%.3f max=%.3f median=%.3f first=%.3f\n", nm, c->count, channel_mean(c),
           channel_min(c), channel_max(c), channel_median(c), c->count ? c->vals[0] : 0.0);
}

int main(void) {
    char cmd[16];
    while (scanf("%15s", cmd) == 1) {
        Log L; log_init(&L);
        if (!strcmp(cmd, "basic")) {
            double v[] = {3.5, 1.25, 9.0, 2.75, 2.5, 8.0};
            for (int i = 0; i < 6; i++) log_add(&L, i % 2 ? "imu.ax" : "wheel.left.rpm", v[i]);
            log_add(&L, "battery", 12.6); log_add(&L, "battery", 12.4); log_add(&L, "battery", 12.5); log_add(&L, "battery", 12.3);
            stats(&L, "wheel.left.rpm"); stats(&L, "imu.ax"); stats(&L, "battery"); stats(&L, "gps");
            int i1 = log_add(&L, "imu.ax", 0.5), i2 = log_add(&L, "a_name_of_16_chr", 1), i3 = log_add(&L, "", 1);
            printf("idx %d %d %d\n", i1, i2, i3);
            printf("idx15 %d\n", log_add(&L, "exactly15chars!", 4.0));
            stats(&L, "exactly15chars!");
        } else if (!strcmp(cmd, "negative")) {
            log_add(&L, "temp", -5.0); log_add(&L, "temp", -0.25); log_add(&L, "temp", -0.75); log_add(&L, "temp", -12.0);
            log_add(&L, "close", 0.1); log_add(&L, "close", 0.4); log_add(&L, "close", 0.3); log_add(&L, "close", 0.2); log_add(&L, "close", 0.5);
            stats(&L, "temp"); stats(&L, "close");
        } else if (!strcmp(cmd, "remove")) {
            const char *nm[] = {"a", "b", "c", "d", "e"};
            for (int i = 0; i < 5; i++) for (int k = 0; k <= i; k++) log_add(&L, nm[i], i * 10 + k);
            int r1 = log_remove(&L, "c"), r2 = log_remove(&L, "c"), r3 = log_remove(&L, "e");
            printf("%d %d %d\n", r1, r2, r3);
            for (int i = 0; i < L.n; i++) printf("%s(%d) ", L.ch[i].name, L.ch[i].count);
            printf("\n");
            printf("re-add idx %d\n", log_add(&L, "c", 1.0));
            stats(&L, "d"); stats(&L, "c");
        } else if (!strcmp(cmd, "stress")) {
            char name[16]; double total = 0; unsigned long long h = 1469598103934665603ull;
            for (int it = 0; it < 400000; it++) {
                snprintf(name, sizeof name, "ch%u", rnd() % 300);
                unsigned op = rnd() % 100;
                if (op < 92) log_add(&L, name, (double)(int)(rnd() % 20001) / 100.0 - 100.0);
                else if (op < 95) log_remove(&L, name);
                else { const Channel *c = log_find(&L, name); if (c) { total += channel_median(c) + channel_mean(c); h = (h ^ (unsigned)c->count) * 1099511628211ull; } }
            }
            double mn = 1e9, mx = -1e9; long cnt = 0;
            for (int i = 0; i < L.n; i++) { cnt += L.ch[i].count; if (channel_min(&L.ch[i]) < mn) mn = channel_min(&L.ch[i]); if (channel_max(&L.ch[i]) > mx) mx = channel_max(&L.ch[i]); }
            printf("channels %d values %ld min %.2f max %.2f checksum %.4f hash %016llx\n", L.n, cnt, mn, mx, total, h);
            for (int i = 0; i < L.n; i += 60) stats(&L, L.ch[i].name);
            log_free(&L); log_init(&L);
            printf("reuse idx %d\n", log_add(&L, "x", 1));
        }
        log_free(&L);
    }
    return 0;
}
```

## Tests
=== sample
basic
---
wheel.left.rpm: n=3 mean=5.000 min=2.500 max=9.000 median=3.500 first=3.500
imu.ax: n=3 mean=4.000 min=1.250 max=8.000 median=2.750 first=1.250
battery: n=4 mean=12.450 min=12.300 max=12.600 median=12.450 first=12.600
gps: missing
idx 1 -1 -1
idx15 3
exactly15chars!: n=1 mean=4.000 min=4.000 max=4.000 median=4.000 first=4.000
=== hidden
negative
---
temp: n=4 mean=-4.500 min=-12.000 max=-0.250 median=-2.875 first=-5.000
close: n=5 mean=0.300 min=0.100 max=0.500 median=0.300 first=0.100
=== hidden
remove
---
0 -1 0
a(1) b(2) d(4) 
re-add idx 3
d: n=4 mean=31.500 min=30.000 max=33.000 median=31.500 first=30.000
c: n=1 mean=1.000 min=1.000 max=1.000 median=1.000 first=1.000
=== hidden
stress
---
channels 288 values 9061 min -99.99 max 100.00 checksum -5982.9683 hash 79f8004af5426521
ch298: n=189 mean=0.305 min=-99.260 max=99.060 median=-2.080 first=-32.390
ch180: n=51 mean=-3.724 min=-97.590 max=99.470 median=-1.620 first=-35.900
ch1: n=29 mean=-2.218 min=-98.450 max=99.440 median=4.000 first=-69.570
ch125: n=15 mean=-16.630 min=-98.340 max=88.700 median=-18.940 first=-1.800
ch183: n=7 mean=-2.893 min=-99.600 max=80.670 median=20.160 first=-99.600
reuse idx 0

## Hints
- `log_find` and `log_remove` contain classic **off-by-one** errors. One reads a channel that doesn't exist, and the other copies one element too many.
- Growing from capacity 0 by doubling stays 0 forever. And `realloc(p, cap)` allocates `cap` **bytes**, not `cap` doubles.
- A 16-character name doesn't fit in `char name[16]` together with its terminator.
- What are `min` and `max` after the first value if both start at 0 and every reading is positive (or every reading is negative)? And what's `0.0 / 0`?
- The comparator truncates `0.3 - 0.2` to 0, so it calls them equal. The median also sorts the caller's data in place, and for an even count, which two indices are the middle ones?

## Solution
```c
#include <stdlib.h>
#include <string.h>

typedef struct {
    char name[16];
    double *vals;
    int count, cap;
    double sum, min, max;
} Channel;

typedef struct {
    Channel *ch;
    int n, cap;
} Log;

void log_init(Log *l) { l->ch = NULL; l->n = 0; l->cap = 0; }

void log_free(Log *l) {
    for (int i = 0; i < l->n; i++) free(l->ch[i].vals);
    free(l->ch);
    log_init(l);                                          /* reusable, no dangling pointer */
}

const Channel *log_find(const Log *l, const char *name) {
    if (name == NULL) return NULL;
    for (int i = 0; i < l->n; i++)                        /* was <= : read past the end */
        if (strcmp(l->ch[i].name, name) == 0) return &l->ch[i];
    return NULL;
}

int log_add(Log *l, const char *name, double v) {
    if (name == NULL) return -1;
    size_t len = strlen(name);
    if (len == 0 || len > 15) return -1;                  /* 15 chars + '\0' = 16 bytes */
    int idx = -1;
    for (int i = 0; i < l->n && idx < 0; i++) if (strcmp(l->ch[i].name, name) == 0) idx = i;
    if (idx < 0) {
        if (l->n == l->cap) {
            int ncap = l->cap ? l->cap * 2 : 8;           /* 0 * 2 == 0 */
            Channel *p = realloc(l->ch, (size_t)ncap * sizeof *p);
            if (p == NULL) return -1;                     /* keep the old block on failure */
            l->ch = p; l->cap = ncap;
        }
        idx = l->n++;
        Channel *c = &l->ch[idx];
        memcpy(c->name, name, len + 1);
        c->vals = NULL; c->count = 0; c->cap = 0;
        c->sum = 0;
    }
    Channel *c = &l->ch[idx];
    if (c->count == c->cap) {
        int ncap = c->cap ? c->cap * 2 : 4;
        double *p = realloc(c->vals, (size_t)ncap * sizeof *p);   /* bytes, not elements */
        if (p == NULL) return -1;
        c->vals = p; c->cap = ncap;
    }
    c->vals[c->count++] = v;
    c->sum += v;
    if (c->count == 1 || v < c->min) c->min = v;          /* first value initialises min/max */
    if (c->count == 1 || v > c->max) c->max = v;
    return idx;
}

double channel_mean(const Channel *c) { return c->count ? c->sum / c->count : 0.0; }
double channel_min(const Channel *c) { return c->count ? c->min : 0.0; }
double channel_max(const Channel *c) { return c->count ? c->max : 0.0; }

static int cmp_double(const void *a, const void *b) {
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);                             /* no truncation, no overflow */
}

double channel_median(const Channel *c) {
    if (c->count == 0) return 0.0;
    int n = c->count;
    double *v = malloc((size_t)n * sizeof *v);            /* sort a copy: keep arrival order */
    if (v == NULL) return 0.0;
    memcpy(v, c->vals, (size_t)n * sizeof *v);
    qsort(v, (size_t)n, sizeof *v, cmp_double);
    double m = n % 2 ? v[n / 2] : (v[n / 2 - 1] + v[n / 2]) / 2;   /* middle pair is n/2-1, n/2 */
    free(v);
    return m;
}

int log_remove(Log *l, const char *name) {
    if (name == NULL) return -1;
    for (int i = 0; i < l->n; i++) {
        if (strcmp(l->ch[i].name, name) == 0) {
            free(l->ch[i].vals);
            memmove(&l->ch[i], &l->ch[i + 1], (size_t)(l->n - i - 1) * sizeof(Channel));   /* was n - i */
            l->n--;
            return 0;
        }
    }
    return -1;
}
```

The bugs, and how you'd find each one:

| Bug | Symptom | Tool that pinpoints it |
|---|---|---|
| `i <= l->n` in `log_find` | reads garbage or crashes for a missing name | ASan: heap-buffer-overflow in `log_find` |
| capacity `0 * 2` | the first channel writes through a NULL or zero-size block | segfault, so `bt` in GDB |
| `realloc(vals, cap)` (bytes) | heap corruption, later random crashes | ASan: heap-buffer-overflow at `c->vals[c->count++]` |
| `strlen > 16` | a 16-char name overflows `name[16]` | ASan or `-D_FORTIFY_SOURCE=2` |
| min/max start at 0 | wrong min for all-positive data, wrong max for all-negative | unit test with negative values |
| mean of an empty channel | `0/0` = NaN | UBSan (`-fsanitize=float-divide-by-zero`) |
| truncating comparator | 0.3 and 0.2 compare "equal", giving a wrong median | test with values closer than 1 |
| in-place sort | `vals[0]` changes after a median call | test checks arrival order |
| wrong middle pair | even-count median uses `n/2` and `n/2+1`, reading past the end | ASan, test with 2 values |
| `memmove` copies `n - i` items | reads one `Channel` past the live end | ASan or Valgrind |
| `log_free` leaves stale `ch`/`n` | use-after-free when the log is reused | ASan: heap-use-after-free |

- The lesson: `-Wall -Wextra` caught **none** of these. A sanitizer build plus focused tests (edge values, empty, negative, close values, reuse) catches all of them, and GDB answers "where" once something crashes.
