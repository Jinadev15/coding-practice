---
id: cpp-concurrent-ledger
title: Concurrent Ledger with Fine-Grained Locks
difficulty: Hard
order: 1
tags: mutex, scoped_lock, shared_mutex, deadlock avoidance, invariants
time_limit: 4
---
## Statement
A ledger of accounts is updated by many threads at once. Implement it with **one mutex per account** (so transfers between unrelated accounts run in parallel), avoiding deadlock and data races:

```cpp
class Ledger {
public:
    explicit Ledger(std::vector<long long> initial);         // accounts 0..n-1
    bool transfer(std::size_t from, std::size_t to, long long amount);   // false if insufficient funds or from == to
    long long balance(std::size_t id) const;
    long long total() const;                                   // a CONSISTENT snapshot: lock all accounts (in order)
    std::size_t transfers_done() const;                        // successful transfers (std::atomic counter)
    // audit(): returns all balances atomically, as a single consistent snapshot
    std::vector<long long> audit() const;
};
```

Rules:
- Use `std::scoped_lock` (or a fixed global order) when locking two accounts.
- `total()` and `audit()` must never observe money in flight.
- Use `mutable` mutexes so the `const` queries can lock.

The driver runs 8 threads doing random transfers in all directions, while an auditor thread keeps checking `total()` and `audit()`.

## Starter
```cpp
#include <vector>
#include <mutex>
#include <atomic>

class Ledger {
public:
    explicit Ledger(std::vector<long long> initial) : bal_(std::move(initial)) {}
    bool transfer(std::size_t from, std::size_t to, long long amount) {
        if (bal_[from] < amount) return false;
        bal_[from] -= amount;
        bal_[to] += amount;
        ++done_;
        return true;
    }
    long long balance(std::size_t id) const { return bal_[id]; }
    long long total() const { long long s = 0; for (auto b : bal_) s += b; return s; }
    std::size_t transfers_done() const { return done_; }
    std::vector<long long> audit() const { return bal_; }
private:
    std::vector<long long> bal_;
    std::size_t done_ = 0;
};
```

## Driver
```cpp
#include <iostream>
#include <thread>
#include <random>
#include <numeric>

int main() {
    int accounts, threads, ops;
    unsigned seed;
    std::cin >> accounts >> threads >> ops >> seed;
    Ledger L(std::vector<long long>(accounts, 1000));
    long long expected = 1000LL * accounts;
    std::atomic<bool> stop{false};
    std::atomic<int> bad_snapshots{0}, audits{0};
    std::atomic<long long> attempted{0}, succeeded{0};
    {
        std::jthread auditor([&] {
            do {                                          // at least one audit, even if the workers finish first
                if (L.total() != expected) ++bad_snapshots;
                auto snap = L.audit();
                if (std::accumulate(snap.begin(), snap.end(), 0LL) != expected) ++bad_snapshots;
                ++audits;
            } while (!stop.load());
        });
        {
            std::vector<std::jthread> ws;
            for (int t = 0; t < threads; ++t)
                ws.emplace_back([&, t] {
                    std::mt19937 rng(seed * 100 + t);
                    std::uniform_int_distribution<int> acc(0, accounts - 1), amt(1, 400);
                    for (int i = 0; i < ops; ++i) {
                        ++attempted;
                        if (L.transfer(acc(rng), acc(rng), amt(rng))) ++succeeded;
                    }
                });
        }
        stop = true;
    }
    bool nonneg = true;
    for (int a = 0; a < accounts; ++a) nonneg &= L.balance(a) >= 0;
    std::cout << "total preserved: " << (L.total() == expected) << '\n'
              << "snapshots consistent: " << (bad_snapshots == 0) << " (audits ran: " << (audits > 0) << ")\n"
              << "no negative balances: " << nonneg << '\n'
              << "counter matches: " << (L.transfers_done() == static_cast<std::size_t>(succeeded)) << '\n'
              << "self transfer rejected: " << !L.transfer(0, 0, 1) << '\n';
}
```

## Tests
=== sample
4 4 20000 1
---
total preserved: 1
snapshots consistent: 1 (audits ran: 1)
no negative balances: 1
counter matches: 1
self transfer rejected: 1
=== hidden
2 8 50000 7
---
total preserved: 1
snapshots consistent: 1 (audits ran: 1)
no negative balances: 1
counter matches: 1
self transfer rejected: 1
=== hidden
64 8 50000 3
---
total preserved: 1
snapshots consistent: 1 (audits ran: 1)
no negative balances: 1
counter matches: 1
self transfer rejected: 1

## Hints
- `std::vector<std::mutex>` can't be resized after construction, but `std::vector<std::mutex> m_(n)` (constructed with a size) is fine. Mark it `mutable`.
- `transfer`: return false if `from == to` (locking one mutex twice would deadlock), then `std::scoped_lock lk(m_[from], m_[to]);`, check the funds, and move the money.
- `total`/`audit`: lock all the mutexes in index order with `std::unique_lock`s kept in a vector, then read the balances.
- `std::atomic<std::size_t> done_{0};`

## Solution
```cpp
#include <vector>
#include <mutex>
#include <atomic>
#include <numeric>

class Ledger {
public:
    explicit Ledger(std::vector<long long> initial)
        : bal_(std::move(initial)), m_(bal_.size()) {}

    bool transfer(std::size_t from, std::size_t to, long long amount) {
        if (from == to) return false;
        std::scoped_lock lk(m_[from], m_[to]);             // deadlock-free acquisition of both
        if (bal_[from] < amount) return false;
        bal_[from] -= amount;
        bal_[to] += amount;
        done_.fetch_add(1, std::memory_order_relaxed);
        return true;
    }

    long long balance(std::size_t id) const {
        std::lock_guard lk(m_[id]);
        return bal_[id];
    }

    std::vector<long long> audit() const {
        std::vector<std::unique_lock<std::mutex>> locks;
        locks.reserve(m_.size());
        for (auto& m : m_) locks.emplace_back(m);           // all of them, always in index order
        return bal_;                                        // a consistent snapshot; unlocks at return
    }

    long long total() const {
        auto snap = audit();
        return std::accumulate(snap.begin(), snap.end(), 0LL);
    }

    std::size_t transfers_done() const { return done_.load(std::memory_order_relaxed); }

private:
    std::vector<long long> bal_;
    mutable std::vector<std::mutex> m_;
    std::atomic<std::size_t> done_{0};
};
```

- **Fine-grained locking:** one mutex per account lets transfers between disjoint pairs proceed in parallel. A single global mutex would be simpler but would serialise all 8 threads.
- **Deadlock freedom:** `std::scoped_lock` acquires the two mutexes with a deadlock-avoidance algorithm, so A→B and B→A can't deadlock. `audit` locks everything in a fixed index order, and since `scoped_lock`'s algorithm never holds one lock while blocking on another, the two strategies can't form a cycle.
- **Consistent snapshots:** holding every account lock while reading guarantees `total()` sees each transfer either completely or not at all. The auditor thread checks this thousands of times under contention.
- **The counter is atomic** with relaxed ordering, which is enough for a statistic read after the threads are joined. The starter's plain `size_t` is a data race.
