---
id: cpp-ownership-refactor
title: Remove the Naked new
difficulty: Medium
order: 1
tags: new/delete, leaks, vector, refactoring
---
## Statement
The starter code builds a list of sensor readings with raw `new[]`/`delete[]` and **leaks** whenever a reading is invalid (it returns early). Rewrite `process` so that:

- it uses `std::vector<double>` (no `new`/`delete` anywhere)
- invalid input (a negative reading) makes it return `std::nullopt` **without leaking**
- otherwise it returns the mean of the readings after removing the single largest value (if there are at least 2 readings; with 1 reading, return that reading)

The driver counts allocations through a global hook: your solution must leave **zero live heap allocations** made by `process` after it returns.

## Starter
```cpp
#include <optional>
#include <vector>

std::optional<double> process(const std::vector<double>& input) {
    double* buf = new double[input.size()];
    for (std::size_t i = 0; i < input.size(); ++i) {
        if (input[i] < 0) return std::nullopt;     // LEAK!
        buf[i] = input[i];
    }
    double sum = 0, mx = buf[0];
    for (std::size_t i = 0; i < input.size(); ++i) { sum += buf[i]; if (buf[i] > mx) mx = buf[i]; }
    double r = input.size() == 1 ? buf[0] : (sum - mx) / (input.size() - 1);
    delete[] buf;
    return r;
}
```

## Driver
```cpp
#include <iostream>
#include <iomanip>
#include <cstdlib>
#include <new>
static long live = 0;
void* operator new(std::size_t n) { ++live; if (void* p = std::malloc(n)) return p; throw std::bad_alloc(); }
void* operator new[](std::size_t n) { ++live; if (void* p = std::malloc(n)) return p; throw std::bad_alloc(); }
void operator delete(void* p) noexcept { if (p) { --live; std::free(p); } }
void operator delete[](void* p) noexcept { if (p) { --live; std::free(p); } }
void operator delete(void* p, std::size_t) noexcept { if (p) { --live; std::free(p); } }
void operator delete[](void* p, std::size_t) noexcept { if (p) { --live; std::free(p); } }
int main() {
    int t; std::cin >> t;
    std::cout << std::fixed << std::setprecision(2);
    while (t--) {
        int n; std::cin >> n;
        std::vector<double> in(n);
        for (auto& x : in) std::cin >> x;
        long before = live;
        auto r = process(in);
        long leaked = live - before;
        if (r) std::cout << *r; else std::cout << "invalid";
        std::cout << " leaked=" << leaked << '\n';
    }
}
```

## Tests
=== sample
2
4 1 2 3 10
3 5 -1 2
---
2.00 leaked=0
invalid leaked=0
=== hidden
2
1 7.5
2 4 4
---
7.50 leaked=0
4.00 leaked=0

## Hints
- `std::vector<double> buf(input.begin(), input.end());`, or simply work on `input` directly, since it's already a vector.
- Any `return` now exits cleanly, because the vector's destructor frees its memory.

## Solution
```cpp
#include <optional>
#include <vector>
#include <algorithm>
#include <numeric>

std::optional<double> process(const std::vector<double>& input) {
    std::vector<double> buf;
    buf.reserve(input.size());
    for (double x : input) {
        if (x < 0) return std::nullopt;     // no leak: buf's destructor runs
        buf.push_back(x);
    }
    if (buf.size() == 1) return buf[0];
    double sum = std::accumulate(buf.begin(), buf.end(), 0.0);
    double mx = *std::max_element(buf.begin(), buf.end());
    return (sum - mx) / static_cast<double>(buf.size() - 1);
}
```

The starter leaks one allocation on every invalid input, and the driver's counting `operator new` makes that visible as `leaked=1`. With `std::vector`, **every** exit path, early returns and exceptions included, releases the memory. That's RAII doing the bookkeeping, and it's why modern C++ guidelines say "no naked new".
