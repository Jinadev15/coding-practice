# Case Study: Parking Lot in C++

"Design a parking lot" is the most common object-oriented design interview question, because it tests requirements analysis, class modelling, data structures and extensibility in one problem. This case study works through it as a professional would: requirements, domain model, the key data-structure decision (finding the nearest free spot in O(log n)), pricing with the Strategy pattern, error handling, and the C++ ownership choices, ending with a multi-file implementation (the judged problem).

## 1. Requirements (clarify first)

- Multiple **levels**, each with numbered **spots** of three sizes: `Small` (motorcycle), `Compact` (car) and `Large` (truck or van).
- **Vehicles** fit spots of their size or larger: a motorcycle fits anywhere, and a truck only in Large.
- **Park**: assign the *nearest* suitable free spot (lowest level, then lowest number, then smallest fitting size) and issue a **ticket** with the entry time.
- **Leave**: compute the **fee** from the duration and the vehicle type using pluggable pricing, and free the spot.
- Queries: free spots per size, and occupancy.
- Errors: lot full, unknown ticket, the same vehicle parked twice.

## 2. Domain model

```mermaid
classDiagram
    class ParkingLot {
        +park(Vehicle, time) Ticket
        +leave(ticketId, time) Receipt
        +free_count(SpotSize) int
    }
    class Level { +id; +spots }
    class Spot { +level; +number; +size; +occupant }
    class Ticket { +id; +plate; +spot; +entry }
    class PricingPolicy { <<interface>> +fee(VehicleType, minutes) }
    ParkingLot "1" *-- "many" Level
    Level "1" *-- "many" Spot
    ParkingLot --> PricingPolicy
    ParkingLot "1" o-- "many" Ticket
```

- `Vehicle` is a **value** (plate plus type), and `Ticket` and `Receipt` are values.
- `Spot` objects are **entities** owned by their level. They never move, so they can be identified by `(level, number)`.
- The `PricingPolicy` is injected (DIP and Strategy): hourly, flat-rate, or weekend rules are new classes.

## 3. The data-structure decision

A naive `park` scans every spot (O(N)). With thousands of spots and frequent events, keep a **sorted set of free spots per size**:

```cpp
struct SpotKey {
    int level, number;
    auto operator<=>(const SpotKey&) const = default;   // lexicographic: nearest first
};
std::array<std::set<SpotKey>, 3> free_;                  // one ordered set per SpotSize
```

`park` checks each size from the vehicle's minimum upward, taking `begin()` of each non-empty set and choosing the nearest candidate (the smallest key, with the smaller size breaking ties). That's O(log N) for insert and erase. `leave` reinserts the key. Tickets are in an `unordered_map<TicketId, Ticket>`, and a `unordered_set<std::string>` of plates detects double parking.

## 4. Pricing as a strategy

```cpp
struct PricingPolicy {
    virtual ~PricingPolicy() = default;
    virtual long fee_cents(VehicleType t, long minutes) const = 0;
};

class HourlyPricing : public PricingPolicy {
public:
    long fee_cents(VehicleType t, long minutes) const override {
        static constexpr long rate[] = {100, 250, 400};          // per started hour: moto, car, truck
        long hours = (minutes + 59) / 60;                         // round up started hours
        return std::max(1L, hours) * rate[static_cast<int>(t)];   // minimum one hour
    }
};
```

Money is **integer cents**. Policies are stateless, so one instance can be shared.

## 5. Error handling

Interview-grade code makes failure explicit: `std::expected<Ticket, ParkError>` (C++23), where `ParkError` is an enum class with `Full`, `AlreadyParked` and `UnknownTicket`. Exceptions are reasonable too, but `expected` puts the business outcomes in the type signature and keeps them cheap.

## 6. Extensions interviewers ask about

- **Concurrency** (several gates): put a mutex around the lot, or per-size locks with a consistent lock ordering. Tickets get unique ids from an atomic counter.
- **Reservations** and **EV charging spots**: a new spot attribute plus a filter in allocation. Thanks to the per-size free sets and the injected policy, these touch little existing code (OCP).
- **Persistence**: serialise tickets and occupancy. Spot keys are stable ids, which makes this straightforward.

> [!EXAM]
> **How would you find the nearest free parking spot efficiently, and why does the choice matter for the design?**
> Keep, for each spot size, an ordered set (a balanced BST such as `std::set`) of free spot keys ordered by (level, number). Parking examines the first element of each size set that's large enough, and picks the minimum: O(k log N) for k sizes, effectively O(log N). Leaving reinserts the key in O(log N). A linear scan costs O(N) per event and degrades as the lot grows. Encapsulating this index inside `ParkingLot` means callers only see `park` and `leave`, so the allocation strategy can change (to reservations or EV spots, for example) without affecting clients.
