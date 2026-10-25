---
id: c-abi-stable-library
title: An ABI-Stable Library Interface (Multi-File)
difficulty: Hard
order: 1
tags: libraries, ABI, opaque types, versioned structs, function tables, plugins, multi-file
time_limit: 3
---
## Statement
You maintain `libgeo`, a calibration library shipped as a shared object. Version 2 added clamping to the config struct, but robot applications compiled against **version 1** must keep working **without recompiling**. Plugin loaders find the library through one entry point that returns a function table (the `dlsym` pattern). Implement `geo.c` against the public header `geo.h`, which is part of the published ABI: don't change it.

```c
typedef struct Geo Geo;                      /* opaque: clients never see the layout */
typedef struct {
    uint32_t size;                           /* sizeof(GeoConfig) the CALLER was compiled with */
    double scale, offset;                    /* v1 */
    double clamp_min, clamp_max;             /* added in v2 */
} GeoConfig;
#define GEO_CONFIG_V1_SIZE offsetof(GeoConfig, clamp_min)
```

| Function (via the table) | Contract |
|---|---|
| `geo_get_api(major)` | Returns a pointer to one **static const** `GeoApi` with `abi_major = 2`, `abi_minor = 1`, if `major == 2`. Otherwise NULL. |
| `create()` | New object: scale 1, offset 0, no clamping, 0 calls. NULL if allocation fails. |
| `destroy(g)` | Frees `g`. `destroy(NULL)` is a no-op. |
| `configure(g, cfg)` | See below. |
| `apply(g, x)` | `y = scale·x + offset`, clamped to `[clamp_min, clamp_max]` when clamping is on. Counts the call. `apply(NULL, x)` returns NaN. |
| `calls(g)` | The number of `apply` calls on `g` (0 for NULL). |

**`configure`** reads **only the bytes the caller says exist**:
- NULL `g` or `cfg` gives -1.
- `cfg->size < GEO_CONFIG_V1_SIZE` gives -2.
- `scale` must be finite and non-zero, and `offset` finite, else -3.
- If `cfg->size >= sizeof(GeoConfig)` (a v2 caller, or a future caller with a larger struct), read the clamp fields. Both must be non-NaN, else -3. Clamping is on iff `clamp_min <= clamp_max`.
- A v1 caller has clamping off.
- On any error the object is unchanged. Return 0 on success, or **1** if `size > sizeof(GeoConfig)` (accepted, but the extension fields were ignored).

The judge passes v1 configs that **end exactly at an unmapped page**. Reading `clamp_min` from a v1 caller's struct crashes, just as it would read garbage in a real old binary.

## Starter: geo.h
```c
#ifndef GEO_H
#define GEO_H
#include <stddef.h>
#include <stdint.h>

#define GEO_ABI_MAJOR 2u
#define GEO_ABI_MINOR 1u

typedef struct Geo Geo;

typedef struct {
    uint32_t size;
    double scale, offset;
    double clamp_min, clamp_max;
} GeoConfig;
#define GEO_CONFIG_V1_SIZE offsetof(GeoConfig, clamp_min)

typedef struct {
    uint32_t abi_major, abi_minor;
    Geo *(*create)(void);
    void (*destroy)(Geo *g);
    int (*configure)(Geo *g, const GeoConfig *cfg);
    double (*apply)(Geo *g, double x);
    uint64_t (*calls)(const Geo *g);
} GeoApi;

const GeoApi *geo_get_api(uint32_t abi_major);
#endif
```

## Starter: geo.c
```c
#include "geo.h"
#include <stdlib.h>

struct Geo { double scale, offset, lo, hi; int clamp; uint64_t calls; };

static Geo *create(void) { Geo *g = malloc(sizeof *g); g->scale = 1; g->offset = 0; g->clamp = 0; return g; }
static void destroy(Geo *g) { g->calls = 0; free(g); }
static int configure(Geo *g, const GeoConfig *c) {
    g->scale = c->scale; g->offset = c->offset;
    g->lo = c->clamp_min; g->hi = c->clamp_max; g->clamp = 1;
    return 0;
}
static double apply(Geo *g, double x) {
    double y = g->scale * x + g->offset;
    if (g->clamp) y = y < g->lo ? g->lo : y > g->hi ? g->hi : y;
    return y;
}
static uint64_t calls(const Geo *g) { return g->calls; }

const GeoApi *geo_get_api(uint32_t abi_major) {
    static GeoApi api = { 2, 1, create, destroy, configure, apply, calls };
    (void)abi_major;
    return &api;
}
```

