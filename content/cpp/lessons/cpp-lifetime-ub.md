# Object Lifetime and Undefined Behavior

C++ gives you direct control over when objects are created and destroyed, and what memory they live in. The price is a set of precise rules. Break one and the program has **undefined behaviour (UB)**: the standard places no requirements on it at all. UB isn't "it crashes". It's "the optimiser was allowed to assume this never happens", which produces bugs that vanish in debug builds, appear at `-O2`, and depend on the compiler version. This lesson covers the lifetime rules, the UB categories that bite real code, and the tools that find them.

## 1. What "lifetime" means

Every object has a **storage duration** (how long its memory exists) and a **lifetime** (when it's a live object you may use). The two aren't the same:

| Storage duration | Memory exists | Example |
|---|---|---|
| automatic | until the enclosing block ends | local variables |
| static | the whole program | globals, `static` locals |
| thread | the thread's lifetime | `thread_local` |
| dynamic | from `new` to `delete` | heap objects |

An object's lifetime **begins** when its initialisation completes and **ends** when its destructor starts (or, for trivially destructible types, when its storage is reused or released). Outside its lifetime, the memory may still be there, but using the object is UB.

```cpp
struct Sensor { std::string name; };

alignas(Sensor) std::byte buf[sizeof(Sensor)];        // storage, but no object yet
Sensor* s = new (buf) Sensor{"lidar"};                 // placement new: lifetime begins
s->name += "_front";
s->~Sensor();                                          // lifetime ends; storage remains
// s->name;                                            // UB: object is dead
```

## 2. Dangling: references and pointers that outlive their object

The most common lifetime bug in modern C++ is a **dangling reference**: the reference or view is still there, but the object it refers to is gone.

```cpp
const std::string& longest(const std::string& a, const std::string& b) {
    return a.size() >= b.size() ? a : b;
}
const std::string& r = longest("short", std::string("much longer"));   // both temporaries die at the ';'
std::cout << r;                                                          // UB: dangling
```

```cpp
std::string_view name() {
    std::string s = "robot";
    return s;                     // view into a local that dies on return: dangling
}

std::vector<int> v{1, 2, 3};
int& first = v[0];
v.push_back(4);                   // may reallocate: 'first' now dangles (iterator invalidation)
```

> [!KEY]
> **Temporary lifetime extension** applies only when a temporary is bound **directly** to a `const&` or `&&` local: `const std::string& r = std::string("x");` extends the temporary to `r`'s scope. It does **not** pass through function return values (`longest` above), member accessors (`get().name()` where `get()` returns by value), or `std::string_view`.

The C++23 range-for fix: before C++23, `for (auto x : make_vec()[0])` and `for (auto c : getObj().name())` iterated over a destroyed temporary. C++23 (P2718) extends the lifetime of all temporaries in the range-init expression. Older code is still UB.

## 3. The UB categories you must know

| Category | Example | Why the optimiser cares |
|---|---|---|
| Signed integer overflow | `INT_MAX + 1` | lets it assume `i + 1 > i`, simplify loops |
| Out-of-bounds access | `v[v.size()]` | assumes all indices are valid |
| Null dereference | `*p` with `p == nullptr` | after `*p`, it may delete `if (!p)` checks |
| Use after free / lifetime end | dangling pointers | |
| Data race | two threads, one writing, no sync | assumes single-threaded reasoning per thread |
| Strict aliasing violation | reading a `float` through `int*` | assumes differently typed pointers don't alias |
| Misaligned access | `*(uint32_t*)(buf + 1)` | can emit aligned-only instructions |
| Uninitialised read | `int x; return x;` | may treat the value as anything (even inconsistently) |
| Shift by ≥ width / negative | `1 << 32` | |
| Infinite loop without side effects | `while (true) {}` with no I/O or atomics | assumes forward progress (C++ only, relaxed in C++26 for trivial loops) |
| Modifying a `const` object | `const_cast` then write | |
| Returning without a value from a non-void function | falling off the end | |

### How UB breaks code at -O2

```cpp
bool check(int* p) {
    int v = *p;                // UB if p is null…
    if (p == nullptr)          // …so the compiler may DELETE this check
        return false;
    return v > 0;
}

int count_up(int start) {
    int n = 0;
    for (int i = start; i <= start + 10; ++i) ++n;   // compiler assumes no overflow: always 11
    return n;
}
```

> [!DANGER]
> Because UB can be assumed not to happen, its effects can travel **backwards in time**: code that runs *before* the UB can behave unexpectedly, because the compiler reasoned from the UB that a branch is impossible. "It printed fine before it crashed" proves nothing.

## 4. Strict aliasing and type punning

The **strict aliasing rule**: you may access an object only through an lvalue of its own type (ignoring cv-qualifiers and signedness), or through `char`, `unsigned char` or `std::byte`.

```cpp
float f = 1.0f;
std::uint32_t bits = *reinterpret_cast<std::uint32_t*>(&f);   // UB: float accessed as uint32_t

std::uint32_t ok1;
std::memcpy(&ok1, &f, sizeof f);                              // OK: compilers optimise memcpy into a move

auto ok2 = std::bit_cast<std::uint32_t>(f);                   // C++20: OK, constexpr, checks sizes
```

Union type punning (write one member, read another) is allowed in C but is UB in C++, although GCC documents it as an extension. Use `std::bit_cast` or `memcpy`.

> [!KEY]
> `reinterpret_cast` is almost never the right tool for reading bytes as another type. It doesn't create an object. It only changes the pointer type, and the object behind it is still the old type.

## 5. Implicit object creation and `std::launder`

Since C++20, certain operations (`malloc`, `memcpy`, `std::byte` arrays starting their lifetime, `operator new`) **implicitly create** objects of *implicit-lifetime types* (scalars, aggregates and trivially copyable classes) as needed to make the program valid. That retroactively blesses the classic C pattern `auto* p = (Point*)std::malloc(sizeof(Point)); p->x = 1;`.

`std::launder(p)` is needed in a narrow case: you reused storage with placement new for an object that has `const` or reference members (or a different dynamic type), and you want to reach the new object through an **old** pointer. Most code never needs it. Use the pointer returned by placement new instead.

## 6. Order of initialisation and destruction

- Members are initialised in **declaration order**, not in the order of the mem-initializer list (enable `-Wreorder`).
- Destruction happens in reverse order of construction: members, then bases, and locals in reverse.
- **Static initialisation order fiasco**: globals in different translation units are initialised in an unspecified order. A global that uses another TU's global during its own initialisation may see it uninitialised. Fix it with a function-local static (`static Registry& reg() { static Registry r; return r; }`) or `constinit`.

```cpp
struct Bad {
    int size;
    std::vector<int> data;
    Bad(int n) : data(size), size(n) {}   // data(size) runs FIRST: 'size' is uninitialised (UB)
};
```

## 7. Finding UB: sanitizers and tools

| Tool | Flag | Finds |
|---|---|---|
| AddressSanitizer | `-fsanitize=address` | out-of-bounds, use-after-free, use-after-return, double free, leaks |
| UBSan | `-fsanitize=undefined` | signed overflow, bad shifts, null deref, misalignment, invalid enum/bool values |
| ThreadSanitizer | `-fsanitize=thread` | data races, lock-order inversions |
| MemorySanitizer (Clang) | `-fsanitize=memory` | uninitialised reads |
| Valgrind memcheck | `valgrind ./a.out` | similar to ASan, without recompiling (slower) |
| Compiler warnings | `-Wall -Wextra -Wpedantic -Wshadow -Wconversion -Wnull-dereference -Wdangling-reference` (GCC 14) | many lifetime bugs at compile time |
| constexpr evaluation | `static_assert(f())` | the compiler **must** reject UB inside constant evaluation |
| `_GLIBCXX_ASSERTIONS` / `-D_LIBCPP_HARDENING_MODE` | | bounds checks in `operator[]`, iterator checks |

> [!TIP]
> Compile tests with `-fsanitize=address,undefined -fno-omit-frame-pointer -g`, and keep a TSan build for concurrent code. A clean sanitizer run on a good test suite is the closest practical thing to "proved free of these UBs".

## 8. Exam-ready answers

> [!EXAM]
> **Undefined behaviour.** Undefined behaviour is behaviour for which the C++ standard imposes no requirements, such as signed integer overflow, out-of-bounds access, dereferencing null or dangling pointers, data races and strict-aliasing violations. Because compilers may assume UB never occurs, they can optimise on that basis: removing checks, reordering code or assuming loop bounds. The resulting failures may appear only under optimisation and may seem to affect code executed before the faulty operation. UB differs from unspecified behaviour (one of several allowed outcomes, such as evaluation order of function arguments) and implementation-defined behaviour (an outcome the implementation must document, such as the size of `int`).

> [!EXAM]
> **Object lifetime.** An object's lifetime begins when its storage has been obtained and its initialisation is complete, and ends when its destructor call begins or its storage is released or reused. Accessing an object outside its lifetime, for example through a reference to a destroyed temporary, a pointer to a local after its function returns, or an iterator invalidated by container reallocation, is undefined behaviour. Temporaries normally live until the end of the full-expression; binding one directly to a const lvalue reference or rvalue reference extends its lifetime to that of the reference.

## 9. Cheat sheet

| Situation | Safe practice |
|---|---|
| return a local | by value (move/NRVO), never `&`, `string_view` or `span` to it |
| keep a pointer into a vector | indices, or `reserve` first and never grow |
| type punning | `std::bit_cast` / `std::memcpy` |
| raw storage | `alignas(T) std::byte buf[sizeof(T)]` + placement new + explicit destructor call |
| global depending on another global | function-local static or `constinit` |
| arithmetic that may overflow | wider type, `__builtin_add_overflow`, or C++26 `std::add_sat` |
| test builds | `-fsanitize=address,undefined`, plus `-fsanitize=thread` for threads |

> [!INTERVIEW]
> **"Is `i++ + i++` undefined?"** Yes. Two unsequenced modifications of the same scalar are UB. (C++17 sequenced some cases such as `a[i] = i++`, `<<` chains and assignment right-to-left, but not this one.) Follow-up: "unspecified vs undefined?" In `f(g(), h())`, whether `g` or `h` runs first is unspecified: both orders are valid, and the program isn't broken. Contrast that with UB, where *no* requirement remains.
