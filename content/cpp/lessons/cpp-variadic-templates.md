# Variadic Templates and Fold Expressions

**Variadic templates** take any number of template arguments: `template <typename... Ts>`. They power `std::tuple`, `std::make_unique(args...)`, `emplace_back(args...)`, `std::format`, `std::variant` and `std::visit`. Before C++17, using a parameter pack required recursive templates. **Fold expressions** now reduce a pack over an operator in a single expression. This lesson covers packs, expansion patterns, perfect forwarding of packs, and folds.

## 1. Parameter packs

```cpp
template <typename... Ts>          // a template parameter pack: zero or more types
void log(const Ts&... args) {      // a function parameter pack: zero or more arguments
    std::cout << sizeof...(Ts) << " args\n";   // sizeof... counts the pack's elements
}
log(1, "two", 3.0);   // Ts = {int, const char*, double}
log();                // an empty pack is fine
```

A pack can only be used by **expanding** it with `...` after a *pattern*. The pattern is repeated once per element, separated by commas:

```cpp
template <typename... Ts>
void f(Ts... args) {
    g(args...);                  // g(a1, a2, a3)
    g(std::move(args)...);       // g(std::move(a1), std::move(a2), ...)
    g(h(args)...);               // g(h(a1), h(a2), ...)
    g(h(args...));               // g(h(a1, a2, a3)): note the different placement
    std::tuple<Ts*...> ptrs;     // std::tuple<T1*, T2*, T3*>
}
```

## 2. The classic recursive style (pre-C++17)

```cpp
void print() { std::cout << '\n'; }                 // the base case: empty pack

template <typename T, typename... Rest>
void print(const T& first, const Rest&... rest) {   // peel off one argument
    std::cout << first << ' ';
    print(rest...);                                 // recurse on the rest
}
print(1, "two", 3.5);   // 1 two 3.5
```

This works, but it generates N functions and needs a separate base case. `if constexpr (sizeof...(rest) > 0)` can remove the base-case overload.

## 3. Fold expressions (C++17)

A fold applies a binary operator across a pack:

| Form | Expands to |
|---|---|
| `(pack op ...)` | right fold: `a1 op (a2 op (a3 op a4))` |
| `(... op pack)` | left fold: `((a1 op a2) op a3) op a4` |
| `(pack op ... op init)` | right fold with an initial value |
| `(init op ... op pack)` | left fold with an initial value |

```cpp
template <typename... Ts>
auto sum(Ts... xs) { return (xs + ... + 0); }        // the init value makes sum() == 0 valid

template <typename... Ts>
bool all_positive(Ts... xs) { return ((xs > 0) && ...); }   // an empty && fold is true

template <typename... Ts>
void print_all(const Ts&... xs) {
    ((std::cout << xs << ' '), ...);                 // a fold over the comma operator: runs left to right
    std::cout << '\n';
}

template <typename T, typename... Ts>
bool is_one_of(const T& x, const Ts&... options) { return ((x == options) || ...); }

sum(1, 2, 3, 4);              // 10
is_one_of(3, 1, 2, 3);        // true
```

> [!KEY]
> An empty pack is allowed in a fold only for `&&` (gives `true`), `||` (`false`) and `,` (`void()`). For other operators, provide an init value: `(xs + ... + 0)`.

## 4. Perfect forwarding of packs

The idiom behind every factory and every `emplace` function:

```cpp
template <typename T, typename... Args>
std::unique_ptr<T> make(Args&&... args) {                 // forwarding references
    return std::unique_ptr<T>(new T(std::forward<Args>(args)...));   // each argument keeps its category
}

auto motor = make<Motor>("left", 3000);      // Motor's constructor receives exactly these arguments
```

`std::forward<Args>(args)...` expands to `std::forward<A1>(a1), std::forward<A2>(a2), …`, so lvalues stay lvalues and rvalues stay rvalues (Value Categories lesson).

## 5. Packs in classes

```cpp
template <typename... Ts>
struct TypeList {
    static constexpr std::size_t size = sizeof...(Ts);
};

template <typename... Mixins>
struct Robot : Mixins... {                // inherit from every type in the pack
    using Mixins::describe...;            // C++17: bring all their describe overloads into scope
};

template <class... Fs> struct overloaded : Fs... { using Fs::operator()...; };   // the visit helper from the Utilities lesson
```

Indexing into a pack: `std::tuple_element_t<I, std::tuple<Ts...>>` gives the I-th type, and `std::get<I>(tuple)` the I-th value. Generating index sequences with `std::index_sequence_for<Ts...>{}` lets you loop over a tuple at compile time:

```cpp
template <typename Tuple, std::size_t... I>
void print_tuple_impl(const Tuple& t, std::index_sequence<I...>) {
    ((std::cout << (I ? ", " : "") << std::get<I>(t)), ...);
}
template <typename... Ts>
void print_tuple(const std::tuple<Ts...>& t) { print_tuple_impl(t, std::index_sequence_for<Ts...>{}); }
```

## 6. Exam-ready answers

> [!EXAM]
> **Variadic templates.** A variadic template accepts a parameter pack, a template parameter declared `typename... Ts` representing zero or more types, together with a corresponding function parameter pack. A pack is used through pack expansion, written as a pattern followed by `...`, which instantiates the pattern for each element. `sizeof...(Ts)` gives the number of elements. Packs were traditionally processed by recursion with a base case; C++17 fold expressions reduce a pack over a binary operator directly, as unary or binary, left or right folds, with empty packs permitted only for `&&`, `||` and the comma operator unless an initial value is supplied. Combined with forwarding references and `std::forward`, variadic templates implement perfect forwarding in functions such as `std::make_unique` and `emplace_back`.

## 7. Cheat sheet

| Need | Code |
|---|---|
| any number of types | `template <typename... Ts>` |
| count | `sizeof...(Ts)` |
| expand | `f(args...)`, `f(g(args)...)` |
| sum with an empty case | `(xs + ... + 0)` |
| all/any | `(pred(xs) && ...)` / `(... \|\| pred(xs))` |
| do something to each | `(action(xs), ...)` |
| forward everything | `f(std::forward<Args>(args)...)` |
| loop over a tuple | `std::index_sequence_for<Ts...>` or `std::apply` |

> [!INTERVIEW]
> **"Implement `make_unique`."** `template <class T, class... Args> std::unique_ptr<T> make_unique(Args&&... args) { return std::unique_ptr<T>(new T(std::forward<Args>(args)...)); }`. Explain each part: the variadic pack accepts any constructor arguments, `Args&&` in a deduced context is a forwarding reference, and `std::forward<Args>(args)...` expands per argument while preserving each one's value category, so rvalues are moved and lvalues copied. Mention why `make_unique` exists: exception safety in calls like `f(unique_ptr<A>(new A), g())` before C++17, and not writing `new`.
