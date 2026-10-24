---
id: cpp-generic-stats
title: Generic Statistics Templates
difficulty: Medium
order: 1
tags: function templates, deduction, non-type parameters, iterators
---
## Statement
Write **function templates** that work with any container of numbers (`std::vector`, `std::array`, `std::list`, `std::deque`, and even C arrays through the overloads below):

```cpp
template <typename Container> double mean(const Container& c);         // throws std::invalid_argument if empty
template <typename Container> auto max_element_value(const Container& c); // returns the element type (by value); throws if empty
template <typename Container> std::vector<typename Container::value_type> top_k(const Container& c, std::size_t k);  // k largest, descending
template <typename T, std::size_t N> constexpr std::size_t length(const T (&)[N]);    // array length, usable in static_assert
template <typename T> T clamp_to(T value, T lo, T hi);                  // like std::clamp
template <typename To, typename From> To checked_cast(From value);      // throws std::out_of_range if value doesn't fit in To
```

`checked_cast` must work for any integral or floating `To`/`From`: convert, convert back, and check that the value round-trips **and** that the sign didn't change (so `checked_cast<unsigned>(-1)` and `checked_cast<std::int8_t>(300)` throw, while `checked_cast<int>(3.0)` returns 3 and `checked_cast<int>(3.5)` throws).

## Starter
```cpp
#include <vector>
#include <stdexcept>
#include <cstddef>
#include <algorithm>

template <typename Container>
double mean(const Container& c) { return 0; }
```

## Driver
```cpp
#include <iostream>
#include <array>
#include <list>
#include <deque>
#include <string>
#include <cstdint>

int raw[] = {4, 8, 15, 16, 23, 42};
static_assert(length(raw) == 6, "length must be constexpr");

template <typename F>
void attempt(const std::string& label, F f) {
    try { auto r = f(); std::cout << label << ": " << r << '\n'; }
    catch (const std::invalid_argument&) { std::cout << label << ": invalid_argument\n"; }
    catch (const std::out_of_range&) { std::cout << label << ": out_of_range\n"; }
}

int main() {
    int n;
    std::cin >> n;
    std::vector<int> v(n);
    for (int& x : v) std::cin >> x;
    std::list<long long> l(v.begin(), v.end());
    std::deque<double> d;
    for (int x : v) d.push_back(x / 2.0);
    std::array<float, 3> a{1.5f, -2.25f, 9.0f};

    attempt("mean vector", [&] { return mean(v); });
    attempt("mean list", [&] { return mean(l); });
    attempt("mean array", [&] { return mean(a); });
    attempt("mean empty", [&] { return mean(std::vector<int>{}); });
    attempt("max deque", [&] { return max_element_value(d); });
    attempt("max list", [&] { return max_element_value(l); });
    attempt("max empty", [&] { return max_element_value(std::list<int>{}); });
    auto top = top_k(v, 3);
    std::cout << "top3:";
    for (int x : top) std::cout << ' ' << x;
    std::cout << "\ntop99 size: " << top_k(l, 99).size() << '\n';
    std::cout << "length raw: " << length(raw) << '\n';
    std::cout << "clamp: " << clamp_to(15, 0, 10) << ' ' << clamp_to(-2.5, -1.0, 1.0) << ' '
              << clamp_to(std::string("m"), std::string("a"), std::string("k")) << '\n';
    attempt("cast int<-3.0", [] { return checked_cast<int>(3.0); });
    attempt("cast int<-3.5", [] { return checked_cast<int>(3.5); });
    attempt("cast unsigned<--1", [] { return checked_cast<unsigned>(-1); });
    attempt("cast int8<-300", [] { return static_cast<int>(checked_cast<std::int8_t>(300)); });
    attempt("cast int8<--128", [] { return static_cast<int>(checked_cast<std::int8_t>(-128)); });
    attempt("cast double<-big", [] { return checked_cast<double>(9007199254740993LL); });
    attempt("cast long<-1e18", [] { return checked_cast<long long>(1e18); });
}
```

