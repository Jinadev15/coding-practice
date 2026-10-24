---
id: cpp-mini-format
title: A Type-Safe Mini Format Library
difficulty: Hard
order: 1
tags: variadic templates, fold expressions, parameter packs, perfect forwarding
---
## Statement
Implement a small `std::format`-like library with **variadic templates**:

```cpp
template <typename... Args>
std::string fmt(std::string_view pattern, const Args&... args);
```

- Each `{}` in the pattern is replaced by the next argument, converted with `operator<<` into a `std::ostringstream`.
- `{N}` (a decimal index) uses argument N explicitly, and can repeat. Don't mix automatic and explicit indexing in one pattern (throw `std::invalid_argument("mixed indexing")`).
- `{{` and `}}` produce literal braces.
- Errors throw `std::invalid_argument` with these messages: `"too few arguments"` (a `{}` or `{N}` refers past the end), `"too many arguments"` (with automatic indexing, some argument is never used), `"unmatched brace"` (also used for anything other than digits between braces, like `{x}`).

Also write these variadic helpers:

```cpp
template <typename... Ts> constexpr auto sum(Ts... xs);                 // fold; sum() == 0
template <typename T, typename... Ts> constexpr bool any_equal(const T& x, const Ts&... ys);   // fold over ||
template <typename... Ts> std::string join(std::string_view sep, const Ts&... xs);             // fmt each with operator<<
template <typename F, typename... Ts> void for_each_arg(F&& f, Ts&&... xs);                   // call f on each, left to right, forwarding
template <typename... Ts> constexpr std::size_t count_of_type_int();    // how many Ts are exactly int
```

## Starter
```cpp
#include <string>
#include <string_view>
#include <sstream>
#include <stdexcept>

template <typename... Args>
std::string fmt(std::string_view pattern, const Args&... args) {
    return std::string(pattern);
}
```

## Driver
```cpp
#include <iostream>
#include <vector>
#include <memory>

static_assert(sum() == 0 && sum(1, 2, 3) == 6, "sum must be constexpr");
static_assert(any_equal(3, 1, 2, 3) && !any_equal('a', 'b'), "any_equal must be constexpr");
static_assert(count_of_type_int<int, long, int, const int, char>() == 2);

void attempt(std::string_view pattern, auto... args) {
    try { std::cout << fmt(pattern, args...) << '\n'; }
    catch (const std::invalid_argument& e) { std::cout << "error: " << e.what() << '\n'; }
}

int main() {
    int which;
    std::cin >> which;
    if (which == 1) {
        attempt("{} has {} wheels and {} sensors", std::string("rover"), 4, 2.5);
        attempt("{1}-{0}-{1}", 'a', "b");
        attempt("literal {{braces}} and {}", 7);
        attempt("{}{}", 1);
        attempt("{}", 1, 2);
        attempt("{0} {}", 1, 2);
        attempt("oops }", 1);
        attempt("{5}", 1);
        attempt("no args");
        std::cout << sum(1, 2.5, 3L) << ' ' << join(", ", 1, "two", 3.5, 'c') << " [" << join("-") << "]\n";
    } else {
        std::vector<std::string> seen;
        for_each_arg([&](auto&& x) { std::ostringstream os; os << x; seen.push_back(os.str()); }, 10, "x", 2.25);
        for (auto& s : seen) std::cout << s << ' ';
        std::cout << '\n';
        auto p = std::make_unique<int>(42);
        int moved_count = 0;
        for_each_arg([&](auto&& x) {
            if constexpr (std::is_rvalue_reference_v<decltype(x)>) ++moved_count;
        }, std::move(p), 1, seen[0]);
        std::cout << "rvalues seen: " << moved_count << '\n';
        attempt("{2}{1}{0}{0}", "c", "b", "a");
        attempt("{{{}}}", "x");
        attempt("{", 1);
        attempt("{x}", 1);
    }
}
```

## Tests
=== sample
1
---
rover has 4 wheels and 2.5 sensors
b-a-b
literal {braces} and 7
error: too few arguments
error: too many arguments
error: mixed indexing
error: unmatched brace
error: too few arguments
no args
6.5 1, two, 3.5, c []
=== hidden
2
---
10 x 2.25 
rvalues seen: 2
abcc
{x}
error: unmatched brace
error: unmatched brace

