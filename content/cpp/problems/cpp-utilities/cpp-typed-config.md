---
id: cpp-typed-config
title: Typed Configuration Store
difficulty: Medium
order: 1
tags: variant, optional, visit, parsing
---
## Statement
Robot launch files hold typed parameters. Parse lines of the form `key = value` into a store where each value is a

```cpp
using Value = std::variant<bool, long long, double, std::string>;
```

with these parsing rules, tried in order: `true`/`false` → bool; an optional sign followed by digits → `long long`; a decimal number (with a `.` or an exponent, as accepted by `std::from_chars` for `double` consuming the **whole** token) → double; a double-quoted string → string without the quotes; anything else is a **parse error** for that line (`error line N`), and the line is skipped. Blank lines and lines starting with `#` are ignored. A repeated key overwrites the old value.

After a line containing exactly `== queries ==` come the queries:

| Query | Output |
|---|---|
| `type KEY` | `bool`, `int`, `double`, `string`, or `missing` |
| `get_int KEY` | the value if it's an int, otherwise `none` (use `std::optional<long long>`) |
| `get_double KEY` | the value if it's a double **or an int** (converted), printed with 6 significant digits, otherwise `none` |
| `show KEY` | the value formatted by `std::visit`: bools as `true`/`false`, ints plainly, doubles with 6 significant digits, strings in double quotes |
| `dump` | every key in **sorted** order as `key: shown-value` |

## Starter
```cpp
#include <iostream>
#include <string>
#include <variant>
#include <optional>
#include <map>
#include <charconv>

using Value = std::variant<bool, long long, double, std::string>;

int main() {
    std::map<std::string, Value> cfg;
    std::string line;
}
```

## Tests
=== sample
# robot.yaml (simplified)
name = "rover-7"
max_speed = 2.5
wheels = 4
debug = false
gain = 1e-3
broken = 12abc
wheels = 6
== queries ==
type wheels
type gain
type nothing
get_int wheels
get_int max_speed
get_double wheels
get_double name
show name
show debug
dump
---
error line 7
int
double
missing
6
none
6
none
"rover-7"
false
debug: false
gain: 0.001
max_speed: 2.5
name: "rover-7"
wheels: 6
=== hidden
x = -0
y = +7
z = -.5
s = ""
q = "with spaces inside"
t = TRUE
u = 1.
v = 3.141592653589793
w = 1e400
== queries ==
dump
type t
get_double z
get_int y
show w
---
error line 6
error line 9
q: "with spaces inside"
s: ""
u: 1
v: 3.14159
x: 0
y: 7
z: -0.5
missing
-0.5
7
missing
=== hidden

   
# nothing at all
== queries ==
dump
type a
---
missing

## Hints
- Split at the first `=`, and trim spaces around the key and the value.
- Integers: check the token yourself (an optional sign, then only digits) before `std::from_chars`, so `12abc` is rejected. `from_chars` accepts a leading `-` but not `+`, so skip a `+` yourself.
- Doubles: `std::from_chars(first, last, d)` must return `ec == std::errc{}` **and** `ptr == last`. Out-of-range values like `1e400` give `std::errc::result_out_of_range`, which counts as a parse error.
- `std::visit` with an "overloaded" set of lambdas formats every alternative, and the compiler checks that you handled all four.

