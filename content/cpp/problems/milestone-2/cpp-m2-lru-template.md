---
id: cpp-m2-lru-template
title: Generic Thread-Safe LRU Cache
difficulty: Hard
order: 1
tags: templates, concepts, STL, list splice, mutex, optional
time_limit: 3
---
## Statement
Implement a **generic, thread-safe LRU cache** template with O(1) operations:

```cpp
template <class K> concept CacheKey = std::equality_comparable<K> && requires(const K& k) {
    { std::hash<K>{}(k) } -> std::convertible_to<std::size_t>;
};

template <CacheKey K, std::copy_constructible V>
class LruCache {
public:
    explicit LruCache(std::size_t capacity);        // capacity >= 1
    std::optional<V> get(const K& key);             // a hit moves the key to most-recently-used
    void put(const K& key, V value);                // insert or update (becomes MRU); evict the LRU entry if over capacity
    bool erase(const K& key);
    template <class F> V get_or_compute(const K& key, F&& compute);   // compute(key) on a miss, store and return it
    std::size_t size() const;
    std::vector<K> keys_mru_to_lru() const;         // for inspection
    struct Stats { std::size_t hits, misses, evictions; };
    Stats stats() const;
};
```

- Use a `std::list<std::pair<K, V>>` (MRU at the front) plus an `std::unordered_map<K, list::iterator>`. **Move entries with `list::splice`**, which is O(1) and never invalidates iterators.
- All public operations take one `std::mutex` (mutable, for the const methods). `get_or_compute` must **not hold the lock while computing** (the computation may be slow, or may recursively use the cache). If another thread inserted the key in the meantime, keep the existing value.
- The driver also checks that a type without `std::hash` is rejected at compile time (`static_assert(!CacheKey<...>)`).

## Starter
```cpp
#include <list>
#include <unordered_map>
#include <optional>
#include <mutex>
#include <vector>
#include <concepts>
#include <functional>

template <class K> concept CacheKey = true;

template <CacheKey K, std::copy_constructible V>
class LruCache {
public:
    explicit LruCache(std::size_t capacity) : cap_(capacity) {}
    std::optional<V> get(const K& key) { return std::nullopt; }
    void put(const K& key, V value) {}
    bool erase(const K& key) { return false; }
    template <class F> V get_or_compute(const K& key, F&& compute) { return compute(key); }
    std::size_t size() const { return 0; }
    std::vector<K> keys_mru_to_lru() const { return {}; }
    struct Stats { std::size_t hits, misses, evictions; };
    Stats stats() const { return {0, 0, 0}; }
private:
    std::size_t cap_;
};
```

## Driver
```cpp
#include <iostream>
#include <string>
#include <thread>
#include <atomic>

struct NoHash { int x; bool operator==(const NoHash&) const = default; };
static_assert(CacheKey<int> && CacheKey<std::string>);
static_assert(!CacheKey<NoHash>, "keys need std::hash");

template <class K, class V>
void show(const LruCache<K, V>& c) {
    std::cout << "  [";
    bool first = true;
    for (const auto& k : c.keys_mru_to_lru()) { std::cout << (first ? "" : " ") << k; first = false; }
    auto s = c.stats();
    std::cout << "] size=" << c.size() << " hits=" << s.hits << " misses=" << s.misses << " evictions=" << s.evictions << '\n';
}

int main() {
    std::string cmd;
    LruCache<std::string, int> c(3);
    while (std::cin >> cmd) {
        if (cmd == "put") { std::string k; int v; std::cin >> k >> v; c.put(k, v); std::cout << "put " << k << '\n'; show(c); }
        else if (cmd == "get") { std::string k; std::cin >> k; auto v = c.get(k); std::cout << "get " << k << " -> " << (v ? std::to_string(*v) : "miss") << '\n'; show(c); }
        else if (cmd == "erase") { std::string k; std::cin >> k; std::cout << "erase " << k << " -> " << c.erase(k) << '\n'; show(c); }
        else if (cmd == "compute") {
            std::string k; std::cin >> k;
            int calls = 0;
            int v = c.get_or_compute(k, [&](const std::string& key) { ++calls; return static_cast<int>(key.size()) * 100; });
            std::cout << "compute " << k << " -> " << v << " (computed " << calls << "x)\n"; show(c);
        } else if (cmd == "stress") {
            LruCache<int, long long> big(512);
            std::atomic<long long> computed{0};
            {
                std::vector<std::jthread> ts;
                for (int t = 0; t < 8; ++t)
                    ts.emplace_back([&, t] {
                        for (int i = 0; i < 20000; ++i) {
                            int key = (i * 31 + t * 7) % 1000;
                            long long v = big.get_or_compute(key, [&](int k) { ++computed; return 1LL * k * k; });
                            if (v != 1LL * key * key) std::cout << "WRONG VALUE\n";
                            if (i % 97 == 0) big.erase(key);
                        }
                    });
            }
            auto s = big.stats();
            std::cout << "stress: size<=512 " << (big.size() <= 512) << " hits+misses=" << (s.hits + s.misses)
                      << " computed>0 " << (computed > 0) << '\n';
        }
    }
}
```

