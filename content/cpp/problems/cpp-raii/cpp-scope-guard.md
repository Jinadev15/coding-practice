---
id: cpp-scope-guard
title: RAII Motor Session
difficulty: Medium
order: 1
tags: RAII, destructors, exceptions, deleted copy
---
## Statement
A motor driver must **always** be disabled after use, even if the trajectory code throws. Implement the RAII class `MotorSession`:

- constructor: calls `motor.enable()` and logs through the motor
- destructor: calls `motor.disable()` (it must never throw)
- non-copyable (`= delete`), because two sessions would disable the same motor twice
- `void run(int speed)` sets the speed; if `speed > motor.limit`, it **throws** `std::runtime_error("overspeed")`

The `Motor` class (with a log) is given in the driver. Make sure that after every scenario the motor is disabled and the log shows the correct order.

## Starter
```cpp
#include <stdexcept>
#include <string>
#include <vector>
#include <type_traits>

struct Motor {
    int limit;
    bool enabled = false;
    std::vector<std::string> log;
    void enable() { enabled = true; log.push_back("enable"); }
    void disable() { enabled = false; log.push_back("disable"); }
    void set_speed(int s) { log.push_back("speed " + std::to_string(s)); }
};

class MotorSession {
public:
    explicit MotorSession(Motor& m) {}
    void run(int speed) {}
};
```

## Driver
```cpp
#include <iostream>
int main() {
    Motor m{100};
    int t; std::cin >> t;
    while (t--) {
        int a, b; std::cin >> a >> b;
        try {
            MotorSession s(m);
            s.run(a);
            s.run(b);
        } catch (const std::runtime_error& e) {
            m.log.push_back(std::string("caught ") + e.what());
        }
        m.log.push_back(m.enabled ? "STILL ENABLED" : "safe");
    }
    for (auto& line : m.log) std::cout << line << '\n';
    static_assert(!std::is_copy_constructible_v<MotorSession>, "MotorSession must not be copyable");
}
```

## Tests
=== sample
2
50 80
50 150
---
enable
speed 50
speed 80
disable
safe
enable
speed 50
disable
caught overspeed
safe
=== hidden
1
200 10
---
enable
disable
caught overspeed
safe

## Hints
- Keep the given `Motor` struct unchanged. The driver (appended after your code) uses it.
- `MotorSession` holds a `Motor&`.
- Note the order in the second case: `disable` is logged **before** `caught overspeed`, because the destructor runs during stack unwinding, before the catch block executes.

## Solution
The destructor runs when the `try` block is left, normally or by an exception, so the motor is disabled on every path, and before the handler runs. Deleting the copy operations makes it a compile error to accidentally duplicate the session.

```cpp
#include <stdexcept>
#include <string>
#include <vector>
#include <type_traits>

struct Motor {
    int limit;
    bool enabled = false;
    std::vector<std::string> log;
    void enable() { enabled = true; log.push_back("enable"); }
    void disable() { enabled = false; log.push_back("disable"); }
    void set_speed(int s) { log.push_back("speed " + std::to_string(s)); }
};

class MotorSession {
    Motor& m_;
public:
    explicit MotorSession(Motor& m) : m_(m) { m_.enable(); }
    ~MotorSession() { m_.disable(); }
    MotorSession(const MotorSession&) = delete;
    MotorSession& operator=(const MotorSession&) = delete;

    void run(int speed) {
        if (speed > m_.limit) throw std::runtime_error("overspeed");
        m_.set_speed(speed);
    }
};
```

This is exactly what a robotics safety layer looks like. Without RAII, every early return and every exception path would need its own `disable()` call, and one forgotten path is a robot arm left powered. `std::lock_guard`, `std::jthread` and file streams are the same idea.
