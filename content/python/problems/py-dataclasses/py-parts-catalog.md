---
id: py-parts-catalog
title: Robot Parts Catalog with Dataclasses
difficulty: Medium
order: 1
tags: dataclasses, frozen, order, __post_init__, field
---
## Statement
Model a parts catalog with dataclasses. The driver uses your classes, so the interface must match exactly:

```python
@dataclass(frozen=True, order=True)
class PartId:
    family: str      # e.g. "MTR"
    number: int      # e.g. 42
    # str(PartId("MTR", 42)) == "MTR-0042"
    # PartId.parse("MTR-0042") -> PartId("MTR", 42)  (a classmethod; raise ValueError on bad text)

@dataclass
class Part:
    pid: PartId
    name: str
    price_cents: int
    tags: list[str] = (a NEW empty list per instance)
    # __post_init__: raise ValueError if price_cents < 0 or name is blank (after strip);
    #                store the name stripped, and tags lowercased with duplicates removed (keep first occurrence order)

class Catalog:
    def add(self, part: Part) -> None     # ValueError if the id already exists
    def get(self, pid: PartId) -> Part    # KeyError if missing
    def by_tag(self, tag: str) -> list[Part]           # sorted by pid
    def reprice(self, pid: PartId, pct: int) -> Part   # NEW Part (dataclasses.replace) with price * (100 + pct) // 100, stored in place of the old one
    def cheapest(self, n: int) -> list[Part]           # by price, then pid
```

`PartId` must be hashable and sortable (the driver puts ids in sets and sorts them). `PartId.parse` accepts `FAMILY-NNNN`, where FAMILY is 2–4 uppercase letters and NNNN is exactly four digits.

## Starter
```python
from dataclasses import dataclass, field, replace

@dataclass
class PartId:
    family: str
    number: int

@dataclass
class Part:
    pid: PartId
    name: str
    price_cents: int
    tags: list = None

class Catalog:
    def __init__(self):
        self.parts = {}
```

## Driver
```python
import sys
from dataclasses import FrozenInstanceError, fields

def show(p):
    return f"{p.pid} {p.name} {p.price_cents} [{','.join(p.tags)}]"

cat = Catalog()
for line in sys.stdin.read().splitlines():
    cmd, _, rest = line.partition(" ")
    try:
        if cmd == "add":
            pid, name, price, tags = rest.split("|")
            cat.add(Part(PartId.parse(pid), name, int(price), [t for t in tags.split(",") if t]))
            print("added", pid)
        elif cmd == "get":
            print(show(cat.get(PartId.parse(rest))))
        elif cmd == "tag":
            print(rest + ":", ", ".join(str(p.pid) for p in cat.by_tag(rest)) or "none")
        elif cmd == "reprice":
            pid, pct = rest.split()
            old = cat.get(PartId.parse(pid))
            new = cat.reprice(PartId.parse(pid), int(pct))
            print("repriced", show(new), "| old object unchanged:", old.price_cents != new.price_cents or int(pct) == 0)
        elif cmd == "cheapest":
            print("cheapest:", ", ".join(f"{p.pid}={p.price_cents}" for p in cat.cheapest(int(rest))))
        elif cmd == "check":
            a, b = PartId("MTR", 7), PartId("MTR", 7)
            print("hashable:", len({a, b}) == 1, "| sorted:", [str(x) for x in sorted([PartId("SEN", 1), PartId("MTR", 9), PartId("MTR", 2)])])
            try:
                a.number = 8
                print("frozen: no")
            except FrozenInstanceError:
                print("frozen: yes")
            p1, p2 = Part(a, "x", 1), Part(a, "y", 1)
            p1.tags.append("t")
            print("independent tags:", p2.tags == [], "| fields:", [f.name for f in fields(Part)])
    except (ValueError, KeyError) as e:
        print("error:", type(e).__name__)
```

