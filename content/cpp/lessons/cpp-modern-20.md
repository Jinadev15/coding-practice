# C++20: Modules, Coroutines, Spaceship

C++20 is the biggest release since C++11. It brought the "big four", **concepts**, **ranges**, **coroutines** and **modules**, plus the three-way comparison operator `<=>`, `std::format`, `std::span`, `<bit>`, `consteval`/`constinit`, designated initialisers and `std::jthread`. Concepts, ranges, `<=>` and `format` have their own lessons. This lesson focuses on **coroutines** and **modules**, and surveys the rest.

## 1. Coroutines

A **coroutine** is a function that can **suspend** its execution and **resume** later, keeping its local state. A function becomes a coroutine by using `co_yield`, `co_await` or `co_return`. They enable generators (lazy sequences), asynchronous code without callback pyramids, and cooperative state machines.

C++20 provides the **language mechanism** but only minimal library types. You write (or use) a return type with a `promise_type` that controls the behaviour. C++23 added a ready-made generator, `std::generator`:

```cpp
#include <generator>                       // C++23
std::generator<int> fibonacci() {
    int a = 0, b = 1;
    while (true) {
        co_yield a;                        // suspend, handing a to the caller
        std::tie(a, b) = std::pair{b, a + b};
    }
}
for (int x : fibonacci() | std::views::take(8)) std::cout << x << ' ';   // 0 1 1 2 3 5 8 13
```

What a minimal hand-written generator involves (the machinery `std::generator` hides):

```cpp
template <typename T>
struct Gen {
    struct promise_type {                                    // the compiler requires this nested type
        std::optional<T> current;
        Gen get_return_object() { return Gen{std::coroutine_handle<promise_type>::from_promise(*this)}; }
        std::suspend_always initial_suspend() noexcept { return {}; }   // lazy: don't run until asked
        std::suspend_always final_suspend() noexcept { return {}; }
        std::suspend_always yield_value(T v) { current = v; return {}; } // co_yield v lands here
        void return_void() {}
        void unhandled_exception() { throw; }
    };
    std::coroutine_handle<promise_type> h;                   // the resumable frame
    explicit Gen(std::coroutine_handle<promise_type> h) : h(h) {}
    Gen(Gen&& o) noexcept : h(std::exchange(o.h, {})) {}
    ~Gen() { if (h) h.destroy(); }                           // RAII for the coroutine frame
    std::optional<T> next() {
        if (!h || h.done()) return std::nullopt;
        h.resume();                                          // run until the next co_yield or the end
        return h.done() ? std::nullopt : h.promise().current;
    }
};

Gen<int> count_to(int n) { for (int i = 1; i <= n; ++i) co_yield i; }
```

> [!KEY]
> C++ coroutines are **stackless**: the compiler turns the function into a state machine, and its locals live in a heap-allocated **coroutine frame** (often optimised away). Suspension can only happen directly in the coroutine body, not in functions it calls. That makes them cheap (a few hundred bytes, versus a full thread stack), so you can have millions. Libraries built on them include cppcoro, Asio's `awaitable`, and the C++26 `std::execution` senders/receivers model for structured async I/O, a natural fit for robot networking stacks.

## 2. Modules

Header files are textual inclusion: every translation unit re-parses the same headers (slow builds), macros leak between headers, and include order matters. **Modules** are compiled once into a binary interface and imported:

```cpp
// motor.cppm: a module interface unit
export module robot.motor;
import <string>;                        // header units, or `import std;` in C++23
export class Motor {
public:
    explicit Motor(int id);
    void spin(int rpm);
private:
    int id_;
};
int internal_helper();                  // NOT exported: invisible to importers

// main.cpp
import robot.motor;
int main() { Motor m{1}; m.spin(100); }
```

