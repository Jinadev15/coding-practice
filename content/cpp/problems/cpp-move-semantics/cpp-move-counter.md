---
id: cpp-move-counter
title: Count the Copies
difficulty: Hard
order: 1
tags: move semantics, std::move, emplace_back, RVO
---
## Statement
`Blob` (provided) counts its copies and moves in global counters. Implement four functions so that the driver's measured counts match the **minimum possible**:

| Function | Requirement |
|---|---|
| `Blob make_blob(int n)` | returns a new Blob of size n: **0 copies, 0 moves** (rely on RVO; don't `std::move` the return) |
| `void append_temp(std::vector<Blob>& v, int n)` | adds a new Blob of size n: **0 copies, 0 moves** (construct in place) |
| `void append_steal(std::vector<Blob>& v, Blob& b)` | adds `b` without copying: **1 move** (b may be left empty) |
| `class Holder` with constructor `Holder(Blob b)` | stores its parameter: callers passing a temporary → **1 move**, passing an lvalue → **1 copy + 1 move** |

The vector has `reserve`d enough space, so there are no reallocation moves.

## Starter
```cpp
#include <vector>
#include <utility>
#include <cstddef>

int COPIES = 0, MOVES = 0;

struct Blob {
    std::vector<int> data;
    explicit Blob(int n) : data(static_cast<std::size_t>(n), 7) {}
    Blob(const Blob& o) : data(o.data) { ++COPIES; }
    Blob(Blob&& o) noexcept : data(std::move(o.data)) { ++MOVES; }
    Blob& operator=(const Blob&) = default;
    Blob& operator=(Blob&&) = default;
};

Blob make_blob(int n) {
    Blob b(n);
    return std::move(b);
}

void append_temp(std::vector<Blob>& v, int n) {
    v.push_back(Blob(n));
}

void append_steal(std::vector<Blob>& v, Blob& b) {
    v.push_back(b);
}

class Holder {
public:
    Blob blob;
    Holder(Blob b) : blob(b) {}
};
```

## Driver
```cpp
#include <iostream>
static void report(const char* what) {
    std::cout << what << ": copies=" << COPIES << " moves=" << MOVES << '\n';
    COPIES = MOVES = 0;
}
int main() {
    int n; std::cin >> n;
    std::vector<Blob> v; v.reserve(8);
    Blob a = make_blob(n);                report("make_blob");
    append_temp(v, n);                    report("append_temp");
    append_steal(v, a);                   report("append_steal");
    Holder h1{Blob(n)};                   report("holder_temp");
    Blob b(n);
    Holder h2(b);                         report("holder_lvalue");
    std::cout << "sizes " << v[0].data.size() << ' ' << v[1].data.size() << ' ' << a.data.size()
              << ' ' << h1.blob.data.size() << ' ' << h2.blob.data.size() << '\n';
}
```

## Tests
=== sample
3
---
make_blob: copies=0 moves=0
append_temp: copies=0 moves=0
append_steal: copies=0 moves=1
holder_temp: copies=0 moves=1
holder_lvalue: copies=1 moves=1
sizes 3 3 0 3 3

## Hints
- `return b;` (not `return std::move(b);`) lets the compiler apply NRVO. gcc elides even at `-O0`.
- `v.emplace_back(n)` constructs the Blob directly inside the vector.
- `v.push_back(std::move(b))` moves.
- `Holder(Blob b) : blob(std::move(b)) {}`: the parameter is a named object, an lvalue, so it must be moved explicitly into the member.
- `Holder h1{Blob(n)};` (braces, because `Holder h1(Blob(n));` would be the *most vexing parse*, declaring a function): guaranteed copy elision constructs the temporary directly as the parameter, so the only operation is the move into the member.

## Solution
```cpp
#include <vector>
#include <utility>
#include <cstddef>

int COPIES = 0, MOVES = 0;

struct Blob {
    std::vector<int> data;
    explicit Blob(int n) : data(static_cast<std::size_t>(n), 7) {}
    Blob(const Blob& o) : data(o.data) { ++COPIES; }
    Blob(Blob&& o) noexcept : data(std::move(o.data)) { ++MOVES; }
    Blob& operator=(const Blob&) = default;
    Blob& operator=(Blob&&) = default;
};

Blob make_blob(int n) {
    Blob b(n);
    return b;
}

void append_temp(std::vector<Blob>& v, int n) {
    v.emplace_back(n);
}

void append_steal(std::vector<Blob>& v, Blob& b) {
    v.push_back(std::move(b));
}

class Holder {
public:
    Blob blob;
    Holder(Blob b) : blob(std::move(b)) {}
};
```

The starter does everything "almost right": `return std::move(b)` **blocks** NRVO (1 move), `push_back(Blob(n))` creates a temporary and moves it (1 move), `push_back(b)` copies, and `blob(b)` copies from the named parameter. Counting special-member calls like this is how you verify move-correctness in real code, and the same technique applies to profiling allocations in performance-critical robotics loops.
