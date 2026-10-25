---
id: cpp-shared-weak-ptr
title: Implement shared_ptr and weak_ptr
difficulty: Expert
order: 1
tags: interview, smart pointers, control block, atomics, memory ordering, weak references, RAII
time_limit: 6
---
## Statement
Implement reference-counted ownership the way the standard library does, with a **control block** holding atomic strong and weak counts.

**`template <class T> class SharedPtr`**
- `SharedPtr()`, `SharedPtr(std::nullptr_t)`, and `explicit SharedPtr(T* p)`: takes ownership. A null `p` creates no control block.
- Copy and move constructors and assignments. Moves are `noexcept` and leave the source empty. Self-assignment must be safe.
- `~SharedPtr()` releases its share.
- `reset()`, `reset(T* p)`, `T* get() const`, `T& operator*() const`, `T* operator->() const`, `long use_count() const` (0 when empty), `explicit operator bool() const`.

**`template <class T> class WeakPtr`**
- Default constructor, construction and assignment from a `SharedPtr<T>`, copy and move.
- `bool expired() const`, `long use_count() const`, `SharedPtr<T> lock() const`: an empty pointer if expired, **atomically** (no race between the check and the increment).

**`template <class T, class... A> SharedPtr<T> make_shared_ptr(A&&... args)`** constructs a `T` and returns the owning pointer.

**Lifetime rules**
- The object is destroyed (exactly once) when the last `SharedPtr` lets go.
- The control block is freed when **both** the strong and the weak counts reach zero. Weak pointers that outlive the object must still work: they report `expired() == true`.

**Threading:** copies and destructions of different `SharedPtr` objects that share one control block may happen concurrently from many threads, and `lock()` may race with the last owner's release. The judge hammers this with 8 threads. Use `std::atomic` with appropriate memory ordering.

## Starter
```cpp
#include <atomic>
#include <cstddef>
#include <utility>

template <class T>
class SharedPtr {
public:
    SharedPtr() = default;
    SharedPtr(std::nullptr_t) {}
    explicit SharedPtr(T* p) : p_(p), count_(new long(1)) {}
    SharedPtr(const SharedPtr& o) : p_(o.p_), count_(o.count_) { if (count_) ++*count_; }
    ~SharedPtr() { if (count_ && --*count_ == 0) { delete p_; delete count_; } }
    SharedPtr& operator=(const SharedPtr& o) { p_ = o.p_; count_ = o.count_; if (count_) ++*count_; return *this; }
    T* get() const { return p_; }
    T& operator*() const { return *p_; }
    T* operator->() const { return p_; }
    long use_count() const { return count_ ? *count_ : 0; }
    explicit operator bool() const { return p_ != nullptr; }
    void reset() { *this = SharedPtr(); }
    void reset(T* p) { *this = SharedPtr(p); }
private:
    T* p_ = nullptr;
    long* count_ = nullptr;
};

template <class T>
class WeakPtr {
public:
    WeakPtr() = default;
    WeakPtr(const SharedPtr<T>& s) : s_(s) {}
    bool expired() const { return false; }
    long use_count() const { return s_.use_count(); }
    SharedPtr<T> lock() const { return s_; }
private:
    SharedPtr<T> s_;
};

template <class T, class... A>
SharedPtr<T> make_shared_ptr(A&&... args) { return SharedPtr<T>(new T(std::forward<A>(args)...)); }
```

