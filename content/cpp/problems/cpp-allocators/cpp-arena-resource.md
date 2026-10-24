---
id: cpp-arena-resource
title: A Fixed-Buffer Arena memory_resource for PMR Containers
difficulty: Hard
order: 1
tags: std::pmr, memory_resource, arena, alignment, real-time, no heap
---
## Statement
A 1 kHz controller must never touch the heap inside its control loop. Implement a **bump-pointer arena** as a `std::pmr::memory_resource`, so the standard `std::pmr` containers can run entirely inside a pre-allocated buffer.

```cpp
class FixedArena : public std::pmr::memory_resource {
public:
    FixedArena(void* buffer, std::size_t size) noexcept;
    std::size_t used() const noexcept;          // bytes from buffer start to the bump pointer
    std::size_t peak() const noexcept;          // maximum used() ever reached (release() keeps it)
    std::size_t allocations() const noexcept;   // successful allocations so far
    void release() noexcept;                    // reset the bump pointer to the start
private:
    void* do_allocate(std::size_t bytes, std::size_t alignment) override;
    void do_deallocate(void* p, std::size_t bytes, std::size_t alignment) override;
    bool do_is_equal(const std::pmr::memory_resource& other) const noexcept override;
};
```

The rules:
- **Allocate**: round the bump pointer up to `alignment` (a power of two), hand out `bytes` (a request for 0 bytes counts as 1), and advance. If the block doesn't fit, throw `std::bad_alloc` and leave the state unchanged. **Never** fall back to the heap.
- **Deallocate**: a no-op, *except* when the block is the most recent one (it ends exactly at the bump pointer). Then roll the bump pointer back to the block's start (the LIFO optimisation). Padding inserted before that block stays used.
- **Equality**: two resources are equal only if they are the same object.

The hidden driver replaces global `operator new` to count heap allocations, and expects zero while `std::pmr::vector` and `std::pmr::string` run on your arena. It uses a 64-byte-aligned buffer and prints offsets relative to it.

## Starter
```cpp
#include <memory_resource>
#include <cstddef>
#include <new>

class FixedArena : public std::pmr::memory_resource {
public:
    FixedArena(void* buffer, std::size_t size) noexcept : buf_(static_cast<std::byte*>(buffer)), size_(size) {}
    std::size_t used() const noexcept { return used_; }
    std::size_t peak() const noexcept { return used_; }
    std::size_t allocations() const noexcept { return count_; }
    void release() noexcept { used_ = 0; }
private:
    void* do_allocate(std::size_t bytes, std::size_t) override {
        void* p = buf_ + used_;
        used_ += bytes;
        ++count_;
        return p;
    }
    void do_deallocate(void*, std::size_t, std::size_t) override {}
    bool do_is_equal(const std::pmr::memory_resource&) const noexcept override { return true; }
    std::byte* buf_;
    std::size_t size_, used_ = 0, count_ = 0;
};
```

