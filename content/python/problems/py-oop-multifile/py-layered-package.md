---
id: py-layered-package
title: A Layered Multi-Package Project
difficulty: Hard
order: 1
tags: packages, layered architecture, __init__ re-exports, relative imports, ports and adapters, multi-file
time_limit: 5
---
## Statement
Organise a small fleet-dispatch application as a **layered package**. The judge imports your package, checks the public API, runs the use case, and **parses your source files with `ast`** to enforce the dependency rule.

```text
fleetops/
  __init__.py              public API: Robot, Mission, DispatchError, Dispatcher (and __all__ with exactly these)
  domain/   robot.py mission.py errors.py     pure model: must not import services or adapters
  services/ ports.py dispatcher.py            use case + Protocols: must not import adapters
  adapters/ memory.py                         InMemoryRobots, ListLog (implement the ports)
```

**Domain**
- `Robot(id, battery, busy=False)` is a dataclass with `can_take(distance)`: not busy, and `battery − distance·0.001 ≥ 0.2`. Its `take(distance)` marks the robot busy and sets `battery = round(battery − distance·0.001, 4)`.
- `Mission(id, distance, priority=0)` is **frozen**. `distance <= 0` raises `DispatchError`.

**Ports** (`services/ports.py`): Protocols `RobotRepository` (`all()`, `save(robot)`) and `MissionLog` (`record(line)`).

**Use case: `Dispatcher(robots, log).dispatch(missions) -> dict[mission_id, robot_id | None]`**
- Duplicate mission ids raise `DispatchError`.
- Process missions by **priority descending, then id**.
- For each mission, pick the robot that can take it with the **highest battery** (ties go to the lower id), call `take`, **`save` it through the repository**, and log `"<mission>-><robot>"`.
- If no robot can take a mission, map it to `None` and log `"mission <id> unassigned"`.

**Adapters**
- `InMemoryRobots(robots)` behaves like a database: `all()` returns **copies** sorted by id, and `save` stores a copy. Changes therefore persist only through `save`.
- `ListLog` has `.lines`.

Use **relative imports** inside the package.

## Starter: fleetops/__init__.py
```python
from .adapters.memory import *          # everything dumped at the top level
```

## Starter: fleetops/domain/__init__.py
```python

```

## Starter: fleetops/domain/errors.py
```python
class DispatchError(Exception):
    pass
```

## Starter: fleetops/domain/robot.py
```python
from dataclasses import dataclass
from ..adapters.memory import InMemoryRobots     # domain importing an adapter: layering violation


@dataclass
class Robot:
    id: str
    battery: float
    busy: bool = False
```

## Starter: fleetops/domain/mission.py
```python
from dataclasses import dataclass


@dataclass
class Mission:
    id: str
    distance: float
    priority: int = 0
```

## Starter: fleetops/services/__init__.py
```python

```

## Starter: fleetops/services/ports.py
```python

```

## Starter: fleetops/services/dispatcher.py
```python
class Dispatcher:
    def __init__(self, robots, log):
        self.robots, self.log = robots, log

    def dispatch(self, missions):
        return {m.id: None for m in missions}
```

## Starter: fleetops/adapters/__init__.py
```python

```

## Starter: fleetops/adapters/memory.py
```python
from ..domain.robot import Robot


class InMemoryRobots:
    def __init__(self, robots=None):
        self.robots = robots or []

    def all(self):
        return self.robots

    def save(self, robot):
        pass


class ListLog:
    def __init__(self):
        self.lines = []

    def record(self, line):
        self.lines.append(line)
```

