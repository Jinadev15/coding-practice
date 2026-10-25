---
id: cpp-mini-vector
title: Implement std::vector (Exception-Safe)
difficulty: Expert
order: 1
tags: interview, rule of five, placement new, move_if_noexcept, strong guarantee, iterator, templates
time_limit: 4
---
## Statement
"Implement `vector`" is the definitive C++ interview question. Write `template <typename T> class Vec` over **raw storage**: allocate with `::operator new`, construct with placement new or `std::construct_at`, and destroy explicitly. `T` need not be default-constructible.

**Interface**
- `Vec()`, `~Vec()`, copy constructor and copy assignment, `noexcept` move constructor and move assignment (the source is left empty with capacity 0).
- `size()`, `capacity()`, `empty()`, `operator[]`, `at(i)` (throws `std::out_of_range`), `T* begin()`, `T* end()` (const overloads too), `front()`, `back()`.
- `push_back(const T&)`, `push_back(T&&)`, `template <class... A> T& emplace_back(A&&...)`, `pop_back()`, `clear()` (keeps the capacity), `reserve(n)`.
- `T* insert(const T* pos, const T& value)`: inserts before `pos` and returns a pointer to the new element.
- `T* erase(const T* pos)`: returns a pointer to the element after the erased one.

**Rules the judge checks** (with an instrumented element type that counts live objects, copies and moves, and can throw):
- Growth when full: the new capacity is `max(1, 2 * capacity)`. `reserve(n)` with `n <= capacity` does nothing. Otherwise the capacity becomes exactly `n`.
- Reallocation **moves** elements if `T`'s move constructor is `noexcept`, and otherwise **copies** them (`std::move_if_noexcept`).
- **Strong guarantee** for `push_back`, `emplace_back`, `reserve` and copy assignment: if a constructor throws, the vector is unchanged (same size, capacity and contents) and nothing leaks.
- `v.push_back(v[0])` must work even when it triggers reallocation (aliasing).
- No leaks: every constructed element is destroyed exactly once.

## Starter
```cpp
#include <cstddef>
#include <memory>
#include <new>
#include <stdexcept>
#include <utility>

template <typename T>
class Vec {
public:
    Vec() = default;
    ~Vec() { delete[] data_; }
    std::size_t size() const { return size_; }
    std::size_t capacity() const { return cap_; }
    bool empty() const { return size_ == 0; }
    T& operator[](std::size_t i) { return data_[i]; }
    const T& operator[](std::size_t i) const { return data_[i]; }
    T& at(std::size_t i) { return data_[i]; }
    T* begin() { return data_; }
    T* end() { return data_ + size_; }
    const T* begin() const { return data_; }
    const T* end() const { return data_ + size_; }
    T& front() { return data_[0]; }
    T& back() { return data_[size_ - 1]; }
    void push_back(const T& v) { grow(); data_[size_++] = v; }
    void push_back(T&& v) { grow(); data_[size_++] = std::move(v); }
    template <class... A> T& emplace_back(A&&... a) { grow(); data_[size_] = T(std::forward<A>(a)...); return data_[size_++]; }
    void pop_back() { --size_; }
    void clear() { size_ = 0; }
    void reserve(std::size_t) {}
    T* insert(const T* pos, const T& v) { return nullptr; }
    T* erase(const T* pos) { return nullptr; }
private:
    void grow() {
        if (size_ < cap_) return;
        std::size_t nc = cap_ ? cap_ * 2 : 1;
        T* nd = new T[nc];
        for (std::size_t i = 0; i < size_; ++i) nd[i] = data_[i];
        delete[] data_; data_ = nd; cap_ = nc;
    }
    T* data_ = nullptr;
    std::size_t size_ = 0, cap_ = 0;
};
```

