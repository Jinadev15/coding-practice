---
id: cpp-m4-pubsub-middleware
title: A Typed In-Process Pub/Sub Middleware (ROS-Style)
difficulty: Expert
order: 3
tags: type erasure, templates, std::type_index, RAII, weak_ptr, queues, executors, middleware design
time_limit: 4
---
## Statement
Capstone: build the in-process core of a robotics middleware, a miniature `rclcpp` with typed topics, bounded queues with keep-last QoS, latched (transient-local) topics, RAII subscriptions, timers and a single-threaded executor on simulated time.

**`class Bus`**
- **`template <class T> Publisher<T> advertise(const std::string& topic, std::size_t depth = 10, bool latched = false)`**.
- **`template <class T> Subscription<T> subscribe(const std::string& topic, std::function<void(const T&)> cb, std::size_t depth = 10)`**.
  - Using a topic with a **different message type** than its first use throws `std::logic_error("type mismatch on topic <name>")`.
  - On a **latched** topic, a new subscriber immediately gets the last published message **queued** (delivered at the next spin).
- **`Publisher<T>::publish(const T&)`** copies the message into every live subscriber's queue. A full queue **drops its oldest** message (keep-last) and counts it in `bus.dropped(topic)`. It also has `subscriber_count()`.
- **`std::size_t spin_some()`**: for each subscription **in creation order**, deliver the messages that were queued **when spin_some started** (FIFO). Messages published by callbacks during the spin wait for the next spin. Returns the number of callbacks run.
- **Timers**: `add_timer(period, cb)` first fires at `now + period`. `spin_until(t)` processes the timer firings with time `<= t` in time order (ties go to the earliest-added timer): set `now` to the firing time, call `cb`, then `spin_some()`. Finally `now = t` (it never goes backwards). Returns the total number of callbacks, timers plus subscriptions.
- `now()` and `dropped(topic)`.

**`Subscription<T>`** is move-only and **RAII**: destroying it (or calling `reset()`) unsubscribes immediately and discards its pending messages. A publisher or subscription that outlives the `Bus` must be safe to use and destroy: publishing becomes a no-op.

## Starter
```cpp
#include <functional>
#include <map>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

template <class T> class Publisher;
template <class T> class Subscription { public: void reset() {} };

class Bus {
public:
    template <class T> Publisher<T> advertise(const std::string& topic, std::size_t = 10, bool = false) { return Publisher<T>(this, topic); }
    template <class T> Subscription<T> subscribe(const std::string& topic, std::function<void(const T&)> cb, std::size_t = 10) {
        callbacks_[topic].push_back([cb](const void* m) { cb(*static_cast<const T*>(m)); });
        return {};
    }
    std::size_t spin_some() { return 0; }
    void add_timer(double, std::function<void()>) {}
    std::size_t spin_until(double t) { now_ = t; return 0; }
    double now() const { return now_; }
    std::size_t dropped(const std::string&) const { return 0; }
    std::map<std::string, std::vector<std::function<void(const void*)>>> callbacks_;
private:
    double now_ = 0;
};

template <class T> class Publisher {                 // delivers synchronously, ignores types and queues
public:
    Publisher(Bus* b, std::string t) : bus_(b), topic_(std::move(t)) {}
    void publish(const T& m) { for (auto& cb : bus_->callbacks_[topic_]) cb(&m); }
    std::size_t subscriber_count() const { return bus_->callbacks_[topic_].size(); }
private:
    Bus* bus_; std::string topic_;
};
```