## Hints
- Stringify every argument up front into a `std::vector<std::string>`: `std::vector<std::string> parts{to_str(args)...};` with a helper `to_str` using `std::ostringstream`. Then parse the pattern once, with ordinary loops over that vector.
- Track two flags, `used_auto` and `used_explicit`, plus a `next` counter and a `used` bit per argument, to detect mixing and unused arguments.
- `sum`: `return (xs + ... + 0);`. `any_equal`: `return ((x == ys) || ...);`.
- `for_each_arg`: `(f(std::forward<Ts>(xs)), ...);`. The comma fold guarantees left-to-right order.
- `count_of_type_int`: `return (std::size_t{0} + ... + (std::is_same_v<Ts, int> ? 1 : 0));`.

## Solution
```cpp
#include <string>
#include <string_view>
#include <sstream>
#include <stdexcept>
#include <vector>
#include <type_traits>
#include <utility>
#include <cctype>

template <typename T>
std::string to_str(const T& v) {
    std::ostringstream os;
    os << v;
    return os.str();
}

template <typename... Args>
std::string fmt(std::string_view pattern, const Args&... args) {
    std::vector<std::string> parts{to_str(args)...};          // pack expansion: one string per argument
    std::vector<bool> used(parts.size(), false);
    std::string out;
    std::size_t next = 0;
    bool autos = false, explicits = false;
    for (std::size_t i = 0; i < pattern.size(); ++i) {
        char c = pattern[i];
        if (c == '{' && i + 1 < pattern.size() && pattern[i + 1] == '{') { out += '{'; ++i; continue; }
        if (c == '}' && i + 1 < pattern.size() && pattern[i + 1] == '}') { out += '}'; ++i; continue; }
        if (c == '}') throw std::invalid_argument("unmatched brace");
        if (c != '{') { out += c; continue; }
        std::size_t close = pattern.find('}', i);
        if (close == std::string_view::npos) throw std::invalid_argument("unmatched brace");
        std::string_view inside = pattern.substr(i + 1, close - i - 1);
        std::size_t idx;
        if (inside.empty()) {
            autos = true;
            idx = next++;
        } else {
            for (char d : inside)
                if (!std::isdigit(static_cast<unsigned char>(d))) throw std::invalid_argument("unmatched brace");
            explicits = true;
            idx = std::stoul(std::string(inside));
        }
        if (autos && explicits) throw std::invalid_argument("mixed indexing");
        if (idx >= parts.size()) throw std::invalid_argument("too few arguments");
        used[idx] = true;
        out += parts[idx];
        i = close;
    }
    if (autos && next < parts.size()) throw std::invalid_argument("too many arguments");
    return out;
}

template <typename... Ts>
constexpr auto sum(Ts... xs) { return (xs + ... + 0); }

template <typename T, typename... Ts>
constexpr bool any_equal(const T& x, const Ts&... ys) { return ((x == ys) || ...); }

template <typename... Ts>
std::string join(std::string_view sep, const Ts&... xs) {
    std::string out;
    bool first = true;
    ((out += (first ? "" : std::string(sep)) + to_str(xs), first = false), ...);
    return out;
}

template <typename F, typename... Ts>
void for_each_arg(F&& f, Ts&&... xs) {
    (f(std::forward<Ts>(xs)), ...);                            // left to right, categories preserved
}

template <typename... Ts>
constexpr std::size_t count_of_type_int() {
    return (std::size_t{0} + ... + (std::is_same_v<Ts, int> ? 1u : 0u));
}
```

- **Pack expansion into an initializer list** (`{to_str(args)...}`) turns a compile-time list of heterogeneous arguments into a run-time vector of uniform strings. After that, the parsing is ordinary code. That's the core trick of type-safe formatting: every argument's type is known at compile time, so no `printf`-style type mismatch is possible.
- **Fold expressions** replace recursion: `+` with an initial value for `sum`, `||` for `any_equal` (an empty `||` fold is `false`), and the comma operator for ordered side effects in `join` and `for_each_arg`.
- **Perfect forwarding** in `for_each_arg` preserves each argument's value category, which the driver verifies by counting rvalues: `std::move(p)` and the literal `1` arrive as rvalues, while `seen[0]` stays an lvalue.
- **Compile-time counting** over types with `std::is_same_v` in a fold: `const int` isn't `int`, so the count is 2.
