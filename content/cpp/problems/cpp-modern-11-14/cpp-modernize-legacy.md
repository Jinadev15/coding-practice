---
id: cpp-modernize-legacy
title: Modernize a Legacy Robot Module
difficulty: Medium
order: 1
tags: modern C++, enum class, unique_ptr, nullptr, = delete, override, constexpr
---
## Statement
The starter is a working but **C++98-style** module: raw `new`/`delete`, `NULL`, a plain `enum`, `#define` constants, a copyable class owning a raw pointer (a double-delete waiting to happen), and a virtual function without `override`. **Rewrite it in modern C++** with the same behaviour. The driver enforces the modernisation at compile time:

- `Mode` must be an `enum class` (not implicitly convertible to `int`) with underlying type `std::uint8_t`.
- `kMaxSpeed` must be a `constexpr double` (usable in `static_assert`).
- `Robot` must be **non-copyable** but **nothrow-movable**, and must own its `Battery` through `std::unique_ptr<Battery>`.
- `SafeRobot` must override `limit` with `override`, and be `final`.
- `make_robot` must return `std::unique_ptr<Robot>`.
- `find_robot` must return a `Robot*` that is `nullptr` (not `NULL`) when nothing matches.

Behaviour (unchanged from the legacy code): `Robot(name, capacity)` creates a battery of that capacity. `drive(speed)` clamps the speed through `limit()`, drains `speed * 2` battery units (never below 0), and returns the applied speed. `describe()` returns `name [MODE] battery=X/Y`. `SafeRobot::limit` caps the speed at half of `kMaxSpeed`.

## Starter
```cpp
#include <string>
#include <vector>
#include <cstdint>
#include <sstream>

#define MAX_SPEED 4.0

enum Mode { IDLE, DRIVING, CHARGING };

struct Battery {
    double level, capacity;
    Battery(double c) : level(c), capacity(c) {}
};

class Robot {
public:
    Robot(const std::string& name, double capacity) : name_(name), battery_(new Battery(capacity)), mode_(IDLE) {}
    virtual ~Robot() { delete battery_; }
    virtual double limit(double s) const { return s > MAX_SPEED ? MAX_SPEED : (s < 0 ? 0 : s); }
    double drive(double speed) {
        double s = limit(speed);
        battery_->level -= s * 2;
        if (battery_->level < 0) battery_->level = 0;
        mode_ = s > 0 ? DRIVING : IDLE;
        return s;
    }
    void charge() { battery_->level = battery_->capacity; mode_ = CHARGING; }
    std::string describe() const {
        const char* names[] = {"IDLE", "DRIVING", "CHARGING"};
        std::ostringstream os;
        os << name_ << " [" << names[mode_] << "] battery=" << battery_->level << "/" << battery_->capacity;
        return os.str();
    }
    const std::string& name() const { return name_; }
    Mode mode() const { return mode_; }
private:
    std::string name_;
    Battery* battery_;
    Mode mode_;
};

class SafeRobot : public Robot {
public:
    SafeRobot(const std::string& n, double c) : Robot(n, c) {}
    virtual double limit(double s) const { double m = MAX_SPEED / 2; return s > m ? m : (s < 0 ? 0 : s); }
};

Robot* make_robot(const std::string& kind, const std::string& name, double cap) {
    if (kind == "safe") return new SafeRobot(name, cap);
    return new Robot(name, cap);
}

Robot* find_robot(const std::vector<Robot*>& fleet, const std::string& name) {
    for (size_t i = 0; i < fleet.size(); ++i) if (fleet[i]->name() == name) return fleet[i];
    return NULL;
}
```

## Driver
```cpp
#include <iostream>
#include <memory>
#include <type_traits>

static_assert(std::is_enum_v<Mode> && !std::is_convertible_v<Mode, int>, "Mode must be an enum class");
static_assert(std::is_same_v<std::underlying_type_t<Mode>, std::uint8_t>);
static_assert(kMaxSpeed == 4.0, "kMaxSpeed must be constexpr");
static_assert(!std::is_copy_constructible_v<Robot> && !std::is_copy_assignable_v<Robot>, "Robot must not be copyable");
static_assert(std::is_nothrow_move_constructible_v<Robot>, "Robot must be nothrow movable");
static_assert(std::is_final_v<SafeRobot>);
static_assert(std::is_same_v<decltype(make_robot("", "", 0)), std::unique_ptr<Robot>>);

int main() {
    std::vector<std::unique_ptr<Robot>> fleet;
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "make") {
            std::string kind, name; double cap;
            std::cin >> kind >> name >> cap;
            fleet.push_back(make_robot(kind, name, cap));
        } else if (cmd == "drive" || cmd == "charge" || cmd == "show" || cmd == "move") {
            std::string name;
            std::cin >> name;
            std::vector<Robot*> raw;
            for (auto& r : fleet) raw.push_back(r.get());
            Robot* r = find_robot(raw, name);
            if (r == nullptr) { std::cout << "no robot " << name << '\n'; if (cmd == "drive") { double d; std::cin >> d; } continue; }
            if (cmd == "drive") { double s; std::cin >> s; std::cout << "applied " << r->drive(s) << '\n'; }
            else if (cmd == "charge") r->charge();
            else if (cmd == "show") std::cout << r->describe() << '\n';
            else {
                Robot moved = std::move(*r);   // move construction must work
                std::cout << "moved: " << moved.describe() << '\n';
            }
        }
    }
    std::cout << "fleet size " << fleet.size() << '\n';
}
```

