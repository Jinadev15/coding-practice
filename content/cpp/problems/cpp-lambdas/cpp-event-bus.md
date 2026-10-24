---
id: cpp-event-bus
title: Publish/Subscribe Event Bus
difficulty: Medium
order: 1
tags: lambdas, std::function, captures, callbacks, observer pattern
---
## Statement
Robot software is often wired together through an **event bus** (ROS topics work this way): components subscribe callbacks to topics, and publishers don't know who listens. Implement:

```cpp
class EventBus {
public:
    using Handler = std::function<void(const std::string& payload)>;
    int subscribe(const std::string& topic, Handler h);   // returns a unique id: 1, 2, 3, ...
    bool unsubscribe(int id);                             // false if the id is unknown
    int publish(const std::string& topic, const std::string& payload);  // calls the topic's handlers in subscription order; returns how many ran
    std::size_t handler_count(const std::string& topic) const;
};
```

**Re-entrancy rule:** a handler may call `subscribe`, `unsubscribe` or `publish` *during* a publish. Handlers subscribed during a publish must **not** run in that same publish. A handler unsubscribed during a publish (and not yet called) must **not** run. Nested publishes run immediately (depth first). Your implementation mustn't crash or invalidate iterators in these cases.

The driver builds several lambda handlers with different capture styles (by value, by reference, init-capture with a `unique_ptr`-free counter, `mutable`) and runs a script.

## Starter
```cpp
#include <functional>
#include <string>
#include <map>
#include <vector>

class EventBus {
public:
    using Handler = std::function<void(const std::string&)>;
    int subscribe(const std::string& topic, Handler h) {
        subs_[topic].push_back(std::move(h));
        return 0;
    }
    bool unsubscribe(int id) { return false; }
    int publish(const std::string& topic, const std::string& payload) {
        int n = 0;
        for (auto& h : subs_[topic]) { h(payload); ++n; }
        return n;
    }
    std::size_t handler_count(const std::string& topic) const {
        auto it = subs_.find(topic);
        return it == subs_.end() ? 0 : it->second.size();
    }
private:
    std::map<std::string, std::vector<Handler>> subs_;
};
```

## Driver
```cpp
#include <iostream>
#include <sstream>

int main() {
    EventBus bus;
    std::ostringstream log;
    int total_len = 0;                                               // captured by reference
    std::string prefix = "imu";
    int id_print = bus.subscribe("sensor", [prefix, &log](const std::string& p) {   // by value + by reference
        log << "[" << prefix << "] " << p << '\n';
    });
    prefix = "CHANGED";                                              // must not affect the copy above
    bus.subscribe("sensor", [&total_len](const std::string& p) { total_len += static_cast<int>(p.size()); });
    bus.subscribe("sensor", [count = 0, &log](const std::string&) mutable {         // stateful handler
        ++count;
        log << "count=" << count << '\n';
    });
    int id_once = 0;
    id_once = bus.subscribe("alarm", [&](const std::string& p) {    // unsubscribes itself, then publishes
        log << "ALARM " << p << " (once)\n";
        bus.unsubscribe(id_once);
        bus.publish("sensor", "from-alarm");
    });
    bus.subscribe("alarm", [&](const std::string& p) {              // subscribes a new handler mid-publish
        log << "alarm-2 " << p << '\n';
        bus.subscribe("alarm", [&log](const std::string& q) { log << "late " << q << '\n'; });
    });
    int id_victim = 0;
    bus.subscribe("chain", [&](const std::string&) { log << "chain-1 removes victim\n"; bus.unsubscribe(id_victim); });
    id_victim = bus.subscribe("chain", [&](const std::string&) { log << "victim ran (WRONG)\n"; });

    std::string cmd, topic, payload;
    while (std::cin >> cmd) {
        if (cmd == "pub") {
            std::cin >> topic >> payload;
            int n = bus.publish(topic, payload);
            log << "pub " << topic << " -> " << n << " handler(s)\n";
        } else if (cmd == "unsub") {
            int id; std::cin >> id;
            log << "unsub " << id << ' ' << (bus.unsubscribe(id) ? "ok" : "unknown") << '\n';
        } else if (cmd == "count") {
            std::cin >> topic;
            log << "count " << topic << ' ' << bus.handler_count(topic) << '\n';
        }
    }
    std::cout << log.str() << "total_len=" << total_len << " first_id=" << id_print << '\n';
}
```

