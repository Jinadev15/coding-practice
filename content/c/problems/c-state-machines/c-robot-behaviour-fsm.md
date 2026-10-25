---
id: c-robot-behaviour-fsm
title: A Robot Behaviour State Machine
difficulty: Medium
order: 1
tags: state machine, table-driven, guards, timeouts, fail-safe
time_limit: 2
---
## Statement
Implement the behaviour layer of a cleaning robot as a deterministic FSM. Time is an **input** (`now_ms`, a free-running `uint32_t` millisecond counter that may **wrap around**).

```c
typedef enum { ST_IDLE, ST_EXPLORE, ST_AVOID, ST_DOCK, ST_CHARGE, ST_FAULT, ST_COUNT } State;
typedef enum { EV_START, EV_OBSTACLE, EV_CLEAR, EV_BATTERY_LOW, EV_DOCKED,
               EV_CHARGED, EV_FAULT, EV_RESET, EV_TICK, EV_COUNT } Event;
```

Rules, applied in this order:
1. A `state` that isn't a valid `State` (memory corruption): **any** event moves to `FAULT`.
2. An event that isn't a valid `Event` is ignored.
3. `EV_FAULT` from any state except `FAULT` moves to `FAULT`.
4. Per-state transitions:

| State | Event → next |
|---|---|
| IDLE | START → EXPLORE |
| EXPLORE | OBSTACLE → AVOID, BATTERY_LOW → DOCK |
| AVOID | CLEAR → EXPLORE, BATTERY_LOW → DOCK, TICK → EXPLORE **if** at least 3000 ms have passed since entering AVOID (a timeout) |
| DOCK | DOCKED → CHARGE |
| CHARGE | CHARGED → IDLE |
| FAULT | RESET → IDLE **only if** at least 1000 ms have passed since entering FAULT |

5. Anything else is ignored: no change, and the entry time is untouched.

Implement:
- `void robot_init(Robot *r, uint32_t now_ms)`: starts in IDLE, entered at `now_ms`.
- `int robot_handle(Robot *r, Event e, uint32_t now_ms)`: returns 1 if the state changed, 0 otherwise. Record the entry time on every change.
- `int robot_motors(const Robot *r)`: the Moore output, 1 in EXPLORE, AVOID and DOCK, else 0.

Define `Robot` yourself, but it must have a member `State state;` (the judge reads it, and corrupts it in one test). Elapsed time must be computed correctly across the `uint32_t` wrap at 2³² ms (about 49.7 days of uptime).

## Starter
```c
#include <stdint.h>

typedef enum { ST_IDLE, ST_EXPLORE, ST_AVOID, ST_DOCK, ST_CHARGE, ST_FAULT, ST_COUNT } State;
typedef enum { EV_START, EV_OBSTACLE, EV_CLEAR, EV_BATTERY_LOW, EV_DOCKED,
               EV_CHARGED, EV_FAULT, EV_RESET, EV_TICK, EV_COUNT } Event;

typedef struct {
    State state;
    uint32_t entered_ms;
} Robot;

void robot_init(Robot *r, uint32_t now_ms) { r->state = ST_IDLE; r->entered_ms = now_ms; }

int robot_handle(Robot *r, Event e, uint32_t now_ms) {
    State old = r->state;
    switch (r->state) {
    case ST_IDLE: if (e == EV_START) r->state = ST_EXPLORE; break;
    case ST_EXPLORE: if (e == EV_OBSTACLE) r->state = ST_AVOID; break;
    default: break;
    }
    (void)now_ms;
    return r->state != old;
}

int robot_motors(const Robot *r) { return r->state == ST_EXPLORE; }
```

