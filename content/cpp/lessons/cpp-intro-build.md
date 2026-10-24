# C++ vs C, Compilation and Build

C++ began as "C with Classes" (Bjarne Stroustrup, 1979). Today it's a multi-paradigm language that keeps C's performance and hardware access and adds **zero-cost abstractions**: classes, RAII, templates, the STL and lambdas. Abstractions you don't use cost nothing, and the ones you do use compile down to code as fast as hand-written C. That's why robotics stacks (ROS 2, MoveIt, PX4), game engines, browsers, databases and the cores of ML frameworks (PyTorch's ATen, TensorFlow) are written in C++.

## 1. What C++ adds to C

| Feature | C | C++ |
|---|---|---|
| user types with behaviour | `struct` + free functions | `class` with methods, access control, constructors/destructors |
| resource management | manual `malloc`/`free` | **RAII**: destructors release automatically |
| generics | `void *` + size | **templates** (type-safe, compile-time) |
| containers and algorithms | write your own | **STL**: `vector`, `map`, `sort`, … |
| strings | `char` arrays | `std::string` |
| references | pointers only | `T&` references |
| overloading | no | functions and operators |
| errors | return codes | exceptions (and `std::expected` in C++23) |
| namespaces | prefixes (`vec_add`) | `namespace geo { … }` |
| type inference | (C23 `auto`) | `auto`, `decltype` |

Almost all C is valid C++, with some differences: `void *` doesn't convert implicitly (`int *p = malloc(...)` needs a cast), `sizeof('a')` is 1 instead of 4, and C++ has more keywords (`class`, `new`, `template`…). Modern C++ style is very different from C style, though: **avoid raw `new`/`delete`, C arrays and `char *` strings** in favour of `std::vector`, `std::string` and smart pointers.

## 2. Hello, C++

```cpp
#include <iostream>

int main() {
    std::cout << "Hello, C++!\n";
    return 0;
}
```

```bash
g++ -std=c++23 -Wall -Wextra -O2 hello.cpp -o hello && ./hello
```

- Standard headers have no `.h`: `<iostream>`, `<vector>`, `<string>`. C headers are available as `<cstdio>`, `<cmath>`.
- Everything in the standard library lives in the `std` namespace.
- `int main()` with empty parentheses means "no parameters" in C++ (unlike in old C).

## 3. The build model: the same as C, with more to compile

The four stages (preprocess, compile, assemble, link) are the same as in C. What C++ adds:

- **Name mangling**: overloading means `f(int)` and `f(double)` need different linker symbols, so the compiler encodes the parameter types into the name (`_Z1fi`, `_Z1fd`). Calling C code from C++ requires `extern "C"` to turn mangling off.
- **Templates are instantiated per type in each translation unit**, which is why template code lives in headers and why C++ builds are slower.
- **The One Definition Rule (ODR)** is stricter: inline functions, templates and class definitions may appear in several translation units, but must be identical everywhere.

```bash
nm hello.o | c++filt       # demangle symbol names: _Z1fi → f(int)
```

## 4. Language standards

| Standard | Highlights |
|---|---|
| C++98/03 | the STL, templates, exceptions (the "old C++") |
| **C++11** | the modern baseline: `auto`, lambdas, move semantics, smart pointers, `nullptr`, range-for, threads |
| C++14 | generic lambdas, `make_unique` |
| C++17 | structured bindings, `optional`/`variant`, `if constexpr`, `<filesystem>`, parallel algorithms |
| C++20 | concepts, ranges, coroutines, modules, `<=>`, `std::format`, `span` |
| C++23 | `std::print`, `std::expected`, deducing `this`, `mdspan` |

Use at least `-std=c++17`. This platform compiles with **`-std=c++23`** (g++ 15).

## 5. Compiler flags

| Flag | Purpose |
|---|---|
| `-std=c++23` | the language version |
| `-Wall -Wextra -Wpedantic` | warnings (always) |
| `-O0 -g` / `-O2` / `-O3` | debug / release |
| `-fsanitize=address,undefined` | memory and UB checking |
| `-D_GLIBCXX_DEBUG` | bounds-checked STL containers (great for learning) |

## 6. Exam-ready answers

> [!EXAM]
> **C++ and its relationship to C.** C++ is a statically typed, compiled, multi-paradigm language derived from C. It retains C's low-level features and performance while adding support for object-oriented programming (classes, inheritance, virtual functions), generic programming (templates), resource management through constructors and destructors (RAII), references, function and operator overloading, namespaces, exceptions and a large standard library including containers, algorithms and strings. C++ follows the zero-overhead principle: features that are not used incur no cost, and used features should be as efficient as equivalent hand-written code. Compilation follows the same preprocess–compile–assemble–link model as C, with name mangling to encode overloaded function signatures in linker symbols.

## 7. Cheat sheet

| Need | Code |
|---|---|
| compile | `g++ -std=c++23 -Wall -Wextra -O2 main.cpp -o main` |
| print | `std::cout << x << '\n';` |
| headers | `<iostream>`, `<vector>`, `<string>`, `<algorithm>` |
| C library | `<cstdio>`, `<cmath>`, `<cstring>` |
| call C from C++ | `extern "C" { #include "lib.h" }` |
| demangle | `c++filt` |

> [!INTERVIEW]
> **"What does the zero-overhead principle mean?"** Two things. You don't pay for what you don't use: a program without exceptions or virtual functions doesn't carry their cost. And what you do use, you couldn't hand-code any better: `std::vector<int>` indexing compiles to the same instructions as a raw array, and `std::sort` with a lambda typically beats C's `qsort`, because the comparison is inlined instead of called through a function pointer.
