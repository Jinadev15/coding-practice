# Custom Allocators and PMR

General-purpose heap allocation (`new`, `malloc`) is flexible but slow and unpredictable. It takes tens of nanoseconds, may lock, fragments memory over long runs, and has unbounded worst-case latency. That's unacceptable inside a 1 kHz robot control loop or a game frame. C++ lets you plug your own memory strategy into the standard containers in two ways: the classic **allocator template parameter**, and C++17's **polymorphic memory resources (PMR)**. This lesson builds both and the arena and pool strategies behind them.

## 1. Why customise allocation?

| Problem | Custom strategy |
|---|---|
| many small, same-size objects (graph nodes, particles) | **pool** / free-list allocator |
| many objects freed together (per frame, per request, per parse) | **arena** (monotonic / bump) allocator |
| no heap allowed after start-up (hard real-time, MISRA/AUTOSAR) | pre-allocated buffers + arena |
| allocation hot spots in profiles | pools or arenas, fewer allocations |
| memory accounting / leak tracking per subsystem | counting/tracking resource |
| shared memory, GPU memory, NUMA-local memory | allocators returning special memory |

## 2. Arena (bump) allocation, the core idea

```cpp
class Arena {
public:
    Arena(std::byte* buf, std::size_t size) : begin_(buf), cur_(buf), end_(buf + size) {}

    void* allocate(std::size_t n, std::size_t align) {
        auto p = reinterpret_cast<std::uintptr_t>(cur_);
        auto aligned = (p + align - 1) & ~(std::uintptr_t(align) - 1);   // round up (align is a power of 2)
        if (aligned + n > reinterpret_cast<std::uintptr_t>(end_)) throw std::bad_alloc{};
        cur_ = reinterpret_cast<std::byte*>(aligned + n);
        return reinterpret_cast<void*>(aligned);
    }
    void reset() noexcept { cur_ = begin_; }        // "free" everything at once: O(1)

private:
    std::byte *begin_, *cur_, *end_;
};
```

Allocation is a pointer bump: a couple of instructions, no locks, no fragmentation, and perfect locality (objects allocated together sit together). Individual deallocation is a no-op, and memory is reclaimed all at once with `reset()`.

> [!WARNING]
> `reset()` releases memory, but it doesn't run destructors. Objects in an arena must either be trivially destructible or be destroyed explicitly before the reset, or resources they own (file handles, heap buffers outside the arena) leak.

## 3. Pool (free-list) allocation

For fixed-size blocks, keep the free blocks in a singly linked list threaded **through the free blocks themselves**:

```cpp
template <std::size_t BlockSize, std::size_t Count>
class Pool {
    static_assert(BlockSize >= sizeof(void*));
    struct Node { Node* next; };
    alignas(std::max_align_t) std::byte storage_[BlockSize * Count];
    Node* free_ = nullptr;
public:
    Pool() {
        for (std::size_t i = Count; i-- > 0;) {                     // build the list
            auto* n = reinterpret_cast<Node*>(storage_ + i * BlockSize);
            n->next = free_;
            free_ = n;
        }
    }
    void* allocate() {
        if (!free_) throw std::bad_alloc{};
        Node* n = free_;
        free_ = n->next;
        return n;
    }
    void deallocate(void* p) noexcept {
        auto* n = static_cast<Node*>(p);
        n->next = free_;
        free_ = n;
    }
};
```

Both operations are O(1) with a bounded worst case, which is exactly what real-time code needs. (`BlockSize` should be a multiple of the required alignment.)

## 4. The classic allocator model (C++11 and later)

A standard allocator is a small class that containers use through `std::allocator_traits`. The minimal C++11 allocator needs only this:

```cpp
template <class T>
struct CountingAlloc {
    using value_type = T;
    static inline std::size_t live_bytes = 0;

    CountingAlloc() = default;
    template <class U> CountingAlloc(const CountingAlloc<U>&) noexcept {}   // rebind conversion

    T* allocate(std::size_t n) {
        live_bytes += n * sizeof(T);
        return static_cast<T*>(::operator new(n * sizeof(T)));
    }
    void deallocate(T* p, std::size_t n) noexcept {
        live_bytes -= n * sizeof(T);
        ::operator delete(p);
    }
    template <class U> bool operator==(const CountingAlloc<U>&) const noexcept { return true; }
};

std::vector<int, CountingAlloc<int>> v(1000);
std::map<int, int, std::less<>, CountingAlloc<std::pair<const int, int>>> m;   // allocates NODES via rebind
```

Key points:
- **Rebinding**: a `std::list<T, A>` doesn't allocate `T`s. It allocates nodes. `allocator_traits<A>::rebind_alloc<Node>` produces the node allocator, which is why the converting constructor is required.
- **The allocator is part of the type**: `vector<int, A1>` and `vector<int, A2>` are different, incompatible types. That's the big ergonomic problem with this model.
- **Stateful allocators** (holding a pointer to an arena) need `operator==` to compare that state, plus the propagation traits `propagate_on_container_copy_assignment`, `..._move_assignment` and `..._swap`.

## 5. PMR: runtime-polymorphic allocation (C++17)

