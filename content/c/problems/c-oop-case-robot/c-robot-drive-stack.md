---
id: c-robot-drive-stack
title: "Case Study: Driver Interfaces and a Drive Controller (Multi-File)"
difficulty: Expert
order: 1
tags: OOP in C, case study, vtables, HAL, dependency inversion, fail-safe, simulation, multi-file
time_limit: 4
---
## Statement
Build the software skeleton of a differential-drive robot from the case-study lesson. The **interfaces** (`hal.h`) and the **controller API** (`drive.h`) are given. You implement:
- **`drivers.c`**: two concrete drivers behind the HAL vtables.
- **`drive.c`**: the opaque controller, which talks to hardware **only through the interfaces**.

**`sim_motor_create(name, max_vel, max_acc)`**: NULL unless both limits are > 0. `kind` is `"sim-motor"`.
- `set_velocity` returns -1 for NaN. Otherwise it clamps the command to ±max_vel and returns 0.
- `update(dt)` moves the velocity toward the command by at most `max_acc·dt`.
- `velocity` returns the current velocity.

**`scripted_range_create(name, script, n)`**: NULL for an empty script. `kind` is `"scripted-range"`.
- Each `read` returns the next script entry. After the end, it keeps returning the last entry.
- A **NaN entry is a failed read** (return -1, leave `*m` untouched).
- The sensor must **copy** the script.

**Drive controller**
- `drive_create(l, r, front, cruise, stop, slow)` returns NULL if any pointer is NULL, or unless `cruise > 0` and `0 < stop < slow`. The drivers are **borrowed**: `drive_destroy` must not destroy them.

`drive_step(dt)` does exactly this, in order:
1. Read the front sensor. A failed read, or a negative distance, counts as a failure.
2. **Three consecutive failures** latch `DRIVE_FAULT`. While faulted, good readings don't change the state, but they still reset the failure count. Otherwise a good reading sets:
   - `STOP` if `d <= stop`;
   - `SLOW` if `d < slow`;
   - `OK` otherwise.
3. Compute the target:
   - `OK`: the cruise speed;
   - `SLOW`: `cruise·(d - stop)/(slow - stop)`;
   - `STOP` or `FAULT`: 0.
   A failed read keeps the current non-fault state and reuses the last valid distance.
4. Command both motors with the target, then `update(dt)` both.

`drive_reset` clears the fault and the failure count (the state becomes `OK`). `drive_set_cruise(v)` returns -1 unless `v > 0`. `drive_target` returns the last commanded target.

## Starter: hal.h
```c
#ifndef HAL_H
#define HAL_H
#include <stddef.h>

typedef struct Motor Motor;
typedef struct {
    const char *kind;
    int    (*set_velocity)(Motor *m, double rad_s);
    double (*velocity)(const Motor *m);
    void   (*update)(Motor *m, double dt);
    void   (*destroy)(Motor *m);
} MotorOps;
struct Motor { const MotorOps *ops; const char *name; };

typedef struct RangeSensor RangeSensor;
typedef struct {
    const char *kind;
    int  (*read)(RangeSensor *s, double *meters);
    void (*destroy)(RangeSensor *s);
} RangeOps;
struct RangeSensor { const RangeOps *ops; const char *name; };

Motor       *sim_motor_create(const char *name, double max_vel, double max_acc);
RangeSensor *scripted_range_create(const char *name, const double *script, size_t n);
#endif
```

## Starter: drive.h
```c
#ifndef DRIVE_H
#define DRIVE_H
#include "hal.h"

typedef enum { DRIVE_OK, DRIVE_SLOW, DRIVE_STOP, DRIVE_FAULT } DriveState;
typedef struct DriveController DriveController;

DriveController *drive_create(Motor *left, Motor *right, RangeSensor *front,
                              double cruise, double stop_dist, double slow_dist);
void       drive_destroy(DriveController *c);
void       drive_step(DriveController *c, double dt);
DriveState drive_state(const DriveController *c);
double     drive_target(const DriveController *c);
void       drive_reset(DriveController *c);
int        drive_set_cruise(DriveController *c, double v);
#endif
```

