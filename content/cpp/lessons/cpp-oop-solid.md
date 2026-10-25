# SOLID in C++

**SOLID** is five principles (Robert C. Martin) for designs that stay flexible as requirements change. They're often taught with Java-style interfaces, but C++ offers more tools: virtual interfaces, templates and concepts, `std::function`, and value semantics. Applying SOLID well in C++ means choosing between **runtime** and **compile-time** polymorphism. This lesson explains each principle with a robotics example, the C++ idiom that implements it, and the over-engineering traps.

## S: Single Responsibility Principle

*A class should have one reason to change.*

```cpp
// Before: one class, four reasons to change (sensor driver, filtering, logging format, network)
class LidarNode { void read_serial(); void filter(); void log_csv(); void publish_udp(); };

// After: each responsibility isolated, composed by a thin coordinator
class LidarDriver   { public: Scan read(); };
class ScanFilter    { public: Scan apply(const Scan&) const; };
class ScanLogger    { public: void log(const Scan&); };
class ScanPublisher { public: void publish(const Scan&); };
```

The test is "who asks for changes?" Hardware engineers, algorithm researchers and the ops team are different people, so they get different classes.

## O: Open/Closed Principle

*Open for extension, closed for modification.* Add new behaviour by adding code, not by editing working code.

```cpp
struct PricingRule {                                    // extension point
    virtual ~PricingRule() = default;
    virtual double adjust(const Rental& r, double price) const = 0;
};

class PricingEngine {
public:
    void add_rule(std::unique_ptr<PricingRule> r) { rules_.push_back(std::move(r)); }
    double quote(const Rental& r) const {
        double p = r.hours * base_rate_;
        for (const auto& rule : rules_) p = rule->adjust(r, p);   // never edited for new rules
        return p;
    }
private:
    double base_rate_ = 12.0;
    std::vector<std::unique_ptr<PricingRule>> rules_;
};
```

New discounts, surcharges and taxes are new classes. The engine stays closed. Compile-time alternatives are a template parameter pack of rules, or a `std::vector<std::function<double(const Rental&, double)>>`.

## L: Liskov Substitution Principle

*Subtypes must be usable anywhere their base type is, without surprising the caller.* Overrides may not strengthen preconditions, weaken postconditions or break invariants.

```cpp
class Rectangle { public: virtual void set_width(double); virtual void set_height(double); double area() const; };
class Square : public Rectangle { /* set_width also sets height */ };   // the classic violation

void stretch(Rectangle& r) { r.set_width(4); r.set_height(5); assert(r.area() == 20); }   // fails for Square
```

The fix is to stop making `Square` a mutable `Rectangle`. Model both as immutable values, or give them a common read-only `Shape` interface. In robotics, a `SimulatedMotor` that silently ignores torque limits violates LSP: code tested in simulation then breaks on hardware.

## I: Interface Segregation Principle

*Clients shouldn't depend on methods they don't use.*

```cpp
// Fat interface: every sensor must implement calibrate() and firmware_update(), even a fake one
struct Sensor { virtual Reading read() = 0; virtual void calibrate() = 0; virtual void firmware_update(Blob) = 0; };

// Segregated: small role interfaces, combined where needed
struct Readable     { virtual ~Readable() = default; virtual Reading read() = 0; };
struct Calibratable { virtual ~Calibratable() = default; virtual void calibrate() = 0; };
class Imu : public Readable, public Calibratable { /* ... */ };
```

The control loop depends only on `Readable`, so a test fake implements one function. C++20 concepts express segregated requirements without inheritance: `template <class S> concept Readable = requires(S s) { { s.read() } -> std::same_as<Reading>; };`.

## D: Dependency Inversion Principle

*High-level policy shouldn't depend on low-level details. Both depend on abstractions.*

```cpp
class Navigator {                                       // high-level policy
public:
    Navigator(Localizer& loc, MotorDriver& motors, Clock& clock);   // injected abstractions
    void step();
};
// main(): the composition root wires concrete details
CanMotorDriver motors{"can0"}; AmclLocalizer loc{map}; SteadyClock clock;
Navigator nav{loc, motors, clock};
// tests: FakeMotorDriver, ScriptedLocalizer, ManualClock
```

