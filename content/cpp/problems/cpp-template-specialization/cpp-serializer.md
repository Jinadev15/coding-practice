---
id: cpp-serializer
title: Compile-Time Serializer via Specialization
difficulty: Hard
order: 1
tags: template specialization, partial specialization, recursion, type traits
---
## Statement
Write a JSON-like serializer whose behaviour is chosen **by type at compile time** through class template specialization. Provide a primary template and specializations of

```cpp
template <typename T, typename Enable = void> struct Serializer;   // static std::string write(const T&)
template <typename T> std::string to_text(const T& v) { return Serializer<T>::write(v); }
```

| Type | Output |
|---|---|
| integral types (not `bool`, not `char`) | decimal, e.g. `42` |
| floating-point | `std::format("{}", v)` (shortest round-trip form: `2.5`, `0.1`, `1e+20`) |
| `bool` (full specialization) | `true` / `false` |
| `char` (full specialization) | a quoted one-character string, `"x"` |
| `std::string` (full specialization) | quoted, with `"` and `\` escaped as `\"` and `\\` |
| `const char*` (full specialization) | the same as `std::string`, or `null` for a null pointer |
| `char[N]` (partial, on `N`) | string literals: `to_text("lit")` deduces `T = char[4]`, so it needs its own specialization; quoted like `std::string` |
| `std::vector<T>` (partial) | `[a,b,c]`, recursively |
| `std::array<T, N>` (partial) | the same as vector |
| `std::pair<A, B>` (partial) | `[a,b]` |
| `std::optional<T>` (partial) | the value, or `null` |
| `std::map<std::string, V>` (partial) | `{"k":v,...}` in key order |
| `T*` for any other pointer (partial) | `null`, or `&` followed by the pointee's text |

Using any other type must fail **at compile time**. Leave the primary template undefined (or put a `static_assert` in it).

Integral and floating types need a constraint on the `Enable` parameter (`std::enable_if_t<...>`), because a partial specialization can't name "all integers" directly.

## Starter
```cpp
#include <string>
#include <vector>

template <typename T, typename Enable = void>
struct Serializer;

template <typename T>
std::string to_text(const T& v) { return Serializer<T>::write(v); }
```

## Driver
```cpp
#include <iostream>
#include <array>
#include <map>
#include <optional>
#include <cstdint>
#include <climits>

template <typename T, typename = void> struct is_serializable : std::false_type {};
template <typename T> struct is_serializable<T, std::void_t<decltype(Serializer<T>::write(std::declval<const T&>()))>> : std::true_type {};

struct Opaque {};
static_assert(!is_serializable<Opaque>::value, "unsupported types must not be serializable");
static_assert(!is_serializable<std::vector<Opaque>>::value, "nor containers of them");

int main() {
    int which;
    std::cin >> which;
    if (which == 1) {
        std::cout << to_text(42) << ' ' << to_text(-7L) << ' ' << to_text(std::uint8_t{200}) << ' ' << to_text(LLONG_MIN) << '\n';
        std::cout << to_text(2.5) << ' ' << to_text(0.1) << ' ' << to_text(1e20) << ' ' << to_text(-0.0f) << '\n';
        std::cout << to_text(true) << ' ' << to_text(false) << ' ' << to_text('x') << '\n';
        std::cout << to_text(std::string("say \"hi\" \\o/")) << ' ' << to_text("lit") << ' ' << to_text(static_cast<const char*>(nullptr)) << '\n';
    } else if (which == 2) {
        std::vector<std::vector<int>> grid{{1, 2}, {}, {3}};
        std::cout << to_text(grid) << '\n';
        std::cout << to_text(std::array<double, 3>{0.5, 1, -2}) << '\n';
        std::cout << to_text(std::pair{std::string("id"), 7}) << '\n';
        std::cout << to_text(std::optional<int>{}) << ' ' << to_text(std::optional<std::string>{"s"}) << '\n';
        std::map<std::string, std::vector<bool>> flags{{"zeta", {true}}, {"alpha", {false, true}}};
        std::cout << to_text(flags) << '\n';
        int x = 5;
        int* px = &x;
        int* nul = nullptr;
        std::cout << to_text(px) << ' ' << to_text(nul) << ' ' << to_text(&px) << '\n';
        std::vector<std::pair<std::string, std::optional<double>>> mixed{{"a", 1.5}, {"b", std::nullopt}};
        std::cout << to_text(mixed) << '\n';
    }
}
```

## Tests
=== sample
1
---
42 -7 200 -9223372036854775808
2.5 0.1 1e+20 -0
true false "x"
"say \"hi\" \\o/" "lit" null
=== hidden
2
---
[[1,2],[],[3]]
[0.5,1,-2]
["id",7]
null "s"
{"alpha":[false,true],"zeta":[true]}
&5 null &&5
[["a",1.5],["b",null]]