## Driver
```cpp
#include <cstdio>
#include <iostream>
#include <string>
#include <thread>
#include <vector>

std::atomic<long> live{0}, destroyed{0};
struct Robot {
    std::string name;
    explicit Robot(std::string n) : name(std::move(n)) { ++live; }
    ~Robot() { --live; ++destroyed; }
};
struct Node { int v; SharedPtr<Node> next; WeakPtr<Node> prev; explicit Node(int x) : v(x) { ++live; } ~Node() { --live; } };

int main() {
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "basic") {
            SharedPtr<Robot> a(new Robot("r1"));
            std::printf("a use=%ld name=%s\n", a.use_count(), a->name.c_str());
            {
                SharedPtr<Robot> b = a, c; c = b;
                std::printf("shared use=%ld same=%d\n", a.use_count(), b.get() == c.get());
                c = c; std::printf("self-assign use=%ld\n", a.use_count());
                SharedPtr<Robot> d = std::move(c);
                std::printf("moved: c empty=%d use=%ld d=%s\n", !c, a.use_count(), (*d).name.c_str());
            }
            std::printf("after scope use=%ld live=%ld\n", a.use_count(), live.load());
            a.reset(new Robot("r2")); std::printf("reset to %s live=%ld destroyed=%ld\n", a->name.c_str(), live.load(), destroyed.load());
            a.reset(); std::printf("empty=%d use=%ld live=%ld\n", !a, a.use_count(), live.load());
            SharedPtr<Robot> n(nullptr), m(static_cast<Robot*>(nullptr));
            std::printf("null use=%ld %ld\n", n.use_count(), m.use_count());
            auto e = make_shared_ptr<Robot>("made"); SharedPtr<Robot> f = e; e = std::move(f);
            std::printf("make_shared use=%ld f empty=%d\n", e.use_count(), !f);
        } else if (cmd == "weak") {
            WeakPtr<Robot> w;
            std::printf("default expired=%d use=%ld locked=%d\n", w.expired(), w.use_count(), (bool)w.lock());
            {
                auto s = make_shared_ptr<Robot>("scout");
                w = s; WeakPtr<Robot> w2 = w;
                std::printf("expired=%d use=%ld\n", w.expired(), w.use_count());
                if (auto l = w2.lock()) std::printf("locked %s use=%ld\n", l->name.c_str(), s.use_count());
                std::printf("after lock use=%ld\n", s.use_count());
            }
            std::printf("owner gone: expired=%d use=%ld locked=%d live=%ld\n", w.expired(), w.use_count(), (bool)w.lock(), live.load());
            WeakPtr<Robot> w3 = std::move(w); std::printf("moved weak expired=%d\n", w3.expired());
        } else if (cmd == "cycle") {
            {
                auto a = make_shared_ptr<Node>(1), b = make_shared_ptr<Node>(2);
                a->next = b; b->prev = a;            // forward strong, back weak: no cycle
                std::printf("a use=%ld b use=%ld prev=%d\n", a.use_count(), b.use_count(), b->prev.lock()->v);
            }
            std::printf("live after chain=%ld\n", live.load());
            {
                auto head = make_shared_ptr<Node>(0); SharedPtr<Node> cur = head;
                for (int i = 1; i < 1000; ++i) { auto n = make_shared_ptr<Node>(i); n->prev = cur; cur->next = n; cur = n; }
                long sum = 0; for (SharedPtr<Node> p = head; p; p = p->next) sum += p->v;
                std::printf("list sum=%ld live=%ld tail prev=%d\n", sum, live.load(), cur->prev.lock()->v);
                cur = SharedPtr<Node>();
                head->next->next = SharedPtr<Node>();
                std::printf("cut: live=%ld\n", live.load());
            }
            std::printf("live=%ld\n", live.load());
        } else if (cmd == "threads") {
            destroyed = 0;
            for (int round = 0; round < 20; ++round) {
                auto shared = make_shared_ptr<Robot>("hot");
                WeakPtr<Robot> watcher = shared;
                std::atomic<long> locks{0};
                std::vector<std::thread> ts;
                for (int t = 0; t < 8; ++t) {
                    ts.emplace_back([copy = shared, &watcher, &locks, t]() mutable {
                        std::vector<SharedPtr<Robot>> mine;
                        for (int i = 0; i < 20000; ++i) {
                            mine.push_back(copy);
                            if (mine.size() > 16) mine.erase(mine.begin());
                            if ((i & 63) == t) { WeakPtr<Robot> w = copy; if (w.lock()) ++locks; }
                        }
                        copy.reset();
                        for (int i = 0; i < 2000; ++i) if (auto l = watcher.lock()) { ++locks; (void)l->name.size(); }
                    });
                }
                shared.reset();
                for (auto& th : ts) th.join();
                if (!watcher.expired() || live.load() != 0) { std::printf("round %d broken\n", round); break; }
            }
            std::printf("threads ok: destroyed=%ld live=%ld\n", destroyed.load(), live.load());
        }
    }
}
```

## Tests
=== sample
basic
weak
---
a use=1 name=r1
shared use=3 same=1
self-assign use=3
moved: c empty=1 use=3 d=r1
after scope use=1 live=1
reset to r2 live=1 destroyed=1
empty=1 use=0 live=0
null use=0 0
make_shared use=1 f empty=1
default expired=1 use=0 locked=0
expired=0 use=1
locked scout use=2
after lock use=1
owner gone: expired=1 use=0 locked=0 live=0
moved weak expired=1
=== hidden
cycle
---
a use=2 b use=2 prev=1
live after chain=0
list sum=499500 live=1000 tail prev=998
cut: live=2
live=0
=== hidden
threads
---
threads ok: destroyed=20 live=0

## Hints
- Control block: `struct Ctrl { std::atomic<long> strong{1}, weak{1}; T* ptr; }`. The weak count includes **+1 while any strong owner exists**, so the block dies exactly when the last weak reference (counting that +1) goes. This is libstdc++'s trick.
- Release a strong reference with `fetch_sub(1, std::memory_order_acq_rel)`. If it was 1: `delete ptr`, then release that implicit weak reference. Increments can be `relaxed`.
- `lock()`: a compare-exchange loop that increments `strong` **only if it's non-zero**. Never `load()` and then `fetch_add()` separately.
- Assignment: copy-and-swap (`SharedPtr(o).swap(*this)`) makes self-assignment and exception safety automatic.

