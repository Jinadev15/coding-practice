---
id: cpp-pimpl-motor
title: Refactor a Motor Controller to PIMPL (Multi-File)
difficulty: Hard
order: 1
tags: PIMPL, unique_ptr, incomplete types, rule of five, ABI stability, multi-file
---
## Statement
`MotorController` ships in a shared library used by several robot applications. Every time someone tweaks a private member, all the clients must be rebuilt and redeployed. That's an ABI break. Refactor it to the **PIMPL idiom**, so the public header never changes when the implementation does.

The class works today. Keep its behaviour exactly, but change its structure:
1. `motor_controller.h` may contain only the public interface plus `struct Impl;` and `std::unique_ptr<Impl> impl_;`. The hidden test checks `static_assert(sizeof(MotorController) == sizeof(void*))`.
2. All state and the controller maths move into `motor_controller.cpp`.
3. Implement the **rule of five** correctly:
   - **copy** makes a deep, independent copy
   - **move** is `noexcept` and leaves the source empty (`valid() == false`)
   - copy assignment and move assignment (including self-assignment) work
   - the destructor is defined in the `.cpp` file
4. The heavy include `<cmath>` (standing in for a big CAN driver header) must disappear from the header.

The controller is a PI velocity loop with anti-windup driving a first-order motor model:

```
e = target − v
I' = I + e·dt                         (candidate integral)
u  = kp·e + ki·I'
if u > 12  → u = 12   (saturated: don't commit I')
if u < −12 → u = −12  (saturated: don't commit I')
else I = I'
v += (2·u − v) · dt / 0.1             (gain 2 rad/s per volt, time constant 0.1 s)
```

## Starter: motor_controller.h
```cpp
#pragma once
#include <cmath>

class MotorController {
public:
    MotorController(int can_id, double kp, double ki);
    bool valid() const noexcept { return true; }
    int can_id() const;
    void set_target(double rad_s);
    void step(double dt);
    double velocity() const;
    double voltage() const;

private:
    int can_id_;
    double kp_, ki_;
    double target_ = 0, integral_ = 0, v_ = 0, u_ = 0;
};
```

## Starter: motor_controller.cpp
```cpp
#include "motor_controller.h"

MotorController::MotorController(int can_id, double kp, double ki) : can_id_(can_id), kp_(kp), ki_(ki) {}
int MotorController::can_id() const { return can_id_; }
void MotorController::set_target(double rad_s) { target_ = rad_s; }
double MotorController::velocity() const { return v_; }
double MotorController::voltage() const { return u_; }

void MotorController::step(double dt) {
    double e = target_ - v_;
    double cand = integral_ + e * dt;
    double u = kp_ * e + ki_ * cand;
    if (u > 12) u = 12;
    else if (u < -12) u = -12;
    else integral_ = cand;
    u_ = u;
    v_ += (2.0 * u - v_) * dt / 0.1;
}
```

## Driver: main.cpp
```cpp
#include "motor_controller.h"
#include <cstdio>
#include <iostream>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

static_assert(sizeof(MotorController) == sizeof(void*), "use PIMPL: the class must hold only a pointer to Impl");
static_assert(std::is_copy_constructible_v<MotorController>, "deep copy required");
static_assert(std::is_nothrow_move_constructible_v<MotorController>, "move must be noexcept");
static_assert(std::is_nothrow_move_assignable_v<MotorController>, "move assignment must be noexcept");

static void show(const char* tag, const MotorController& m) {
    if (!m.valid()) { std::printf("%s: empty\n", tag); return; }
    std::printf("%s: id=%d v=%.4f u=%.4f\n", tag, m.can_id(), m.velocity(), m.voltage());
}

int main() {
    std::string scenario;
    std::cin >> scenario;
    if (scenario == "run") {
        int id, steps; double kp, ki, target, dt;
        std::cin >> id >> kp >> ki >> target >> dt >> steps;
        MotorController m(id, kp, ki);
        m.set_target(target);
        for (int i = 1; i <= steps; ++i) {
            m.step(dt);
            if (i % 10 == 0 || i == steps) {
                std::string tag = "step " + std::to_string(i);
                show(tag.c_str(), m);
            }
        }
    } else if (scenario == "semantics") {
        MotorController a(3, 2.0, 5.0);
        a.set_target(5);
        for (int i = 0; i < 30; ++i) a.step(0.01);
        MotorController b = a;                         // deep copy
        b.set_target(-5);
        for (int i = 0; i < 30; ++i) b.step(0.01);
        show("original after copy ran", a);
        show("copy", b);
        MotorController c = std::move(b);              // move
        show("moved-from", b);
        show("moved-to", c);
        b = a;                                         // copy-assign INTO a moved-from object
        show("reassigned", b);
        a = a;                                         // self copy-assign
        show("self-assigned", a);
        MotorController d(9, 1.0, 1.0);
        d = std::move(c);                              // move-assign
        show("move-assigned", d);
        show("source after move-assign", c);
        std::vector<MotorController> fleet;
        for (int i = 0; i < 5; ++i) fleet.emplace_back(100 + i, 1.5, 2.0);   // reallocations move elements
        for (auto& m : fleet) { m.set_target(m.can_id() - 100); m.step(0.05); }
        for (auto& m : fleet) show("fleet", m);
        std::vector<MotorController> copy = fleet;
        copy[0].set_target(50); copy[0].step(0.05);
        show("fleet[0] unchanged", fleet[0]);
        show("copy[0] changed", copy[0]);
    }
}
```