## Starter: drivers.c
```c
#include "hal.h"
#include <stdlib.h>

Motor *sim_motor_create(const char *name, double max_vel, double max_acc) { (void)name; (void)max_vel; (void)max_acc; return NULL; }
RangeSensor *scripted_range_create(const char *name, const double *script, size_t n) { (void)name; (void)script; (void)n; return NULL; }
```

## Starter: drive.c
```c
#include "drive.h"
#include <stdlib.h>

struct DriveController { Motor *l, *r; RangeSensor *f; double cruise, stop, slow, target; DriveState st; };

DriveController *drive_create(Motor *left, Motor *right, RangeSensor *front, double cruise, double stop_dist, double slow_dist) {
    DriveController *c = malloc(sizeof *c);
    *c = (DriveController){ left, right, front, cruise, stop_dist, slow_dist, 0, DRIVE_OK };
    return c;
}
void drive_destroy(DriveController *c) { free(c); }
void drive_step(DriveController *c, double dt) {
    (void)dt;
    c->target = c->cruise;
    c->l->ops->set_velocity(c->l, c->target);
    c->r->ops->set_velocity(c->r, c->target);
}
DriveState drive_state(const DriveController *c) { return c->st; }
double drive_target(const DriveController *c) { return c->target; }
void drive_reset(DriveController *c) { (void)c; }
int drive_set_cruise(DriveController *c, double v) { c->cruise = v; return 0; }
```

## Driver: main.c
```c
#include "drive.h"
#include <math.h>
#include <stdio.h>
#include <string.h>

static const char *SN[] = {"OK", "SLOW", "STOP", "FAULT"};

int main(void) {
    char cmd[32];
    while (scanf("%31s", cmd) == 1) {
        if (!strcmp(cmd, "drivers")) {
            Motor *m = sim_motor_create("m", 2.0, 4.0);
            printf("kind %s name %s\n", m->ops->kind, m->name);
            printf("nan rejected %d, clamp ok %d\n", m->ops->set_velocity(m, NAN), m->ops->set_velocity(m, 10));
            for (int i = 0; i < 6; i++) { m->ops->update(m, 0.1); printf(" %.2f", m->ops->velocity(m)); }
            m->ops->set_velocity(m, -1); for (int i = 0; i < 4; i++) { m->ops->update(m, 0.25); printf(" %.2f", m->ops->velocity(m)); }
            printf("\ninvalid motor: %s %s\n", sim_motor_create("x", 0, 1) ? "?" : "NULL", sim_motor_create("x", 1, -1) ? "?" : "NULL");
            double script[] = {1.5, NAN, 0.25};
            RangeSensor *r = scripted_range_create("front", script, 3);
            script[0] = 99;                                      /* sensor must own a copy */
            for (int i = 0; i < 5; i++) { double d = -1; int rc = r->ops->read(r, &d); printf(" [%d %.2f]", rc, d); }
            printf("\nempty script: %s\n", scripted_range_create("e", script, 0) ? "?" : "NULL");
            m->ops->destroy(m); r->ops->destroy(r);
        } else if (!strcmp(cmd, "drive")) {
            Motor *l = sim_motor_create("l", 10, 20), *rm = sim_motor_create("r", 10, 20);
            double script[] = {5, 5, 0.8, NAN, 0.65, 0.3, 0.2, 2.0, NAN, 2.0, NAN, NAN, NAN, 3.0, 3.0};
            RangeSensor *f = scripted_range_create("front", script, sizeof script / sizeof *script);
            printf("bad create: %s %s %s\n", drive_create(NULL, rm, f, 1, 0.3, 1) ? "?" : "NULL",
                   drive_create(l, rm, f, 1, 1.0, 0.3) ? "?" : "NULL", drive_create(l, rm, f, 0, 0.3, 1) ? "?" : "NULL");
            DriveController *c = drive_create(l, rm, f, 4.0, 0.3, 1.0);
            for (int i = 0; i < 17; i++) {
                if (i == 15) { drive_reset(c); printf("  reset\n"); }
                drive_step(c, 0.1);
                printf("t%-2d %-5s target %.3f vel %.3f %.3f\n", i, SN[drive_state(c)], drive_target(c) + 0.0, l->ops->velocity(l) + 0.0, rm->ops->velocity(rm) + 0.0);
            }
            printf("set cruise %d %d\n", drive_set_cruise(c, -1), drive_set_cruise(c, 6));
            drive_step(c, 0.1); printf("after cruise change: %s %.3f\n", SN[drive_state(c)], drive_target(c));
            drive_destroy(c);
            printf("drivers still alive: %.3f\n", l->ops->velocity(l));
            l->ops->destroy(l); rm->ops->destroy(rm); f->ops->destroy(f);
        } else if (!strcmp(cmd, "sim")) {
            enum { N = 20000 };
            static double script[N];
            unsigned x = 3;
            for (int i = 0; i < N; i++) {
                x = x * 1103515245u + 12345u;
                script[i] = (x >> 16) % 1000 == 0 ? NAN : 0.1 + ((x >> 8) % 400) / 100.0;
            }
            Motor *l = sim_motor_create("l", 6, 8), *r = sim_motor_create("r", 6, 8);
            RangeSensor *f = scripted_range_create("f", script, N);
            DriveController *c = drive_create(l, r, f, 5.0, 0.4, 1.5);
            int counts[4] = {0}; double dist = 0;
            for (int i = 0; i < N; i++) {
                drive_step(c, 0.01);
                if (drive_state(c) == DRIVE_FAULT && i % 50 == 0) drive_reset(c);
                counts[drive_state(c)]++;
                dist += 0.5 * (l->ops->velocity(l) + r->ops->velocity(r)) * 0.01 * 0.05;
            }
            printf("OK %d SLOW %d STOP %d FAULT %d distance %.4f m\n", counts[0], counts[1], counts[2], counts[3], dist);
            drive_destroy(c); l->ops->destroy(l); r->ops->destroy(r); f->ops->destroy(f);
        }
    }
    return 0;
}
```

