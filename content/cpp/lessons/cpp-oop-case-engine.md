# Case Study: Event-Driven Simulation Engine

Simulators are how robotics teams test fleets of robots, networks and warehouses before touching hardware. Their core is a **discrete-event simulation (DES)** engine: instead of advancing time in fixed steps, it jumps from one event to the next, which is hugely efficient when events are sparse. This final case study designs a small but professional DES kernel in modern C++:
- a priority-queue scheduler with deterministic ordering;
- events as values with `std::variant`;
- handlers as type-erased callbacks;
- cancellation via handles;
- entities that schedule future events.

## 1. The DES model

- **Simulation time** is a number (seconds, as an integer number of milliseconds or a double), advanced only by the engine.
- An **event** is a timestamp plus a payload, such as "robot 3 arrives at shelf 17".
- The **event queue** is a min-heap ordered by `(time, sequence number)`. The sequence number makes simultaneous events run in **insertion order**, so runs are reproducible, which is essential for debugging and regression tests.
- **Processing an event** may schedule new future events. The loop pops the earliest event, sets `now`, dispatches it, and repeats until the queue is empty or the end time is reached.

```cpp
struct Arrive { int robot, shelf; };
struct PickDone { int robot; };
struct BatteryLow { int robot; };
using Payload = std::variant<Arrive, PickDone, BatteryLow>;

struct Scheduled {
    double time;
    std::uint64_t seq;               // tie-breaker: FIFO among equal times
    std::uint64_t id;                // for cancellation
    Payload payload;
};
struct Later {
    bool operator()(const Scheduled& a, const Scheduled& b) const {
        return a.time != b.time ? a.time > b.time : a.seq > b.seq;    // min-heap via std::priority_queue
    }
};
```

## 2. Dispatch: variant plus visitor

```cpp
class Simulator {
public:
    std::uint64_t schedule(double delay, Payload p);
    bool cancel(std::uint64_t id);                    // lazy: mark it, skip it when popped
    void run_until(double end);
    double now() const { return now_; }
    template <class E> void on(std::function<void(Simulator&, const E&)> h) {
        handlers_[Payload(std::in_place_type<E>).index()].push_back(
            [h = std::move(h)](Simulator& s, const Payload& p) { h(s, std::get<E>(p)); });
    }
private:
    std::priority_queue<Scheduled, std::vector<Scheduled>, Later> q_;
    std::unordered_set<std::uint64_t> cancelled_;
    std::vector<std::vector<std::function<void(Simulator&, const Payload&)>>> handlers_ =
        std::vector<std::vector<std::function<void(Simulator&, const Payload&)>>>(std::variant_size_v<Payload>);
    double now_ = 0;
    std::uint64_t seq_ = 0, next_id_ = 1;
};
```

Handlers are registered per event type and stored type-erased in `std::function`s, indexed by the variant's alternative index. Adding a new event type means adding it to the variant, and the compiler then flags any `std::visit` that misses it.

**Lazy cancellation**: removing an arbitrary element from a binary heap is awkward, so `cancel` records the id, and the loop discards cancelled events when they surface. That's O(1) to cancel and O(log n) per pop. The same trick appears in timer wheels and the `asyncio` loop.

## 3. Entities and processes

Robots are entities with state (position, battery, current task). They react to events and schedule follow-ups:

```cpp
sim.on<Arrive>([&](Simulator& s, const Arrive& e) {
    auto& r = robots[e.robot];
    r.at = e.shelf;
    s.schedule(pick_time(e.shelf), PickDone{e.robot});      // the process continues in the future
});
sim.on<PickDone>([&](Simulator& s, const PickDone& e) {
    auto& r = robots[e.robot];
    r.picks++;
    r.battery -= 0.02;
    if (r.battery < 0.2) s.schedule(0, BatteryLow{e.robot});
    else s.schedule(travel_time(r.at, next_shelf(r)), Arrive{e.robot, next_shelf(r)});
});
```

## 4. Determinism and statistics

