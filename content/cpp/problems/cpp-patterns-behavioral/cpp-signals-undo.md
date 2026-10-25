---
id: cpp-signals-undo
title: Safe Signals and an Undoable Command History
difficulty: Hard
order: 1
tags: observer, RAII, weak_ptr, command, undo/redo, composite command, templates
time_limit: 4
---
## Statement
A robot-arm teach pendant needs undo/redo, and its UI widgets subscribe to history changes. Implement two behavioural patterns.

**Part A: `template <typename... Args> class Signal`** (Observer):
- `[[nodiscard]] Connection connect(std::function<void(Args...)> slot)`.
- `void emit(Args... args)` calls the live slots **in connection order**. A slot connected *during* an emit isn't called by that emit. A slot disconnected during an emit, before its turn comes, is **not** called.
- `std::size_t size() const`: the number of live connections.
- `Signal::Connection` is **move-only RAII**: its destructor disconnects. It has `disconnect()` (idempotent) and `bool connected() const`. A default-constructed or moved-from connection is disconnected. A connection must be safe to destroy, or disconnect, **after its Signal is gone**.

**Part B: commands** on `struct Arm { std::vector<double> q; };` (given):
- `Command` interface: `bool execute(Arm&)`, `void undo(Arm&)`, `std::string name() const`.
- `MoveJoint(int j, double target)`:
  - `execute` fails (returns false, changes nothing) when `j` is out of range or `|target| > π` (`std::numbers::pi`). Otherwise it remembers the old value and sets the new one.
  - `undo` restores the old value.
  - `name()` is `std::format("j{}={}", j, target)`.
- `Macro(std::string name, std::vector<std::unique_ptr<Command>> steps)`:
  - Executes the steps in order. If one fails, it undoes the already-executed steps **in reverse** and returns false.
  - `undo` runs in reverse order.
  - `name()` is the given name.
- `History(std::size_t max_depth)`:
  - `bool run(std::unique_ptr<Command>, Arm&)`: a failed command is discarded, and history (including redo) is untouched. On success it's pushed onto the undo stack, the redo stack is cleared, and if the undo stack exceeds `max_depth` the **oldest** entry is dropped.
  - `bool undo(Arm&)` and `bool redo(Arm&)` return false when there's nothing to do.
  - `std::size_t undo_depth() const` and `redo_depth() const`.
  - A public member `Signal<const std::string&> changed;` emits `"do <name>"`, `"undo <name>"` or `"redo <name>"` after each successful operation.

## Starter
```cpp
#include <format>
#include <functional>
#include <memory>
#include <numbers>
#include <string>
#include <vector>

template <typename... Args>
class Signal {
public:
    using Slot = std::function<void(Args...)>;
    class Connection {
    public:
        void disconnect() {}
        bool connected() const { return true; }
    };
    Connection connect(Slot s) { slots_.push_back(std::move(s)); return {}; }
    void emit(Args... args) { for (auto& s : slots_) s(args...); }
    std::size_t size() const { return slots_.size(); }
private:
    std::vector<Slot> slots_;
};

struct Arm { std::vector<double> q; };

struct Command {
    virtual ~Command() = default;
    virtual bool execute(Arm& a) = 0;
    virtual void undo(Arm& a) = 0;
    virtual std::string name() const = 0;
};

class MoveJoint : public Command {
public:
    MoveJoint(int j, double target) : j_(j), t_(target) {}
    bool execute(Arm& a) override { a.q[j_] = t_; return true; }
    void undo(Arm& a) override { a.q[j_] = 0; }
    std::string name() const override { return "move"; }
private:
    int j_; double t_;
};

class Macro : public Command {
public:
    Macro(std::string n, std::vector<std::unique_ptr<Command>> s) : n_(std::move(n)), s_(std::move(s)) {}
    bool execute(Arm& a) override { for (auto& c : s_) c->execute(a); return true; }
    void undo(Arm& a) override { for (auto& c : s_) c->undo(a); }
    std::string name() const override { return n_; }
private:
    std::string n_; std::vector<std::unique_ptr<Command>> s_;
};

class History {
public:
    explicit History(std::size_t max_depth) {}
    bool run(std::unique_ptr<Command> c, Arm& a) { return c->execute(a); }
    bool undo(Arm& a) { return false; }
    bool redo(Arm& a) { return false; }
    std::size_t undo_depth() const { return 0; }
    std::size_t redo_depth() const { return 0; }
    Signal<const std::string&> changed;
};
```

