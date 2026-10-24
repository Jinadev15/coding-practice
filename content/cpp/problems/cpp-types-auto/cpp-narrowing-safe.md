---
id: cpp-narrowing-safe
title: Safe Conversions
difficulty: Medium
order: 1
tags: brace init, static_cast, auto, numeric limits
---
## Statement
Implement `std::optional<int> to_int_checked(double x)`. It returns the value rounded to the nearest integer (halves away from zero, as `std::lround` does) if that fits in an `int`, otherwise `std::nullopt` (including NaN and ±infinity).

Then implement `int saturating_add(int a, int b)`, which returns `a + b` clamped to `[INT_MIN, INT_MAX]` **without** ever overflowing (signed overflow is UB).

## Starter
```cpp
#include <optional>
#include <limits>
#include <cmath>

std::optional<int> to_int_checked(double x) {
    return std::nullopt;
}

int saturating_add(int a, int b) {
    return 0;
}
```

## Driver
```cpp
#include <iostream>
#include <string>
int main() {
    std::string kind;
    while (std::cin >> kind) {
        if (kind == "conv") {
            std::string s; std::cin >> s;
            double x = std::stod(s);
            auto r = to_int_checked(x);
            if (r) std::cout << *r << '\n'; else std::cout << "out of range\n";
        } else {
            long long a, b; std::cin >> a >> b;
            std::cout << saturating_add(static_cast<int>(a), static_cast<int>(b)) << '\n';
        }
    }
}
```

## Tests
=== sample
conv 2.5
conv -2.5
conv 1e10
add 2147483647 1
add -5 3
---
3
-3
out of range
2147483647
-2
=== hidden
conv 2147483647.4
conv 2147483647.6
conv -2147483648.4
conv nan
conv inf
add -2147483648 -1
add 2000000000 2000000000
add -2147483648 2147483647
---
2147483647
out of range
-2147483648
out of range
out of range
-2147483648
2147483647
-1

## Hints
- Check `std::isfinite(x)` first. Round with `std::round(x)` (a double) and compare it against `std::numeric_limits<int>::min()` and `max()` **as doubles** before converting with `static_cast<int>`.
- Saturating add: if `b > 0 && a > INT_MAX - b`, return `INT_MAX`; if `b < 0 && a < INT_MIN - b`, return `INT_MIN`.

## Solution
```cpp
#include <optional>
#include <limits>
#include <cmath>

std::optional<int> to_int_checked(double x) {
    if (!std::isfinite(x)) return std::nullopt;
    double r = std::round(x);
    constexpr double lo = std::numeric_limits<int>::min();
    constexpr double hi = std::numeric_limits<int>::max();
    if (r < lo || r > hi) return std::nullopt;
    return static_cast<int>(r);
}

int saturating_add(int a, int b) {
    constexpr int mx = std::numeric_limits<int>::max();
    constexpr int mn = std::numeric_limits<int>::min();
    if (b > 0 && a > mx - b) return mx;
    if (b < 0 && a < mn - b) return mn;
    return a + b;
}
```

Converting a double outside the target type's range with `static_cast<int>` is **undefined behaviour**, so the range check must happen in floating point first. `mx - b` can't overflow when `b > 0` (and `mn - b` can't when `b < 0`), which makes the check itself safe. Robotics control code uses saturating arithmetic constantly (motor commands, PWM duty cycles), and C++26 adds `std::add_sat` for exactly this.