## Tests
=== sample
pub sensor hello
pub alarm fire
pub alarm smoke
count alarm
pub chain x
pub chain y
unsub 1
pub sensor bye
unsub 1
unsub 42
pub nobody hi
---
[imu] hello
count=1
pub sensor -> 3 handler(s)
ALARM fire (once)
[imu] from-alarm
count=2
alarm-2 fire
pub alarm -> 2 handler(s)
alarm-2 smoke
late smoke
pub alarm -> 2 handler(s)
count alarm 3
chain-1 removes victim
pub chain -> 1 handler(s)
chain-1 removes victim
pub chain -> 1 handler(s)
unsub 1 ok
count=3
pub sensor -> 2 handler(s)
unsub 1 unknown
unsub 42 unknown
pub nobody -> 0 handler(s)
total_len=18 first_id=1
=== hidden
count sensor
pub sensor a
pub sensor bb
pub sensor ccc
unsub 3
pub sensor dddd
count chain
pub chain z
pub alarm q
pub alarm r
---
count sensor 3
[imu] a
count=1
pub sensor -> 3 handler(s)
[imu] bb
count=2
pub sensor -> 3 handler(s)
[imu] ccc
count=3
pub sensor -> 3 handler(s)
unsub 3 ok
[imu] dddd
pub sensor -> 2 handler(s)
count chain 2
chain-1 removes victim
pub chain -> 1 handler(s)
ALARM q (once)
[imu] from-alarm
alarm-2 q
pub alarm -> 2 handler(s)
alarm-2 r
late r
pub alarm -> 2 handler(s)
total_len=20 first_id=1

## Hints
- Store a `std::vector` of `{id, alive, handler}` records per topic, plus a map `id → topic` for `unsubscribe`.
- In `publish`, first note `n = current size of the topic's vector`, then loop by **index** up to `n`. Index-based access is safe even if a handler appends to the vector, which can reallocate, but indices stay valid. New subscribers sit at positions ≥ n, so they don't run.
- `unsubscribe` only marks a record dead (`alive = false`). Compact dead records at the end of the **outermost** publish (track the nesting depth), never while a loop over that vector might be running.
- Don't call `vec[i].fn(...)` directly: a nested `subscribe` can reallocate the vector while that handler runs, destroying the closure mid-call. Don't call a *copy* either: a `mutable` stateful lambda would update the copy's state, which is then lost. Store each handler as `std::shared_ptr<Handler>`, copy the `shared_ptr` (which keeps the one closure alive), and call through it.

## Solution
```cpp
#include <functional>
#include <string>
#include <map>
#include <unordered_map>
#include <vector>
#include <algorithm>
#include <memory>

class EventBus {
public:
    using Handler = std::function<void(const std::string&)>;

    int subscribe(const std::string& topic, Handler h) {
        int id = next_id_++;
        subs_[topic].push_back({id, true, std::make_shared<Handler>(std::move(h))});
        topic_of_[id] = topic;
        return id;
    }

    bool unsubscribe(int id) {
        auto t = topic_of_.find(id);
        if (t == topic_of_.end()) return false;
        for (auto& s : subs_[t->second])
            if (s.id == id) s.alive = false;      // mark only: a publish loop may be running
        topic_of_.erase(t);
        dirty_ = true;
        return true;
    }

    int publish(const std::string& topic, const std::string& payload) {
        auto it = subs_.find(topic);
        if (it == subs_.end()) return 0;
        ++depth_;
        int ran = 0;
        std::size_t n = it->second.size();        // handlers added during this publish are not called
        for (std::size_t i = 0; i < n; ++i) {
            auto& vec = subs_[topic];             // re-fetch: nested calls may have reallocated it
            if (!vec[i].alive) continue;
            auto h = vec[i].fn;                   // copy the shared_ptr, not the closure: state persists,
            (*h)(payload);                        // and the closure survives a reallocation during the call
            ++ran;
        }
        if (--depth_ == 0 && dirty_) compact();
        return ran;
    }

    std::size_t handler_count(const std::string& topic) const {
        auto it = subs_.find(topic);
        if (it == subs_.end()) return 0;
        return static_cast<std::size_t>(std::count_if(it->second.begin(), it->second.end(),
                                                      [](const Sub& s) { return s.alive; }));
    }

private:
    struct Sub { int id; bool alive; std::shared_ptr<Handler> fn; };

    void compact() {
        for (auto& [topic, vec] : subs_)
            std::erase_if(vec, [](const Sub& s) { return !s.alive; });
        dirty_ = false;
    }

    std::map<std::string, std::vector<Sub>> subs_;
    std::unordered_map<int, std::string> topic_of_;
    int next_id_ = 1;
    int depth_ = 0;
    bool dirty_ = false;
};
```

**The lambda lessons in the driver:**
- `[prefix, &log]` copies `prefix` at subscription time, so changing `prefix` afterwards doesn't affect the handler. It also references the shared log.
- `[count = 0, &log](...) mutable` is a **stateful** callback: its counter lives inside the closure object, which `std::function` stores.
- `[&]` handlers capture the bus and ids by reference. That's safe here only because everything lives in `main` and outlives the bus.

**The re-entrancy lessons in the bus:**
- Snapshot the count, iterate by index, and re-fetch the vector, because a nested `subscribe` may reallocate it.
- **Shared ownership of each closure** (`shared_ptr<Handler>`): the publish loop holds its own reference while calling, so a reallocation can't destroy the running handler, and a `mutable` lambda's state persists because there's only ever one closure object. Copying the `std::function` instead would silently fork the state (every call would see `count=1`).
- **Tombstones plus deferred compaction:** never erase from a vector that an outer loop is iterating. This is the observer-pattern pitfall behind many real crashes in GUI toolkits and game engines.