## Driver
```cpp
#include <cstdio>
#include <iostream>
#include <optional>

struct Twist { double v, w; };
struct Scan { int seq; double range; };

int main() {
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "basic") {
            Bus bus;
            std::vector<std::string> log;
            auto pub = bus.advertise<Twist>("cmd_vel", 3);
            auto s1 = bus.subscribe<Twist>("cmd_vel", [&](const Twist& t) { log.push_back("A" + std::to_string((int)(t.v * 10))); });
            auto s2 = bus.subscribe<Twist>("cmd_vel", [&](const Twist& t) { log.push_back("B" + std::to_string((int)(t.v * 10))); }, 2);
            std::printf("subscribers %zu\n", pub.subscriber_count());
            for (int i = 1; i <= 4; ++i) pub.publish({i * 0.1, 0});
            std::printf("before spin %zu delivered so far\n", log.size());
            std::size_t n = bus.spin_some();
            std::printf("spin %zu:", n); for (auto& l : log) std::printf(" %s", l.c_str()); std::printf("\n");
            std::size_t dr = bus.dropped("cmd_vel"), second = bus.spin_some();
            std::printf("dropped %zu, second spin %zu\n", dr, second);
            try { bus.subscribe<Scan>("cmd_vel", [](const Scan&) {}); } catch (const std::logic_error& e) { std::printf("error: %s\n", e.what()); }
            try { bus.advertise<Scan>("cmd_vel"); } catch (const std::logic_error& e) { std::printf("error: %s\n", e.what()); }
            log.clear();
            pub.publish({0.9, 0});
            s2.reset();
            std::size_t subs_now = pub.subscriber_count(), sp = bus.spin_some();
            std::printf("after reset subscribers %zu, spin %zu:", subs_now, sp); for (auto& l : log) std::printf(" %s", l.c_str()); std::printf("\n");
            { auto tmp = bus.subscribe<Twist>("cmd_vel", [](const Twist&) {}); std::printf("scoped subscribers %zu\n", pub.subscriber_count()); }
            std::printf("after scope %zu\n", pub.subscriber_count());
            Subscription<Twist> moved = std::move(s1);
            pub.publish({0.5, 0}); log.clear(); bus.spin_some();
            std::printf("moved subscription still active: %zu\n", log.size());
        } else if (cmd == "latched") {
            Bus bus;
            auto map_pub = bus.advertise<Scan>("map", 1, true);
            map_pub.publish({1, 1.0}); map_pub.publish({2, 2.0});
            std::vector<int> got;
            auto late = bus.subscribe<Scan>("map", [&](const Scan& s) { got.push_back(s.seq); });
            std::size_t before = got.size(), spun = bus.spin_some();
            std::printf("late joiner before spin %zu, spin %zu, got", before, spun); for (int g : got) std::printf(" %d", g); std::printf("\n");
            auto normal = bus.advertise<Scan>("scan");
            normal.publish({5, 5});
            std::vector<int> g2;
            auto late2 = bus.subscribe<Scan>("scan", [&](const Scan& s) { g2.push_back(s.seq); });
            bus.spin_some();
            std::printf("non-latched late joiner got %zu\n", g2.size());
        } else if (cmd == "executor") {
            Bus bus;
            std::vector<std::string> log;
            auto scan_pub = bus.advertise<Scan>("scan");
            auto cmd_pub = bus.advertise<Twist>("cmd");
            int seq = 0;
            auto ctrl = bus.subscribe<Scan>("scan", [&](const Scan& s) {
                log.push_back("ctrl@" + std::to_string(bus.now()).substr(0, 4) + "#" + std::to_string(s.seq));
                cmd_pub.publish({s.range < 1.0 ? 0.0 : 0.5, 0});
            });
            auto motors = bus.subscribe<Twist>("cmd", [&](const Twist& t) { log.push_back("motor v=" + std::to_string(t.v).substr(0, 3)); });
            bus.add_timer(0.1, [&] { scan_pub.publish({++seq, seq % 3 == 0 ? 0.5 : 2.0}); });
            bus.add_timer(0.25, [&] { log.push_back("health@" + std::to_string(bus.now()).substr(0, 4)); });
            std::size_t n = bus.spin_until(0.5);
            std::printf("callbacks %zu now %.2f\n", n, bus.now());
            for (auto& l : log) std::printf("  %s\n", l.c_str());
            log.clear();
            std::size_t left = bus.spin_some();
            std::printf("leftover spin %zu, motors logged %zu\n", left, log.size());
            std::size_t rew = bus.spin_until(0.3);
            std::printf("no rewind: %zu now %.2f\n", rew, bus.now());
        } else if (cmd == "lifetime") {
            std::optional<Publisher<Twist>> pub;
            std::optional<Subscription<Twist>> sub;
            {
                Bus bus;
                pub.emplace(bus.advertise<Twist>("x"));
                sub.emplace(bus.subscribe<Twist>("x", [](const Twist&) {}));
                pub->publish({1, 1});
            }
            pub->publish({2, 2});
            std::printf("publish after bus destroyed ok, subscribers %zu\n", pub->subscriber_count());
            sub.reset(); pub.reset();
            std::printf("clean teardown\n");
        } else if (cmd == "load") {
            Bus bus;
            long total = 0;
            std::vector<Publisher<Scan>> pubs;
            std::vector<Subscription<Scan>> subs;
            for (int t = 0; t < 20; ++t) {
                pubs.push_back(bus.advertise<Scan>("t" + std::to_string(t), 50));
                for (int k = 0; k < 5; ++k) subs.push_back(bus.subscribe<Scan>("t" + std::to_string(t), [&total](const Scan& s) { total += s.seq; }, 8 + k * 10));
            }
            std::size_t cbs = 0;
            for (int round = 0; round < 2000; ++round) {
                for (int t = 0; t < 20; ++t) for (int m = 0; m < 1 + (round + t) % 25; ++m) pubs[t].publish({m, 0});
                cbs += bus.spin_some();
            }
            std::size_t dropped = 0; for (int t = 0; t < 20; ++t) dropped += bus.dropped("t" + std::to_string(t));
            std::printf("callbacks %zu total %ld dropped %zu\n", cbs, total, dropped);
        }
    }
}
```

