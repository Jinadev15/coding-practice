# Namespaces

C has one global namespace, which is why C libraries prefix everything (`SDL_CreateWindow`, `vec_add`). C++ **namespaces** group names into named scopes, so `geometry::Point` and `graphics::Point` can coexist. The standard library lives in `std`, and every serious library has its own (`Eigen::`, `cv::`, `rclcpp::`). This lesson covers declaring namespaces, the difference between using-declarations and using-directives, and why `using namespace std;` in a header is a bug.

## 1. Declaring and using

```cpp
namespace robot {
    constexpr double max_speed = 2.0;

    struct Pose { double x, y, theta; };

    double distance(const Pose& a, const Pose& b) {
        return std::hypot(a.x - b.x, a.y - b.y);
    }
}

robot::Pose start{0, 0, 0};          // qualified name
auto d = robot::distance(start, {3, 4, 0});
```

`::` is the **scope resolution operator**. A leading `::` means the global namespace: `::helper()`.

## 2. Namespaces are open and can nest

```cpp
namespace robot { void stop(); }          // reopen anywhere, in any file
namespace robot::sensors {                // C++17 nested shorthand
    struct Lidar { /* ... */ };
}
robot::sensors::Lidar front;
```

Large codebases mirror their directory structure in namespaces: `robot/sensors/lidar.hpp` declares `robot::sensors::Lidar`.

## 3. Bringing names in: declarations vs directives

| Form | Effect | Risk |
|---|---|---|
| `std::cout` | fully qualified | none (the clearest) |
| `using std::cout;` | **using-declaration**: this one name becomes visible | low |
| `using namespace std;` | **using-directive**: every name in `std` becomes visible | name clashes, ambiguity |
| `namespace fs = std::filesystem;` | namespace alias | none |

```cpp
#include <algorithm>
using namespace std;
int count = 0;          // collides with std::count once algorithm is visible
// count++;             // error: reference to 'count' is ambiguous
```

> [!DANGER]
> **Never put `using namespace ...;` in a header file.** It leaks into every file that includes the header, silently changing the meaning of their code and causing ambiguity errors far away. In `.cpp` files, `using namespace std;` is tolerable in small programs and contest code, but professional code prefers explicit `std::` or targeted using-declarations inside functions.

## 4. Argument-dependent lookup (ADL)

Why does `std::cout << x` work without writing `std::operator<<`? When you call an unqualified function, the compiler also searches the namespaces of the **argument types**:

```cpp
namespace geo {
    struct Point { double x, y; };
    void print(const Point& p);
}
geo::Point p{1, 2};
print(p);       // finds geo::print through ADL, because p's type lives in geo
```

ADL makes operators and customisation points (`swap`, `begin`, `to_string`) work naturally for user types.

## 5. Anonymous namespaces: file-private names

```cpp
namespace {
    int call_count = 0;               // visible only in this .cpp: internal linkage
    void helper() { /* ... */ }
}
```

This is the C++ replacement for file-scope `static` in C. Use it for every helper that isn't part of a module's interface.

## 6. Inline namespaces (library versioning)

```cpp
namespace lib {
    inline namespace v2 { void api(); }    // lib::api refers to v2::api by default
    namespace v1 { void api(); }           // the old version is still reachable as lib::v1::api
}
```

The standard library uses this for things like `std::literals`.

## 7. Exam-ready answers

> [!EXAM]
> **Namespaces.** A namespace is a declarative region that groups related names under a common prefix to prevent name collisions between libraries and modules. Names are accessed with the scope resolution operator (`ns::name`). Namespaces can be reopened and nested (`a::b::c`). A using-declaration (`using std::cout;`) introduces a single name into the current scope, while a using-directive (`using namespace std;`) makes all names of a namespace visible and should be avoided in headers because it affects every including file. Unnamed (anonymous) namespaces give their contents internal linkage, restricting them to the translation unit. Argument-dependent lookup finds unqualified function names in the namespaces of their arguments' types.

## 8. Cheat sheet

| Need | Code |
|---|---|
| define | `namespace robot { ... }` |
| nested | `namespace robot::nav { ... }` |
| use one name | `using std::vector;` |
| alias | `namespace fs = std::filesystem;` |
| file-private | `namespace { ... }` |
| global scope | `::name` |
| never in headers | `using namespace X;` |

> [!INTERVIEW]
> **"Why is `using namespace std;` considered bad practice?"** It imports hundreds of names (`count`, `distance`, `size`, `data`, `max`…) into the current scope, so your own identifiers may clash or silently resolve to a different overload. Future standard library additions can break code that compiles today. In a header, it imposes all that on every includer. Qualify names, or import specific ones locally.

## Worked example: organising a small library

```cpp
#include <iostream>

namespace robo::units {                         // nested namespace (C++17)
    constexpr double cm_per_m = 100.0;
    double to_cm(double m) { return m * cm_per_m; }
}

namespace robo {
    namespace {                                 // anonymous: private to this file
        int calls = 0;
    }
    struct Pose { double x, y; };
    void print(const Pose& p) {                 // found by ADL for robo::Pose
        ++calls;
        std::cout << "(" << p.x << ", " << p.y << ")\n";
    }
    int print_calls() { return calls; }
}

int main() {
    using robo::units::to_cm;                   // using-declaration: one name only
    std::cout << to_cm(1.5) << " cm\n";
    robo::Pose p{1, 2};
    print(p);                                   // no robo:: needed, thanks to ADL
    std::cout << robo::print_calls() << " call\n";
}
```

```output
150 cm
(1, 2)
1 call
```

**Argument-dependent lookup (ADL):** `print(p)` works without `robo::` because `p` is a `robo::Pose`, so the compiler also searches namespace `robo`. That is how `std::cout << x` finds `operator<<` for your own types.

## Common mistakes

- **`using namespace std;` at global scope in a header.** Name clashes appear in unrelated files.
- **Using `static` globals in C++ code**, where an anonymous namespace is idiomatic. Both give internal linkage, but the anonymous namespace also works for types.
- **Defining a function in a namespace in a header without `inline`.** Each `.cpp` that includes it gets a definition, and the linker complains about multiple definitions.

## Check your understanding

1. Can you add a function to namespace `robo` from another file?
2. What does an anonymous namespace give its contents?

<details><summary>Answers</summary>

1. Yes. Namespaces are open, and any file can reopen `namespace robo { ... }`. (Adding to `std` is not allowed, though.)
2. Internal linkage: the names are visible only in that translation unit.

</details>