## Driver
```cpp
#include <cstdio>
#include <iostream>

static void arm(const Arm& a) {
    std::printf("[");
    for (std::size_t i = 0; i < a.q.size(); ++i) std::printf("%s%.2f", i ? " " : "", a.q[i] + 0.0);
    std::printf("]");
}
static std::unique_ptr<Command> mv(int j, double t) { return std::make_unique<MoveJoint>(j, t); }

int main() {
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "signal") {
            Signal<int> s;
            std::string log;
            auto c1 = s.connect([&](int v) { log += std::format("a{} ", v); });
            Signal<int>::Connection c2 = s.connect([&](int v) { log += std::format("b{} ", v); });
            {
                auto c3 = s.connect([&](int v) { log += std::format("c{} ", v); });
                s.emit(1);
                std::printf("size in scope %zu\n", s.size());
            }
            s.emit(2);
            c1.disconnect(); c1.disconnect();
            s.emit(3);
            std::printf("%s| size %zu c1 %d c2 %d\n", log.c_str(), s.size(), c1.connected(), c2.connected());
            Signal<int>::Connection moved = std::move(c2);
            std::printf("moved: src %d dst %d size %zu\n", c2.connected(), moved.connected(), s.size());
            Signal<int>::Connection none;
            std::printf("default %d\n", none.connected());
        } else if (cmd == "reentrant") {
            Signal<> s;
            std::string log;
            Signal<>::Connection late, victim, self;
            auto first = s.connect([&] {
                log += "first ";
                if (!late.connected()) late = s.connect([&] { log += "late "; });
                victim.disconnect();
            });
            victim = s.connect([&] { log += "victim "; });
            self = s.connect([&] { log += "self "; self.disconnect(); });
            s.emit(); log += "| "; s.emit(); log += "| "; s.emit();
            std::printf("%s size %zu\n", log.c_str(), s.size());
            Signal<>::Connection survivor;
            {
                Signal<> temp;
                survivor = temp.connect([] {});
                std::printf("temp size %zu\n", temp.size());
            }
            std::printf("after signal died: %d\n", survivor.connected());
            survivor.disconnect();
        } else if (cmd == "history") {
            Arm a{{0, 0, 0}};
            History h(10);
            std::vector<std::string> events;
            auto conn = h.changed.connect([&](const std::string& e) { events.push_back(e); });
            std::printf("run %d ", h.run(mv(0, 1.0), a)); arm(a); std::printf("\n");
            std::printf("run %d ", h.run(mv(1, -0.5), a)); arm(a); std::printf("\n");
            std::printf("bad joint %d bad angle %d ", h.run(mv(5, 0.1), a), h.run(mv(2, 3.5), a)); arm(a); std::printf("\n");
            std::printf("undo %d ", h.undo(a)); arm(a); std::printf("\n");
            std::printf("undo %d ", h.undo(a)); arm(a); std::printf("\n");
            std::printf("undo %d ", h.undo(a)); arm(a); std::printf("\n");
            std::printf("redo %d ", h.redo(a)); arm(a); std::printf(" depths %zu/%zu\n", h.undo_depth(), h.redo_depth());
            std::printf("failed run keeps redo: %d depths %zu/%zu\n", h.run(mv(9, 0), a), h.undo_depth(), h.redo_depth());
            std::printf("run %d ", h.run(mv(2, 2.0), a)); arm(a); std::printf(" depths %zu/%zu\n", h.undo_depth(), h.redo_depth());
            std::printf("redo %d\n", h.redo(a));
            for (auto& e : events) std::printf("%s; ", e.c_str());
            std::printf("\n");
        } else if (cmd == "macro") {
            Arm a{{0.1, 0.2, 0.3}};
            History h(10);
            std::vector<std::unique_ptr<Command>> steps;
            steps.push_back(mv(0, 1)); steps.push_back(mv(1, 2)); steps.push_back(mv(0, -1));
            std::printf("macro %d ", h.run(std::make_unique<Macro>("wave", std::move(steps)), a)); arm(a); std::printf("\n");
            std::printf("undo %d ", h.undo(a)); arm(a); std::printf("\n");
            std::vector<std::unique_ptr<Command>> bad;
            bad.push_back(mv(2, 1.5)); bad.push_back(mv(1, -2)); bad.push_back(mv(7, 0));
            std::printf("failing macro %d ", h.run(std::make_unique<Macro>("bad", std::move(bad)), a)); arm(a);
            std::printf(" depths %zu/%zu\n", h.undo_depth(), h.redo_depth());
            std::vector<std::unique_ptr<Command>> inner, outer;
            inner.push_back(mv(1, 1)); inner.push_back(mv(2, 1));
            outer.push_back(mv(0, 0.5)); outer.push_back(std::make_unique<Macro>("inner", std::move(inner)));
            std::printf("nested %d ", h.run(std::make_unique<Macro>("outer", std::move(outer)), a)); arm(a); std::printf("\n");
            h.undo(a); std::printf("undo "); arm(a); std::printf("\n");
            h.redo(a); std::printf("redo "); arm(a); std::printf("\n");
        } else if (cmd == "depth") {
            Arm a{{0, 0}};
            History h(3);
            std::string log;
            {
                auto c = h.changed.connect([&](const std::string& e) { log += e + ","; });
                for (int i = 1; i <= 5; ++i) h.run(mv(i % 2, i * 0.5), a);
            }
            h.run(mv(0, 3.0), a);
            int undos = 0;
            while (h.undo(a)) ++undos;
            std::printf("undos %d ", undos); arm(a); std::printf(" log %s\n", log.c_str());
            History big(1000);
            Arm b{std::vector<double>(6, 0.0)};
            long events = 0;
            auto c = big.changed.connect([&](const std::string&) { ++events; });
            for (int i = 0; i < 20000; ++i) big.run(mv(i % 6, ((i * 37) % 600) / 100.0 - 3.0), b);
            for (int i = 0; i < 1500; ++i) big.undo(b);
            for (int i = 0; i < 300; ++i) big.redo(b);
            arm(b); std::printf(" depths %zu/%zu events %ld\n", big.undo_depth(), big.redo_depth(), events);
        }
    }
}
```