## Solution
```cpp
#include <iostream>
#include <string>
#include <variant>
#include <optional>
#include <map>
#include <charconv>
#include <cctype>
#include <sstream>

using Value = std::variant<bool, long long, double, std::string>;
template <class... Fs> struct overloaded : Fs... { using Fs::operator()...; };

static std::string trim(const std::string& s) {
    auto b = s.find_first_not_of(" \t\r");
    if (b == std::string::npos) return "";
    return s.substr(b, s.find_last_not_of(" \t\r") - b + 1);
}

static std::optional<Value> parse_value(const std::string& t) {
    if (t == "true") return Value{true};
    if (t == "false") return Value{false};
    if (t.size() >= 2 && t.front() == '"' && t.back() == '"') return Value{t.substr(1, t.size() - 2)};
    std::size_t i = (!t.empty() && (t[0] == '+' || t[0] == '-')) ? 1 : 0;
    bool digits = i < t.size();
    for (std::size_t j = i; j < t.size(); ++j) digits = digits && std::isdigit(static_cast<unsigned char>(t[j]));
    if (digits) {
        long long v;
        const char* first = t.data() + (t[0] == '+' ? 1 : 0);
        auto [p, ec] = std::from_chars(first, t.data() + t.size(), v);
        if (ec == std::errc{} && p == t.data() + t.size()) return Value{v};
        return std::nullopt;
    }
    double d;
    const char* first = t.data() + (!t.empty() && t[0] == '+' ? 1 : 0);
    auto [p, ec] = std::from_chars(first, t.data() + t.size(), d);
    if (!t.empty() && ec == std::errc{} && p == t.data() + t.size()) return Value{d};
    return std::nullopt;
}

static std::string show(const Value& v) {
    return std::visit(overloaded{
        [](bool b) -> std::string { return b ? "true" : "false"; },
        [](long long i) -> std::string { return std::to_string(i); },
        [](double d) -> std::string { std::ostringstream os; os.precision(6); os << d; return os.str(); },
        [](const std::string& s) -> std::string { return '"' + s + '"'; },
    }, v);
}

static const char* type_name(const Value& v) {
    static const char* names[] = {"bool", "int", "double", "string"};
    return names[v.index()];
}

static std::optional<long long> get_int(const Value& v) {
    if (auto p = std::get_if<long long>(&v)) return *p;
    return std::nullopt;
}

static std::optional<double> get_double(const Value& v) {
    if (auto p = std::get_if<double>(&v)) return *p;
    if (auto p = std::get_if<long long>(&v)) return static_cast<double>(*p);
    return std::nullopt;
}

int main() {
    std::map<std::string, Value> cfg;
    std::string line;
    int lineno = 0;
    while (std::getline(std::cin, line)) {
        ++lineno;
        if (line == "== queries ==") break;
        std::string t = trim(line);
        if (t.empty() || t[0] == '#') continue;
        auto eq = t.find('=');
        auto val = eq == std::string::npos ? std::nullopt : parse_value(trim(t.substr(eq + 1)));
        if (!val) { std::cout << "error line " << lineno << '\n'; continue; }
        cfg.insert_or_assign(trim(t.substr(0, eq)), *val);
    }
    std::string cmd, key;
    while (std::cin >> cmd) {
        if (cmd == "dump") {
            for (const auto& [k, v] : cfg) std::cout << k << ": " << show(v) << '\n';
            continue;
        }
        std::cin >> key;
        auto it = cfg.find(key);
        if (cmd == "type") {
            std::cout << (it == cfg.end() ? "missing" : type_name(it->second)) << '\n';
        } else if (cmd == "get_int") {
            auto v = it == cfg.end() ? std::nullopt : get_int(it->second);
            if (v) std::cout << *v << '\n'; else std::cout << "none\n";
        } else if (cmd == "get_double") {
            auto v = it == cfg.end() ? std::nullopt : get_double(it->second);
            if (v) std::cout << show(Value{*v}) << '\n'; else std::cout << "none\n";
        } else if (cmd == "show") {
            std::cout << (it == cfg.end() ? "missing" : show(it->second)) << '\n';
        }
    }
}
```

- **`std::variant`** stores one of the four types *inline* and tracks which, with no inheritance, heap or casts. `index()` gives a cheap type tag for `type`.
- **`std::visit` + `overloaded`** formats every alternative, and forgetting one is a compile error (exhaustiveness checking).
- **`std::optional`** expresses "maybe a value" for parse results and typed getters. That's better than sentinels (what sentinel would you even use for a double?) or exceptions for an expected outcome.
- **`std::get_if`** gives non-throwing, typed access to the active alternative.
- **`std::from_chars`** with the `ptr == end` check accepts only tokens that are *entirely* numbers, and reports out-of-range values instead of silently producing `inf`.
