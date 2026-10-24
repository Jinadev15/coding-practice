# pair, tuple, optional, variant, any

Modern C++ has a set of **vocabulary types** that say exactly what a value means: `std::pair` and `std::tuple` for grouping, `std::optional` for "maybe a value", `std::variant` for "one of these types", and `std::any` for "anything". Used well, they replace sentinel values (`-1` meaning "not found"), output parameters, null pointers and unsafe unions with types the compiler can check.

## 1. `std::pair` and `std::tuple`

```cpp
#include <utility>
#include <tuple>

std::pair<std::string, int> p{"ada", 36};
p.first; p.second;
auto q = std::make_pair(1, 2.5);

std::tuple<int, double, std::string> t{1, 2.5, "x"};
std::get<0>(t);                     // 1
std::get<std::string>(t);           // by type (when unique)
auto [a, b, c] = t;                 // structured bindings (C++17)

std::tuple<int, int> minmax_of(const std::vector<int>& v);   // return several values
auto [lo, hi] = minmax_of(v);
```

Pairs and tuples compare **lexicographically**, which is handy for sorting by several keys:

```cpp
std::sort(people.begin(), people.end(), [](const P& x, const P& y) {
    return std::tie(x.age, x.name) < std::tie(y.age, y.name);   // tie builds a tuple of references
});
```

> [!TIP]
> Prefer a small named `struct` over `pair`/`tuple` in public APIs: `result.distance` documents itself, `std::get<2>(result)` doesn't. Tuples shine in generic code and as quick local groupings.

## 2. `std::optional<T>`: maybe a value

```cpp
#include <optional>

std::optional<int> find_index(const std::vector<int>& v, int x) {
    for (std::size_t i = 0; i < v.size(); ++i)
        if (v[i] == x) return static_cast<int>(i);
    return std::nullopt;                         // "no value": better than returning -1
}

auto idx = find_index(v, 7);
if (idx) std::cout << *idx;                      // test, then dereference
idx.has_value();
idx.value();                                     // throws std::bad_optional_access if empty
idx.value_or(-1);                                // a fallback
// C++23 monadic operations:
auto doubled = idx.transform([](int i) { return i * 2; });   // optional<int>
```

`optional<T>` stores the `T` **inline** (no heap allocation) plus a bool flag. It's ideal for parse results, lookups and lazily initialised members.

> [!WARNING]
> `*opt` on an empty optional is **undefined behaviour** (unchecked). `opt.value()` is the checked version. Also, `std::optional<bool>` and `std::optional<T*>` are confusing in conditions: `if (flag)` tests for *presence*, not truth.

## 3. `std::variant<Ts...>`: a type-safe union

A variant holds exactly **one** of its alternative types at a time, and knows which:

```cpp
#include <variant>

std::variant<int, double, std::string> v = 42;
v = std::string("hi");                  // now holds a string
v.index();                              // 2
std::holds_alternative<std::string>(v); // true
std::get<std::string>(v);               // "hi"
std::get<int>(v);                       // throws std::bad_variant_access
if (auto* pi = std::get_if<int>(&v)) {} // pointer, or nullptr: no exception
```

### `std::visit` and the overloaded pattern

```cpp
template <class... Fs> struct overloaded : Fs... { using Fs::operator()...; };

using Event = std::variant<struct KeyPress, struct MouseMove, struct Quit>;
struct KeyPress { char key; };
struct MouseMove { int x, y; };
struct Quit {};

void handle(const Event& e) {
    std::visit(overloaded{
        [](const KeyPress& k)  { std::cout << "key " << k.key << '\n'; },
        [](const MouseMove& m) { std::cout << "move " << m.x << ',' << m.y << '\n'; },
        [](const Quit&)        { std::cout << "quit\n"; },
    }, e);
}
```

If you forget an alternative, `std::visit` **fails to compile**. That exhaustiveness checking is something virtual functions can't give you.

| | Virtual functions | `std::variant` + `visit` |
|---|---|---|
| Set of types | **open** (add classes anywhere) | **closed** (fixed in the type) |
| Set of operations | closed (fixed in the base class) | **open** (write a new visitor) |
| Storage | heap + pointer usually | inline, no allocation |
| Exhaustiveness | no | checked at compile time |
| Use for | plugins, extensible hierarchies | messages, ASTs, state machines, results |

This is the classic **expression problem**: choose based on which axis will grow.

## 4. `std::any`

```cpp
#include <any>
std::any a = 5;
a = std::string("text");
std::any_cast<std::string>(a);          // throws std::bad_any_cast if the type is wrong
a.type() == typeid(std::string);
```

`any` holds a value of **any** copyable type, with type checking at run time only. It's rarely the right choice in application code: prefer `variant` (a known set of types) or templates. It's useful for things like property bags and plugin metadata.

## 5. Exam-ready answers

> [!EXAM]
> **Vocabulary types.** `std::pair` and `std::tuple` group a fixed number of values of possibly different types, accessed with `first`/`second` or `std::get`, unpacked with structured bindings, and compared lexicographically. `std::optional<T>` represents a value that may be absent, storing it inline together with an engaged flag; it is queried with `has_value`, accessed with `*`, `value` (checked) or `value_or`, and replaces sentinel values and nullable pointers for optional results. `std::variant<Ts...>` is a type-safe discriminated union holding exactly one of its alternatives, accessed with `std::get`, `std::get_if` or `std::visit`, which applies a callable to the active alternative and requires all alternatives to be handled. `std::any` holds a value of any copyable type with run-time type checking through `any_cast`.

## 6. Cheat sheet

| Need | Code |
|---|---|
| return two values | a struct, `std::pair`, or `std::tuple` + structured bindings |
| multi-key comparison | `std::tie(a.x, a.y) < std::tie(b.x, b.y)` |
| maybe a result | `std::optional<T>`, `std::nullopt`, `value_or` |
| one of several types | `std::variant<A, B, C>` |
| handle all alternatives | `std::visit(overloaded{...}, v)` |
| non-throwing variant access | `std::get_if<T>(&v)` |
| truly anything | `std::any` (rarely) |

> [!INTERVIEW]
> **"When would you model a set of types with `std::variant` instead of an inheritance hierarchy?"** When the set of types is closed and known (message types in a protocol, tokens in a lexer, robot states, AST node kinds) and you expect to add operations more often than types. `variant` stores values inline (no heap, cache-friendly), copies naturally (no clone), and `std::visit` checks at compile time that every alternative is handled. Inheritance fits when new types are added by other teams or plugins, and the operation set is stable.
