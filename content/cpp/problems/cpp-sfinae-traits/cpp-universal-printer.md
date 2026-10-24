---
id: cpp-universal-printer
title: A Universal Pretty-Printer with Traits
difficulty: Hard
order: 1
tags: type traits, detection idiom, if constexpr, void_t, recursion
---
## Statement
Write `std::string show(const T& value)`, a single function template that can print **almost anything**, by inspecting the type at compile time with **type traits, the detection idiom and `if constexpr`** (no overloads for specific containers):

Rules, checked in this order:
1. `bool` → `true`/`false`.
2. `char` → `'c'` (in single quotes).
3. anything convertible to `std::string_view` (`std::string`, `const char*`, literals, `string_view`) → `"text"` (in double quotes).
4. arithmetic types → `std::to_string`-like output: integers in decimal, floating-point via `std::format("{}")`.
5. `std::nullptr_t` → `nullptr`.
6. **tuple-like** types (detected via `std::tuple_size<T>::value`: `pair`, `tuple`, `std::array`) → `(a, b, c)`. `std::array` is also a range, so this rule must be checked first.
7. **ranges** (detected: `std::begin(v)` and `std::end(v)` are valid) → `[a, b, c]`. If the elements are tuple-like with exactly 2 elements and the range has a `key_type` member type (a map), print `{k: v, ...}` instead.
8. **optional-like** (has `has_value()` and `operator*`) → the value, or `none`.
9. pointers (including smart pointers detected by `.get()`) → `null` or `->` followed by the pointee.
10. types with `operator<<` to `std::ostream` (detected) → whatever it prints.
11. otherwise → `<unprintable>`.

Everything recurses: a `std::map<std::string, std::vector<std::optional<int>>>` must print correctly.

## Starter
```cpp
#include <string>
#include <sstream>

template <typename T>
std::string show(const T& value) {
    return "<unprintable>";
}
```

## Driver
```cpp
#include <iostream>
#include <vector>
#include <map>
#include <set>
#include <list>
#include <array>
#include <tuple>
#include <optional>
#include <memory>
#include <string_view>

struct Vec2 { double x, y; };
std::ostream& operator<<(std::ostream& os, const Vec2& v) { return os << "Vec2(" << v.x << ", " << v.y << ")"; }
struct Secret { int code = 7; };

int main() {
    int which;
    std::cin >> which;
    if (which == 1) {
        std::cout << show(true) << ' ' << show('q') << ' ' << show(42) << ' ' << show(-3.25) << ' ' << show(1e-7) << '\n';
        std::cout << show(std::string("hi")) << ' ' << show("lit") << ' ' << show(std::string_view("sv")) << ' ' << show(nullptr) << '\n';
        std::cout << show(std::vector<int>{1, 2, 3}) << ' ' << show(std::set<char>{'b', 'a'}) << ' ' << show(std::list<std::string>{"x"}) << '\n';
        std::cout << show(std::pair{1, std::string("one")}) << ' ' << show(std::tuple{1, 2.5, 'c', true}) << ' ' << show(std::array{4, 5}) << '\n';
        std::cout << show(std::map<std::string, int>{{"b", 2}, {"a", 1}}) << '\n';
        std::cout << show(Vec2{1, 2.5}) << ' ' << show(Secret{}) << '\n';
    } else {
        std::map<std::string, std::vector<std::optional<int>>> m{{"k", {1, std::nullopt, 3}}, {"e", {}}};
        std::cout << show(m) << '\n';
        int x = 9;
        int* px = &x;
        int* np = nullptr;
        auto up = std::make_unique<std::vector<Vec2>>(std::vector<Vec2>{{0, 0}});
        std::shared_ptr<int> sp;
        std::cout << show(px) << ' ' << show(np) << ' ' << show(up) << ' ' << show(sp) << '\n';
        std::vector<std::tuple<int, std::pair<char, bool>>> deep{{1, {'a', false}}};
        std::cout << show(deep) << ' ' << show(std::optional<std::string>{"opt"}) << ' ' << show(std::optional<Secret>{}) << '\n';
        int raw[3] = {7, 8, 9};
        std::cout << show(raw) << ' ' << show(std::vector<std::vector<int>>{{}, {1}}) << '\n';
    }
}
```

## Tests
=== sample
1
---
true 'q' 42 -3.25 1e-07
"hi" "lit" "sv" nullptr
[1, 2, 3] ['a', 'b'] ["x"]
(1, "one") (1, 2.5, 'c', true) (4, 5)
{"a": 1, "b": 2}
Vec2(1, 2.5) <unprintable>
=== hidden
2
---
{"e": [], "k": [1, none, 3]}
->9 null ->[Vec2(0, 0)] null
[(1, ('a', false))] "opt" none
[7, 8, 9] [[], [1]]