## Tests
=== sample
5
3 9 -4 9 1
---
mean vector: 3.6
mean list: 3.6
mean array: 2.75
mean empty: invalid_argument
max deque: 4.5
max list: 9
max empty: invalid_argument
top3: 9 9 3
top99 size: 5
length raw: 6
clamp: 10 -1 k
cast int<-3.0: 3
cast int<-3.5: out_of_range
cast unsigned<--1: out_of_range
cast int8<-300: out_of_range
cast int8<--128: -128
cast double<-big: out_of_range
cast long<-1e18: 1000000000000000000
=== hidden
1
-7
---
mean vector: -7
mean list: -7
mean array: 2.75
mean empty: invalid_argument
max deque: -3.5
max list: -7
max empty: invalid_argument
top3: -7
top99 size: 1
length raw: 6
clamp: 10 -1 k
cast int<-3.0: 3
cast int<-3.5: out_of_range
cast unsigned<--1: out_of_range
cast int8<-300: out_of_range
cast int8<--128: -128
cast double<-big: out_of_range
cast long<-1e18: 1000000000000000000
=== hidden
8
100 200 300 400 500 600 700 800
---
mean vector: 450
mean list: 450
mean array: 2.75
mean empty: invalid_argument
max deque: 400
max list: 800
max empty: invalid_argument
top3: 800 700 600
top99 size: 8
length raw: 6
clamp: 10 -1 k
cast int<-3.0: 3
cast int<-3.5: out_of_range
cast unsigned<--1: out_of_range
cast int8<-300: out_of_range
cast int8<--128: -128
cast double<-big: out_of_range
cast long<-1e18: 1000000000000000000

## Hints
- `mean`: `std::accumulate(c.begin(), c.end(), 0.0) / std::size(c)`. The `0.0` makes the sum a `double`. Note that `std::size` works for every container here.
- `max_element_value`: dereference `std::max_element(...)` after checking `c.begin() == c.end()`.
- `top_k`: copy into a `std::vector<typename Container::value_type>`, `std::sort` with `std::greater<>()`, then `resize(std::min(k, size))`.
- `length`: a reference to an array keeps `N` in its type: `const T (&)[N]`.
- `checked_cast`: `auto r = static_cast<To>(value); if (static_cast<From>(r) != value || ((r < To{}) != (value < From{}))) throw ...`. Converting a float that's out of range for an integer type is UB, so first check the range with `std::numeric_limits<To>` when `From` is floating-point.

## Solution
```cpp
#include <vector>
#include <stdexcept>
#include <cstddef>
#include <algorithm>
#include <numeric>
#include <iterator>
#include <limits>
#include <type_traits>
#include <functional>

template <typename Container>
double mean(const Container& c) {
    if (std::begin(c) == std::end(c)) throw std::invalid_argument("mean of empty container");
    return std::accumulate(std::begin(c), std::end(c), 0.0) / static_cast<double>(std::size(c));
}

template <typename Container>
auto max_element_value(const Container& c) {
    if (std::begin(c) == std::end(c)) throw std::invalid_argument("max of empty container");
    return *std::max_element(std::begin(c), std::end(c));
}

template <typename Container>
std::vector<typename Container::value_type> top_k(const Container& c, std::size_t k) {
    std::vector<typename Container::value_type> v(std::begin(c), std::end(c));
    std::sort(v.begin(), v.end(), std::greater<>());
    v.resize(std::min(k, v.size()));
    return v;
}

template <typename T, std::size_t N>
constexpr std::size_t length(const T (&)[N]) { return N; }

template <typename T>
T clamp_to(T value, T lo, T hi) { return value < lo ? lo : hi < value ? hi : value; }

template <typename To, typename From>
To checked_cast(From value) {
    if constexpr (std::is_floating_point_v<From> && std::is_integral_v<To>) {
        // out-of-range float -> int conversion is UB, so check the range first
        if (!(value >= static_cast<From>(std::numeric_limits<To>::lowest()) &&
              value <= static_cast<From>(std::numeric_limits<To>::max())))
            throw std::out_of_range("value out of range");
    }
    To r = static_cast<To>(value);
    if (static_cast<From>(r) != value || ((r < To{}) != (value < From{})))
        throw std::out_of_range("value does not fit");
    return r;
}
```

- **One template, every container:** `std::begin`, `std::end` and `std::size` work with all the standard containers (and with C arrays), so a single definition serves `vector`, `list`, `deque` and `array`. The compiler instantiates one optimised copy per container type.
- **`auto` return type** lets `max_element_value` return exactly the element type (`long long` for the list, `double` for the deque).
- **`typename Container::value_type`** names a type that depends on the template parameter, so it needs the `typename` disambiguator.
- **A non-type parameter `N`** deduced from `const T (&)[N]` gives a compile-time array length, verified by the driver's `static_assert`.
- **`checked_cast`** is the idea behind `gsl::narrow`: the round-trip catches truncation and precision loss (`9007199254740993` doesn't survive conversion to `double`), and the sign check catches wrap-around (`-1` becomes `4294967295` as `unsigned`, which round-trips back to `-1`!).