## Tests
=== sample
signal
history
---
size in scope 3
a1 b1 c1 a2 b2 b3 | size 1 c1 0 c2 1
moved: src 0 dst 1 size 1
default 0
run 1 [1.00 0.00 0.00]
run 1 [1.00 -0.50 0.00]
bad joint 0 bad angle 0 [1.00 -0.50 0.00]
undo 1 [1.00 0.00 0.00]
undo 1 [0.00 0.00 0.00]
undo 0 [0.00 0.00 0.00]
redo 1 [1.00 0.00 0.00] depths 1/1
failed run keeps redo: 0 depths 1/1
run 1 [1.00 0.00 2.00] depths 2/0
redo 0
do j0=1; do j1=-0.5; undo j1=-0.5; undo j0=1; redo j0=1; do j2=2; 
=== hidden
reentrant
---
first self | first late | first late  size 2
temp size 1
after signal died: 0
=== hidden
macro
---
macro 1 [-1.00 2.00 0.30]
undo 1 [0.10 0.20 0.30]
failing macro 0 [0.10 0.20 0.30] depths 0/1
nested 1 [0.50 1.00 1.00]
undo [0.10 0.20 0.30]
redo [0.50 1.00 1.00]
=== hidden
depth
---
undos 3 [1.00 1.50] log do j1=0.5,do j0=1,do j1=1.5,do j0=2,do j1=2.5,
[2.52 2.89 -2.74 -2.37 1.78 2.15] depths 300/700 events 21300

