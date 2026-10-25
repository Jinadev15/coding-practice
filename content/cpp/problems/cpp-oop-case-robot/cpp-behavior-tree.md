---
id: cpp-behavior-tree
title: "Case Study: A Behavior Tree Engine"
difficulty: Expert
order: 1
tags: composite pattern, decorators, NVI, std::function, std::any, robotics architecture
time_limit: 4
---
## Statement
Implement the decision-making engine from the case-study lesson: a **behavior tree** like those driving Nav2 and BehaviorTree.CPP.

```cpp
enum class Status { Success, Failure, Running };
```

**`Blackboard`**: a typed key-value store.
- `template <class T> void set(const std::string& key, T value)`.
- `template <class T> std::optional<T> get(const std::string& key) const`: nullopt if the key is missing **or holds a different type**.
- `bool has(const std::string&) const`.

**`Node`** (abstract, non-copyable, uses the NVI pattern):
- `Status tick(Blackboard&)` calls the private `on_tick`, records the result as `status()`, and increments `ticks()`.
- `virtual void halt(Blackboard&)`: if the node is currently `Running`, it stops its running work (see each node). In every case it resets its internal progress, and `status()` becomes `Failure`.
- `const std::string& name() const`.

**Leaves:**
- `Condition(name, std::function<bool(const Blackboard&)>)` returns Success or Failure. It's never Running.
- `Action(name, std::function<Status(Blackboard&)> fn, std::function<void(Blackboard&)> on_halt = {})`: `halt` calls `on_halt` **only if the action was Running**.

**Composites** (`add(std::unique_ptr<Node>)` returns `*this` for chaining; children are owned):
- `Sequence` (with memory): resume from the child that returned Running. A Failure resets progress and returns Failure. Success after the last child resets progress.
- `ReactiveSequence`: restart from the **first** child on every tick. When a child returns Running, **halt every later child**, then return Running. On Failure, halt all children and return Failure.
- `Fallback` (with memory): resume at the remembered child. Return Success on the first Success (and reset), Running when a child is Running, and Failure once all have failed (and reset).

**Decorators** (each owns one child):
- `Inverter(name, child)` swaps Success and Failure, and passes Running through.
- `Retry(name, attempts, child)`: if the child fails, tick it again **within the same tick**, for at most `attempts` failures in total, and Fail after that. Running passes through and keeps the count. Success resets the count.

Halting a composite or decorator halts its children.

## Starter
```cpp
#include <any>
#include <functional>
#include <memory>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

enum class Status { Success, Failure, Running };

class Blackboard {
public:
    template <class T> void set(const std::string& k, T v) { data_[k] = std::move(v); }
    template <class T> std::optional<T> get(const std::string& k) const { return std::any_cast<T>(data_.at(k)); }
    bool has(const std::string& k) const { return data_.count(k); }
private:
    std::unordered_map<std::string, std::any> data_;
};

class Node {
public:
    explicit Node(std::string n) : name_(std::move(n)) {}
    virtual ~Node() = default;
    Status tick(Blackboard& bb) { return on_tick(bb); }
    virtual void halt(Blackboard&) {}
    const std::string& name() const { return name_; }
    Status status() const { return Status::Failure; }
    unsigned ticks() const { return 0; }
private:
    virtual Status on_tick(Blackboard& bb) = 0;
    std::string name_;
};

class Condition : public Node {
public:
    Condition(std::string n, std::function<bool(const Blackboard&)> f) : Node(std::move(n)), f_(std::move(f)) {}
private:
    Status on_tick(Blackboard& bb) override { return f_(bb) ? Status::Success : Status::Failure; }
    std::function<bool(const Blackboard&)> f_;
};

class Action : public Node {
public:
    Action(std::string n, std::function<Status(Blackboard&)> f, std::function<void(Blackboard&)> h = {}) : Node(std::move(n)), f_(std::move(f)) { (void)h; }
private:
    Status on_tick(Blackboard& bb) override { return f_(bb); }
    std::function<Status(Blackboard&)> f_;
};

class Sequence : public Node {
public:
    using Node::Node;
    Sequence& add(std::unique_ptr<Node> c) { kids_.push_back(std::move(c)); return *this; }
private:
    Status on_tick(Blackboard& bb) override {
        for (auto& k : kids_) { Status s = k->tick(bb); if (s != Status::Success) return s; }
        return Status::Success;
    }
    std::vector<std::unique_ptr<Node>> kids_;
};

using ReactiveSequence = Sequence;
using Fallback = Sequence;

class Inverter : public Node {
public:
    Inverter(std::string n, std::unique_ptr<Node> c) : Node(std::move(n)), c_(std::move(c)) {}
private:
    Status on_tick(Blackboard& bb) override { return c_->tick(bb); }
    std::unique_ptr<Node> c_;
};

class Retry : public Node {
public:
    Retry(std::string n, int attempts, std::unique_ptr<Node> c) : Node(std::move(n)), c_(std::move(c)) { (void)attempts; }
private:
    Status on_tick(Blackboard& bb) override { return c_->tick(bb); }
    std::unique_ptr<Node> c_;
};
```

