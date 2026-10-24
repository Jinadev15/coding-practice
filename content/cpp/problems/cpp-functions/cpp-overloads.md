---
id: cpp-overloads
title: Overloads and Default Arguments
difficulty: Medium
order: 1
tags: overloading, default arguments, string_view
---
## Statement
Implement an overload set `describe` and a function with default arguments:

| Signature | Returns |
|---|---|
| `std::string describe(int x)` | `"int:X"` |
| `std::string describe(double x)` | `"double:X"` with 2 decimals |
| `std::string describe(std::string_view s)` | `"text:S(len)"` |
| `std::string describe(const std::vector<int>& v)` | `"list:[a,b,c]"` |
| `std::string pad(std::string_view s, int width = 8, char fill = '.')` | `s` right-aligned in `width`, padded with `fill` on the left (no truncation) |

The driver calls them with various literal types to check that overload resolution picks the right one (including `'A'`, a `char` that must promote to `int`, and `2.5f`, a `float` that promotes to `double`).

## Starter
```cpp
#include <string>
#include <string_view>
#include <vector>

std::string describe(int x) { return ""; }
```

## Driver
```cpp
#include <iostream>
int main() {
    std::cout << describe(42) << '\n';
    std::cout << describe(2.5f) << '\n';
    std::cout << describe('A') << '\n';
    std::cout << describe("robot") << '\n';
    std::cout << describe(std::vector<int>{1, 2, 3}) << '\n';
    std::cout << describe(std::vector<int>{}) << '\n';
    std::string w; int n;
    while (std::cin >> w >> n) {
        std::cout << pad(w) << '|' << pad(w, n) << '|' << pad(w, n, '*') << '\n';
    }
}
```

## Tests
=== sample
abc 5
---
int:42
double:2.50
int:65
text:robot(5)
list:[1,2,3]
list:[]
.....abc|..abc|**abc
=== hidden
toolongword 3
x 1
---
int:42
double:2.50
int:65
text:robot(5)
list:[1,2,3]
list:[]
toolongword|toolongword|toolongword
.......x|x|x

## Hints
- A string literal (`const char*`) converts to `std::string_view`; that's the overload it should reach.
- Format the double with `std::ostringstream` + `std::fixed << std::setprecision(2)`, or `std::format("{:.2f}", x)`.
- `pad`: if `s.size() >= width`, return `std::string(s)`; otherwise `std::string(width - s.size(), fill) + std::string(s)`.

## Solution
```cpp
#include <string>
#include <string_view>
#include <vector>
#include <format>

std::string describe(int x) {
    return "int:" + std::to_string(x);
}

std::string describe(double x) {
    return std::format("double:{:.2f}", x);
}

std::string describe(std::string_view s) {
    return "text:" + std::string(s) + "(" + std::to_string(s.size()) + ")";
}

std::string describe(const std::vector<int>& v) {
    std::string out = "list:[";
    for (std::size_t i = 0; i < v.size(); ++i) {
        if (i) out += ',';
        out += std::to_string(v[i]);
    }
    return out + "]";
}

std::string pad(std::string_view s, int width = 8, char fill = '.') {
    if (static_cast<int>(s.size()) >= width) return std::string(s);
    return std::string(width - s.size(), fill) + std::string(s);
}
```

`'A'` picks `describe(int)` because char → int is a **promotion**, which beats the char → double **conversion**. `2.5f` picks `describe(double)` because float → double is a promotion. Without the `string_view` overload, `describe("robot")` would fail to compile, since const char* → int/double/vector are all impossible. A `std::string` overload would also accept the literal, but `string_view` avoids allocating a temporary string.
