---
id: cpp-string-buffer
title: Rule of Five: A Resource-Owning Buffer
difficulty: Hard
order: 1
tags: rule of five, copy and swap, deep copy, move
---
## Statement
Implement a class `IntBuffer` that owns a raw `int*` array (the exercise forbids `std::vector` inside it), with the full **Rule of Five**:

- `explicit IntBuffer(std::size_t n, int fill = 0)`
- destructor (frees the array)
- copy constructor: a **deep** copy
- move constructor: steals, leaving the source with `size() == 0` and a null pointer (`noexcept`)
- copy and move assignment: use **copy-and-swap** (`IntBuffer& operator=(IntBuffer other) noexcept`)
- `std::size_t size() const`, `int& operator[](std::size_t)`, `int sum() const`

The driver's global allocation counter verifies there are no leaks and no double frees (a double free would crash).

## Starter
```cpp
#include <cstddef>
#include <utility>
#include <algorithm>

class IntBuffer {
    std::size_t n_ = 0;
    int* data_ = nullptr;
public:
    explicit IntBuffer(std::size_t n, int fill = 0) : n_(n), data_(new int[n]) {
        std::fill(data_, data_ + n_, fill);
    }
    ~IntBuffer() { delete[] data_; }
    std::size_t size() const { return n_; }
    int& operator[](std::size_t i) { return data_[i]; }
    int sum() const { int s = 0; for (std::size_t i = 0; i < n_; ++i) s += data_[i]; return s; }
};
```

## Driver
```cpp
#include <iostream>
#include <cstdlib>
#include <new>
#include <vector>
static long live = 0;
void* operator new[](std::size_t n) { ++live; if (void* p = std::malloc(n)) return p; throw std::bad_alloc(); }
void operator delete[](void* p) noexcept { if (p) { --live; std::free(p); } }
void operator delete[](void* p, std::size_t) noexcept { if (p) { --live; std::free(p); } }
int main() {
    {
        IntBuffer a(3, 1);
        IntBuffer b = a;              // deep copy
        b[0] = 100;
        std::cout << a.sum() << ' ' << b.sum() << '\n';
        IntBuffer c = std::move(b);   // steal
        std::cout << b.size() << ' ' << c.sum() << '\n';
        a = c;                        // copy assignment
        c[1] = 50;
        std::cout << a.sum() << ' ' << c.sum() << '\n';
        a = IntBuffer(2, 9);          // move assignment from a temporary
        std::cout << a.size() << ' ' << a.sum() << '\n';
        a = a;                        // self-assignment must be safe
        std::cout << a.sum() << '\n';
        std::vector<IntBuffer> v;
        for (int i = 0; i < 5; ++i) v.push_back(IntBuffer(1, i));
        int total = 0; for (auto& x : v) total += x.sum();
        std::cout << "vector total " << total << '\n';
    }
    std::cout << "live arrays " << live << '\n';
}
```

## Tests
=== sample
---
3 102
0 102
102 151
2 18
18
vector total 10
live arrays 0

## Hints
- Copy constructor: allocate `new int[o.n_]` and `std::copy` the elements.
- Move constructor: `n_(std::exchange(o.n_, 0)), data_(std::exchange(o.data_, nullptr))`.
- `friend void swap(IntBuffer& a, IntBuffer& b) noexcept` swaps both members. The by-value assignment parameter is built by a copy (from lvalues) or a move (from rvalues).
- `delete[]` on `nullptr` is safe, so a moved-from object's destructor is fine.

## Solution
```cpp
#include <cstddef>
#include <utility>
#include <algorithm>

class IntBuffer {
    std::size_t n_ = 0;
    int* data_ = nullptr;
public:
    explicit IntBuffer(std::size_t n, int fill = 0) : n_(n), data_(new int[n]) {
        std::fill(data_, data_ + n_, fill);
    }
    ~IntBuffer() { delete[] data_; }

    IntBuffer(const IntBuffer& o) : n_(o.n_), data_(new int[o.n_]) {
        std::copy(o.data_, o.data_ + n_, data_);
    }
    IntBuffer(IntBuffer&& o) noexcept
        : n_(std::exchange(o.n_, 0)), data_(std::exchange(o.data_, nullptr)) {}

    IntBuffer& operator=(IntBuffer other) noexcept {
        swap(*this, other);
        return *this;
    }
    friend void swap(IntBuffer& a, IntBuffer& b) noexcept {
        std::swap(a.n_, b.n_);
        std::swap(a.data_, b.data_);
    }

    std::size_t size() const { return n_; }
    int& operator[](std::size_t i) { return data_[i]; }
    int sum() const {
        int s = 0;
        for (std::size_t i = 0; i < n_; ++i) s += data_[i];
        return s;
    }
};
```

The starter has only a destructor (the Rule of Three violation), so `IntBuffer b = a;` copies the pointer and the program crashes with a double free at the end of scope. Copy-and-swap handles self-assignment with no special check: `a = a` copies `a` into the parameter, swaps, and the old copy is freed. In real code you'd write this class as `std::vector<int>` (Rule of Zero). This exercise shows exactly what the vector does for you.
