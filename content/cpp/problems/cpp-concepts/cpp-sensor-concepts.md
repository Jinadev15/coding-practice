---
id: cpp-sensor-concepts
title: Constraining a Sensor Library with Concepts
difficulty: Hard
order: 1
tags: concepts, requires expressions, subsumption, constrained overloads
---
## Statement
A robotics library processes many kinds of sensor drivers **without virtual functions**: all dispatch happens at compile time. Define these **concepts** and constrained functions:

```cpp
template <class T> concept Sensor =                 // read() returns something convertible to double,
                                                    // name() returns exactly std::string, and both work on a const T
template <class T> concept CalibratableSensor =     // Sensor + calibrate(double offset) is valid (non-const)
                                                    //        + offset() returns double
template <class T> concept BatchSensor =            // Sensor + read_batch(std::size_t n) returns a std::vector<double>
template <class R> concept SensorRange =            // a std::ranges::input_range whose elements are Sensors
```

Functions:
- `double sample(const Sensor auto& s, int n)`: the average of n `read()`s. **Overloaded** by a more constrained version for `BatchSensor` that calls `read_batch(n)` once (prints nothing extra, but returns the average of the batch). Overload resolution must pick it automatically (subsumption).
- `std::string describe(const Sensor auto& s)` → `NAME (basic)`, `NAME (calibratable, offset=X)` or `NAME (batch)`, using `if constexpr` with the concepts. If a sensor is both calibratable and batch, describe it as calibratable.
- `void zero_all(SensorRange auto& sensors)`: for each element that's a `CalibratableSensor`, call `calibrate(-s.read())`.
- `double total(const SensorRange auto& sensors)`: the sum of one `read()` from each element.

The driver uses `static_assert` to check which provided types satisfy which concepts, including types that **almost** qualify (a `name()` returning `const char*`, a non-const `read()`, a `read()` returning `std::string`).

## Starter
```cpp
#include <concepts>
#include <ranges>
#include <string>
#include <vector>

template <class T> concept Sensor = true;
template <class T> concept CalibratableSensor = Sensor<T>;
template <class T> concept BatchSensor = Sensor<T>;
template <class R> concept SensorRange = true;

double sample(const auto& s, int n) { return 0; }
std::string describe(const auto& s) { return ""; }
void zero_all(auto& sensors) {}
double total(const auto& sensors) { return 0; }
```

## Driver
```cpp
#include <iostream>
#include <list>
#include <array>
#include <numeric>

struct Thermo {                                     // basic
    double t = 21.5;
    double read() const { return t; }
    std::string name() const { return "thermo"; }
};
struct Imu {                                        // calibratable
    double raw = 9.9, off = 0;
    double read() const { return raw + off; }
    std::string name() const { return "imu"; }
    void calibrate(double o) { off += o; }
    double offset() const { return off; }
};
struct Lidar {                                      // batch
    mutable int calls = 0;
    float read() const { return 4.0f; }             // float converts to double: fine
    std::string name() const { return "lidar"; }
    std::vector<double> read_batch(std::size_t n) const { ++calls; return std::vector<double>(n, 3.0); }
};
struct Fancy : Imu {                                // calibratable AND batch
    std::string name() const { return "fancy"; }
    std::vector<double> read_batch(std::size_t n) const { return std::vector<double>(n, read()); }
};
struct BadName { double read() const { return 1; } const char* name() const { return "x"; } };
struct NonConstRead { double read() { return 1; } std::string name() const { return "n"; } };
struct StringRead { std::string read() const { return "1"; } std::string name() const { return "s"; } };
struct NoOffset { double read() const { return 1; } std::string name() const { return "o"; } void calibrate(double) {} };

static_assert(Sensor<Thermo> && Sensor<Imu> && Sensor<Lidar> && Sensor<Fancy>);
static_assert(!Sensor<BadName> && !Sensor<NonConstRead> && !Sensor<StringRead> && !Sensor<int>);
static_assert(CalibratableSensor<Imu> && CalibratableSensor<Fancy> && !CalibratableSensor<Thermo> && !CalibratableSensor<NoOffset>);
static_assert(BatchSensor<Lidar> && BatchSensor<Fancy> && !BatchSensor<Imu>);
static_assert(SensorRange<std::vector<Imu>> && SensorRange<std::list<Thermo>> && SensorRange<std::array<Lidar, 2>>);
static_assert(!SensorRange<std::vector<int>> && !SensorRange<Thermo>);

int main() {
    Thermo th;
    Imu imu;
    Lidar li;
    Fancy fy;
    std::cout << describe(th) << " | " << describe(imu) << " | " << describe(li) << " | " << describe(fy) << '\n';
    std::cout << "sample thermo " << sample(th, 3) << ", lidar " << sample(li, 5) << " (batch calls " << li.calls << ")\n";
    std::vector<Imu> imus(3);
    imus[1].raw = 10.5;
    std::cout << "total before " << total(imus) << '\n';
    zero_all(imus);
    std::cout << "total after " << total(imus) << ", " << describe(imus[1]) << '\n';
    std::list<Thermo> ths(2);
    zero_all(ths);                                  // nothing calibratable: no-op
    std::cout << "thermo total " << total(ths) << '\n';
}
```

