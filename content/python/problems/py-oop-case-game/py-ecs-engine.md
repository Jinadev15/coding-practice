---
id: py-ecs-engine
title: "Case Study: An Entity-Component-System Engine"
difficulty: Hard
order: 1
tags: case study, ECS, composition, data-oriented design, command buffer, deterministic simulation
time_limit: 6
---
## Statement
Implement the Entity-Component-System world from the case-study lesson. Entities are integer ids, components are plain objects (any class; at most one per type per entity), and systems are functions `system(world, dt)`.

**Structural changes are deferred**: `spawn`, `despawn`, `add` and `remove` are **recorded** and applied, in call order, by `flush()`. That makes it safe to call them from inside a system while it iterates a query.

| Method | Contract |
|---|---|
| `spawn(*components) -> int` | Returns the new id **immediately** (1, 2, …). The entity exists after the next flush. Two components of the same type raise `ValueError`. |
| `despawn(e)` | Deferred. Unknown or already-dead entities are ignored at flush time. |
| `add(e, component)` | Deferred. Replaces any component of the same type. Ignored if `e` is dead at flush time. |
| `remove(e, ctype)` | Deferred. Ignored if absent. |
| `flush()` | Applies the pending commands and returns how many were applied (ignored commands don't count). |
| `get(e, ctype)` / `has(e, ctype)` / `alive(e)` | Return the component or None, a bool, and a bool. |
| `query(*ctypes) -> list[tuple]` | `[(e, c1, c2, …)]` for alive entities having **all** the types, **sorted by entity id**. No types raises `ValueError`. |
| `count(ctype=None) -> int` | The number of alive entities (with that component type, if one is given). |
| `add_system(fn)` / `step(dt)` | Runs the systems in registration order, **flushing after each system**, and increments `world.ticks`. |

Queries must not scan every entity for every type. Iterate the smallest of the requested component stores.

## Starter
```python
class World:
    def __init__(self):
        self.entities = {}
        self.next_id = 1
        self.systems = []
        self.ticks = 0

    def spawn(self, *components):
        e = self.next_id
        self.next_id += 1
        self.entities[e] = {type(c): c for c in components}
        return e

    def despawn(self, e):
        del self.entities[e]

    def query(self, *types):
        return [(e, *(cs[t] for t in types)) for e, cs in self.entities.items() if all(t in cs for t in types)]

    def add_system(self, fn):
        self.systems.append(fn)

    def step(self, dt):
        for s in self.systems:
            s(self, dt)
        self.ticks += 1

    def flush(self):
        return 0
```

## Driver
```python
import sys
from dataclasses import dataclass

@dataclass
class Position: x: float; y: float
@dataclass
class Velocity: vx: float; vy: float
@dataclass
class Health: hp: int
@dataclass
class Lifetime: ticks: int
@dataclass
class Tag: name: str

def movement(world, dt):
    for e, p, v in world.query(Position, Velocity):
        p.x += v.vx * dt; p.y += v.vy * dt

def lava(world, dt):
    for e, p, h in world.query(Position, Health):
        if p.x < 0:
            h.hp -= 10
            if h.hp <= 0:
                world.despawn(e)
                world.spawn(Position(p.x, p.y), Tag("wreck"), Lifetime(2))

def aging(world, dt):
    for e, life in world.query(Lifetime):
        life.ticks -= 1
        if life.ticks <= 0:
            world.despawn(e)

def show(world, label):
    rows = [(e, round(p.x, 2), round(p.y, 2)) for e, p in world.query(Position)]
    print(label, "tick", world.ticks, "alive", world.count(), rows)

for cmd in sys.stdin.read().split():
    w = World()
    if cmd == "basic":
        a = w.spawn(Position(0, 0), Velocity(1, 0))
        b = w.spawn(Position(5, 5))
        c = w.spawn(Velocity(2, 2), Tag("ghost"))
        print("ids", a, b, c, "alive before flush", w.alive(a), "count", w.count())
        print("applied", w.flush(), "alive", w.alive(a), w.count(), w.count(Velocity), w.count(Tag))
        print("query pos+vel", [(e, p.x) for e, p, v in w.query(Position, Velocity)])
        try:
            w.spawn(Position(0, 0), Position(1, 1))
        except ValueError:
            print("duplicate component rejected")
        try:
            w.query()
        except ValueError:
            print("empty query rejected")
        w.add(b, Velocity(0, -1)); w.remove(c, Tag); w.add(c, Position(9, 9)); w.despawn(99); w.remove(a, Health)
        print("before flush", w.has(b, Velocity), "applied", w.flush(), "after", w.has(b, Velocity), w.get(c, Tag), w.get(c, Position))
        w.add(b, Velocity(3, 3)); w.flush(); print("replaced", w.get(b, Velocity))
        w.despawn(a); w.despawn(a); w.add(a, Tag("late")); print("applied", w.flush(), "alive a", w.alive(a), w.get(a, Position))
        print("ids after deaths", w.spawn(Tag("new")))
    elif cmd == "sim":
        w.add_system(movement); w.add_system(lava); w.add_system(aging)
        w.spawn(Position(2, 0), Velocity(-1, 0), Health(25))
        w.spawn(Position(10, 1), Velocity(0, 1), Health(50))
        w.spawn(Position(0.5, 3), Velocity(-0.5, 0), Health(10), Lifetime(8))
        w.flush()
        for t in range(9):
            w.step(1.0)
            show(w, "after")
        print("wrecks", w.count(Tag), "healthy", w.count(Health))
    elif cmd == "spawner":
        def spawner(world, dt):
            for e, p, tag in world.query(Position, Tag):
                if tag.name == "turret" and world.ticks % 2 == 0:
                    world.spawn(Position(p.x, p.y), Velocity(1, 0), Lifetime(3), Tag("bullet"))
        w.add_system(spawner); w.add_system(movement); w.add_system(aging)
        w.spawn(Position(0, 0), Tag("turret")); w.flush()
        for t in range(7):
            w.step(1.0)
            print(t, "bullets", sorted((e, round(p.x, 1)) for e, p, tag in w.query(Position, Tag) if tag.name == "bullet"))
    elif cmd == "load":
        import time
        for i in range(20000):
            comps = [Position(i % 100, i // 100)]
            if i % 2 == 0: comps.append(Velocity((i % 7) - 3, (i % 5) - 2))
            if i % 3 == 0: comps.append(Health(30 + i % 20))
            if i % 50 == 0: comps.append(Lifetime(5 + i % 10))
            w.spawn(*comps)
        w.flush()
        w.add_system(movement); w.add_system(lava); w.add_system(aging)
        t0 = time.perf_counter()
        for _ in range(15):
            w.step(0.5)
        rare = len(w.query(Lifetime, Velocity))
        print("alive", w.count(), "health", w.count(Health), "tags", w.count(Tag), "rare query", rare, "fast", time.perf_counter() - t0 < 4.0)
```

## Tests
=== sample
basic
---
ids 1 2 3 alive before flush False count 0
applied 3 alive True 3 2 1
query pos+vel [(1, 0)]
duplicate component rejected
empty query rejected
before flush False applied 3 after True None Position(x=9, y=9)
replaced Velocity(vx=3, vy=3)
applied 1 alive a False None
ids after deaths 4
=== hidden
sim
---
after tick 1 alive 3 [(1, 1.0, 0.0), (2, 10.0, 2.0), (3, 0.0, 3.0)]
after tick 2 alive 3 [(1, 0.0, 0.0), (2, 10.0, 3.0), (4, -0.5, 3.0)]
after tick 3 alive 2 [(1, -1.0, 0.0), (2, 10.0, 4.0)]
after tick 4 alive 2 [(1, -2.0, 0.0), (2, 10.0, 5.0)]
after tick 5 alive 2 [(2, 10.0, 6.0), (5, -3.0, 0.0)]
after tick 6 alive 1 [(2, 10.0, 7.0)]
after tick 7 alive 1 [(2, 10.0, 8.0)]
after tick 8 alive 1 [(2, 10.0, 9.0)]
after tick 9 alive 1 [(2, 10.0, 10.0)]
wrecks 0 healthy 1
=== hidden
spawner
---
0 bullets [(2, 1.0)]
1 bullets [(2, 2.0)]
2 bullets [(3, 1.0)]
3 bullets [(3, 2.0)]
4 bullets [(4, 1.0)]
5 bullets [(4, 2.0)]
6 bullets [(5, 1.0)]
=== hidden
load
---
alive 19466 health 6390 tags 9 rare query 0 fast True

## Hints
- Storage: `self._stores: dict[type, dict[int, object]]` (component type → entity → component), plus `self._alive: set[int]`.
- Commands: `self._pending: list[tuple]`, such as `("spawn", e, comps)`, `("despawn", e)`, `("add", e, c)` and `("remove", e, t)`. `flush` takes the list (swap in a fresh one first), then applies each command in order.
- `query`: pick `min(stores, key=len)`, iterate `sorted(smallest)`, and keep the entities present in every store.
- Despawning removes the entity from every store. Make sure `alive()` is False and that later `add`s to it are ignored.

## Solution
```python
from itertools import count


class World:
    def __init__(self):
        self._ids = count(1)
        self._alive: set[int] = set()
        self._stores: dict[type, dict[int, object]] = {}
        self._pending: list[tuple] = []
        self._systems: list = []
        self.ticks = 0

    # --- deferred structural changes (command buffer) ---
    def spawn(self, *components) -> int:
        types = [type(c) for c in components]
        if len(types) != len(set(types)):
            raise ValueError("duplicate component type")
        e = next(self._ids)
        self._pending.append(("spawn", e, components))
        return e

    def despawn(self, e: int) -> None:
        self._pending.append(("despawn", e))

    def add(self, e: int, component) -> None:
        self._pending.append(("add", e, component))

    def remove(self, e: int, ctype: type) -> None:
        self._pending.append(("remove", e, ctype))

    def flush(self) -> int:
        pending, self._pending = self._pending, []
        applied = 0
        for cmd in pending:
            op, e = cmd[0], cmd[1]
            if op == "spawn":
                self._alive.add(e)
                for c in cmd[2]:
                    self._stores.setdefault(type(c), {})[e] = c
                applied += 1
            elif op == "despawn":
                if e in self._alive:
                    self._alive.discard(e)
                    for store in self._stores.values():
                        store.pop(e, None)
                    applied += 1
            elif op == "add":
                if e in self._alive:
                    self._stores.setdefault(type(cmd[2]), {})[e] = cmd[2]
                    applied += 1
            elif op == "remove":
                store = self._stores.get(cmd[2])
                if store is not None and e in store:
                    del store[e]
                    applied += 1
        return applied

    # --- reads ---
    def alive(self, e: int) -> bool:
        return e in self._alive

    def get(self, e: int, ctype: type):
        return self._stores.get(ctype, {}).get(e)

    def has(self, e: int, ctype: type) -> bool:
        return e in self._stores.get(ctype, {})

    def query(self, *ctypes) -> list[tuple]:
        if not ctypes:
            raise ValueError("query needs at least one component type")
        stores = [self._stores.get(t, {}) for t in ctypes]
        smallest = min(stores, key=len)
        return [(e, *(s[e] for s in stores)) for e in sorted(smallest) if all(e in s for s in stores)]

    def count(self, ctype: type | None = None) -> int:
        return len(self._alive) if ctype is None else len(self._stores.get(ctype, {}))

    # --- systems ---
    def add_system(self, fn) -> None:
        self._systems.append(fn)

    def step(self, dt: float) -> None:
        for system in self._systems:
            system(self, dt)
            self.flush()                                # structural changes become visible to the next system
        self.ticks += 1
```

- **Composition at the extreme**: an entity is just an id. Behaviour comes from which components it has, so adding `Health` makes the lava system affect it, and adding `Lifetime` makes it age. There are no class hierarchies to edit.
- **Systems are pure logic over data**: `movement`, `lava` and `aging` are small functions that know only the components they query, so they're easy to test and reorder.
- **A command buffer for structural changes**: despawning a robot and spawning its wreck *inside* the lava system's loop is safe, because the changes are queued and applied at `flush()`. The starter's immediate `del` crashes with "dictionary changed size during iteration" or skips entities.
- **Queries iterate the smallest store**: a query for the rare `Lifetime` component touches about 400 entities instead of 20,000. Sorting by id keeps runs deterministic, which matters for replays and networked games.
- **Flushing after each system** gives a clear, documented visibility rule: changes made by one system are seen by the next system in the same tick.