## Tests
=== sample
drivers
---
kind sim-motor name m
nan rejected -1, clamp ok 0
 0.40 0.80 1.20 1.60 2.00 2.00 1.00 0.00 -1.00 -1.00
invalid motor: NULL NULL
 [0 1.50] [-1 -1.00] [0 0.25] [0 0.25] [0 0.25]
empty script: NULL
=== hidden
drive
---
bad create: NULL NULL NULL
t0  OK    target 4.000 vel 2.000 2.000
t1  OK    target 4.000 vel 4.000 4.000
t2  SLOW  target 2.857 vel 2.857 2.857
t3  SLOW  target 2.857 vel 2.857 2.857
t4  SLOW  target 2.000 vel 2.000 2.000
t5  STOP  target 0.000 vel 0.000 0.000
t6  STOP  target 0.000 vel 0.000 0.000
t7  OK    target 4.000 vel 2.000 2.000
t8  OK    target 4.000 vel 4.000 4.000
t9  OK    target 4.000 vel 4.000 4.000
t10 OK    target 4.000 vel 4.000 4.000
t11 OK    target 4.000 vel 4.000 4.000
t12 FAULT target 0.000 vel 2.000 2.000
t13 FAULT target 0.000 vel 0.000 0.000
t14 FAULT target 0.000 vel 0.000 0.000
  reset
t15 OK    target 4.000 vel 2.000 2.000
t16 OK    target 4.000 vel 4.000 4.000
set cruise -1 0
after cruise change: OK 6.000
drivers still alive: 6.000
=== hidden
sim
---
OK 13064 SLOW 5407 STOP 1529 FAULT 0 distance 49.0801 m