## Driver: main.py
```python
import ast
import pathlib
import sys

import fleetops
from fleetops import Dispatcher, DispatchError, Mission, Robot
from fleetops.adapters.memory import InMemoryRobots, ListLog

def layer_violations():
    root = pathlib.Path(fleetops.__file__).parent
    rules = {"domain": ("services", "adapters"), "services": ("adapters",)}
    bad = []
    for layer, forbidden in rules.items():
        for path in sorted((root / layer).glob("*.py")):
            for node in ast.walk(ast.parse(path.read_text())):
                mods = []
                if isinstance(node, ast.ImportFrom):
                    mods = [("." * node.level) + (node.module or "")]
                elif isinstance(node, ast.Import):
                    mods = [a.name for a in node.names]
                for m in mods:
                    if any(f in m.split(".") for f in forbidden):
                        bad.append(f"{layer}/{path.name} imports {m}")
    return bad

for cmd in sys.stdin.read().split():
    if cmd == "api":
        print("public:", sorted(fleetops.__all__))
        print("violations:", layer_violations())
        print("robot module:", Robot.__module__, "| dispatcher module:", Dispatcher.__module__)
        try:
            Mission("m0", 0)
        except DispatchError as e:
            print("invalid mission:", e)
        m = Mission("m1", 10.0, 2)
        try:
            m.priority = 5
        except Exception as e:
            print("missions immutable:", type(e).__name__)
    elif cmd == "dispatch":
        repo = InMemoryRobots([Robot("r1", 0.9), Robot("r2", 0.95), Robot("r3", 0.3), Robot("r4", 0.95)])
        log = ListLog()
        d = Dispatcher(repo, log)
        result = d.dispatch([Mission("a", 100), Mission("b", 50, priority=5), Mission("c", 200, priority=5),
                             Mission("d", 150), Mission("e", 10, priority=-1)])
        print(result)
        print(log.lines)
        print([(r.id, r.battery, r.busy) for r in repo.all()])
        try:
            d.dispatch([Mission("x", 1), Mission("x", 2)])
        except DispatchError as e:
            print("error:", e)
    elif cmd == "load":
        repo = InMemoryRobots([Robot(f"r{i:03d}", 0.3 + (i % 70) / 100) for i in range(300)])
        log = ListLog()
        res = Dispatcher(repo, log).dispatch([Mission(f"m{i:04d}", 10 + (i * 37) % 500, priority=i % 4) for i in range(400)])
        assigned = sum(v is not None for v in res.values())
        print("assigned", assigned, "unassigned", len(res) - assigned, "busy", sum(r.busy for r in repo.all()), "log", len(log.lines), log.lines[:2])
```

## Tests
=== sample
api
---
public: ['DispatchError', 'Dispatcher', 'Mission', 'Robot']
violations: []
robot module: fleetops.domain.robot | dispatcher module: fleetops.services.dispatcher
invalid mission: mission m0: distance must be > 0
missions immutable: FrozenInstanceError
=== hidden
dispatch
---
{'b': 'r2', 'c': 'r4', 'a': 'r1', 'd': None, 'e': 'r3'}
['b->r2', 'c->r4', 'a->r1', 'mission d unassigned', 'e->r3']
[('r1', 0.8, True), ('r2', 0.9, True), ('r3', 0.29, True), ('r4', 0.75, True)]
error: duplicate mission ids
=== hidden
load
---
assigned 273 unassigned 127 busy 273 log 400 ['m0003->r069', 'm0007->r139']

## Hints
- The domain is the innermost layer: it may import only from itself (`from .errors import DispatchError`).
- `services/ports.py` defines the `Protocol`s, and `services/dispatcher.py` imports `..domain.*` and `.ports`, but never `..adapters`.
- Re-export the public API in `fleetops/__init__.py` and define `__all__`, so users write `from fleetops import Robot`.
- Because `InMemoryRobots.all()` returns copies, the dispatcher must call `save(robot)` after `take`. Otherwise later missions see the old battery and busy flag.

## Solution: fleetops/__init__.py
```python
"""fleetops: public API re-exported from the internal layers."""
from .domain.mission import Mission
from .domain.robot import Robot
from .domain.errors import DispatchError
from .services.dispatcher import Dispatcher

__all__ = ["Robot", "Mission", "DispatchError", "Dispatcher"]
__version__ = "1.0.0"
```

## Solution: fleetops/domain/__init__.py
```python
"""Pure domain model: no imports from services or adapters."""
```

## Solution: fleetops/domain/errors.py
```python
class DispatchError(Exception):
    """Raised for invalid dispatch requests."""
```

