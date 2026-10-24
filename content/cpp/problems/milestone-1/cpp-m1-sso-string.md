---
id: cpp-m1-sso-string
title: String Class with Small-String Optimisation
difficulty: Hard
order: 1
tags: rule of five, move semantics, operator overloading, RAII, memory layout
---
## Statement
Implement `SString`, a string class with **small-string optimisation (SSO)**: strings of up to **15 characters** are stored *inside the object* with no heap allocation, while longer strings use a heap buffer. `std::string` does exactly this in every major standard library.

```cpp
class SString {
public:
    SString();                                  // empty, no allocation
    SString(const char* s);                     // implicit, like std::string
    SString(const SString&);                    // deep copy (allocates only if long)
    SString(SString&&) noexcept;                // steals the heap buffer; never allocates
    SString& operator=(const SString&);         // strong exception guarantee, self-assignment safe
    SString& operator=(SString&&) noexcept;
    ~SString();

    std::size_t size() const;
    std::size_t capacity() const;               // 15 while small
    bool is_small() const;
    const char* c_str() const;                  // always NUL-terminated
    char& operator[](std::size_t i);
    const char& operator[](std::size_t i) const;

    SString& operator+=(const SString& rhs);    // amortised O(1) growth: at least double the capacity
    friend SString operator+(SString lhs, const SString& rhs);
    friend bool operator==(const SString&, const SString&);
    friend std::strong_ordering operator<=>(const SString&, const SString&);  // lexicographic, like strcmp
    friend std::ostream& operator<<(std::ostream&, const SString&);
};
```

The driver **replaces global `operator new`/`delete` to count heap allocations**, then checks:
- small strings never allocate,
- moves never allocate,
- copies allocate only for long strings,
- repeated `+=` reallocates O(log n) times,
- everything allocated is freed.

The storage scheme is your design choice, but a natural one is a `union { char small[16]; char* heap; }` plus a size and a capacity.

## Starter
```cpp
#include <cstring>
#include <cstddef>
#include <compare>
#include <ostream>
#include <utility>

class SString {
public:
    SString() : data_(new char[1]{}) {}
    SString(const char* s) : len_(std::strlen(s)), data_(new char[len_ + 1]) { std::memcpy(data_, s, len_ + 1); }
    SString(const SString& o) : SString(o.data_) {}
    SString& operator=(const SString& o) { SString t(o); std::swap(len_, t.len_); std::swap(data_, t.data_); return *this; }
    ~SString() { delete[] data_; }

    std::size_t size() const { return len_; }
    std::size_t capacity() const { return len_; }
    bool is_small() const { return false; }
    const char* c_str() const { return data_; }
    char& operator[](std::size_t i) { return data_[i]; }
    const char& operator[](std::size_t i) const { return data_[i]; }

    SString& operator+=(const SString& r) {
        char* n = new char[len_ + r.len_ + 1];
        std::memcpy(n, data_, len_);
        std::memcpy(n + len_, r.data_, r.len_ + 1);
        delete[] data_; data_ = n; len_ += r.len_;
        return *this;
    }
    friend SString operator+(SString l, const SString& r) { l += r; return l; }
    friend bool operator==(const SString& a, const SString& b) { return std::strcmp(a.data_, b.data_) == 0; }
    friend std::strong_ordering operator<=>(const SString& a, const SString& b) { return std::strcmp(a.data_, b.data_) <=> 0; }
    friend std::ostream& operator<<(std::ostream& os, const SString& s) { return os << s.data_; }
private:
    std::size_t len_ = 0;
    char* data_;
};
```