## Driver
```cpp
#include <cstdio>
#include <iostream>
#include <string>

struct Stats { long live = 0, copies = 0, moves = 0, throw_at = -1; } S;

template <bool NoexceptMove>
struct Tr {
    std::string v;
    explicit Tr(std::string s) : v(std::move(s)) { ++S.live; }
    Tr(const Tr& o) : v(o.v) {
        if (S.throw_at >= 0 && S.copies == S.throw_at) throw std::runtime_error("copy failed");
        ++S.copies; ++S.live;
    }
    Tr(Tr&& o) noexcept(NoexceptMove) : v(std::move(o.v)) { ++S.moves; ++S.live; }
    Tr& operator=(const Tr& o) { v = o.v; ++S.copies; return *this; }
    Tr& operator=(Tr&& o) noexcept { v = std::move(o.v); ++S.moves; return *this; }
    ~Tr() { --S.live; }
};
using Good = Tr<true>;
using Risky = Tr<false>;

template <class V> void dump(const char* label, const V& v) {
    std::printf("%s size=%zu cap=%zu [", label, v.size(), v.capacity());
    for (auto it = v.begin(); it != v.end(); ++it) std::printf("%s%s", it == v.begin() ? "" : " ", it->v.c_str());
    std::printf("] live=%ld\n", S.live);
}
static void reset_counts() { S.copies = S.moves = 0; S.throw_at = -1; }

int main() {
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "basic") {
            {
                Vec<Good> v;
                for (int i = 0; i < 5; ++i) v.emplace_back(std::to_string(i));
                dump("emplace", v);
                Good g("x"); v.push_back(g); v.push_back(Good("y"));
                dump("push", v);
                v.pop_back(); v.erase(v.begin() + 1); dump("erase", v);
                Good* p = v.insert(v.begin() + 2, Good("ins")); std::printf("inserted %s at %td\n", p->v.c_str(), p - v.begin());
                p = v.insert(v.end(), Good("tail")); dump("insert", v);
                Good* nxt = v.erase(v.end() - 1); std::printf("erase last -> end? %d\n", nxt == v.end());
                try { v.at(100); } catch (const std::out_of_range&) { std::printf("at throws\n"); }
                std::printf("front %s back %s\n", v.front().v.c_str(), v.back().v.c_str());
                v.reserve(3); dump("reserve small", v); v.reserve(20); dump("reserve 20", v);
                v.clear(); dump("clear", v);
            }
            std::printf("live after scope %ld\n", S.live);
        } else if (cmd == "moves") {
            reset_counts();
            { Vec<Good> v; for (int i = 0; i < 9; ++i) v.emplace_back("g"); std::printf("noexcept move: copies=%ld moves=%ld cap=%zu\n", S.copies, S.moves, v.capacity()); }
            reset_counts();
            { Vec<Risky> v; for (int i = 0; i < 9; ++i) v.emplace_back("r"); std::printf("throwing move: copies=%ld moves=%ld cap=%zu\n", S.copies, S.moves, v.capacity()); }
            reset_counts();
            {
                Vec<Good> a; for (int i = 0; i < 4; ++i) a.emplace_back(std::to_string(i * 11));
                Vec<Good> b(a); Vec<Good> c; c = a; c = c;
                Vec<Good> d(std::move(a)); Vec<Good> e; e = std::move(b);
                dump("a(moved)", a); dump("d", d); dump("e", e); dump("c", c);
                std::printf("copies=%ld\n", S.copies);
            }
            std::printf("live %ld\n", S.live);
        } else if (cmd == "alias") {
            reset_counts();
            {
                Vec<Good> v; v.emplace_back("first"); v.emplace_back("second");
                for (int i = 0; i < 6; ++i) v.push_back(v[0]);          // v[0] referenced during reallocation
                v.push_back(std::move(v[1]));
                dump("alias", v);
                Vec<Good> w; w.emplace_back("self"); w.insert(w.begin(), w[0]); w.insert(w.begin() + 1, w.back()); dump("insert alias", w);
            }
            std::printf("live %ld\n", S.live);
        } else if (cmd == "strong") {
            reset_counts();
            {
                Vec<Risky> v;
                for (int i = 0; i < 4; ++i) v.emplace_back("r" + std::to_string(i));
                S.copies = 0; S.throw_at = 2;                          // 3rd copy during reallocation throws
                try { v.push_back(Risky("new")); } catch (const std::exception& e) { std::printf("push threw: %s\n", e.what()); }
                dump("after failed push", v);
                S.copies = 0; S.throw_at = 1;
                try { v.reserve(100); } catch (const std::exception&) { std::printf("reserve threw\n"); }
                dump("after failed reserve", v);
                S.throw_at = -1;
                Vec<Risky> big; for (int i = 0; i < 6; ++i) big.emplace_back("b" + std::to_string(i));
                S.copies = 0; S.throw_at = 3;
                try { v = big; } catch (const std::exception&) { std::printf("assign threw\n"); }
                dump("after failed assign", v);
                S.throw_at = -1; v = big; dump("assign ok", v);
                Risky src("copyme"); S.copies = 0; S.throw_at = 0;
                Vec<Risky> one; one.reserve(2);
                try { one.push_back(src); } catch (const std::exception&) { std::printf("element copy threw\n"); }
                dump("one", one);
            }
            std::printf("live %ld\n", S.live);
        } else if (cmd == "big") {
            reset_counts();
            {
                Vec<Good> v; unsigned long long h = 0;
                for (int i = 0; i < 200000; ++i) v.emplace_back(std::to_string(i % 1000));
                for (int i = 0; i < 1000; ++i) v.erase(v.begin() + (i * 37 % v.size()));
                for (int i = 0; i < 500; ++i) v.insert(v.begin() + (i * 53 % v.size()), Good("z"));
                for (auto& x : v) h = h * 131 + std::hash<std::string>{}(x.v) % 1000003;
                std::printf("size %zu cap %zu hash %llu moves>0 %d\n", v.size(), v.capacity(), h % 1000000007ULL, S.moves > 0);
            }
            std::printf("live %ld\n", S.live);
        }
    }
}
```

