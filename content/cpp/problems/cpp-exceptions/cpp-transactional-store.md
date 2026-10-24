---
id: cpp-transactional-store
title: An Exception-Safe Transactional Store
difficulty: Hard
order: 1
tags: exceptions, strong guarantee, RAII, custom exceptions, noexcept
---
## Statement
Implement a key-value store whose batch updates are **all-or-nothing** even when the stored type's **copy constructor throws** at arbitrary moments.

```cpp
class StoreError : public std::runtime_error { ... };          // base for store errors
class KeyNotFound : public StoreError { ... };                 // what() == "key not found: <key>"; key() accessor
class InvalidOp : public StoreError { ... };                   // what() == "invalid op: <text>"

template <typename V>
class Store {
public:
    void put(const std::string& key, const V& value);          // strong guarantee
    const V& get(const std::string& key) const;                // throws KeyNotFound
    void erase(const std::string& key);                        // throws KeyNotFound
    // apply_batch: ops are "put KEY" (value from the values vector, consumed in order),
    // "erase KEY", "rename OLD NEW"; anything else throws InvalidOp.
    // If ANY op throws (including V's copy constructor), the store must be exactly as before, and the
    // exception propagates unchanged.
    void apply_batch(const std::vector<std::string>& ops, const std::vector<V>& values);
    std::size_t size() const noexcept;
    std::vector<std::string> keys() const;                     // sorted
};
```

The driver stores a `Fragile` type whose copy constructor throws `std::bad_alloc` after a configurable number of copies (simulating out-of-memory), and checks the store contents after every failed batch.

## Starter
```cpp
#include <map>
#include <string>
#include <vector>
#include <stdexcept>
#include <sstream>

class StoreError : public std::runtime_error { using std::runtime_error::runtime_error; };
class KeyNotFound : public StoreError { using StoreError::StoreError; };
class InvalidOp : public StoreError { using StoreError::StoreError; };

template <typename V>
class Store {
public:
    void put(const std::string& k, const V& v) { data_[k] = v; }
    const V& get(const std::string& k) const { return data_.at(k); }
    void erase(const std::string& k) { data_.erase(k); }
    void apply_batch(const std::vector<std::string>& ops, const std::vector<V>& values) {}
    std::size_t size() const noexcept { return data_.size(); }
    std::vector<std::string> keys() const { return {}; }
private:
    std::map<std::string, V> data_;
};
```

## Driver
```cpp
#include <iostream>
#include <new>

struct Fragile {
    static inline int copies_left = 1 << 30;      // throw when this reaches 0
    int v;
    explicit Fragile(int x) : v(x) {}
    Fragile(const Fragile& o) : v(o.v) { if (--copies_left < 0) throw std::bad_alloc(); }
    Fragile& operator=(const Fragile& o) { Fragile tmp(o); v = tmp.v; return *this; }
    Fragile(Fragile&&) noexcept = default;
    Fragile& operator=(Fragile&&) noexcept = default;
};

void dump(const Store<Fragile>& s) {
    std::cout << "  {";
    bool first = true;
    for (const auto& k : s.keys()) { std::cout << (first ? "" : ", ") << k << '=' << s.get(k).v; first = false; }
    std::cout << "}\n";
}

int main() {
    Store<Fragile> s;
    std::string line;
    while (std::getline(std::cin, line)) {
        std::istringstream in(line);
        std::string cmd;
        in >> cmd;
        try {
            if (cmd == "budget") { in >> Fragile::copies_left; std::cout << "budget " << Fragile::copies_left << '\n'; continue; }
            if (cmd == "get") { std::string k; in >> k; int v = s.get(k).v; std::cout << "get " << k << " = " << v << '\n'; continue; }
            if (cmd == "erase") { std::string k; in >> k; s.erase(k); std::cout << "erased " << k << '\n'; dump(s); continue; }
            if (cmd == "batch") {
                std::vector<std::string> ops;
                std::vector<Fragile> vals;
                std::string tok;
                std::string op;
                while (in >> tok) {
                    if (tok == ";") { ops.push_back(op); op.clear(); continue; }
                    if (tok.rfind("=", 0) == 0) { vals.emplace_back(std::stoi(tok.substr(1))); continue; }
                    op += (op.empty() ? "" : " ") + tok;
                }
                if (!op.empty()) ops.push_back(op);
                s.apply_batch(ops, vals);
                std::cout << "batch ok (" << ops.size() << " ops)\n";
                dump(s);
            }
        } catch (const KeyNotFound& e) {
            std::cout << "KeyNotFound: " << e.what() << '\n';
            dump(s);
        } catch (const StoreError& e) {
            std::cout << "StoreError: " << e.what() << '\n';
            dump(s);
        } catch (const std::bad_alloc&) {
            std::cout << "bad_alloc\n";
            Fragile::copies_left = 1 << 30;
            dump(s);
        }
    }
}
```

## Tests
=== sample
batch put a =1 ; put b =2 ; put c =3
batch rename a z ; erase b
batch put q =9 ; erase nope
batch put q =9 ; frobnicate x
get z
get a
budget 1
batch put x =5 ; put y =6
batch put n =4 ; rename z w
---
batch ok (3 ops)
  {a=1, b=2, c=3}
batch ok (2 ops)
  {c=3, z=1}