## Driver: main.c
```c
#define _DEFAULT_SOURCE
#include "geo.h"
#include <math.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

static unsigned char *page; static long psz;
static const GeoConfig *at_guard(const void *src, size_t n) {   /* copy n bytes so they end at the guard page */
    unsigned char *p = page + psz - n; memcpy(p, src, n); return (const GeoConfig *)p;
}
typedef struct { uint32_t size; double scale, offset, clamp_min, clamp_max, future_gain; } GeoConfigV3;

int main(void) {
    psz = sysconf(_SC_PAGESIZE);
    page = mmap(NULL, (size_t)psz * 2, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (page == MAP_FAILED || mprotect(page + psz, (size_t)psz, PROT_NONE)) return 1;
    char cmd[16];
    while (scanf("%15s", cmd) == 1) {
        if (!strcmp(cmd, "api")) {
            const GeoApi *a = geo_get_api(2), *b = geo_get_api(2);
            printf("v2 %s same=%d abi=%u.%u | v1 %s | v3 %s\n", a ? "ok" : "NULL", a == b, a ? a->abi_major : 0, a ? a->abi_minor : 0,
                   geo_get_api(1) ? "ok" : "NULL", geo_get_api(3) ? "ok" : "NULL");
        } else if (!strcmp(cmd, "v2")) {
            const GeoApi *A = geo_get_api(GEO_ABI_MAJOR);
            Geo *g = A->create();
            printf("default %.2f %.2f\n", A->apply(g, 3.0), A->apply(g, -1.5));
            GeoConfig c = { sizeof c, 2.0, 1.0, -5.0, 5.0 };
            int r = A->configure(g, at_guard(&c, sizeof c));
            printf("cfg %d -> %.2f %.2f %.2f\n", r, A->apply(g, 1.0), A->apply(g, 10.0), A->apply(g, -10.0));
            GeoConfig off = { sizeof off, 0.5, 0.0, 1.0, -1.0 };
            r = A->configure(g, &off);
            double y1 = A->apply(g, 100.0), y2 = A->apply(g, -100.0);
            printf("min>max %d -> %.2f %.2f calls=%llu\n", r, y1, y2, (unsigned long long)A->calls(g));
            A->destroy(g); A->destroy(NULL);
            printf("null: %d %d nan=%d calls=%llu\n", A->configure(NULL, &c), A->configure(g = A->create(), NULL), isnan(A->apply(NULL, 1.0)),
                   (unsigned long long)A->calls(NULL));
            A->destroy(g);
        } else if (!strcmp(cmd, "v1")) {
            const GeoApi *A = geo_get_api(2);
            Geo *g = A->create();
            GeoConfig c2 = { sizeof c2, 1.0, 0.0, 0.0, 1.0 };
            A->configure(g, &c2);
            printf("v2 clamp on: %.2f\n", A->apply(g, 7.0));
            struct { uint32_t size; double scale, offset; } v1 = { (uint32_t)GEO_CONFIG_V1_SIZE, 3.0, -2.0 };
            int r = A->configure(g, at_guard(&v1, GEO_CONFIG_V1_SIZE));
            printf("v1 cfg %d -> %.2f %.2f (clamp off)\n", r, A->apply(g, 7.0), A->apply(g, -7.0));
            v1.size = (uint32_t)GEO_CONFIG_V1_SIZE - 1;
            r = A->configure(g, at_guard(&v1, sizeof v1));
            printf("short %d -> %.2f\n", r, A->apply(g, 1.0));
            A->destroy(g);
        } else if (!strcmp(cmd, "future")) {
            const GeoApi *A = geo_get_api(2);
            Geo *g = A->create();
            GeoConfigV3 c3 = { sizeof c3, 2.0, 0.0, -1.0, 3.0, 42.0 };
            int r = A->configure(g, (const GeoConfig *)at_guard(&c3, sizeof c3));
            printf("v3 cfg %d -> %.2f %.2f\n", r, A->apply(g, 1.0), A->apply(g, 5.0));
            GeoConfig bad[] = { { sizeof(GeoConfig), 0.0, 1.0, 0, 1 }, { sizeof(GeoConfig), NAN, 1.0, 0, 1 },
                                { sizeof(GeoConfig), 1.0, INFINITY, 0, 1 }, { sizeof(GeoConfig), 1.0, 0.0, NAN, 1 },
                                { sizeof(GeoConfig), 1.0, 0.0, 0, NAN } };
            for (int i = 0; i < 5; i++) printf("%d ", A->configure(g, &bad[i]));
            double y1 = A->apply(g, 1.0), y2 = A->apply(g, 5.0);
            printf("-> unchanged %.2f %.2f calls=%llu\n", y1, y2, (unsigned long long)A->calls(g));
            A->destroy(g);
        } else if (!strcmp(cmd, "many")) {
            const GeoApi *A = geo_get_api(2);
            enum { K = 2000 };
            static Geo *gs[K];
            double total = 0;
            for (int i = 0; i < K; i++) {
                gs[i] = A->create();
                GeoConfig c = { sizeof c, 1.0 + i % 7, (double)(i % 13) - 6.0, -50.0, 50.0 + i % 5 };
                if (i % 3 == 0) { struct { uint32_t size; double s, o; } v1 = { (uint32_t)GEO_CONFIG_V1_SIZE, c.scale, c.offset };
                                  A->configure(gs[i], at_guard(&v1, GEO_CONFIG_V1_SIZE)); }
                else A->configure(gs[i], &c);
            }
            for (int r = 0; r < 500; r++) for (int i = 0; i < K; i++) total += A->apply(gs[i], (double)((r * 31 + i) % 41) - 20.0);
            unsigned long long calls = 0;
            for (int i = 0; i < K; i++) { calls += A->calls(gs[i]); A->destroy(gs[i]); }
            printf("total %.1f calls %llu\n", total, calls);
        }
    }
    return 0;
}
```

