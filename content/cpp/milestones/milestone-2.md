# Study guide: Special quiz 2

Quiz 2 combines templates, concurrency and modern vocabulary types.

## 1. Generic thread-safe LRU cache — templates, concepts, `list::splice`

A `std::list` keeps the recency order, and an `unordered_map` maps each key to its **list iterator**. List iterators stay valid when other elements are inserted, erased or moved, which is exactly why this pairing works.

```cpp
template <class K, class V>
    requires std::equality_comparable<K> && requires(K k) { std::hash<K>{}(k); }
class LRU {
    std::size_t cap_;
    std::list<std::pair<K, V>> order_;                         // front = newest
    std::unordered_map<K, typename decltype(order_)::iterator> idx_;
    mutable std::mutex m_;
public:
    std::optional<V> get(const K& k) {
        std::lock_guard lock(m_);
        auto it = idx_.find(k);
        if (it == idx_.end()) return std::nullopt;
        order_.splice(order_.begin(), order_, it->second);     // O(1) move to front
        return it->second->second;
    }
    void put(K k, V v) {
        std::lock_guard lock(m_);
        if (auto it = idx_.find(k); it != idx_.end()) {
            it->second->second = std::move(v);
            order_.splice(order_.begin(), order_, it->second);
            return;
        }
        order_.emplace_front(k, std::move(v));
        idx_.emplace(std::move(k), order_.begin());
        if (order_.size() > cap_) { idx_.erase(order_.back().first); order_.pop_back(); }
    }
};
```

- A **concept** (`requires ...`) turns a confusing template error into a clear "constraint not satisfied" message.
- `std::optional<V>` says "maybe a value" without sentinels or exceptions.
- `splice` relinks a node without copying it or invalidating the iterator.
- Return values **by copy** from a locked cache. Returning a reference would escape the lock.

## 2. Parallel DAG executor — threads, futures, condition variables

Run tasks on N worker threads, starting a task as soon as all its dependencies are done.

```cpp
std::mutex m; std::condition_variable cv;
std::queue<int> ready; int remaining = n;
std::vector<int> indeg = /* ... */;

auto worker = [&] {
    for (;;) {
        int t;
        {
            std::unique_lock lk(m);
            cv.wait(lk, [&] { return !ready.empty() || remaining == 0; });   // predicate!
            if (ready.empty()) return;            // all done
            t = ready.front(); ready.pop();
        }
        run(t);                                   // outside the lock
        {
            std::lock_guard lk(m);
            --remaining;
            for (int v : out[t]) if (--indeg[v] == 0) ready.push(v);
        }
        cv.notify_all();
    }
};
```

Rules:

- Always call `wait` **with a predicate**. It handles spurious wakeups and missed notifications.
- Never run user work while holding the lock.
- If a task throws, catch the exception in the worker, store it as a `std::exception_ptr`, and rethrow it after the workers have been joined. `std::future` does the same thing for `std::async`.
- `std::jthread` joins automatically in its destructor.

## 3. A dynamically typed expression language — `variant`, `visit`, `expected`

```cpp
using Value = std::variant<std::monostate, long long, double, bool, std::string>;
```

`std::visit` with an "overloaded" helper handles each alternative in a type-safe way:

```cpp
template <class... F> struct overloaded : F... { using F::operator()...; };

std::string type_name(const Value& v) {
    return std::visit(overloaded{
        [](std::monostate)        { return std::string("nil"); },
        [](long long)             { return std::string("int"); },
        [](double)                { return std::string("float"); },
        [](bool)                  { return std::string("bool"); },
        [](const std::string&)    { return std::string("string"); },
    }, v);
}
```

For binary operators, visit **two** variants at once with `std::visit(f, a, b)`. You get one call for every combination of types, which is where you implement `int + float → float` and `string + string → concat`.

**Errors without exceptions:** `std::expected<Value, std::string>` (C++23) holds either a result or an error. Check it with `if (!r) return std::unexpected(r.error());`. The parser and evaluator both return `expected`, so errors bubble up cleanly.
