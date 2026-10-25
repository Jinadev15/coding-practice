# Creational Patterns in C++

Creational patterns control **how objects come into existence**: who decides the concrete type, how complex objects are assembled step by step, and how many instances exist. The *Gang of Four* book (1994) described them for C++98, and modern C++ changes their shape. `std::unique_ptr` makes ownership explicit, lambdas replace many tiny factory classes, `std::function` and templates replace inheritance hierarchies, and `std::expected` lets a builder report errors without exceptions. This lesson covers Factory Method, Abstract Factory, a self-registering factory, Builder, Prototype, Singleton (and why to avoid it), and Object Pool, all in modern C++ with robotics examples.

## 1. Simple factory and factory method

The client asks for an object by **description**, such as a config string, and gets back an interface. It never names concrete classes.

```cpp
struct Sensor {
    virtual ~Sensor() = default;
    virtual double read() = 0;
    virtual std::string_view kind() const = 0;
};
struct Lidar : Sensor { double read() override { return 4.2; } std::string_view kind() const override { return "lidar"; } };
struct Sonar : Sensor { double read() override { return 1.3; } std::string_view kind() const override { return "sonar"; } };

std::unique_ptr<Sensor> make_sensor(std::string_view type) {
    if (type == "lidar") return std::make_unique<Lidar>();
    if (type == "sonar") return std::make_unique<Sonar>();
    return nullptr;                              // or throw / std::expected
}
```

> [!KEY]
> Factories return `std::unique_ptr<Base>`. Ownership transfers to the caller, there's no leak on any path, and it converts to `shared_ptr` if needed. Returning raw `new`-ed pointers was the C++98 way and the source of countless leaks.

The **Factory Method** proper is a virtual function that subclasses override to choose what to create: `virtual std::unique_ptr<Planner> make_planner() const = 0;` in a `RobotBase` class, so a `DroneRobot` produces a 3-D planner.

## 2. Registry (self-registering) factory

An if/else chain violates the open/closed principle: every new sensor edits the factory. A **registry** maps names to creator functions, and new types register themselves:

```cpp
class SensorRegistry {
public:
    using Creator = std::function<std::unique_ptr<Sensor>(const Config&)>;
    static SensorRegistry& instance() { static SensorRegistry r; return r; }      // thread-safe since C++11
    bool add(std::string name, Creator c) { return creators_.emplace(std::move(name), std::move(c)).second; }
    std::unique_ptr<Sensor> create(const std::string& name, const Config& cfg) const {
        auto it = creators_.find(name);
        return it == creators_.end() ? nullptr : it->second(cfg);
    }
private:
    std::map<std::string, Creator, std::less<>> creators_;
};

// in lidar.cpp: registration at static-initialisation time
namespace { const bool reg = SensorRegistry::instance().add("lidar",
    [](const Config& c) { return std::make_unique<Lidar>(c); }); }
```

This is how ROS 2 `pluginlib`, Gazebo plugins and game engines extend systems without touching the core. Beware the **static initialisation order fiasco**: use a function-local static (as above), never a global map, and make sure the linker keeps the registering object files. Static libraries drop unreferenced `.o` files, and with them the registration.

## 3. Abstract factory

An Abstract Factory creates **families** of related objects that must match: a simulation factory produces simulated sensors and simulated motors, while a hardware factory produces real drivers.

```cpp
struct HardwareFactory {
    virtual ~HardwareFactory() = default;
    virtual std::unique_ptr<Sensor> make_lidar() = 0;
    virtual std::unique_ptr<Motor> make_motor(int id) = 0;
};
struct SimFactory : HardwareFactory { /* returns SimLidar, SimMotor */ };
struct RealFactory : HardwareFactory { /* returns UsbLidar, CanMotor */ };

Robot build_robot(HardwareFactory& f) { return Robot{f.make_lidar(), f.make_motor(1), f.make_motor(2)}; }
```

Choosing the factory once (`--sim` flag) guarantees no mix of simulated and real components: the classic "sim-to-real" switch.

## 4. Builder

Objects with many parameters, optional parts and validation rules are hard to construct with a constructor (telescoping constructors, or `Robot(1.5, 0.3, true, false, 7)` that nobody can read). A **Builder** assembles them step by step and validates once:

```cpp
struct MotionLimits { double v_max, a_max, j_max; bool reversible; };

class MotionLimitsBuilder {
public:
    MotionLimitsBuilder& max_velocity(double v) { v_ = v; return *this; }
    MotionLimitsBuilder& max_accel(double a)    { a_ = a; return *this; }
    MotionLimitsBuilder& max_jerk(double j)     { j_ = j; return *this; }
    MotionLimitsBuilder& reversible(bool r = true) { rev_ = r; return *this; }

    std::expected<MotionLimits, std::string> build() const {
        if (!v_ || *v_ <= 0) return std::unexpected("max_velocity must be set and > 0");
        if (!a_ || *a_ <= 0) return std::unexpected("max_accel must be set and > 0");
        return MotionLimits{*v_, *a_, j_.value_or(10 * *a_), rev_};     // derived default
    }
private:
    std::optional<double> v_, a_, j_;
    bool rev_ = false;
};

auto lim = MotionLimitsBuilder{}.max_velocity(1.2).max_accel(0.5).reversible().build();
if (!lim) std::cerr << lim.error();
```

Fluent setters return `*this` by reference. `build()` validates the combination and can compute derived defaults. `std::expected` (C++23) makes failure part of the type. C++20 **designated initialisers** (`MotionLimits{.v_max = 1.2, .a_max = 0.5}`) cover the simple cases without a builder.

## 5. Prototype

Prototype creates new objects by **cloning** an existing one, when the concrete type is only known through a base pointer:

```cpp
struct Shape {
    virtual ~Shape() = default;
    virtual std::unique_ptr<Shape> clone() const = 0;
};
struct Circle : Shape {
    double r;
    explicit Circle(double r) : r(r) {}
    std::unique_ptr<Shape> clone() const override { return std::make_unique<Circle>(*this); }
};
```

Copy constructors don't work polymorphically: `Shape s = *ptr` **slices**. A virtual `clone()` is the idiomatic polymorphic copy, used when copying a whole scene graph or a vector of `unique_ptr<Shape>`.

## 6. Singleton, and why to avoid it

```cpp
class Logger {
public:
    static Logger& get() { static Logger inst; return inst; }    // Meyers singleton: lazy, thread-safe init
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;
private:
    Logger() = default;
};
```

Singletons are global state in disguise:
- They hide dependencies (a function's signature doesn't reveal that it logs or reads config).
- They make tests interfere with each other.
- They create destruction-order problems at exit.

Prefer **dependency injection**: create one object in `main` and pass references down. Use a singleton only for true process-wide resources, or as a registry's storage as in §2.

## 7. Object pool

Real-time loops must not call `new`, because allocation time is unbounded. Pre-allocate a fixed set of objects and recycle them:

```cpp
template <typename T, std::size_t N>
class Pool {
public:
    Pool() { for (std::size_t i = 0; i < N; ++i) free_.push_back(&slots_[i]); }
    struct Releaser { Pool* p; void operator()(T* t) const { p->free_.push_back(t); } };
    using Handle = std::unique_ptr<T, Releaser>;
    Handle acquire() {
        if (free_.empty()) return Handle(nullptr, Releaser{this});
        T* t = free_.back(); free_.pop_back();
        return Handle(t, Releaser{this});              // returned to the pool automatically
    }
private:
    std::array<T, N> slots_{};
    std::vector<T*> free_;                             // reserve()d once; never grows past N
};
```

The custom deleter turns the pool into RAII: dropping the handle returns the object. This pattern is common for message buffers, particles and network packets.

> [!EXAM]
> **When would you use a Builder instead of a constructor, and how do you implement one in modern C++?**
> Use a Builder when an object has many parameters, optional parts or derived defaults, or validation rules that involve combinations of fields. Constructors then become unreadable, with positional booleans and telescoping overloads, and they can't report validation errors without exceptions. Implement it with fluent setters that store values in `std::optional` members and return `*this`, and a `build()` that checks the combination, fills in defaults and returns the finished object, or a `std::expected<T, Error>` describing what's wrong. The product can then be immutable (const members), because it's only created fully valid.