## Tests
=== sample
make basic rover 100
make safe tortoise 50
drive rover 10
drive tortoise 10
show rover
show tortoise
charge rover
show rover
drive ghost 3
drive rover -1
show rover
---
applied 4
applied 2
rover [DRIVING] battery=92/100
tortoise [DRIVING] battery=46/50
rover [CHARGING] battery=100/100
no robot ghost
applied 0
rover [IDLE] battery=100/100
fleet size 2
=== hidden
make basic a 10
drive a 3
drive a 3
show a
make safe b 8
drive b 1.5
show b
charge b
move b
show nobody
---
applied 3
applied 3
a [DRIVING] battery=0/10
applied 1.5
b [DRIVING] battery=5/8
moved: b [CHARGING] battery=8/8
no robot nobody
fleet size 2

## Hints
- `enum class Mode : std::uint8_t { Idle, Driving, Charging };`. To index the names array, use `static_cast<std::size_t>(mode_)`.
- `inline constexpr double kMaxSpeed = 4.0;` replaces the macro.
- With `std::unique_ptr<Battery> battery_;` the class automatically becomes non-copyable but movable, so you don't need to write a destructor at all (the Rule of Zero). You may still write `Robot(Robot&&) noexcept = default;` to document it. Note that a user-declared virtual destructor suppresses the implicit move operations, so declare them explicitly (`= default`).
- `make_robot` returns `std::make_unique<SafeRobot>(...)`, which converts to `std::unique_ptr<Robot>`.

## Solution
```cpp
#include <string>
#include <vector>
#include <cstdint>
#include <sstream>
#include <memory>
#include <algorithm>
#include <array>

inline constexpr double kMaxSpeed = 4.0;

enum class Mode : std::uint8_t { Idle, Driving, Charging };

struct Battery {
    double level, capacity;
    explicit Battery(double c) : level(c), capacity(c) {}
};

class Robot {
public:
    Robot(std::string name, double capacity)
        : name_(std::move(name)), battery_(std::make_unique<Battery>(capacity)) {}
    virtual ~Robot() = default;
    Robot(const Robot&) = delete;
    Robot& operator=(const Robot&) = delete;
    Robot(Robot&&) noexcept = default;
    Robot& operator=(Robot&&) noexcept = default;

    virtual double limit(double s) const { return std::clamp(s, 0.0, kMaxSpeed); }

    double drive(double speed) {
        double s = limit(speed);
        battery_->level = std::max(0.0, battery_->level - s * 2);
        mode_ = s > 0 ? Mode::Driving : Mode::Idle;
        return s;
    }
    void charge() { battery_->level = battery_->capacity; mode_ = Mode::Charging; }

    std::string describe() const {
        static constexpr std::array<const char*, 3> names{"IDLE", "DRIVING", "CHARGING"};
        std::ostringstream os;
        os << name_ << " [" << names[static_cast<std::size_t>(mode_)] << "] battery="
           << battery_->level << "/" << battery_->capacity;
        return os.str();
    }
    const std::string& name() const noexcept { return name_; }
    Mode mode() const noexcept { return mode_; }

private:
    std::string name_;
    std::unique_ptr<Battery> battery_;
    Mode mode_ = Mode::Idle;
};

class SafeRobot final : public Robot {
public:
    using Robot::Robot;
    double limit(double s) const override { return std::clamp(s, 0.0, kMaxSpeed / 2); }
};

std::unique_ptr<Robot> make_robot(const std::string& kind, const std::string& name, double cap) {
    if (kind == "safe") return std::make_unique<SafeRobot>(name, cap);
    return std::make_unique<Robot>(name, cap);
}

Robot* find_robot(const std::vector<Robot*>& fleet, const std::string& name) {
    auto it = std::find_if(fleet.begin(), fleet.end(), [&](const Robot* r) { return r->name() == name; });
    return it == fleet.end() ? nullptr : *it;
}
```

**Each modernisation fixes a real hazard:**
- **`unique_ptr<Battery>`**: the legacy class was copyable, so copying a `Robot` copied the raw pointer and both destructors deleted it (a double free). With `unique_ptr`, copying doesn't compile and moving transfers ownership. The defaulted `noexcept` moves are explicitly declared because the virtual destructor would otherwise suppress them.
- **`enum class` with an explicit underlying type** gives scoped names, no accidental integer arithmetic, and a fixed 1-byte size.
- **`constexpr`** gives a typed, scoped constant the debugger and `static_assert` understand, unlike `#define`.
- **`override` and `final`**: a signature typo now breaks the build instead of silently not overriding. `final` documents and enforces "no further subclasses".
- **Factories returning `unique_ptr`** make ownership explicit in the signature, so callers can't forget to delete.
- **`nullptr`** is a pointer-typed null, and `std::clamp`/`std::find_if` replace hand-written logic.
