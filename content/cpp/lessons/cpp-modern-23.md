# C++23 and Beyond

C++23 is a "completion" release: it fills gaps in C++20 and adds conveniences you'll use daily: **`std::print`**, **`std::expected`**, **deducing `this`**, `std::generator`, `std::flat_map`, `std::mdspan`, more ranges (`zip`, `enumerate`, `chunk`, `to`), `import std;`, `std::stacktrace` and multidimensional subscripts. This lesson surveys C++23 and previews **C++26**: static reflection, contracts, `std::execution` and hazard pointers. It's the frontier of the language.

## 1. Everyday conveniences

```cpp
#include <print>
std::println("speed = {:.2f} m/s, mode = {}", speed, mode);   // like std::format + output, with no iostream state
std::print(stderr, "warning: {}\n", msg);

import std;                         // the whole standard library as one module (needs toolchain support)

auto v = std::views::iota(1, 6) | std::views::transform(sq) | std::ranges::to<std::vector>();
for (auto [i, x] : std::views::enumerate(v)) ...
for (auto [a, b] : std::views::zip(xs, ys)) ...
for (auto win : v | std::views::slide(3)) ...                  // sliding windows
for (auto chunk : v | std::views::chunk(4)) ...

std::string s = "robot";
s.contains("bo");                                               // C++23 string::contains
std::unreachable();                                             // tells the optimiser a path is impossible
```

## 2. `std::expected` and monadic `optional`

```cpp
std::expected<Config, Error> cfg = load(path).and_then(validate);   // (own lesson)
std::optional<int> maybe = find_id(name).transform([](int id) { return id * 10; })
                                        .or_else([] { return std::optional<int>{-1}; });
```

## 3. Deducing `this` (explicit object parameters)

A member function can take the object as an explicit first parameter, `this Self&& self`, deducing its type and value category:

```cpp
struct Buffer {
    std::vector<int> data;
    template <typename Self>
    auto&& at(this Self&& self, std::size_t i) {        // ONE function replaces const/non-const/&& overloads
        return std::forward<Self>(self).data[i];
    }
};

auto fib = [](this auto self, int n) -> int {           // recursive lambdas, finally
    return n < 2 ? n : self(n - 1) + self(n - 2);
};

template <typename Derived>                               // CRTP without the template boilerplate
struct Base { void hello(this auto&& self) { self.impl(); } };
```

## 4. New containers and views

| Feature | What it is |
|---|---|
| `std::flat_map` / `flat_set` | sorted vectors with a map interface: cache-friendly lookups, slow inserts |
| `std::mdspan` | a non-owning multidimensional view: `m[i, j]` over contiguous data (matrices, images, tensors). It's in the C++23 standard but not yet shipped by every standard library: GCC 15's libstdc++ doesn't have it, while Clang's libc++ does |
| `std::generator<T>` | the standard coroutine generator |
| `std::stacktrace` | capture and print the call stack at run time (for logging and error reports) |
| `std::byteswap`, `std::to_underlying` | byte-order swap; enum → its underlying integer |
| multidimensional `operator[]` | `m[i, j]` is now legal syntax for your own types |

```cpp
std::flat_map<std::string, int> fm{{"b", 2}, {"a", 1}};
fm.begin()->first;                                       // "a": sorted, contiguous

// mdspan, where the standard library provides it:
std::vector<double> buf(rows * cols);
std::mdspan grid(buf.data(), rows, cols);                // a 2D view, no copy
grid[2, 3] = 1.0;
```

## 5. C++26 preview

| Feature | Why it matters |
|---|---|
| **static reflection** (`^^T`, `std::meta`) | inspect types at compile time: generate serialisers, ORMs and enum-to-string with no macros or code generators |
| **contracts** (`pre`, `post`, `contract_assert`) | standard preconditions and postconditions with configurable checking (from the error-handling lesson) |
| **`std::execution`** (senders/receivers) | a standard model for asynchronous and parallel work: schedulers, composition, cancellation |
| **hazard pointers and RCU** | safe memory reclamation for lock-free data structures |
| `std::inplace_vector` | fixed-capacity vector with no heap (the StaticVector problem!) |
| `#embed` | include binary files (firmware blobs, models) directly as data |
| linear algebra (`<linalg>`, BLAS-like) | standard matrix operations on top of `mdspan` |
| erroneous behaviour for uninitialised reads | turns a classic UB into defined-but-diagnosable behaviour |

> [!TIP]
> Track what your **toolchain** supports, not just what the standard says. Check cppreference's compiler support tables, and use feature-test macros (`#if __cpp_lib_expected >= 202211L`). Robotics stacks (ROS 2 distributions, embedded vendor compilers) often lag the standard by several years, so C++17 is a common baseline even in 2026.

## 6. Exam-ready answers

> [!EXAM]
> **C++23 and later.** C++23 completed many C++20 features and added conveniences: formatted output with `std::print` and `std::println`; `std::expected` for value-or-error results and monadic operations on `std::optional`; explicit object parameters ("deducing this"), which allow a single member function to handle all cv- and reference-qualifications and enable recursive lambdas; `std::generator` for coroutine-based ranges; the container adaptors `std::flat_map` and `std::flat_set`; the multidimensional view `std::mdspan` and multidimensional subscript operators; additional range adaptors such as `zip`, `enumerate`, `chunk` and `slide`, plus `ranges::to`; `import std`; and `std::stacktrace`. C++26 is expected to add static reflection, contracts, the `std::execution` asynchronous framework and hazard pointers.

## 7. Cheat sheet

| Need | Modern tool |
|---|---|
| print formatted text | `std::println("{}", x)` |
| a value or an error | `std::expected<T, E>` |
| one accessor for const and non-const | `auto&& get(this Self&& self)` |
| a recursive lambda | `[](this auto self, ...)` |
| a sorted small map | `std::flat_map` |
| a 2D view of a buffer | `std::mdspan` (where available) |
| a lazy sequence | `std::generator<T>` |
| a pipeline to a vector | `\| std::ranges::to<std::vector>()` |
| feature check | `#if __cpp_lib_xxx` |

> [!INTERVIEW]
> **"What problem does 'deducing this' solve?"** Before C++23, a member function needing to behave correctly for `const`, non-const and rvalue objects needed several near-identical overloads (`T& get() &`, `const T& get() const&`, `T&& get() &&`), or a template helper. An explicit object parameter `this Self&& self` deduces the object's type and value category, so one function template with `std::forward<Self>(self)` covers every case. It also enables recursive lambdas (the lambda can refer to itself through `self`) and a simpler CRTP: the base can call derived members through `self` without being a template parameterised on the derived class.