## Hints
- Store slots as `std::shared_ptr<Entry>`, where `Entry` holds the `std::function` and an `alive` flag, in a `std::shared_ptr<std::vector<...>>` owned by the Signal. Connections keep a `std::weak_ptr` to the entry.
- `emit`: copy the vector of entry pointers first (so new connections aren't called), then call each entry **only if still alive** at its turn.
- Disconnecting marks the entry dead and erases it from the live list. If the Signal (and its list) is gone, the `weak_ptr`s simply fail to lock.
- History: a `std::deque<std::unique_ptr<Command>>` for undo (`pop_front` when too deep) and a vector for redo.

## Solution
```cpp
#include <algorithm>
#include <cmath>
#include <deque>
#include <format>
#include <functional>
#include <memory>
#include <numbers>
#include <string>
#include <utility>
#include <vector>

template <typename... Args>
class Signal {
public:
    using Slot = std::function<void(Args...)>;
private:
    struct Entry { Slot fn; bool alive = true; };
    using List = std::vector<std::shared_ptr<Entry>>;
public:
    class Connection {
    public:
        Connection() = default;
        Connection(std::weak_ptr<List> list, std::weak_ptr<Entry> e) : list_(std::move(list)), entry_(std::move(e)) {}
        Connection(Connection&& o) noexcept : list_(std::move(o.list_)), entry_(std::move(o.entry_)) {}
        Connection& operator=(Connection&& o) noexcept {
            if (this != &o) { disconnect(); list_ = std::move(o.list_); entry_ = std::move(o.entry_); }
            return *this;
        }
        Connection(const Connection&) = delete;
        Connection& operator=(const Connection&) = delete;
        ~Connection() { disconnect(); }

        void disconnect() {
            auto e = entry_.lock();
            auto l = list_.lock();
            if (e && l) {
                e->alive = false;
                std::erase(*l, e);
            }
            entry_.reset();
            list_.reset();
        }
        bool connected() const {
            auto e = entry_.lock();
            return e && e->alive && !list_.expired();
        }
    private:
        std::weak_ptr<List> list_;
        std::weak_ptr<Entry> entry_;
    };

    [[nodiscard]] Connection connect(Slot s) {
        auto e = std::make_shared<Entry>(Entry{std::move(s)});
        slots_->push_back(e);
        return Connection(slots_, e);
    }

    void emit(Args... args) {
        const List snapshot = *slots_;                // slots added during emit are not called
        for (const auto& e : snapshot)
            if (e->alive) e->fn(args...);             // skip slots disconnected mid-emit
    }

    std::size_t size() const { return slots_->size(); }

private:
    std::shared_ptr<List> slots_ = std::make_shared<List>();
};

struct Arm { std::vector<double> q; };

struct Command {
    virtual ~Command() = default;
    virtual bool execute(Arm& a) = 0;
    virtual void undo(Arm& a) = 0;
    virtual std::string name() const = 0;
};

class MoveJoint : public Command {
public:
    MoveJoint(int j, double target) : j_(j), t_(target) {}
    bool execute(Arm& a) override {
        if (j_ < 0 || static_cast<std::size_t>(j_) >= a.q.size() || std::abs(t_) > std::numbers::pi) return false;
        prev_ = a.q[j_];
        a.q[j_] = t_;
        return true;
    }
    void undo(Arm& a) override { a.q[j_] = prev_; }
    std::string name() const override { return std::format("j{}={}", j_, t_); }
private:
    int j_;
    double t_, prev_ = 0;
};

class Macro : public Command {                        // composite command
public:
    Macro(std::string n, std::vector<std::unique_ptr<Command>> s) : n_(std::move(n)), s_(std::move(s)) {}
    bool execute(Arm& a) override {
        for (std::size_t i = 0; i < s_.size(); ++i) {
            if (!s_[i]->execute(a)) {
                while (i-- > 0) s_[i]->undo(a);       // roll back what already ran, newest first
                return false;
            }
        }
        return true;
    }
    void undo(Arm& a) override {
        for (auto it = s_.rbegin(); it != s_.rend(); ++it) (*it)->undo(a);
    }
    std::string name() const override { return n_; }
private:
    std::string n_;
    std::vector<std::unique_ptr<Command>> s_;
};

class History {
public:
    explicit History(std::size_t max_depth) : max_(max_depth) {}

    bool run(std::unique_ptr<Command> c, Arm& a) {
        if (!c || !c->execute(a)) return false;       // failed commands leave history untouched
        std::string n = c->name();
        done_.push_back(std::move(c));
        redo_.clear();                                // a new action invalidates the redo future
        while (done_.size() > max_) done_.pop_front();
        changed.emit("do " + n);
        return true;
    }
    bool undo(Arm& a) {
        if (done_.empty()) return false;
        auto c = std::move(done_.back());
        done_.pop_back();
        c->undo(a);
        std::string n = c->name();
        redo_.push_back(std::move(c));
        changed.emit("undo " + n);
        return true;
    }
    bool redo(Arm& a) {
        if (redo_.empty()) return false;
        auto c = std::move(redo_.back());
        redo_.pop_back();
        if (!c->execute(a)) return false;
        std::string n = c->name();
        done_.push_back(std::move(c));
        while (done_.size() > max_) done_.pop_front();
        changed.emit("redo " + n);
        return true;
    }
    std::size_t undo_depth() const { return done_.size(); }
    std::size_t redo_depth() const { return redo_.size(); }

    Signal<const std::string&> changed;

private:
    std::size_t max_;
    std::deque<std::unique_ptr<Command>> done_;
    std::vector<std::unique_ptr<Command>> redo_;
};
```

- **RAII connections** make the observer's lifetime control its subscription. The widget (or lambda owner) holds the `Connection`, and destroying it unsubscribes, so a dead observer can never be called.
- **`weak_ptr` in both directions of uncertainty**: a connection outliving its signal finds the list expired and does nothing. A signal never keeps observers alive.
- **Re-entrancy rules** are explicit and safe: emit iterates a snapshot, so new slots wait for the next emit and the list can be modified mid-iteration. The `alive` flag skips slots disconnected before their turn, which is exactly what you want when one handler tears down another.
- **Commands carry their own undo data** (`prev_`), captured at execute time, so undo is exact even after other commands have run.
- **The Macro is a composite command** with transactional semantics. A failing step rolls back the steps before it, so a half-executed motion sequence never stays in effect.
- **History invariants**: failures change nothing, a new action clears redo, and depth is bounded (the oldest entry is dropped, so memory is constant for long teach sessions). Observers hear about every state change through the signal.