## Driver
```cpp
#include <cstdio>
#include <iostream>

static const char* S(Status s) { return s == Status::Success ? "SUCCESS" : s == Status::Failure ? "FAILURE" : "RUNNING"; }
static std::vector<std::string> trace;

/* an action that runs for `n` ticks then returns `result`; records ticks and halts */
static std::unique_ptr<Action> timed(const std::string& name, int n, Status result) {
    auto left = std::make_shared<int>(n);
    return std::make_unique<Action>(name,
        [name, left, n, result](Blackboard&) {
            trace.push_back(name);
            if (--*left > 0) return Status::Running;
            *left = n;
            return result;
        },
        [name, left, n](Blackboard&) { trace.push_back("halt:" + name); *left = n; });
}
static std::unique_ptr<Condition> flag(const std::string& key) {
    return std::make_unique<Condition>("?" + key, [key](const Blackboard& bb) { trace.push_back("?" + key); return bb.get<bool>(key).value_or(false); });
}
static void run(Node& root, Blackboard& bb, int ticks, const char* label) {
    for (int i = 0; i < ticks; ++i) {
        trace.clear();
        Status s = root.tick(bb);
        std::printf("%s t%d %s:", label, i, S(s));
        for (auto& t : trace) std::printf(" %s", t.c_str());
        std::printf("\n");
    }
}

int main() {
    std::string cmd;
    while (std::cin >> cmd) {
        Blackboard bb;
        if (cmd == "blackboard") {
            bb.set("battery", 0.42); bb.set<std::string>("goal", "dock"); bb.set("count", 3);
            std::printf("battery %.2f goal %s count %d\n", bb.get<double>("battery").value(), bb.get<std::string>("goal")->c_str(), *bb.get<int>("count"));
            std::printf("wrong type %d missing %d has %d %d\n", bb.get<int>("battery").has_value(), bb.get<double>("nope").has_value(), bb.has("goal"), bb.has("nope"));
            bb.set("count", 4); std::printf("overwrite %d\n", *bb.get<int>("count"));
        } else if (cmd == "sequence") {
            Sequence seq("patrol");
            seq.add(timed("A", 1, Status::Success)).add(timed("B", 3, Status::Success)).add(timed("C", 1, Status::Success));
            run(seq, bb, 5, "seq");
            std::printf("ticks %u status %s\n", seq.ticks(), S(seq.status()));
            Sequence fail("fail");
            fail.add(timed("X", 1, Status::Success)).add(timed("Y", 2, Status::Failure)).add(timed("Z", 1, Status::Success));
            run(fail, bb, 3, "fail");
        } else if (cmd == "fallback") {
            Fallback fb("dock-or-patrol");
            auto low = std::make_unique<Sequence>("low-battery");
            low->add(flag("battery_low")).add(timed("GoToDock", 2, Status::Success));
            fb.add(std::move(low)).add(timed("Patrol", 3, Status::Running));
            run(fb, bb, 2, "fb");
            bb.set("battery_low", true);
            run(fb, bb, 4, "fb");
            Fallback allfail("all-fail");
            allfail.add(timed("P", 1, Status::Failure)).add(timed("Q", 1, Status::Failure));
            run(allfail, bb, 2, "allfail");
        } else if (cmd == "reactive") {
            ReactiveSequence rs("move-safely");
            rs.add(std::make_unique<Inverter>("not-obstacle", flag("obstacle"))).add(timed("MoveTo", 4, Status::Success));
            run(rs, bb, 2, "rs");
            bb.set("obstacle", true);
            run(rs, bb, 1, "rs");
            bb.set("obstacle", false);
            run(rs, bb, 4, "rs");
            Sequence memory("memory-seq");
            memory.add(std::make_unique<Inverter>("not-obstacle", flag("obstacle"))).add(timed("MoveTo2", 3, Status::Success));
            run(memory, bb, 1, "mem");
            bb.set("obstacle", true);
            run(memory, bb, 2, "mem");
        } else if (cmd == "decorators") {
            auto attempts = std::make_shared<int>(0);
            Retry r("retry3", 3, std::make_unique<Action>("Grasp", [attempts](Blackboard&) {
                trace.push_back("Grasp#" + std::to_string(++*attempts));
                return *attempts == 3 ? Status::Success : Status::Failure;
            }));
            run(r, bb, 1, "retry");
            *attempts = -10;
            run(r, bb, 1, "retry");
            Retry rr("retry-running", 2, timed("Slow", 2, Status::Failure));
            run(rr, bb, 3, "rr");
            Inverter inv("inv", timed("Busy", 2, Status::Success));
            run(inv, bb, 2, "inv");
            Sequence root("halt-test");
            root.add(timed("Long", 5, Status::Success));
            run(root, bb, 2, "halt");
            trace.clear(); root.halt(bb);
            std::printf("after halt:"); for (auto& t : trace) std::printf(" %s", t.c_str()); std::printf(" status %s\n", S(root.status()));
            trace.clear(); root.halt(bb);
            std::printf("halt idle: %zu events\n", trace.size());
            run(root, bb, 1, "restart");
        } else if (cmd == "stress") {
            auto root = std::make_unique<Fallback>("root");
            long work = 0;
            for (int b = 0; b < 50; ++b) {
                auto seq = std::make_unique<ReactiveSequence>("branch" + std::to_string(b));
                seq->add(std::make_unique<Condition>("c", [b](const Blackboard& bb) { return bb.get<int>("mode").value_or(0) % 50 == b; }));
                seq->add(std::make_unique<Action>("w", [&work](Blackboard&) { return ++work % 3 ? Status::Running : Status::Success; }));
                root->add(std::move(seq));
            }
            int succ = 0, running = 0;
            for (int t = 0; t < 20000; ++t) {
                bb.set("mode", t / 7);
                Status s = root->tick(bb);
                succ += s == Status::Success; running += s == Status::Running;
            }
            std::printf("success %d running %d work %ld root ticks %u\n", succ, running, work, root->ticks());
        }
    }
}
```

