---
id: cpp-crtp-units
title: Compile-Time Units and CRTP Mixins
difficulty: Expert
order: 1
tags: CRTP, template metaprogramming, constexpr, strong types, dimensional analysis
---
## Statement
The Mars Climate Orbiter was lost because one team used pound-force seconds and another newton-seconds. Prevent such bugs **at compile time** with a dimensional-analysis type and CRTP mixins.

**Part 1: dimensioned quantities (template metaprogramming).**

```cpp
template <int M, int L, int T>        // exponents of mass (kg), length (m) and time (s)
struct Quantity {
    double value;
    // + and - only between identical dimensions (anything else must not compile)
    // * and / combine dimensions: Quantity<M1,L1,T1> * Quantity<M2,L2,T2> -> Quantity<M1+M2, L1+L2, T1+T2>
    // scalar * Quantity and Quantity * scalar
    // comparisons (<, ==) only between identical dimensions
};
using Scalar = Quantity<0, 0, 0>;  using Length = Quantity<0, 1, 0>;  using Time = Quantity<0, 0, 1>;
using Mass = Quantity<1, 0, 0>;    using Speed = Quantity<0, 1, -1>;  using Accel = Quantity<0, 1, -2>;
using Force = Quantity<1, 1, -2>;
constexpr Length operator""_m(long double v);   constexpr Time operator""_s(long double v);
constexpr Mass operator""_kg(long double v);    // also integer-literal overloads (unsigned long long)
std::string unit_string(const Quantity<M,L,T>&);  // e.g. "kg*m/s^2", "m/s", "m", "1" (dimensionless), "s^-1"... see below
```

Unit string format: numerator units in the order `kg`, `m`, `s` with `^n` when n > 1, joined by `*`, then `/` and the denominator units the same way. A dimensionless quantity is `1`. With nothing in the numerator it's `1/s`.

**Part 2: CRTP mixins.** Write `template <class D> struct Comparable` (given `D::key()`, provides `==, !=, <, <=, >, >=`), `template <class D> struct Printable` (provides `std::string str() const` returning `D::type_name() + "(" + std::to_string(self.key()) + ")"`), and `template <class D> struct Counted` (counts live instances **per derived type**: `D::live()`). The driver derives `RobotId` and `TaskId` from all three, and checks that their counts are independent and that comparing a `RobotId` with a `TaskId` doesn't compile.

## Starter
```cpp
#include <string>

template <int M, int L, int T>
struct Quantity {
    double value;
};
```

## Driver
```cpp
#include <iostream>
#include <type_traits>
#include <concepts>

struct RobotId : Comparable<RobotId>, Printable<RobotId>, Counted<RobotId> {
    int k;
    explicit RobotId(int k) : k(k) {}
    int key() const { return k; }
    static std::string type_name() { return "RobotId"; }
};
struct TaskId : Comparable<TaskId>, Printable<TaskId>, Counted<TaskId> {
    int k;
    explicit TaskId(int k) : k(k) {}
    int key() const { return k; }
    static std::string type_name() { return "TaskId"; }
};

template <class A, class B> concept Addable = requires(A a, B b) { a + b; };
template <class A, class B> concept LessComparable = requires(A a, B b) { a < b; };
static_assert(Addable<Length, Length> && !Addable<Length, Time> && !Addable<Mass, Force>);
static_assert(std::is_same_v<decltype(Length{} / Time{}), Speed>);
static_assert(std::is_same_v<decltype(Mass{} * (Length{} / (Time{} * Time{}))), Force>);
static_assert(LessComparable<RobotId, RobotId> && !LessComparable<RobotId, TaskId>);
static_assert(!LessComparable<Length, Time>);
constexpr Length track = 2.0_m + 50_m;
static_assert(track.value == 52.0, "literals and + must be constexpr");

int main() {
    Length d = 100.0_m;
    Time t = 9.58_s;
    Speed v = d / t;
    Accel a = v / t;
    Force f = 80.0_kg * a;
    std::cout << v.value << ' ' << unit_string(v) << '\n';
    std::cout << f.value << ' ' << unit_string(f) << '\n';
    std::cout << unit_string(Scalar{}) << ' ' << unit_string(1.0 / t) << ' ' << unit_string(d * d) << ' '
              << unit_string(f * d / t) << ' ' << unit_string(Mass{} / (Length{} * Length{} * Length{})) << '\n';
    std::cout << ((2 * d) < (250_m)) << (d == 100_m) << ' ' << (d - 40_m).value << ' ' << (d / 50_m).value << '\n';
    {
        RobotId r1(5), r2(9);
        TaskId t1(5);
        std::cout << (r1 < r2) << (r1 == RobotId(5)) << (r2 >= r1) << (r1 != r2) << ' ' << r2.str() << ' ' << t1.str() << '\n';
        std::cout << "live robots " << RobotId::live() << ", tasks " << TaskId::live() << '\n';
    }
    std::cout << "after scope " << RobotId::live() << ' ' << TaskId::live() << '\n';
}
```

## Tests
=== sample
---
10.4384 m/s
87.1684 kg*m/s^2
1 1/s m^2 kg*m^2/s^3 kg/m^3
11 60 2
1111 RobotId(9) TaskId(5)
live robots 2, tasks 1
after scope 0 0
=== hidden
x
---
10.4384 m/s
87.1684 kg*m/s^2
1 1/s m^2 kg*m^2/s^3 kg/m^3
11 60 2
1111 RobotId(9) TaskId(5)
live robots 2, tasks 1
after scope 0 0

