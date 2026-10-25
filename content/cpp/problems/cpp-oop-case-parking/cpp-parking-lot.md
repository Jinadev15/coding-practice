---
id: cpp-parking-lot
title: "Case Study: Parking Lot (Multi-File)"
difficulty: Hard
order: 1
tags: object-oriented design, case study, strategy, std::expected, ordered sets, pimpl, multi-file
time_limit: 4
---
## Statement
Implement the parking lot from the case-study lesson behind the given `parking.hpp`, in **`parking.cpp`**. The header hides all data structures behind a pimpl, so you choose them, but `park` and `leave` must be **O(log n)**: the hidden test runs 300,000 operations on a 4,000-spot lot.

**Layout**
- `levels[i] = {small, compact, large}` spot counts.
- On each level, spots are numbered from 1: small spots first, then compact, then large.
- `SpotId{level, number}` orders lexicographically, and "nearest" means the smallest `SpotId`.

**`park(vehicle, now)`**
- A motorcycle fits any spot, a car fits compact or large, and a truck fits large only.
- Choose the **nearest free spot among all sizes the vehicle fits**.
- Tickets are numbered 1, 2, 3, …
- Errors: a plate that's already parked gives `AlreadyParked`, and no spot gives `Full`.

**`leave(ticket, now)`**
- `UnknownTicket` for an unknown or already-used ticket, and `InvalidTime` if `now < entry`.
- Otherwise, a receipt with the minutes parked and the fee from the injected `PricingPolicy`, and the spot is freed.

**`HourlyPricing`**
- **0** for up to 15 minutes (the grace period).
- Otherwise, per **started** hour (minimum 1): motorcycle 100, car 250, truck 400 cents.

Also implement `free_count(size)`, `occupied()` and `occupant(spot)`.

## Starter: parking.hpp
```cpp
#pragma once
#include <array>
#include <compare>
#include <expected>
#include <memory>
#include <optional>
#include <string>
#include <vector>

enum class SpotSize { Small, Compact, Large };
enum class VehicleType { Motorcycle, Car, Truck };
enum class ParkError { Full, AlreadyParked, UnknownTicket, InvalidTime };

struct Vehicle { std::string plate; VehicleType type; };
struct SpotId {
    int level, number;
    auto operator<=>(const SpotId&) const = default;
};
struct Ticket { long id; std::string plate; VehicleType type; SpotId spot; SpotSize size; long entry_min; };
struct Receipt { long ticket; std::string plate; SpotId spot; long minutes; long fee_cents; };

struct PricingPolicy {
    virtual ~PricingPolicy() = default;
    virtual long fee_cents(VehicleType type, long minutes) const = 0;
};

class HourlyPricing : public PricingPolicy {
public:
    long fee_cents(VehicleType type, long minutes) const override;
};

class ParkingLot {
public:
    // levels[i] = {small, compact, large} spot counts; numbering per level: small first, then compact, then large, from 1
    ParkingLot(std::vector<std::array<int, 3>> levels, std::shared_ptr<const PricingPolicy> pricing);
    ~ParkingLot();
    ParkingLot(const ParkingLot&) = delete;
    ParkingLot& operator=(const ParkingLot&) = delete;

    std::expected<Ticket, ParkError> park(const Vehicle& v, long now_min);
    std::expected<Receipt, ParkError> leave(long ticket_id, long now_min);
    int free_count(SpotSize s) const;
    int occupied() const;
    std::optional<std::string> occupant(SpotId spot) const;

private:
    struct State;
    std::unique_ptr<State> st_;                 // pimpl: data structures are an implementation detail
};
```

## Starter: parking.cpp
```cpp
#include "parking.hpp"

long HourlyPricing::fee_cents(VehicleType, long minutes) const { return minutes * 5; }

struct ParkingLot::State { std::vector<std::array<int, 3>> levels; };

ParkingLot::ParkingLot(std::vector<std::array<int, 3>> levels, std::shared_ptr<const PricingPolicy>) : st_(new State{levels}) {}
ParkingLot::~ParkingLot() = default;
std::expected<Ticket, ParkError> ParkingLot::park(const Vehicle&, long) { return std::unexpected(ParkError::Full); }
std::expected<Receipt, ParkError> ParkingLot::leave(long, long) { return std::unexpected(ParkError::UnknownTicket); }
int ParkingLot::free_count(SpotSize) const { return 0; }
int ParkingLot::occupied() const { return 0; }
std::optional<std::string> ParkingLot::occupant(SpotId) const { return std::nullopt; }
```

