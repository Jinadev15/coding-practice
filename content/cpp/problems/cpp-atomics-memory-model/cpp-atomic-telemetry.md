---
id: cpp-atomic-telemetry
title: Lock-Free Telemetry Counters and a Spinlock
difficulty: Hard
order: 1
tags: std::atomic, compare_exchange, memory orders, atomic_flag, false sharing
time_limit: 3
---
## Statement
A real-time controller records telemetry from many threads without taking locks. Implement:

```cpp
class Telemetry {
public:
    void record(long long latency_ns);   // called concurrently from many threads
    long long count() const;
    long long sum() const;
    long long max() const;               // a lock-free maximum via a compare_exchange_weak loop
    long long min() const;               // likewise (starts at LLONG_MAX)
};

class SpinLock {                         // a test-and-set spinlock built on std::atomic_flag
public:
    void lock();                         // acquire with memory_order_acquire (spin while it's set)
    void unlock();                       // release with memory_order_release
};

struct Published {                       // the release/acquire publication pattern
    void publish(const std::array<int, 4>& data);   // write the data (plain stores), then ready.store(true, release)
    std::optional<std::array<int, 4>> try_read() const;   // if ready.load(acquire), return the data
    std::array<int, 4> data{};
    std::atomic<bool> ready{false};
};
```

- `count` and `sum` use `fetch_add` with `memory_order_relaxed` (pure statistics).
- `min`/`max` use CAS loops: load the current value, and while the new value is better, try `compare_exchange_weak`.
- Put the hot atomics on **separate cache lines** (`alignas(64)`) to avoid false sharing.
- `SpinLock` must be usable with `std::lock_guard<SpinLock>` (it satisfies *BasicLockable*).

The driver hammers these from 8 threads and checks the exact totals.

## Starter
```cpp
#include <atomic>
#include <array>
#include <optional>
#include <climits>

class Telemetry {
public:
    void record(long long v) { ++count_; sum_ += v; if (v > max_) max_ = v; if (v < min_) min_ = v; }
    long long count() const { return count_; }
    long long sum() const { return sum_; }
    long long max() const { return max_; }
    long long min() const { return min_; }
private:
    long long count_ = 0, sum_ = 0, max_ = LLONG_MIN, min_ = LLONG_MAX;
};

class SpinLock {
public:
    void lock() {}
    void unlock() {}
};

struct Published {
    void publish(const std::array<int, 4>& d) { data = d; }
    std::optional<std::array<int, 4>> try_read() const { return data; }
    std::array<int, 4> data{};
    std::atomic<bool> ready{false};
};
```

## Driver
```cpp
#include <iostream>
#include <thread>
#include <vector>
#include <mutex>

int main() {
    int threads, per_thread;
    std::cin >> threads >> per_thread;
    Telemetry t;
    SpinLock sl;
    long long protected_counter = 0;                 // incremented only under the spinlock
    {
        std::vector<std::jthread> ws;
        for (int k = 0; k < threads; ++k)
            ws.emplace_back([&, k] {
                for (int i = 0; i < per_thread; ++i) {
                    long long v = (static_cast<long long>(k) * 7919 + i * 104729) % 1000003;
                    t.record(v);
                    std::lock_guard<SpinLock> g(sl);
                    ++protected_counter;
                }
            });
    }
    long long exp_sum = 0, exp_max = LLONG_MIN, exp_min = LLONG_MAX;
    for (int k = 0; k < threads; ++k)
        for (int i = 0; i < per_thread; ++i) {
            long long v = (static_cast<long long>(k) * 7919 + i * 104729) % 1000003;
            exp_sum += v; exp_max = std::max(exp_max, v); exp_min = std::min(exp_min, v);
        }
    std::cout << "count ok: " << (t.count() == 1LL * threads * per_thread) << '\n'
              << "sum ok: " << (t.sum() == exp_sum) << '\n'
              << "max ok: " << (t.max() == exp_max) << " min ok: " << (t.min() == exp_min) << '\n'
              << "spinlock ok: " << (protected_counter == 1LL * threads * per_thread) << '\n';

    Published pub;
    std::atomic<int> torn{0}, seen{0};
    {
        std::jthread reader([&] {
            for (int i = 0; i < 2000000 && seen == 0; ++i)
                if (auto d = pub.try_read()) { ++seen; if ((*d)[0] + (*d)[1] + (*d)[2] + (*d)[3] != 10) ++torn; }
        });
        std::jthread writer([&] { pub.publish({1, 2, 3, 4}); });
    }
    auto final_read = pub.try_read();
    std::cout << "published data consistent: " << (torn == 0 && final_read && (*final_read)[3] == 4) << '\n';
    std::cout << "lock-free: " << std::atomic<long long>::is_always_lock_free << '\n';
}
```

