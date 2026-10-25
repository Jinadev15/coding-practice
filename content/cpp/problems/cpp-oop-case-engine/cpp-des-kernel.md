---
id: cpp-des-kernel
title: "Case Study: A Discrete-Event Simulation Kernel"
difficulty: Expert
order: 1
tags: variadic templates, std::variant, priority_queue, type erasure, determinism, simulation
time_limit: 4
---
## Statement
Build the generic core of a discrete-event simulator. Events are **values** in a `std::variant`, handlers are **type-erased** callbacks registered per event type, and the queue orders events deterministically.

`template <class... Events> class Simulator` with `using Payload = std::variant<Events...>`:

| Member | Contract |
|---|---|
| `std::uint64_t schedule(double delay, Payload p)` | Schedules at `now() + delay`. A negative delay throws `std::invalid_argument`. Returns a unique id (1, 2, 3, …). |
| `std::uint64_t schedule_at(double time, Payload p)` | `time < now()` throws `std::invalid_argument`. |
| `bool cancel(std::uint64_t id)` | True if the event was still pending. Cancelled events never run. |
| `template <class E> void on(std::function<void(Simulator&, const E&)> h)` | Several handlers per type are called in registration order. Events with no handler are processed silently. |
| `bool step()` | Process the next event (time, then **scheduling order** for ties). Sets `now()` to its time. False if nothing is pending. |
| `std::size_t run_until(double end)` | Processes all events with `time <= end` and returns how many. Afterwards `now() == end`, but never moves time backwards. |
| `std::size_t run()` | Until empty. |
| `double now() const`, `std::size_t pending() const` | `pending` counts non-cancelled events only. |

Handlers may schedule new events (including at the current time, which run later in the same pass) and cancel pending ones.

## Starter
```cpp
#include <cstdint>
#include <functional>
#include <stdexcept>
#include <variant>
#include <vector>

template <class... Events>
class Simulator {
public:
    using Payload = std::variant<Events...>;
    std::uint64_t schedule(double delay, Payload p) { q_.push_back({now_ + delay, std::move(p)}); return q_.size(); }
    std::uint64_t schedule_at(double t, Payload p) { q_.push_back({t, std::move(p)}); return q_.size(); }
    bool cancel(std::uint64_t) { return false; }
    template <class E> void on(std::function<void(Simulator&, const E&)>) {}
    bool step() { if (q_.empty()) return false; now_ = q_.back().t; q_.pop_back(); return true; }   // LIFO: wrong order
    std::size_t run_until(double end) { std::size_t n = 0; while (!q_.empty() && step()) ++n; now_ = end; return n; }
    std::size_t run() { std::size_t n = 0; while (step()) ++n; return n; }
    double now() const { return now_; }
    std::size_t pending() const { return q_.size(); }
private:
    struct Item { double t; Payload p; };
    std::vector<Item> q_;
    double now_ = 0;
};
```

