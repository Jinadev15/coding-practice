---
id: cpp-dimensional-units
title: Compile-Time Dimensional Analysis with Strong Types
difficulty: Hard
order: 1
tags: strong types, templates, constexpr, operator overloading, concepts, value types
time_limit: 4
---
## Statement
Make unit errors impossible to compile. Implement `template <int L, int M, int T> class Quantity`: a double tagged with exponents of length, mass and time. Then use it in a robot kinematics helper.

**`Quantity<L, M, T>`** requirements (everything `constexpr`):
- `explicit` construction from `double`, and `double value() const`. There's no implicit conversion to or from `double`.
- `+` and `-` (binary, between **identical** dimensions only), unary `-`, and `+=`/`-=`.
- `*` and `/` between quantities, **adding or subtracting the exponents**.
- `*` by a `double` on either side, and `/` by a `double`.
- Comparison with `==` and `<=>`, between identical dimensions only.

**Aliases:**

| Alias | L, M, T |
|---|---|
| `Scalar` | 0, 0, 0 |
| `Length` | 1, 0, 0 |
| `Mass` | 0, 1, 0 |
| `Time` | 0, 0, 1 |
| `Velocity` | 1, 0, −1 |
| `Acceleration` | 1, 0, −2 |
| `Force` | 1, 1, −2 |
| `Energy` | 2, 1, −2 |

**Literals:** `_m`, `_kg` and `_s` for both floating (`2.5_m`) and integer (`3_s`) literals.

**Functions:**
- `Velocity average_speed(Length, Time)`
- `Energy kinetic_energy(Mass, Velocity)`, which is ½mv²
- `Time stopping_time(Velocity, Acceleration)`, which is v/a
- `Length stopping_distance(Velocity, Acceleration)`, which is v²/(2a)

The judge **static_asserts** that, for example, `Length + Time` and `Length == Time` don't compile, that `Length * Length / Length` is a `Length`, and that it all works in constant expressions.

## Starter
```cpp
using Length = double;
using Time = double;
using Mass = double;
using Velocity = double;
using Acceleration = double;
using Energy = double;
using Force = double;
using Scalar = double;
template <int L, int M, int T> using Quantity = double;

constexpr Length operator""_m(long double v) { return v; }
constexpr Length operator""_m(unsigned long long v) { return v; }
constexpr Mass operator""_kg(long double v) { return v; }
constexpr Mass operator""_kg(unsigned long long v) { return v; }
constexpr Time operator""_s(long double v) { return v; }
constexpr Time operator""_s(unsigned long long v) { return v; }

constexpr Velocity average_speed(Length d, Time t) { return d / t; }
constexpr Energy kinetic_energy(Mass m, Velocity v) { return m * v * v; }
constexpr Time stopping_time(Velocity v, Acceleration a) { return v / a; }
constexpr Length stopping_distance(Velocity v, Acceleration a) { return v * v / a; }
```

## Driver
```cpp
#include <cmath>
#include <cstdio>
#include <iostream>
#include <string>
#include <type_traits>

template <class A, class B> concept Addable = requires(A a, B b) { a + b; };
template <class A, class B> concept Comparable = requires(A a, B b) { a == b; };
template <class A> concept FromDouble = std::is_convertible_v<double, A>;
template <class A> concept ToDouble = std::is_convertible_v<A, double>;

static_assert(!Addable<Length, Time>, "meters + seconds must not compile");
static_assert(!Addable<Velocity, Acceleration>);
static_assert(Addable<Length, Length>);
static_assert(!Comparable<Mass, Time>);
static_assert(!FromDouble<Length> && !ToDouble<Length>, "no implicit conversions");
static_assert(std::is_same_v<decltype(Length(2) * Length(3) / Length(1)), Length>);
static_assert(std::is_same_v<decltype(Mass(1) * Acceleration(1)), Force>);
static_assert(std::is_same_v<decltype(Force(1) * Length(1)), Energy>);
static_assert(std::is_same_v<decltype(Length(1) / Length(1)), Scalar>);
static_assert(std::is_same_v<decltype(1.0_m / 2_s), Velocity>);
static_assert(std::is_same_v<decltype(2.0 * Time(3)), Time> && std::is_same_v<decltype(Time(3) / 2.0), Time>);
constexpr Velocity kV = average_speed(100_m, 8_s);
static_assert(kV.value() == 12.5);
static_assert(stopping_distance(Velocity(10), Acceleration(2)) == Length(25));
static_assert(Length(3) < Length(4) && Length(4) >= 4_m && Length(2) != Length(3));
static_assert(sizeof(Velocity) == sizeof(double), "zero overhead");

int main() {
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "kinematics") {
            Length d = 120.0_m; Time t = 15_s;
            Velocity v = average_speed(d, t);
            Mass m = 35_kg;
            Acceleration brake(2.5);
            std::printf("v=%.3f m/s  KE=%.3f J  t_stop=%.3f s  d_stop=%.3f m\n", v.value(), kinetic_energy(m, v).value(),
                        stopping_time(v, brake).value(), stopping_distance(v, brake).value());
            Length path = 0_m;
            for (double seg : {1.5, 2.25, 4.0}) path += Length(seg);
            path -= 0.75_m;
            std::printf("path=%.3f m  neg=%.3f  scaled=%.3f  ratio=%.3f\n", path.value(), (-path).value(), (path * 2.0).value(), (path / 7.0_m).value());
            Force f = m * brake; Energy work = f * stopping_distance(v, brake);
            std::printf("brake force=%.3f N  work=%.3f J  equals KE: %d\n", f.value(), work.value(), std::abs(work.value() - kinetic_energy(m, v).value()) < 1e-9);
        } else if (cmd == "fleet") {
            double total = 0; int n = 0;
            for (int i = 1; i <= 100000; ++i) {
                Length leg(i % 97 + 0.5); Time dt((i % 13) + 1.0);
                Velocity v = leg / dt;
                if (v > Velocity(10)) { total += kinetic_energy(Mass(20 + i % 5), v).value(); ++n; }
            }
            std::printf("fast legs %d total KE %.4f J\n", n, total);
        }
    }
}
```

