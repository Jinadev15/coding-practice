---
id: cpp-m3-robin-hood-map
title: A Robin Hood Hash Map
difficulty: Expert
order: 3
tags: hash tables, open addressing, templates, move semantics, std::optional, performance engineering
time_limit: 6
---
## Statement
`std::unordered_map` allocates a node per element and chases pointers. High-performance maps (Abseil's, Rust's former HashMap, ska::flat_hash_map) use **open addressing**. Implement the classic **Robin Hood** variant: on collision, the element that is *further from its home slot* keeps the slot ("take from the rich, give to the poor"), which keeps probe lengths short and uniform.

`template <class K, class V, class Hash = std::hash<K>> class RobinHoodMap`:
- The capacity is a **power of two** (at least 8), and the table **doubles** when an insertion would push the load factor above **0.875**. Slots are `std::optional<std::pair<K, V>>` (or equivalent) plus a stored probe distance. The home slot is `hash(key) & (capacity − 1)`.
- `bool insert(K key, V value)`: false (and no change) if the key already exists. Values may be **move-only** (`std::unique_ptr`).
- `V& operator[](const K&)` inserts a default-constructed value if needed.
- `V* find(const K&)` and `const V* find(const K&) const` return nullptr if the key is missing. Searches may stop early: once the current slot's distance is smaller than the probe distance so far, the key can't be further on.
- `bool erase(const K&)` uses **backward-shift deletion**: no tombstones, so later elements move back by one.
- `size()`, `empty()`, `capacity()`, `clear()` (keeps the capacity), `reserve(n)` (grows so that n elements fit under the load limit), and `max_probe()` (the largest stored probe distance).
- `template <class F> void for_each(F f) const` calls `f(key, value)` for every element.

## Starter
```cpp
#include <cstddef>
#include <functional>
#include <list>
#include <utility>
#include <vector>

template <class K, class V, class Hash = std::hash<K>>
class RobinHoodMap {                                  // a linked-list chain map: not Robin Hood, wrong growth rules
public:
    bool insert(K key, V value) { items_.emplace_back(std::move(key), std::move(value)); return true; }
    V* find(const K& k) { for (auto& [kk, v] : items_) if (kk == k) return &v; return nullptr; }
    const V* find(const K& k) const { for (auto& [kk, v] : items_) if (kk == k) return &v; return nullptr; }
    V& operator[](const K& k) { if (auto p = find(k)) return *p; items_.emplace_back(k, V{}); return items_.back().second; }
    bool erase(const K&) { return false; }
    std::size_t size() const { return items_.size(); }
    bool empty() const { return items_.empty(); }
    std::size_t capacity() const { return 8; }
    std::size_t max_probe() const { return 0; }
    void clear() { items_.clear(); }
    void reserve(std::size_t) {}
    template <class F> void for_each(F f) const { for (auto& [k, v] : items_) f(k, v); }
private:
    std::list<std::pair<K, V>> items_;
};
```