## Tests
=== sample
4 10000
---
count ok: 1
sum ok: 1
max ok: 1 min ok: 1
spinlock ok: 1
published data consistent: 1
lock-free: 1
=== hidden
1 5
---
count ok: 1
sum ok: 1
max ok: 1 min ok: 1
spinlock ok: 1
published data consistent: 1
lock-free: 1
=== hidden
8 200000
---
count ok: 1
sum ok: 1
max ok: 1 min ok: 1
spinlock ok: 1
published data consistent: 1
lock-free: 1

## Hints
- Counters: `alignas(64) std::atomic<long long> count_{0};` and `count_.fetch_add(1, std::memory_order_relaxed);`.
- Max: `long long cur = max_.load(std::memory_order_relaxed); while (v > cur && !max_.compare_exchange_weak(cur, v, std::memory_order_relaxed)) {}`. A failed CAS refreshes `cur` automatically.
- SpinLock: `std::atomic_flag f = ATOMIC_FLAG_INIT;`, then `while (f.test_and_set(std::memory_order_acquire)) { /* optionally f.wait(true) in C++20 */ }` and `f.clear(std::memory_order_release);`.
- Publication: write `data` first, then `ready.store(true, std::memory_order_release)`. The reader does `if (!ready.load(std::memory_order_acquire)) return std::nullopt; return data;`.

## Solution
```cpp
#include <atomic>
#include <array>
#include <optional>
#include <climits>

class Telemetry {
public:
    void record(long long v) {
        count_.fetch_add(1, std::memory_order_relaxed);
        sum_.fetch_add(v, std::memory_order_relaxed);
        long long cur = max_.load(std::memory_order_relaxed);
        while (v > cur && !max_.compare_exchange_weak(cur, v, std::memory_order_relaxed)) {}
        cur = min_.load(std::memory_order_relaxed);
        while (v < cur && !min_.compare_exchange_weak(cur, v, std::memory_order_relaxed)) {}
    }
    long long count() const { return count_.load(std::memory_order_relaxed); }
    long long sum() const { return sum_.load(std::memory_order_relaxed); }
    long long max() const { return max_.load(std::memory_order_relaxed); }
    long long min() const { return min_.load(std::memory_order_relaxed); }
private:
    alignas(64) std::atomic<long long> count_{0};
    alignas(64) std::atomic<long long> sum_{0};
    alignas(64) std::atomic<long long> max_{LLONG_MIN};
    alignas(64) std::atomic<long long> min_{LLONG_MAX};
};

class SpinLock {
public:
    void lock() {
        while (flag_.test_and_set(std::memory_order_acquire))
            flag_.wait(true, std::memory_order_relaxed);     // C++20: sleep instead of burning the CPU
    }
    void unlock() {
        flag_.clear(std::memory_order_release);
        flag_.notify_one();
    }
private:
    std::atomic_flag flag_ = ATOMIC_FLAG_INIT;
};

struct Published {
    void publish(const std::array<int, 4>& d) {
        data = d;                                           // plain writes...
        ready.store(true, std::memory_order_release);       // ...published by the release store
    }
    std::optional<std::array<int, 4>> try_read() const {
        if (!ready.load(std::memory_order_acquire)) return std::nullopt;
        return data;                                        // happens-after the writer's stores
    }
    std::array<int, 4> data{};
    std::atomic<bool> ready{false};
};
```

- **Relaxed RMW counters:** `fetch_add` is indivisible, so no increments are lost, and since the counters publish no other data, relaxed ordering is enough. The final values are read after the threads are joined, and the join synchronises.
- **CAS loops** implement atomic operations the hardware doesn't provide directly (there's no "atomic max" instruction). On failure, `compare_exchange_weak` loads the current value into `cur`, and the loop re-checks whether the update is still needed.
- **The spinlock** shows that a mutex is acquire on lock and release on unlock. It's built on `atomic_flag`, the one type guaranteed lock-free. C++20's `wait`/`notify` stop it from burning a core while waiting.
- **Release/acquire publication** guarantees that a reader who sees `ready == true` sees the whole array. The plain `data` accesses are then race-free, because they're ordered by the flag.
- **`alignas(64)`** keeps each counter on its own cache line, avoiding false sharing between the threads hammering them.
