---
id: cpp-bounded-queue
title: Bounded Blocking Queue with Close
difficulty: Hard
order: 1
tags: condition_variable, unique_lock, producer-consumer, backpressure
time_limit: 3
---
## Statement
Implement the workhorse of multi-threaded pipelines, a **bounded blocking queue**:

```cpp
template <typename T>
class BoundedQueue {
public:
    explicit BoundedQueue(std::size_t capacity);
    bool push(T value);                       // blocks while full; returns false (and drops value) if the queue is closed
    std::optional<T> pop();                   // blocks while empty; std::nullopt once closed AND drained
    std::optional<T> try_pop_for(std::chrono::milliseconds timeout);   // nullopt on timeout (or closed and drained)
    void close();                             // wake everyone: pushes start failing, pops drain the remaining items
    std::size_t size() const;
};
```

Use **one mutex and two condition variables** (`not_full_`, `not_empty_`), with predicates in every wait. The driver runs stress scenarios with several producers and consumers, verifying that every item is delivered exactly once, that the queue never exceeds its capacity, that per-producer order is preserved, and that blocked threads are released by `close()`.

## Starter
```cpp
#include <mutex>
#include <condition_variable>
#include <deque>
#include <optional>
#include <chrono>

template <typename T>
class BoundedQueue {
public:
    explicit BoundedQueue(std::size_t capacity) : cap_(capacity) {}
    bool push(T value) { q_.push_back(std::move(value)); return true; }
    std::optional<T> pop() {
        if (q_.empty()) return std::nullopt;
        T v = std::move(q_.front()); q_.pop_front(); return v;
    }
    std::optional<T> try_pop_for(std::chrono::milliseconds) { return pop(); }
    void close() {}
    std::size_t size() const { return q_.size(); }
private:
    std::size_t cap_;
    std::deque<T> q_;
};
```

## Driver
```cpp
#include <iostream>
#include <thread>
#include <vector>
#include <atomic>
#include <algorithm>
#include <string>

void scenario(int producers, int consumers, int items, std::size_t cap) {
    BoundedQueue<std::pair<int, int>> q(cap);
    std::atomic<std::size_t> max_size{0};
    std::vector<std::vector<std::pair<int, int>>> got(consumers);
    {
        std::vector<std::jthread> threads;
        for (int c = 0; c < consumers; ++c)
            threads.emplace_back([&, c] {
                while (auto item = q.pop()) {
                    got[c].push_back(*item);
                    std::size_t s = q.size(), m = max_size.load();
                    while (s > m && !max_size.compare_exchange_weak(m, s)) {}
                }
            });
        std::vector<std::jthread> prods;
        for (int p = 0; p < producers; ++p)
            prods.emplace_back([&, p] { for (int i = 0; i < items; ++i) q.push({p, i}); });
        prods.clear();                       // wait for the producers
        q.close();                           // then release the consumers
    }
    std::vector<std::pair<int, int>> all;
    bool ordered = true;
    for (auto& v : got) {
        std::vector<int> last(producers, -1);
        for (auto [p, i] : v) { if (i <= last[p]) ordered = false; last[p] = i; }
        all.insert(all.end(), v.begin(), v.end());
    }
    std::sort(all.begin(), all.end());
    bool exact = all.size() == static_cast<std::size_t>(producers * items) &&
                 std::adjacent_find(all.begin(), all.end()) == all.end();
    std::cout << "P=" << producers << " C=" << consumers << " items=" << items * producers
              << " delivered_exactly_once=" << exact << " per_producer_order=" << ordered
              << " within_capacity=" << (max_size.load() <= cap) << '\n';
}

int main() {
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "run") { int p, c, n; std::size_t cap; std::cin >> p >> c >> n >> cap; scenario(p, c, n, cap); }
        else if (cmd == "closed") {
            BoundedQueue<int> q(2);
            q.push(1);
            q.close();
            bool pushed = q.push(2);
            auto a = q.pop(), b = q.pop();
            std::cout << "after close: push=" << pushed << " pop=" << (a ? *a : -1) << " then " << (b ? "value" : "nullopt") << '\n';
        } else if (cmd == "timeout") {
            BoundedQueue<int> q(1);
            auto t0 = std::chrono::steady_clock::now();
            auto r = q.try_pop_for(std::chrono::milliseconds(50));
            auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - t0).count();
            std::cout << "timeout: got " << (r ? "value" : "nullopt") << " waited>=45ms " << (ms >= 45) << '\n';
        } else if (cmd == "unblock") {
            BoundedQueue<int> q(1);
            q.push(1);
            std::jthread blocked([&] { bool ok = q.push(2); std::cout << "blocked producer returned " << ok << '\n'; });
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
            q.close();
        }
    }
}
```