## Tests
=== sample
api
v2
---
v2 ok same=1 abi=2.1 | v1 NULL | v3 NULL
default 3.00 -1.50
cfg 0 -> 3.00 5.00 -5.00
min>max 0 -> 50.00 -50.00 calls=7
null: -1 -1 nan=1 calls=0
=== hidden
v1
---
v2 clamp on: 1.00
v1 cfg 0 -> 19.00 -23.00 (clamp off)
short -2 -> 1.00
=== hidden
future
---
v3 cfg 1 -> 2.00 3.00
-3 -3 -3 -3 -3 -> unchanged 2.00 3.00 calls=4
=== hidden
many
---
total 212278.0 calls 1000000

## Hints
- Read `cfg->size` first. It's always present, because every version starts with it.
- Validate into locals, then commit to `*g` only when everything is valid.
- Only touch `cfg->clamp_min` and `clamp_max` when `cfg->size >= sizeof(GeoConfig)`.
- `isfinite` and `isnan` come from `<math.h>`. The judge links `-lm`.
- Make the table `static const GeoApi` at file scope, and every implementation function `static`. Only `geo_get_api` is exported, which mirrors `-fvisibility=hidden` with a single public symbol.

## Solution: geo.h
```c
#ifndef GEO_H
#define GEO_H
#include <stddef.h>
#include <stdint.h>

#define GEO_ABI_MAJOR 2u
#define GEO_ABI_MINOR 1u

typedef struct Geo Geo;

typedef struct {
    uint32_t size;
    double scale, offset;
    double clamp_min, clamp_max;
} GeoConfig;
#define GEO_CONFIG_V1_SIZE offsetof(GeoConfig, clamp_min)

typedef struct {
    uint32_t abi_major, abi_minor;
    Geo *(*create)(void);
    void (*destroy)(Geo *g);
    int (*configure)(Geo *g, const GeoConfig *cfg);
    double (*apply)(Geo *g, double x);
    uint64_t (*calls)(const Geo *g);
} GeoApi;

const GeoApi *geo_get_api(uint32_t abi_major);
#endif
```

