---
id: cpp-sensor-factory-builder
title: Sensor Registry, Prototypes and a Validating Builder
difficulty: Medium
order: 1
tags: factory, registry, prototype, clone, builder, std::expected, unique_ptr
time_limit: 4
---
## Statement
A robot description is assembled from a config. Implement the three creational pieces it relies on.

**1. `SensorRegistry`**, a name → creator factory:
- `bool add(std::string name, Creator c)` returns false (and changes nothing) for an empty name, an empty `std::function`, or a duplicate name.
- `std::unique_ptr<Sensor> create(std::string_view name, const Config& cfg) const` returns nullptr for unknown names. A creator may itself return nullptr for an invalid config.
- `std::vector<std::string> names() const`: sorted.

**2. `void register_builtin(SensorRegistry& r)`** registers these kinds. `cfg.get(key, default)` reads parameters.

| kind | `read(truth)` | config |
|---|---|---|
| `ideal` | `truth` | |
| `biased` | `truth + bias` | `bias` (default 0) |
| `quantized` | `std::round(truth / step) * step` | `step` (default 0.01). The creator returns nullptr if `step <= 0`. |
| `drifting` | `truth + drift * k`, where k is the number of earlier `read` calls on **this** object | `drift` (default 0.001) |

Every sensor's `kind()` returns its kind name. `clone()` returns an independent copy **including its state**: a cloned `drifting` sensor continues from the same k, independently. That's the Prototype pattern.

**3. `RobotSpecBuilder`**, with fluent setters `name(s)`, `wheel_radius(m)`, `track(m)`, `max_rpm(r)` and `add_sensor(id, kind)`. Then `std::expected<RobotSpec, std::string> build() const` validates, returning the **first** failing message in this order:
1. `"name required"` (unset or empty)
2. `"wheel_radius must be > 0"` (unset or ≤ 0)
3. `"track must be > 0"`
4. `"max_rpm must be > 0"` (`max_rpm` defaults to 3000)
5. `"duplicate sensor: <id>"` for the first repeated sensor id, in insertion order

On success:
- `max_speed = max_rpm / 60 · 2π · wheel_radius`.
- `sensors` keeps the insertion order.
- `build()` may be called repeatedly and doesn't change the builder.

## Starter
```cpp
#include <cmath>
#include <expected>
#include <functional>
#include <map>
#include <memory>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

struct Config {
    std::map<std::string, double, std::less<>> values;
    double get(std::string_view k, double def) const {
        auto it = values.find(k);
        return it == values.end() ? def : it->second;
    }
};

struct Sensor {
    virtual ~Sensor() = default;
    virtual std::string kind() const = 0;
    virtual double read(double truth) = 0;
    virtual std::unique_ptr<Sensor> clone() const = 0;
};

class SensorRegistry {
public:
    using Creator = std::function<std::unique_ptr<Sensor>(const Config&)>;
    bool add(std::string name, Creator c) { creators_[name] = c; return true; }
    std::unique_ptr<Sensor> create(std::string_view name, const Config& cfg) const {
        return creators_.at(std::string(name))(cfg);
    }
    std::vector<std::string> names() const { return {}; }
private:
    std::map<std::string, Creator> creators_;
};

struct Ideal : Sensor {
    std::string kind() const override { return "ideal"; }
    double read(double t) override { return t; }
    std::unique_ptr<Sensor> clone() const override { return std::make_unique<Ideal>(); }
};

void register_builtin(SensorRegistry& r) {
    r.add("ideal", [](const Config&) { return std::make_unique<Ideal>(); });
}

struct RobotSpec {
    std::string name;
    double wheel_radius = 0, track = 0, max_rpm = 0, max_speed = 0;
    std::vector<std::pair<std::string, std::string>> sensors;
};

class RobotSpecBuilder {
public:
    RobotSpecBuilder& name(std::string n) { spec_.name = std::move(n); return *this; }
    RobotSpecBuilder& wheel_radius(double r) { spec_.wheel_radius = r; return *this; }
    RobotSpecBuilder& track(double t) { spec_.track = t; return *this; }
    RobotSpecBuilder& max_rpm(double r) { spec_.max_rpm = r; return *this; }
    RobotSpecBuilder& add_sensor(std::string id, std::string kind) { spec_.sensors.emplace_back(id, kind); return *this; }
    std::expected<RobotSpec, std::string> build() const { return spec_; }
private:
    RobotSpec spec_;
};
```

