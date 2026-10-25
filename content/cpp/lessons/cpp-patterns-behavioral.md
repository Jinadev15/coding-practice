# Behavioral Patterns in C++

Behavioral patterns describe **how objects communicate and divide responsibility**: who's notified when something changes, how requests are encapsulated and undone, how algorithms are swapped, and how behaviour changes with state. In modern C++ many of them shrink: `std::function` and lambdas replace single-method interfaces, `std::variant` with `std::visit` replaces the classic Visitor and State hierarchies, and RAII handles make subscriptions safe. This lesson covers Observer, Command (with undo and redo), Strategy, State, Template Method, Chain of Responsibility, Visitor and Mediator, with the lifetime pitfalls that make them hard in C++.

## 1. Observer, and the lifetime problem

A subject notifies registered observers about events: a battery monitor tells the UI, the logger and the planner when the charge drops.

```cpp
template <typename... Args>
class Signal {
public:
    using Slot = std::function<void(Args...)>;
    class Connection {                                       // RAII: disconnects on destruction
    public:
        Connection() = default;
        Connection(std::weak_ptr<std::map<int, Slot>> s, int id) : slots_(std::move(s)), id_(id) {}
        Connection(Connection&& o) noexcept : slots_(std::move(o.slots_)), id_(std::exchange(o.id_, -1)) {}
        Connection& operator=(Connection&& o) noexcept { disconnect(); slots_ = std::move(o.slots_); id_ = std::exchange(o.id_, -1); return *this; }
        ~Connection() { disconnect(); }
        void disconnect() { if (auto s = slots_.lock(); s && id_ >= 0) s->erase(id_); id_ = -1; }
    private:
        std::weak_ptr<std::map<int, Slot>> slots_;
        int id_ = -1;
    };
    [[nodiscard]] Connection connect(Slot s) { int id = next_++; slots_->emplace(id, std::move(s)); return {slots_, id}; }
    void emit(Args... args) const {
        auto snapshot = *slots_;                             // slots may disconnect during emit
        for (auto& [id, slot] : snapshot) slot(args...);
    }
private:
    std::shared_ptr<std::map<int, Slot>> slots_ = std::make_shared<std::map<int, Slot>>();
    int next_ = 0;
};
```

> [!DANGER]
> The classic C++ observer bug is a subject calling an observer that was **already destroyed**: a dangling `this` captured in a lambda. Make the subscription an RAII object owned by the observer, so it unsubscribes in its destructor. The `weak_ptr` lets a `Connection` outlive the `Signal` safely. Also guard against observers that subscribe or unsubscribe *during* notification, which here is handled by iterating a snapshot. This is the design of Boost.Signals2 and Qt's signals and slots, and the same problem as ROS subscriptions that must be stored as members.

## 2. Command: requests as objects, with undo

A Command wraps an action as an object: queue it, log it, send it, **undo** it.

```cpp
struct Command {
    virtual ~Command() = default;
    virtual void execute(Arm& arm) = 0;
    virtual void undo(Arm& arm) = 0;
    virtual std::string name() const = 0;
};

class MoveJoint : public Command {
public:
    MoveJoint(int j, double target) : j_(j), target_(target) {}
    void execute(Arm& a) override { prev_ = a.joint(j_); a.set_joint(j_, target_); }   // remember for undo
    void undo(Arm& a) override { a.set_joint(j_, prev_); }
    std::string name() const override { return "move j" + std::to_string(j_); }
private:
    int j_; double target_, prev_ = 0;
};

class History {
public:
    void run(std::unique_ptr<Command> c, Arm& a) { c->execute(a); done_.push_back(std::move(c)); redo_.clear(); }
    bool undo(Arm& a) { if (done_.empty()) return false; done_.back()->undo(a); redo_.push_back(std::move(done_.back())); done_.pop_back(); return true; }
    bool redo(Arm& a) { if (redo_.empty()) return false; redo_.back()->execute(a); done_.push_back(std::move(redo_.back())); redo_.pop_back(); return true; }
private:
    std::vector<std::unique_ptr<Command>> done_, redo_;
};
```

Running a new command **clears the redo stack**: the redone future no longer exists. A **macro command** (a composite of commands) undoes its children in reverse order. Commands also make the action log a replayable recording.

## 3. Strategy

A Strategy swaps an algorithm behind a stable interface: the path planner (A*, RRT*, Dijkstra) or the controller (PID, MPC). In modern C++ it's often just a `std::function` or a template parameter:

```cpp
using Heuristic = std::function<double(Cell, Cell)>;
std::vector<Cell> astar(const Grid& g, Cell s, Cell t, Heuristic h);

auto manhattan = [](Cell a, Cell b) { return std::abs(a.x - b.x) + std::abs(a.y - b.y); };
auto path = astar(grid, start, goal, manhattan);

template <typename Controller>             // static strategy: zero overhead, inlined
void control_loop(Controller& c);
```

## 4. State, the variant way

Behaviour depends on the current state, and the State pattern objectifies each state. With `std::variant`, each state is a plain struct holding its own data, transitions are values, and the compiler checks that every state is handled:

```cpp
struct Idle {};
struct Moving { Pose goal; double started; };
struct Fault { std::string reason; };
using DriveState = std::variant<Idle, Moving, Fault>;

template <class... F> struct overloaded : F... { using F::operator()...; };

DriveState on_obstacle(const DriveState& s) {
    return std::visit(overloaded{
        [](const Moving& m) -> DriveState { return Fault{"obstacle while moving to goal"}; },
        [](const auto& other) -> DriveState { return other; },
    }, s);
}
```

State-specific data, like `Moving::goal`, exists only while in that state, which removes a whole class of "stale field" bugs. The classic version, with a `State` base class whose virtual handlers return the next state, still suits open-ended state sets loaded from plugins.

## 5. Template Method and the NVI idiom

A base class fixes the algorithm skeleton and lets subclasses fill in steps. C++'s **Non-Virtual Interface** idiom makes the public function non-virtual and the customisation points private virtual functions:

```cpp
class Controller {
public:
    Command step(const State& s, double dt) {          // non-virtual: invariant pre/post steps
        if (dt <= 0) return Command::stop();
        Command c = compute(s, dt);                    // customisation point
        return saturate(c);                            // always applied: safety cannot be skipped
    }
    virtual ~Controller() = default;
private:
    virtual Command compute(const State& s, double dt) = 0;
};
```

The base class guarantees the safety clamp runs no matter what a subclass does.

## 6. Chain of Responsibility, Visitor and Mediator

- **Chain of Responsibility**: a request passes along handlers until one handles it. Examples are middleware pipelines, the safety checks on a velocity command (e-stop, geofence, speed limit), and event bubbling in GUIs.
- **Visitor**: adds operations over a fixed set of types without modifying them. Classic double dispatch (`accept(Visitor&)`) is verbose. With a closed set of types, `std::variant` plus `std::visit` is the modern Visitor.
- **Mediator**: components talk through a central hub instead of to each other. A message bus, or ROS topics themselves, decouples publishers from subscribers entirely.

> [!EXAM]
> **How do you implement Observer safely in C++?**
> The subject stores callbacks (`std::function`) keyed by id, and `connect` returns an RAII connection object that the observer owns as a member. Its destructor removes the callback, so a destroyed observer can never be called. The connection refers to the subject's slot table through a `weak_ptr`, so it also tolerates the subject dying first. Notification iterates over a snapshot (or uses deferred removal), so callbacks may connect or disconnect during `emit`. For threads, protect the slot table with a mutex but never call callbacks while holding it, because that invites deadlock.