## Driver
```cpp
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <map>
#include <string>
#include <vector>

static std::size_t g_heap = 0;
static bool g_watch = false;
void* operator new(std::size_t n) {
    if (g_watch) ++g_heap;
    if (void* p = std::malloc(n ? n : 1)) return p;
    throw std::bad_alloc{};
}
void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }

alignas(64) static std::byte buffer[1 << 16];

int main() {
    std::string cmd;
    std::size_t cap = 0;
    std::cin >> cap;
    FixedArena arena(buffer, cap);
    std::map<std::string, std::pair<void*, std::pair<std::size_t, std::size_t>>> blocks;
    while (std::cin >> cmd) {
        if (cmd == "alloc") {
            std::string id; std::size_t n, a; std::cin >> id >> n >> a;
            std::pmr::memory_resource& r = arena;
            try {
                void* p = r.allocate(n, a);
                blocks[id] = {p, {n, a}};
                std::printf("alloc %s %zu/%zu -> offset %td (used %zu)\n", id.c_str(), n, a,
                            static_cast<std::byte*>(p) - buffer, arena.used());
            } catch (const std::bad_alloc&) {
                std::printf("alloc %s %zu/%zu -> bad_alloc (used %zu)\n", id.c_str(), n, a, arena.used());
            }
        } else if (cmd == "free") {
            std::string id; std::cin >> id;
            auto& b = blocks.at(id);
            std::pmr::memory_resource& r = arena;
            r.deallocate(b.first, b.second.first, b.second.second);
            std::printf("free %s -> used %zu\n", id.c_str(), arena.used());
        } else if (cmd == "stats") {
            std::printf("stats: used=%zu peak=%zu allocations=%zu\n", arena.used(), arena.peak(), arena.allocations());
        } else if (cmd == "release") {
            arena.release();
            std::printf("release -> used %zu\n", arena.used());
        } else if (cmd == "equal") {
            FixedArena other(buffer, cap);
            std::pmr::memory_resource& r = arena;
            std::printf("equal: self=%d other=%d heap_resource=%d\n", r.is_equal(arena), r.is_equal(other),
                        r.is_equal(*std::pmr::new_delete_resource()));
        } else if (cmd == "pmr") {
            int n; std::cin >> n;
            arena.release();
            g_heap = 0; g_watch = true;
            std::size_t total = 0;
            {
                std::pmr::vector<std::pmr::string> topics{&arena};
                char name[96];
                for (int i = 0; i < n; ++i) {
                    std::snprintf(name, sizeof name, "/robot/sensor/%d/a_fairly_long_suffix_beyond_sso", i);
                    topics.emplace_back(name);              // the string's characters come from the arena too
                }
                for (auto& t : topics) total += t.size();
                std::pmr::vector<int> scratch{&arena};
                scratch.assign(1000, 7);
                total += scratch.size();
            }
            g_watch = false;
            std::printf("pmr %d: chars+ints=%zu heap_allocations=%zu arena_used_by_containers=%d\n",
                        n, total, g_heap, arena.allocations() > 0);
        } else if (cmd == "overflow") {
            arena.release();
            std::size_t before = arena.allocations();
            g_heap = 0; g_watch = true;
            bool threw = false;
            try {
                std::pmr::vector<double> v{&arena};
                for (int i = 0; i < 100000; ++i) v.push_back(i);
            } catch (const std::bad_alloc&) { threw = true; }
            g_watch = false;
            std::printf("overflow: threw_bad_alloc=%d heap_allocations=%zu grew=%d\n", threw, g_heap,
                        arena.allocations() > before);
        }
    }
}
```

## Tests
=== sample
256
alloc a 10 1
alloc b 8 8
stats
free b
free a
alloc c 1 64
stats
---
alloc a 10/1 -> offset 0 (used 10)
alloc b 8/8 -> offset 16 (used 24)
stats: used=24 peak=24 allocations=2
free b -> used 16
free a -> used 16
alloc c 1/64 -> offset 64 (used 65)
stats: used=65 peak=65 allocations=3
=== hidden
128
alloc a 0 1
alloc b 0 1
alloc c 100 16
alloc d 20 8
alloc e 12 4
stats
free e
free c
free b
stats
release
stats
equal
---
alloc a 0/1 -> offset 0 (used 1)
alloc b 0/1 -> offset 1 (used 2)
alloc c 100/16 -> offset 16 (used 116)
alloc d 20/8 -> bad_alloc (used 116)
alloc e 12/4 -> offset 116 (used 128)
stats: used=128 peak=128 allocations=4
free e -> used 116
free c -> used 16
free b -> used 16
stats: used=16 peak=128 allocations=4
release -> used 0
stats: used=0 peak=128 allocations=4
equal: self=1 other=0 heap_resource=0
=== hidden
64
alloc x 64 64
alloc y 1 1
free x
alloc z 3 2
alloc w 1 32
alloc v 31 1
alloc u 1 1
stats
---
alloc x 64/64 -> offset 0 (used 64)
alloc y 1/1 -> bad_alloc (used 64)
free x -> used 0
alloc z 3/2 -> offset 0 (used 3)
alloc w 1/32 -> offset 32 (used 33)
alloc v 31/1 -> offset 33 (used 64)
alloc u 1/1 -> bad_alloc (used 64)
stats: used=64 peak=64 allocations=4
=== hidden
65536
pmr 200
overflow
stats
---
pmr 200: chars+ints=10690 heap_allocations=0 arena_used_by_containers=1
overflow: threw_bad_alloc=1 heap_allocations=0 grew=1
stats: used=32760 peak=65528 allocations=223

