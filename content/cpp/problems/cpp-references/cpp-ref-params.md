---
id: cpp-ref-params
title: References as Parameters
difficulty: Easy
order: 1
tags: references, const reference, pass by reference
---
## Statement
Implement:

- `void normalize(std::vector<double>& v)`: scale **in place** so the largest absolute value becomes 1 (unchanged if all values are 0)
- `double mean(const std::vector<double>& v)`: the average (0 for empty), without copying `v`
- `void minmax(const std::vector<double>& v, double& lo, double& hi)`: output through reference parameters (leave them unchanged if `v` is empty)

## Starter
```cpp
#include <vector>
#include <cmath>

void normalize(std::vector<double>& v) {
}

double mean(const std::vector<double>& v) {
    return 0;
}

void minmax(const std::vector<double>& v, double& lo, double& hi) {
}
```

## Driver
```cpp
#include <iostream>
#include <iomanip>
int main() {
    std::vector<double> v;
    for (double x; std::cin >> x; ) v.push_back(x);
    double lo = -999, hi = -999;
    minmax(v, lo, hi);
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "mean=" << mean(v) << " lo=" << lo << " hi=" << hi << '\n';
    normalize(v);
    for (double x : v) std::cout << x << ' ';
    std::cout << '\n';
}
```

## Tests
=== sample
2 -4 1
---
mean=-0.333 lo=-4.000 hi=2.000
0.500 -1.000 0.250 
=== hidden
0 0
---
mean=0.000 lo=0.000 hi=0.000
0.000 0.000 
=== hidden

---
mean=0.000 lo=-999.000 hi=-999.000


## Hints
- A non-const reference (`std::vector<double>&`) lets the function modify the caller's vector; `const&` reads it without copying.
- `normalize`: find the largest absolute value first; if it is 0, return early, otherwise divide every element (loop with `double& x`).
- `minmax` returns two values through the reference parameters `lo` and `hi`; leave them untouched for an empty vector.

## Solution
```cpp
#include <vector>
#include <cmath>

void normalize(std::vector<double>& v) {
    double m = 0;
    for (double x : v) m = std::max(m, std::abs(x));
    if (m == 0) return;
    for (double& x : v) x /= m;
}

double mean(const std::vector<double>& v) {
    if (v.empty()) return 0;
    double s = 0;
    for (double x : v) s += x;
    return s / static_cast<double>(v.size());
}

void minmax(const std::vector<double>& v, double& lo, double& hi) {
    if (v.empty()) return;
    lo = hi = v[0];
    for (double x : v) {
        if (x < lo) lo = x;
        if (x > hi) hi = x;
    }
}
```

The three signatures say three different things. `std::vector<double>&` means "I will modify your vector". `const std::vector<double>&` means "I only read it, and no copy is made". `double&` output parameters write results back. The `for (double& x : v)` loop in `normalize` must use a reference, because a plain `double x` would scale copies.