## Hints
- Make the operators friends or free templates, so the dimensions are deduced: `template <int M1, int L1, int T1, int M2, int L2, int T2> constexpr auto operator*(Quantity<M1,L1,T1> a, Quantity<M2,L2,T2> b) { return Quantity<M1+M2, L1+L2, T1+T2>{a.value * b.value}; }`.
- `+` takes two `Quantity<M,L,T>` with the **same** parameters, so mismatched dimensions have no matching overload and don't compile (the driver checks this with concepts).
- User-defined literals: `constexpr Length operator""_m(long double v) { return Length{static_cast<double>(v)}; }`, plus an `unsigned long long` overload for `50_m`.
- CRTP: inside `Comparable<D>`, `friend bool operator<(const D& a, const D& b) { return a.key() < b.key(); }`. Because the parameters are `D`, comparing different derived types doesn't compile.
- `Counted<D>` has a `static inline int count`. Each `D` gets its own because `Counted<RobotId>` and `Counted<TaskId>` are different classes. Increment it in the constructor, including the copy constructor, and decrement it in the destructor.

## Solution
```cpp
#include <string>

template <int M, int L, int T>
struct Quantity {
    double value = 0;
    friend constexpr Quantity operator+(Quantity a, Quantity b) { return {a.value + b.value}; }
    friend constexpr Quantity operator-(Quantity a, Quantity b) { return {a.value - b.value}; }
    friend constexpr bool operator<(Quantity a, Quantity b) { return a.value < b.value; }
    friend constexpr bool operator==(Quantity a, Quantity b) { return a.value == b.value; }
    friend constexpr Quantity operator*(double k, Quantity q) { return {k * q.value}; }
    friend constexpr Quantity operator*(Quantity q, double k) { return {q.value * k}; }
};

template <int M1, int L1, int T1, int M2, int L2, int T2>
constexpr auto operator*(Quantity<M1, L1, T1> a, Quantity<M2, L2, T2> b) {
    return Quantity<M1 + M2, L1 + L2, T1 + T2>{a.value * b.value};
}
template <int M1, int L1, int T1, int M2, int L2, int T2>
constexpr auto operator/(Quantity<M1, L1, T1> a, Quantity<M2, L2, T2> b) {
    return Quantity<M1 - M2, L1 - L2, T1 - T2>{a.value / b.value};
}
template <int M, int L, int T>
constexpr auto operator/(double k, Quantity<M, L, T> q) { return Quantity<-M, -L, -T>{k / q.value}; }

using Scalar = Quantity<0, 0, 0>;
using Length = Quantity<0, 1, 0>;
using Time = Quantity<0, 0, 1>;
using Mass = Quantity<1, 0, 0>;
using Speed = Quantity<0, 1, -1>;
using Accel = Quantity<0, 1, -2>;
using Force = Quantity<1, 1, -2>;

constexpr Length operator""_m(long double v) { return {static_cast<double>(v)}; }
constexpr Length operator""_m(unsigned long long v) { return {static_cast<double>(v)}; }
constexpr Time operator""_s(long double v) { return {static_cast<double>(v)}; }
constexpr Time operator""_s(unsigned long long v) { return {static_cast<double>(v)}; }
constexpr Mass operator""_kg(long double v) { return {static_cast<double>(v)}; }
constexpr Mass operator""_kg(unsigned long long v) { return {static_cast<double>(v)}; }

inline void append_unit(std::string& s, const char* name, int e) {
    if (e <= 0) return;
    if (!s.empty()) s += '*';
    s += name;
    if (e > 1) s += "^" + std::to_string(e);
}

template <int M, int L, int T>
std::string unit_string(const Quantity<M, L, T>&) {
    std::string num, den;
    append_unit(num, "kg", M);
    append_unit(num, "m", L);
    append_unit(num, "s", T);
    append_unit(den, "kg", -M);
    append_unit(den, "m", -L);
    append_unit(den, "s", -T);
    if (num.empty() && den.empty()) return "1";
    if (num.empty()) num = "1";
    return den.empty() ? num : num + "/" + den;
}

template <class D>
struct Comparable {
    friend bool operator==(const D& a, const D& b) { return a.key() == b.key(); }
    friend bool operator!=(const D& a, const D& b) { return !(a == b); }
    friend bool operator<(const D& a, const D& b) { return a.key() < b.key(); }
    friend bool operator<=(const D& a, const D& b) { return !(b < a); }
    friend bool operator>(const D& a, const D& b) { return b < a; }
    friend bool operator>=(const D& a, const D& b) { return !(a < b); }
};

template <class D>
struct Printable {
    std::string str() const {
        const D& self = static_cast<const D&>(*this);
        return D::type_name() + "(" + std::to_string(self.key()) + ")";
    }
};

template <class D>
struct Counted {
    Counted() { ++count; }
    Counted(const Counted&) { ++count; }
    ~Counted() { --count; }
    static int live() { return count; }
private:
    static inline int count = 0;
};
```

- **Dimensions as template parameters:** `Quantity<1, 1, -2>` *is* "kg·m/s²". Multiplication and division compute the resulting exponents **in the type system**, so `Mass * Accel` has type `Force`, and `Length + Time` simply has no matching `operator+`. The bug class is eliminated at compile time, and since the struct holds one `double`, the run-time cost is zero. Libraries like `mp-units` and Boost.Units work exactly this way.
- **User-defined literals** (`9.58_s`) make code read like physics, and `constexpr` lets the compiler evaluate unit math in `static_assert`s.
- **CRTP mixins** inject behaviour using the derived type: `Comparable<D>` defines comparisons on `D` only, so a `RobotId` can't be compared with a `TaskId` (a strong-typedef benefit). `Counted<D>` gives each derived type its own static counter because each instantiation is a separate class. All of it is static: no vtables, no virtual calls.