## Solution: geo.c
```c
#include "geo.h"
#include <math.h>
#include <stdbool.h>
#include <stdlib.h>

struct Geo {                      /* private: free to change without breaking clients */
    double scale, offset, lo, hi;
    bool clamp;
    uint64_t calls;
};

static Geo *geo_create(void) {
    Geo *g = malloc(sizeof *g);
    if (g == NULL) return NULL;
    *g = (Geo){ .scale = 1.0, .offset = 0.0, .lo = 0.0, .hi = 0.0, .clamp = false, .calls = 0 };
    return g;
}

static void geo_destroy(Geo *g) { free(g); }          /* free(NULL) is a no-op */

static int geo_configure(Geo *g, const GeoConfig *cfg) {
    if (g == NULL || cfg == NULL) return -1;
    const uint32_t size = cfg->size;                   /* the one field every version has */
    if (size < GEO_CONFIG_V1_SIZE) return -2;
    Geo next = *g;
    if (!isfinite(cfg->scale) || cfg->scale == 0.0 || !isfinite(cfg->offset)) return -3;
    next.scale = cfg->scale;
    next.offset = cfg->offset;
    next.clamp = false;
    if (size >= sizeof(GeoConfig)) {                   /* caller's struct contains the v2 fields */
        if (isnan(cfg->clamp_min) || isnan(cfg->clamp_max)) return -3;
        next.lo = cfg->clamp_min;
        next.hi = cfg->clamp_max;
        next.clamp = next.lo <= next.hi;
    }
    next.calls = g->calls;
    *g = next;                                         /* commit atomically after validation */
    return size > sizeof(GeoConfig) ? 1 : 0;
}

static double geo_apply(Geo *g, double x) {
    if (g == NULL) return NAN;
    g->calls++;
    double y = g->scale * x + g->offset;
    if (g->clamp) y = y < g->lo ? g->lo : (y > g->hi ? g->hi : y);
    return y;
}

static uint64_t geo_calls(const Geo *g) { return g ? g->calls : 0u; }

static const GeoApi GEO_API_V2 = {
    GEO_ABI_MAJOR, GEO_ABI_MINOR, geo_create, geo_destroy, geo_configure, geo_apply, geo_calls,
};

const GeoApi *geo_get_api(uint32_t abi_major) {       /* the single exported symbol */
    return abi_major == GEO_ABI_MAJOR ? &GEO_API_V2 : NULL;
}
```

## Solution
- **An opaque handle** (`typedef struct Geo Geo;`) keeps the object's layout out of the ABI. `geo.c` can add fields in version 3 and old binaries keep working, because they only ever hold a pointer.
- **A size-versioned struct** is the Win32 and Vulkan technique for structs that *must* cross the boundary. The caller stamps `sizeof` as it was compiled, and the library reads only the fields that fit: v1 callers get v1 behaviour, and future callers get their known prefix honoured, with a return code saying that extensions were ignored. The guard page proves the library never reads past the caller's struct.
- **Validate, then commit**: an invalid config leaves the object exactly as it was, so a bad parameter upload can't leave a half-applied calibration on a running robot.
- **One exported entry point** returning a `static const` function table: `dlsym(h, "geo_get_api")` gives a whole, version-checked interface. New functions are appended to the table (bumping `abi_minor`), and a major-version mismatch is refused cleanly instead of crashing. This is the pattern behind ROS 2 pluginlib, Vulkan and many game engines.
- **`static` everywhere else** means internal functions don't leak into the symbol table. With a shared build you'd also compile with `-fvisibility=hidden` and mark `geo_get_api` with `__attribute__((visibility("default")))`.