## Driver
```cpp
#include <cstdio>
#include <iostream>

static void show(const std::expected<RobotSpec, std::string>& r) {
    if (!r) { std::printf("error: %s\n", r.error().c_str()); return; }
    std::printf("%s r=%.3f track=%.3f rpm=%.0f vmax=%.4f sensors:", r->name.c_str(), r->wheel_radius, r->track, r->max_rpm, r->max_speed);
    for (auto& [id, k] : r->sensors) std::printf(" %s/%s", id.c_str(), k.c_str());
    std::printf("\n");
}

int main() {
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "registry") {
            SensorRegistry reg;
            register_builtin(reg);
            for (auto& n : reg.names()) std::printf("%s ", n.c_str());
            std::printf("\n");
            std::printf("add dup %d, empty %d, null %d, new %d\n", reg.add("ideal", [](const Config&) { return std::unique_ptr<Sensor>(); }),
                        reg.add("", [](const Config&) { return std::unique_ptr<Sensor>(); }), reg.add("x", SensorRegistry::Creator{}),
                        reg.add("zero", [](const Config&) -> std::unique_ptr<Sensor> { return std::make_unique<Ideal>(); }));
            std::printf("unknown -> %s\n", reg.create("sonar", {}) ? "object" : "null");
            Config c; c.values = {{"bias", 0.25}, {"step", 0.5}, {"drift", 0.1}};
            for (const char* k : {"ideal", "biased", "quantized", "drifting", "zero"}) {
                auto s = reg.create(k, c);
                std::printf("%s(%s):", k, s ? s->kind().c_str() : "null");
                for (double t : {1.0, 1.2, -0.74}) std::printf(" %.3f", s->read(t) + 0.0);
                std::printf("\n");
            }
            auto d = reg.create("quantized", {});
            std::printf("default step: %.3f\n", d->read(0.123456));
            Config bad; bad.values = {{"step", 0}};
            std::printf("bad step -> %s\n", reg.create("quantized", bad) ? "object" : "null");
        } else if (cmd == "prototype") {
            SensorRegistry reg; register_builtin(reg);
            Config c; c.values = {{"drift", 0.5}};
            auto a = reg.create("drifting", c);
            a->read(0); a->read(0);
            auto b = a->clone();
            double a3 = a->read(0), a4 = a->read(0), b3 = b->read(0);
            std::printf("a: %.1f %.1f  b: %.1f  kind %s\n", a3, a4, b3, b->kind().c_str());
            std::vector<std::unique_ptr<Sensor>> fleet;
            for (const char* k : {"biased", "quantized", "drifting", "ideal"}) fleet.push_back(reg.create(k, c));
            std::vector<std::unique_ptr<Sensor>> copy;
            for (auto& s : fleet) copy.push_back(s->clone());
            for (std::size_t i = 0; i < fleet.size(); ++i) fleet[i]->read(1);
            for (auto& s : copy) std::printf("%s=%.3f ", s->kind().c_str(), s->read(1.004));
            std::printf("\n");
        } else if (cmd == "builder") {
            RobotSpecBuilder b;
            show(b.build());
            b.name("rover");
            show(b.build());
            b.wheel_radius(-0.1); show(b.build());
            b.wheel_radius(0.05); show(b.build());
            b.track(0.3); show(b.build());
            b.add_sensor("front", "lidar").add_sensor("imu0", "imu"); show(b.build());
            b.max_rpm(0); show(b.build());
            b.max_rpm(6000); show(b.build());
            b.add_sensor("rear", "sonar").add_sensor("imu0", "imu2").add_sensor("rear", "x"); show(b.build());
            show(RobotSpecBuilder{}.name("").wheel_radius(1).track(1).build());
            auto r1 = RobotSpecBuilder{}.name("arm").wheel_radius(0.1).track(0.5).build();
            show(r1);
        }
    }
}
```

