---
id: cpp-static-vector
title: StaticVector<T, N>: a Fixed-Capacity Container
difficulty: Hard
order: 1
tags: class templates, placement new, aligned storage, rule of five, iterators
---
## Statement
Embedded and real-time code often can't use the heap, but still wants a vector-like container. Implement `StaticVector<T, N>` (like `boost::static_vector` or C++26's `std::inplace_vector`): up to `N` elements stored **inside the object**, constructed only when added. It must work for types **without a default constructor** and for **move-only** types, so you can't use `std::array<T, N>`, which would default-construct N objects. Use raw aligned storage and placement new.

```cpp
template <typename T, std::size_t N>
class StaticVector {
public:
    StaticVector() noexcept;
    StaticVector(std::initializer_list<T>);        // throws std::length_error if it's longer than N
    StaticVector(const StaticVector&); StaticVector(StaticVector&&) noexcept(std::is_nothrow_move_constructible_v<T>);
    StaticVector& operator=(const StaticVector&); StaticVector& operator=(StaticVector&&);
    ~StaticVector();                                // destroys exactly the live elements

    template <typename... Args> T& emplace_back(Args&&... args);   // throws std::length_error when full
    void push_back(const T& v); void push_back(T&& v);
    void pop_back();                                // destroys the last element (precondition: not empty)
    void clear() noexcept;

    T& operator[](std::size_t i); const T& operator[](std::size_t i) const;
    T* begin(); T* end(); const T* begin() const; const T* end() const;
    std::size_t size() const noexcept;
    static constexpr std::size_t capacity() noexcept { return N; }
    bool empty() const noexcept;
};
```

The driver uses an instrumented element type that counts live objects, constructions and destructions, a move-only `std::unique_ptr`, and a type without a default constructor. It checks that no element is ever constructed until it's added, and that every element is destroyed exactly once.

## Starter
```cpp
#include <array>
#include <cstddef>
#include <initializer_list>
#include <stdexcept>
#include <utility>
#include <type_traits>

template <typename T, std::size_t N>
class StaticVector {
public:
    StaticVector() = default;
    template <typename... Args> T& emplace_back(Args&&... args) { data_[n_] = T(std::forward<Args>(args)...); return data_[n_++]; }
    void push_back(const T& v) { emplace_back(v); }
    void pop_back() { --n_; }
    T& operator[](std::size_t i) { return data_[i]; }
    T* begin() { return data_.data(); }
    T* end() { return data_.data() + n_; }
    std::size_t size() const noexcept { return n_; }
    static constexpr std::size_t capacity() noexcept { return N; }
private:
    std::array<T, N> data_;
    std::size_t n_ = 0;
};
```

## Driver
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <numeric>

struct Probe {                                  // counts lifetimes
    static inline int live = 0, constructed = 0, destroyed = 0;
    int v;
    explicit Probe(int x) : v(x) { ++live; ++constructed; }
    Probe(const Probe& o) : v(o.v) { ++live; ++constructed; }
    Probe(Probe&& o) noexcept : v(o.v) { o.v = -1; ++live; ++constructed; }
    Probe& operator=(const Probe&) = default;
    Probe& operator=(Probe&&) noexcept = default;
    ~Probe() { --live; ++destroyed; }
};
struct NoDefault { explicit NoDefault(std::string s) : s(std::move(s)) {} std::string s; };

static_assert(sizeof(StaticVector<char, 16>) <= 32, "storage must be inline");