`std::pmr` separates **what** allocates (a `memory_resource` object with virtual `do_allocate`) from **the container type** (always `std::pmr::polymorphic_allocator<T>`). Containers using different resources therefore have the *same* type.

```cpp
#include <memory_resource>

std::array<std::byte, 64 * 1024> buffer;
std::pmr::monotonic_buffer_resource arena{buffer.data(), buffer.size(),
                                          std::pmr::null_memory_resource()};  // throw instead of falling back to the heap

std::pmr::vector<std::pmr::string> names{&arena};
names.emplace_back("lidar_front_left_long_name");   // the vector AND the string chars come from the arena
```

> [!KEY]
> **Allocator propagation**: a `pmr::vector<pmr::string>` passes its resource to the elements it constructs (uses-allocator construction). The strings' heap buffers come from the same arena, so the whole data structure lives in one buffer. With the classic model, you'd have to wire that by hand.

Standard resources:

| Resource | Behaviour |
|---|---|
| `new_delete_resource()` | the global heap (the default) |
| `null_memory_resource()` | always throws `bad_alloc`: use it as upstream to *guarantee* no heap use |
| `monotonic_buffer_resource` | arena: bump allocation, `deallocate` is a no-op, `release()` frees all |
| `unsynchronized_pool_resource` | pools of size classes, single-threaded |
| `synchronized_pool_resource` | the thread-safe version |

### Writing your own resource

```cpp
class TrackingResource : public std::pmr::memory_resource {
public:
    explicit TrackingResource(std::pmr::memory_resource* up = std::pmr::get_default_resource()) : up_(up) {}
    std::size_t bytes = 0, peak = 0, calls = 0;
private:
    void* do_allocate(std::size_t n, std::size_t align) override {
        ++calls; bytes += n; peak = std::max(peak, bytes);
        return up_->allocate(n, align);
    }
    void do_deallocate(void* p, std::size_t n, std::size_t align) override {
        bytes -= n;
        up_->deallocate(p, n, align);
    }
    bool do_is_equal(const memory_resource& o) const noexcept override { return this == &o; }
    std::pmr::memory_resource* up_;
};
```

Resources chain (an **upstream** resource), so you can compose them: tracking → pool → monotonic → null.

## 6. Classic vs PMR

| | Classic allocator template | PMR |
|---|---|---|
| Dispatch | compile time (inlined) | virtual call per allocation |
| Container type | changes with the allocator | always the same `pmr::` type |
| Passing containers to functions | needs templates | ordinary `std::pmr::vector<T>&` |
| Nested containers sharing a resource | manual (`scoped_allocator_adaptor`) | automatic |
| Typical use | allocator-aware libraries, max performance | applications, real-time subsystems, per-request arenas |

The virtual call costs about 1–2 ns, which is negligible next to the 20–100 ns of a general heap allocation it replaces.

## 7. Real-time pattern: allocate at start-up, never after

```cpp
class Controller {
    std::array<std::byte, 1 << 20> mem_;                         // reserved once
    std::pmr::monotonic_buffer_resource frame_{mem_.data(), mem_.size(), std::pmr::null_memory_resource()};
public:
    void tick() {
        std::pmr::vector<Waypoint> plan{&frame_};                // per-cycle scratch
        plan.reserve(256);
        compute_plan(plan);
        execute(plan);
        // plan is destroyed here (destructors run, deallocate is a no-op)
        frame_.release();                                        // O(1) reset for the next cycle
    }
};
```

There are no heap calls in the control loop, the worst-case time is bounded, and a capacity bug throws immediately (thanks to `null_memory_resource`) instead of silently allocating.

## 8. Exam-ready answers

> [!EXAM]
> **Allocators and memory resources.** An allocator encapsulates how a container obtains and releases memory. In the classic model, the allocator is a template parameter accessed through `std::allocator_traits`, supporting rebinding to node types and propagation policies, but making the allocator part of the container's type. C++17 polymorphic memory resources move the strategy into a runtime object derived from `std::pmr::memory_resource`, used through `std::pmr::polymorphic_allocator`, so containers with different strategies share one type and nested containers propagate the resource automatically. Standard resources include monotonic (arena) and pool resources, used to avoid heap allocation, reduce fragmentation and bound allocation latency.

## 9. Cheat sheet

| Need | Use |
|---|---|
| per-frame/per-request scratch | `pmr::monotonic_buffer_resource` + `release()` |
| forbid heap fallback | upstream `pmr::null_memory_resource()` |
| many same-size nodes | pool / `unsynchronized_pool_resource` |
| containers on a resource | `std::pmr::vector<T> v{&res};` |
| count/track allocations | derive from `pmr::memory_resource` |
| zero-size stateless allocator member | `[[no_unique_address]] Alloc a;` |
| allocator-aware container code | `std::allocator_traits<A>::allocate/construct/destroy` |

> [!INTERVIEW]
> **"How would you guarantee no heap allocation in a control loop?"** Reserve all memory at start-up and back containers with `pmr::monotonic_buffer_resource` whose upstream is `null_memory_resource` (any overflow throws, so it's caught in testing). `reserve()` vector capacity, avoid `std::function` captures and `std::string` growth, and verify by overriding global `operator new` in a test build to count or abort calls inside the loop. Mention real-time OS features too: `mlockall` to prevent page faults.
