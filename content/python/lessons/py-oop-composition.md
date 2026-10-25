# Composition over Inheritance and Dependency Injection

"Favour object composition over class inheritance" is the most quoted line of the *Design Patterns* book (1994). Inheritance couples a subclass to its parent's implementation details: change the parent, and every subclass may break (the **fragile base class** problem), and combining features through inheritance explodes into dozens of subclasses. **Composition** builds behaviour from small, swappable parts. **Dependency injection** supplies those parts from outside, which makes code flexible and testable. This lesson covers both, plus mixins, delegation, and a minimal DI container.

## 1. The subclass explosion

Robots vary by locomotion (wheels, legs, tracks), power (battery, solar, tethered) and sensing (lidar, camera). With inheritance you'd need `WheeledBatteryLidarRobot`, `LeggedSolarCameraRobot`, and so on: 3 × 3 × 3 = 27 classes, each fixed at definition time.

```python
from typing import Protocol

class Locomotion(Protocol):
    def move(self, distance: float) -> float: ...      # returns energy used (Wh)

class Wheels:
    def move(self, d): return 0.5 * d
class Legs:
    def move(self, d): return 2.0 * d

class PowerSource(Protocol):
    def draw(self, wh: float) -> bool: ...

class Robot:
    def __init__(self, locomotion: Locomotion, power: PowerSource, sensors: list):
        self.locomotion, self.power, self.sensors = locomotion, power, sensors    # composed parts

    def drive(self, d: float) -> bool:
        return self.power.draw(self.locomotion.move(d))  # delegate to parts

rover = Robot(Wheels(), Battery(500), [Lidar()])
walker = Robot(Legs(), Tethered(), [Camera(), Imu()])     # any combination, chosen at runtime
```

3 + 3 + 3 small classes replace 27, and parts can even be swapped while the program runs, for example `robot.locomotion = Tracks()` for rough terrain. That's the **Strategy** pattern applied to structure.

## 2. When inheritance is right

- A genuine **is-a** relationship where substitutability holds (LSP).
- **Framework hooks**: subclassing `unittest.TestCase`, `threading.Thread` or `Exception`.
- **Shallow hierarchies**: one level of abstract base class plus implementations.

Prefer an abstract base class or `Protocol` for the interface, and composition for the implementation.

## 3. Mixins: a middle ground

Mixins are small classes adding one capability through multiple inheritance:

```python
import json

class JsonMixin:
    def to_json(self) -> str:
        return json.dumps(self.__dict__, default=str)

class ReprMixin:
    def __repr__(self) -> str:
        fields = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{type(self).__name__}({fields})"

class Mission(ReprMixin, JsonMixin):
    def __init__(self, goal, priority): self.goal, self.priority = goal, priority
```

Keep mixins stateless and narrowly focused, and be aware of the MRO (C3 linearisation decides `super()` order). Heavy mixin use recreates the fragile-base problem.

## 4. Delegation

Composition plus automatic forwarding:

```python
class LoggedSensor:
    def __init__(self, inner, log): self._inner, self._log = inner, log
    def read(self):
        value = self._inner.read()
        self._log.append(value)
        return value
    def __getattr__(self, name):            # forward everything else to the wrapped object
        return getattr(self._inner, name)
```

## 5. Dependency injection

Objects receive their collaborators instead of creating them:

```python
class MissionPlanner:
    def __init__(self, map_service: "MapService", clock: "Clock", rng: "random.Random"):
        ...
```

| Style | Example | Notes |
|---|---|---|
| Constructor injection | `Planner(map, clock)` | the default: dependencies explicit and immutable |
| Parameter injection | `plan(goal, clock=SystemClock())` | for per-call dependencies |
| Setter injection | `planner.clock = FakeClock()` | optional or cyclic dependencies (use rarely) |
| Container | `container.resolve(Planner)` | auto-wires large object graphs |

**A tiny container** registers how to build each type, then resolves constructor parameters from their type hints:

```python
import inspect, typing

class Container:
    def __init__(self): self._providers, self._singletons = {}, {}
    def register(self, iface, factory=None, *, singleton=False):
        self._providers[iface] = (factory or iface, singleton)
    def resolve(self, iface):
        factory, singleton = self._providers[iface]
        if singleton and iface in self._singletons:
            return self._singletons[iface]
        hints = typing.get_type_hints(factory.__init__) if inspect.isclass(factory) else typing.get_type_hints(factory)
        kwargs = {name: self.resolve(t) for name, t in hints.items() if name != "return"}
        obj = factory(**kwargs)
        if singleton:
            self._singletons[iface] = obj
        return obj
```

Frameworks such as FastAPI's `Depends`, `dependency-injector` and `punq` provide this with scopes, overrides and cycle detection. Most Python projects need nothing more than constructor injection and a `main()` composition root.

> [!EXAM]
> **Why prefer composition over inheritance? Give a concrete example.**
> Inheritance binds a subclass to its parent's implementation at definition time. Changes to the base can break subclasses (the fragile base class problem), and combining independent variations requires a class for every combination: robots varying in locomotion, power and sensors would need 3×3×3 = 27 subclasses. With composition, a `Robot` holds `locomotion`, `power` and `sensors` objects behind small interfaces and delegates to them, so the 9 part classes combine freely, can be chosen or swapped at runtime, are tested in isolation, and are injected from outside (dependency injection), making the robot easy to configure and to test with fakes.
