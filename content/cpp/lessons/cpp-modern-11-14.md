# C++11/14 Essentials

C++11 was so large a change that Stroustrup said it "feels like a new language". It's the dividing line between "legacy C++" (raw `new`/`delete`, manual loops, macros, `auto_ptr`) and **modern C++**. C++14 polished it. You've met most features in earlier lessons. This one consolidates the **modern baseline** that every C++ codebase and interview assumes, shows old-style code next to its modern equivalent, and fills in the features not yet covered: uniform initialisation, `nullptr`, `enum class`, `override`/`final`, delegating constructors, `= default`/`= delete`, `using` aliases, `static_assert`, `std::thread` and `<chrono>`.

## 1. Old style vs modern style

| Old (C++98) | Modern (C++11/14) |
|---|---|
| `std::vector<int>::iterator it = v.begin();` | `auto it = v.begin();` |
| `for (size_t i = 0; i < v.size(); ++i) f(v[i]);` | `for (const auto& x : v) f(x);` |
| `Widget* w = new Widget; ... delete w;` | `auto w = std::make_unique<Widget>();` (C++14) |
| `NULL` (an int: overloading surprises) | `nullptr` (type `std::nullptr_t`) |
| `enum Color { RED };` (leaks names, converts to int) | `enum class Color { Red };` (scoped, strongly typed) |
| `typedef std::map<int, std::string> Map;` | `using Map = std::map<int, std::string>;` (also templatable) |
| function objects with a hand-written struct | lambdas |
| `std::auto_ptr` (broken copy semantics) | `std::unique_ptr` + move semantics |
| `#define MAX 10` | `constexpr int max = 10;` |
| C-style casts | `static_cast`, `const_cast`, `reinterpret_cast`, `dynamic_cast` |

## 2. Uniform (brace) initialisation

```cpp
int x{5};
std::vector<int> v{1, 2, 3};
Pose p{1.0, 2.0, 0.5};
int narrow{3.7};               // ERROR: braces forbid narrowing conversions (double → int)
int legacy(3.7);               // compiles silently: 3

Widget w{};                    // value-initialised (zeros for built-ins)
Widget w2();                   // most vexing parse: declares a FUNCTION returning Widget!
```

> [!WARNING]
> Braces prefer `std::initializer_list` constructors: `std::vector<int> v{10, 0}` has two elements (10 and 0), while `std::vector<int> v(10, 0)` has ten zeros. Use parentheses to call a count/value constructor.

## 3. Class features

```cpp
class Motor {
public:
    Motor() : Motor(0, 3000) {}                       // delegating constructor
    Motor(int id, int max_rpm) : id_(id), max_rpm_(max_rpm) {}
    Motor(const Motor&) = delete;                     // non-copyable
    Motor& operator=(const Motor&) = delete;
    Motor(Motor&&) noexcept = default;                // movable, using the compiler's version
    virtual ~Motor() = default;
    virtual void spin(int rpm);
private:
    int id_ = 0;                                      // default member initialisers
    int max_rpm_ = 3000;
    double temperature_ = 25.0;
};

class StepperMotor final : public Motor {             // final: no further derivation
    void spin(int rpm) override;                      // override: the compiler checks the signature
};
```

## 4. `constexpr`, `static_assert` and type deduction

```cpp
constexpr int square(int x) { return x * x; }         // C++14 relaxed: loops and locals allowed
static_assert(square(12) == 144, "computed at compile time");

auto add = [](auto a, auto b) { return a + b; };      // C++14 generic lambda
template <typename T> auto twice(T x) { return x * 2; }   // C++14 return-type deduction
decltype(auto) get_ref(std::vector<int>& v) { return v[0]; }   // preserves the reference type
auto [it, ok] = m.insert({1, "a"});                   // (structured bindings arrived in C++17)
```

## 5. Concurrency and time enter the standard library

```cpp
#include <thread>
#include <mutex>
#include <chrono>
using namespace std::chrono_literals;

std::mutex m;
int counter = 0;
std::thread t([&] {
    for (int i = 0; i < 1000; ++i) {
        std::lock_guard<std::mutex> lock(m);          // RAII lock
        ++counter;
    }
});
t.join();

auto start = std::chrono::steady_clock::now();        // a monotonic clock
std::this_thread::sleep_for(50ms);                    // 50ms: a chrono literal (C++14)
auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(
    std::chrono::steady_clock::now() - start).count();
```

`<chrono>` makes time units type-safe: you can't accidentally pass seconds where milliseconds were meant. That's a common robotics bug in C-style code using bare `int`s. The Concurrency module covers threads in depth.

## 6. Other C++11 additions worth knowing

| Feature | Purpose |
|---|---|
| `std::array`, `std::unordered_map/set`, `std::forward_list`, `std::tuple` | new containers |
| `<random>`: `std::mt19937`, distributions | real random number generation (no more `rand() % n`) |
| `<regex>` | regular expressions (slow, but standard) |
| `std::function`, `std::bind` | callable wrappers |
| `alignas`, `alignof` | alignment control |
| `thread_local` | per-thread variables |
| raw string literals `R"(C:\path\n)"` | no escaping |
| user-defined literals | `10_m`, `5ms` |
| variadic templates, rvalue references, `std::move`, `std::forward` | (earlier lessons) |

## 7. Exam-ready answers

> [!EXAM]
> **Modern C++ (C++11/14).** C++11 introduced move semantics and rvalue references, `auto` type deduction, range-based for loops, lambda expressions, smart pointers (`unique_ptr`, `shared_ptr`, `weak_ptr`) replacing manual memory management, `nullptr`, scoped enumerations (`enum class`), uniform brace initialisation that prohibits narrowing, `constexpr` functions, `static_assert`, variadic templates, defaulted and deleted special member functions, `override` and `final`, delegating constructors, default member initialisers, type aliases with `using`, and a standard threading library with `std::thread`, mutexes, atomics and `<chrono>`. C++14 added generic lambdas, return-type deduction for functions, `std::make_unique`, relaxed `constexpr` rules and chrono literals. Together they define the modern style that favours value semantics, RAII and expressing intent through the type system.

## 8. Cheat sheet

| Legacy habit | Modern replacement |
|---|---|
| `new`/`delete` | `std::make_unique` / `std::make_shared` |
| `NULL` | `nullptr` |
| plain `enum` | `enum class` |
| `typedef` | `using` |
| `#define` constant | `constexpr` |
| index loop | range-for / algorithms |
| a functor struct | a lambda |
| `rand() % n` | `std::uniform_int_distribution` + `std::mt19937` |
| `time(NULL)` diffs | `std::chrono::steady_clock` |
| a C-style cast | `static_cast` etc. |

> [!INTERVIEW]
> **"What's the difference between `enum` and `enum class`?"** Unscoped `enum` enumerators leak into the enclosing scope (so two enums can't both have `Red`), convert implicitly to `int` (so `Color::Red == Fruit::Apple` compiles if both are 0), and have an implementation-defined underlying type. `enum class` enumerators are scoped (`Color::Red`), never convert implicitly to integers or to other enums (`static_cast` is needed), and have a fixed underlying type (`int` by default, or specified: `enum class Cmd : std::uint8_t`), which also allows forward declarations. Prefer `enum class` for type safety, especially for protocol message types and state machines.