## Tests
=== sample
basic
---
subscribers 2
before spin 0 delivered so far
spin 6: A1 A2 A3 A4 B3 B4
dropped 2, second spin 0
error: type mismatch on topic cmd_vel
error: type mismatch on topic cmd_vel
after reset subscribers 1, spin 1: A9
scoped subscribers 2
after scope 1
moved subscription still active: 1
=== hidden
latched
---
late joiner before spin 0, spin 1, got 2
non-latched late joiner got 0
=== hidden
executor
---
callbacks 17 now 0.50
  ctrl@0.10#1
  ctrl@0.20#2
  motor v=0.5
  health@0.25
  motor v=0.5
  ctrl@0.30#3
  ctrl@0.40#4
  motor v=0.0
  ctrl@0.50#5
  motor v=0.5
  health@0.50
  motor v=0.5
leftover spin 0, motors logged 0
no rewind: 0 now 0.50
=== hidden
lifetime
---
publish after bus destroyed ok, subscribers 0
clean teardown
=== hidden
load
---
callbacks 2310400 total 19404800 dropped 289600

## Hints
- Type erasure: the bus keeps `std::map<std::string, std::shared_ptr<TopicBase>>`, where `TopicBase` stores `std::type_index` and a drop counter, and `Topic<T> : TopicBase` holds a list of subscriber records and the latched message. `advertise` and `subscribe` check `typeid(T)` against the stored index.
- A subscriber record: `{ std::uint64_t order; std::size_t depth; std::deque<T> queue; std::function<void(const T&)> cb; bool alive; }`, held by `shared_ptr`. The `Subscription<T>` keeps a `weak_ptr` to its record and to the topic, and its destructor removes the record.
- `spin_some`: gather all live records across topics, sort them by creation order, snapshot each queue's current size, and pop and deliver that many messages.
- Publishers and subscriptions hold `weak_ptr`s, so when the `Bus` (and its topics) die they simply find nothing to do.

