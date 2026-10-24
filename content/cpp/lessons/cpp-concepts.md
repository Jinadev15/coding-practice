# Concepts (C++20)

Before C++20, a template's requirements on its types were **implicit**: you discovered that `T` needed `operator<` only when instantiation failed, with an error deep inside the library. **Concepts** make requirements **explicit and checked at the call site**: `template <std::sortable R> void sort(R&)`. They give readable errors, express overloading by capability, and document generic interfaces. They're the modern replacement for SFINAE and `enable_if`.

## 1. Using standard concepts

```cpp
#include <concepts>

template <std::integral T>                 // T must satisfy std::integral
T gcd(T a, T b) { return b == 0 ? a : gcd(b, a % b); }

gcd(12, 18);          // OK
gcd(1.5, 2.5);        // error: "the required constraints are not satisfied: double does not satisfy integral"
```

Four equivalent spellings:

```cpp
template <std::integral T> T f(T x);                      // constrained template parameter
template <typename T> requires std::integral<T> T f(T x); // requires clause
template <typename T> T f(T x) requires std::integral<T>; // trailing requires clause
std::integral auto f(std::integral auto x);               // abbreviated (C++20)
```

| Category | Concepts |
|---|---|
| core language | `same_as`, `derived_from`, `convertible_to`, `integral`, `floating_point`, `signed_integral` |
| comparison | `equality_comparable`, `totally_ordered`, `three_way_comparable` |
| object | `movable`, `copyable`, `regular` (copyable + default constructible + `==`) |
| callable | `invocable<F, Args...>`, `predicate<F, Args...>`, `strict_weak_order<R, T, U>` |
| iterators and ranges | `input_iterator`, `random_access_iterator`, `ranges::range`, `ranges::random_access_range`, `sortable` |

## 2. Writing your own concepts

A concept is a named compile-time predicate on types:

```cpp
template <typename T>
concept Numeric = std::integral<T> || std::floating_point<T>;

template <typename T>
concept Sensor = requires(T s, double dt) {      // a requires-expression lists valid expressions
    { s.read() } -> std::convertible_to<double>; // must compile, and the result must convert to double
    { s.name() } -> std::same_as<std::string>;
    s.update(dt);                                // just needs to be valid
    typename T::config_type;                     // must have this nested type
};

template <Sensor S>
double average(S& s, int n) {
    double total = 0;
    for (int i = 0; i < n; ++i) total += s.read();
    return total / n;
}
```

The requires-expression's clauses:

| Clause | Checks |
|---|---|
| `expr;` | the expression is valid |
| `{ expr } -> concept<…>;` | valid, and its type satisfies the concept |
| `{ expr } noexcept;` | valid and non-throwing |
| `typename T::X;` | the nested type exists |
| `requires constraint;` | a nested constraint |

## 3. Overloading on concepts

When several constrained overloads match, the **most constrained** one wins (subsumption):

```cpp
template <std::input_iterator It>
void advance(It& it, int n) { while (n--) ++it; }          // generic: O(n)

template <std::random_access_iterator It>                  // refines input_iterator: preferred when satisfied
void advance(It& it, int n) { it += n; }                   // O(1)
```

This replaces tag dispatch and SFINAE overload sets with code that reads like the specification. Subsumption only works when one constraint is literally built from the other (named concepts combined with `&&`), not for arbitrary equivalent expressions.

## 4. Concepts vs alternatives

| Technique | Readability | Error messages | Can overload | Era |
|---|---|---|---|---|
| unconstrained template | best | worst (deep in the body) | — | C++98 |
| `enable_if` SFINAE | poor | poor | yes | C++11 |
| `static_assert` in the body | good | good | no | C++11 |
| `if constexpr` | good | ok | no (a single function) | C++17 |
| **concepts** | **good** | **good** | **yes** | C++20 |

> [!TIP]
> Concepts also constrain `auto` variables (`std::integral auto n = compute();`) and class templates (`template <std::regular T> class Set`). In robotics code, a concept like `Sensor` documents the interface a driver must provide at compile time, with zero run-time overhead, unlike a virtual base class.

## 5. Concepts vs virtual interfaces

```cpp
// run-time polymorphism: any Sensor-derived object, decided at run time
double avg(ISensor& s);            // virtual calls; works with heterogeneous containers

// compile-time polymorphism: any type modelling Sensor, resolved per type at compile time
template <Sensor S> double avg(S& s);   // inlined, no vtable; but one instantiation per type
```

They're complementary. Pick concepts for performance-critical generic code with types known at compile time, and virtual interfaces when types are chosen at run time.

## 6. Exam-ready answers

> [!EXAM]
> **Concepts.** A concept is a named set of compile-time requirements on template arguments, defined with `template <typename T> concept Name = constraint-expression;`, where the constraint may combine other concepts with `&&` and `||` or use a requires-expression listing expressions, return-type constraints and nested types that must be valid. Concepts constrain templates through constrained parameters (`template <std::integral T>`), requires clauses, or abbreviated `auto` parameters. Unsatisfied constraints remove a template from overload resolution and produce diagnostics at the point of use naming the failed requirement. When several constrained overloads are viable, the most constrained one is selected. The standard library defines core concepts in `<concepts>` and iterator and range concepts used by the Ranges library.

## 7. Cheat sheet

| Need | Code |
|---|---|
| constrain a parameter | `template <std::integral T>` |
| shorthand | `void f(std::floating_point auto x)` |
| custom concept | `template <class T> concept C = requires(T t) { t.f(); };` |
| return-type requirement | `{ t.size() } -> std::convertible_to<std::size_t>;` |
| combine | `concept Num = std::integral<T> \|\| std::floating_point<T>;` |
| overload by capability | the more refined concept wins |
| check in tests | `static_assert(Sensor<MyLidar>);` |

> [!INTERVIEW]
> **"How do concepts improve on SFINAE?"** They state requirements declaratively in the interface (`template <Sortable R>`) instead of encoding them in obscure signature tricks. When a requirement isn't met, the compiler reports which concept, and which clause of it, failed, at the call site, instead of pages of substitution errors. They support overloading by refinement (the most constrained overload wins), which is clearer than tag dispatch. They also work on `auto` variables and class templates. Semantically, concepts are checked only syntactically: the compiler can't verify that `<` is really a strict weak ordering, so documenting the semantic requirements still matters.