## Tests
=== sample
blackboard
sequence
---
battery 0.42 goal dock count 3
wrong type 0 missing 0 has 1 0
overwrite 4
seq t0 RUNNING: A B
seq t1 RUNNING: B
seq t2 SUCCESS: B C
seq t3 RUNNING: A B
seq t4 RUNNING: B
ticks 5 status RUNNING
fail t0 RUNNING: X Y
fail t1 FAILURE: Y
fail t2 RUNNING: X Y
=== hidden
fallback
---
fb t0 RUNNING: ?battery_low Patrol
fb t1 RUNNING: Patrol
fb t0 RUNNING: Patrol
fb t1 RUNNING: Patrol
fb t2 RUNNING: Patrol
fb t3 RUNNING: Patrol
allfail t0 FAILURE: P Q
allfail t1 FAILURE: P Q
=== hidden
reactive
---
rs t0 RUNNING: ?obstacle MoveTo
rs t1 RUNNING: ?obstacle MoveTo
rs t0 FAILURE: ?obstacle halt:MoveTo
rs t0 RUNNING: ?obstacle MoveTo
rs t1 RUNNING: ?obstacle MoveTo
rs t2 RUNNING: ?obstacle MoveTo
rs t3 SUCCESS: ?obstacle MoveTo
mem t0 RUNNING: ?obstacle MoveTo2
mem t0 RUNNING: MoveTo2
mem t1 SUCCESS: MoveTo2
=== hidden
decorators
---
retry t0 SUCCESS: Grasp#1 Grasp#2 Grasp#3
retry t0 FAILURE: Grasp#-9 Grasp#-8 Grasp#-7
rr t0 RUNNING: Slow
rr t1 RUNNING: Slow Slow
rr t2 FAILURE: Slow
inv t0 RUNNING: Busy
inv t1 FAILURE: Busy
halt t0 RUNNING: Long
halt t1 RUNNING: Long
after halt: halt:Long status FAILURE
halt idle: 0 events
restart t0 RUNNING: Long
=== hidden
stress
---
success 6657 running 13314 work 19971 root ticks 20000

