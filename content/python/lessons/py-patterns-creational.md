# Creational Patterns in Python

The Gang of Four patterns were written for C++ and Smalltalk. In Python many of them shrink, because classes are first-class objects, functions are values, modules are singletons, and keyword arguments with defaults remove most telescoping constructors. Peter Norvig observed that 16 of the 23 GoF patterns are "invisible or simpler" in dynamic languages. This lesson shows the Pythonic form of each creational pattern: factories (functions, classmethods, registries with decorators and `__init_subclass__`), builders (and when dataclasses make them unnecessary), prototypes with `copy`, singletons (and the module alternative), and object pools.

## 1. Factories are just callables

```python
class Lidar:
    def __init__(self, port: str, rate_hz: float = 10.0): ...
class Sonar:
    def __init__(self, pin: int): ...

SENSORS = {"lidar": Lidar, "sonar": Sonar}          # classes are values

def make_sensor(kind: str, **cfg):
    try:
        cls = SENSORS[kind]
    except KeyError:
        raise ValueError(f"unknown sensor kind {kind!r}; choose from {sorted(SENSORS)}") from None
    return cls(**cfg)

s = make_sensor("lidar", port="/dev/ttyUSB0", rate_hz=20)
```

A dict from names to classes replaces the factory class hierarchy. Any callable can be the "creator": a class, a function, a `functools.partial`, a lambda.

**Alternative constructors** use `@classmethod`, the Pythonic factory method, and they work for subclasses too:

```python
from dataclasses import dataclass
import json

@dataclass(frozen=True)
class Pose:
    x: float; y: float; theta: float = 0.0
    @classmethod
    def from_dict(cls, d: dict) -> "Pose": return cls(float(d["x"]), float(d["y"]), float(d.get("theta", 0)))
    @classmethod
    def from_json(cls, text: str) -> "Pose": return cls.from_dict(json.loads(text))
    @classmethod
    def origin(cls) -> "Pose": return cls(0.0, 0.0)
```

The standard library does this throughout: `datetime.fromisoformat`, `dict.fromkeys`, `int.from_bytes`.

## 2. Registries: decorators and `__init_subclass__`

To make new types plug in without editing the factory, let them **register themselves**:

```python
CONTROLLERS: dict[str, type] = {}

def register(name: str):
    def deco(cls):
        if name in CONTROLLERS:
            raise ValueError(f"duplicate controller {name!r}")
        CONTROLLERS[name] = cls
        return cls                          # class decorators must return the class
    return deco

@register("pid")
class PID:
    def __init__(self, kp: float, ki: float = 0.0, kd: float = 0.0): ...
```

`__init_subclass__` (PEP 487) runs whenever a subclass is defined. That gives automatic registration with no decorator, which is how many plugin systems and ORMs work:

```python
class Controller:
    registry: dict[str, type["Controller"]] = {}
    def __init_subclass__(cls, /, key: str | None = None, **kw):
        super().__init_subclass__(**kw)
        if key is not None:
            Controller.registry[key] = cls

class MPC(Controller, key="mpc"): ...
class PurePursuit(Controller, key="pure_pursuit"): ...
print(sorted(Controller.registry))        # ['mpc', 'pure_pursuit']
```

For third-party plugins, packages advertise **entry points** (`[project.entry-points."robot.controllers"]` in `pyproject.toml`), discovered with `importlib.metadata.entry_points(group="robot.controllers")`. That's how pytest plugins and many CLI tools are found.

## 3. Builders, and why dataclasses usually suffice

In Java and C++, a builder fixes telescoping constructors. Python has keyword arguments and defaults, so `RobotConfig(name="r1", wheel_radius=0.05)` is already readable. A frozen dataclass with `__post_init__` validation covers most cases:

```python
from dataclasses import dataclass, field, replace

@dataclass(frozen=True, slots=True)
class RobotConfig:
    name: str
    wheel_radius: float
    track: float = 0.3
    sensors: tuple[str, ...] = ()
    max_rpm: float = 3000.0

    def __post_init__(self):
        if not self.name: raise ValueError("name required")
        if self.wheel_radius <= 0: raise ValueError("wheel_radius must be > 0")

    @property
    def max_speed(self) -> float:
        return self.max_rpm / 60 * 2 * 3.141592653589793 * self.wheel_radius

base = RobotConfig("r1", 0.05)
fast = replace(base, max_rpm=6000)            # "with" copy of an immutable object
```

A real **Builder** still earns its place when construction is **incremental** (assembled across several steps or config sources), when it needs **cross-field validation only at the end**, or when the product is complex (a query, a URDF tree, a plot). Make the builder methods return `self` for chaining:

```python
class QueryBuilder:
    def __init__(self, table: str): self._table, self._where, self._params, self._limit = table, [], [], None
    def where(self, column: str, op: str, value):
        if op not in {"=", "<", ">", "<=", ">=", "!="}: raise ValueError(op)
        self._where.append(f"{column} {op} ?"); self._params.append(value); return self
    def limit(self, n: int): self._limit = n; return self
    def build(self) -> tuple[str, list]:
        sql = f"SELECT * FROM {self._table}"
        if self._where: sql += " WHERE " + " AND ".join(self._where)
        if self._limit is not None: sql += f" LIMIT {int(self._limit)}"
        return sql, list(self._params)
```

## 4. Prototype: `copy`

```python
import copy
template = {"name": "patrol", "waypoints": [[0, 0], [5, 0]], "speed": 0.5}
m1 = copy.deepcopy(template)          # independent nested lists
m1["waypoints"].append([5, 5])
shallow = copy.copy(template)         # shares the inner list!
```

Customise copying with `__copy__` and `__deepcopy__(self, memo)`, for example to share an expensive immutable mesh while copying the mutable pose. Frozen dataclasses plus `dataclasses.replace` are often a cleaner prototype mechanism.

## 5. Singleton, the Pythonic way

A **module is a singleton**: it's imported once and cached in `sys.modules`. Module-level objects (a configured logger, a settings object) give single-instance semantics without any pattern code. If a class really must be single-instance, the simplest robust approach is a module-level instance or `functools.cache` on a getter:

```python
from functools import cache

@cache
def get_settings() -> "Settings":
    return Settings.from_env()          # created once, on first call
```

Tests can call `get_settings.cache_clear()`. The same caveats as in C++ apply: hidden global state makes dependencies invisible and tests order-dependent, so prefer passing objects explicitly (dependency injection).

## 6. Object pools

CPython's allocator makes pooling plain objects pointless. Pool **expensive external resources** instead: database connections, threads (`concurrent.futures.ThreadPoolExecutor`), processes, GPU buffers.

```python
import queue
from contextlib import contextmanager

class Pool:
    def __init__(self, factory, size: int):
        self._q = queue.Queue()
        for _ in range(size): self._q.put(factory())
    @contextmanager
    def lease(self, timeout: float | None = None):
        item = self._q.get(timeout=timeout)       # blocks when exhausted
        try:
            yield item
        finally:
            self._q.put(item)                     # always returned, even on exceptions
```

> [!EXAM]
> **How do creational patterns change in Python compared with C++/Java?**
> Classes and functions are first-class objects, so a factory is often just a dict mapping names to classes (or any callables) plus a lookup function. Factory methods become `@classmethod` alternative constructors. Registration can be automatic through class decorators or `__init_subclass__`, and third-party discovery uses entry points. Keyword arguments, defaults and frozen dataclasses with `__post_init__` validation remove most needs for builders. Prototype is `copy.deepcopy` or `dataclasses.replace`, and modules are natural singletons. The underlying ideas (decoupling creation from use, validating construction, controlling instances) remain, with far less code.
