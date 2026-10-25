# Case Study: Game Engine Entities (ECS)

Game engines and robot simulators manage thousands of objects (players, bullets, robots, sensors) with many combinations of behaviour. Deep inheritance hierarchies (`FlyingShootingEnemy`) break down quickly. The industry answer is the **Entity-Component-System (ECS)** architecture, used by Unity DOTS, Bevy, EnTT and Overwatch's engine, and close in spirit to how ROS separates data (messages) from processing (nodes). This case study builds a small ECS in Python and explains why it scales.

## 1. Three ideas

| Concept | What it is | Example |
|---|---|---|
| **Entity** | just an id (an integer) | `42` |
| **Component** | plain data, no behaviour | `Position(x, y)`, `Velocity(vx, vy)`, `Health(hp)` |
| **System** | a function over all entities having certain components | movement updates `Position` from `Velocity` |

Behaviour comes from **which components an entity has**, and can change at runtime: add `Burning` to an entity and the fire system starts damaging it. That's composition taken to its logical end.

## 2. A minimal world

```python
from dataclasses import dataclass
from itertools import count

@dataclass
class Position: x: float; y: float
@dataclass
class Velocity: vx: float; vy: float
@dataclass
class Health: hp: int

class World:
    def __init__(self):
        self._ids = count(1)
        self._stores: dict[type, dict[int, object]] = {}   # component type -> {entity: component}
        self._alive: set[int] = set()

    def spawn(self, *components) -> int:
        e = next(self._ids)
        self._alive.add(e)
        for c in components:
            self._stores.setdefault(type(c), {})[e] = c
        return e

    def query(self, *types):
        """Yield (entity, c1, c2, ...) for entities having all the given component types."""
        stores = [self._stores.get(t, {}) for t in types]
        smallest = min(stores, key=len) if stores else {}
        for e in sorted(smallest):                         # deterministic order
            if all(e in s for s in stores):
                yield (e, *(s[e] for s in stores))
```

**Iterating the smallest store** makes queries efficient when one component is rare. Real ECS engines go further with **archetypes**: entities with identical component sets are stored together in contiguous arrays, which makes systems cache-friendly and vectorisable.

## 3. Systems and the tick

```python
def movement(world, dt):
    for e, p, v in world.query(Position, Velocity):
        p.x += v.vx * dt
        p.y += v.vy * dt

def damage_zone(world, dt):
    for e, p, h in world.query(Position, Health):
        if p.x < 0:
            h.hp -= 1
            if h.hp <= 0:
                world.despawn(e)          # structural change during iteration!

SYSTEMS = [movement, damage_zone]
for tick in range(1000):
    for system in SYSTEMS:
        system(world, 0.016)
    world.flush()                         # apply deferred despawns and spawns
```

> [!DANGER]
> **Changing structure during iteration** (despawning, adding or removing components while a query is iterating) mutates the dicts being looped over, raising `RuntimeError: dictionary changed size during iteration` or silently skipping entities. ECS engines use **command buffers**: `despawn` only records a request, and `flush()` applies the changes between systems or at the end of the tick.

## 4. Why ECS?

- **Composition at runtime**: new behaviour means a new component plus a system, with no class hierarchy surgery.
- **Separation of data and logic**: systems are easy to test (build a world, run a system, check components) and easy to parallelise when they touch disjoint component sets.
- **Performance**: data-oriented layouts (struct-of-arrays) keep CPU caches hot. In Python the gain is architectural rather than raw speed, unless the components are NumPy arrays.
- **Determinism**: a fixed system order and a sorted entity order give reproducible simulations, which is essential for networked games and for robotics regression tests.

> [!EXAM]
> **What problem does the Entity-Component-System architecture solve compared with deep inheritance hierarchies?**
> With inheritance, every combination of behaviours (moving, shooting, flying, damageable) needs its own subclass, the hierarchy becomes rigid and fragile, and behaviour can't change at runtime. ECS makes an entity just an id, stores data in independent component types, and puts all logic in systems that process every entity having a given set of components. Behaviour comes from composition (which components an entity has) and can change at runtime by adding or removing components. Systems are decoupled, testable and parallelisable, and storing components contiguously by type or archetype makes iteration cache-friendly. Structural changes are deferred through command buffers to keep iteration safe.