## Hints
- `Blackboard::get`: `auto it = data_.find(k); if (it == end) return nullopt; if (auto p = std::any_cast<T>(&it->second)) return *p; return nullopt;`. The pointer form of `any_cast` doesn't throw.
- `Node` stores `status_` and `ticks_`. The public non-virtual `tick` wraps the private virtual `on_tick`. `halt` checks `status_ == Running`, calls a protected virtual `on_halt` hook, then sets `status_ = Failure`.
- Composites keep `std::size_t current_`. `ReactiveSequence` ignores it when ticking, but must remember which child was running so it knows which later children to halt.
- `Retry`: `while (true) { s = child->tick(bb); if (s != Failure) break; if (++failures_ >= attempts_) { failures_ = 0; return Failure; } }`.

## Solution
```cpp
#include <any>
#include <functional>
#include <memory>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

enum class Status { Success, Failure, Running };

class Blackboard {
public:
    template <class T> void set(const std::string& k, T v) { data_[k] = std::move(v); }
    template <class T> std::optional<T> get(const std::string& k) const {
        auto it = data_.find(k);
        if (it == data_.end()) return std::nullopt;
        if (const T* p = std::any_cast<T>(&it->second)) return *p;
        return std::nullopt;                                     // wrong type: no exception
    }
    bool has(const std::string& k) const { return data_.find(k) != data_.end(); }
private:
    std::unordered_map<std::string, std::any> data_;
};

class Node {
public:
    explicit Node(std::string n) : name_(std::move(n)) {}
    Node(const Node&) = delete;
    Node& operator=(const Node&) = delete;
    virtual ~Node() = default;

    Status tick(Blackboard& bb) {                                // NVI: bookkeeping in one place
        status_ = on_tick(bb);
        ++ticks_;
        return status_;
    }
    void halt(Blackboard& bb) {
        if (status_ == Status::Running) on_halt(bb);
        reset();
        status_ = Status::Failure;
    }
    const std::string& name() const { return name_; }
    Status status() const { return status_; }
    unsigned ticks() const { return ticks_; }

protected:
    virtual void on_halt(Blackboard&) {}                         // stop running work
    virtual void reset() {}                                       // forget internal progress

private:
    virtual Status on_tick(Blackboard& bb) = 0;
    std::string name_;
    Status status_ = Status::Failure;
    unsigned ticks_ = 0;
};

class Condition : public Node {
public:
    Condition(std::string n, std::function<bool(const Blackboard&)> f) : Node(std::move(n)), f_(std::move(f)) {}
private:
    Status on_tick(Blackboard& bb) override { return f_(bb) ? Status::Success : Status::Failure; }
    std::function<bool(const Blackboard&)> f_;
};

class Action : public Node {
public:
    Action(std::string n, std::function<Status(Blackboard&)> f, std::function<void(Blackboard&)> h = {})
        : Node(std::move(n)), f_(std::move(f)), h_(std::move(h)) {}
private:
    Status on_tick(Blackboard& bb) override { return f_(bb); }
    void on_halt(Blackboard& bb) override { if (h_) h_(bb); }
    std::function<Status(Blackboard&)> f_;
    std::function<void(Blackboard&)> h_;
};

class Composite : public Node {
public:
    using Node::Node;
protected:
    void add_child(std::unique_ptr<Node> c) { kids_.push_back(std::move(c)); }
    void halt_from(Blackboard& bb, std::size_t first) {
        for (std::size_t i = first; i < kids_.size(); ++i) kids_[i]->halt(bb);
    }
    void on_halt(Blackboard& bb) override { halt_from(bb, 0); }
    void reset() override { current_ = 0; }
    std::vector<std::unique_ptr<Node>> kids_;
    std::size_t current_ = 0;
};

class Sequence : public Composite {
public:
    using Composite::Composite;
    Sequence& add(std::unique_ptr<Node> c) { add_child(std::move(c)); return *this; }
private:
    Status on_tick(Blackboard& bb) override {
        while (current_ < kids_.size()) {
            Status s = kids_[current_]->tick(bb);
            if (s == Status::Running) return s;                  // resume here next tick
            if (s == Status::Failure) { current_ = 0; return s; }
            ++current_;
        }
        current_ = 0;
        return Status::Success;
    }
};

class ReactiveSequence : public Composite {
public:
    using Composite::Composite;
    ReactiveSequence& add(std::unique_ptr<Node> c) { add_child(std::move(c)); return *this; }
private:
    Status on_tick(Blackboard& bb) override {
        for (std::size_t i = 0; i < kids_.size(); ++i) {         // always restart from the first child
            Status s = kids_[i]->tick(bb);
            if (s == Status::Running) { halt_from(bb, i + 1); return s; }
            if (s == Status::Failure) { halt_from(bb, 0); return s; }
        }
        return Status::Success;
    }
};

class Fallback : public Composite {
public:
    using Composite::Composite;
    Fallback& add(std::unique_ptr<Node> c) { add_child(std::move(c)); return *this; }
private:
    Status on_tick(Blackboard& bb) override {
        while (current_ < kids_.size()) {
            Status s = kids_[current_]->tick(bb);
            if (s == Status::Running) return s;
            if (s == Status::Success) { current_ = 0; return s; }
            ++current_;
        }
        current_ = 0;
        return Status::Failure;
    }
};

class Decorator : public Node {
public:
    Decorator(std::string n, std::unique_ptr<Node> c) : Node(std::move(n)), child_(std::move(c)) {}
protected:
    void on_halt(Blackboard& bb) override { child_->halt(bb); }
    std::unique_ptr<Node> child_;
};

class Inverter : public Decorator {
public:
    using Decorator::Decorator;
private:
    Status on_tick(Blackboard& bb) override {
        Status s = child_->tick(bb);
        return s == Status::Running ? s : s == Status::Success ? Status::Failure : Status::Success;
    }
};

class Retry : public Decorator {
public:
    Retry(std::string n, int attempts, std::unique_ptr<Node> c) : Decorator(std::move(n), std::move(c)), attempts_(attempts) {}
private:
    Status on_tick(Blackboard& bb) override {
        for (;;) {
            Status s = child_->tick(bb);
            if (s == Status::Running) return s;
            if (s == Status::Success) { failures_ = 0; return s; }
            if (++failures_ >= attempts_) { failures_ = 0; return Status::Failure; }
        }
    }
    void reset() override { failures_ = 0; }
    int attempts_, failures_ = 0;
};
```

- **The Composite pattern**: every node, leaf or container, offers the same `tick`/`halt` interface, so arbitrarily deep trees are built from the same few classes and owned top-down by `unique_ptr`.
- **NVI**: the base class's public `tick` and `halt` keep the status and tick counters and enforce the halt contract (only Running nodes get `on_halt`, and progress always resets). Subclasses implement just `on_tick`, `on_halt` and `reset`, so they can't forget the bookkeeping.
- **Memory vs reactive sequences** are a deliberate design choice. The memory `Sequence` doesn't re-check the obstacle condition while `MoveTo2` runs, while the `ReactiveSequence` re-evaluates it every tick and **halts** the running move the moment an obstacle appears. That's exactly the trade-off Nav2 exposes.
- **Decorators** add behaviour (inversion, retries) to any subtree without modifying it: the Decorator pattern applied to behaviour.
- **The typed blackboard** with `std::any` lets independent nodes share data without knowing each other's types. A wrong-type read returns `nullopt` instead of throwing in the middle of a control cycle.
