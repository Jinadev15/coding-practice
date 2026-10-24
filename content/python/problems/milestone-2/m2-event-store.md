---
id: py-m2-event-store
title: Event-Sourced Order Book
difficulty: Hard
order: 2
tags: dataclasses, enums, pattern matching, JSON, design, error handling
---
## Statement
In **event sourcing**, state isn't stored directly: it's rebuilt by **replaying an append-only log of events**. Implement a small event-sourced order system for a robot-parts shop.

Events arrive as JSON lines:

```json
{"type": "OrderPlaced", "order": "o1", "customer": "ada", "items": {"motor": 2, "lidar": 1}}
{"type": "ItemAdded", "order": "o1", "item": "imu", "qty": 3}
{"type": "ItemRemoved", "order": "o1", "item": "motor", "qty": 1}
{"type": "OrderShipped", "order": "o1"}
{"type": "OrderCancelled", "order": "o2", "reason": "out of stock"}
{"type": "PriceSet", "item": "motor", "cents": 4999}
```

Model it with:
- `class Status(Enum)`: `OPEN`, `SHIPPED`, `CANCELLED`
- `@dataclass class Order` (id, customer, items as a dict of item → qty, status), with a `total(prices)` method
- `@dataclass(frozen=True)` event classes, plus `parse_event(d: dict) -> Event`, which uses **`match`** on the dict's shape (`case {"type": "OrderPlaced", "order": str(o), "customer": str(c), "items": dict(items)}:` …). Unknown or malformed events raise `ValueError`.
- `apply(state, event) -> None`, which updates the state with a `match` on the event class. Business rules (a violation raises `ValueError` with the message given, and **the state must not change**):
  - placing an existing order: `"duplicate order o1"`
  - any change to a missing order: `"unknown order o9"`
  - modifying or shipping a non-OPEN order: `"order o1 is shipped"` / `"... is cancelled"`
  - removing more than present: `"not enough motor in o1"` (if an item reaches 0, remove it)
  - shipping an empty order: `"order o1 is empty"`
  - cancelling a shipped order: `"order o1 is shipped"`

Process the log line by line. Print `ok`, or `rejected: MESSAGE` (malformed JSON or events: `rejected: bad event`). Then print a report: every order sorted by id, as `o1 ada SHIPPED lidar=1,motor=1 total=$X.XX` (items sorted, or `-` if the order has none; a price defaults to 0 if never set; prices apply at report time; the `$` amount uses integer cents), and finally `snapshot:` followed by the full state as **canonical JSON** (`json.dumps(..., sort_keys=True)`), with this shape: `{"orders": {id: {"customer", "items", "status"}}, "prices": {...}}`.

## Starter
```python
import json
import sys
from dataclasses import dataclass, field
from enum import Enum

for line in sys.stdin.read().splitlines():
    print("ok")
```

