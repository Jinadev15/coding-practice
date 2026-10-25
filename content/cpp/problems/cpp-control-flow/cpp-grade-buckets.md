---
id: cpp-grade-buckets
title: Range-for and Structured Bindings
difficulty: Easy
order: 1
tags: range-for, structured bindings, map, if with initializer
---
## Statement
Read lines `name score` until EOF. Group the names by grade: A (≥ 90), B (≥ 80), C (≥ 70), F otherwise. For a duplicate name, keep the **highest** score, which needs an `if` with an initialiser around `std::map::find` or `try_emplace`.

Print each grade that has students, in order A, B, C, F, as `A: name(score) name(score)` with the names in alphabetical order.

## Starter
```cpp
#include <iostream>
#include <map>
#include <string>
#include <vector>

int main() {
    std::map<std::string, int> best;
    std::string name;
    int score;

    return 0;
}
```

## Tests
=== sample
ada 95
bo 72
cy 88
bo 81
dee 40
---
A: ada(95)
B: bo(81) cy(88)
F: dee(40)
=== hidden
x 70
x 69
---
C: x(70)

## Hints
- `try_emplace(name, score)` inserts only if the key is new and returns `{iterator, inserted}`; if not inserted, compare and keep the higher score.
- `if (auto [it, ins] = m.try_emplace(k, v); !ins && v > it->second)` is an if-statement with an initialiser: the variables exist only inside the if.
- `std::map` keeps keys sorted, so iterating it already gives names in alphabetical order; group them into one vector per grade.

## Solution
```cpp
#include <iostream>
#include <map>
#include <string>
#include <vector>

int main() {
    std::map<std::string, int> best;
    std::string name;
    int score;
    while (std::cin >> name >> score) {
        if (auto [it, inserted] = best.try_emplace(name, score); !inserted && score > it->second)
            it->second = score;
    }
    std::map<char, std::vector<std::pair<std::string, int>>> grades;
    for (const auto& [n, s] : best) {
        char g = s >= 90 ? 'A' : s >= 80 ? 'B' : s >= 70 ? 'C' : 'F';
        grades[g].push_back({n, s});
    }
    for (const auto& [g, list] : grades) {
        std::cout << g << ':';
        for (const auto& [n, s] : list) std::cout << ' ' << n << '(' << s << ')';
        std::cout << '\n';
    }
    return 0;
}
```

`try_emplace` returns `{iterator, bool inserted}`, which the structured binding unpacks inside the `if` initialiser. `std::map` keeps its keys sorted, so names come out alphabetically, and the grade letters sort `A < B < C < F` naturally. Every loop here is a range-for with `const auto&`, so no copies are made.