## Tests
=== sample
registry
---
biased drifting ideal quantized 
add dup 0, empty 0, null 0, new 1
unknown -> null
ideal(ideal): 1.000 1.200 -0.740
biased(biased): 1.250 1.450 -0.490
quantized(quantized): 1.000 1.000 -0.500
drifting(drifting): 1.000 1.300 -0.540
zero(ideal): 1.000 1.200 -0.740
default step: 0.120
bad step -> null
=== hidden
prototype
---
a: 1.0 1.5  b: 1.0  kind drifting
biased=1.004 quantized=1.000 drifting=1.004 ideal=1.004 
=== hidden
builder
---
error: name required
error: wheel_radius must be > 0
error: wheel_radius must be > 0
error: track must be > 0
rover r=0.050 track=0.300 rpm=3000 vmax=15.7080 sensors:
rover r=0.050 track=0.300 rpm=3000 vmax=15.7080 sensors: front/lidar imu0/imu
error: max_rpm must be > 0
rover r=0.050 track=0.300 rpm=6000 vmax=31.4159 sensors: front/lidar imu0/imu
error: duplicate sensor: imu0
error: name required
arm r=0.100 track=0.500 rpm=3000 vmax=31.4159 sensors:

## Hints
- `add`: check `name.empty() || !c`, then `creators_.emplace(...)`, and return `.second` (false for duplicates).
- Make the map `std::map<std::string, Creator, std::less<>>`, so `find(std::string_view)` works without building a string.
- Each concrete sensor stores its parameters (and the drifting sensor its counter). `clone()` is `std::make_unique<Self>(*this)`, using the copy constructor.
- Store builder inputs in `std::optional` members, so you can tell "unset" from 0. Check for duplicates with a `std::set` while scanning in order.