## Driver
```cpp
#include <iostream>
#include <new>
#include <cstdlib>
#include <vector>
#include <algorithm>
#include <string>
#include <type_traits>

static long g_allocs = 0, g_frees = 0;
void* operator new(std::size_t n) { ++g_allocs; if (void* p = std::malloc(n ? n : 1)) return p; throw std::bad_alloc(); }
void* operator new[](std::size_t n) { ++g_allocs; if (void* p = std::malloc(n ? n : 1)) return p; throw std::bad_alloc(); }
void operator delete(void* p) noexcept { if (p) { ++g_frees; std::free(p); } }
void operator delete[](void* p) noexcept { if (p) { ++g_frees; std::free(p); } }
void operator delete(void* p, std::size_t) noexcept { operator delete(p); }
void operator delete[](void* p, std::size_t) noexcept { operator delete[](p); }

static_assert(std::is_nothrow_move_constructible_v<SString>);
static_assert(std::is_nothrow_move_assignable_v<SString>);

#define CHECK(label, expr) std::cout << label << ": " << ((expr) ? "ok" : "FAIL") << '\n'

int main() {
    std::string cmd;
    std::cin >> cmd;
    if (cmd == "basics") {
        long a0 = g_allocs;
        SString e, s("robot"), f("exactly15chars!");
        CHECK("small no alloc", g_allocs == a0 && s.is_small() && f.is_small() && e.size() == 0);
        CHECK("capacity 15", s.capacity() == 15 && f.size() == 15);
        SString l("this one is definitely long");
        CHECK("long allocates once", g_allocs == a0 + 1 && !l.is_small());
        long a1 = g_allocs;
        SString c1 = s, c2 = l;
        CHECK("copy small: 0 allocs, copy long: 1", g_allocs == a1 + 1);
        SString m1 = std::move(l), m2 = std::move(s);
        CHECK("moves never allocate", g_allocs == a1 + 1);
        CHECK("moved values", m1 == c2 && m2 == "robot");
        c1 = c1;
        c2 = c2;
        CHECK("self-assignment", c1 == "robot" && c2 == "this one is definitely long");
        c1 = c2; c2 = "tiny";
        CHECK("assign long into small and small into long", c1 == m1 && c2 == "tiny" && c2.is_small());
        m2[0] = 'R';
        std::cout << m2 << ' ' << m2.size() << ' ' << (m2 < c2) << (c2 < m2) << (SString("abc") < SString("abd")) << (SString("ab") < SString("abc")) << '\n';
        SString x = SString("ab") + "cd" + SString("ef");
        std::cout << x << ' ' << x.is_small() << ' ' << std::strlen(x.c_str()) << '\n';
    } else if (cmd == "grow") {
        int n; std::cin >> n;
        long a0 = g_allocs;
        SString s;
        for (int i = 0; i < n; ++i) s += "x";
        long reallocs = g_allocs - a0;
        long bound = 2;
        for (long c = 16; c < n; c *= 2) ++bound;
        CHECK("size", s.size() == static_cast<std::size_t>(n));
        CHECK("logarithmic reallocations", reallocs <= bound);
        CHECK("terminated", s.c_str()[n] == '\0' && std::strlen(s.c_str()) == static_cast<std::size_t>(n));
    } else if (cmd == "sort") {
        int n; std::cin >> n;
        std::vector<SString> v;
        v.reserve(static_cast<std::size_t>(n));
        for (int i = 0; i < n; ++i) { std::string w; std::cin >> w; v.emplace_back(w.c_str()); }
        long a0 = g_allocs;
        std::sort(v.begin(), v.end());
        CHECK("sorting moves only (no allocations)", g_allocs == a0);
        for (const auto& s : v) std::cout << s << '\n';
    }
    std::cout << "leaked allocations: " << (g_allocs - g_frees) << '\n';   // all strings above are out of scope
}
```

## Tests
=== sample
basics
---
small no alloc: ok
capacity 15: ok
long allocates once: ok
copy small: 0 allocs, copy long: 1: ok
moves never allocate: ok
moved values: ok
self-assignment: ok
assign long into small and small into long: ok
Robot 5 1011
abcdef 1 6
leaked allocations: 0
=== hidden
grow 1
---
size: ok
logarithmic reallocations: ok
terminated: ok
leaked allocations: 0
=== hidden
grow 100000
---
size: ok
logarithmic reallocations: ok
terminated: ok
leaked allocations: 0
=== hidden
sort 8
pear apple zebra-crossing-is-long Apple banana a-very-long-word-indeed apple fig
---
sorting moves only (no allocations): ok
Apple
a-very-long-word-indeed
apple
apple
banana
fig
pear
zebra-crossing-is-long
leaked allocations: 0
=== hidden
grow 15
---
size: ok
logarithmic reallocations: ok
terminated: ok
leaked allocations: 0

## Hints
- Store `std::size_t size_`, `std::size_t cap_` and `union { char small_[16]; char* heap_; }`. `is_small()` is `cap_ == 15`. Write `char* data()` returning `is_small() ? small_ : heap_` and use it everywhere.
- Move construction from a long string: copy `heap_`, `size_` and `cap_`, then reset the source to an empty small string. From a small string: `memcpy` the 16 bytes. Neither allocates.
- Copy assignment with the strong guarantee: copy-and-swap. But a `swap` built from moves is cheaper than swapping via copies, and `std::swap` uses your move operations.
- `+=`: if `size_ + r.size_ > cap_`, allocate `max(2 * cap_, needed)` + 1 bytes, copy, free the old heap buffer (if any), and switch to long mode. Careful with `s += s`, where `r` aliases `*this`: read `r`'s data before freeing.
- The driver's last line counts allocations still alive after every string has gone out of scope. It must be 0, so check the moved-from and temporary paths (`operator+`) too.