## Driver
```cpp
#include <cstdio>
#include <iostream>
#include <string>

struct Arrive { int robot, shelf; };
struct PickDone { int robot; };
struct LowBattery { int robot; };
struct Tick {};
using Sim = Simulator<Arrive, PickDone, LowBattery, Tick>;

int main() {
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "order") {
            Sim s;
            std::vector<std::string> log;
            s.on<Arrive>([&](Sim& sim, const Arrive& e) { log.push_back("arrive r" + std::to_string(e.robot) + "@" + std::to_string(sim.now())); });
            s.on<Arrive>([&](Sim&, const Arrive& e) { log.push_back("  second handler s" + std::to_string(e.shelf)); });
            s.on<PickDone>([&](Sim& sim, const PickDone& e) { log.push_back("pick r" + std::to_string(e.robot) + "@" + std::to_string(sim.now())); });
            s.schedule(5, Arrive{1, 10}); s.schedule(2, PickDone{2}); s.schedule(5, PickDone{3}); s.schedule(2, Arrive{4, 11});
            auto id = s.schedule(3, PickDone{9});
            s.schedule(1, Tick{});
            std::size_t p0 = s.pending(); bool c1 = s.cancel(id); bool c2 = s.cancel(id); std::size_t p1 = s.pending();
            std::printf("pending %zu cancel %d again %d pending %zu\n", p0, c1, c2, p1);
            std::size_t done = s.run();
            std::printf("processed %zu now %.1f\n", done, s.now());
            for (auto& l : log) std::printf("%s\n", l.c_str());
            try { s.schedule(-1, Tick{}); } catch (const std::invalid_argument&) { std::printf("negative delay rejected\n"); }
            try { s.schedule_at(1.0, Tick{}); } catch (const std::invalid_argument&) { std::printf("past time rejected\n"); }
            bool st = s.step(); bool cu = s.cancel(999);
            std::printf("step on empty %d, cancel unknown %d\n", st, cu);
        } else if (cmd == "cascade") {
            Sim s;
            std::vector<std::string> log;
            std::uint64_t victim = 0;
            s.on<Arrive>([&](Sim& sim, const Arrive& e) {
                log.push_back("arrive " + std::to_string(e.robot) + " t=" + std::to_string((int)sim.now()));
                sim.schedule(0, PickDone{e.robot});                       // same-time follow-up
                if (e.robot == 1) sim.cancel(victim);
            });
            s.on<PickDone>([&](Sim& sim, const PickDone& e) {
                log.push_back("pick " + std::to_string(e.robot) + " t=" + std::to_string((int)sim.now()));
                if (e.robot < 3) sim.schedule(4, Arrive{e.robot + 1, 0});
            });
            s.schedule(1, Arrive{0, 0});
            victim = s.schedule(6, Arrive{99, 0});
            s.schedule(5, Arrive{50, 0});
            std::size_t n6 = s.run_until(6);
            std::printf("until 6: %zu now %.1f pending %zu\n", n6, s.now(), s.pending());
            std::size_t n3 = s.run_until(3);
            std::printf("until 3 (no rewind): %zu now %.1f\n", n3, s.now());
            std::size_t nr = s.run();
            std::printf("rest: %zu now %.1f\n", nr, s.now());
            for (auto& l : log) std::printf("%s\n", l.c_str());
        } else if (cmd == "warehouse") {
            Sim s;
            struct Robot { int shelf = 0; double battery = 1.0; int picks = 0; bool charging = false; };
            std::vector<Robot> robots(25);
            unsigned x = 12345;
            auto rnd = [&x]() { x = x * 1103515245u + 12345u; return (x >> 8) % 1000 / 1000.0; };
            long charges = 0;
            s.on<Arrive>([&](Sim& sim, const Arrive& e) { robots[e.robot].shelf = e.shelf; sim.schedule(2.0 + rnd() * 3.0, PickDone{e.robot}); });
            s.on<PickDone>([&](Sim& sim, const PickDone& e) {
                Robot& r = robots[e.robot];
                r.picks++; r.battery -= 0.03 + rnd() * 0.02;
                if (r.battery < 0.25) sim.schedule(0, LowBattery{e.robot});
                else sim.schedule(5.0 + rnd() * 20.0, Arrive{e.robot, (int)(rnd() * 400)});
            });
            s.on<LowBattery>([&](Sim& sim, const LowBattery& e) {
                charges++; robots[e.robot].battery = 1.0;
                sim.schedule(600.0, Arrive{e.robot, 0});
            });
            for (int i = 0; i < 25; ++i) s.schedule(rnd() * 10, Arrive{i, i});
            std::size_t n = s.run_until(36000);
            long picks = 0; for (auto& r : robots) picks += r.picks;
            std::printf("events %zu picks %ld charges %ld now %.1f pending %zu\n", n, picks, charges, s.now(), s.pending());
        }
    }
}
```

## Tests
=== sample
order
---
pending 6 cancel 1 again 0 pending 5
processed 5 now 5.0
pick r2@2.000000
arrive r4@2.000000
  second handler s11
arrive r1@5.000000
  second handler s10
pick r3@5.000000
negative delay rejected
past time rejected
step on empty 0, cancel unknown 0
=== hidden
cascade
---
until 6: 6 now 6.0 pending 1
until 3 (no rewind): 0 now 6.0
rest: 4 now 13.0
arrive 0 t=1
pick 0 t=1
arrive 50 t=5
arrive 1 t=5
pick 50 t=5
pick 1 t=5
arrive 2 t=9
pick 2 t=9
arrive 3 t=13
pick 3 t=13
=== hidden
warehouse
---
events 38138 picks 18589 charges 957 now 36000.0 pending 25