## Tests
=== sample
run 1 2.0 5.0 10 0.01 30
---
step 10: id=1 v=8.3773 u=4.4099
step 20: id=1 v=8.6932 u=4.4693
step 30: id=1 v=8.9369 u=4.5682
=== hidden
run 2 10.0 50.0 20 0.01 50
---
step 10: id=2 v=15.6317 u=12.0000
step 20: id=2 v=19.2945 u=10.0303
step 30: id=2 v=19.6556 u=10.8566
step 40: id=2 v=19.8886 u=12.0000
step 50: id=2 v=19.8598 u=12.0000
=== hidden
run 3 0.5 1.0 -4 0.005 40
---
step 10: id=3 v=-1.3740 u=-1.5208
step 20: id=3 v=-1.9382 u=-1.3305
step 30: id=3 v=-2.2018 u=-1.2859
step 40: id=3 v=-2.3520 u=-1.2935
=== hidden
semantics
---
original after copy ran: id=3 v=4.5434 u=2.3145
copy: id=3 v=-4.1720 u=-2.1637
moved-from: empty
moved-to: id=3 v=-4.1720 u=-2.1637
reassigned: id=3 v=4.5434 u=2.3145
self-assigned: id=3 v=4.5434 u=2.3145
move-assigned: id=3 v=-4.1720 u=-2.1637
source after move-assign: empty
fleet: id=100 v=0.0000 u=0.0000
fleet: id=101 v=1.6000 u=1.6000
fleet: id=102 v=3.2000 u=3.2000
fleet: id=103 v=4.8000 u=4.8000
fleet: id=104 v=6.4000 u=6.4000
fleet[0] unchanged: id=100 v=0.0000 u=0.0000
copy[0] changed: id=100 v=12.0000 u=12.0000

## Hints
- In the header: forward-declare `struct Impl;`, hold `std::unique_ptr<Impl> impl_;`, and **declare** (don't define) all five special members.
- In the `.cpp`: define `struct MotorController::Impl { ... }` first, then `MotorController::~MotorController() = default;` and the defaulted move operations. They must be defaulted *after* `Impl` is complete.
- The copy constructor: `impl_(other.impl_ ? std::make_unique<Impl>(*other.impl_) : nullptr)`. For copy assignment, use copy-and-swap, or assign `*impl_ = *other.impl_` with care for an empty `this`.
- `valid()` is `impl_ != nullptr`. Move it to the `.cpp` too, or define it inline in the header; both are ABI-safe because it only reads the pointer.

## Solution: motor_controller.h
```cpp
#pragma once
#include <memory>

class MotorController {
public:
    MotorController(int can_id, double kp, double ki);
    ~MotorController();
    MotorController(const MotorController& other);
    MotorController& operator=(const MotorController& other);
    MotorController(MotorController&& other) noexcept;
    MotorController& operator=(MotorController&& other) noexcept;

    bool valid() const noexcept { return impl_ != nullptr; }
    int can_id() const;
    void set_target(double rad_s);
    void step(double dt);
    double velocity() const;
    double voltage() const;

private:
    struct Impl;                     // defined only in motor_controller.cpp
    std::unique_ptr<Impl> impl_;
};
```

## Solution: motor_controller.cpp
```cpp
#include "motor_controller.h"
#include <cmath>                     // heavy dependencies live here now, invisible to clients

struct MotorController::Impl {
    int can_id;
    double kp, ki;
    double target = 0, integral = 0, v = 0, u = 0;

    void step(double dt) {
        double e = target - v;
        double cand = integral + e * dt;
        double out = kp * e + ki * cand;
        if (out > 12) out = 12;
        else if (out < -12) out = -12;
        else integral = cand;        // anti-windup: integrate only when not saturated
        u = out;
        v += (2.0 * out - v) * dt / 0.1;
    }
};

MotorController::MotorController(int can_id, double kp, double ki)
    : impl_(std::make_unique<Impl>(Impl{can_id, kp, ki})) {}

MotorController::~MotorController() = default;                                   // Impl is complete here
MotorController::MotorController(MotorController&&) noexcept = default;
MotorController& MotorController::operator=(MotorController&&) noexcept = default;

MotorController::MotorController(const MotorController& other)
    : impl_(other.impl_ ? std::make_unique<Impl>(*other.impl_) : nullptr) {}

MotorController& MotorController::operator=(const MotorController& other) {
    if (this != &other) {
        MotorController tmp(other);  // copy-and-swap: strong exception guarantee, self-assignment safe
        std::swap(impl_, tmp.impl_);
    }
    return *this;
}

int MotorController::can_id() const { return impl_->can_id; }
void MotorController::set_target(double rad_s) { impl_->target = rad_s; }
void MotorController::step(double dt) { impl_->step(dt); }
double MotorController::velocity() const { return impl_->v; }
double MotorController::voltage() const { return impl_->u; }
```

## Solution
After the refactor, the public class is exactly one pointer. Adding a field, changing the controller maths or swapping `<cmath>` for a real CAN driver header changes only `motor_controller.cpp`. Clients neither recompile nor break. That's the ABI firewall.

The subtle part is **where the special members are defined**:
- `std::unique_ptr<Impl>`'s destructor calls `delete` on an `Impl`, which requires the complete type. A destructor defaulted in the header would be generated in every client TU, where `Impl` is incomplete, and fail to compile. So you declare it in the header and `= default` it in the `.cpp`. The same applies to the move operations, because move assignment must destroy the old `Impl`.
- `unique_ptr` isn't copyable, so **copying must be written by hand**: `make_unique<Impl>(*other.impl_)` copies the state. Copy-and-swap handles self-assignment and gives the strong exception guarantee.
- Moves are just pointer transfers, which is why PIMPL objects move for free and `std::vector` can use the `noexcept` move when it reallocates. The cost is one heap allocation per object and an indirection per call.
