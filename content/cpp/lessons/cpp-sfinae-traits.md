# SFINAE and Type Traits

Generic code often needs to **ask questions about types** at compile time ("is T an integer?", "does T have a `.size()`?", "what's the type without references and const?") and to **choose implementations** based on the answers. The `<type_traits>` library answers the questions. Three generations of techniques make the choices: **SFINAE** with `enable_if` (C++11), **`if constexpr`** (C++17) and **concepts** (C++20, next lesson). You'll meet all three in real codebases, so you need to read them all.

## 1. Type traits

Traits are class templates computed at compile time, with `_v` (value) and `_t` (type) shortcuts:

```cpp
#include <type_traits>
std::is_integral_v<int>                  // true
std::is_floating_point_v<float>          // true
std::is_pointer_v<int*>                  // true
std::is_same_v<int, std::int32_t>        // true on common platforms
std::is_base_of_v<Base, Derived>
std::is_trivially_copyable_v<Pose>       // safe to memcpy?
std::is_nothrow_move_constructible_v<T>  // can vector move it during growth?

std::remove_reference_t<const int&>      // const int
std::remove_cvref_t<const int&>          // int (C++20)
std::decay_t<int[3]>                     // int* (what pass-by-value does)
std::conditional_t<(sizeof(void*) == 8), std::int64_t, std::int32_t>   // compile-time "if" for types
std::common_type_t<int, double>          // double
std::underlying_type_t<MyEnum>
```

They're computed entirely by the compiler: zero run-time cost. They let you assert assumptions:

```cpp
template <typename T>
void send_raw(const T& msg) {
    static_assert(std::is_trivially_copyable_v<T>, "messages must be memcpy-safe");
    write(fd, &msg, sizeof msg);
}
```

## 2. SFINAE: "Substitution Failure Is Not An Error"

During overload resolution, the compiler substitutes the deduced template arguments into each candidate's **signature**. If substitution produces an invalid type, that candidate is **silently discarded** instead of causing an error. `std::enable_if` exploits this deliberately:

```cpp
template <bool B, class T = void> struct enable_if {};             // no ::type when false
template <class T> struct enable_if<true, T> { using type = T; };  // ::type exists only when true

template <typename T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
std::string kind(T) { return "integral"; }

template <typename T, std::enable_if_t<std::is_floating_point_v<T>, int> = 0>
std::string kind(T) { return "floating"; }

kind(3);      // "integral": the floating overload's enable_if_t has no ::type, so it's discarded
kind(2.5);    // "floating"
kind("x");    // error: no viable overload (both discarded)
```

> [!WARNING]
> SFINAE applies only to the **immediate context**: the function's signature (return type, parameter types, template parameters). An error inside the function **body** is a hard error, not a substitution failure. That's why traits go in the signature. SFINAE code is notoriously hard to read and gives awful error messages, so prefer `if constexpr` or concepts in new code.

### The detection idiom: "does T have a member X?"

```cpp
template <typename T, typename = void>
struct has_size : std::false_type {};

template <typename T>
struct has_size<T, std::void_t<decltype(std::declval<const T&>().size())>> : std::true_type {};
// void_t<...> is void if the expression is valid; otherwise SFINAE discards this specialisation

static_assert(has_size<std::string>::value);
static_assert(!has_size<int>::value);
```

`std::declval<T>()` pretends to produce a `T` in unevaluated contexts (`decltype`, `sizeof`) without constructing one.

## 3. `if constexpr` (C++17): compile-time branches

```cpp
template <typename T>
std::string describe(const T& x) {
    if constexpr (std::is_pointer_v<T>)
        return "ptr to " + describe(*x);
    else if constexpr (std::is_arithmetic_v<T>)
        return std::to_string(x);
    else if constexpr (has_size<T>::value)
        return "container of " + std::to_string(x.size());
    else
        return "something";
}
```

The discarded branches **aren't instantiated** for that `T`, so `*x` is never compiled when `T` isn't a pointer. That replaces most SFINAE overload sets and tag dispatch with readable code. A regular `if` would try to compile all branches and fail.

## 4. Compile-time computation

```cpp
constexpr int fib(int n) { return n < 2 ? n : fib(n - 1) + fib(n - 2); }   // may run at compile time
static_assert(fib(20) == 6765);

consteval int square(int x) { return x * x; }   // C++20: MUST run at compile time
constexpr auto table = [] {                      // build lookup tables during compilation
    std::array<int, 16> t{};
    for (int i = 0; i < 16; ++i) t[i] = i * i;
    return t;
}();
```

## 5. Exam-ready answers

> [!EXAM]
> **SFINAE and type traits.** Type traits in `<type_traits>` are templates that compute properties of types (`is_integral`, `is_pointer`, `is_same`, `is_trivially_copyable`) or transform them (`remove_reference`, `decay`, `conditional`) at compile time. SFINAE, "substitution failure is not an error", means that when substituting template arguments into a function template's signature produces an invalid construct, that candidate is removed from overload resolution rather than causing a compilation error. `std::enable_if` uses this to enable overloads only when a trait holds, and the detection idiom with `std::void_t` and `std::declval` tests whether expressions are valid for a type. C++17's `if constexpr` selects code paths at compile time, discarding the untaken branches, and C++20 concepts express such constraints more directly with clearer diagnostics.

## 6. Cheat sheet

| Need | Code |
|---|---|
| ask about a type | `std::is_integral_v<T>`, `std::is_same_v<A, B>` |
| strip `const` and `&` | `std::remove_cvref_t<T>` |
| choose a type | `std::conditional_t<cond, A, B>` |
| check an assumption | `static_assert(trait, "msg")` |
| enable an overload | `std::enable_if_t<cond, int> = 0` |
| "has member X?" | `std::void_t<decltype(std::declval<T>().x())>` |
| branch on a type | `if constexpr (trait) ... else ...` |
| compile-time function | `constexpr` / `consteval` |

> [!INTERVIEW]
> **"What is SFINAE and why has it largely been replaced?"** When the compiler substitutes template arguments into a candidate function's declaration and the result is ill-formed (`T::value_type` when T has none, or `enable_if<false>::type`), it quietly drops that candidate instead of erroring. Libraries used it with `enable_if` and `void_t` to constrain templates and detect capabilities. It's been largely superseded because it's hard to write and read, it only works in the declaration's immediate context, and failures produce pages of unhelpful errors. `if constexpr` handles branching inside one function, and C++20 concepts state requirements declaratively with readable diagnostics.
