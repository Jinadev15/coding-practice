# Case Study: Parking Lot

The parking-lot problem appears in almost every object-oriented design interview. The Python version here adds a twist that real systems have: **reservations over time intervals** and **electric-vehicle charging spots**. That forces a careful model of availability, plus interval logic, on top of the classic class design.

## 1. Requirements

- **Spots** have a size (`motorcycle`, `compact`, `large`), a level, a number, and optionally an **EV charger**.
- **Vehicles** have a plate, a size, and an `electric` flag. A vehicle fits a spot of its size or larger. **EVs prefer charger spots** but may use regular ones. Non-EVs take charger spots only if nothing else fits.
- **Walk-in parking**: allocate the best spot now (preferred kind first, then the smallest fitting size, then the lowest level and number) and issue a ticket.
- **Reservations**: reserve a spot of a given size for an interval `[start, end)`. A walk-in can't take a spot that's reserved at any time during the next hour.
- **Exit**: the fee is computed by an injected pricing policy. EV charging adds a per-hour energy fee.

## 2. Model and responsibilities

| Class | Kind | Responsibility |
|---|---|---|
| `Interval` | value | `[start, end)` with `overlaps()` |
| `Spot` | entity | its size, charger, current occupant, list of reservation intervals; `is_free(at, horizon)` |
| `Vehicle` | value | plate, size, electric |
| `Ticket` | value | ticket id, plate, spot, entry time |
| `PricingPolicy` (Protocol) | strategy | `fee(ticket, exit_time) -> Decimal` |
| `ParkingLot` | aggregate | allocation, reservations, tickets, indices |

## 3. Allocation as a ranking

The "best spot" rule is a **sort key**. Python tuples compare lexicographically, which makes multi-criteria choices declarative:

```python
def allocation_key(spot: Spot, vehicle: Vehicle) -> tuple:
    preferred = spot.has_charger == vehicle.electric      # EVs prefer chargers, others prefer non-chargers
    return (not preferred, spot.size.value, spot.level, spot.number)

candidates = [s for s in lot.spots if s.fits(vehicle) and s.is_free(now, horizon=60)]
best = min(candidates, key=lambda s: allocation_key(s, vehicle), default=None)
```

For large lots, keep indices (a heap or sorted container per category). The key function stays the single definition of "best".

## 4. Interval logic

```python
@dataclass(frozen=True)
class Interval:
    start: int     # minutes since opening
    end: int
    def __post_init__(self):
        if self.end <= self.start:
            raise ValueError("empty interval")
    def overlaps(self, other: "Interval") -> bool:
        return self.start < other.end and other.start < self.end     # half-open intervals
```

Half-open intervals make back-to-back bookings (`[60, 120)` then `[120, 180)`) not overlap, which is what users expect.

## 5. Strategy for pricing

```python
class HourlyPricing:
    def __init__(self, rates: dict[Size, Decimal], ev_rate: Decimal):
        self.rates, self.ev_rate = rates, ev_rate
    def fee(self, ticket: Ticket, exit_min: int) -> Decimal:
        hours = max(1, -(-(exit_min - ticket.entry) // 60))          # ceiling division, minimum 1 hour
        energy = self.ev_rate * hours if ticket.charging else Decimal(0)
        return self.rates[ticket.size] * hours + energy
```

New pricing schemes (weekend, member discounts) are new classes passed to the lot's constructor (OCP and DIP).

> [!EXAM]
> **How would you design spot allocation so that changing the "best spot" policy doesn't require rewriting the parking lot?**
> Separate the policy from the mechanism. The lot collects candidate spots that fit the vehicle and are free for the required horizon (the mechanism), and a single key function or injected policy object ranks them: preferred kind (EV charger match), then the smallest fitting size, then the lowest level and number, expressed as a tuple so `min(..., key=...)` picks the best. Changing the policy means supplying a different key or policy object. For performance, the same ranking defines the ordering of per-category indices (heaps or sorted lists), so the policy stays the single source of truth.

## Worked example: a tiny end-to-end run

Before reading the full design, follow one car through a minimal version of the system:

```python
from dataclasses import dataclass, field
from enum import Enum

class Size(Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3

@dataclass
class Spot:
    id: str
    size: Size
    car: str | None = None

@dataclass
class Lot:
    spots: list[Spot]
    tickets: dict[str, tuple[str, int]] = field(default_factory=dict)   # plate -> (spot id, entry minute)

    def park(self, plate: str, size: Size, minute: int) -> str:
        # smallest free spot that fits: don't waste large spots on small cars
        free = [s for s in self.spots if s.car is None and s.size.value >= size.value]
        if not free:
            raise RuntimeError("lot full")
        spot = min(free, key=lambda s: (s.size.value, s.id))
        spot.car = plate
        self.tickets[plate] = (spot.id, minute)
        return spot.id

    def leave(self, plate: str, minute: int, rate_per_hour: int = 20) -> int:
        spot_id, start = self.tickets.pop(plate)
        next(s for s in self.spots if s.id == spot_id).car = None
        hours = max(1, -(-(minute - start) // 60))      # ceiling division, minimum one hour
        return hours * rate_per_hour

lot = Lot([Spot("A1", Size.SMALL), Spot("B1", Size.MEDIUM), Spot("C1", Size.LARGE)])
print(lot.park("KA01", Size.SMALL, 0))     # A1
print(lot.park("KA02", Size.SMALL, 5))     # B1 (A1 taken; B1 is the next smallest that fits)
print(lot.leave("KA01", 130))              # 130 minutes -> 3 hours -> 60
```

```output
A1
B1
60
```

The case study then improves each part:

- the ranking rule becomes a **strategy**
- the fee calculation becomes a **pricing policy**
- reservations need **interval overlap** logic

## Common mistakes

- **Putting all the logic in `Lot`.** Fees, allocation and reservations change for different reasons, so give each its own object.
- **Overlap bugs.** Two bookings `[a, b)` and `[c, d)` overlap exactly when `a < d and c < b`. Using `<=` double-books the minute one booking ends and the next begins.
- **Floating-point money.** Use integer paise or cents, or `Decimal`.

## Check your understanding

1. Why use half-open intervals `[start, end)` for reservations?
2. How would you add a weekend surcharge without editing `Lot`?

<details><summary>Answers</summary>

1. Back-to-back bookings (one ends at 10:00, the next starts at 10:00) don't overlap, and the length is simply `end - start`.
2. Make pricing a strategy object passed to `Lot` (for example `WeekendPricing(base)`), so `Lot` just calls `pricing.fee(ticket)`.

</details>