## Driver
```cpp
#include <cstdio>
#include <iostream>
#include <memory>
#include <random>
#include <string>
#include <unordered_map>

struct BadHash { std::size_t operator()(int x) const { return static_cast<std::size_t>(x % 3); } };

int main() {
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "basic") {
            RobinHoodMap<std::string, int> m;
            std::printf("empty %d cap %zu\n", m.empty(), m.capacity());
            bool a = m.insert("lidar", 10), b = m.insert("imu", 200), c = m.insert("lidar", 99);
            std::printf("insert %d %d dup %d size %zu lidar %d\n", a, b, c, m.size(), *m.find("lidar"));
            m["gps"] += 5; m["gps"] += 5;
            std::printf("gps %d missing %s\n", m["gps"], m.find("sonar") ? "?" : "null");
            for (int i = 0; i < 7; ++i) m.insert("k" + std::to_string(i), i);
            std::printf("size %zu cap %zu (grew at load > 0.875)\n", m.size(), m.capacity());
            bool e1 = m.erase("imu"), e2 = m.erase("imu");
            std::printf("erase %d %d size %zu imu %s k6 %d\n", e1, e2, m.size(), m.find("imu") ? "?" : "null", *m.find("k6"));
            long sum = 0; m.for_each([&](const std::string&, int v) { sum += v; });
            std::printf("sum %ld\n", sum);
            m.clear(); std::printf("cleared size %zu cap %zu find %s\n", m.size(), m.capacity(), m.find("gps") ? "?" : "null");
            RobinHoodMap<int, int> r; r.reserve(100); std::printf("reserve(100) cap %zu\n", r.capacity());
        } else if (cmd == "collisions") {
            RobinHoodMap<int, int, BadHash> m;
            for (int i = 0; i < 60; ++i) m.insert(i, i * i);
            bool ok = m.size() == 60;
            for (int i = 0; i < 60; i += 2) ok &= m.erase(i);
            for (int i = 0; i < 60; ++i) ok &= (i % 2 == 0) ? m.find(i) == nullptr : (m.find(i) && *m.find(i) == i * i);
            for (int i = 0; i < 60; i += 2) ok &= m.insert(i, -i);
            for (int i = 0; i < 60; ++i) ok &= *m.find(i) == (i % 2 ? i * i : -i);
            std::printf("adversarial hash ok %d size %zu\n", ok, m.size());
            RobinHoodMap<int, std::unique_ptr<int>> mo;
            for (int i = 0; i < 1000; ++i) mo.insert(i, std::make_unique<int>(i * 3));
            for (int i = 0; i < 1000; i += 3) mo.erase(i);
            long s = 0; mo.for_each([&](int, const std::unique_ptr<int>& p) { s += *p; });
            std::printf("move-only values ok, size %zu sum %ld\n", mo.size(), s);
        } else if (cmd == "fuzz") {
            RobinHoodMap<std::uint64_t, std::uint64_t> m;
            std::unordered_map<std::uint64_t, std::uint64_t> ref;
            std::mt19937_64 rng(5);
            bool ok = true;
            for (int i = 0; i < 400000; ++i) {
                std::uint64_t k = rng() % 50000, v = rng();
                switch (rng() % 4) {
                case 0: ok &= m.insert(k, v) == ref.emplace(k, v).second; break;
                case 1: ok &= m.erase(k) == (ref.erase(k) == 1); break;
                case 2: m[k] = v; ref[k] = v; break;
                default: { auto* p = m.find(k); auto it = ref.find(k); ok &= (p == nullptr) == (it == ref.end()) && (!p || *p == it->second); }
                }
            }
            ok &= m.size() == ref.size();
            std::size_t cnt = 0; m.for_each([&](std::uint64_t k, std::uint64_t v) { ++cnt; ok &= ref.at(k) == v; });
            std::printf("fuzz vs unordered_map ok %d size %zu counted %zu\n", ok, m.size(), cnt);
            RobinHoodMap<std::uint64_t, int> big;
            for (std::uint64_t i = 0; i < 1000000; ++i) big.insert(i * 0x9E3779B97F4A7C15ULL, 1);
            std::printf("1M inserts: size %zu cap %zu max probe small %d\n", big.size(), big.capacity(), big.max_probe() < 64);
        }
    }
}
```

## Tests
=== sample
basic
---
empty 1 cap 8
insert 1 1 dup 0 size 2 lidar 10
gps 10 missing null
size 10 cap 16 (grew at load > 0.875)
erase 1 0 size 9 imu null k6 6
sum 41
cleared size 0 cap 16 find null
reserve(100) cap 128
=== hidden
collisions
---
adversarial hash ok 1 size 60
move-only values ok, size 666 sum 998001
=== hidden
fuzz
---
fuzz vs unordered_map ok 1 size 33293 counted 33293
1M inserts: size 1000000 cap 2097152 max probe small 1

## Hints
- Slots: `struct Slot { std::int32_t dist = -1; std::optional<std::pair<K, V>> kv; };`, where `dist = -1` means empty. On insert, carry `(key, value, d)`. At each slot, if it's empty, place there; if `slot.dist < d`, **swap** the carried element with the resident and continue with the evicted one; then `d++`.
- Check for an existing key *before* inserting (find first), so a duplicate never moves anything.
- Grow first if `(size + 1) > capacity * 7 / 8`. Rehash by re-inserting every element into a fresh table (moving the values).
- Backward shift: after emptying slot `i`, while the next slot is occupied and its `dist > 0`, move it into slot `i`, decrement its dist, and advance.