int main() {
    std::string cmd;
    std::cin >> cmd;
    if (cmd == "lifetimes") {
        {
            StaticVector<Probe, 8> v;
            std::cout << "after construct: live=" << Probe::live << '\n';
            v.emplace_back(1); v.emplace_back(2); v.push_back(Probe(3));
            std::cout << "size=" << v.size() << " live=" << Probe::live << '\n';
            v.pop_back();
            std::cout << "after pop: live=" << Probe::live << '\n';
            StaticVector<Probe, 8> c = v;
            StaticVector<Probe, 8> m = std::move(c);
            std::cout << "copies: " << v[0].v << v[1].v << " / " << m[0].v << m[1].v << " live=" << Probe::live << '\n';
            v = m;
            v.emplace_back(9);
            int sum = 0;
            for (const auto& p : v) sum += p.v;
            std::cout << "sum=" << sum << " live=" << Probe::live << '\n';
            v.clear();
            std::cout << "after clear: live=" << Probe::live << " empty=" << v.empty() << '\n';
        }
        std::cout << "end: live=" << Probe::live << " balanced=" << (Probe::constructed == Probe::destroyed) << '\n';
    } else if (cmd == "full") {
        StaticVector<int, 3> v{1, 2, 3};
        try { v.push_back(4); std::cout << "no throw\n"; }
        catch (const std::length_error&) { std::cout << "full: length_error size=" << v.size() << '\n'; }
        try { StaticVector<int, 2> w{1, 2, 3}; std::cout << "no throw\n"; }
        catch (const std::length_error&) { std::cout << "init list too long: length_error\n"; }
        std::cout << "capacity=" << decltype(v)::capacity() << " sum=" << std::accumulate(v.begin(), v.end(), 0) << '\n';
    } else if (cmd == "moveonly") {
        StaticVector<std::unique_ptr<int>, 4> v;
        for (int i = 1; i <= 4; ++i) v.push_back(std::make_unique<int>(i * 10));
        StaticVector<std::unique_ptr<int>, 4> w = std::move(v);
        std::cout << "moved: " << *w[0] << ' ' << *w[3] << " size=" << w.size() << '\n';
        StaticVector<NoDefault, 2> nd;
        nd.emplace_back("lidar");
        nd.emplace_back("imu");
        std::cout << "no-default: " << nd[0].s << ' ' << nd[1].s << '\n';
    }
}
```

## Tests
=== sample
lifetimes
---
after construct: live=0
size=3 live=3
after pop: live=2
copies: 12 / 12 live=4
sum=12 live=5
after clear: live=2 empty=1
end: live=0 balanced=1
=== hidden
full
---
full: length_error size=3
init list too long: length_error
capacity=3 sum=6
=== hidden
moveonly
---
moved: 10 40 size=4
no-default: lidar imu

## Hints
- Storage: `alignas(T) std::byte buf_[N * sizeof(T)];` and `T* data() { return std::launder(reinterpret_cast<T*>(buf_)); }`. No `T` objects exist until you construct them.
- Construct in place: `::new (static_cast<void*>(data() + n_)) T(std::forward<Args>(args)...);`, then `++n_` **after** the construction succeeds (it might throw).
- Destroy: `std::destroy_at(data() + i)` (or `p->~T()`) for each live element, in `pop_back`, `clear` and the destructor.
- The copy and move constructors build each element with placement new from the other vector's elements. For assignment, `clear()` then copy or move the elements across (that's simple and correct, though it doesn't give the strong guarantee).

## Solution
```cpp
#include <cstddef>
#include <initializer_list>
#include <stdexcept>
#include <utility>
#include <type_traits>
#include <memory>
#include <new>

template <typename T, std::size_t N>
class StaticVector {
public:
    StaticVector() noexcept = default;

    StaticVector(std::initializer_list<T> il) {
        if (il.size() > N) throw std::length_error("StaticVector: initializer list too long");
        for (const T& v : il) emplace_back(v);
    }
    StaticVector(const StaticVector& o) {
        for (const T& v : o) emplace_back(v);
    }
    StaticVector(StaticVector&& o) noexcept(std::is_nothrow_move_constructible_v<T>) {
        for (T& v : o) emplace_back(std::move(v));
        o.clear();
    }
    StaticVector& operator=(const StaticVector& o) {
        if (this != &o) {
            clear();
            for (const T& v : o) emplace_back(v);
        }
        return *this;
    }
    StaticVector& operator=(StaticVector&& o) {
        if (this != &o) {
            clear();
            for (T& v : o) emplace_back(std::move(v));
            o.clear();
        }
        return *this;
    }
    ~StaticVector() { clear(); }

    template <typename... Args>
    T& emplace_back(Args&&... args) {
        if (n_ == N) throw std::length_error("StaticVector: full");
        T* p = ::new (static_cast<void*>(data() + n_)) T(std::forward<Args>(args)...);
        ++n_;                                           // only after successful construction
        return *p;
    }
    void push_back(const T& v) { emplace_back(v); }
    void push_back(T&& v) { emplace_back(std::move(v)); }
    void pop_back() { std::destroy_at(data() + --n_); }
    void clear() noexcept {
        while (n_ > 0) std::destroy_at(data() + --n_);   // destroy in reverse order
    }

    T& operator[](std::size_t i) { return data()[i]; }
    const T& operator[](std::size_t i) const { return data()[i]; }
    T* begin() { return data(); }
    T* end() { return data() + n_; }
    const T* begin() const { return data(); }
    const T* end() const { return data() + n_; }
    std::size_t size() const noexcept { return n_; }
    static constexpr std::size_t capacity() noexcept { return N; }
    bool empty() const noexcept { return n_ == 0; }

private:
    T* data() noexcept { return std::launder(reinterpret_cast<T*>(buf_)); }
    const T* data() const noexcept { return std::launder(reinterpret_cast<const T*>(buf_)); }

    alignas(T) std::byte buf_[N * sizeof(T)];
    std::size_t n_ = 0;
};
```

**Key ideas:**
- **Raw, aligned storage** (`alignas(T) std::byte[...]`) reserves space without creating objects, so no default constructor is needed and nothing runs until an element is added. That's exactly how `std::vector` treats its spare capacity.
- **Placement new** constructs an object at a given address, and **`std::destroy_at`** ends its lifetime. Every constructed element is destroyed exactly once, which the `Probe` counters verify (`balanced=1`).
- **The template parameter `N`** makes capacity part of the type, and since the storage is inline, there are zero heap allocations. That's the property real-time and embedded code needs.
- **Move-only types** work because elements are moved one by one with `std::move`. They never need copying.
- `std::launder` tells the compiler that a `T` object now lives in storage obtained as bytes. It's a C++17 formality for this kind of low-level container code.