## Driver: main.cpp
```cpp
#include <cstdio>
#include <iostream>
#include "parking.hpp"

static const char* err(ParkError e) {
    switch (e) { case ParkError::Full: return "full"; case ParkError::AlreadyParked: return "already parked";
                 case ParkError::UnknownTicket: return "unknown ticket"; default: return "invalid time"; }
}
static const char* sz(SpotSize s) { return s == SpotSize::Small ? "S" : s == SpotSize::Compact ? "C" : "L"; }

static long park(ParkingLot& lot, const char* plate, VehicleType t, long now) {
    auto r = lot.park({plate, t}, now);
    if (!r) { std::printf("park %s: %s\n", plate, err(r.error())); return -1; }
    std::printf("park %s: ticket %ld spot L%d#%d (%s)\n", plate, r->id, r->spot.level, r->spot.number, sz(r->size));
    return r->id;
}
static void leave(ParkingLot& lot, long id, long now) {
    auto r = lot.leave(id, now);
    if (!r) { std::printf("leave %ld: %s\n", id, err(r.error())); return; }
    std::printf("leave %ld: %s %ld min fee %ld\n", id, r->plate.c_str(), r->minutes, r->fee_cents);
}

int main() {
    std::string cmd;
    while (std::cin >> cmd) {
        auto pricing = std::make_shared<HourlyPricing>();
        if (cmd == "basic") {
            ParkingLot lot({{1, 2, 1}, {2, 1, 1}}, pricing);
            long t1 = park(lot, "MOTO-1", VehicleType::Motorcycle, 0);
            long t2 = park(lot, "CAR-1", VehicleType::Car, 5);
            long t3 = park(lot, "TRUCK-1", VehicleType::Truck, 10);
            park(lot, "CAR-2", VehicleType::Car, 12);
            park(lot, "CAR-3", VehicleType::Car, 13);
            park(lot, "TRUCK-2", VehicleType::Truck, 14);
            park(lot, "TRUCK-3", VehicleType::Truck, 15);
            park(lot, "CAR-1", VehicleType::Car, 16);
            std::printf("free S%d C%d L%d occupied %d\n", lot.free_count(SpotSize::Small), lot.free_count(SpotSize::Compact), lot.free_count(SpotSize::Large), lot.occupied());
            leave(lot, t2, 75); leave(lot, t2, 80); leave(lot, t1, 10); leave(lot, t3, 5); leave(lot, t3, 200);
            auto who = lot.occupant({0, 2}); std::printf("L0#2: %s\n", who ? who->c_str() : "(free)");
            park(lot, "MOTO-2", VehicleType::Motorcycle, 210);
            park(lot, "CAR-1", VehicleType::Car, 211);
        } else if (cmd == "fill") {
            ParkingLot lot({{3, 0, 0}}, pricing);
            for (int i = 0; i < 3; ++i) park(lot, ("M" + std::to_string(i)).c_str(), VehicleType::Motorcycle, i);
            park(lot, "C0", VehicleType::Car, 5);
            park(lot, "M9", VehicleType::Motorcycle, 6);
            leave(lot, 2, 61); leave(lot, 1, 16); leave(lot, 3, 15);
            park(lot, "M9", VehicleType::Motorcycle, 70);
            std::printf("occupied %d\n", lot.occupied());
        } else if (cmd == "big") {
            std::vector<std::array<int, 3>> lv(20, std::array<int, 3>{40, 120, 40});
            ParkingLot lot(lv, pricing);
            std::vector<long> open; long fees = 0, full = 0; unsigned x = 3;
            for (int step = 0; step < 300000; ++step) {
                x = x * 1103515245u + 12345u;
                if ((x >> 16) % 3 != 0 || open.empty()) {
                    auto r = lot.park({"P" + std::to_string(step), static_cast<VehicleType>((x >> 8) % 3)}, step);
                    if (r) open.push_back(r->id); else ++full;
                } else {
                    size_t k = (x >> 4) % open.size();
                    auto r = lot.leave(open[k], step + (long)((x >> 12) % 400));
                    if (r) fees += r->fee_cents;
                    open[k] = open.back(); open.pop_back();
                }
            }
            std::printf("occupied %d full %ld fees %ld free S%d C%d L%d\n", lot.occupied(), full, fees,
                        lot.free_count(SpotSize::Small), lot.free_count(SpotSize::Compact), lot.free_count(SpotSize::Large));
        }
    }
}
```

