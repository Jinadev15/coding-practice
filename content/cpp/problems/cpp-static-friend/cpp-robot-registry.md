---
id: cpp-robot-registry
title: Robot Registry with a Factory
difficulty: Medium
order: 1
tags: static members, factory, friend, private constructor
---
## Statement
A fleet manager needs every robot to get a unique serial **per model** (`ur5-1`, `ur5-2`, `spot-1`, …) and needs live statistics. Implement:

```cpp
class Robot {
public:
    static std::unique_ptr<Robot> create(const std::string& model);   // the ONLY way to make a Robot
    ~Robot();
    Robot(const Robot&) = delete;
    Robot& operator=(const Robot&) = delete;

    const std::string& serial() const;
    static int alive();                              // robots currently existing
    static int created();                            // robots ever created
    static int alive_of(const std::string& model);   // currently existing robots of a model

    friend std::ostream& operator<<(std::ostream& os, const Robot& r);   // prints Robot(SERIAL)
private:
    explicit Robot(const std::string& model);        // private: forces use of create()
    // ...
};
```

- Serial numbers are never reused: if `ur5-1` and `ur5-2` were created and `ur5-1` was scrapped, the next `ur5` is `ur5-3`.
- `operator<<` must be a friend that reads the private serial directly (you may also keep a public `serial()`).
- The constructor is private, so `create` can't use `std::make_unique`. Think about why.

The driver handles these commands: `make MODEL` (prints the robot), `scrap I` (destroys the I-th robot still held, 0-based in creation order), `stat MODEL`, `stats`.

## Starter
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <map>

class Robot {
public:
    static std::unique_ptr<Robot> create(const std::string& model) { return nullptr; }
    ~Robot() {}
    Robot(const Robot&) = delete;
    Robot& operator=(const Robot&) = delete;

    const std::string& serial() const { return serial_; }
    static int alive() { return 0; }
    static int created() { return 0; }
    static int alive_of(const std::string& model) { return 0; }

    friend std::ostream& operator<<(std::ostream& os, const Robot& r) { return os; }
private:
    explicit Robot(const std::string& model) {}
    std::string serial_;
};
```

## Driver
```cpp
#include <vector>
#include <type_traits>

static_assert(!std::is_constructible_v<Robot, std::string>, "the constructor must be private");
static_assert(!std::is_copy_constructible_v<Robot>);

int main() {
    std::vector<std::unique_ptr<Robot>> held;
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "make") {
            std::string m; std::cin >> m;
            held.push_back(Robot::create(m));
            std::cout << *held.back() << '\n';
        } else if (cmd == "scrap") {
            std::size_t i; std::cin >> i;
            std::cout << "scrapped " << held.at(i)->serial() << '\n';
            held.erase(held.begin() + static_cast<long>(i));
        } else if (cmd == "stat") {
            std::string m; std::cin >> m;
            std::cout << m << ": " << Robot::alive_of(m) << '\n';
        } else if (cmd == "stats") {
            std::cout << "alive " << Robot::alive() << " created " << Robot::created() << '\n';
        }
    }
    held.clear();
    std::cout << "end alive " << Robot::alive() << '\n';
}
```

## Tests
=== sample
make ur5
make spot
make ur5
stats
scrap 0
make ur5
stat ur5
stat spot
stats
---
Robot(ur5-1)
Robot(spot-1)
Robot(ur5-2)
alive 3 created 3
scrapped ur5-1
Robot(ur5-3)
ur5: 2
spot: 1
alive 3 created 4
end alive 0
=== hidden
stats
stat none
make a
scrap 0
make a
make a
scrap 1
make b
stat a
stat b
stats
scrap 0
scrap 0
stats
make a
---
alive 0 created 0
none: 0
Robot(a-1)
scrapped a-1
Robot(a-2)
Robot(a-3)
scrapped a-3
Robot(b-1)
a: 1
b: 1
alive 2 created 4
scrapped a-2
scrapped b-1
alive 0 created 4
Robot(a-4)
end alive 0
=== hidden
make x
make x
make x
make x
make x
make y
scrap 2
scrap 2
scrap 2
stat x
stat y
make x
stats
---
Robot(x-1)
Robot(x-2)
Robot(x-3)
Robot(x-4)
Robot(x-5)
Robot(y-1)
scrapped x-3
scrapped x-4
scrapped x-5
x: 2
y: 1
Robot(x-6)
alive 4 created 7
end alive 0

## Hints
- `static inline int alive_ = 0;` (C++17) lets you define static data inside the class.
- Per-model data fits `static inline std::map<std::string, int>`. You need two maps: the next serial number, and the live count.
- The destructor needs to know the robot's model to decrement its live count, so store it.
- `std::make_unique<Robot>(m)` calls the constructor from inside the standard library, which isn't a member of `Robot`, so it has no access. `std::unique_ptr<Robot>(new Robot(m))` runs inside `create`, which does.

## Solution
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <map>

class Robot {
public:
    static std::unique_ptr<Robot> create(const std::string& model) {
        return std::unique_ptr<Robot>(new Robot(model));   // make_unique can't reach the private ctor
    }
    ~Robot() {
        --alive_;
        --live_[model_];
    }
    Robot(const Robot&) = delete;
    Robot& operator=(const Robot&) = delete;

    const std::string& serial() const { return serial_; }
    static int alive() { return alive_; }
    static int created() { return created_; }
    static int alive_of(const std::string& model) {
        auto it = live_.find(model);
        return it == live_.end() ? 0 : it->second;
    }

    friend std::ostream& operator<<(std::ostream& os, const Robot& r) {
        return os << "Robot(" << r.serial_ << ')';
    }

private:
    explicit Robot(const std::string& model)
        : model_(model), serial_(model + "-" + std::to_string(++next_[model])) {
        ++alive_;
        ++created_;
        ++live_[model];
    }

    std::string model_;
    std::string serial_;
    static inline int alive_ = 0;
    static inline int created_ = 0;
    static inline std::map<std::string, int> next_;   // last serial number issued per model
    static inline std::map<std::string, int> live_;   // currently alive per model
};
```

Class-wide state (`alive_`, `created_`, the per-model maps) is `static`: there's one copy shared by all robots, and it's reachable from static member functions with no object. Making the constructor private and copying deleted means every robot is created by `create` and counted exactly once. The destructor keeps the counts correct automatically whenever a `unique_ptr` is destroyed, which is RAII for bookkeeping. `operator<<` is a hidden friend, so it can read `serial_` and is found by argument-dependent lookup on `std::cout << robot`.