## Hints
- Store `std::byte* begin_, *cur_, *end_`, and compute the aligned address as `(uintptr_t(cur_) + a - 1) & ~uintptr_t(a - 1)`. Check `aligned + bytes <= end_` **before** changing any state.
- In `do_deallocate`: `if (static_cast<std::byte*>(p) + bytes == cur_) cur_ = static_cast<std::byte*>(p);`, with bytes == 0 treated as 1, as in allocate.
- `peak_ = std::max(peak_, used())` after each successful allocation.
- `do_is_equal`: `return this == &other;`.

## Solution
```cpp
#include <memory_resource>
#include <cstddef>
#include <cstdint>
#include <new>
#include <algorithm>

class FixedArena : public std::pmr::memory_resource {
public:
    FixedArena(void* buffer, std::size_t size) noexcept
        : begin_(static_cast<std::byte*>(buffer)), cur_(begin_), end_(begin_ + size) {}

    std::size_t used() const noexcept { return std::size_t(cur_ - begin_); }
    std::size_t peak() const noexcept { return peak_; }
    std::size_t allocations() const noexcept { return count_; }
    void release() noexcept { cur_ = begin_; }

private:
    void* do_allocate(std::size_t bytes, std::size_t alignment) override {
        if (bytes == 0) bytes = 1;
        auto cur = reinterpret_cast<std::uintptr_t>(cur_);
        auto aligned = (cur + alignment - 1) & ~std::uintptr_t(alignment - 1);
        auto end = reinterpret_cast<std::uintptr_t>(end_);
        if (aligned < cur || aligned > end || bytes > end - aligned) throw std::bad_alloc{};   // no state change
        cur_ = reinterpret_cast<std::byte*>(aligned + bytes);
        ++count_;
        peak_ = std::max(peak_, used());
        return reinterpret_cast<void*>(aligned);
    }

    void do_deallocate(void* p, std::size_t bytes, std::size_t) override {
        if (bytes == 0) bytes = 1;
        auto* b = static_cast<std::byte*>(p);
        if (b + bytes == cur_) cur_ = b;            // LIFO: undo the most recent allocation
    }

    bool do_is_equal(const std::pmr::memory_resource& other) const noexcept override {
        return this == &other;
    }

    std::byte* begin_;
    std::byte* cur_;
    std::byte* end_;
    std::size_t peak_ = 0, count_ = 0;
};
```

A `memory_resource` is a three-function interface, and the containers handle the rest through `polymorphic_allocator`.
- **Allocation** is a rounded-up pointer bump. The overflow check uses subtraction (`bytes > end - aligned`) rather than `aligned + bytes > end`, so a huge request can't wrap around and slip through. The state changes only after the check passes, which gives the strong exception guarantee.
- **The LIFO rollback** makes stack-like use patterns (temporary buffers, a vector growing by reallocate-copy-free) reuse memory immediately. Otherwise, a monotonic arena only reclaims memory on `release()`.
- **Composition**: because the arena never calls upstream, exhausting it throws (the `overflow` test) instead of quietly allocating. That's what makes heap-free guarantees verifiable in testing.
- **Identity equality** matters: containers compare resources to decide whether they can steal each other's memory on move. Two different arenas must never be considered interchangeable.
