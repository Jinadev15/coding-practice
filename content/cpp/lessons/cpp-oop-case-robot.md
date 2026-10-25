# Case Study: Robot Software Architecture

Robot software combines hard requirements, such as real-time control, safety, many interacting components and testability without hardware, so architecture matters more than in most domains. This case study builds the decision-making core of a robot with a **behavior tree** (BT), the design used by Nav2 (ROS 2), MoveIt Task Constructor, game AI, and BehaviorTree.CPP. It shows how composite, decorator and leaf node classes, a shared **blackboard**, and a tick-based execution model produce modular, reactive behaviour, and how the OOP principles from this module apply.

## 1. Why behavior trees?

Finite state machines become unmanageable as behaviours grow: with N states, transitions grow as N², and reusing a sub-behaviour means duplicating states. A **behavior tree** organises behaviour hierarchically:
- **Leaves** do work: **Actions** (move, grasp) and **Conditions** (is the battery low?).
- **Control nodes** combine children: **Sequence** ("do all in order, fail if any fails") and **Fallback**, also called Selector ("try alternatives until one succeeds").
- **Decorators** modify a single child: **Inverter**, **Retry(n)**, **Timeout**, **RunOnce**.

Every node is **ticked** and returns `SUCCESS`, `FAILURE` or `RUNNING`. `RUNNING` means "not done yet, tick me again next cycle", which lets long actions run across many control cycles without blocking.

```text
Fallback
├── Sequence                    "dock if the battery is low"
│   ├── Condition BatteryLow
│   └── Action GoToDock
└── Sequence                    "otherwise patrol"
    ├── Action NextWaypoint
    └── Retry(3)
        └── Action MoveTo
```

## 2. The class hierarchy (Composite pattern)

```cpp
enum class Status { Success, Failure, Running };

class Blackboard {                                    // shared typed key-value memory
public:
    template <class T> void set(const std::string& k, T v) { data_[k] = std::move(v); }
    template <class T> std::optional<T> get(const std::string& k) const {
        auto it = data_.find(k);
        if (it == data_.end()) return std::nullopt;
        if (auto p = std::any_cast<T>(&it->second)) return *p;
        return std::nullopt;
    }
private:
    std::unordered_map<std::string, std::any> data_;
};

class Node {
public:
    explicit Node(std::string name) : name_(std::move(name)) {}
    virtual ~Node() = default;
    Status tick(Blackboard& bb) {                     // NVI: one place for tracing and statistics
        status_ = on_tick(bb);
        ++ticks_;
        return status_;
    }
    virtual void halt() { status_ = Status::Failure; }   // interrupt a RUNNING subtree
    const std::string& name() const { return name_; }
private:
    virtual Status on_tick(Blackboard& bb) = 0;
    std::string name_;
    Status status_ = Status::Failure;
    unsigned ticks_ = 0;
};
```

**Sequence with memory**: remember which child is running, so earlier children aren't re-executed while a later one is still `RUNNING`:

```cpp
class Sequence : public Node {
    std::vector<std::unique_ptr<Node>> children_;     // composition: the tree owns its nodes
    std::size_t current_ = 0;
    Status on_tick(Blackboard& bb) override {
        while (current_ < children_.size()) {
            Status s = children_[current_]->tick(bb);
            if (s == Status::Running) return s;        // resume here next tick
            if (s == Status::Failure) { current_ = 0; return s; }
            ++current_;
        }
        current_ = 0;
        return Status::Success;
    }
};
```

**Reactive vs memory nodes**: a *reactive* sequence re-checks earlier conditions every tick and **halts** a running child when a condition flips. For example, stop moving the moment `ObstacleAhead` becomes true. Nav2 uses both kinds deliberately.

## 3. Leaves wrap the outside world

Actions talk to the rest of the robot through interfaces (DIP): a `MoveTo` action holds a `MotionClient&`, sends a goal on its first tick, returns `RUNNING` while it's in progress, and maps the result to `SUCCESS` or `FAILURE`. In tests, a scripted fake client makes every scenario deterministic.

## 4. Applying the module's principles

- **SRP**: each node does one thing, and behaviours are composed, not coded.
- **OCP**: new behaviours are new node classes, often loaded from XML at runtime through a **factory registry** (`factory.register<MoveTo>("MoveTo")`), and the tree engine never changes.
- **LSP**: every node honours the tick contract, never blocks, and returns `RUNNING` instead.
- **Ownership**: parents own their children through `unique_ptr`. The blackboard is shared by reference and owned by the executor, so it outlives the tree.
- **Testability**: ticking is deterministic, so tests drive N ticks and assert the status sequence and blackboard contents.

## 5. The execution loop

```cpp
Blackboard bb;
auto tree = build_tree_from_xml("patrol.xml", factory);   // or built in code
while (running) {
    update_blackboard_from_sensors(bb);
    Status s = tree->tick(bb);                            // 10-100 Hz
    if (s != Status::Running) tree = next_mission();
    sleep_until(next_cycle);
}
```

> [!EXAM]
> **Why do robotics frameworks prefer behavior trees to large finite state machines, and what does `RUNNING` enable?**
> Behaviour trees compose behaviour hierarchically from reusable nodes. Control nodes (Sequence, Fallback) and decorators (Retry, Inverter, Timeout) combine leaf actions and conditions, so adding or reusing a behaviour means inserting a subtree, rather than rewiring the quadratically growing transitions of an FSM, and the tree is easy to read and edit (often as XML). The three-valued tick result makes nodes non-blocking. `RUNNING` lets long actions (navigation, grasping) span many control cycles while the tree keeps ticking, so reactive nodes can re-check conditions each tick and halt a running action the moment its preconditions fail.