## Hints
- Queue item: `{double time; std::uint64_t seq; std::uint64_t id; Payload p;}` in a `std::priority_queue` whose comparator is `a.time != b.time ? a.time > b.time : a.seq > b.seq` (a min-heap with FIFO ties).
- Cancellation: keep `std::unordered_set<std::uint64_t>` of pending ids. `cancel` erases from it, and `step` skips popped items whose id is no longer pending.
- Handlers: `std::array<std::vector<std::function<void(Simulator&, const Payload&)>>, sizeof...(Events)>`. Index them by `variant` alternative index. Register by wrapping: `[h](Simulator& s, const Payload& p) { h(s, std::get<E>(p)); }`. Find the index of `E` with a small constexpr helper, or with `Payload(std::in_place_type<E>).index()` for default-constructible events.
- Pop the item **before** calling the handlers, because they may push new items into the queue.

## Solution
```cpp
#include <array>
#include <cstdint>
#include <functional>
#include <queue>
#include <stdexcept>
#include <type_traits>
#include <unordered_set>
#include <variant>
#include <vector>

template <class... Events>
class Simulator {
public:
    using Payload = std::variant<Events...>;

    std::uint64_t schedule(double delay, Payload p) {
        if (delay < 0) throw std::invalid_argument("negative delay");
        return push(now_ + delay, std::move(p));
    }
    std::uint64_t schedule_at(double time, Payload p) {
        if (time < now_) throw std::invalid_argument("cannot schedule in the past");
        return push(time, std::move(p));
    }
    bool cancel(std::uint64_t id) { return live_.erase(id) > 0; }           // lazy: skipped when popped

    template <class E>
    void on(std::function<void(Simulator&, const E&)> h) {
        handlers_[index_of<E>()].push_back([h = std::move(h)](Simulator& s, const Payload& p) { h(s, std::get<E>(p)); });
    }

    bool step() {
        while (!q_.empty()) {
            Item it = q_.top();
            q_.pop();                                    // pop first: handlers may schedule
            if (!live_.erase(it.id)) continue;           // cancelled
            now_ = it.time;
            for (auto& h : handlers_[it.payload.index()]) h(*this, it.payload);
            return true;
        }
        return false;
    }

    std::size_t run_until(double end) {
        std::size_t n = 0;
        for (;;) {
            drop_cancelled_top();
            if (q_.empty() || q_.top().time > end) break;
            if (step()) ++n;
        }
        if (end > now_) now_ = end;                      // never rewind time
        return n;
    }

    std::size_t run() { std::size_t n = 0; while (step()) ++n; return n; }
    double now() const { return now_; }
    std::size_t pending() const { return live_.size(); }

private:
    struct Item { double time; std::uint64_t seq, id; Payload payload; };
    struct Later {
        bool operator()(const Item& a, const Item& b) const { return a.time != b.time ? a.time > b.time : a.seq > b.seq; }
    };

    template <class E, std::size_t I = 0>
    static constexpr std::size_t index_of() {
        static_assert(I < sizeof...(Events), "event type not in this simulator");
        if constexpr (std::is_same_v<E, std::variant_alternative_t<I, Payload>>) return I;
        else return index_of<E, I + 1>();
    }

    std::uint64_t push(double t, Payload p) {
        std::uint64_t id = next_id_++;
        q_.push(Item{t, seq_++, id, std::move(p)});
        live_.insert(id);
        return id;
    }
    void drop_cancelled_top() { while (!q_.empty() && !live_.count(q_.top().id)) q_.pop(); }

    std::priority_queue<Item, std::vector<Item>, Later> q_;
    std::unordered_set<std::uint64_t> live_;
    std::array<std::vector<std::function<void(Simulator&, const Payload&)>>, sizeof...(Events)> handlers_;
    double now_ = 0;
    std::uint64_t seq_ = 0, next_id_ = 1;
};
```

- **Determinism**: the queue orders by `(time, sequence number)`, so simultaneous events run in scheduling order, and the same seed always produces the same history. That's essential for debugging simulations and for regression tests like the warehouse run.
- **Events are values**: `std::variant` holds them by value with no heap allocation or inheritance, and `index_of` resolves handler slots at compile time (an unknown event type is a `static_assert`, not a runtime error).
- **Type erasure for handlers**: `std::function` wrappers keyed by variant index let the engine store handlers for unrelated types uniformly. Adding an event type touches the type list, not the engine.
- **Lazy cancellation**: cancelling only removes the id from the live set (O(1)), and stale heap entries are discarded when they reach the top, which avoids an awkward arbitrary-delete in a binary heap.
- **Re-entrancy**: popping before dispatch means handlers can freely schedule follow-ups (even at the current time, as in the `cascade` test) or cancel pending events.
