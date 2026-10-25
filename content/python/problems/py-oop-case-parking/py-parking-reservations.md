---
id: py-parking-reservations
title: "Case Study: Parking Lot with Reservations and EV Charging"
difficulty: Hard
order: 1
tags: case study, value objects, intervals, strategy, ranking keys, IntEnum, Decimal
time_limit: 5
---
## Statement
Implement the parking lot from the case-study lesson, including **future reservations** and **EV charger preference**. Times are integers (minutes since opening).

**Values**
- `Size(IntEnum)` is `MOTORCYCLE=0, COMPACT=1, LARGE=2`.
- `Vehicle(plate, size, electric=False)` is frozen.
- `Interval(start, end)` is a frozen **half-open** interval `[start, end)`. `end <= start` raises `ValueError`. It provides `overlaps(other)`.

**`ParkingLot(spots, pricing)`**, where `spots` is a list of `(level, number, size, charger: bool)`.
- A vehicle fits a spot of its size or larger.
- `reserve(size, interval) -> int | None` reserves the best spot for a vehicle of `size` that:
  - is **not currently occupied**;
  - has **no overlapping reservation**.

  Best means a **non-charger** spot first, then the smallest fitting size, then level, then number. Returns a reservation id (1, 2, …), or None.
- `park(vehicle, now) -> int | None` returns a ticket id (1, 2, …), or None when nothing is suitable.
  - A plate that's already parked raises `ValueError`.
  - A candidate spot must fit, be unoccupied, and have **no reservation overlapping `[now, now+60)`**.
  - Ranking key: `(spot.charger != vehicle.electric, size, level, number)`, so EVs prefer chargers and others avoid them.
  - The vehicle is **charging** if it's electric and the spot has a charger.
- `park_reserved(reservation_id, vehicle, now) -> int` parks in the reserved spot and consumes the reservation. It raises `ValueError` for an unknown or used reservation, `now` outside the interval, a vehicle that doesn't fit, or a plate that's already parked.
- `leave(ticket_id, now) -> Decimal` returns the fee from `pricing.fee(ticket, now)` and frees the spot. An unknown ticket raises `KeyError`.
- `spot_of(ticket_id) -> tuple[int, int]` and `occupied() -> int`.

**`Ticket`** (a frozen dataclass) has `id, plate, size, spot (level, number), entry, charging`.

**`HourlyPricing(rates: dict[Size, Decimal], ev_rate: Decimal)`** charges `hours = max(1, ceil((now − entry) / 60))`, and `fee = rates[size]·hours + (ev_rate·hours if charging else 0)`.

## Starter
```python
from dataclasses import dataclass
from decimal import Decimal
from enum import IntEnum


class Size(IntEnum):
    MOTORCYCLE = 0
    COMPACT = 1
    LARGE = 2


@dataclass
class Vehicle:
    plate: str
    size: Size
    electric: bool = False


@dataclass
class Interval:
    start: int
    end: int


class HourlyPricing:
    def __init__(self, rates, ev_rate):
        self.rates = rates

    def fee(self, ticket, now):
        return self.rates[ticket.size]


class ParkingLot:
    def __init__(self, spots, pricing):
        self.free = list(spots)

    def park(self, vehicle, now):
        return 1 if self.free else None
```