## Solution
```cpp
#include <cstring>
#include <cstddef>
#include <compare>
#include <ostream>
#include <utility>
#include <algorithm>

class SString {
public:
    static constexpr std::size_t kSmall = 15;

    SString() noexcept { small_[0] = '\0'; }
    SString(const char* s) { init(s, std::strlen(s)); }
    SString(const SString& o) { init(o.data(), o.size_); }
    SString(SString&& o) noexcept { steal(o); }
    SString& operator=(const SString& o) {
        if (this != &o) { SString tmp(o); swap(tmp); }   // copy may throw; swap never does
        return *this;
    }
    SString& operator=(SString&& o) noexcept {
        if (this != &o) { release(); steal(o); }
        return *this;
    }
    ~SString() { release(); }

    std::size_t size() const noexcept { return size_; }
    std::size_t capacity() const noexcept { return cap_; }
    bool is_small() const noexcept { return cap_ == kSmall; }
    const char* c_str() const noexcept { return data(); }
    char& operator[](std::size_t i) { return data()[i]; }
    const char& operator[](std::size_t i) const { return data()[i]; }

    SString& operator+=(const SString& r) {
        std::size_t rlen = r.size_;                    // read before any reallocation (r may be *this)
        std::size_t need = size_ + rlen;
        if (need > cap_) {
            std::size_t ncap = std::max(need, 2 * cap_);
            char* buf = new char[ncap + 1];
            std::memcpy(buf, data(), size_);
            std::memcpy(buf + size_, r.data(), rlen);  // r's buffer is still alive here
            release();
            heap_ = buf;
            cap_ = ncap;
        } else {
            std::memmove(data() + size_, r.data(), rlen);
        }
        size_ = need;
        data()[size_] = '\0';
        return *this;
    }
    friend SString operator+(SString lhs, const SString& rhs) { lhs += rhs; return lhs; }
    friend bool operator==(const SString& a, const SString& b) {
        return a.size_ == b.size_ && std::memcmp(a.data(), b.data(), a.size_) == 0;
    }
    friend std::strong_ordering operator<=>(const SString& a, const SString& b) {
        int c = std::memcmp(a.data(), b.data(), std::min(a.size_, b.size_));
        if (c != 0) return c <=> 0;
        return a.size_ <=> b.size_;
    }
    friend std::ostream& operator<<(std::ostream& os, const SString& s) { return os.write(s.data(), static_cast<std::streamsize>(s.size_)); }

    void swap(SString& o) noexcept { SString t(std::move(o)); o = std::move(*this); *this = std::move(t); }

private:
    char* data() noexcept { return is_small() ? small_ : heap_; }
    const char* data() const noexcept { return is_small() ? small_ : heap_; }

    void init(const char* s, std::size_t n) {
        size_ = n;
        if (n <= kSmall) {
            cap_ = kSmall;
            std::memcpy(small_, s, n);
            small_[n] = '\0';
        } else {
            heap_ = new char[n + 1];
            cap_ = n;
            std::memcpy(heap_, s, n);
            heap_[n] = '\0';
        }
    }
    void steal(SString& o) noexcept {
        size_ = o.size_;
        cap_ = o.cap_;
        if (o.is_small()) std::memcpy(small_, o.small_, sizeof small_);
        else heap_ = o.heap_;
        o.size_ = 0;                                   // leave the source as a valid empty small string
        o.cap_ = kSmall;
        o.small_[0] = '\0';
    }
    void release() noexcept {
        if (!is_small()) delete[] heap_;
        cap_ = kSmall;
        size_ = 0;
        small_[0] = '\0';
    }

    std::size_t size_ = 0;
    std::size_t cap_ = kSmall;
    union {
        char small_[kSmall + 1];
        char* heap_;
    };
};
```

**What makes it work:**
- **The union** overlays the inline buffer and the heap pointer. `cap_ == 15` is the discriminator for which member is active. The object is 32 bytes, and short strings (most identifiers, keys and labels in real programs) never touch the allocator.
- **Moves are `noexcept`** and never allocate. That's why `std::sort` and `std::vector` reallocation can use them (the driver checks both). Without `noexcept`, `vector` would *copy* during reallocation to keep its strong guarantee.
- **The moved-from state is a valid empty string**, so it can be destroyed or reassigned safely.
- **Copy assignment** builds the copy first, then swaps: if `new` throws, `*this` is untouched (the strong guarantee), and self-assignment is harmless.
- **Geometric growth** in `+=` makes n appends cost O(n) total with O(log n) allocations. The aliasing case `s += s` works because the new buffer is filled before the old one is released.
- **`<=>`** compares with `memcmp` on the common prefix, then by length: exactly `std::string`'s lexicographic order.