## Hints
- Concrete driver structs embed the interface struct **first** (`typedef struct { Motor base; double cmd, vel, max_vel, max_acc; } SimMotor;`). Each driver has a `static const` ops table, and its functions downcast `self`.
- Keep the **last valid distance** in a local that's initialised by the read. On a failed read in `SLOW`, use the stored value. The simplest way is to keep `d` in the controller struct.
- A NaN check needs `<math.h>`: `isnan(v)`.
- The controller must call **only** `ops->...` functions, never driver internals. That's what lets the judge swap in the scripted sensor.

## Solution: hal.h
```c
#ifndef HAL_H
#define HAL_H
#include <stddef.h>

typedef struct Motor Motor;
typedef struct {
    const char *kind;
    int    (*set_velocity)(Motor *m, double rad_s);
    double (*velocity)(const Motor *m);
    void   (*update)(Motor *m, double dt);
    void   (*destroy)(Motor *m);
} MotorOps;
struct Motor { const MotorOps *ops; const char *name; };

typedef struct RangeSensor RangeSensor;
typedef struct {
    const char *kind;
    int  (*read)(RangeSensor *s, double *meters);
    void (*destroy)(RangeSensor *s);
} RangeOps;
struct RangeSensor { const RangeOps *ops; const char *name; };

Motor       *sim_motor_create(const char *name, double max_vel, double max_acc);
RangeSensor *scripted_range_create(const char *name, const double *script, size_t n);
#endif
```

## Solution: drive.h
```c
#ifndef DRIVE_H
#define DRIVE_H
#include "hal.h"

typedef enum { DRIVE_OK, DRIVE_SLOW, DRIVE_STOP, DRIVE_FAULT } DriveState;
typedef struct DriveController DriveController;

DriveController *drive_create(Motor *left, Motor *right, RangeSensor *front,
                              double cruise, double stop_dist, double slow_dist);
void       drive_destroy(DriveController *c);
void       drive_step(DriveController *c, double dt);
DriveState drive_state(const DriveController *c);
double     drive_target(const DriveController *c);
void       drive_reset(DriveController *c);
int        drive_set_cruise(DriveController *c, double v);
#endif
```

## Solution: drivers.c
```c
#include "hal.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

/* ---- simulated motor: clamped command, acceleration-limited response ---- */
typedef struct { Motor base; double cmd, vel, max_vel, max_acc; } SimMotor;

static int sim_set(Motor *m, double v) {
    SimMotor *s = (SimMotor *)m;
    if (isnan(v)) return -1;
    s->cmd = v > s->max_vel ? s->max_vel : v < -s->max_vel ? -s->max_vel : v;
    return 0;
}
static double sim_vel(const Motor *m) { return ((const SimMotor *)m)->vel; }
static void sim_update(Motor *m, double dt) {
    SimMotor *s = (SimMotor *)m;
    double dv = s->cmd - s->vel, lim = s->max_acc * dt;
    s->vel += dv > lim ? lim : dv < -lim ? -lim : dv;
}
static void sim_destroy(Motor *m) { free(m); }
static const MotorOps SIM_MOTOR_OPS = { "sim-motor", sim_set, sim_vel, sim_update, sim_destroy };

Motor *sim_motor_create(const char *name, double max_vel, double max_acc) {
    if (!(max_vel > 0) || !(max_acc > 0)) return NULL;
    SimMotor *s = malloc(sizeof *s);
    if (!s) return NULL;
    *s = (SimMotor){ .base = { &SIM_MOTOR_OPS, name }, .max_vel = max_vel, .max_acc = max_acc };
    return &s->base;
}

/* ---- scripted range sensor: replays a sequence, NaN = failure, holds the last entry ---- */
typedef struct { RangeSensor base; double *script; size_t n, i; } Scripted;

static int scripted_read(RangeSensor *r, double *out) {
    Scripted *s = (Scripted *)r;
    double v = s->script[s->i < s->n ? s->i : s->n - 1];
    if (s->i < s->n) s->i++;
    if (isnan(v)) return -1;
    *out = v;
    return 0;
}
static void scripted_destroy(RangeSensor *r) { Scripted *s = (Scripted *)r; free(s->script); free(s); }
static const RangeOps SCRIPTED_OPS = { "scripted-range", scripted_read, scripted_destroy };

RangeSensor *scripted_range_create(const char *name, const double *script, size_t n) {
    if (!script || n == 0) return NULL;
    Scripted *s = malloc(sizeof *s);
    double *copy = malloc(n * sizeof *copy);
    if (!s || !copy) { free(s); free(copy); return NULL; }
    memcpy(copy, script, n * sizeof *copy);                 /* own a copy: caller's array may go away */
    *s = (Scripted){ .base = { &SCRIPTED_OPS, name }, .script = copy, .n = n };
    return &s->base;
}
```