KeyNotFound: key not found: nope
  {c=3, z=1}
StoreError: invalid op: frobnicate x
  {c=3, z=1}
get z = 1
KeyNotFound: key not found: a
  {c=3, z=1}
budget 1
bad_alloc
  {c=3, z=1}
batch ok (2 ops)
  {c=3, n=4, w=1}
=== hidden
batch put k1 =10 ; put k2 =20 ; put k3 =30 ; put k4 =40
budget 0
batch put k1 =99
budget 2
batch put a =1 ; put b =2 ; put c =3
batch rename k1 k2
batch rename missing x
erase k9
erase k4
batch put k1 =7 ; put k1 =8
batch
---
batch ok (4 ops)
  {k1=10, k2=20, k3=30, k4=40}
budget 0
bad_alloc
  {k1=10, k2=20, k3=30, k4=40}
budget 2
bad_alloc
  {k1=10, k2=20, k3=30, k4=40}
batch ok (1 ops)
  {k2=10, k3=30, k4=40}
KeyNotFound: key not found: missing
  {k2=10, k3=30, k4=40}
KeyNotFound: key not found: k9
  {k2=10, k3=30, k4=40}
erased k4
  {k2=10, k3=30}
batch ok (2 ops)
  {k1=8, k2=10, k3=30}
batch ok (0 ops)
  {k1=8, k2=10, k3=30}

## Hints
- **Copy, modify, swap:** in `apply_batch`, copy `data_` into a local map, apply every op to the copy (any of them may throw), and only then do `data_.swap(copy)` (`noexcept`). If anything throws, the copy is destroyed and `data_` was never touched.
- The copy of the map itself copies every `V`, so it can throw too, and that's fine because it happens before the commit.
- `put` with the strong guarantee: `std::map::insert_or_assign` already gives it for a single element, or use the same copy/swap idea.
- `rename OLD NEW`: throws `KeyNotFound` if OLD is missing. Move the value (`std::move`, the move constructor is `noexcept`) into NEW, then erase OLD.
- Construct the exceptions with the full message: `KeyNotFound(key)` builds `"key not found: " + key`.

## Solution
```cpp
#include <map>
#include <string>
#include <vector>
#include <stdexcept>
#include <sstream>
#include <utility>

class StoreError : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

class KeyNotFound : public StoreError {
public:
    explicit KeyNotFound(const std::string& key) : StoreError("key not found: " + key), key_(key) {}
    const std::string& key() const noexcept { return key_; }
private:
    std::string key_;
};

class InvalidOp : public StoreError {
public:
    explicit InvalidOp(const std::string& op) : StoreError("invalid op: " + op) {}
};

template <typename V>
class Store {
public:
    void put(const std::string& key, const V& value) {
        auto copy = data_;                        // may throw: data_ untouched
        copy.insert_or_assign(key, value);
        data_.swap(copy);                         // noexcept commit
    }

    const V& get(const std::string& key) const {
        auto it = data_.find(key);
        if (it == data_.end()) throw KeyNotFound(key);
        return it->second;
    }

    void erase(const std::string& key) {
        if (data_.erase(key) == 0) throw KeyNotFound(key);
    }

    void apply_batch(const std::vector<std::string>& ops, const std::vector<V>& values) {
        std::map<std::string, V> work = data_;    // all the work happens on a copy
        std::size_t next_value = 0;
        for (const auto& op : ops) {
            std::istringstream in(op);
            std::string verb, a, b;
            in >> verb >> a >> b;
            if (verb == "put" && !a.empty()) {
                if (next_value >= values.size()) throw InvalidOp(op);
                work.insert_or_assign(a, values[next_value++]);       // copies V: may throw
            } else if (verb == "erase" && !a.empty()) {
                if (work.erase(a) == 0) throw KeyNotFound(a);
            } else if (verb == "rename" && !a.empty() && !b.empty()) {
                auto it = work.find(a);
                if (it == work.end()) throw KeyNotFound(a);
                V moved = std::move(it->second);                      // noexcept move
                work.erase(it);
                work.insert_or_assign(b, std::move(moved));
            } else {
                throw InvalidOp(op);
            }
        }
        data_.swap(work);                         // commit: cannot throw
    }

    std::size_t size() const noexcept { return data_.size(); }

    std::vector<std::string> keys() const {
        std::vector<std::string> k;
        k.reserve(data_.size());
        for (const auto& [key, v] : data_) k.push_back(key);
        return k;
    }

private:
    std::map<std::string, V> data_;
};
```

**Exception safety, demonstrated:**
- **The strong guarantee by construction:** every step that can throw (copying the map, copying values, failing lookups, invalid ops) happens on `work`. The only operation touching `data_` is `swap`, which is `noexcept`. Whatever throws, the store is exactly as before, which the driver verifies by dumping it after every failure, including simulated `bad_alloc`s in the middle of copying.
- **RAII cleans up the half-done work:** when an exception escapes, `work`'s destructor frees everything automatically. No `catch` blocks are needed inside `Store` at all.
- **A custom exception hierarchy** lets callers handle failures at the right granularity (`KeyNotFound` specifically, any `StoreError`, or anything at all), with context carried in the exception object (`key()`).
- The cost of copy-and-swap is a full copy per batch. Real databases get the same guarantee more cheaply with undo logs or persistent data structures, but the reasoning is identical.
