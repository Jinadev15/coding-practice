# CRTP and Template Metaprogramming

Two advanced template techniques show up in high-performance libraries. The **Curiously Recurring Template Pattern** (CRTP), where a class derives from a template instantiated with itself, gives **static polymorphism**: interface sharing and code reuse with no virtual calls. It's used in Eigen's expression templates, `std::enable_shared_from_this`, and robotics math libraries. **Template metaprogramming** (TMP) runs computations in the compiler: type lists, compile-time recursion, and generated tables. Modern C++ replaces much classic TMP with `constexpr`, but you need to recognise both.

## 1. The CRTP

```cpp
template <typename Derived>
class Shape {
public:
    double area() const {
        return static_cast<const Derived*>(this)->area_impl();   // calls the derived version: resolved at compile time
    }
    void describe() const { std::cout << "area " << area() << '\n'; }   // shared code using derived behaviour
};

class Square : public Shape<Square> {          // derives from Shape<itself>
public:
    explicit Square(double s) : s_(s) {}
    double area_impl() const { return s_ * s_; }
private:
    double s_;
};

class Circle : public Shape<Circle> {
public:
    explicit Circle(double r) : r_(r) {}
    double area_impl() const { return 3.14159 * r_ * r_; }
private:
    double r_;
};

template <typename D>
void report(const Shape<D>& s) { s.describe(); }   // generic over all CRTP shapes

report(Square(3));    // area 9: no vtable, no virtual call, fully inlinable
```

> [!KEY]
> The base knows its derived type at compile time (it's the template argument), so `static_cast<Derived*>(this)` is safe and the call is **static**: inlined, with no vptr in the object. The trade-off is that `Shape<Square>` and `Shape<Circle>` are **unrelated types**, so you can't store mixed shapes in one container. CRTP gives compile-time polymorphism, virtual functions give run-time polymorphism.

### CRTP mixins: inject functionality

```cpp
template <typename D>
struct Comparable {                                     // write < and get all the others
    friend bool operator>(const D& a, const D& b) { return b < a; }
    friend bool operator<=(const D& a, const D& b) { return !(b < a); }
    friend bool operator>=(const D& a, const D& b) { return !(a < b); }
};

template <typename D>
struct InstanceCounter {                                // a separate counter per derived type
    static inline int count = 0;
    InstanceCounter() { ++count; }
    ~InstanceCounter() { --count; }
};

struct Version : Comparable<Version>, InstanceCounter<Version> {
    int major, minor;
    friend bool operator<(const Version& a, const Version& b) {
        return std::tie(a.major, a.minor) < std::tie(b.major, b.minor);
    }
};
```

(C++20's `operator<=>` makes the comparison mixin obsolete, but the pattern generalises.) The standard library's `std::enable_shared_from_this<T>` is a CRTP base.

## 2. Classic template metaprogramming

Templates are a Turing-complete compile-time language: recursion through instantiation, with specialisation as the base case:

```cpp
template <unsigned N>
struct Factorial { static constexpr unsigned long long value = N * Factorial<N - 1>::value; };
template <>
struct Factorial<0> { static constexpr unsigned long long value = 1; };

static_assert(Factorial<20>::value == 2432902008176640000ULL);
```

Type-level computation, the original reason TMP exists:

```cpp
template <typename... Ts> struct TypeList {};

template <typename List> struct Length;
template <typename... Ts> struct Length<TypeList<Ts...>> { static constexpr std::size_t value = sizeof...(Ts); };

template <typename T, typename List> struct Contains;
template <typename T, typename... Ts>
struct Contains<T, TypeList<Ts...>> : std::bool_constant<(std::is_same_v<T, Ts> || ...)> {};

using Msgs = TypeList<int, double, std::string>;
static_assert(Length<Msgs>::value == 3);
static_assert(Contains<double, Msgs>::value);
```

## 3. Modern compile-time programming

Value computations are now written as ordinary code with `constexpr`/`consteval`:

```cpp
constexpr unsigned long long factorial(unsigned n) { return n ? n * factorial(n - 1) : 1; }
static_assert(factorial(20) == 2432902008176640000ULL);

consteval std::array<std::uint8_t, 256> make_crc_table() {   // computed entirely by the compiler
    std::array<std::uint8_t, 256> t{};
    for (int i = 0; i < 256; ++i) {
        std::uint8_t c = static_cast<std::uint8_t>(i);
        for (int k = 0; k < 8; ++k) c = (c & 0x80) ? static_cast<std::uint8_t>((c << 1) ^ 0x07) : static_cast<std::uint8_t>(c << 1);
        t[i] = c;
    }
    return t;
}
constexpr auto CRC8 = make_crc_table();   // lives in read-only data: no start-up cost
```

Embedded systems use this to put lookup tables in flash with no run-time initialisation.

## 4. Expression templates (an idea)

Libraries like Eigen make `a + b + c` on vectors return a lightweight **expression object** (`Sum<Sum<Vec, Vec>, Vec>`, built with CRTP) instead of computing temporaries. Evaluation happens once, when it's assigned, in a single fused loop with no temporary vectors. That's how Eigen matches hand-written loops while keeping mathematical syntax. (Also why `auto x = a + b;` with Eigen can hold dangling references to temporaries: a classic gotcha.)

## 5. Exam-ready answers

> [!EXAM]
> **CRTP and template metaprogramming.** In the Curiously Recurring Template Pattern, a class derives from a base class template instantiated with the derived class itself (`class D : public Base<D>`); the base can then call derived-class members through `static_cast<D*>(this)`, providing static polymorphism resolved at compile time without virtual functions or vtables, and enabling reusable mixins such as comparison operators or per-type counters. Its limitation is that different instantiations of the base are unrelated types, precluding heterogeneous containers. Template metaprogramming uses template instantiation, recursion and specialisation to perform computations on types and constants at compile time; much value-level metaprogramming is now expressed with `constexpr` and `consteval` functions, while type-level techniques (type lists, traits) remain template-based.

## 6. Cheat sheet

| Need | Technique |
|---|---|
| interface reuse without virtuals | CRTP: `class D : Base<D>` + `static_cast<const D*>(this)` |
| inject operators or counters | CRTP mixins |
| compile-time constant | `constexpr` / `consteval` function |
| compile-time table | `constexpr auto t = make_table();` |
| type-level list operations | variadic class templates + folds |
| guard assumptions | `static_assert` |

> [!INTERVIEW]
> **"When would you choose CRTP over virtual functions?"** When the concrete type is known at compile time and the call is on a hot path: CRTP calls are resolved statically and inlinable, with no vptr per object (8 bytes saved) and no indirect branch. Examples are math libraries (Eigen), per-element operations in tight loops, and mixins adding functionality to many classes. Choose virtual functions when you need run-time choice of type (plugins, heterogeneous containers, types loaded from configuration) or a stable ABI across library boundaries. CRTP's costs are template bloat, harder-to-read code, and no common base type.