## Tests
=== sample
{"type": "PriceSet", "item": "motor", "cents": 4999}
{"type": "PriceSet", "item": "lidar", "cents": 12900}
{"type": "OrderPlaced", "order": "o1", "customer": "ada", "items": {"motor": 2, "lidar": 1}}
{"type": "ItemAdded", "order": "o1", "item": "imu", "qty": 3}
{"type": "ItemRemoved", "order": "o1", "item": "motor", "qty": 5}
{"type": "ItemRemoved", "order": "o1", "item": "imu", "qty": 3}
{"type": "OrderShipped", "order": "o1"}
{"type": "ItemAdded", "order": "o1", "item": "imu", "qty": 1}
{"type": "OrderPlaced", "order": "o1", "customer": "bob", "items": {}}
{"type": "OrderPlaced", "order": "o2", "customer": "bob", "items": {}}
{"type": "OrderShipped", "order": "o2"}
{"type": "OrderCancelled", "order": "o2", "reason": "changed mind"}
{"type": "OrderShipped", "order": "o9"}
{"type": "Teleport", "order": "o1"}
not json at all
{"type": "ItemAdded", "order": "o2", "item": "x", "qty": "two"}
---
ok
ok
ok
ok
rejected: not enough motor in o1
ok
ok
rejected: order o1 is shipped
rejected: duplicate order o1
ok
rejected: order o2 is empty
ok
rejected: unknown order o9
rejected: bad event
rejected: bad event
rejected: bad event
o1 ada SHIPPED lidar=1,motor=2 total=$228.98
o2 bob CANCELLED - total=$0.00
snapshot: {"orders": {"o1": {"customer": "ada", "items": {"lidar": 1, "motor": 2}, "status": "SHIPPED"}, "o2": {"customer": "bob", "items": {}, "status": "CANCELLED"}}, "prices": {"lidar": 12900, "motor": 4999}}
=== hidden
{"type": "OrderPlaced", "order": "z", "customer": "c", "items": {"a": 1}}
{"type": "OrderCancelled", "order": "z", "reason": "r"}
{"type": "OrderCancelled", "order": "z", "reason": "again"}
{"type": "OrderShipped", "order": "z"}
{"type": "ItemAdded", "order": "z", "item": "a", "qty": 1}
{"type": "OrderPlaced", "order": "y", "customer": "d", "items": {"gear": 4}}
{"type": "PriceSet", "item": "gear", "cents": 125}
{"type": "ItemRemoved", "order": "y", "item": "gear", "qty": 4}
{"type": "ItemAdded", "order": "y", "item": "gear", "qty": 2}
{"type": "OrderShipped", "order": "y"}
{"type": "OrderCancelled", "order": "y", "reason": "late"}
{"type": "PriceSet", "item": "gear", "cents": 99}
{"type": "OrderPlaced", "order": "x", "customer": "e", "items": {"bolt": 0}}
{"type": "ItemAdded", "order": "x", "item": "bolt", "qty": -1}
{"type": "PriceSet", "item": "nut", "cents": -5}
---
ok
ok
rejected: order z is cancelled
rejected: order z is cancelled
rejected: order z is cancelled
ok
ok
ok
ok
ok
rejected: order y is shipped
ok
rejected: bad event
rejected: bad event
rejected: bad event
y d SHIPPED gear=2 total=$1.98
z c CANCELLED a=1 total=$0.00
snapshot: {"orders": {"y": {"customer": "d", "items": {"gear": 2}, "status": "SHIPPED"}, "z": {"customer": "c", "items": {"a": 1}, "status": "CANCELLED"}}, "prices": {"gear": 99}}

## Hints
- `parse_event` with `match d:` and class/mapping patterns plus guards: `case {"type": "ItemAdded", "order": str(o), "item": str(i), "qty": int(q)} if q > 0:`. Also make sure `bool` isn't accepted as an `int` (`type(q) is int`). `OrderPlaced` items must be a dict of `str` to positive `int` (zero quantities are invalid). `PriceSet` cents must be ≥ 0.
- Make `apply` validate **everything first** and mutate only at the end, so a rejected event leaves the state untouched.
- Snapshot: `{"orders": {oid: {"customer": o.customer, "items": o.items, "status": o.status.name} ...}, "prices": prices}`, then `json.dumps(snapshot, sort_keys=True)`.