## Tests
=== sample
kinematics
---
v=8.000 m/s  KE=1120.000 J  t_stop=3.200 s  d_stop=12.800 m
path=7.000 m  neg=-7.000  scaled=14.000  ratio=1.000
brake force=87.500 N  work=1120.000 J  equals KE: 1
=== hidden
fleet
---
fast legs 33543 total KE 395540876.2814 J

## Hints
- `template <int L, int M, int T> class Quantity { double v_; public: constexpr explicit Quantity(double v) : v_(v) {} constexpr double value() const { return v_; } ... };`. Member `operator+(Quantity)` only accepts the same instantiation, which is exactly the type check you want.
- Multiplication between different dimensions needs a free function template: `template <int L1, int M1, int T1, int L2, int M2, int T2> constexpr Quantity<L1 + L2, M1 + M2, T1 + T2> operator*(Quantity<L1, M1, T1> a, Quantity<L2, M2, T2> b)`.
- `constexpr auto operator<=>(const Quantity&) const = default;` provides `==` and the ordering in one line.
- Literal operators: `constexpr Length operator""_m(long double v) { return Length(static_cast<double>(v)); }`, plus an `unsigned long long` overload.

## Solution
```cpp
#include <compare>

template <int L, int M, int T>
class Quantity {
public:
    constexpr explicit Quantity(double v) : v_(v) {}
    constexpr double value() const { return v_; }

    constexpr Quantity operator+(Quantity o) const { return Quantity(v_ + o.v_); }
    constexpr Quantity operator-(Quantity o) const { return Quantity(v_ - o.v_); }
    constexpr Quantity operator-() const { return Quantity(-v_); }
    constexpr Quantity& operator+=(Quantity o) { v_ += o.v_; return *this; }
    constexpr Quantity& operator-=(Quantity o) { v_ -= o.v_; return *this; }
    constexpr Quantity operator*(double s) const { return Quantity(v_ * s); }
    constexpr Quantity operator/(double s) const { return Quantity(v_ / s); }
    friend constexpr Quantity operator*(double s, Quantity q) { return Quantity(s * q.v_); }

    constexpr auto operator<=>(const Quantity&) const = default;   // same dimensions only

private:
    double v_;
};

template <int L1, int M1, int T1, int L2, int M2, int T2>
constexpr Quantity<L1 + L2, M1 + M2, T1 + T2> operator*(Quantity<L1, M1, T1> a, Quantity<L2, M2, T2> b) {
    return Quantity<L1 + L2, M1 + M2, T1 + T2>(a.value() * b.value());
}
template <int L1, int M1, int T1, int L2, int M2, int T2>
constexpr Quantity<L1 - L2, M1 - M2, T1 - T2> operator/(Quantity<L1, M1, T1> a, Quantity<L2, M2, T2> b) {
    return Quantity<L1 - L2, M1 - M2, T1 - T2>(a.value() / b.value());
}

using Scalar = Quantity<0, 0, 0>;
using Length = Quantity<1, 0, 0>;
using Mass = Quantity<0, 1, 0>;
using Time = Quantity<0, 0, 1>;
using Velocity = Quantity<1, 0, -1>;
using Acceleration = Quantity<1, 0, -2>;
using Force = Quantity<1, 1, -2>;
using Energy = Quantity<2, 1, -2>;

constexpr Length operator""_m(long double v) { return Length(static_cast<double>(v)); }
constexpr Length operator""_m(unsigned long long v) { return Length(static_cast<double>(v)); }
constexpr Mass operator""_kg(long double v) { return Mass(static_cast<double>(v)); }
constexpr Mass operator""_kg(unsigned long long v) { return Mass(static_cast<double>(v)); }
constexpr Time operator""_s(long double v) { return Time(static_cast<double>(v)); }
constexpr Time operator""_s(unsigned long long v) { return Time(static_cast<double>(v)); }

constexpr Velocity average_speed(Length d, Time t) { return d / t; }
constexpr Energy kinetic_energy(Mass m, Velocity v) { return 0.5 * (m * v * v); }
constexpr Time stopping_time(Velocity v, Acceleration a) { return v / a; }
constexpr Length stopping_distance(Velocity v, Acceleration a) { return v * v / (2.0 * a); }
```

- **Dimensions live in the type**, so the compiler does dimensional analysis: `Length + Time` has no matching `operator+`, and `Mass * Acceleration` *is* a `Force`. The formulas in the helpers are checked against physics at compile time. Writing `v / a` as the stopping distance wouldn't compile, because it's a `Time`.
- **Zero overhead**: a `Quantity` is one `double`, everything is `constexpr`, and optimised code is identical to raw doubles. The static_assert on `sizeof` and the constant-expression checks prove it.
- **No implicit conversions** (`explicit` constructor, `value()` accessor): the boundary between unitless numbers and physical quantities is always visible in the code.
- **Value semantics**: quantities are copyable, comparable and immutable-friendly. That's the right kind of type for physical values (see the value vs entity discussion in the lesson).
- `std::chrono::duration` applies the same idea to time, and mp-units generalises it to all SI dimensions with unit conversions.
