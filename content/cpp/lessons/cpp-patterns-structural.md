# Structural Patterns in C++

Structural patterns are about **composing objects and interfaces**: adapting a library you can't change, adding behaviour without subclass explosions, treating groups like individuals, and hiding a messy subsystem behind a clean front. This lesson covers Adapter, Decorator, Composite, Facade, Proxy, Bridge and Flyweight. Each is shown both with classic virtual interfaces and with modern alternatives (templates, type erasure, `std::function`), because in C++ the choice between runtime and compile-time polymorphism matters for performance.

## 1. Adapter

An **Adapter** makes an existing interface fit the one your code expects. It's typical when integrating a vendor C SDK:

```cpp
// vendor C API (can't change): distances in millimetres, error codes
extern "C" int vendor_lidar_read_mm(int handle, int* out_mm);

struct RangeSensor {                                // our interface: metres, optional on failure
    virtual ~RangeSensor() = default;
    virtual std::optional<double> range_m() = 0;
};

class VendorLidarAdapter : public RangeSensor {
public:
    explicit VendorLidarAdapter(int handle) : h_(handle) {}
    std::optional<double> range_m() override {
        int mm = 0;
        if (vendor_lidar_read_mm(h_, &mm) != 0) return std::nullopt;
        return mm / 1000.0;
    }
private:
    int h_;
};
```

The adapter translates units, error conventions and naming in one place, so the rest of the code never sees millimetres or C error codes. It's the anti-corruption layer for every hardware driver.

## 2. Decorator

A **Decorator** wraps an object that has the **same interface** and adds behaviour before or after delegating. Decorators stack in any order, avoiding a combinatorial explosion of subclasses (`FilteredClampedLoggedSensor`…):

```cpp
class SensorDecorator : public RangeSensor {
public:
    explicit SensorDecorator(std::unique_ptr<RangeSensor> inner) : inner_(std::move(inner)) {}
protected:
    std::unique_ptr<RangeSensor> inner_;
};

class Clamped : public SensorDecorator {
public:
    Clamped(std::unique_ptr<RangeSensor> s, double lo, double hi) : SensorDecorator(std::move(s)), lo_(lo), hi_(hi) {}
    std::optional<double> range_m() override {
        auto v = inner_->range_m();
        if (!v || *v < lo_ || *v > hi_) return std::nullopt;     // reject out-of-range readings
        return v;
    }
private:
    double lo_, hi_;
};

class MovingAverage : public SensorDecorator {
public:
    MovingAverage(std::unique_ptr<RangeSensor> s, std::size_t n) : SensorDecorator(std::move(s)), n_(n) {}
    std::optional<double> range_m() override {
        auto v = inner_->range_m();
        if (!v) return std::nullopt;
        win_.push_back(*v); sum_ += *v;
        if (win_.size() > n_) { sum_ -= win_.front(); win_.pop_front(); }
        return sum_ / win_.size();
    }
private:
    std::size_t n_; std::deque<double> win_; double sum_ = 0;
};

auto s = std::make_unique<MovingAverage>(
            std::make_unique<Clamped>(std::make_unique<VendorLidarAdapter>(3), 0.05, 30.0), 5);
```

Order matters: clamping before averaging keeps outliers out of the average. In C++, decorators also appear as I/O stream buffers, `std::ranges` views (`v | filter | transform`) and middleware chains.

## 3. Composite

A **Composite** lets clients treat individual objects and groups uniformly: a part-whole tree.

```cpp
struct Frame {                                       // a node in a kinematic or scene tree
    virtual ~Frame() = default;
    virtual double mass() const = 0;
    virtual void visit(const std::function<void(const Frame&, int)>& f, int depth = 0) const = 0;
    std::string name;
};
struct Link : Frame {
    double m;
    double mass() const override { return m; }
    void visit(const std::function<void(const Frame&, int)>& f, int d) const override { f(*this, d); }
};
struct Assembly : Frame {
    std::vector<std::unique_ptr<Frame>> children;
    double mass() const override {
        double s = 0; for (const auto& c : children) s += c->mass(); return s;
    }
    void visit(const std::function<void(const Frame&, int)>& f, int d) const override {
        f(*this, d); for (const auto& c : children) c->visit(f, d + 1);
    }
};
```

Robot description trees (URDF links and joints), GUI widget hierarchies, scene graphs and behaviour trees are all composites. Ownership flows down through `unique_ptr`. If children need their parent, use a raw non-owning pointer: never a `shared_ptr` cycle.

## 4. Facade

A **Facade** gives a simple interface to a complex subsystem:

```cpp
class Navigation {                         // hides localisation, mapping, planning, control
public:
    bool go_to(Pose goal);                 // one call for the application
    void cancel();
    NavStatus status() const;
private:
    Localizer loc_; CostMap map_; GlobalPlanner planner_; Controller ctrl_;
};
```

Nav2's `BasicNavigator` and MoveIt's `MoveGroupInterface` are facades. A facade doesn't forbid direct subsystem access. It just provides a convenient default path.

## 5. Proxy

A **Proxy** has the same interface as the real object and controls access to it:
- **Lazy loading**: a map is only loaded from disk on first query.
- **Remote** access: the proxy serialises calls over the network, as RPC stubs and ROS action clients do.
- **Protection**: permission checks.
- **Caching** and **smart references**. `std::shared_ptr` is itself a proxy that counts references.

```cpp
class LazyMap : public OccupancyMap {
public:
    explicit LazyMap(std::string path) : path_(std::move(path)) {}
    bool occupied(int x, int y) const override { return real().occupied(x, y); }
private:
    const OccupancyMap& real() const {
        std::call_once(once_, [&] { map_ = load_pgm(path_); });     // thread-safe one-time load
        return *map_;
    }
    std::string path_;
    mutable std::once_flag once_;
    mutable std::unique_ptr<OccupancyMap> map_;
};
```

## 6. Bridge

A **Bridge** separates an abstraction from its implementation, so both can vary independently: `Robot` (abstraction: `DiffDriveRobot`, `OmniRobot`) holds a `MotorDriver&` (implementation: `CanDriver`, `PwmDriver`, `SimDriver`). Without it you'd need 2 × 3 subclasses. PIMPL is a bridge used for compilation firewalls.

## 7. Flyweight

A **Flyweight** shares immutable intrinsic state across many objects to save memory. For example, 100,000 trees in a simulator share one `TreeModel` (mesh and texture) and store only position and scale each. String interning (`std::string_view` into a shared pool) is a flyweight too.

## 8. Static alternatives: CRTP and type erasure

Virtual calls cost an indirection and block inlining. That's negligible in most code, but it matters in a 10 kHz filter loop. Alternatives:
- **Templates/CRTP** compose decorators at compile time: `MovingAverage<Clamped<Lidar>>`. There's zero overhead, but the type is fixed at compile time.
- **Type erasure** (`std::function`, or a hand-written `AnySensor` with a small-buffer-optimised concept/model) gives value semantics with runtime flexibility and no inheritance in user types.

Pick runtime composition (virtuals) for configuration-driven assembly, and compile-time composition for hot paths.

> [!EXAM]
> **Compare Decorator and Adapter, and explain why Decorator beats subclassing for optional behaviours.**
> An Adapter changes an interface: it wraps an object with an incompatible API, such as a vendor C SDK, and exposes the interface the client expects, translating units and errors. A Decorator keeps the same interface and adds behaviour (filtering, clamping, logging, caching) by wrapping and delegating. Because decorators share the component's interface, they can be stacked in any combination and order at runtime. Subclassing would need a class for every combination of N behaviours (2^N classes), fixed at compile time.