## Tests
=== sample
closed
run 2 2 1000 4
---
after close: push=0 pop=1 then nullopt
P=2 C=2 items=2000 delivered_exactly_once=1 per_producer_order=1 within_capacity=1
=== hidden
timeout
unblock
run 1 1 50000 1
run 8 3 20000 16
run 3 8 20000 1000
---
timeout: got nullopt waited>=45ms 1
blocked producer returned 0
P=1 C=1 items=50000 delivered_exactly_once=1 per_producer_order=1 within_capacity=1
P=8 C=3 items=160000 delivered_exactly_once=1 per_producer_order=1 within_capacity=1
P=3 C=8 items=60000 delivered_exactly_once=1 per_producer_order=1 within_capacity=1

## Hints
- `push`: `std::unique_lock lk(m_); not_full_.wait(lk, [&] { return closed_ || q_.size() < cap_; }); if (closed_) return false;`, then push, unlock, and `not_empty_.notify_one()`.
- `pop`: wait on `not_empty_` for `closed_ || !q_.empty()`. If it's empty, return `nullopt`. Otherwise take the item and `not_full_.notify_one()`.
- `try_pop_for`: `not_empty_.wait_for(lk, timeout, pred)` returns false on timeout.
- `close`: set `closed_` under the lock, then `notify_all` on **both** condition variables.
- Make the mutex `mutable` so that `size() const` can lock it.

## Solution
```cpp
#include <mutex>
#include <condition_variable>
#include <deque>
#include <optional>
#include <chrono>

template <typename T>
class BoundedQueue {
public:
    explicit BoundedQueue(std::size_t capacity) : cap_(capacity ? capacity : 1) {}

    bool push(T value) {
        {
            std::unique_lock lk(m_);
            not_full_.wait(lk, [&] { return closed_ || q_.size() < cap_; });
            if (closed_) return false;
            q_.push_back(std::move(value));
        }
        not_empty_.notify_one();
        return true;
    }

    std::optional<T> pop() {
        std::optional<T> out;
        {
            std::unique_lock lk(m_);
            not_empty_.wait(lk, [&] { return closed_ || !q_.empty(); });
            if (q_.empty()) return std::nullopt;            // closed and drained
            out = std::move(q_.front());
            q_.pop_front();
        }
        not_full_.notify_one();
        return out;
    }

    std::optional<T> try_pop_for(std::chrono::milliseconds timeout) {
        std::optional<T> out;
        {
            std::unique_lock lk(m_);
            if (!not_empty_.wait_for(lk, timeout, [&] { return closed_ || !q_.empty(); })) return std::nullopt;
            if (q_.empty()) return std::nullopt;
            out = std::move(q_.front());
            q_.pop_front();
        }
        not_full_.notify_one();
        return out;
    }

    void close() {
        {
            std::lock_guard lk(m_);
            closed_ = true;
        }
        not_full_.notify_all();                              // release blocked producers
        not_empty_.notify_all();                             // release blocked consumers
    }

    std::size_t size() const {
        std::lock_guard lk(m_);
        return q_.size();
    }

private:
    std::size_t cap_;
    mutable std::mutex m_;
    std::condition_variable not_full_, not_empty_;
    std::deque<T> q_;
    bool closed_ = false;
};
```

- **Two condition variables** separate the two reasons to wait: producers wait for space, consumers for items. Each state change notifies only the side that can now make progress, which avoids waking threads that would just go back to sleep.
- **Predicates in every wait** handle spurious and stolen wake-ups, and checking `closed_` inside the predicates makes `close()` release everyone, so shutdown can't hang.
- **Notify after unlocking** (outside the inner scope) so a woken thread doesn't immediately block on the mutex the notifier still holds.
- **Backpressure:** a full queue blocks producers, so memory stays bounded when consumers are slower. That's essential in sensor pipelines where frames arrive faster than they can be processed.
- **FIFO with a single mutex** preserves each producer's order, which the driver verifies.