## Tests
=== sample
put a 1
put b 2
put c 3
get a
put d 4
get b
put c 30
compute e
compute e
erase a
erase zzz
---
put a
  [a] size=1 hits=0 misses=0 evictions=0
put b
  [b a] size=2 hits=0 misses=0 evictions=0
put c
  [c b a] size=3 hits=0 misses=0 evictions=0
get a -> 1
  [a c b] size=3 hits=1 misses=0 evictions=0
put d
  [d a c] size=3 hits=1 misses=0 evictions=1
get b -> miss
  [d a c] size=3 hits=1 misses=1 evictions=1
put c
  [c d a] size=3 hits=1 misses=1 evictions=1
compute e -> 100 (computed 1x)
  [e c d] size=3 hits=1 misses=2 evictions=2
compute e -> 100 (computed 0x)
  [e c d] size=3 hits=2 misses=2 evictions=2
erase a -> 0
  [e c d] size=3 hits=2 misses=2 evictions=2
erase zzz -> 0
  [e c d] size=3 hits=2 misses=2 evictions=2
=== hidden
get nothing
compute abc
put x 1
put y 2
get abc
put z 3
put w 4
get x
get abc
erase w
put v 5
stress
---
get nothing -> miss
  [] size=0 hits=0 misses=1 evictions=0
compute abc -> 300 (computed 1x)
  [abc] size=1 hits=0 misses=2 evictions=0
put x
  [x abc] size=2 hits=0 misses=2 evictions=0
put y
  [y x abc] size=3 hits=0 misses=2 evictions=0
get abc -> 300
  [abc y x] size=3 hits=1 misses=2 evictions=0
put z
  [z abc y] size=3 hits=1 misses=2 evictions=1
put w
  [w z abc] size=3 hits=1 misses=2 evictions=2
get x -> miss
  [w z abc] size=3 hits=1 misses=3 evictions=2
get abc -> 300
  [abc w z] size=3 hits=2 misses=3 evictions=2
erase w -> 1
  [abc z] size=2 hits=2 misses=3 evictions=2
put v
  [v abc z] size=3 hits=2 misses=3 evictions=2
stress: size<=512 1 hits+misses=160000 computed>0 1

## Hints
- `get`: find the key in the map. On a miss, count it and return `nullopt`. On a hit, `items_.splice(items_.begin(), items_, it->second)`, count a hit, and return a copy of the value.
- `put` with an existing key: update the value and splice it to the front. Otherwise `emplace_front` and record the iterator; if `size() > cap_`, erase `items_.back()`'s key from the map, `pop_back`, and count an eviction.
- `get_or_compute`: call `get` (which takes the lock and releases it), and on a miss, compute **without the lock**, then lock again: if the key now exists, return the existing value (count nothing extra), otherwise insert it.
- Factor the unlocked internals into private `*_locked` helpers to avoid recursive locking.