## Driver
```python
import sys
from decimal import Decimal

def attempt(label, fn):
    try:
        print(f"{label}: {fn()}")
    except (ValueError, KeyError) as e:
        print(f"{label}: {type(e).__name__}")

pricing = HourlyPricing({Size.MOTORCYCLE: Decimal("1.00"), Size.COMPACT: Decimal("2.50"), Size.LARGE: Decimal("4.00")}, Decimal("1.50"))
S, C, L = Size.MOTORCYCLE, Size.COMPACT, Size.LARGE

for cmd in sys.stdin.read().split():
    if cmd == "values":
        attempt("empty interval", lambda: Interval(10, 10))
        a, b, c = Interval(60, 120), Interval(120, 180), Interval(100, 130)
        print(a.overlaps(b), a.overlaps(c), c.overlaps(b), Interval(0, 1000).overlaps(a))
        v = Vehicle("EV-1", C, True)
        try:
            v.plate = "X"
        except Exception as e:
            print("vehicle immutable:", type(e).__name__)
        print(hash(Interval(1, 2)) == hash(Interval(1, 2)))
    elif cmd == "park":
        lot = ParkingLot([(0, 1, S, False), (0, 2, C, True), (0, 3, C, False), (1, 1, L, False), (1, 2, L, True)], pricing)
        t1 = lot.park(Vehicle("EV-CAR", C, True), 0); print("EV car ->", lot.spot_of(t1))
        t2 = lot.park(Vehicle("GAS-CAR", C), 5); print("gas car ->", lot.spot_of(t2))
        t3 = lot.park(Vehicle("MOTO", S), 6); print("moto ->", lot.spot_of(t3))
        t4 = lot.park(Vehicle("MOTO-2", S), 7); print("moto 2 ->", lot.spot_of(t4))
        t5 = lot.park(Vehicle("TRUCK", L), 8); print("truck ->", lot.spot_of(t5) if t5 else None)
        attempt("dup plate", lambda: lot.park(Vehicle("MOTO", S), 9))
        print("full for EV truck:", lot.park(Vehicle("EV-TRUCK", L, True), 10), "occupied", lot.occupied())
        attempt("fee EV car 125 min", lambda: lot.leave(t1, 125))
        attempt("fee gas 10 min", lambda: lot.leave(t2, 15))
        attempt("leave again", lambda: lot.leave(t2, 20))
        attempt("fee truck 3h", lambda: lot.leave(t5, 188))
        t6 = lot.park(Vehicle("EV-TRUCK", L, True), 190); print("EV truck ->", lot.spot_of(t6))
    elif cmd == "reserve":
        lot = ParkingLot([(0, 1, C, False), (0, 2, C, False), (0, 3, C, True), (0, 4, L, False)], pricing)
        r1 = lot.reserve(C, Interval(100, 200)); r2 = lot.reserve(C, Interval(150, 250)); r3 = lot.reserve(C, Interval(200, 300))
        print("reservations", r1, r2, r3)
        t = lot.park(Vehicle("EARLY", C), 50); print("walk-in at 50 ->", lot.spot_of(t))
        t2 = lot.park(Vehicle("LATER", C), 95); print("walk-in at 95 ->", lot.spot_of(t2) if t2 else None)
        attempt("reserved too early", lambda: lot.park_reserved(r1, Vehicle("R1", C), 90))
        attempt("reserved wrong size", lambda: lot.park_reserved(r1, Vehicle("BIG", L), 110))
        tr = lot.park_reserved(r1, Vehicle("R1", C), 110); print("reserved park ->", lot.spot_of(tr))
        attempt("reuse reservation", lambda: lot.park_reserved(r1, Vehicle("R1B", C), 120))
        attempt("unknown reservation", lambda: lot.park_reserved(99, Vehicle("R9", C), 120))
        print("reserve while occupied:", lot.reserve(L, Interval(400, 500)), lot.reserve(C, Interval(400, 500)))
        attempt("fee reserved", lambda: lot.leave(tr, 230))
    elif cmd == "load":
        spots = [(lv, n, Size(n % 3), n % 10 == 0) for lv in range(10) for n in range(1, 101)]
        lot = ParkingLot(spots, pricing)
        tickets, revenue, rejected, x = [], Decimal("0"), 0, 11
        for step in range(30000):
            x = (x * 1103515245 + 12345) % (1 << 31)
            now = step * 2
            if x % 3 and len(tickets) < 1500:
                t = lot.park(Vehicle(f"P{step}", Size(x % 3), x % 7 == 0), now)
                if t: tickets.append(t)
                else: rejected += 1
            elif tickets:
                revenue += lot.leave(tickets.pop((x >> 4) % len(tickets)), now + (x % 300))
            if step % 500 == 0:
                lot.reserve(Size(x % 3), Interval(now + 100, now + 400))
        print("occupied", lot.occupied(), "rejected", rejected, "revenue", revenue)
```

## Tests
=== sample
values
park
---
empty interval: ValueError
False True True True
vehicle immutable: FrozenInstanceError
True
EV car -> (0, 2)
gas car -> (0, 3)
moto -> (0, 1)
moto 2 -> (1, 1)
truck -> (1, 2)
dup plate: ValueError
full for EV truck: None occupied 5
fee EV car 125 min: 12.00
fee gas 10 min: 2.50
leave again: KeyError
fee truck 3h: 12.00
EV truck -> (1, 2)
=== hidden
reserve
---
reservations 1 2 3
walk-in at 50 -> (0, 2)
walk-in at 95 -> (0, 4)
reserved too early: ValueError
reserved wrong size: ValueError
reserved park -> (0, 1)
reuse reservation: ValueError
unknown reservation: ValueError
reserve while occupied: None 4
fee reserved: 5.00
=== hidden
load
---
occupied 669 rejected 9357 revenue 1957460.00

## Hints
- `Interval.overlaps`: `self.start < other.end and other.start < self.end`. Half-open intervals make back-to-back bookings compatible.
- Each spot keeps its `occupant` (a ticket id or None) and a list of `(reservation_id, Interval)`.
- Ranking: `min(candidates, key=lambda s: (s.charger != v.electric, s.size, s.level, s.number))`. For reservations use `(s.charger, s.size, s.level, s.number)`.
- `ceil` without floats: `-(-minutes // 60)`.