## Tests
=== sample
basic
---
park MOTO-1: ticket 1 spot L0#1 (S)
park CAR-1: ticket 2 spot L0#2 (C)
park TRUCK-1: ticket 3 spot L0#4 (L)
park CAR-2: ticket 4 spot L0#3 (C)
park CAR-3: ticket 5 spot L1#3 (C)
park TRUCK-2: ticket 6 spot L1#4 (L)
park TRUCK-3: full
park CAR-1: already parked
free S2 C0 L0 occupied 6
leave 2: CAR-1 70 min fee 500
leave 2: unknown ticket
leave 1: MOTO-1 10 min fee 0
leave 3: invalid time
leave 3: TRUCK-1 190 min fee 1600
L0#2: (free)
park MOTO-2: ticket 7 spot L0#1 (S)
park CAR-1: ticket 8 spot L0#2 (C)
=== hidden
fill
---
park M0: ticket 1 spot L0#1 (S)
park M1: ticket 2 spot L0#2 (S)
park M2: ticket 3 spot L0#3 (S)
park C0: full
park M9: full
leave 2: M1 60 min fee 100
leave 1: M0 16 min fee 100
leave 3: M2 13 min fee 0
park M9: ticket 4 spot L0#1 (S)
occupied 1
=== hidden
big
---
occupied 3997 full 95429 fees 3677636600 free S1 C2 L0

## Hints
- Keep one `std::set<SpotId>` of free spots per size. For a vehicle, look at `begin()` of each size set it fits, and take the smallest.
- Use `std::unordered_map<long, Ticket>` for open tickets and `std::unordered_set<std::string>` for parked plates. Erase the ticket on `leave`, so a second `leave` reports `UnknownTicket`.
- Store the size of each spot (or the size in the ticket), so `leave` returns the spot to the right set.
- The pimpl's `State` struct is defined in `parking.cpp`. The header already declares the destructor, which you define there with `= default`.

## Solution: parking.hpp
```cpp
#pragma once
#include <array>
#include <compare>
#include <expected>
#include <memory>
#include <optional>
#include <string>
#include <vector>

enum class SpotSize { Small, Compact, Large };
enum class VehicleType { Motorcycle, Car, Truck };
enum class ParkError { Full, AlreadyParked, UnknownTicket, InvalidTime };

struct Vehicle { std::string plate; VehicleType type; };
struct SpotId {
    int level, number;
    auto operator<=>(const SpotId&) const = default;
};
struct Ticket { long id; std::string plate; VehicleType type; SpotId spot; SpotSize size; long entry_min; };
struct Receipt { long ticket; std::string plate; SpotId spot; long minutes; long fee_cents; };

struct PricingPolicy {
    virtual ~PricingPolicy() = default;
    virtual long fee_cents(VehicleType type, long minutes) const = 0;
};

class HourlyPricing : public PricingPolicy {
public:
    long fee_cents(VehicleType type, long minutes) const override;
};

class ParkingLot {
public:
    // levels[i] = {small, compact, large} spot counts; numbering per level: small first, then compact, then large, from 1
    ParkingLot(std::vector<std::array<int, 3>> levels, std::shared_ptr<const PricingPolicy> pricing);
    ~ParkingLot();
    ParkingLot(const ParkingLot&) = delete;
    ParkingLot& operator=(const ParkingLot&) = delete;

    std::expected<Ticket, ParkError> park(const Vehicle& v, long now_min);
    std::expected<Receipt, ParkError> leave(long ticket_id, long now_min);
    int free_count(SpotSize s) const;
    int occupied() const;
    std::optional<std::string> occupant(SpotId spot) const;

private:
    struct State;
    std::unique_ptr<State> st_;                 // pimpl: data structures are an implementation detail
};
```