## Solution
```cpp
#include <algorithm>
#include <cstdint>
#include <deque>
#include <functional>
#include <map>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <typeindex>
#include <vector>

namespace detail {
struct RecordBase {
    std::uint64_t order = 0;
    bool alive = true;
    virtual ~RecordBase() = default;
    virtual std::size_t queued() const = 0;
    virtual void deliver_one() = 0;
};

template <class T>
struct Record : RecordBase {
    std::size_t depth = 10;
    std::deque<T> queue;
    std::function<void(const T&)> cb;
    std::size_t queued() const override { return queue.size(); }
    void deliver_one() override {
        T msg = std::move(queue.front());
        queue.pop_front();
        cb(msg);
    }
};

struct TopicBase {
    explicit TopicBase(std::type_index t) : type(t) {}
    virtual ~TopicBase() = default;
    virtual void collect(std::vector<std::shared_ptr<RecordBase>>& out) const = 0;
    std::type_index type;
    std::size_t dropped = 0;
};

template <class T>
struct Topic : TopicBase {
    Topic() : TopicBase(typeid(T)) {}
    std::vector<std::shared_ptr<Record<T>>> subs;
    bool latched = false;
    std::optional<T> last;
    void push(Record<T>& r, const T& m) {
        if (r.queue.size() >= r.depth) { r.queue.pop_front(); ++dropped; }   // keep-last QoS
        r.queue.push_back(m);
    }
    void collect(std::vector<std::shared_ptr<RecordBase>>& out) const override {
        for (const auto& s : subs) if (s->alive) out.push_back(s);
    }
};
}  // namespace detail

template <class T>
class Publisher {
public:
    explicit Publisher(std::weak_ptr<detail::Topic<T>> t) : topic_(std::move(t)) {}
    void publish(const T& m) {
        auto t = topic_.lock();
        if (!t) return;                                       // the bus is gone: no-op
        if (t->latched) t->last = m;
        for (auto& r : t->subs) if (r->alive) t->push(*r, m);
    }
    std::size_t subscriber_count() const {
        auto t = topic_.lock();
        if (!t) return 0;
        return static_cast<std::size_t>(std::count_if(t->subs.begin(), t->subs.end(), [](auto& r) { return r->alive; }));
    }
private:
    std::weak_ptr<detail::Topic<T>> topic_;
};

template <class T>
class Subscription {
public:
    Subscription() = default;
    Subscription(std::weak_ptr<detail::Topic<T>> t, std::weak_ptr<detail::Record<T>> r) : topic_(std::move(t)), rec_(std::move(r)) {}
    Subscription(Subscription&& o) noexcept : topic_(std::move(o.topic_)), rec_(std::move(o.rec_)) {}
    Subscription& operator=(Subscription&& o) noexcept {
        if (this != &o) { reset(); topic_ = std::move(o.topic_); rec_ = std::move(o.rec_); }
        return *this;
    }
    Subscription(const Subscription&) = delete;
    Subscription& operator=(const Subscription&) = delete;
    ~Subscription() { reset(); }

    void reset() {
        auto t = topic_.lock();
        auto r = rec_.lock();
        if (t && r) {
            r->alive = false;
            r->queue.clear();
            std::erase(t->subs, r);
        }
        topic_.reset();
        rec_.reset();
    }
private:
    std::weak_ptr<detail::Topic<T>> topic_;
    std::weak_ptr<detail::Record<T>> rec_;
};

class Bus {
public:
    template <class T>
    Publisher<T> advertise(const std::string& name, std::size_t depth = 10, bool latched = false) {
        (void)depth;
        auto t = topic<T>(name);
        if (latched) t->latched = true;
        return Publisher<T>(t);
    }

    template <class T>
    Subscription<T> subscribe(const std::string& name, std::function<void(const T&)> cb, std::size_t depth = 10) {
        auto t = topic<T>(name);
        auto r = std::make_shared<detail::Record<T>>();
        r->order = next_order_++;
        r->depth = depth;
        r->cb = std::move(cb);
        if (t->latched && t->last) t->push(*r, *t->last);   // transient-local: replay the last message
        t->subs.push_back(r);
        return Subscription<T>(t, r);
    }

    std::size_t spin_some() {
        std::vector<std::shared_ptr<detail::RecordBase>> recs;
        for (auto& [_, t] : topics_) t->collect(recs);
        std::sort(recs.begin(), recs.end(), [](auto& a, auto& b) { return a->order < b->order; });
        std::vector<std::size_t> budget;
        for (auto& r : recs) budget.push_back(r->queued());   // snapshot: messages published now wait
        std::size_t n = 0;
        for (std::size_t i = 0; i < recs.size(); ++i)
            for (std::size_t k = 0; k < budget[i] && recs[i]->alive && recs[i]->queued() > 0; ++k) {
                recs[i]->deliver_one();
                ++n;
            }
        return n;
    }

    void add_timer(double period, std::function<void()> cb) {
        timers_.push_back({period, now_ + period, timers_.size(), std::move(cb)});
    }

    std::size_t spin_until(double t) {
        std::size_t n = 0;
        for (;;) {
            Timer* next = nullptr;
            for (auto& tm : timers_)
                if (tm.next <= t + 1e-12 && (!next || tm.next < next->next - 1e-12)) next = &tm;
            if (!next) break;
            now_ = next->next;
            next->next += next->period;
            next->cb();
            ++n;
            n += spin_some();
        }
        if (t > now_) now_ = t;
        return n;
    }

    double now() const { return now_; }
    std::size_t dropped(const std::string& name) const {
        auto it = topics_.find(name);
        return it == topics_.end() ? 0 : it->second->dropped;
    }

private:
    template <class T>
    std::shared_ptr<detail::Topic<T>> topic(const std::string& name) {
        auto it = topics_.find(name);
        if (it == topics_.end()) {
            auto t = std::make_shared<detail::Topic<T>>();
            topics_.emplace(name, t);
            return t;
        }
        if (it->second->type != std::type_index(typeid(T))) throw std::logic_error("type mismatch on topic " + name);
        return std::static_pointer_cast<detail::Topic<T>>(it->second);
    }

    struct Timer { double period, next; std::size_t order; std::function<void()> cb; };
    std::map<std::string, std::shared_ptr<detail::TopicBase>> topics_;
    std::vector<Timer> timers_;
    std::uint64_t next_order_ = 0;
    double now_ = 0;
};
```

- **Type erasure with a runtime check**: topics live in one map behind `TopicBase`, but every typed access compares `std::type_index`, so publishing a `Scan` on a `Twist` topic is a clear `logic_error`, not memory corruption. That's the job ROS's type support performs across processes.
- **Keep-last QoS**: bounded per-subscriber queues drop the oldest message under load and count the drops. A slow consumer then sees fresh data instead of an ever-growing backlog, which is right for sensor streams.
- **Latched (transient-local) topics** replay the last message to late joiners. That's how ROS publishes maps and robot descriptions.
- **RAII subscriptions and weak ownership**: destroying a `Subscription` unsubscribes immediately. Publishers and subscriptions hold `weak_ptr`s, so they can outlive the `Bus` safely, which is the lifetime rule `rclcpp` users hit constantly.
- **A deterministic executor**: callbacks run in creation order, messages published during a spin wait for the next one (no unbounded recursion), and timers fire in simulated time order. That makes multi-node behaviour reproducible in tests, like ROS 2's single-threaded executor driven by sim time.