## Solution
```python
from dataclasses import dataclass, field
from decimal import Decimal
from enum import IntEnum
from itertools import count


class Size(IntEnum):
    MOTORCYCLE = 0
    COMPACT = 1
    LARGE = 2


@dataclass(frozen=True)
class Vehicle:
    plate: str
    size: Size
    electric: bool = False


@dataclass(frozen=True)
class Interval:
    start: int
    end: int

    def __post_init__(self):
        if self.end <= self.start:
            raise ValueError("interval must have end > start")

    def overlaps(self, other: "Interval") -> bool:
        return self.start < other.end and other.start < self.end


@dataclass(frozen=True)
class Ticket:
    id: int
    plate: str
    size: Size
    spot: tuple[int, int]
    entry: int
    charging: bool


@dataclass
class Spot:
    level: int
    number: int
    size: Size
    charger: bool
    occupant: int | None = None
    reservations: dict[int, Interval] = field(default_factory=dict)

    def fits(self, size: Size) -> bool:
        return self.size >= size

    def reserved_during(self, window: Interval) -> bool:
        return any(iv.overlaps(window) for iv in self.reservations.values())


class HourlyPricing:
    def __init__(self, rates: dict[Size, Decimal], ev_rate: Decimal):
        self.rates, self.ev_rate = rates, ev_rate

    def fee(self, ticket: Ticket, now: int) -> Decimal:
        hours = max(1, -(-(now - ticket.entry) // 60))
        return self.rates[ticket.size] * hours + (self.ev_rate * hours if ticket.charging else Decimal(0))


class ParkingLot:
    def __init__(self, spots, pricing):
        self._spots = [Spot(lv, n, Size(sz), bool(ch)) for lv, n, sz, ch in spots]
        self._pricing = pricing
        self._tickets: dict[int, tuple[Ticket, Spot]] = {}
        self._parked: set[str] = set()
        self._reservations: dict[int, tuple[Spot, Interval, Size]] = {}
        self._ticket_ids, self._reservation_ids = count(1), count(1)

    def reserve(self, size: Size, interval: Interval) -> int | None:
        candidates = [s for s in self._spots
                      if s.fits(size) and s.occupant is None and not s.reserved_during(interval)]
        if not candidates:
            return None
        spot = min(candidates, key=lambda s: (s.charger, s.size, s.level, s.number))
        rid = next(self._reservation_ids)
        spot.reservations[rid] = interval
        self._reservations[rid] = (spot, interval, size)
        return rid

    def _issue(self, vehicle: Vehicle, spot: Spot, now: int) -> int:
        tid = next(self._ticket_ids)
        ticket = Ticket(tid, vehicle.plate, vehicle.size, (spot.level, spot.number), now, vehicle.electric and spot.charger)
        spot.occupant = tid
        self._tickets[tid] = (ticket, spot)
        self._parked.add(vehicle.plate)
        return tid

    def park(self, vehicle: Vehicle, now: int) -> int | None:
        if vehicle.plate in self._parked:
            raise ValueError(f"{vehicle.plate} already parked")
        window = Interval(now, now + 60)
        candidates = [s for s in self._spots
                      if s.fits(vehicle.size) and s.occupant is None and not s.reserved_during(window)]
        if not candidates:
            return None
        spot = min(candidates, key=lambda s: (s.charger != vehicle.electric, s.size, s.level, s.number))
        return self._issue(vehicle, spot, now)

    def park_reserved(self, reservation_id: int, vehicle: Vehicle, now: int) -> int:
        if reservation_id not in self._reservations:
            raise ValueError("unknown or used reservation")
        spot, interval, size = self._reservations[reservation_id]
        if not interval.start <= now < interval.end:
            raise ValueError("outside reservation interval")
        if not spot.fits(vehicle.size) or vehicle.size > size:
            raise ValueError("vehicle does not fit the reservation")
        if vehicle.plate in self._parked:
            raise ValueError(f"{vehicle.plate} already parked")
        del self._reservations[reservation_id]
        del spot.reservations[reservation_id]
        return self._issue(vehicle, spot, now)

    def leave(self, ticket_id: int, now: int) -> Decimal:
        ticket, spot = self._tickets.pop(ticket_id)       # KeyError if unknown
        spot.occupant = None
        self._parked.discard(ticket.plate)
        return self._pricing.fee(ticket, now)

    def spot_of(self, ticket_id: int) -> tuple[int, int]:
        return self._tickets[ticket_id][0].spot

    def occupied(self) -> int:
        return len(self._tickets)
```

- **Value objects** (`Vehicle`, `Interval`, `Ticket`) are frozen and validated, so they're safe to share, hash and log. Half-open intervals make adjacent bookings like `[100, 200)` and `[200, 300)` compatible.
- **Policy as a ranking key**: "EVs prefer chargers, others avoid them, then the smallest fitting size, then the nearest" is one tuple. Changing the policy means changing one expression, not rewriting the allocation logic.
- **Reservations protect the future**: a walk-in at minute 95 can't take a spot reserved from minute 100. The one-hour look-ahead window encodes that rule in a single place.
- **Strategy for pricing**: the lot calls `pricing.fee(ticket, now)` without knowing the formula. EV energy surcharges and hour rounding live in the policy object.
- **Explicit errors** for misuse (a reused reservation, a wrong vehicle, a duplicate plate) keep the lot's state consistent.