## Hints
- Detection helpers: `template <class T, class = void> struct is_range : std::false_type {}; template <class T> struct is_range<T, std::void_t<decltype(std::begin(std::declval<const T&>())), decltype(std::end(std::declval<const T&>()))>> : std::true_type {};`. Do the same for `std::tuple_size<T>::value`, `key_type`, `has_value()`, `.get()` and `os << value`.
- Order matters: `std::string` is a range and `std::array` is both tuple-like and a range. Test the rules in the order listed with an `if constexpr ... else if constexpr` chain.
- Tuple printing: `std::apply([&](const auto&... xs) { ... fold ... }, value)`.
- Use `std::remove_cvref_t<T>` before comparing types, and `std::is_same_v<T, bool>` before the arithmetic check (`bool` is arithmetic too!).

## Solution
```cpp
#include <string>
#include <string_view>
#include <sstream>
#include <format>
#include <tuple>
#include <type_traits>
#include <iterator>
#include <utility>
#include <cstddef>

template <class T, class = void> struct is_range : std::false_type {};
template <class T>
struct is_range<T, std::void_t<decltype(std::begin(std::declval<const T&>())),
                               decltype(std::end(std::declval<const T&>()))>> : std::true_type {};

template <class T, class = void> struct is_tuple_like : std::false_type {};
template <class T>
struct is_tuple_like<T, std::void_t<decltype(std::tuple_size<T>::value)>> : std::true_type {};

template <class T, class = void> struct has_key_type : std::false_type {};
template <class T> struct has_key_type<T, std::void_t<typename T::key_type>> : std::true_type {};

template <class T, class = void> struct is_optional_like : std::false_type {};
template <class T>
struct is_optional_like<T, std::void_t<decltype(std::declval<const T&>().has_value()),
                                       decltype(*std::declval<const T&>())>> : std::true_type {};

template <class T, class = void> struct is_smart_ptr : std::false_type {};
template <class T>
struct is_smart_ptr<T, std::void_t<decltype(std::declval<const T&>().get())>>
    : std::bool_constant<std::is_pointer_v<decltype(std::declval<const T&>().get())>> {};

template <class T, class = void> struct is_streamable : std::false_type {};
template <class T>
struct is_streamable<T, std::void_t<decltype(std::declval<std::ostream&>() << std::declval<const T&>())>> : std::true_type {};

template <typename T>
std::string show(const T& value) {
    using U = std::remove_cvref_t<T>;
    if constexpr (std::is_same_v<U, bool>) {
        return value ? "true" : "false";
    } else if constexpr (std::is_same_v<U, char>) {
        return std::string("'") + value + "'";
    } else if constexpr (std::is_convertible_v<const U&, std::string_view>) {
        return "\"" + std::string(std::string_view(value)) + "\"";
    } else if constexpr (std::is_integral_v<U>) {
        return std::to_string(value);
    } else if constexpr (std::is_floating_point_v<U>) {
        return std::format("{}", value);
    } else if constexpr (std::is_same_v<U, std::nullptr_t>) {
        return "nullptr";
    } else if constexpr (is_tuple_like<U>::value) {
        std::string out = "(";
        std::apply([&](const auto&... xs) {
            std::size_t i = 0;
            ((out += (i++ ? ", " : "") + show(xs)), ...);
        }, value);
        return out + ")";
    } else if constexpr (is_range<U>::value) {
        using Elem = std::remove_cvref_t<decltype(*std::begin(value))>;
        constexpr bool is_map = has_key_type<U>::value && is_tuple_like<Elem>::value;
        std::string out = is_map ? "{" : "[";
        bool first = true;
        for (const auto& e : value) {
            if (!first) out += ", ";
            first = false;
            if constexpr (is_map) out += show(std::get<0>(e)) + ": " + show(std::get<1>(e));
            else out += show(e);
        }
        return out + (is_map ? "}" : "]");
    } else if constexpr (is_optional_like<U>::value) {
        return value.has_value() ? show(*value) : "none";
    } else if constexpr (std::is_pointer_v<U>) {
        return value ? "->" + show(*value) : "null";
    } else if constexpr (is_smart_ptr<U>::value) {
        return value.get() ? "->" + show(*value) : "null";
    } else if constexpr (is_streamable<U>::value) {
        std::ostringstream os;
        os << value;
        return os.str();
    } else {
        return "<unprintable>";
    }
}
```

- **The detection idiom** (`void_t` + `declval` + a partially specialized trait) asks "is this expression valid for T?" at compile time: begin/end, `tuple_size`, `has_value`, `get`, `operator<<`.
- **`if constexpr` chains** pick exactly one branch per type, and the other branches aren't instantiated. So `*value` is never compiled for an `int`, and `std::get<0>(e)` only for map elements.
- **Rule order encodes priority:** `bool` before arithmetic, strings before ranges (strings *are* ranges), tuple-like before ranges (`std::array` is both).
- **Recursion through `show`** handles arbitrarily nested types, and C arrays work through `std::begin`.

This is the essence of how libraries like `fmt`/`std::format` ranges support, and Catch2's value printer, decide how to print types they've never seen.