## Solution: fleetops/domain/robot.py
```python
from dataclasses import dataclass

RESERVE = 0.2
ENERGY_PER_M = 0.001


@dataclass
class Robot:
    id: str
    battery: float
    busy: bool = False

    def can_take(self, distance: float) -> bool:
        return not self.busy and self.battery - distance * ENERGY_PER_M >= RESERVE

    def take(self, distance: float) -> None:
        self.busy = True
        self.battery = round(self.battery - distance * ENERGY_PER_M, 4)
```

## Solution: fleetops/domain/mission.py
```python
from dataclasses import dataclass

from .errors import DispatchError


@dataclass(frozen=True)
class Mission:
    id: str
    distance: float
    priority: int = 0

    def __post_init__(self):
        if self.distance <= 0:
            raise DispatchError(f"mission {self.id}: distance must be > 0")
```

## Solution: fleetops/services/__init__.py
```python
"""Use cases. Depend on domain + ports only, never on adapters."""
```

## Solution: fleetops/services/ports.py
```python
from typing import Protocol

from ..domain.robot import Robot


class RobotRepository(Protocol):
    def all(self) -> list[Robot]: ...
    def save(self, robot: Robot) -> None: ...


class MissionLog(Protocol):
    def record(self, line: str) -> None: ...
```

## Solution: fleetops/services/dispatcher.py
```python
from ..domain.errors import DispatchError
from ..domain.mission import Mission
from .ports import MissionLog, RobotRepository


class Dispatcher:
    def __init__(self, robots: RobotRepository, log: MissionLog):
        self._robots = robots
        self._log = log

    def dispatch(self, missions: list[Mission]) -> dict[str, str | None]:
        ids = [m.id for m in missions]
        if len(ids) != len(set(ids)):
            raise DispatchError("duplicate mission ids")
        result: dict[str, str | None] = {}
        for m in sorted(missions, key=lambda m: (-m.priority, m.id)):
            candidates = [r for r in self._robots.all() if r.can_take(m.distance)]
            if not candidates:
                result[m.id] = None
                self._log.record(f"mission {m.id} unassigned")
                continue
            best = min(candidates, key=lambda r: (-r.battery, r.id))
            best.take(m.distance)
            self._robots.save(best)
            result[m.id] = best.id
            self._log.record(f"{m.id}->{best.id}")
        return result
```

## Solution: fleetops/adapters/__init__.py
```python
"""I/O implementations of the service ports."""
```

## Solution: fleetops/adapters/memory.py
```python
import copy

from ..domain.robot import Robot


class InMemoryRobots:
    """Behaves like a database: returns copies, so changes persist only through save()."""

    def __init__(self, robots: list[Robot] | None = None):
        self._data = {r.id: copy.copy(r) for r in robots or []}

    def all(self) -> list[Robot]:
        return [copy.copy(self._data[k]) for k in sorted(self._data)]

    def save(self, robot: Robot) -> None:
        self._data[robot.id] = copy.copy(robot)


class ListLog:
    def __init__(self):
        self.lines: list[str] = []

    def record(self, line: str) -> None:
        self.lines.append(line)
```

## Solution
- **Layers with one-way dependencies**: adapters → services → domain. The `ast` check proves that the domain imports nothing outward and that services never touch adapters. The starter's `domain/robot.py` importing an adapter is the classic violation, and it creates a circular import once the adapter imports `Robot` back.
- **Ports as Protocols**: the dispatcher depends on `RobotRepository` and `MissionLog` abstractions. An SQL repository or a ROS logger could replace the in-memory adapters without editing the use case.
- **A curated public API**: `fleetops/__init__.py` re-exports four names with `__all__`, so the internal layout can be reorganised without breaking users. The starter's `import *` leaked adapter internals.
- **Copying repositories** model real persistence: because `all()` returns detached copies, a use case that mutates without `save()` silently loses its changes. The dispatch test would show two missions given to the same "still idle" robot.
- **Frozen missions** are value objects: dispatching can't accidentally change a mission's priority or distance.