The benefits are faster builds (no re-parsing), true encapsulation (only `export`ed names are visible, and macros don't leak), and order independence. As of the mid-2020s, support in compilers and build systems (CMake 3.28+ with Ninja) works but is still maturing. Most codebases still use headers, so you need to know both.

## 3. The three-way comparison and defaulted equality

```cpp
struct Version {
    int major, minor, patch;
    auto operator<=>(const Version&) const = default;   // generates <, <=, >, >= (and == via the default)
    bool operator==(const Version&) const = default;
};
auto c = (3 <=> 5);                     // std::strong_ordering::less
if (c < 0) { /* 3 is less */ }
```

There are three ordering categories: `strong_ordering` (equal values are interchangeable), `weak_ordering` (equivalent but distinguishable, like case-insensitive strings) and `partial_ordering` (some values are unordered, like floating-point NaN).

## 4. Library highlights

```cpp
std::span<const double> window(samples.data() + i, 32);   // a non-owning view of contiguous data (like string_view)
std::format("{:>8.2f} | {:<6} | {:#06x}", 3.14159, "ok", 255);   // type-safe formatting
#include <bit>
std::popcount(255u); std::bit_width(1000u); std::has_single_bit(64u); std::rotl(x, 3);
std::bit_cast<std::uint32_t>(1.0f);     // reinterpret bits safely (0x3F800000)
#include <numbers>
std::numbers::pi; std::numbers::e;
std::jthread worker([](std::stop_token st) { while (!st.stop_requested()) work(); });   // auto-joins, cooperative cancellation
std::source_location::current();        // file, line and function without macros
std::ranges::sort(v); views::filter(...);   // ranges (own lesson)
```

## 5. Language highlights

```cpp
Pose p{.x = 1.0, .y = 2.0};                       // designated initialisers (in declaration order)
consteval int sq(int x) { return x * x; }         // must run at compile time
constinit static int counter = 0;                 // statically initialised: no static-init-order fiasco
template <std::integral T> T gcd(T a, T b);       // concepts (own lesson)
auto f = []<typename T>(T x) { return x; };       // lambdas with template parameter lists
if (x > 0) [[likely]] { ... }                     // branch hints
using enum Color;                                 // bring enumerators into scope
std::vector<int> v; v.push_back(1);               // constexpr vector and string in constexpr functions
```

## 6. Exam-ready answers

> [!EXAM]
> **C++20 features.** C++20 added concepts for constraining templates; the Ranges library with range algorithms and lazy views; coroutines, which are functions that suspend and resume using `co_await`, `co_yield` and `co_return`, with behaviour customised by a promise type and state stored in a coroutine frame; and modules, which replace textual header inclusion with separately compiled interfaces exporting selected declarations, improving build times and encapsulation. It also introduced the three-way comparison operator `<=>` with defaultable comparisons, `std::format`, `std::span`, the `<bit>` header, `std::jthread` with stop tokens, `consteval` and `constinit`, designated initialisers, and template parameter lists for lambdas.

## 7. Cheat sheet

| Need | C++20 tool |
|---|---|
| lazy sequence | a coroutine with `co_yield` (`std::generator` in C++23) |
| async without callbacks | `co_await` with a library (Asio, cppcoro) |
| faster builds, encapsulation | `export module` / `import` |
| all comparisons | `auto operator<=>(const T&) const = default;` |
| view an array slice | `std::span<T>` |
| formatting | `std::format` |
| bit tricks | `<bit>` (`popcount`, `bit_cast`, `rotl`) |
| a thread that auto-joins and can be cancelled | `std::jthread` + `std::stop_token` |
| a compile-time-only function | `consteval` |

> [!INTERVIEW]
> **"What does 'stackless coroutine' mean in C++20, and what are the trade-offs?"** A C++ coroutine doesn't get its own call stack. The compiler transforms it into a state machine whose locals and suspension point live in a coroutine frame object (usually heap-allocated, sometimes elided). Suspension can only happen at `co_await`/`co_yield` in the coroutine's own body, and a regular function it calls can't suspend it. The benefits are a tiny memory footprint (you can have millions of concurrent coroutines), fast switching, and no thread synchronisation for cooperative tasks. The costs are "function colouring" (callers of async code become coroutines too), complex customisation machinery (promise types, awaiters), and lifetime pitfalls (references captured across suspension points can dangle).
