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
