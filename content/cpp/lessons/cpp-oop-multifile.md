# Header/Source Organization

A C++ project's file structure is part of its design. It decides **compile times** (a header change recompiles every includer), **coupling** (what each translation unit can see), and correctness under the **One Definition Rule**. This lesson covers what goes in headers and what goes in sources, `inline` and templates, include hygiene and forward declarations, namespaces and internal linkage, project layout and CMake targets, and C++20 modules.

## 1. The rules

| Put in the header (`.hpp`) | Put in the source (`.cpp`) |
|---|---|
| class definitions, function declarations | non-inline function definitions |
| `inline` / `constexpr` functions, **templates** (definitions must be visible) | static data member definitions (or use `inline` variables) |
| `inline` variables, constants (`inline constexpr double kMaxSpeed = 2.0;`) | file-local helpers in an anonymous `namespace` |
| type aliases, enums, concepts | `#include`s needed only by the implementation |

> [!DANGER]
> A **non-inline function or variable defined in a header** violates the ODR as soon as two `.cpp` files include it: the linker reports "multiple definition", or, worse, with inline functions that differ between translation units, the program silently misbehaves. Functions defined *inside* a class body are implicitly `inline`. Free functions in headers need `inline` (or `constexpr`, or to be templates).

## 2. Include hygiene

```cpp
// planner.hpp
#pragma once                       // or classic include guards
#include <memory>                  // needed: unique_ptr member
#include <vector>
#include "geometry/pose.hpp"       // needed: Pose by value in the interface

class OccupancyMap;                // forward declaration: only used by reference/pointer
class Costmap;

class Planner {
public:
    explicit Planner(const OccupancyMap& map);
    std::vector<Pose> plan(const Pose& start, const Pose& goal) const;
private:
    const OccupancyMap& map_;
    std::unique_ptr<Costmap> costmap_;   // ok with an incomplete type if ~Planner is defined in the .cpp
};
```

- **Include what you use**: every header compiles on its own (test this by including it first in its own `.cpp`). Don't rely on transitive includes.
- **Forward-declare** classes used only by pointer or reference, to cut rebuild cascades. A `unique_ptr<Incomplete>` member needs the destructor defined where the type is complete, so declare `~Planner();` in the header and define it `= default` in the `.cpp`. That's the pimpl lesson's rule.
- Never put `using namespace std;` in a header: it leaks into every includer.

## 3. Namespaces and linkage

```cpp
namespace robo::nav {                       // C++17 nested namespace syntax
class Planner { ... };
}

// planner.cpp
namespace {                                  // anonymous namespace: internal linkage (like C's static)
double heuristic(const Pose& a, const Pose& b) { ... }
}
namespace robo::nav {
Planner::Planner(const OccupancyMap& m) : map_(m) {}
}
```

Organise namespaces by component (`robo::nav`, `robo::drivers`), and put implementation details in `detail::` or anonymous namespaces.

## 4. Templates across files

Template definitions must be visible wherever they're instantiated, so they normally live in headers, sometimes split into `foo.hpp` plus `foo_impl.hpp` for readability. If only a few types are ever used, **explicit instantiation** keeps the definitions in a `.cpp`:

```cpp
// filter.hpp: declaration only
template <class T> T lowpass(T prev, T x, double alpha);
extern template float lowpass<float>(float, float, double);    // suppress implicit instantiation

// filter.cpp
template <class T> T lowpass(T prev, T x, double alpha) { return prev + alpha * (x - prev); }
template float lowpass<float>(float, float, double);           // explicit instantiation
```

## 5. Project layout and build targets

```text
robot/
  CMakeLists.txt
  include/robo/nav/planner.hpp    public headers (installed)
  src/nav/planner.cpp             implementation
  src/nav/astar_detail.hpp        private header (not installed)
  tests/nav/planner_test.cpp
```

```cmake
add_library(robo_nav src/nav/planner.cpp)
target_include_directories(robo_nav PUBLIC include PRIVATE src)
target_link_libraries(robo_nav PUBLIC robo_geometry)
target_compile_features(robo_nav PUBLIC cxx_std_23)
```

One library target per component enforces the architecture: if `robo_nav` doesn't link `robo_drivers`, it can't use them.

## 6. C++20 modules

```cpp
// geometry.cppm
export module robo.geometry;
export struct Pose { double x, y, theta; };
export double distance(const Pose& a, const Pose& b);
```

Modules replace textual inclusion: each is compiled once, there are no include-order dependencies, macros don't leak, and only `export`ed names are visible. Support in GCC, Clang, MSVC and CMake (3.28+) is maturing, while headers remain dominant in existing codebases, including ROS 2.

> [!EXAM]
> **What may appear in a C++ header file without violating the One Definition Rule, and why?**
> Headers are included into many translation units, so they may contain declarations, plus definitions that the ODR allows to be repeated identically: class and enum definitions, `inline` functions (including member functions defined in the class body and `constexpr` functions, which are implicitly inline), `inline` variables and constants, templates, type aliases and concepts. Ordinary non-inline function or variable definitions must appear in exactly one `.cpp` file, or the linker sees multiple definitions. The `inline` exemption also requires every copy to be token-for-token identical, and violations there are undefined behaviour without a diagnostic.

## Worked example: a class split into header and source

```cpp
// ---- geometry/vec2.hpp ----
#pragma once
#include <iosfwd>                     // forward declarations only: cheap

namespace geo {
class Vec2 {
public:
    Vec2(double x, double y) : x_(x), y_(y) {}   // trivial: fine to define in the header
    double length() const;                       // declared here, defined in the .cpp
    Vec2 operator+(const Vec2& o) const { return {x_ + o.x_, y_ + o.y_}; }
    friend std::ostream& operator<<(std::ostream&, const Vec2&);
private:
    double x_, y_;
};
}

// ---- geometry/vec2.cpp ----
// #include "geometry/vec2.hpp"
#include <cmath>
#include <ostream>
namespace geo {
double Vec2::length() const { return std::hypot(x_, y_); }
std::ostream& operator<<(std::ostream& os, const Vec2& v) { return os << '(' << v.x_ << ", " << v.y_ << ')'; }
}

// ---- main.cpp ----
// #include "geometry/vec2.hpp"
#include <iostream>
int main() {
    geo::Vec2 a{3, 4}, b{1, 1};
    std::cout << a + b << " length " << a.length() << '\n';
}
```

```output
(4, 5) length 5
```

(The three files are shown together here so the example runs as one. In a project you compile `vec2.cpp` and `main.cpp` separately and link them: `g++ -c vec2.cpp`, `g++ -c main.cpp`, `g++ vec2.o main.o`.)

The rules in short:

- **The header has declarations and tiny inline functions.** Each `.cpp` has the definitions.
- **Templates and `inline`/`constexpr` functions must be fully defined in headers**, because every file that uses them needs the body.
- **Include what you use**, and use `<iosfwd>` or forward declarations in headers to keep rebuilds fast.

## Common mistakes

- **Defining a non-inline function in a header.** It gets defined once per including `.cpp`, which causes "multiple definition" linker errors.
- **Defining a template in a `.cpp`.** The result is "undefined reference" at link time.
- **Missing include guards or `#pragma once`.** Including a header twice in one file redefines its classes.

## Check your understanding

1. Why can `Vec2`'s constructor live in the header without `inline`?
2. What does `<iosfwd>` buy you?

<details><summary>Answers</summary>

1. Member functions defined inside the class body are implicitly `inline`.
2. Declarations of `std::ostream` and friends without the whole heavy `<iostream>` header, which means faster compiles for every includer.

</details>