## Solution
```python
import json
import sys
from dataclasses import dataclass, field
from enum import Enum

class Status(Enum):
    OPEN = "open"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"

@dataclass
class Order:
    id: str
    customer: str
    items: dict = field(default_factory=dict)
    status: Status = Status.OPEN

    def total(self, prices):
        return sum(prices.get(item, 0) * qty for item, qty in self.items.items())

@dataclass(frozen=True)
class OrderPlaced:
    order: str
    customer: str
    items: tuple

@dataclass(frozen=True)
class ItemAdded:
    order: str
    item: str
    qty: int

@dataclass(frozen=True)
class ItemRemoved:
    order: str
    item: str
    qty: int

@dataclass(frozen=True)
class OrderShipped:
    order: str

@dataclass(frozen=True)
class OrderCancelled:
    order: str
    reason: str

@dataclass(frozen=True)
class PriceSet:
    item: str
    cents: int

def _pos_int(v):
    return type(v) is int and v > 0

def parse_event(d):
    match d:
        case {"type": "OrderPlaced", "order": str(o), "customer": str(c), "items": dict(items)} \
                if all(isinstance(k, str) and _pos_int(v) for k, v in items.items()):
            return OrderPlaced(o, c, tuple(sorted(items.items())))
        case {"type": "ItemAdded", "order": str(o), "item": str(i), "qty": q} if _pos_int(q):
            return ItemAdded(o, i, q)
        case {"type": "ItemRemoved", "order": str(o), "item": str(i), "qty": q} if _pos_int(q):
            return ItemRemoved(o, i, q)
        case {"type": "OrderShipped", "order": str(o)}:
            return OrderShipped(o)
        case {"type": "OrderCancelled", "order": str(o), "reason": str(r)}:
            return OrderCancelled(o, r)
        case {"type": "PriceSet", "item": str(i), "cents": c} if type(c) is int and c >= 0:
            return PriceSet(i, c)
        case _:
            raise ValueError("bad event")

def _open_order(state, oid):
    order = state["orders"].get(oid)
    if order is None:
        raise ValueError(f"unknown order {oid}")
    if order.status is not Status.OPEN:
        raise ValueError(f"order {oid} is {order.status.value}")
    return order

def apply(state, event):
    match event:
        case OrderPlaced(order=oid, customer=c, items=items):
            if oid in state["orders"]:
                raise ValueError(f"duplicate order {oid}")
            state["orders"][oid] = Order(oid, c, dict(items))
        case ItemAdded(order=oid, item=i, qty=q):
            order = _open_order(state, oid)
            order.items[i] = order.items.get(i, 0) + q
        case ItemRemoved(order=oid, item=i, qty=q):
            order = _open_order(state, oid)
            if order.items.get(i, 0) < q:
                raise ValueError(f"not enough {i} in {oid}")
            order.items[i] -= q
            if order.items[i] == 0:
                del order.items[i]
        case OrderShipped(order=oid):
            order = _open_order(state, oid)
            if not order.items:
                raise ValueError(f"order {oid} is empty")
            order.status = Status.SHIPPED
        case OrderCancelled(order=oid):
            order = _open_order(state, oid)
            order.status = Status.CANCELLED
        case PriceSet(item=i, cents=c):
            state["prices"][i] = c

state = {"orders": {}, "prices": {}}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    try:
        event = parse_event(json.loads(line))
    except (json.JSONDecodeError, ValueError):
        print("rejected: bad event")
        continue
    try:
        apply(state, event)
        print("ok")
    except ValueError as e:
        print(f"rejected: {e}")

for oid in sorted(state["orders"]):
    o = state["orders"][oid]
    items = ",".join(f"{k}={v}" for k, v in sorted(o.items.items())) or "-"
    cents = o.total(state["prices"])
    print(f"{oid} {o.customer} {o.status.name} {items} total=${cents // 100}.{cents % 100:02d}")
snapshot = {"orders": {oid: {"customer": o.customer, "items": o.items, "status": o.status.name}
                       for oid, o in state["orders"].items()},
            "prices": state["prices"]}
print("snapshot:", json.dumps(snapshot, sort_keys=True))
```

**Design notes:**
- **Events are immutable facts** (frozen dataclasses), and the state is a pure fold over them. Replaying the same log always produces the same state, which gives audit trails, debugging by replay, and snapshots for free. Robot black-box recorders and most financial systems work this way.
- **Validate at the boundary:** `parse_event` turns untrusted JSON into typed events using structural pattern matching with guards, rejecting wrong types such as `"qty": "two"` or `True`.
- **Enforce invariants in one place:** `apply` checks every business rule before mutating, so rejected commands leave no partial state.
- **Money is integer cents.** Floats would accumulate rounding errors.
- **Canonical JSON** (`sort_keys=True`) makes snapshots byte-for-byte comparable across runs.