## Tests
=== sample
basic
moves
---
emplace size=5 cap=8 [0 1 2 3 4] live=5
push size=7 cap=8 [0 1 2 3 4 x y] live=8
erase size=5 cap=8 [0 2 3 4 x] live=6
inserted ins at 2
insert size=7 cap=8 [0 2 ins 3 4 x tail] live=8
erase last -> end? 1
at throws
front 0 back x
reserve small size=6 cap=8 [0 2 ins 3 4 x] live=7
reserve 20 size=6 cap=20 [0 2 ins 3 4 x] live=7
clear size=0 cap=20 [] live=1
live after scope 0
noexcept move: copies=0 moves=15 cap=16
throwing move: copies=15 moves=0 cap=16
a(moved) size=0 cap=0 [] live=12
d size=4 cap=4 [0 11 22 33] live=12
e size=4 cap=4 [0 11 22 33] live=12
c size=4 cap=4 [0 11 22 33] live=12
copies=8
live 0
=== hidden
alias
---
alias size=9 cap=16 [first  first first first first first first second] live=9
insert alias size=3 cap=4 [self self self] live=12
live 0
=== hidden
strong
---
push threw: copy failed
after failed push size=4 cap=4 [r0 r1 r2 r3] live=4
reserve threw
after failed reserve size=4 cap=4 [r0 r1 r2 r3] live=4
assign threw
after failed assign size=4 cap=4 [r0 r1 r2 r3] live=10
assign ok size=6 cap=6 [b0 b1 b2 b3 b4 b5] live=12
element copy threw
one size=0 cap=2 [] live=13
live 0
=== hidden
big
---
size 199500 cap 262144 hash 147115272 moves>0 1
live 0

## Hints
- Raw storage: `T* p = static_cast<T*>(::operator new(n * sizeof(T)));`, `std::construct_at(p + i, args...)`, `std::destroy_at(p + i)`, `::operator delete(p)`. Use `std::uninitialized_*` helpers or write the loops yourself.
- Reallocation: allocate new storage, then **construct the new element first** at index `size` (this handles `push_back(v[0])`, whose reference still points into the old buffer). Then move-or-copy the old elements with `std::move_if_noexcept`. If anything throws, destroy what you built in the new buffer and free it. Only then destroy the old elements and swap the buffers.
- Copy assignment: copy-and-swap (`Vec tmp(o); swap(tmp);`) gives the strong guarantee.
- `insert(pos, value)`: copy `value` into a local first (it may alias an element), then append, then rotate it into place with `std::rotate` or a series of move assignments.