## Hints
- Integral: `template <typename T> struct Serializer<T, std::enable_if_t<std::is_integral_v<T> && !std::is_same_v<T, bool> && !std::is_same_v<T, char>>>`. Print through `std::to_string(+v)` or `long long`, so `uint8_t` doesn't print as a character.
- Containers: `template <typename T, typename A> struct Serializer<std::vector<T, A>>` calls `to_text(elem)` for each element, which recurses into the right specialization for the element type.
- The partial specialization for `T*` must not clash with the full specialization for `const char*`. The full specialization is more specialized, so it wins.
- For the compile-time failure to be "SFINAE-friendly" (the driver checks this with `is_serializable`), the containers' `write` must only be valid when the element is serializable. The simplest way is to leave the primary template **undefined**: then `Serializer<Opaque>::write` doesn't exist. For `vector<Opaque>`, make the vector specialization itself conditional: `template <class T, class A> struct Serializer<std::vector<T, A>, std::enable_if_t<is_serializable<T>::value>>`.

## Solution
```cpp
#include <string>
#include <vector>
#include <array>
#include <map>
#include <optional>
#include <utility>
#include <format>
#include <type_traits>

template <typename T, typename Enable = void>
struct Serializer;                                       // primary: undefined, so unsupported types fail

template <typename T>
std::string to_text(const T& v) { return Serializer<T>::write(v); }

template <typename T, typename = void> struct serializable : std::false_type {};
template <typename T>
struct serializable<T, std::void_t<decltype(Serializer<T>::write(std::declval<const T&>()))>> : std::true_type {};

template <typename T>
struct Serializer<T, std::enable_if_t<std::is_integral_v<T> && !std::is_same_v<T, bool> && !std::is_same_v<T, char>>> {
    static std::string write(T v) {
        if constexpr (std::is_signed_v<T>) return std::to_string(static_cast<long long>(v));
        else return std::to_string(static_cast<unsigned long long>(v));
    }
};

template <typename T>
struct Serializer<T, std::enable_if_t<std::is_floating_point_v<T>>> {
    static std::string write(T v) { return std::format("{}", v); }
};

template <> struct Serializer<bool> {
    static std::string write(bool b) { return b ? "true" : "false"; }
};

inline std::string quote(const char* s) {
    std::string out = "\"";
    for (; *s; ++s) {
        if (*s == '"' || *s == '\\') out += '\\';
        out += *s;
    }
    return out + '"';
}

template <> struct Serializer<char> {
    static std::string write(char c) { const char s[2] = {c, '\0'}; return quote(s); }
};
template <> struct Serializer<std::string> {
    static std::string write(const std::string& s) { return quote(s.c_str()); }
};
template <> struct Serializer<const char*> {
    static std::string write(const char* s) { return s ? quote(s) : "null"; }
};
template <std::size_t N> struct Serializer<char[N]> {        // string literals arrive as const char[N]
    static std::string write(const char (&s)[N]) { return quote(s); }
};

template <typename It>
std::string join_list(It first, It last) {
    std::string out = "[";
    for (It it = first; it != last; ++it) {
        if (it != first) out += ',';
        out += to_text(*it);
    }
    return out + ']';
}

template <typename T, typename A>
struct Serializer<std::vector<T, A>, std::enable_if_t<serializable<T>::value>> {
    static std::string write(const std::vector<T, A>& v) { return join_list(v.begin(), v.end()); }
};

template <typename T, std::size_t N>
struct Serializer<std::array<T, N>, std::enable_if_t<serializable<T>::value>> {
    static std::string write(const std::array<T, N>& a) { return join_list(a.begin(), a.end()); }
};

template <typename A, typename B>
struct Serializer<std::pair<A, B>, std::enable_if_t<serializable<A>::value && serializable<B>::value>> {
    static std::string write(const std::pair<A, B>& p) { return "[" + to_text(p.first) + "," + to_text(p.second) + "]"; }
};

template <typename T>
struct Serializer<std::optional<T>, std::enable_if_t<serializable<T>::value>> {
    static std::string write(const std::optional<T>& o) { return o ? to_text(*o) : "null"; }
};

template <typename V, typename C, typename A>
struct Serializer<std::map<std::string, V, C, A>, std::enable_if_t<serializable<V>::value>> {
    static std::string write(const std::map<std::string, V, C, A>& m) {
        std::string out = "{";
        bool first = true;
        for (const auto& [k, v] : m) {
            if (!first) out += ',';
            first = false;
            out += quote(k.c_str()) + ":" + to_text(v);
        }
        return out + '}';
    }
};

template <typename T>
struct Serializer<T*, std::enable_if_t<!std::is_same_v<std::remove_cv_t<T>, char> && serializable<std::remove_cv_t<T>>::value>> {
    static std::string write(T* p) { return p ? "&" + to_text(*p) : "null"; }
};
```

**What this shows about specialization:**
- **Full specializations** (`bool`, `char`, `std::string`, `const char*`) give unrelated types completely different implementations behind one interface.
- **Partial specializations** match *families*: every `vector<T>`, every `pair<A, B>`, every `T*`. They recurse through `to_text` into the element types, so arbitrarily nested types like `vector<pair<string, optional<double>>>` work with no extra code.
- **The `Enable` parameter plus `enable_if_t`** turns a trait into a pattern ("any integral type"). This is the SFINAE technique from the next lesson, applied to partial specialization.
- **An undefined primary template plus conditional container specializations** make unsupported types fail cleanly at compile time, *and* detectably (`is_serializable<vector<Opaque>>` is false), instead of producing errors deep inside the instantiation.

This is the architecture of real serialization libraries (nlohmann::json's `adl_serializer`, cereal, fmt's `formatter<T>`).