- Use one seeded random-number generator (`std::mt19937_64`), owned by the simulation, for reproducible stochastic runs. Different seeds give independent replications, so you can compute confidence intervals.
- Collect **time-weighted** statistics (utilisation = busy time / total time) by integrating state over event intervals, not by sampling.
- Validate with simple cases that have analytic answers, such as an M/M/1 queue's mean waiting time, before trusting complex scenarios.

## 5. Design review against this module

- **Value types**: events and timestamps are values, cheap to copy and comparable.
- **Ownership**: the simulator owns its queue and handlers, and entities are owned by the scenario. Handlers capture references to entities that outlive the run.
- **Open/closed**: new behaviours register handlers without editing the engine.
- **Testability**: everything is deterministic, so tests assert exact event sequences.

> [!EXAM]
> **Why does a discrete-event simulator order its queue by (time, sequence number), and how is event cancellation implemented efficiently?**
> The queue must release events in time order. When several events share a timestamp, their relative order would otherwise depend on heap internals, making runs irreproducible, so a monotonically increasing sequence number assigned at scheduling time breaks ties in FIFO order and makes every run deterministic. Cancelling an arbitrary element inside a binary heap is costly (it requires finding and re-heapifying), so simulators cancel lazily: `cancel(id)` records the id in a set, and the run loop silently discards popped events whose ids are marked. That's O(1) per cancellation and amortised O(log n) per pop.

## Worked example: the event loop at the heart of a DES

A discrete-event simulation keeps a **priority queue of future events**, always processes the earliest one next, and lets each event schedule more events:

```cpp
#include <functional>
#include <iostream>
#include <queue>
#include <string>
#include <vector>

struct Event {
    double time;
    long seq;                                   // tie-breaker: FIFO for equal times
    std::function<void()> action;
    bool operator>(const Event& o) const { return time != o.time ? time > o.time : seq > o.seq; }
};

class Simulator {
    std::priority_queue<Event, std::vector<Event>, std::greater<>> q_;
    long seq_ = 0;
public:
    double now = 0;
    void schedule(double delay, std::function<void()> f) { q_.push({now + delay, seq_++, std::move(f)}); }
    void run(double until) {
        while (!q_.empty() && q_.top().time <= until) {
            Event e = q_.top(); q_.pop();
            now = e.time;                        // jump straight to the next event
            e.action();
        }
    }
};

int main() {
    Simulator sim;
    int served = 0;
    std::function<void(int)> arrive = [&](int id) {
        std::cout << "t=" << sim.now << " customer " << id << " arrives\n";
        sim.schedule(1.5, [&, id] { ++served; std::cout << "t=" << sim.now << " customer " << id << " served\n"; });
        if (id < 3) sim.schedule(1.0, [&, id] { arrive(id + 1); });
    };
    sim.schedule(0, [&] { arrive(1); });
    sim.run(10);
    std::cout << served << " served\n";
}
```

```output
t=0 customer 1 arrives
t=1 customer 2 arrives
t=1.5 customer 1 served
t=2 customer 3 arrives
t=2.5 customer 2 served
t=3.5 customer 3 served
3 served
```

- **Time jumps** from event to event (0 → 1 → 1.5 → 2 ...). Nothing is simulated between events.
- **The `seq` tie-breaker** makes runs deterministic: two events at the same time always run in scheduling order.
- **The case study** replaces `std::function` with a `std::variant` of event types plus a visitor, so events are inspectable data rather than opaque callbacks.

## Common mistakes

- **Ticking a clock in fixed small steps.** That's slow, and it rounds event times.
- **No tie-breaker.** Equal-time events then pop in an unspecified order, so results differ between runs.
- **Capturing loop variables or locals by reference** in scheduled lambdas that run later. Capture by value.

## Check your understanding

1. Why use `std::greater<>` with the priority queue?
2. How would you collect "average waiting time"?

<details><summary>Answers</summary>

1. `std::priority_queue` is a max-heap by default. With `greater`, the earliest event is on top.
2. Record each customer's arrival time. When service starts, add `now - arrival` to a running sum and count, then divide at the end.

</details>