**Dependency injection** can use constructor parameters (the most common choice), template parameters (static DI: `Navigator<Loc, Motors>` with no virtual calls), or `std::function` callbacks. Avoid global singletons: they're hidden dependencies.

## Runtime vs compile-time SOLID

| Mechanism | Pros | Cons |
|---|---|---|
| Virtual interface + `unique_ptr` | swap implementations at runtime (configuration, plugins); separate compilation | indirect call; heap allocation |
| Template / concept | zero overhead, inlining, value semantics | types fixed at compile time; code bloat; longer compiles |
| `std::function` / type erasure | value semantics plus runtime flexibility, no inheritance | allocation (beyond the small-buffer optimisation); indirect call |

Choose per situation: a plugin-configured planner wants virtuals, while a 10 kHz filter chain wants templates.

## Over-engineering warnings

SOLID is a means, not a goal. An interface with a single implementation and no testing need is noise. Introduce abstractions **when a second implementation or a test double appears** (the "rule of three" for abstraction), and keep YAGNI in mind: you aren't gonna need it.

> [!EXAM]
> **Explain the Dependency Inversion Principle and two ways to implement it in C++.**
> High-level modules, such as a navigation policy, shouldn't depend on low-level details like a CAN motor driver or a specific localiser. Both should depend on abstractions owned by the high-level layer, which keeps the policy reusable and testable. In C++ this is done at runtime by defining abstract interfaces (pure virtual classes) that the high-level class receives by reference or `unique_ptr` through its constructor, with concrete implementations wired in the composition root. At compile time, it's done by making the dependency a template parameter constrained by a concept, giving zero-overhead static dependency injection. Type erasure (`std::function`, or hand-written erasure) is a third option, combining value semantics with runtime substitution.

## Worked example: dependency inversion with an interface

```cpp
#include <iostream>
#include <memory>
#include <string>
#include <vector>

struct Notifier {                                     // abstraction (interface)
    virtual ~Notifier() = default;
    virtual void send(const std::string& msg) = 0;
};

struct ConsoleNotifier : Notifier {                   // production detail
    void send(const std::string& msg) override { std::cout << "ALERT: " << msg << '\n'; }
};

struct RecordingNotifier : Notifier {                 // test double
    std::vector<std::string> sent;
    void send(const std::string& msg) override { sent.push_back(msg); }
};

class BatteryMonitor {                                // high-level policy
    Notifier& notifier_;                              // depends only on the abstraction
public:
    explicit BatteryMonitor(Notifier& n) : notifier_(n) {}
    void update(const std::string& robot, double level) {
        if (level < 0.15) notifier_.send(robot + " battery low");
    }
};

int main() {
    ConsoleNotifier console;
    BatteryMonitor live(console);
    live.update("R2", 0.10);

    RecordingNotifier fake;                           // a unit test would do exactly this
    BatteryMonitor tested(fake);
    tested.update("R3", 0.50);
    tested.update("R3", 0.05);
    std::cout << fake.sent.size() << " message(s) recorded\n";
}
```

```output
ALERT: R2 battery low
1 message(s) recorded
```

`BatteryMonitor` never names a concrete notifier, so you can add `SlackNotifier` or `SmsNotifier` without touching it (open/closed), and tests need no network (dependency inversion).

If the choice is fixed at compile time, a template parameter with a concept gives the same flexibility without virtual calls ("compile-time SOLID").

## Common mistakes

- **Interfaces without a virtual destructor.** Deleting through a base pointer is then undefined behaviour.
- **One fat interface** (`IRobot` with 30 methods). Split it by client need (interface segregation).
- **Abstracting before there is a second implementation or a test.** That adds indirection with no benefit.

## Check your understanding

1. Why does `BatteryMonitor` store a reference, not a `ConsoleNotifier`?
2. What would violate Liskov substitution for `Notifier`?

<details><summary>Answers</summary>

1. So any `Notifier` implementation can be supplied by whoever constructs it (dependency injection).
2. A subclass whose `send` throws for normal messages, or silently requires a call to `connect()` first. Callers of the base contract would break.

</details>