## Solution
```cpp
#include <cmath>
#include <expected>
#include <functional>
#include <map>
#include <memory>
#include <numbers>
#include <optional>
#include <set>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

struct Config {
    std::map<std::string, double, std::less<>> values;
    double get(std::string_view k, double def) const {
        auto it = values.find(k);
        return it == values.end() ? def : it->second;
    }
};

struct Sensor {
    virtual ~Sensor() = default;
    virtual std::string kind() const = 0;
    virtual double read(double truth) = 0;
    virtual std::unique_ptr<Sensor> clone() const = 0;
};

class SensorRegistry {
public:
    using Creator = std::function<std::unique_ptr<Sensor>(const Config&)>;
    bool add(std::string name, Creator c) {
        if (name.empty() || !c) return false;
        return creators_.emplace(std::move(name), std::move(c)).second;
    }
    std::unique_ptr<Sensor> create(std::string_view name, const Config& cfg) const {
        auto it = creators_.find(name);
        return it == creators_.end() ? nullptr : it->second(cfg);
    }
    std::vector<std::string> names() const {
        std::vector<std::string> out;
        for (const auto& [n, _] : creators_) out.push_back(n);     // std::map is already sorted
        return out;
    }
private:
    std::map<std::string, Creator, std::less<>> creators_;
};

// CRTP helper: implements clone() once for every concrete sensor
template <typename Derived>
struct Cloneable : Sensor {
    std::unique_ptr<Sensor> clone() const override {
        return std::make_unique<Derived>(static_cast<const Derived&>(*this));
    }
};

struct Ideal : Cloneable<Ideal> {
    std::string kind() const override { return "ideal"; }
    double read(double t) override { return t; }
};

struct Biased : Cloneable<Biased> {
    explicit Biased(double b) : bias(b) {}
    std::string kind() const override { return "biased"; }
    double read(double t) override { return t + bias; }
    double bias;
};

struct Quantized : Cloneable<Quantized> {
    explicit Quantized(double s) : step(s) {}
    std::string kind() const override { return "quantized"; }
    double read(double t) override { return std::round(t / step) * step; }
    double step;
};

struct Drifting : Cloneable<Drifting> {
    explicit Drifting(double d) : drift(d) {}
    std::string kind() const override { return "drifting"; }
    double read(double t) override { return t + drift * static_cast<double>(reads++); }
    double drift;
    long reads = 0;                                   // state copied by clone()
};

void register_builtin(SensorRegistry& r) {
    r.add("ideal", [](const Config&) { return std::make_unique<Ideal>(); });
    r.add("biased", [](const Config& c) { return std::make_unique<Biased>(c.get("bias", 0.0)); });
    r.add("quantized", [](const Config& c) -> std::unique_ptr<Sensor> {
        double step = c.get("step", 0.01);
        if (!(step > 0)) return nullptr;
        return std::make_unique<Quantized>(step);
    });
    r.add("drifting", [](const Config& c) { return std::make_unique<Drifting>(c.get("drift", 0.001)); });
}

struct RobotSpec {
    std::string name;
    double wheel_radius = 0, track = 0, max_rpm = 0, max_speed = 0;
    std::vector<std::pair<std::string, std::string>> sensors;
};

class RobotSpecBuilder {
public:
    RobotSpecBuilder& name(std::string n) { name_ = std::move(n); return *this; }
    RobotSpecBuilder& wheel_radius(double r) { radius_ = r; return *this; }
    RobotSpecBuilder& track(double t) { track_ = t; return *this; }
    RobotSpecBuilder& max_rpm(double r) { rpm_ = r; return *this; }
    RobotSpecBuilder& add_sensor(std::string id, std::string kind) {
        sensors_.emplace_back(std::move(id), std::move(kind));
        return *this;
    }

    std::expected<RobotSpec, std::string> build() const {
        if (!name_ || name_->empty()) return std::unexpected("name required");
        if (!radius_ || !(*radius_ > 0)) return std::unexpected("wheel_radius must be > 0");
        if (!track_ || !(*track_ > 0)) return std::unexpected("track must be > 0");
        if (!(rpm_ > 0)) return std::unexpected("max_rpm must be > 0");
        std::set<std::string, std::less<>> seen;
        for (const auto& [id, _] : sensors_)
            if (!seen.insert(id).second) return std::unexpected("duplicate sensor: " + id);
        RobotSpec s{*name_, *radius_, *track_, rpm_, rpm_ / 60.0 * 2.0 * std::numbers::pi * *radius_, sensors_};
        return s;
    }

private:
    std::optional<std::string> name_;
    std::optional<double> radius_, track_;
    double rpm_ = 3000;
    std::vector<std::pair<std::string, std::string>> sensors_;
};
```

- **The registry** decouples clients from concrete types. New sensor kinds plug in with one `add` call, and the factory code never changes (open/closed principle). Rejecting duplicates and empty creators keeps the registry consistent.
- **Creators return `unique_ptr`** and may return nullptr for an invalid config (step ≤ 0), so validation sits next to the type that knows its own rules.
- **Prototype via CRTP**: `Cloneable<Derived>` writes the virtual `clone()` once, using the derived copy constructor. That copies *all* state, so a cloned drifting sensor resumes at the same read count and then evolves independently.
- **Builder with `std::optional`** distinguishes "never set" from an explicit 0, validates in a fixed, documented order, computes derived fields (`max_speed`), and returns `std::expected`. Callers must handle failure, and no half-built `RobotSpec` ever exists.
