# Case Study: Sensor and Motor Drivers

The final case study builds the software skeleton of a small differential-drive robot in object-oriented C:
- driver **interfaces** (vtables) for motors and range sensors;
- concrete drivers, including simulated ones;
- a **controller** that depends only on the interfaces;
- a fixed-rate **control loop**.

It's how PX4, ArduPilot, Zephyr and countless commercial products are structured, and why the same control code runs unchanged on hardware, in simulation and in unit tests.

## 1. Requirements

- Two wheel motors, each accepting a velocity command (rad/s), limited by acceleration and maximum speed, and reporting encoder velocity.
- A front range sensor, returning a distance or a failure.
- Behaviour: drive toward a target speed, slow down proportionally inside the slow zone, stop inside the stop zone, and **fail safe** (stop) when the sensor fails 3 times in a row.
- A 100 Hz loop. Everything is testable on a PC with deterministic simulated hardware.

## 2. Interfaces

```c
/* hal_motor.h */
typedef struct Motor Motor;
typedef struct {
    const char *kind;
    int    (*set_velocity)(Motor *m, double rad_s);   /* command */
    double (*velocity)(const Motor *m);               /* measured */
    void   (*update)(Motor *m, double dt);            /* advance the internal state (simulation or filters) */
    void   (*destroy)(Motor *m);
} MotorOps;
struct Motor { const MotorOps *ops; const char *name; };

/* hal_range.h */
typedef struct RangeSensor RangeSensor;
typedef struct {
    const char *kind;
    int  (*read)(RangeSensor *s, double *meters);     /* 0 = ok */
    void (*destroy)(RangeSensor *s);
} RangeOps;
struct RangeSensor { const RangeOps *ops; const char *name; };
```

The controller includes only these headers. It never sees CAN frames, PWM registers or simulator internals.

## 3. Concrete drivers

```c
/* sim_motor.c: a first-order motor with slew-rate limiting */
typedef struct { Motor base; double cmd, vel, max_vel, max_acc; } SimMotor;

static int sim_set(Motor *m, double v) {
    SimMotor *s = (SimMotor *)m;
    if (v > s->max_vel) v = s->max_vel;
    if (v < -s->max_vel) v = -s->max_vel;
    s->cmd = v;
    return 0;
}
static void sim_update(Motor *m, double dt) {
    SimMotor *s = (SimMotor *)m;
    double dv = s->cmd - s->vel, lim = s->max_acc * dt;
    s->vel += dv > lim ? lim : dv < -lim ? -lim : dv;  /* acceleration limit */
}
```

A real `can_motor.c` implements the same `MotorOps` by packing CAN frames. A `fake_range.c` replays a scripted distance sequence (with failures), so tests are exact.

## 4. The controller: pure logic over interfaces

```c
typedef struct {
    Motor *left, *right;
    RangeSensor *front;
    double cruise, stop_dist, slow_dist;
    int consecutive_failures;
    enum { DRIVE_OK, DRIVE_SLOW, DRIVE_STOP, DRIVE_FAULT } state;
} DriveController;

void drive_step(DriveController *c, double dt) {
    double d, target = c->cruise;
    if (c->front->ops->read(c->front, &d) != 0) {
        if (++c->consecutive_failures >= 3) c->state = DRIVE_FAULT;    /* latch: fail safe */
    } else {
        c->consecutive_failures = 0;
        if (c->state != DRIVE_FAULT) {
            if (d <= c->stop_dist) c->state = DRIVE_STOP;
            else if (d < c->slow_dist) c->state = DRIVE_SLOW;
            else c->state = DRIVE_OK;
        }
    }
    if (c->state == DRIVE_FAULT || c->state == DRIVE_STOP) target = 0;
    else if (c->state == DRIVE_SLOW) target *= (d - c->stop_dist) / (c->slow_dist - c->stop_dist);
    c->left->ops->set_velocity(c->left, target);
    c->right->ops->set_velocity(c->right, target);
    c->left->ops->update(c->left, dt);
    c->right->ops->update(c->right, dt);
}
```

Notice:
- **The fault latches**: once in `DRIVE_FAULT`, the robot stays stopped until an explicit reset. A flapping sensor must not let it lurch forward.
- **The state is explicit**, so it can be logged and tested exhaustively.
- The controller holds **borrowed** pointers. The composition root owns and destroys the drivers.

## 5. Composition root and loop

```c
int main(void) {
    Motor *l = sim_motor_create("left", 10.0, 20.0), *r = sim_motor_create("right", 10.0, 20.0);
    RangeSensor *front = fake_range_create("front", script, script_len);
    DriveController c = { l, r, front, 5.0, 0.3, 1.0, 0, DRIVE_OK };
    struct timespec next; clock_gettime(CLOCK_MONOTONIC, &next);
    for (int tick = 0; tick < 1000; tick++) {
        drive_step(&c, 0.01);
        next.tv_nsec += 10 * 1000 * 1000;                                  /* 100 Hz, absolute time: no drift */
        if (next.tv_nsec >= 1000000000L) { next.tv_nsec -= 1000000000L; next.tv_sec++; }
        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next, NULL);
    }
    l->ops->destroy(l); r->ops->destroy(r); front->ops->destroy(front);
}
```

In tests, the loop runs without sleeping, stepping simulated time directly. A thousand seconds of robot behaviour then takes milliseconds.

## 6. What this architecture buys

- **Hardware independence**: switching from simulation to hardware, or to a different motor vendor, means writing one new driver that implements `MotorOps`. The controller doesn't change.
- **Testability**: fakes give exact, reproducible scenarios, such as "the sensor fails on ticks 40, 41 and 42".
- **Safety reviewability**: the safety-relevant logic (`drive_step`) is small, pure and isolated from I/O, which is exactly what certification reviewers want to see.

> [!EXAM]
> **Why should robot control logic depend on driver interfaces (vtables) rather than concrete drivers?**
> Depending on abstract interfaces such as `MotorOps` and `RangeOps` inverts the dependency: the control logic and the concrete drivers both depend on the small interface header, not on each other. The same controller then runs against real hardware drivers, a simulator, or scripted fakes, selected in one composition root. Behaviour (slowing, stopping, fault latching) can be tested deterministically on a PC, hardware vendors can be swapped by writing one new driver, and the safety-critical logic stays small and free of I/O details, which makes it easier to review and certify.
