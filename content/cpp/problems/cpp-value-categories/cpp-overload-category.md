---
id: cpp-overload-category
title: Which Overload Runs?
difficulty: Medium
order: 1
tags: value categories, rvalue references, overload resolution
---
## Statement
Write three overloads of `classify`:

```cpp
std::string classify(int& x);          // returns "lvalue"
std::string classify(const int& x);    // returns "const lvalue"
std::string classify(int&& x);         // returns "rvalue"
```

and a function template `template <typename T> std::string relay(T&& x)` that **perfectly forwards** its argument to `classify`, so `relay` reports the same category as calling `classify` directly.

The driver calls both on many expressions and prints a table. (You don't read input: there's one fixed test.)

## Starter
```cpp
#include <string>
#include <utility>

std::string classify(int& x) { return "?"; }

template <typename T>
std::string relay(T&& x) {
    return classify(x);
}
```

## Driver
```cpp
#include <iostream>
int make() { return 5; }
int& ref(int& r) { return r; }
int main() {
    int a = 1;
    const int c = 2;
    int&& rr = 3;
    std::cout << "a: " << classify(a) << " / " << relay(a) << '\n';
    std::cout << "c: " << classify(c) << " / " << relay(c) << '\n';
    std::cout << "42: " << classify(42) << " / " << relay(42) << '\n';
    std::cout << "a+1: " << classify(a + 1) << " / " << relay(a + 1) << '\n';
    std::cout << "move(a): " << classify(std::move(a)) << " / " << relay(std::move(a)) << '\n';
    std::cout << "rr: " << classify(rr) << " / " << relay(rr) << '\n';
    std::cout << "make(): " << classify(make()) << " / " << relay(make()) << '\n';
    std::cout << "ref(a): " << classify(ref(a)) << " / " << relay(ref(a)) << '\n';
}
```

## Tests
=== sample
---
a: lvalue / lvalue
c: const lvalue / const lvalue
42: rvalue / rvalue
a+1: rvalue / rvalue
move(a): rvalue / rvalue
rr: lvalue / lvalue
make(): rvalue / rvalue
ref(a): lvalue / lvalue

## Hints
- The `int&&` overload is chosen for rvalues; `const int&` would also accept them, but the rvalue reference is a better match.
- `rr` is declared `int&&`, but as an expression it's an **lvalue** (it has a name).
- In `relay`, `x` is always an lvalue expression. `std::forward<T>(x)` restores the original category.

## Solution
```cpp
#include <string>
#include <utility>

std::string classify(int&) { return "lvalue"; }
std::string classify(const int&) { return "const lvalue"; }
std::string classify(int&&) { return "rvalue"; }

template <typename T>
std::string relay(T&& x) {
    return classify(std::forward<T>(x));
}
```

The starter's `classify(x)` inside `relay` would report `lvalue` for everything that isn't const, because a named parameter is always an lvalue. With `T&&` deduced: passing an lvalue `int` gives `T = int&`, and `int& &&` collapses to `int&`. Passing an rvalue gives `T = int`, so the parameter is `int&&`. `std::forward<T>` then casts back to an rvalue only in the second case. That's the entire mechanism behind `make_unique` and `emplace_back`.
