---
id: cpp-sensor-decorator-pipeline
title: Adapter, Decorators and a Composite Sensor Pipeline
difficulty: Hard
order: 1
tags: adapter, decorator, composite, interfaces, unique_ptr, std::optional, std::format
time_limit: 4
---
## Statement
A legacy lidar SDK speaks C: millimetres, integer error codes, raw pointers. Wrap it and build a configurable filtering pipeline from three structural patterns.

The **given** C API (part of the starter, don't change it): `int legacy_read_mm(LegacyLidar* dev, int* out_mm)` returns 0 and writes a reading, or returns a negative error code and writes nothing.

The interface every stage implements:

```cpp
struct RangeSensor {
    virtual ~RangeSensor() = default;
    virtual std::optional<double> range_m() = 0;   // metres, nullopt = no valid reading
    virtual std::string describe() const = 0;
};
```

Implement, with numbers in `describe()` formatted by `std::format("{}", x)`:

| Class | `range_m()` | `describe()` |
|---|---|---|
| `LidarAdapter(LegacyLidar&)` (**Adapter**) | one SDK call: `mm / 1000.0`, or nullopt on an error code | `lidar#<id>` |
| `Clamped(inner, lo, hi)` (**Decorator**) | the inner value if `lo <= v <= hi`, else nullopt | `clamp[lo,hi](<inner>)` |
| `MovingAverage(inner, n)` | Mean of the last `n` valid inner readings, including this one. A nullopt passes through without touching the window. | `avg<n>(<inner>)` |
| `HoldLast(inner, k)` | On nullopt, repeat the last valid output for up to `k` consecutive misses, then nullopt. A valid reading resets the miss count. Nothing to hold yet gives nullopt. | `hold<k>(<inner>)` |
| `NearestOf(children)` (**Composite**) | Polls **every** child exactly once per call and returns the minimum valid value, or nullopt if none are valid | `min(<c1>, <c2>, ...)` |

Each decorator calls its inner sensor **exactly once** per `range_m()` call.

`std::unique_ptr<RangeSensor> make_pipeline(LegacyLidar& dev, const std::vector<std::string>& stages)` starts from a `LidarAdapter` and wraps it with each stage in order (the first stage is innermost). A stage is `"clamp:LO:HI"`, `"avg:N"` (N ≥ 1) or `"hold:K"` (K ≥ 0). Any malformed or unknown stage makes it return **nullptr**.

## Starter
```cpp
#include <deque>
#include <format>
#include <memory>
#include <optional>
#include <string>
#include <vector>

// ---- given legacy SDK (do not modify) ----
struct LegacyLidar { int id; int calls; };
inline int legacy_read_mm(LegacyLidar* d, int* out_mm) {
    long v = (d->id * 7919L + d->calls * 104729L) % 12000L - 500;
    d->calls++;
    if (v % 9 == 0) return -2;                       // sporadic CRC error
    *out_mm = static_cast<int>(v);
    return 0;
}
// -------------------------------------------

struct RangeSensor {
    virtual ~RangeSensor() = default;
    virtual std::optional<double> range_m() = 0;
    virtual std::string describe() const = 0;
};

class LidarAdapter : public RangeSensor {
public:
    explicit LidarAdapter(LegacyLidar& d) : d_(d) {}
    std::optional<double> range_m() override { int mm = 0; legacy_read_mm(&d_, &mm); return mm; }
    std::string describe() const override { return "lidar"; }
private:
    LegacyLidar& d_;
};

std::unique_ptr<RangeSensor> make_pipeline(LegacyLidar& dev, const std::vector<std::string>& stages) {
    return std::make_unique<LidarAdapter>(dev);
}
```

## Driver
```cpp
#include <cstdio>
#include <iostream>

static std::string fmt_opt(std::optional<double> v) { return v ? std::format("{:.3f}", *v + 0.0) : "--"; }
static void run(RangeSensor& s, int n) {
    std::printf("%s:", s.describe().c_str());
    for (int i = 0; i < n; ++i) std::printf(" %s", fmt_opt(s.range_m()).c_str());
    std::printf("\n");
}

int main() {
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "adapter") {
            LegacyLidar d{3, 0};
            LidarAdapter a(d);
            run(a, 12);
            std::printf("sdk calls: %d\n", d.calls);
        } else if (cmd == "decorators") {
            LegacyLidar d1{3, 0}, d2{3, 0}, d3{3, 0}, d4{3, 0};
            Clamped c(std::make_unique<LidarAdapter>(d1), 0.5, 9.0); run(c, 12);
            MovingAverage m(std::make_unique<LidarAdapter>(d2), 3); run(m, 12);
            HoldLast h(std::make_unique<Clamped>(std::make_unique<LidarAdapter>(d3), 0.5, 9.0), 1); run(h, 12);
            HoldLast h0(std::make_unique<Clamped>(std::make_unique<LidarAdapter>(d4), 100.0, 200.0), 3); run(h0, 4);
            std::printf("calls: %d %d %d %d\n", d1.calls, d2.calls, d3.calls, d4.calls);
        } else if (cmd == "composite") {
            LegacyLidar a{1, 0}, b{2, 0}, c{5, 0};
            std::vector<std::unique_ptr<RangeSensor>> kids;
            kids.push_back(std::make_unique<Clamped>(std::make_unique<LidarAdapter>(a), 0.2, 8.0));
            kids.push_back(std::make_unique<MovingAverage>(std::make_unique<LidarAdapter>(b), 2));
            kids.push_back(std::make_unique<LidarAdapter>(c));
            NearestOf n(std::move(kids));
            run(n, 10);
            std::printf("calls: %d %d %d\n", a.calls, b.calls, c.calls);
            NearestOf empty({});
            run(empty, 2);
        } else if (cmd == "pipeline") {
            LegacyLidar d{7, 0};
            auto p = make_pipeline(d, {"clamp:0.25:10", "avg:4", "hold:2"});
            run(*p, 15);
            LegacyLidar e{7, 0};
            auto q = make_pipeline(e, {"hold:0", "clamp:-1:1e9"});
            run(*q, 5);
            for (auto bad : std::vector<std::vector<std::string>>{{"avg:0"}, {"avg:x"}, {"clamp:1"}, {"median:3"}, {"hold:-1"}, {"clamp:a:b"}, {"avg:3", ""}}) {
                LegacyLidar z{1, 0};
                std::printf("%s ", make_pipeline(z, bad) ? "built" : "null");
            }
            std::printf("\n");
            LegacyLidar big{11, 0};
            auto r = make_pipeline(big, {"clamp:0:11", "hold:1", "avg:50", "avg:5"});
            double sum = 0; int valid = 0;
            for (int i = 0; i < 200000; ++i) if (auto v = r->range_m()) { sum += *v; ++valid; }
            std::printf("%s\nbig: valid=%d mean=%.6f calls=%d\n", r->describe().c_str(), valid, sum / valid, big.calls);
        }
    }
}
```

## Tests
=== sample
adapter
decorators
---
lidar#3: 11.257 7.986 4.715 1.444 10.173 6.902 3.631 -- 9.089 5.818 -- 11.276
sdk calls: 12
clamp[0.5,9](lidar#3): -- 7.986 4.715 1.444 -- 6.902 3.631 -- -- 5.818 -- --
avg3(lidar#3): 11.257 9.621 7.986 4.715 5.444 6.173 6.902 -- 6.541 6.179 -- 8.728
hold1(clamp[0.5,9](lidar#3)): -- 7.986 4.715 1.444 1.444 6.902 3.631 3.631 -- 5.818 5.818 --
hold3(clamp[100,200](lidar#3)): -- -- -- --
calls: 12 12 12 4
=== hidden
composite
---
min(clamp[0.2,8](lidar#1), avg2(lidar#2), lidar#5): 3.095 -0.176 0.877 5.282 2.011 3.064 7.469 4.198 5.251 7.170
calls: 10 10 10
min(): -- --
=== hidden
pipeline
---
hold2(avg4(clamp[0.25,10](lidar#7))): 6.933 5.297 3.662 5.026 4.755 4.484 4.484 6.396 5.307 5.307 5.307 5.583 5.583 5.041 5.316
clamp[-1,1e+09](hold0(lidar#7)): 6.933 3.662 0.391 9.120 5.849
null null null null null null null 
avg5(avg50(hold1(clamp[0,11](lidar#11))))
big: valid=196300 mean=5.319886 calls=200000

## Hints
- Give the decorators a common base holding `std::unique_ptr<RangeSensor> inner_`.
- `MovingAverage`: a `std::deque<double>` plus a running sum. Pop from the front when the size exceeds n.
- `NearestOf::range_m` must not stop at the first valid child. Poll them all, so every stateful child advances.
- Parse stages by splitting on `:`, then use `std::stod`/`std::stoi` with `pos` checks inside `try`. Reject trailing garbage and wrong field counts.

## Solution
```cpp
#include <deque>
#include <format>
#include <memory>
#include <optional>
#include <sstream>
#include <string>
#include <vector>

// ---- given legacy SDK (do not modify) ----
struct LegacyLidar { int id; int calls; };
inline int legacy_read_mm(LegacyLidar* d, int* out_mm) {
    long v = (d->id * 7919L + d->calls * 104729L) % 12000L - 500;
    d->calls++;
    if (v % 9 == 0) return -2;                       // sporadic CRC error
    *out_mm = static_cast<int>(v);
    return 0;
}
// -------------------------------------------

struct RangeSensor {
    virtual ~RangeSensor() = default;
    virtual std::optional<double> range_m() = 0;
    virtual std::string describe() const = 0;
};

class LidarAdapter : public RangeSensor {                 // Adapter: C SDK -> our interface
public:
    explicit LidarAdapter(LegacyLidar& d) : d_(d) {}
    std::optional<double> range_m() override {
        int mm = 0;
        if (legacy_read_mm(&d_, &mm) != 0) return std::nullopt;
        return mm / 1000.0;
    }
    std::string describe() const override { return std::format("lidar#{}", d_.id); }
private:
    LegacyLidar& d_;
};

class Decorator : public RangeSensor {
protected:
    explicit Decorator(std::unique_ptr<RangeSensor> inner) : inner_(std::move(inner)) {}
    std::unique_ptr<RangeSensor> inner_;
};

class Clamped : public Decorator {
public:
    Clamped(std::unique_ptr<RangeSensor> s, double lo, double hi) : Decorator(std::move(s)), lo_(lo), hi_(hi) {}
    std::optional<double> range_m() override {
        auto v = inner_->range_m();
        if (!v || *v < lo_ || *v > hi_) return std::nullopt;
        return v;
    }
    std::string describe() const override { return std::format("clamp[{},{}]({})", lo_, hi_, inner_->describe()); }
private:
    double lo_, hi_;
};

class MovingAverage : public Decorator {
public:
    MovingAverage(std::unique_ptr<RangeSensor> s, std::size_t n) : Decorator(std::move(s)), n_(n) {}
    std::optional<double> range_m() override {
        auto v = inner_->range_m();
        if (!v) return std::nullopt;
        win_.push_back(*v);
        sum_ += *v;
        if (win_.size() > n_) { sum_ -= win_.front(); win_.pop_front(); }
        return sum_ / static_cast<double>(win_.size());
    }
    std::string describe() const override { return std::format("avg{}({})", n_, inner_->describe()); }
private:
    std::size_t n_;
    std::deque<double> win_;
    double sum_ = 0;
};

class HoldLast : public Decorator {
public:
    HoldLast(std::unique_ptr<RangeSensor> s, int k) : Decorator(std::move(s)), k_(k) {}
    std::optional<double> range_m() override {
        auto v = inner_->range_m();
        if (v) { last_ = v; misses_ = 0; return v; }
        if (last_ && misses_ < k_) { ++misses_; return last_; }
        return std::nullopt;
    }
    std::string describe() const override { return std::format("hold{}({})", k_, inner_->describe()); }
private:
    int k_, misses_ = 0;
    std::optional<double> last_;
};

class NearestOf : public RangeSensor {                    // Composite: a group is also a sensor
public:
    explicit NearestOf(std::vector<std::unique_ptr<RangeSensor>> kids) : kids_(std::move(kids)) {}
    std::optional<double> range_m() override {
        std::optional<double> best;
        for (auto& k : kids_)                              // poll every child, every time
            if (auto v = k->range_m(); v && (!best || *v < *best)) best = v;
        return best;
    }
    std::string describe() const override {
        std::string s = "min(";
        for (std::size_t i = 0; i < kids_.size(); ++i) s += (i ? ", " : "") + kids_[i]->describe();
        return s + ")";
    }
private:
    std::vector<std::unique_ptr<RangeSensor>> kids_;
};

namespace {
std::vector<std::string> split(const std::string& s) {
    std::vector<std::string> out;
    std::stringstream ss(s);
    std::string part;
    while (std::getline(ss, part, ':')) out.push_back(part);
    if (!s.empty() && s.back() == ':') out.push_back("");
    return out;
}
std::optional<double> to_double(const std::string& s) {
    try { std::size_t pos; double v = std::stod(s, &pos); if (pos == s.size()) return v; } catch (...) {}
    return std::nullopt;
}
std::optional<long> to_long(const std::string& s) {
    try { std::size_t pos; long v = std::stol(s, &pos); if (pos == s.size()) return v; } catch (...) {}
    return std::nullopt;
}
}  // namespace

std::unique_ptr<RangeSensor> make_pipeline(LegacyLidar& dev, const std::vector<std::string>& stages) {
    std::unique_ptr<RangeSensor> s = std::make_unique<LidarAdapter>(dev);
    for (const auto& st : stages) {
        auto f = split(st);
        if (f.size() == 3 && f[0] == "clamp") {
            auto lo = to_double(f[1]), hi = to_double(f[2]);
            if (!lo || !hi) return nullptr;
            s = std::make_unique<Clamped>(std::move(s), *lo, *hi);
        } else if (f.size() == 2 && f[0] == "avg") {
            auto n = to_long(f[1]);
            if (!n || *n < 1) return nullptr;
            s = std::make_unique<MovingAverage>(std::move(s), static_cast<std::size_t>(*n));
        } else if (f.size() == 2 && f[0] == "hold") {
            auto k = to_long(f[1]);
            if (!k || *k < 0) return nullptr;
            s = std::make_unique<HoldLast>(std::move(s), static_cast<int>(*k));
        } else {
            return nullptr;
        }
    }
    return s;
}
```

- **The Adapter** is the only code that knows about millimetres, `int*` out-parameters and error codes. Everything above it speaks metres and `std::optional`.
- **Decorators** share the `RangeSensor` interface and own their inner stage, so any stack can be assembled at runtime from configuration. Three classes give every combination, and order matters: clamping before averaging keeps glitches out of the mean.
- **The Composite** (`NearestOf`) is itself a `RangeSensor`, so groups nest inside pipelines and vice versa. It polls every child each cycle, because skipping children would freeze their internal state (averages, holds).
- **`make_pipeline`** is a small factory that validates the configuration completely and fails with nullptr rather than building half a pipeline.
- **Ownership** flows down through `unique_ptr`: destroying the outermost stage destroys the whole chain.
