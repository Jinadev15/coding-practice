# Operator Overloading

C++ lets your types use operators: `a + b` for vectors, `m[i][j]` for matrices, `p == q` for points, `std::cout << robot` for printing, `f(x)` for function objects. Done well, this makes domain code read like mathematics (Eigen's `T * p + offset`). Done badly, it creates surprises. This lesson covers the syntax, member vs non-member rules, the C++20 **spaceship operator** `<=>`, and the conventions every overload must follow.

## 1. The syntax

An operator is a function named `operator@`:

```cpp
struct Vec2 {
    double x = 0, y = 0;

    Vec2& operator+=(const Vec2& o) { x += o.x; y += o.y; return *this; }   // compound: a member
    Vec2 operator-() const { return {-x, -y}; }                              // unary minus
    double& operator[](std::size_t i) { return i == 0 ? x : y; }             // subscript
};

Vec2 operator+(Vec2 a, const Vec2& b) { a += b; return a; }                  // binary: a non-member, built on +=
Vec2 operator*(double k, const Vec2& v) { return {k * v.x, k * v.y}; }       // scalar on the left
Vec2 operator*(const Vec2& v, double k) { return k * v; }

std::ostream& operator<<(std::ostream& os, const Vec2& v) {
    return os << '(' << v.x << ", " << v.y << ')';
}

Vec2 p{1, 2}, q{3, 4};
std::cout << p + q << ' ' << 2.0 * p << ' ' << -q << '\n';   // (4, 6) (2, 4) (-3, -4)
```

## 2. Member or non-member?

| Operator | Usually | Why |
|---|---|---|
| `=`, `[]`, `()`, `->`, conversions | **must** be members | language rule |
| `+=`, `-=`, `++`, `--` (they modify the object) | member | they change `*this` |
| `+`, `-`, `*`, `==`, `<` (symmetric binary) | **non-member** (often a hidden friend) | allows implicit conversion of the **left** operand: `2.0 * v` |
| `<<`, `>>` for streams | non-member | the left operand is the stream, not your type |

> [!KEY]
> Implement `+` in terms of `+=` (as above): one source of truth, and the non-member gets symmetry for free. Copy the left operand by value, apply `+=`, and return it.

## 3. Comparisons and the spaceship operator (C++20)

```cpp
#include <compare>
struct Version {
    int major, minor, patch;
    auto operator<=>(const Version&) const = default;   // generates <, <=, >, >=
    bool operator==(const Version&) const = default;    // generates == and !=
};

Version a{1, 4, 0}, b{1, 10, 2};
std::cout << (a < b) << (a == b);    // 10: compares members lexicographically, in declaration order
```

`<=>` returns an ordering object (`std::strong_ordering`, `weak_ordering` or `partial_ordering`) comparing as `<0`, `==0` or `>0`. Defaulting it gives correct member-wise lexicographic comparison in **one line**, which replaces six hand-written operators.

## 4. Increment and decrement

```cpp
struct Counter {
    int v = 0;
    Counter& operator++() { ++v; return *this; }                     // prefix: ++c
    Counter operator++(int) { Counter old = *this; ++v; return old; }  // postfix: c++ (the dummy int marks it)
};
```

Postfix has to copy the old value, so prefer `++it` in loops over non-trivial types such as iterators.

## 5. Function call operator: function objects

```cpp
struct InRange {
    double lo, hi;
    bool operator()(double x) const { return lo <= x && x <= hi; }
};

std::vector<double> r{0.5, 3.0, 9.9};
auto n = std::count_if(r.begin(), r.end(), InRange{1.0, 5.0});   // 1
```

A **functor** carries state (`lo`, `hi`) and can be inlined by the compiler. Lambdas are syntactic sugar for exactly this.

## 6. Conversion operators

```cpp
class Percent {
    double v_;
public:
    explicit Percent(double v) : v_(v) {}
    explicit operator double() const { return v_ / 100.0; }   // explicit: requires static_cast
    explicit operator bool() const { return v_ != 0; }        // works in `if (p)` but not `int x = p;`
};
```

Make conversion operators `explicit` to avoid surprising implicit conversions. An `explicit operator bool` is still usable directly in conditions.

## 7. Rules and taboos

> [!DANGER]
> - **Preserve the natural meaning**: `+` shouldn't modify its operands, and `==` must be an equivalence relation. Users assume these properties, and so do STL algorithms.
> - **Don't overload `&&`, `||` or `,`**: the overloaded versions lose short-circuit evaluation and sequencing.
> - Overload related operators consistently (if `a == b`, then `!(a != b)`; `<` must be a strict weak ordering for `std::sort` and `std::map`).
> - You can't create new operators, change precedence or arity, or overload operators for built-in types alone (`int + int`).

## 8. Exam-ready answers

> [!EXAM]
> **Operator overloading.** C++ allows most operators to be redefined for user-defined types by declaring functions named `operator@`, either as non-static member functions (where the left operand is `*this`) or as non-member functions. The assignment, subscript, function-call and member-access operators must be members, while symmetric binary operators such as `+` and `==` are usually non-members so that both operands can be converted implicitly, and stream insertion `<<` must be a non-member because its left operand is the stream. Overloading cannot change an operator's precedence, associativity or arity, nor create new operators. Since C++20, a defaulted three-way comparison operator `<=>` together with a defaulted `operator==` generates all six comparison operators by member-wise lexicographic comparison.

## 9. Cheat sheet

| Need | Code |
|---|---|
| add-assign | `T& operator+=(const T& o) { ...; return *this; }` |
| add | `T operator+(T a, const T& b) { return a += b; }` |
| print | `std::ostream& operator<<(std::ostream& os, const T& t)` |
| all comparisons | `auto operator<=>(const T&) const = default;` + `operator==` |
| index | `T& operator[](size_t i);` + a `const` version |
| callable | `R operator()(Args) const;` |
| bool test | `explicit operator bool() const;` |

> [!INTERVIEW]
> **"Why should `operator+` usually be a non-member while `operator+=` is a member?"** `+=` modifies its left operand, so it naturally belongs to the class. `+` creates a new value from two operands, and as a non-member both operands are treated symmetrically, so implicit conversions work on either side: `2.0 * v` and `v * 2.0` (or `Money(5) + 3` and `3 + Money(5)` with a converting constructor). Implementing `+` via `+=` avoids duplicate logic.