## Driver
```c
#include <stdio.h>
#include <string.h>

static const char *SN[] = {"IDLE", "EXPLORE", "AVOID", "DOCK", "CHARGE", "FAULT"};
static const char *EN[] = {"START", "OBSTACLE", "CLEAR", "BATTERY_LOW", "DOCKED", "CHARGED", "FAULT", "RESET", "TICK"};
static const char *sname(int s) { return (s >= 0 && s < ST_COUNT) ? SN[s] : "CORRUPT"; }
static int ev_of(const char *w) { for (int i = 0; i < EV_COUNT; i++) if (!strcmp(w, EN[i])) return i; return 42; }

int main(void) {
    char w[32]; unsigned long long t;
    Robot r; int inited = 0;
    while (scanf("%31s", w) == 1) {
        if (!strcmp(w, "gen")) {
            unsigned long long n, seed; if (scanf("%llu %llu", &n, &seed) != 2) return 1;
            uint32_t now = 4294000000u, x = (uint32_t)seed;
            robot_init(&r, now);
            unsigned long long changes = 0, motor_ms = 0, h = 1469598103934665603ull, visits[ST_COUNT] = {0};
            for (unsigned long long i = 0; i < n; i++) {
                x ^= x << 13; x ^= x >> 17; x ^= x << 5;
                uint32_t dt = x % 700; x ^= x << 13; x ^= x >> 17; x ^= x << 5;
                int e = (int)(x % 100); e = e < 40 ? EV_TICK : e < 95 ? (e % 8) : (e == 99 ? 42 : EV_FAULT);
                if (robot_motors(&r)) motor_ms += dt;
                now += dt;
                if (robot_handle(&r, (Event)e, now)) { changes++; visits[r.state]++; h = (h ^ (uint64_t)r.state) * 1099511628211ull; h = (h ^ now) * 1099511628211ull; }
            }
            printf("changes %llu final %s motor_ms %llu hash %016llx\n", changes, sname(r.state), motor_ms, h);
            for (int s = 0; s < ST_COUNT; s++) printf("%s=%llu ", SN[s], visits[s]);
            printf("\n");
            continue;
        }
        if (scanf("%llu", &t) != 1) return 1;
        uint32_t now = (uint32_t)t;
        if (!strcmp(w, "INIT")) { robot_init(&r, now); inited = 1; printf("%10u init %s motors=%d\n", now, sname(r.state), robot_motors(&r)); continue; }
        if (!inited) return 1;
        if (!strcmp(w, "CORRUPT")) { r.state = (State)77; printf("%10u state corrupted\n", now); continue; }
        int before = (int)r.state, e = ev_of(w);
        int ch = robot_handle(&r, (Event)e, now);
        if (ch) printf("%10u %-11s %s -> %s motors=%d\n", now, w, sname(before), sname(r.state), robot_motors(&r));
        else printf("%10u %-11s ignored in %s\n", now, w, sname(r.state));
    }
    return 0;
}
```

## Tests
=== sample
INIT 0
START 10
OBSTACLE 500
CLEAR 900
OBSTACLE 1000
TICK 3000
TICK 4000
BATTERY_LOW 4100
OBSTACLE 4200
DOCKED 9000
BATTERY_LOW 9100
CHARGED 20000
---
         0 init IDLE motors=0
        10 START       IDLE -> EXPLORE motors=1
       500 OBSTACLE    EXPLORE -> AVOID motors=1
       900 CLEAR       AVOID -> EXPLORE motors=1
      1000 OBSTACLE    EXPLORE -> AVOID motors=1
      3000 TICK        ignored in AVOID
      4000 TICK        AVOID -> EXPLORE motors=1
      4100 BATTERY_LOW EXPLORE -> DOCK motors=1
      4200 OBSTACLE    ignored in DOCK
      9000 DOCKED      DOCK -> CHARGE motors=0
      9100 BATTERY_LOW ignored in CHARGE
     20000 CHARGED     CHARGE -> IDLE motors=0
=== hidden
INIT 100
FAULT 150
START 200
RESET 900
RESET 1150
START 1200
FAULT 1300
FAULT 1400
RESET 2299
TICK 2300
RESET 2300
BOGUS 2400
START 2500
---
       100 init IDLE motors=0
       150 FAULT       IDLE -> FAULT motors=0
       200 START       ignored in FAULT
       900 RESET       ignored in FAULT
      1150 RESET       FAULT -> IDLE motors=0
      1200 START       IDLE -> EXPLORE motors=1
      1300 FAULT       EXPLORE -> FAULT motors=0
      1400 FAULT       ignored in FAULT
      2299 RESET       ignored in FAULT
      2300 TICK        ignored in FAULT
      2300 RESET       FAULT -> IDLE motors=0
      2400 BOGUS       ignored in IDLE
      2500 START       IDLE -> EXPLORE motors=1
=== hidden
INIT 4294966000
START 4294966100
OBSTACLE 4294967000
TICK 1000
TICK 2703
TICK 2704
OBSTACLE 2800
CORRUPT 2900
TICK 3000
RESET 3999
RESET 4000
---
4294966000 init IDLE motors=0
4294966100 START       IDLE -> EXPLORE motors=1
4294967000 OBSTACLE    EXPLORE -> AVOID motors=1
      1000 TICK        ignored in AVOID
      2703 TICK        ignored in AVOID
      2704 TICK        AVOID -> EXPLORE motors=1
      2800 OBSTACLE    EXPLORE -> AVOID motors=1
      2900 state corrupted
      3000 TICK        CORRUPT -> FAULT motors=0
      3999 RESET       ignored in FAULT
      4000 RESET       FAULT -> IDLE motors=0