## Solution
```cpp
#include <atomic>
#include <cstddef>
#include <utility>

namespace detail {
template <class T>
struct Ctrl {
    explicit Ctrl(T* p) : ptr(p) {}
    std::atomic<long> strong{1};
    std::atomic<long> weak{1};        // +1 held collectively by all strong owners
    T* ptr;

    void add_strong() noexcept { strong.fetch_add(1, std::memory_order_relaxed); }
    void add_weak() noexcept { weak.fetch_add(1, std::memory_order_relaxed); }
    void release_weak() noexcept {
        if (weak.fetch_sub(1, std::memory_order_acq_rel) == 1) delete this;
    }
    void release_strong() noexcept {
        if (strong.fetch_sub(1, std::memory_order_acq_rel) == 1) {
            delete ptr;                // last owner: destroy the object
            ptr = nullptr;
            release_weak();            // drop the owners' collective weak reference
        }
    }
    bool try_add_strong() noexcept {   // lock(): increment only if not already zero
        long n = strong.load(std::memory_order_relaxed);
        while (n != 0)
            if (strong.compare_exchange_weak(n, n + 1, std::memory_order_acq_rel, std::memory_order_relaxed)) return true;
        return false;
    }
};
}  // namespace detail

template <class T> class WeakPtr;

template <class T>
class SharedPtr {
public:
    SharedPtr() noexcept = default;
    SharedPtr(std::nullptr_t) noexcept {}
    explicit SharedPtr(T* p) : c_(p ? new detail::Ctrl<T>(p) : nullptr) {}
    SharedPtr(const SharedPtr& o) noexcept : c_(o.c_) { if (c_) c_->add_strong(); }
    SharedPtr(SharedPtr&& o) noexcept : c_(std::exchange(o.c_, nullptr)) {}
    ~SharedPtr() { if (c_) c_->release_strong(); }

    SharedPtr& operator=(const SharedPtr& o) noexcept { SharedPtr(o).swap(*this); return *this; }
    SharedPtr& operator=(SharedPtr&& o) noexcept { SharedPtr(std::move(o)).swap(*this); return *this; }
    void swap(SharedPtr& o) noexcept { std::swap(c_, o.c_); }

    void reset() noexcept { SharedPtr().swap(*this); }
    void reset(T* p) { SharedPtr(p).swap(*this); }
    T* get() const noexcept { return c_ ? c_->ptr : nullptr; }
    T& operator*() const noexcept { return *get(); }
    T* operator->() const noexcept { return get(); }
    long use_count() const noexcept { return c_ ? c_->strong.load(std::memory_order_relaxed) : 0; }
    explicit operator bool() const noexcept { return get() != nullptr; }

private:
    friend class WeakPtr<T>;
    explicit SharedPtr(detail::Ctrl<T>* c) noexcept : c_(c) {}   // adopts an already-incremented count
    detail::Ctrl<T>* c_ = nullptr;
};

template <class T>
class WeakPtr {
public:
    WeakPtr() noexcept = default;
    WeakPtr(const SharedPtr<T>& s) noexcept : c_(s.c_) { if (c_) c_->add_weak(); }
    WeakPtr(const WeakPtr& o) noexcept : c_(o.c_) { if (c_) c_->add_weak(); }
    WeakPtr(WeakPtr&& o) noexcept : c_(std::exchange(o.c_, nullptr)) {}
    ~WeakPtr() { if (c_) c_->release_weak(); }
    WeakPtr& operator=(const WeakPtr& o) noexcept { WeakPtr(o).swap(*this); return *this; }
    WeakPtr& operator=(WeakPtr&& o) noexcept { WeakPtr(std::move(o)).swap(*this); return *this; }
    WeakPtr& operator=(const SharedPtr<T>& s) noexcept { WeakPtr(s).swap(*this); return *this; }
    void swap(WeakPtr& o) noexcept { std::swap(c_, o.c_); }

    long use_count() const noexcept { return c_ ? c_->strong.load(std::memory_order_relaxed) : 0; }
    bool expired() const noexcept { return use_count() == 0; }
    SharedPtr<T> lock() const noexcept {
        return (c_ && c_->try_add_strong()) ? SharedPtr<T>(c_) : SharedPtr<T>();
    }

private:
    detail::Ctrl<T>* c_ = nullptr;
};

template <class T, class... A>
SharedPtr<T> make_shared_ptr(A&&... args) {
    return SharedPtr<T>(new T(std::forward<A>(args)...));
}
```

- **Two counts, one block**: the strong count controls the object's lifetime, and the weak count controls the control block's lifetime. Weak pointers must be able to ask "is it still alive?" after the object is gone, so the block outlives the object.
- **The "+1 weak" trick**: all strong owners together hold a single weak reference. The block is freed exactly once, by whoever drops the weak count to zero, with no separate "both are zero" check that could race.
- **Memory ordering**: increments only need `relaxed`, because you already hold a reference, so the object can't die. Decrements use `acq_rel`. The release half publishes this thread's writes to the object, and the acquire half makes the deleting thread see every other thread's writes before running the destructor.
- **`lock()` uses a CAS loop**: "check non-zero, then increment" as two steps would resurrect an object whose destructor is already running. The compare-exchange makes the test and the increment one atomic step.
- **Copy-and-swap assignment** handles self-assignment and ordering for free: the old reference is released only after the new one is acquired.
- `std::make_shared` additionally co-allocates the object and the control block in one allocation, saving a heap allocation and improving locality. That's why it's preferred over `shared_ptr<T>(new T)`.
