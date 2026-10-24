---
id: cpp-spsc-ring
title: Wait-Free SPSC Ring Buffer
difficulty: Expert
order: 1
tags: lock-free, atomics, acquire-release, ring buffer, cache lines
time_limit: 3
---
## Statement
Pass millions of messages from a real-time producer thread (say, an IMU interrupt handler at 1 kHz × many channels) to a consumer thread **without locks or allocation**. Implement a single-producer/single-consumer ring buffer:

```cpp
template <typename T, std::size_t N>           // N is a power of two (static_assert it)
class SpscRing {
public:
    bool try_push(const T& v);                  // producer thread only; false if full
    bool try_pop(T& out);                       // consumer thread only; false if empty
    std::size_t size_approx() const;
    static constexpr std::size_t capacity() { return N; }
};
```

Requirements:
- **No mutexes and no CAS**: just two `std::atomic<std::size_t>` indices (`head_` written only by the consumer, `tail_` only by the producer) with the correct memory orders. The producer publishes an element with a **release** store of `tail_`, and the consumer reads `tail_` with **acquire**, and symmetrically for `head_`.
- The indices keep increasing (wrap-around of `size_t` is harmless), and the slot is `index & (N - 1)`.
- Put `head_` and `tail_` on separate cache lines.
- The driver checks at compile time that the indices are always lock-free, and at run time that 10 million messages arrive complete, in order, and fast.

## Starter
```cpp
#include <atomic>
#include <array>
#include <cstddef>

template <typename T, std::size_t N>
class SpscRing {
public:
    bool try_push(const T& v) { if (count_ == N) return false; buf_[(head_ + count_) % N] = v; ++count_; return true; }
    bool try_pop(T& out) { if (count_ == 0) return false; out = buf_[head_]; head_ = (head_ + 1) % N; --count_; return true; }
    std::size_t size_approx() const { return count_; }
    static constexpr std::size_t capacity() { return N; }
private:
    std::array<T, N> buf_{};
    std::size_t head_ = 0, count_ = 0;          // a data race between the two threads!
};
```

## Driver
```cpp
#include <iostream>
#include <thread>
#include <chrono>

struct Sample { std::uint64_t seq; double value; };

static_assert(std::atomic<std::size_t>::is_always_lock_free);

int main() {
    std::uint64_t n;
    std::cin >> n;
    SpscRing<Sample, 1024> ring;
    std::uint64_t received = 0, out_of_order = 0;
    double checksum = 0;
    auto t0 = std::chrono::steady_clock::now();
    {
        std::jthread producer([&] {
            for (std::uint64_t i = 0; i < n;) {
                if (ring.try_push(Sample{i, static_cast<double>(i % 1000) * 0.5})) ++i;
            }
        });
        std::uint64_t expect = 0;
        Sample s;
        while (received < n) {
            if (ring.try_pop(s)) {
                if (s.seq != expect) ++out_of_order;
                ++expect;
                checksum += s.value;
                ++received;
            }
        }
    }
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - t0).count();
    Sample dummy;
    std::cout << "received " << received << " out_of_order " << out_of_order << " checksum " << static_cast<long long>(checksum)
              << " empty_at_end " << !ring.try_pop(dummy) << " capacity " << decltype(ring)::capacity()
              << " fast " << (ms < 2500) << '\n';
}
```

## Tests
=== sample
1000
---
received 1000 out_of_order 0 checksum 249750 empty_at_end 1 capacity 1024 fast 1
=== hidden
1
---
received 1 out_of_order 0 checksum 0 empty_at_end 1 capacity 1024 fast 1
=== hidden
10000000
---
received 10000000 out_of_order 0 checksum 2497500000 empty_at_end 1 capacity 1024 fast 1

## Hints
- `alignas(64) std::atomic<std::size_t> head_{0};` and `alignas(64) std::atomic<std::size_t> tail_{0};`.
- `try_push`: `t = tail_.load(relaxed)` (only we write it); `if (t - head_.load(acquire) == N) return false;`; write `buf_[t & (N-1)]`; then `tail_.store(t + 1, release)`.
- `try_pop`: `h = head_.load(relaxed)`; `if (h == tail_.load(acquire)) return false;`; read the slot; then `head_.store(h + 1, release)`, which frees the slot for the producer.
- The acquire in `try_pop` pairs with the release in `try_push`, so the consumer sees the element's data. The acquire in `try_push` pairs with the release in `try_pop`, so the producer doesn't overwrite a slot that's still being read.

## Solution
```cpp
#include <atomic>
#include <array>
#include <cstddef>

template <typename T, std::size_t N>
class SpscRing {
    static_assert(N >= 2 && (N & (N - 1)) == 0, "N must be a power of two");
public:
    bool try_push(const T& v) {                                  // producer only
        const std::size_t t = tail_.load(std::memory_order_relaxed);
        if (t - head_.load(std::memory_order_acquire) == N) return false;   // full
        buf_[t & (N - 1)] = v;
        tail_.store(t + 1, std::memory_order_release);           // publish the element
        return true;
    }

    bool try_pop(T& out) {                                       // consumer only
        const std::size_t h = head_.load(std::memory_order_relaxed);
        if (h == tail_.load(std::memory_order_acquire)) return false;       // empty
        out = buf_[h & (N - 1)];
        head_.store(h + 1, std::memory_order_release);           // hand the slot back
        return true;
    }

    std::size_t size_approx() const {
        return tail_.load(std::memory_order_acquire) - head_.load(std::memory_order_acquire);
    }
    static constexpr std::size_t capacity() { return N; }

private:
    std::array<T, N> buf_{};
    alignas(64) std::atomic<std::size_t> head_{0};               // written by the consumer
    alignas(64) std::atomic<std::size_t> tail_{0};               // written by the producer
};
```

**Why this is correct without locks:**
- **Single writer per index:** only the producer writes `tail_` and only the consumer writes `head_`, so no read-modify-write races exist and no CAS is needed. Each side reads its own index with relaxed ordering.
- **Release/acquire pairs:** the producer's `tail_.store(release)` happens after writing the slot, and the consumer's `tail_.load(acquire)` that observes the new tail therefore sees the slot's contents. Symmetrically, the consumer releases a slot with `head_.store(release)`, and the producer's acquire load guarantees the consumer has finished reading before the slot is overwritten.
- **Monotonic indices:** `tail - head` is the fill level, even across `size_t` wrap-around (unsigned arithmetic is modular), and `& (N - 1)` maps an index to its slot.
- **Wait-free and allocation-free:** every operation completes in a bounded number of steps. That's what real-time and interrupt contexts require, and why this structure appears in audio engines, robot middleware and trading systems.
- **`alignas(64)`** keeps the producer's and consumer's indices off each other's cache line, which matters at tens of millions of messages per second.