## Solution
```cpp
#include <cstddef>
#include <cstdint>
#include <functional>
#include <optional>
#include <utility>
#include <vector>

template <class K, class V, class Hash = std::hash<K>>
class RobinHoodMap {
    struct Slot {
        std::int32_t dist = -1;                           // -1: empty; else distance from home slot
        std::optional<std::pair<K, V>> kv;
    };

public:
    RobinHoodMap() : slots_(8) {}

    std::size_t size() const { return size_; }
    bool empty() const { return size_ == 0; }
    std::size_t capacity() const { return slots_.size(); }
    std::size_t max_probe() const {
        std::int32_t m = 0;
        for (const auto& s : slots_) m = std::max(m, s.dist);
        return static_cast<std::size_t>(m);
    }

    bool insert(K key, V value) {
        if (find(key)) return false;
        if ((size_ + 1) * 8 > slots_.size() * 7) rehash(slots_.size() * 2);
        place(std::move(key), std::move(value));
        return true;
    }

    V& operator[](const K& key) {
        if (V* p = find(key)) return *p;
        insert(key, V{});
        return *find(key);
    }

    V* find(const K& key) { return const_cast<V*>(std::as_const(*this).find(key)); }

    const V* find(const K& key) const {
        const std::size_t mask = slots_.size() - 1;
        std::size_t i = hash_(key) & mask;
        for (std::int32_t d = 0;; ++d, i = (i + 1) & mask) {
            const Slot& s = slots_[i];
            if (s.dist < d) return nullptr;                // empty, or a "richer" element: key can't be further
            if (s.kv->first == key) return &s.kv->second;
        }
    }

    bool erase(const K& key) {
        const std::size_t mask = slots_.size() - 1;
        std::size_t i = hash_(key) & mask;
        for (std::int32_t d = 0;; ++d, i = (i + 1) & mask) {
            Slot& s = slots_[i];
            if (s.dist < d) return false;
            if (s.kv->first == key) break;
        }
        for (;;) {                                         // backward-shift deletion: no tombstones
            std::size_t next = (i + 1) & mask;
            Slot& n = slots_[next];
            if (n.dist <= 0) {
                slots_[i].kv.reset();
                slots_[i].dist = -1;
                break;
            }
            slots_[i].kv = std::move(n.kv);
            slots_[i].dist = n.dist - 1;
            i = next;
        }
        --size_;
        return true;
    }

    void clear() {
        for (auto& s : slots_) { s.kv.reset(); s.dist = -1; }
        size_ = 0;
    }

    void reserve(std::size_t n) {
        std::size_t cap = slots_.size();
        while (n * 8 > cap * 7) cap *= 2;
        if (cap != slots_.size()) rehash(cap);
    }

    template <class F>
    void for_each(F f) const {
        for (const auto& s : slots_) if (s.dist >= 0) f(s.kv->first, s.kv->second);
    }

private:
    void place(K key, V value) {
        const std::size_t mask = slots_.size() - 1;
        std::size_t i = hash_(key) & mask;
        std::pair<K, V> carry(std::move(key), std::move(value));
        for (std::int32_t d = 0;; ++d, i = (i + 1) & mask) {
            Slot& s = slots_[i];
            if (s.dist < 0) { s.kv.emplace(std::move(carry)); s.dist = d; ++size_; return; }
            if (s.dist < d) {                              // Robin Hood: the poorer element takes the slot
                std::swap(carry, *s.kv);
                std::swap(d, s.dist);
            }
        }
    }

    void rehash(std::size_t new_cap) {
        std::vector<Slot> old = std::move(slots_);
        slots_ = std::vector<Slot>(new_cap);
        size_ = 0;
        for (auto& s : old) if (s.dist >= 0) place(std::move(s.kv->first), std::move(s.kv->second));
    }

    std::vector<Slot> slots_;
    std::size_t size_ = 0;
    Hash hash_;
};
```

- **Open addressing** stores elements inline in one array: no per-node allocation, and probes walk contiguous memory, which is cache-friendly. That's why flat maps beat `std::unordered_map` by a wide margin in practice.
- **Robin Hood displacement** bounds the variance of probe lengths: whenever the carried element is further from home than the resident, they swap. Lookups can stop early as soon as they meet an element "richer" than the probe distance so far.
- **Backward-shift deletion** removes tombstones entirely, so the table never degrades after many erase/insert cycles (the 400,000-operation fuzz against `std::unordered_map` exercises exactly that).
- **Move-only support**: values move during displacement, rehashing and erasure, never copy, so `std::unique_ptr` values work.
- **Power-of-two capacity** turns the modulo into a mask, and a load-factor cap of 0.875 balances memory against probe length. Even an adversarial hash (everything in 3 buckets) stays correct, just slower.
