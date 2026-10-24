# C++17

C++17 made everyday code shorter and safer. It added **structured bindings**, **`if constexpr`**, `if` and `switch` with initialisers, the vocabulary types **`std::optional`, `std::variant`, `std::any`** and **`std::string_view`**, **`std::filesystem`**, parallel algorithms, class template argument deduction, fold expressions, inline variables and guaranteed copy elision. Most of these were covered in their own lessons. This lesson surveys the release as a whole and covers the new pieces: `<filesystem>`, `if` with an initialiser, guaranteed copy elision, nested namespaces, attributes, and parallel algorithms.

## 1. Syntax improvements

```cpp
// structured bindings
std::map<std::string, int> ages{{"ada", 36}};
for (const auto& [name, age] : ages) std::cout << name << age;
auto [it, inserted] = ages.try_emplace("bob", 25);

// if / switch with an initialiser: the variable is scoped to the statement
if (auto it = ages.find("ada"); it != ages.end()) std::cout << it->second;
switch (auto s = read_state(); s) { case State::Idle: ...; }

// nested namespaces
namespace robot::control::pid { double step(double e); }

// inline variables: define globals and statics in headers without ODR problems
struct Config { static inline int max_speed = 3; };
inline constexpr double kPi = 3.141592653589793;

// fold expressions, CTAD, if constexpr: see the Templates module
```

## 2. Guaranteed copy elision

```cpp
std::vector<int> make_big() { return std::vector<int>(1'000'000); }   // a prvalue: constructed directly in the caller
auto v = make_big();       // no copy, no move: guaranteed since C++17

struct NonMovable { NonMovable() = default; NonMovable(NonMovable&&) = delete; };
NonMovable factory() { return NonMovable{}; }   // OK in C++17: no move is needed at all
```

Returning a **prvalue** (a temporary expression) materialises the object directly in its final location. **Named** return values (NRVO, `T x; ...; return x;`) are still only *permitted* to be elided, though compilers almost always do it, falling back to a move.

## 3. `std::filesystem`

```cpp
#include <filesystem>
namespace fs = std::filesystem;

fs::path p = fs::path("logs") / "2026" / "run1.bag";   // portable path joining
p.filename();   p.stem();   p.extension();   p.parent_path();
fs::create_directories("logs/2026");                    // mkdir -p
if (fs::exists(p) && fs::is_regular_file(p)) std::cout << fs::file_size(p);
for (const auto& entry : fs::recursive_directory_iterator("logs"))
    if (entry.path().extension() == ".bag") std::cout << entry.path() << '\n';
fs::copy_file(src, dst, fs::copy_options::overwrite_existing);
fs::rename(old_path, new_path);
fs::remove_all("tmp");                                  // careful: recursive and permanent

std::error_code ec;                                     // the non-throwing overloads
fs::remove("maybe.txt", ec);
if (ec) std::cerr << ec.message();
```

It's the C++ equivalent of Python's `pathlib` + `shutil`, replacing platform-specific `opendir`/`stat` and Win32 calls.

## 4. Parallel algorithms

```cpp
#include <execution>
std::sort(std::execution::par, v.begin(), v.end());                  // multi-threaded sort
auto total = std::reduce(std::execution::par_unseq, v.begin(), v.end(), 0.0);   // threads + SIMD
std::transform(std::execution::par, a.begin(), a.end(), out.begin(), f);
```

| Policy | Meaning |
|---|---|
| `seq` | sequential (like no policy) |
| `par` | may run on multiple threads |
| `par_unseq` | threads plus vectorisation: the element functions must not lock or allocate |
| `unseq` (C++20) | vectorisation only |

`std::reduce` (unlike `accumulate`) may reorder operations, so the operation must be associative and commutative (floating-point results can differ slightly). With GCC, parallel policies need Intel TBB (`-ltbb`) to actually run in parallel.

## 5. Attributes and small library additions

```cpp
[[nodiscard]] std::expected<int, Err> parse(...);   // warn when the result is ignored
[[maybe_unused]] int debug_only = 0;
switch (x) { case 1: f(); [[fallthrough]]; case 2: g(); }

std::clamp(v, lo, hi);  std::gcd(a, b);  std::lcm(a, b);   // <algorithm>, <numeric>
std::size(arr);  std::data(arr);  std::empty(c);            // free functions, work on C arrays
std::invoke(f, args...);  std::apply(f, tuple);             // uniform calling
std::byte b{0x3F};                                          // a byte type that isn't a character or a number
std::from_chars / std::to_chars                             // fast, locale-free number conversion
std::scoped_lock lock(m1, m2);                              // locks several mutexes deadlock-free
std::shared_mutex                                           // reader-writer lock
```

## 6. Exam-ready answers

> [!EXAM]
> **C++17 features.** C++17 introduced structured bindings for unpacking tuples, pairs and structures; `if constexpr` for compile-time branching; initialisers in `if` and `switch` statements; fold expressions; class template argument deduction; inline variables; nested namespace definitions; and guaranteed copy elision for prvalues. The library gained `std::optional`, `std::variant`, `std::any` and `std::string_view`; `std::filesystem` for portable path manipulation and directory traversal; parallel execution policies for standard algorithms, together with `std::reduce` and `std::transform_reduce`; `std::from_chars`/`to_chars`; `std::scoped_lock` and `std::shared_mutex`; and the attributes `[[nodiscard]]`, `[[maybe_unused]]` and `[[fallthrough]]`.

## 7. Cheat sheet

| Need | C++17 tool |
|---|---|
| unpack a pair or struct | `auto [a, b] = ...;` |
| scoped lookup result | `if (auto it = m.find(k); it != m.end())` |
| a header-defined global | `inline constexpr` |
| paths and directories | `std::filesystem` |
| parallel sort or sum | `std::execution::par` + `sort` / `reduce` |
| don't ignore my result | `[[nodiscard]]` |
| lock two mutexes safely | `std::scoped_lock` |
| maybe / one-of / view | `optional` / `variant` / `string_view` |

> [!INTERVIEW]
> **"What does guaranteed copy elision in C++17 change?"** When a function returns a prvalue (`return T{...};`), or an object is initialised from a prvalue of the same type, the object is now constructed **directly** in its final storage. It's no longer an optimisation the compiler *may* do, it's mandated, so no copy or move constructor is called or even required. That lets factory functions return non-copyable, non-movable types (`std::atomic`, `std::mutex` holders) by value. Named return value optimisation (returning a local variable) is still optional, with a move as the fallback, so `return std::move(local);` is a pessimisation that blocks NRVO.
