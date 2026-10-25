---
id: cpp-namespace-units
title: Namespaces for Units
difficulty: Easy
order: 1
tags: namespaces, nested namespaces, anonymous namespace
---
## Statement
Organise unit conversions into namespaces:

- `units::length::to_m(double value, const std::string& unit)` for units `mm`, `cm`, `m`, `km`, `in`, `ft`
- `units::angle::to_rad(double value, const std::string& unit)` for units `deg`, `rad`, `rev`
- a helper `factor(...)` lookup table inside an **anonymous namespace** (file-private)

Unknown units throw `std::invalid_argument`. The driver calls the functions **fully qualified** (no `using namespace`).

## Starter
```cpp
#include <string>
#include <stdexcept>
#include <map>
#include <numbers>

namespace units {
namespace length {
double to_m(double value, const std::string& unit) {
    return 0;
}
}
}
```

## Driver
```cpp
#include <iostream>
#include <iomanip>
int main() {
    std::string kind, unit; double v;
    std::cout << std::fixed << std::setprecision(4);
    while (std::cin >> kind >> v >> unit) {
        try {
            if (kind == "len") std::cout << units::length::to_m(v, unit) << " m\n";
            else std::cout << units::angle::to_rad(v, unit) << " rad\n";
        } catch (const std::invalid_argument& e) {
            std::cout << "error: " << e.what() << '\n';
        }
    }
}
```

## Tests
=== sample
len 1500 mm
len 3 ft
ang 180 deg
ang 0.5 rev
len 2 parsec
---
1.5000 m
0.9144 m
3.1416 rad
3.1416 rad
error: unknown unit parsec
=== hidden
len 1 km
len 12 in
ang 2 rad
ang 90 grad
---
1000.0000 m
0.3048 m
2.0000 rad
error: unknown unit grad

## Hints
- Nested namespaces can be written as `namespace units::length { ... }`.
- Put the shared lookup helper inside an anonymous namespace `namespace { ... }`: it is visible only in this file.
- Store the conversion factors in a `static const std::map<std::string, double>`; `find` returns `end()` for an unknown unit, so throw `std::invalid_argument` then.

## Solution
```cpp
#include <string>
#include <stdexcept>
#include <map>
#include <numbers>

namespace {
double factor(const std::map<std::string, double>& table, const std::string& unit) {
    auto it = table.find(unit);
    if (it == table.end()) throw std::invalid_argument("unknown unit " + unit);
    return it->second;
}
}

namespace units::length {
double to_m(double value, const std::string& unit) {
    static const std::map<std::string, double> table{
        {"mm", 0.001}, {"cm", 0.01}, {"m", 1.0}, {"km", 1000.0},
        {"in", 0.0254}, {"ft", 0.3048}};
    return value * factor(table, unit);
}
}

namespace units::angle {
double to_rad(double value, const std::string& unit) {
    static const std::map<std::string, double> table{
        {"deg", std::numbers::pi / 180.0}, {"rad", 1.0}, {"rev", 2.0 * std::numbers::pi}};
    return value * factor(table, unit);
}
}
```

`units::length` and `units::angle` group related functions without name clashes, so both could have a function called `convert`. The anonymous namespace keeps `factor` private to this file. `static const` tables are built once, on the first call. `std::numbers::pi` (C++20) replaces the non-standard `M_PI`.