## Tests
=== sample
add MTR-0042|  Servo Motor |1999|actuator,Motor,actuator
add SEN-0007|Lidar|45000|sensor,optical
add MTR-0042|Dup|1|
get MTR-0042
tag actuator
tag none
reprice MTR-0042 10
cheapest 5
check
---
added MTR-0042
added SEN-0007
error: ValueError
MTR-0042 Servo Motor 1999 [actuator,motor]
actuator: MTR-0042
none: none
repriced MTR-0042 Servo Motor 2198 [actuator,motor] | old object unchanged: True
cheapest: MTR-0042=2198, SEN-0007=45000
hashable: True | sorted: ['MTR-0002', 'MTR-0009', 'SEN-0001']
frozen: yes
independent tags: True | fields: ['pid', 'name', 'price_cents', 'tags']
=== hidden
add AB-0001|a|0|
add ABCDE-0001|bad family|1|
add AB-001|bad number|1|
add ab-0001|lower|1|
add CD-0002|   |5|
add CD-0003|neg|-1|
get ZZ-9999
add CD-0004|ok|300|X,y,X,Y
get CD-0004
reprice CD-0004 -50
reprice CD-0004 0
cheapest 1
tag x
---
added AB-0001
error: ValueError
error: ValueError
error: ValueError
error: ValueError
error: ValueError
error: KeyError
added CD-0004
CD-0004 ok 300 [x,y]
repriced CD-0004 ok 150 [x,y] | old object unchanged: True
repriced CD-0004 ok 150 [x,y] | old object unchanged: True
cheapest: AB-0001=0
x: CD-0004
=== hidden
add P-0001|short family|1|
add PQ-0010|ten|10|common
add PQ-0002|two|10|common
add PQ-0003|three|5|common
tag common
cheapest 2
reprice PQ-0003 100
cheapest 3
---
error: ValueError
added PQ-0010
added PQ-0002
added PQ-0003
common: PQ-0002, PQ-0003, PQ-0010
cheapest: PQ-0003=5, PQ-0002=10
repriced PQ-0003 three 10 [common] | old object unchanged: True
cheapest: PQ-0002=10, PQ-0003=10, PQ-0010=10

## Hints
- `@dataclass(frozen=True, order=True)` on `PartId` gives `__hash__`, `__eq__` and `<` from `(family, number)`. Add `__str__` returning `f"{self.family}-{self.number:04d}"`.
- `parse` as a `@classmethod` with `re.fullmatch(r"([A-Z]{2,4})-(\d{4})", text)`.
- `tags: list[str] = field(default_factory=list)`. In `__post_init__`, `list(dict.fromkeys(t.lower() for t in self.tags))` dedupes while keeping order.
- `replace(old, price_cents=...)` runs `__init__` and `__post_init__` again, so validation still applies.

## Solution
```python
import re
from dataclasses import dataclass, field, replace

@dataclass(frozen=True, order=True)
class PartId:
    family: str
    number: int

    def __str__(self):
        return f"{self.family}-{self.number:04d}"

    @classmethod
    def parse(cls, text):
        m = re.fullmatch(r"([A-Z]{2,4})-(\d{4})", text.strip())
        if not m:
            raise ValueError(f"bad part id {text!r}")
        return cls(m.group(1), int(m.group(2)))


@dataclass
class Part:
    pid: PartId
    name: str
    price_cents: int
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("blank name")
        if self.price_cents < 0:
            raise ValueError("negative price")
        self.tags = list(dict.fromkeys(t.lower() for t in self.tags))


class Catalog:
    def __init__(self):
        self._parts: dict[PartId, Part] = {}

    def add(self, part):
        if part.pid in self._parts:
            raise ValueError(f"duplicate {part.pid}")
        self._parts[part.pid] = part

    def get(self, pid):
        return self._parts[pid]

    def by_tag(self, tag):
        return sorted((p for p in self._parts.values() if tag in p.tags), key=lambda p: p.pid)

    def reprice(self, pid, pct):
        old = self._parts[pid]
        new = replace(old, price_cents=old.price_cents * (100 + pct) // 100)
        self._parts[pid] = new
        return new

    def cheapest(self, n):
        return sorted(self._parts.values(), key=lambda p: (p.price_cents, p.pid))[:n]
```

**Design choices:**
- **`PartId` is a frozen, ordered value object.** Immutability makes it safe as a dict key (`Catalog._parts`) and a set member, and `order=True` makes it sortable by `(family, number)` with no hand-written comparisons.
- **`Part` validates itself** in `__post_init__`, so an invalid part can't exist, and `replace()` re-runs the validation for derived copies.
- **`field(default_factory=list)`** gives each part its own tag list (the driver's `check` proves it). The starter's `tags: list = None` "works" but forces `None` checks everywhere.
- **`dict.fromkeys`** is the idiomatic ordered de-duplication, because dicts keep insertion order.