## Solution
```cpp
#include <list>
#include <unordered_map>
#include <optional>
#include <mutex>
#include <vector>
#include <concepts>
#include <functional>

template <class K>
concept CacheKey = std::equality_comparable<K> && requires(const K& k) {
    { std::hash<K>{}(k) } -> std::convertible_to<std::size_t>;
};

template <CacheKey K, std::copy_constructible V>
class LruCache {
public:
    struct Stats { std::size_t hits, misses, evictions; };

    explicit LruCache(std::size_t capacity) : cap_(capacity ? capacity : 1) {}

    std::optional<V> get(const K& key) {
        std::lock_guard lk(m_);
        return get_locked(key);
    }

    void put(const K& key, V value) {
        std::lock_guard lk(m_);
        put_locked(key, std::move(value));
    }

    bool erase(const K& key) {
        std::lock_guard lk(m_);
        auto it = index_.find(key);
        if (it == index_.end()) return false;
        items_.erase(it->second);
        index_.erase(it);
        return true;
    }

    template <class F>
    V get_or_compute(const K& key, F&& compute) {
        if (auto v = get(key)) return *v;                       // counts a hit or a miss
        V fresh = std::invoke(std::forward<F>(compute), key);   // computed WITHOUT holding the lock
        std::lock_guard lk(m_);
        if (auto it = index_.find(key); it != index_.end()) {   // someone else inserted it meanwhile
            items_.splice(items_.begin(), items_, it->second);
            return it->second->second;
        }
        put_locked(key, fresh);
        return fresh;
    }

    std::size_t size() const {
        std::lock_guard lk(m_);
        return items_.size();
    }

    std::vector<K> keys_mru_to_lru() const {
        std::lock_guard lk(m_);
        std::vector<K> out;
        out.reserve(items_.size());
        for (const auto& [k, v] : items_) out.push_back(k);
        return out;
    }

    Stats stats() const {
        std::lock_guard lk(m_);
        return stats_;
    }

private:
    std::optional<V> get_locked(const K& key) {
        auto it = index_.find(key);
        if (it == index_.end()) { ++stats_.misses; return std::nullopt; }
        items_.splice(items_.begin(), items_, it->second);      // O(1); the iterator stays valid
        ++stats_.hits;
        return it->second->second;
    }

    void put_locked(const K& key, V value) {
        if (auto it = index_.find(key); it != index_.end()) {
            it->second->second = std::move(value);
            items_.splice(items_.begin(), items_, it->second);
            return;
        }
        items_.emplace_front(key, std::move(value));
        index_.emplace(key, items_.begin());
        if (items_.size() > cap_) {
            index_.erase(items_.back().first);
            items_.pop_back();
            ++stats_.evictions;
        }
    }

    std::size_t cap_;
    mutable std::mutex m_;
    std::list<std::pair<K, V>> items_;                          // MRU at the front
    std::unordered_map<K, typename std::list<std::pair<K, V>>::iterator> index_;
    Stats stats_{0, 0, 0};
};
```

**Milestone review:**
- **STL composition (module 4):** `unordered_map` gives O(1) lookup, and `list` gives O(1) reordering via `splice`, which relinks nodes without copying and keeps every stored iterator valid. That's the classic LRU design, in idiomatic C++.
- **Templates and concepts (module 5):** `CacheKey` documents and enforces the key requirements at the interface, and an invalid key type fails with a readable error instead of a wall of `unordered_map` diagnostics.
- **Concurrency (module 8):** one mutex guards the invariants (the map and list always agree). `get_or_compute` deliberately computes outside the lock, avoiding the classic bug of holding a lock across slow or re-entrant work, and resolves the race by keeping whichever value got in first.
- **Lock-free internals:** private `_locked` helpers that assume the lock is held prevent double-locking a non-recursive mutex.
