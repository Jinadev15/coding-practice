# Control Flow

C++ control flow is C's (`if`, `switch`, `while`, `do`, `for`, `break`, `continue`) plus four modern additions that make code shorter and safer: the **range-based for** loop, **`if`/`switch` with an initialiser**, **structured bindings**, and **`if constexpr`**, a compile-time branch used in templates. This lesson covers the C++-specific parts. The C lessons already cover the shared core.

## 1. Range-based `for` (C++11)

```cpp
std::vector<int> v{3, 1, 4};
for (int x : v)            std::cout << x;     // copy of each element
for (int& x : v)           x *= 2;             // modify in place
for (const auto& x : v)    std::cout << x;     // read without copying (the default for big types)
for (int x : {1, 2, 3})    std::cout << x;     // braced list
int arr[] = {5, 6};
for (int x : arr)          std::cout << x;     // C arrays work too (not pointers!)
```

It works with any type that has `begin()` and `end()` (all containers, `std::string`, your own classes):

```cpp
// for (auto& x : v) body;   is roughly:
auto&& range = v;
for (auto it = std::begin(range), end = std::end(range); it != end; ++it) {
    auto& x = *it;
    // body
}
```

> [!DANGER]
> Don't add or remove elements of a `std::vector` while range-iterating over it: `push_back` can reallocate and invalidate the iterators (UB). Collect the changes and apply them afterwards, or use the erase–remove idiom (STL Algorithms lesson).

Need the index too? Use a classic loop, or C++23 `std::views::enumerate`:

```cpp
for (std::size_t i = 0; i < v.size(); ++i) std::cout << i << ':' << v[i];
```

## 2. `if` and `switch` with an initialiser (C++17)

```cpp
if (auto it = ages.find("ada"); it != ages.end()) {
    std::cout << it->second;          // it is scoped to the if/else only
} else {
    std::cout << "not found";
}

switch (auto cmd = read_command(); cmd.type) {
    case Cmd::Move: /* ... */ break;
    case Cmd::Stop: /* ... */ break;
}
```

It keeps temporary variables in the narrowest scope, so they don't leak into the surrounding code.

## 3. Structured bindings in loops and conditions

```cpp
std::map<std::string, int> stock{{"bolt", 40}, {"nut", 0}};
for (const auto& [item, qty] : stock)
    if (qty == 0) std::cout << item << " is out\n";

if (auto [it, inserted] = stock.insert({"gear", 5}); inserted)
    std::cout << "added " << it->first << '\n';
```

## 4. `switch` improvements

- `[[fallthrough]];` marks intentional fall-through and silences the warning.
- `enum class` values must be qualified in `case` labels (`case Color::Red:`), which avoids collisions.
- `switch` still works only on integral and enum types, not on `std::string`.

## 5. `if constexpr` (C++17): compile-time branching

```cpp
template <typename T>
std::string describe(const T& value) {
    if constexpr (std::is_integral_v<T>)
        return "integer " + std::to_string(value);
    else if constexpr (std::is_floating_point_v<T>)
        return "real " + std::to_string(value);
    else
        return "other";
}
```

The discarded branch isn't even compiled for that `T`. That's why `std::to_string(value)` is fine even when `T` is a string. It replaces lots of old template tricks (Templates module).

## 6. Attributes that help control flow

```cpp
if (error) [[unlikely]] { handle(); }       // C++20: branch prediction hints
[[nodiscard]] int compute();                // warn if the caller ignores the result
[[noreturn]] void fatal(const char* msg);   // the function never returns
```

## 7. `goto`, labels and exceptions

`goto` exists, but modern C++ rarely needs it: **RAII** (destructors) handles cleanup automatically, which removes the main C use case. Exceptions (Error Handling module) provide non-local exits.

## 8. Exam-ready answers

> [!EXAM]
> **Range-based for loop.** The range-based for statement, `for (declaration : range) statement`, iterates over every element of a range, which may be an array, a braced initializer list or any object providing `begin()` and `end()`, such as standard containers. The loop variable can be declared by value (copying each element), by reference (`auto&`, allowing modification) or by const reference (`const auto&`, avoiding copies). It is equivalent to an iterator loop from `begin(range)` to `end(range)`, so modifying the container's size during iteration invalidates it.

> [!EXAM]
> **if with initializer and if constexpr.** Since C++17 an `if` or `switch` statement may contain an initialiser, `if (init; condition)`, whose variables are scoped to that statement. `if constexpr (condition)` evaluates its condition at compile time; in templates the branch not taken is discarded and not instantiated, enabling type-dependent code paths within a single function template.

## 9. Cheat sheet

| Need | Code |
|---|---|
| read every element | `for (const auto& x : c)` |
| modify every element | `for (auto& x : c)` |
| scoped temporary | `if (auto it = m.find(k); it != m.end())` |
| map entries | `for (const auto& [k, v] : m)` |
| compile-time branch | `if constexpr (std::is_integral_v<T>)` |
| intentional fall-through | `[[fallthrough]];` |
| don't ignore the result | `[[nodiscard]]` |

> [!INTERVIEW]
> **"What's the difference between `for (auto x : v)` and `for (auto& x : v)` for `std::vector<std::string>`?"** The first copies every string into `x`, which is slow for long strings and means changes don't affect `v`. The second binds a reference to each element: no copies, and modifications change the vector. For read-only loops use `const auto&`. This is a frequent code-review comment in C++ teams.

## Worked example: modern control flow in one program

```cpp
#include <iostream>
#include <map>
#include <string>

enum class Grade { A, B, C, F };

Grade grade_of(int score) {
    if (score >= 90) return Grade::A;
    if (score >= 75) return Grade::B;
    if (score >= 50) return Grade::C;
    return Grade::F;
}

int main() {
    std::map<std::string, int> scores{{"asha", 91}, {"ben", 48}, {"chen", 77}};

    for (const auto& [name, score] : scores) {           // structured bindings
        switch (grade_of(score)) {                        // enum class in a switch
            case Grade::A: std::cout << name << ": excellent\n"; break;
            case Grade::B:
            case Grade::C: std::cout << name << ": pass\n"; break;   // deliberate shared case
            case Grade::F: std::cout << name << ": retry\n"; break;
        }
    }
    if (auto it = scores.find("ben"); it != scores.end() && it->second < 50)   // if-with-initialiser
        std::cout << "ben needs help (" << it->second << ")\n";
}
```

```output
asha: excellent
ben: retry
chen: pass
ben needs help (48)
```

- **`const auto& [name, score]`** unpacks each `std::pair` without copying it.
- **`if (init; cond)`** keeps `it` scoped to the `if`, so it can't be misused later.
- **Switching on an `enum class`** lets the compiler warn (`-Wswitch`) if you forget a case. Leave out `default:` so that warning can fire.

## Common mistakes

- **Missing `break`**, so execution falls through into the next case. When you mean it, write `[[fallthrough]];`.
- **`for (auto x : big_vector)`** copies every element. Use `const auto&`.
- **Changing a container while range-looping over it** (`push_back` inside the loop) invalidates the iterators.

## Check your understanding

1. What is the scope of a variable declared in `if (auto x = f(); x > 0)`?
2. Why prefer `enum class` over a plain `enum`?

<details><summary>Answers</summary>

1. The whole `if` statement, including any `else` branches, and nothing after it.
2. Its names are scoped (`Grade::A`) and it doesn't convert to `int` implicitly, which prevents mix-ups.

</details>
