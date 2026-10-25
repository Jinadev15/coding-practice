---
id: cpp-pricing-engine
title: An Open/Closed Pricing Engine with Injected Dependencies
difficulty: Medium
order: 1
tags: SOLID, open/closed, dependency inversion, interfaces, strategy, unique_ptr
time_limit: 3
---
## Statement
A robot-rental company keeps adding pricing rules. Build the engine so that **new rules never require editing it** (open/closed), and so it depends on an **abstract rate provider** rather than a database (dependency inversion). The judge adds a rule class of its own and plugs in a fake rate provider.

```cpp
struct Rental { std::string robot_class; int hours; bool weekend; int past_rentals; std::string coupon; };

struct RateProvider {                                // abstraction owned by the pricing layer
    virtual ~RateProvider() = default;
    virtual std::optional<long> hourly_cents(const std::string& robot_class) const = 0;
};
struct PricingRule {
    virtual ~PricingRule() = default;
    virtual std::string name() const = 0;
    virtual long apply(const Rental& r, long cents) const = 0;   // returns the new price
};
struct Quote { long base; long total; std::vector<std::pair<std::string, long>> steps; };
```

**`PricingEngine`**
- `explicit PricingEngine(const RateProvider&)` stores a reference to the provider (it doesn't own it).
- `void add_rule(std::unique_ptr<PricingRule>)` adds a rule. A null pointer throws `std::invalid_argument`.
- `Quote quote(const Rental&) const`:
  - An unknown class throws `std::invalid_argument("unknown robot class <c>")`.
  - `hours < 1` throws `std::invalid_argument("hours must be >= 1")`.
  - Otherwise `base = hours × hourly rate`. The rules are applied **in insertion order**, each step is recorded as `(name, price after the rule)`, and `total` is the final price.

**Built-in rules** (integer cents, using integer division):

| Rule | `name()` | Effect |
|---|---|---|
| `WeekendSurcharge(pct)` | `"weekend+<pct>%"` | if `weekend`: `p += p*pct/100` |
| `LoyaltyDiscount(min_rentals, pct)` | `"loyalty-<pct>%"` | if `past_rentals >= min_rentals`: `p -= p*pct/100` |
| `CouponRule(std::map<std::string,long> codes)` | `"coupon"` | if the coupon is in the map: `p = max(0, p - codes[coupon])` |
| `MinimumCharge(cents)` | `"minimum"` | `p = max(p, cents)` |

Also provide **`MapRateProvider`**, a `RateProvider` built from `std::map<std::string, long>`.

## Starter
```cpp
#include <map>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

struct Rental { std::string robot_class; int hours; bool weekend; int past_rentals; std::string coupon; };
struct RateProvider {
    virtual ~RateProvider() = default;
    virtual std::optional<long> hourly_cents(const std::string& robot_class) const = 0;
};
struct PricingRule {
    virtual ~PricingRule() = default;
    virtual std::string name() const = 0;
    virtual long apply(const Rental& r, long cents) const = 0;
};
struct Quote { long base; long total; std::vector<std::pair<std::string, long>> steps; };

class PricingEngine {                                 // hard-coded rules: must be edited for every change
public:
    explicit PricingEngine(const RateProvider& rates) : rates_(rates) {}
    void add_rule(std::unique_ptr<PricingRule>) {}
    Quote quote(const Rental& r) const {
        long p = r.hours * rates_.hourly_cents(r.robot_class).value_or(0);
        long base = p;
        if (r.weekend) p += p / 5;
        return {base, p, {}};
    }
private:
    const RateProvider& rates_;
};
```

## Driver
```cpp
#include <cstdio>
#include <iostream>

struct FakeRates : RateProvider {                     // test double: no database needed
    mutable int calls = 0;
    std::optional<long> hourly_cents(const std::string& c) const override {
        ++calls;
        if (c == "rover") return 1500;
        if (c == "arm") return 4000;
        if (c == "drone") return 2500;
        return std::nullopt;
    }
};
struct NightOwlRule : PricingRule {                   // a rule the engine has never seen
    std::string name() const override { return "night-owl"; }
    long apply(const Rental& r, long p) const override { return r.hours >= 10 ? p - 999 : p; }
};

static void show(const PricingEngine& e, const Rental& r) {
    try {
        Quote q = e.quote(r);
        std::printf("%s x%dh: base %ld ->", r.robot_class.c_str(), r.hours, q.base);
        for (auto& [n, v] : q.steps) std::printf(" [%s %ld]", n.c_str(), v);
        std::printf(" = %ld\n", q.total);
    } catch (const std::invalid_argument& ex) { std::printf("error: %s\n", ex.what()); }
}

int main() {
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "rules") {
            FakeRates rates;
            PricingEngine e(rates);
            e.add_rule(std::make_unique<WeekendSurcharge>(25));
            e.add_rule(std::make_unique<LoyaltyDiscount>(5, 10));
            e.add_rule(std::make_unique<CouponRule>(std::map<std::string, long>{{"ROBO10", 1000}, {"FREE", 1000000}}));
            e.add_rule(std::make_unique<MinimumCharge>(2000));
            show(e, {"rover", 3, false, 0, ""});
            show(e, {"rover", 3, true, 0, ""});
            show(e, {"arm", 2, true, 7, "ROBO10"});
            show(e, {"drone", 1, false, 5, "FREE"});
            show(e, {"drone", 1, false, 4, "BOGUS"});
            show(e, {"tank", 1, false, 0, ""});
            show(e, {"rover", 0, false, 0, ""});
            try { e.add_rule(nullptr); } catch (const std::invalid_argument&) { std::printf("null rule rejected\n"); }
            std::printf("provider calls: %d\n", rates.calls);
        } else if (cmd == "extend") {
            FakeRates rates;
            PricingEngine e(rates);
            e.add_rule(std::make_unique<NightOwlRule>());
            e.add_rule(std::make_unique<MinimumCharge>(500));
            show(e, {"rover", 12, false, 0, ""});
            show(e, {"rover", 9, false, 0, ""});
            MapRateProvider real({{"rover", 1200}, {"forklift", 9000}});
            PricingEngine e2(real);
            e2.add_rule(std::make_unique<LoyaltyDiscount>(1, 50));
            e2.add_rule(std::make_unique<WeekendSurcharge>(10));
            show(e2, {"forklift", 4, true, 1, ""});
            show(e2, {"rover", 1, true, 0, ""});
            show(e2, {"drone", 1, true, 0, ""});
        } else if (cmd == "bulk") {
            MapRateProvider rates({{"rover", 1500}, {"arm", 4000}, {"drone", 2500}});
            PricingEngine e(rates);
            e.add_rule(std::make_unique<WeekendSurcharge>(15));
            e.add_rule(std::make_unique<LoyaltyDiscount>(3, 7));
            e.add_rule(std::make_unique<CouponRule>(std::map<std::string, long>{{"A", 300}, {"B", 2500}}));
            e.add_rule(std::make_unique<MinimumCharge>(1800));
            long long sum = 0; const char* cls[] = {"rover", "arm", "drone"}; const char* cps[] = {"", "A", "B", "X"};
            for (int i = 0; i < 200000; ++i) sum += e.quote({cls[i % 3], 1 + i % 12, i % 7 >= 5, i % 9, cps[i % 4]}).total;
            std::printf("revenue %lld\n", sum);
        }
    }
}
```

## Tests
=== sample
rules
---
rover x3h: base 4500 -> [weekend+25% 4500] [loyalty-10% 4500] [coupon 4500] [minimum 4500] = 4500
rover x3h: base 4500 -> [weekend+25% 5625] [loyalty-10% 5625] [coupon 5625] [minimum 5625] = 5625
arm x2h: base 8000 -> [weekend+25% 10000] [loyalty-10% 9000] [coupon 8000] [minimum 8000] = 8000
drone x1h: base 2500 -> [weekend+25% 2500] [loyalty-10% 2250] [coupon 0] [minimum 2000] = 2000
drone x1h: base 2500 -> [weekend+25% 2500] [loyalty-10% 2500] [coupon 2500] [minimum 2500] = 2500
error: unknown robot class tank
error: hours must be >= 1
null rule rejected
provider calls: 7
=== hidden
extend
---
rover x12h: base 18000 -> [night-owl 17001] [minimum 17001] = 17001
rover x9h: base 13500 -> [night-owl 13500] [minimum 13500] = 13500
forklift x4h: base 36000 -> [loyalty-50% 18000] [weekend+10% 19800] = 19800
rover x1h: base 1200 -> [loyalty-50% 1200] [weekend+10% 1320] = 1320
error: unknown robot class drone
=== hidden
bulk
---
revenue 3377915893

## Hints
- The engine holds `const RateProvider&` and `std::vector<std::unique_ptr<PricingRule>>`. `quote` asks the provider **once**, computes the base, then folds the price through the rules.
- Each built-in rule is a small class deriving from `PricingRule`, with its parameters as `const` members set by an `explicit` constructor.
- `name()` strings: `"weekend+" + std::to_string(pct) + "%"`.
- `MapRateProvider` stores the map and returns `std::nullopt` for unknown classes.

## Solution
```cpp
#include <algorithm>
#include <map>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

struct Rental { std::string robot_class; int hours; bool weekend; int past_rentals; std::string coupon; };
struct RateProvider {
    virtual ~RateProvider() = default;
    virtual std::optional<long> hourly_cents(const std::string& robot_class) const = 0;
};
struct PricingRule {
    virtual ~PricingRule() = default;
    virtual std::string name() const = 0;
    virtual long apply(const Rental& r, long cents) const = 0;
};
struct Quote { long base; long total; std::vector<std::pair<std::string, long>> steps; };

class PricingEngine {
public:
    explicit PricingEngine(const RateProvider& rates) : rates_(rates) {}

    void add_rule(std::unique_ptr<PricingRule> rule) {
        if (!rule) throw std::invalid_argument("rule must not be null");
        rules_.push_back(std::move(rule));
    }

    Quote quote(const Rental& r) const {
        auto rate = rates_.hourly_cents(r.robot_class);
        if (!rate) throw std::invalid_argument("unknown robot class " + r.robot_class);
        if (r.hours < 1) throw std::invalid_argument("hours must be >= 1");
        Quote q{static_cast<long>(r.hours) * *rate, 0, {}};
        long price = q.base;
        for (const auto& rule : rules_) {             // closed for modification, open for extension
            price = rule->apply(r, price);
            q.steps.emplace_back(rule->name(), price);
        }
        q.total = price;
        return q;
    }

private:
    const RateProvider& rates_;                       // depends on the abstraction, not a database
    std::vector<std::unique_ptr<PricingRule>> rules_;
};

class WeekendSurcharge : public PricingRule {
public:
    explicit WeekendSurcharge(long pct) : pct_(pct) {}
    std::string name() const override { return "weekend+" + std::to_string(pct_) + "%"; }
    long apply(const Rental& r, long p) const override { return r.weekend ? p + p * pct_ / 100 : p; }
private:
    const long pct_;
};

class LoyaltyDiscount : public PricingRule {
public:
    LoyaltyDiscount(int min_rentals, long pct) : min_(min_rentals), pct_(pct) {}
    std::string name() const override { return "loyalty-" + std::to_string(pct_) + "%"; }
    long apply(const Rental& r, long p) const override { return r.past_rentals >= min_ ? p - p * pct_ / 100 : p; }
private:
    const int min_;
    const long pct_;
};

class CouponRule : public PricingRule {
public:
    explicit CouponRule(std::map<std::string, long> codes) : codes_(std::move(codes)) {}
    std::string name() const override { return "coupon"; }
    long apply(const Rental& r, long p) const override {
        auto it = codes_.find(r.coupon);
        return it == codes_.end() ? p : std::max(0L, p - it->second);
    }
private:
    const std::map<std::string, long> codes_;
};

class MinimumCharge : public PricingRule {
public:
    explicit MinimumCharge(long cents) : min_(cents) {}
    std::string name() const override { return "minimum"; }
    long apply(const Rental&, long p) const override { return std::max(p, min_); }
private:
    const long min_;
};

class MapRateProvider : public RateProvider {
public:
    explicit MapRateProvider(std::map<std::string, long> rates) : rates_(std::move(rates)) {}
    std::optional<long> hourly_cents(const std::string& c) const override {
        auto it = rates_.find(c);
        if (it == rates_.end()) return std::nullopt;
        return it->second;
    }
private:
    std::map<std::string, long> rates_;
};
```

- **Open/closed**: the engine folds the price through a list of `PricingRule` objects, so the judge's `NightOwlRule`, a class the engine has never seen, works without touching `PricingEngine`. The starter's hard-coded weekend logic needs an edit for every business change.
- **Dependency inversion**: the engine depends on the `RateProvider` abstraction. Tests inject `FakeRates` (and count its calls), and production would inject a database-backed provider.
- **Single responsibility**: each rule encodes one business policy, and the engine only orchestrates. Rules are stateless and `const`, so one engine can serve many threads.
- **Liskov**: every rule honours the same contract (take a price, return a price, never throw), so the engine can treat them uniformly. `steps` makes each rule's effect auditable, which pricing teams always ask for.