## Solution: drive.c
```c
#include "drive.h"
#include <stdlib.h>

struct DriveController {
    Motor *left, *right;          /* borrowed: owned by the composition root */
    RangeSensor *front;
    double cruise, stop_dist, slow_dist, target;
    double last_d;                /* last valid distance, reused when a read fails */
    int failures;
    DriveState state;
};

DriveController *drive_create(Motor *left, Motor *right, RangeSensor *front,
                              double cruise, double stop_dist, double slow_dist) {
    if (!left || !right || !front || !(cruise > 0) || !(stop_dist > 0) || !(stop_dist < slow_dist)) return NULL;
    DriveController *c = malloc(sizeof *c);
    if (!c) return NULL;
    *c = (DriveController){ left, right, front, cruise, stop_dist, slow_dist, 0.0, slow_dist, 0, DRIVE_OK };
    return c;
}

void drive_destroy(DriveController *c) { free(c); }   /* never destroys borrowed drivers */

void drive_step(DriveController *c, double dt) {
    double d = 0;
    int ok = c->front->ops->read(c->front, &d) == 0 && d >= 0;
    if (!ok) {
        if (++c->failures >= 3) c->state = DRIVE_FAULT;   /* latched until drive_reset */
    } else {
        c->failures = 0;
        c->last_d = d;
        if (c->state != DRIVE_FAULT)
            c->state = d <= c->stop_dist ? DRIVE_STOP : d < c->slow_dist ? DRIVE_SLOW : DRIVE_OK;
    }
    switch (c->state) {
    case DRIVE_OK:    c->target = c->cruise; break;
    case DRIVE_SLOW:  c->target = c->cruise * (c->last_d - c->stop_dist) / (c->slow_dist - c->stop_dist); break;
    default:          c->target = 0.0; break;               /* STOP and FAULT */
    }
    c->left->ops->set_velocity(c->left, c->target);
    c->right->ops->set_velocity(c->right, c->target);
    c->left->ops->update(c->left, dt);
    c->right->ops->update(c->right, dt);
}

DriveState drive_state(const DriveController *c) { return c->state; }
double drive_target(const DriveController *c) { return c->target; }

void drive_reset(DriveController *c) {
    c->failures = 0;
    c->state = DRIVE_OK;
}

int drive_set_cruise(DriveController *c, double v) {
    if (!(v > 0)) return -1;
    c->cruise = v;
    return 0;
}
```

## Solution
- **Dependency inversion**: `drive.c` includes only the interface headers and calls `ops` functions. The same controller would run against CAN motors and a real lidar by writing two new drivers, and against scripted fakes in tests, which is what the judge does.
- **Ownership is explicit**: the controller borrows its drivers, the composition root (`main`) creates and destroys them, and the scripted sensor copies its script, so a caller's temporary array can't dangle.
- **Fail-safe by design**: three consecutive bad readings latch `FAULT`, the motors are commanded to 0, and only an explicit `drive_reset` leaves the safe state. A flapping sensor can't make the robot lurch forward.
- **The simulated motor** models command clamping and acceleration limits, so the trace shows realistic ramping rather than instant velocity jumps, and controller bugs show up in simulation first.
- **Pure, small and testable**: the safety logic is about 25 lines, free of I/O, and fully determined by its inputs, which is exactly what reviewers and certification want.
