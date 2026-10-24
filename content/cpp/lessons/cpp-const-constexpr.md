# const, constexpr and consteval

C++ lets you push work and guarantees **to compile time**. `const` promises a value won't change. `constexpr` says a value or function *can* be computed by the compiler. `consteval` says it *must* be. `constinit` guarantees static initialisation without runtime surprises. Used well, these make programs faster (lookup tables computed during compilation), safer (immutability checked by the compiler), and they enable template metaprogramming. **const correctness** on member functions is also essential for classes.

## 1. `const` variables and pointers

```cpp
const int max_speed = 300;          // must be initialised; can't change
// max_speed = 200;                 // error
const double* p = &d;               // pointer to const double
double* const q = &d;               // const pointer
```

Unlike C, a `const int` initialised with a constant expression **is** usable at compile time in C++ (as an array size, a template argument or a `case` label). Pointer const rules are the same as in C (read right to left).

## 2. `constexpr` variables: guaranteed compile-time constants

```cpp
constexpr double pi = 3.141592653589793;
constexpr int table_size = 1 << 10;
std::array<int, table_size> lut{};           // template argument: must be a compile-time constant
```

A `constexpr` variable **must** be initialised with a constant expression, otherwise it's a compile error. Prefer `constexpr` over `#define` for constants: it's typed, scoped and debuggable.

## 3. `constexpr` functions: can run at compile time

```cpp
constexpr long long factorial(int n) {
    long long r = 1;
    for (int i = 2; i <= n; ++i) r *= i;     // loops, ifs and locals are allowed (C++14+)
    return r;
}

constexpr auto f10 = factorial(10);          // computed by the COMPILER: 3628800 baked into the binary
int n;
std::cin >> n;
auto fn = factorial(n);                      // the same function, called at run time
static_assert(factorial(5) == 120);          // compile-time test: fails the BUILD if false
```

> [!KEY]
> A `constexpr` function is evaluated at compile time **when its arguments are constant and the result is needed in a constant context** (`constexpr` variables, template arguments, `static_assert`, array sizes). Otherwise it runs like a normal function. One definition serves both.

C++20 even allows `std::vector`, `std::string`, virtual functions and `try` inside `constexpr` functions (with limits), so whole algorithms can run in the compiler.

## 4. `consteval` (C++20): must run at compile time

```cpp
consteval int square(int x) { return x * x; }
constexpr int a = square(8);   // OK: 64
int y = 3;
// int b = square(y);          // error: y isn't a constant expression
```

Use it for functions that must never cost run time, such as compile-time format checking or hash computation.

## 5. `constinit` (C++20)

```cpp
constinit int counter = 0;     // guaranteed constant (static) initialisation, but still MUTABLE later
```

It prevents the "static initialisation order fiasco" for globals, where one global's dynamic initialiser reads another global that hasn't been initialised yet.

| Keyword | Value fixed? | Evaluated at compile time? |
|---|---|---|
| `const` | yes | maybe |
| `constexpr` variable | yes | **yes** |
| `constexpr` function | — | when possible or required |
| `consteval` function | — | **always** |
| `constinit` | **no** (mutable) | initialisation only |

## 6. const member functions (preview for classes)

```cpp
class Sensor {
    double value_ = 0;
public:
    double read() const { return value_; }   // promises not to modify the object
    void set(double v) { value_ = v; }
};

void report(const Sensor& s) {
    s.read();       // OK: read() is const
    // s.set(1);    // error: set() isn't const, and s is const
}
```

Mark every member function that doesn't modify the object `const`. Otherwise it can't be called on const objects or through `const&` parameters, which is how you'll pass most objects. That's **const correctness**, and the compiler enforces it transitively.

## 7. Compile-time computation example: a lookup table

```cpp
#include <array>
constexpr std::array<int, 256> make_popcount_table() {
    std::array<int, 256> t{};
    for (int i = 0; i < 256; ++i) t[i] = (i & 1) + t[i / 2];
    return t;
}
constexpr auto POPCOUNT = make_popcount_table();   // built during compilation
static_assert(POPCOUNT[255] == 8);
```

At run time the table already exists in the binary's read-only data: zero initialisation cost, a pattern used in embedded code and codecs.

## 8. Exam-ready answers

> [!EXAM]
> **const vs constexpr.** `const` declares that an object's value will not be modified after initialisation; the value may be computed at run time. `constexpr` applied to a variable requires that it be initialised with a constant expression, so its value is known at compile time and it can be used where constant expressions are required, such as array bounds, template arguments and `static_assert`. A `constexpr` function may be evaluated at compile time when called with constant arguments in a constant-expression context, and otherwise executes at run time. `consteval` (C++20) declares an immediate function that must be evaluated at compile time, and `constinit` requires static initialisation of a variable without making it constant.

## 9. Cheat sheet

| Need | Code |
|---|---|
| read-only value | `const auto x = compute();` |
| compile-time constant | `constexpr int N = 64;` |
| works at compile time and at run time | `constexpr T f(...)` |
| compile time only | `consteval T f(...)` |
| a compile-time test | `static_assert(cond, "msg");` |
| non-mutating method | `T get() const;` |
| safe global initialisation | `constinit int g = 0;` |

> [!INTERVIEW]
> **"Is a `constexpr` function always evaluated at compile time?"** No. It's evaluated at compile time only when it's used in a context that requires a constant expression (or when the compiler chooses to) and its arguments are constants. Called with run-time values it executes normally. If you need a guarantee, use `consteval`, or assign the result to a `constexpr` variable.