=== hidden
gen 2000000 7
---
changes 198440 final IDLE motor_ms 75771476 hash 82f594e435cc18af
IDLE=72550 EXPLORE=31073 AVOID=8638 DOCK=11013 CHARGE=4266 FAULT=70900 
=== hidden
gen 2000000 99991
---
changes 197154 final IDLE motor_ms 75588527 hash 47adf7c8590c52a5
IDLE=72004 EXPLORE=30972 AVOID=8619 DOCK=10947 CHARGE=4333 FAULT=70279 

## Hints
- `uint32_t elapsed = now_ms - r->entered_ms;` is correct across the wrap, because unsigned subtraction is modulo 2³².
- Check validity first: `(unsigned)r->state >= ST_COUNT` and `(unsigned)e >= EV_COUNT`.
- A table `static const State next[ST_COUNT][EV_COUNT]` covers the unconditional transitions. Handle the two guarded ones (the AVOID timeout and the FAULT reset hold-off) explicitly.
- Only update `entered_ms` when the state actually changes.

## Solution
```c
#include <stdint.h>

typedef enum { ST_IDLE, ST_EXPLORE, ST_AVOID, ST_DOCK, ST_CHARGE, ST_FAULT, ST_COUNT } State;
typedef enum { EV_START, EV_OBSTACLE, EV_CLEAR, EV_BATTERY_LOW, EV_DOCKED,
               EV_CHARGED, EV_FAULT, EV_RESET, EV_TICK, EV_COUNT } Event;

typedef struct {
    State state;
    uint32_t entered_ms;
} Robot;

#define AVOID_TIMEOUT_MS 3000u
#define FAULT_HOLD_MS    1000u
#define S_ ST_COUNT                       /* "no transition" marker */

/* unconditional transitions; guarded ones are handled in code */
static const State next_state[ST_COUNT][EV_COUNT] = {
    /*            START       OBSTACLE  CLEAR       BATT_LOW  DOCKED     CHARGED  FAULT     RESET  TICK */
    [ST_IDLE]    = {ST_EXPLORE, S_,      S_,         S_,       S_,        S_,      ST_FAULT, S_,    S_},
    [ST_EXPLORE] = {S_,         ST_AVOID, S_,        ST_DOCK,  S_,        S_,      ST_FAULT, S_,    S_},
    [ST_AVOID]   = {S_,         S_,      ST_EXPLORE, ST_DOCK,  S_,        S_,      ST_FAULT, S_,    S_},
    [ST_DOCK]    = {S_,         S_,      S_,         S_,       ST_CHARGE, S_,      ST_FAULT, S_,    S_},
    [ST_CHARGE]  = {S_,         S_,      S_,         S_,       S_,        ST_IDLE, ST_FAULT, S_,    S_},
    [ST_FAULT]   = {S_,         S_,      S_,         S_,       S_,        S_,      S_,       S_,    S_},
};

void robot_init(Robot *r, uint32_t now_ms) { r->state = ST_IDLE; r->entered_ms = now_ms; }

static int enter(Robot *r, State s, uint32_t now_ms) {
    r->state = s;
    r->entered_ms = now_ms;
    return 1;
}

int robot_handle(Robot *r, Event e, uint32_t now_ms) {
    if ((unsigned)r->state >= (unsigned)ST_COUNT) return enter(r, ST_FAULT, now_ms);   /* fail safe */
    if ((unsigned)e >= (unsigned)EV_COUNT) return 0;
    const uint32_t elapsed = now_ms - r->entered_ms;                                   /* wrap-safe */
    if (r->state == ST_AVOID && e == EV_TICK && elapsed >= AVOID_TIMEOUT_MS) return enter(r, ST_EXPLORE, now_ms);
    if (r->state == ST_FAULT && e == EV_RESET) return elapsed >= FAULT_HOLD_MS ? enter(r, ST_IDLE, now_ms) : 0;
    const State n = next_state[r->state][e];
    return n == ST_COUNT ? 0 : enter(r, n, now_ms);
}

int robot_motors(const Robot *r) {
    return r->state == ST_EXPLORE || r->state == ST_AVOID || r->state == ST_DOCK;
}
```

- **The table** makes every (state, event) decision explicit and reviewable. `EV_FAULT` appears in every active row, so a missing fault transition is visible at a glance. Only the two **guarded** transitions need code.
- **Validation before indexing**: a corrupted `state` would index outside the table (UB), so it's checked first and drives the robot to the safe state, as MISRA-style defensive code requires.
- **Wrap-safe time**: `now - entered` in `uint32_t` is correct across the 49.7-day rollover, while comparing `now >= entered + 3000` breaks there. The third hidden test enters AVOID just before the wrap.
- **Moore output**: motors depend only on the state, so they can't glitch on ignored events.