## Solution: parking.cpp
```cpp
#include "parking.hpp"

#include <algorithm>
#include <map>
#include <set>
#include <unordered_map>
#include <unordered_set>

long HourlyPricing::fee_cents(VehicleType type, long minutes) const {
    if (minutes <= 15) return 0;                                    // grace period
    static constexpr long rate[] = {100, 250, 400};                 // per started hour
    long hours = std::max(1L, (minutes + 59) / 60);
    return hours * rate[static_cast<int>(type)];
}

struct ParkingLot::State {
    std::shared_ptr<const PricingPolicy> pricing;
    std::array<std::set<SpotId>, 3> free;                           // nearest-first free spots per size
    std::map<SpotId, SpotSize> size_of;
    std::map<SpotId, std::string> occupant;
    std::unordered_map<long, Ticket> tickets;
    std::unordered_set<std::string> parked;
    long next_ticket = 1;
};

ParkingLot::ParkingLot(std::vector<std::array<int, 3>> levels, std::shared_ptr<const PricingPolicy> pricing)
    : st_(std::make_unique<State>()) {
    st_->pricing = std::move(pricing);
    for (int lv = 0; lv < static_cast<int>(levels.size()); ++lv) {
        int number = 1;
        for (int s = 0; s < 3; ++s)
            for (int k = 0; k < levels[lv][s]; ++k, ++number) {
                SpotId id{lv, number};
                st_->free[s].insert(id);
                st_->size_of[id] = static_cast<SpotSize>(s);
            }
    }
}

ParkingLot::~ParkingLot() = default;

std::expected<Ticket, ParkError> ParkingLot::park(const Vehicle& v, long now_min) {
    if (st_->parked.contains(v.plate)) return std::unexpected(ParkError::AlreadyParked);
    int best_size = -1;
    for (int s = static_cast<int>(v.type); s < 3; ++s)              // a vehicle fits its size or larger
        if (!st_->free[s].empty() && (best_size < 0 || *st_->free[s].begin() < *st_->free[best_size].begin()))
            best_size = s;
    if (best_size < 0) return std::unexpected(ParkError::Full);
    SpotId spot = *st_->free[best_size].begin();
    st_->free[best_size].erase(st_->free[best_size].begin());
    Ticket t{st_->next_ticket++, v.plate, v.type, spot, static_cast<SpotSize>(best_size), now_min};
    st_->tickets.emplace(t.id, t);
    st_->parked.insert(v.plate);
    st_->occupant[spot] = v.plate;
    return t;
}

std::expected<Receipt, ParkError> ParkingLot::leave(long ticket_id, long now_min) {
    auto it = st_->tickets.find(ticket_id);
    if (it == st_->tickets.end()) return std::unexpected(ParkError::UnknownTicket);
    const Ticket& t = it->second;
    if (now_min < t.entry_min) return std::unexpected(ParkError::InvalidTime);
    long minutes = now_min - t.entry_min;
    Receipt r{t.id, t.plate, t.spot, minutes, st_->pricing->fee_cents(t.type, minutes)};
    st_->free[static_cast<int>(t.size)].insert(t.spot);
    st_->occupant.erase(t.spot);
    st_->parked.erase(t.plate);
    st_->tickets.erase(it);
    return r;
}

int ParkingLot::free_count(SpotSize s) const { return static_cast<int>(st_->free[static_cast<int>(s)].size()); }
int ParkingLot::occupied() const { return static_cast<int>(st_->occupant.size()); }

std::optional<std::string> ParkingLot::occupant(SpotId spot) const {
    auto it = st_->occupant.find(spot);
    if (it == st_->occupant.end()) return std::nullopt;
    return it->second;
}
```

## Solution
- **The right index**: per-size ordered sets make "nearest suitable spot" a few `begin()` lookups, and parking or leaving costs O(log n). The 300,000-operation test would crawl with linear scans.
- **Business outcomes in the type**: `std::expected<Ticket, ParkError>` makes "full", "already parked" and "unknown ticket" ordinary return values that callers must handle, rather than exceptions or magic numbers.
- **Strategy for pricing**: the lot depends on the abstract `PricingPolicy`, shared through `shared_ptr<const ...>`. Weekend rates or EV discounts are new classes, and `ParkingLot` never changes.
- **Pimpl**: the header exposes no containers, so the data structures can change (to an interval tree, or adding reservations) without recompiling clients. `ParkingLot` is non-copyable because a lot is an entity.
- **Value types for records**: `Vehicle`, `SpotId`, `Ticket` and `Receipt` are plain comparable values, so they're easy to log, test and serialise.