## Tests
=== sample
---
thermo (basic) | imu (calibratable, offset=0) | lidar (batch) | fancy (calibratable, offset=0)
sample thermo 21.5, lidar 3 (batch calls 1)
total before 30.3
total after 0, imu (calibratable, offset=-10.5)
thermo total 43
=== hidden
x
---
thermo (basic) | imu (calibratable, offset=0) | lidar (batch) | fancy (calibratable, offset=0)
sample thermo 21.5, lidar 3 (batch calls 1)
total before 30.3
total after 0, imu (calibratable, offset=-10.5)
thermo total 43

## Hints
- `concept Sensor = requires(const T& s) { { s.read() } -> std::convertible_to<double>; { s.name() } -> std::same_as<std::string>; };`. Using `const T&` in the requires-parameter list enforces const-callability.
- Refine by conjunction: `concept CalibratableSensor = Sensor<T> && requires(T& s, double d) { s.calibrate(d); { std::as_const(s).offset() } -> std::same_as<double>; };`. Subsumption works because `BatchSensor` is literally `Sensor<T> && ...`.
- `SensorRange`: `std::ranges::input_range<R> && Sensor<std::ranges::range_value_t<R>>`.
- In `zero_all`, `if constexpr (CalibratableSensor<std::ranges::range_value_t<decltype(sensors)>>)`. Use `std::remove_cvref_t` on the range type first.
- Note that `sample(li, 5)` must return 3 (the batch value), not 4 (the `read()` value), which proves the batch overload was chosen.

## Solution
```cpp
#include <concepts>
#include <ranges>
#include <string>
#include <vector>
#include <numeric>
#include <utility>
#include <format>
#include <type_traits>

template <class T>
concept Sensor = requires(const T& s) {
    { s.read() } -> std::convertible_to<double>;
    { s.name() } -> std::same_as<std::string>;
};

template <class T>
concept CalibratableSensor = Sensor<T> && requires(T& s, double d) {
    s.calibrate(d);
    { std::as_const(s).offset() } -> std::same_as<double>;
};

template <class T>
concept BatchSensor = Sensor<T> && requires(const T& s, std::size_t n) {
    { s.read_batch(n) } -> std::same_as<std::vector<double>>;
};

template <class R>
concept SensorRange = std::ranges::input_range<R> && Sensor<std::ranges::range_value_t<R>>;

double sample(const Sensor auto& s, int n) {
    double sum = 0;
    for (int i = 0; i < n; ++i) sum += s.read();
    return sum / n;
}

double sample(const BatchSensor auto& s, int n) {           // more constrained: preferred when satisfied
    auto v = s.read_batch(static_cast<std::size_t>(n));
    return std::accumulate(v.begin(), v.end(), 0.0) / n;
}

std::string describe(const Sensor auto& s) {
    using T = std::remove_cvref_t<decltype(s)>;
    if constexpr (CalibratableSensor<T>) return std::format("{} (calibratable, offset={})", s.name(), s.offset());
    else if constexpr (BatchSensor<T>) return s.name() + " (batch)";
    else return s.name() + " (basic)";
}

void zero_all(SensorRange auto& sensors) {
    using Elem = std::ranges::range_value_t<std::remove_cvref_t<decltype(sensors)>>;
    if constexpr (CalibratableSensor<Elem>)
        for (auto& s : sensors) s.calibrate(-s.read());
}

double total(const SensorRange auto& sensors) {
    double t = 0;
    for (const auto& s : sensors) t += s.read();
    return t;
}
```

- **Concepts as interfaces:** `Sensor` states the driver contract (const `read()` convertible to `double`, `name()` returning exactly `std::string`) and is checked **at compile time, with zero run-time cost**. The `static_assert`s document which almost-right types are rejected, and why: `const char*` isn't `std::string`, a non-const `read()` fails on a `const T&`, and `std::string` doesn't convert to `double`.
- **Refinement and subsumption:** `BatchSensor` is defined *as* `Sensor<T> && ...`, so the compiler knows it's more specific, and `sample(lidar, n)` picks the batch overload automatically (returning 3, not 4, with one batch call). This replaces tag dispatch.
- **`if constexpr` + concepts** selects behaviour inside one function, and **range concepts** (`input_range`, `range_value_t`) constrain containers of sensors.

Compare this with the virtual `ISensor` interface from the Polymorphism lesson. Concepts give the same documentation and checking, but everything is inlined. The price is that you can't store mixed sensor types in one container without type erasure.