## Solution
```cpp
#include <algorithm>
#include <cstddef>
#include <memory>
#include <new>
#include <stdexcept>
#include <utility>

template <typename T>
class Vec {
public:
    Vec() = default;
    ~Vec() { destroy_all(); ::operator delete(data_); }

    Vec(const Vec& o) : data_(alloc(o.size_)), cap_(o.size_) {
        try {
            for (; size_ < o.size_; ++size_) std::construct_at(data_ + size_, o.data_[size_]);
        } catch (...) {
            destroy_all(); ::operator delete(data_);
            throw;
        }
    }
    Vec(Vec&& o) noexcept
        : data_(std::exchange(o.data_, nullptr)), size_(std::exchange(o.size_, 0)), cap_(std::exchange(o.cap_, 0)) {}
    Vec& operator=(const Vec& o) {
        if (this != &o) { Vec tmp(o); swap(tmp); }        // copy-and-swap: strong guarantee
        return *this;
    }
    Vec& operator=(Vec&& o) noexcept {
        if (this != &o) { Vec tmp(std::move(o)); swap(tmp); }
        return *this;
    }
    void swap(Vec& o) noexcept {
        std::swap(data_, o.data_); std::swap(size_, o.size_); std::swap(cap_, o.cap_);
    }

    std::size_t size() const { return size_; }
    std::size_t capacity() const { return cap_; }
    bool empty() const { return size_ == 0; }
    T& operator[](std::size_t i) { return data_[i]; }
    const T& operator[](std::size_t i) const { return data_[i]; }
    T& at(std::size_t i) { if (i >= size_) throw std::out_of_range("Vec::at"); return data_[i]; }
    const T& at(std::size_t i) const { if (i >= size_) throw std::out_of_range("Vec::at"); return data_[i]; }
    T* begin() { return data_; }
    T* end() { return data_ + size_; }
    const T* begin() const { return data_; }
    const T* end() const { return data_ + size_; }
    T& front() { return data_[0]; }
    T& back() { return data_[size_ - 1]; }

    void push_back(const T& v) { emplace_back(v); }
    void push_back(T&& v) { emplace_back(std::move(v)); }

    template <class... A>
    T& emplace_back(A&&... args) {
        if (size_ < cap_) {
            std::construct_at(data_ + size_, std::forward<A>(args)...);
            return data_[size_++];
        }
        const std::size_t nc = cap_ ? cap_ * 2 : 1;
        T* nd = alloc(nc);
        std::size_t built = 0;
        try {
            std::construct_at(nd + size_, std::forward<A>(args)...);   // new element first: args may alias old storage
            try {
                for (; built < size_; ++built) std::construct_at(nd + built, std::move_if_noexcept(data_[built]));
            } catch (...) {
                std::destroy_at(nd + size_);
                throw;
            }
        } catch (...) {
            std::destroy(nd, nd + built);
            ::operator delete(nd);
            throw;                                                     // *this untouched
        }
        const std::size_t n_old = size_;
        destroy_all();                                                 // also resets size_
        ::operator delete(data_);
        data_ = nd; cap_ = nc; size_ = n_old + 1;
        return data_[n_old];
    }

    void pop_back() { std::destroy_at(data_ + --size_); }
    void clear() { destroy_all(); }

    void reserve(std::size_t n) {
        if (n <= cap_) return;
        T* nd = alloc(n);
        std::size_t built = 0;
        try {
            for (; built < size_; ++built) std::construct_at(nd + built, std::move_if_noexcept(data_[built]));
        } catch (...) {
            std::destroy(nd, nd + built);
            ::operator delete(nd);
            throw;
        }
        const std::size_t n_old = size_;
        destroy_all();
        ::operator delete(data_);
        data_ = nd; cap_ = n; size_ = n_old;
    }

    T* insert(const T* pos, const T& value) {
        const std::size_t idx = static_cast<std::size_t>(pos - data_);
        T copy(value);                                   // value may refer to one of our elements
        emplace_back(std::move(copy));
        std::rotate(data_ + idx, data_ + size_ - 1, data_ + size_);
        return data_ + idx;
    }

    T* erase(const T* pos) {
        const std::size_t idx = static_cast<std::size_t>(pos - data_);
        std::move(data_ + idx + 1, data_ + size_, data_ + idx);
        pop_back();
        return data_ + idx;
    }

private:
    static T* alloc(std::size_t n) { return n ? static_cast<T*>(::operator new(n * sizeof(T))) : nullptr; }
    void destroy_all() noexcept { std::destroy(data_, data_ + size_); size_ = 0; }

    T* data_ = nullptr;
    std::size_t size_ = 0, cap_ = 0;
};
```

- **Raw storage, not `new T[n]`**: `new T[]` default-constructs every slot, which needs a default constructor and wastes work. Separating allocation from construction is what lets capacity exceed size.
- **Construct the new element first** during reallocation. `push_back(v[0])` passes a reference into the old buffer, which stays valid until the very end because the old elements are destroyed last.
- **`std::move_if_noexcept`**: if moving could throw halfway through, the moved-from originals would be damaged, so the strong guarantee would be impossible. In that case the vector copies instead, exactly like `std::vector`. That's why your move constructors should be `noexcept`.
- **Commit-or-rollback**: every throwing step works on the new buffer and cleans up what it built. The old state is only touched after everything has succeeded. Copy assignment gets the same guarantee from copy-and-swap.
- **The instrumented type** proves no leaks (`live` returns to 0) and counts copies versus moves. That's how real container implementations are tested.
