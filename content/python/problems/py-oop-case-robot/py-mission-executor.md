---
id: py-mission-executor
title: "Case Study: Robot Mission Executor"
difficulty: Expert
order: 1
tags: case study, command pattern, observer, planning, state machine, injected clock, error isolation
time_limit: 5
---
## Statement
Implement the warehouse robot's mission layer from the case-study lesson. Tasks are **command objects**, a **planner** inserts charging detours, and an **executor** runs missions while notifying **observers**. Time comes from an injected clock.

**State and world**
- `Mode(Enum)`: `IDLE`, `EXECUTING`, `FAULT`.
- `RobotState(cell: tuple[int, int], battery: float, carrying: str | None = None, mode: Mode = Mode.IDLE)`, a dataclass.
- `World(items: dict[str, tuple[int, int]], chargers: set[tuple[int, int]])`.

**Tasks** (each has `check(state, world) -> str | None`, `apply(state, world) -> int` seconds, and a `repr`):

| Task | `repr` | check failure reason | apply |
|---|---|---|---|
| `MoveTo((x, y))` | `MoveTo(3,4)` | `"battery exhausted"` if `battery − 0.01·d < 0` | `d` = Manhattan distance. The robot moves, `battery = round(battery − 0.01·d, 4)`, and it takes `d` seconds. |
| `Pick(name)` | `Pick(box)` | `"gripper full"`, then `"item <name> not here"` | Carry the item and remove it from `world.items`. 2 s. |
| `Place()` | `Place` | `"nothing to place"` | Put the item at the robot's cell in `world.items`, and empty the gripper. 2 s. |
| `Charge(target=0.9)` | `Charge(0.9)` | `"not at a charger"` | If `battery < target`: take `ceil((target − battery)/0.05)` s and set `battery = target`. Otherwise 0 s. |

**`MissionExecutor(state, world, clock)`**, where `clock.now()` returns seconds and `clock.advance(s)` advances it.
- `subscribe(event, fn)`. Events and their payloads are:
  - `"task_started"(time, task)`
  - `"task_done"(time, task)`
  - `"mission_failed"(time, task, reason)`
  - `"mission_done"(time)`

  Callbacks receive keyword arguments. An exception in a subscriber is recorded in `executor.errors` (as `repr(exc)`) and **doesn't stop the mission**.
- `plan(tasks) -> list`: simulate position and battery. Before any `MoveTo` that would leave the battery **below 0.15**, insert `MoveTo(nearest charger)` (by Manhattan distance from the current simulated cell, ties broken by smaller `(x, y)`) and `Charge(0.9)`, but only if the detour itself keeps the battery ≥ 0. Then the original move. `Charge` tasks in the input update the simulated battery too.
- `run(tasks) -> Report`: plan, set mode to `EXECUTING`, then for each task check → (failure: emit `mission_failed`, mode `IDLE`, return) → emit `task_started` → `clock.advance(apply(...))` → emit `task_done`. On success emit `mission_done` and set mode `IDLE`.
- `Report(ok: bool, reason: str | None, done: int, time: int)`, where `done` counts completed tasks (including detours).

## Starter
```python
from dataclasses import dataclass
from enum import Enum


class Mode(Enum):
    IDLE = "idle"
    EXECUTING = "executing"
    FAULT = "fault"


@dataclass
class RobotState:
    cell: tuple
    battery: float
    carrying: str = None
    mode: Mode = Mode.IDLE


class World:
    def __init__(self, items, chargers):
        self.items, self.chargers = items, chargers


class MoveTo:
    def __init__(self, cell): self.cell = cell
    def apply(self, state, world): state.cell = self.cell; return 0


class MissionExecutor:
    def __init__(self, state, world, clock):
        self.state, self.world, self.clock = state, world, clock

    def run(self, tasks):
        for t in tasks:
            t.apply(self.state, self.world)
```

## Driver
```python
import sys

class Clock:
    def __init__(self): self.t = 0
    def now(self): return self.t
    def advance(self, s): self.t += s

def new(cell=(0, 0), battery=1.0, items=None, chargers=None):
    st = RobotState(cell, battery)
    w = World(dict(items or {}), set(chargers or {(0, 0)}))
    clk = Clock()
    ex = MissionExecutor(st, w, clk)
    log = []
    for ev in ("task_started", "task_done", "mission_failed", "mission_done"):
        ex.subscribe(ev, lambda ev=ev, **kw: log.append(f"{kw['time']}:{ev}" + (f":{kw['task']!r}" if "task" in kw else "") + (f":{kw['reason']}" if "reason" in kw else "")))
    return st, w, clk, ex, log

for cmd in sys.stdin.read().split():
    if cmd == "pickplace":
        st, w, clk, ex, log = new(items={"box": (3, 4)})
        r = ex.run([MoveTo((3, 4)), Pick("box"), MoveTo((1, 1)), Place()])
        print(r)
        print(log)
        print(st, w.items, st.mode)
        print([repr(t) for t in (MoveTo((2, 5)), Pick("x"), Place(), Charge(), Charge(0.75))])
    elif cmd == "failures":
        st, w, clk, ex, log = new(items={"a": (1, 0), "b": (2, 0)})
        print(ex.run([MoveTo((1, 0)), Pick("a"), MoveTo((2, 0)), Pick("b"), Place()]))
        print(log[-2:], st.carrying, st.mode)
        st2, w2, clk2, ex2, log2 = new(items={"a": (5, 5)})
        print(ex2.run([Pick("a")]), ex2.run([Place()]), ex2.run([Charge()]))
        st3, w3, clk3, ex3, log3 = new(cell=(2, 2), chargers={(9, 9)})
        print(ex3.run([MoveTo((3, 3)), Charge()]), log3[-1])
        boom = []
        def bad(**kw): raise RuntimeError("ui crashed")
        st4, w4, clk4, ex4, log4 = new(items={"z": (0, 1)})
        ex4.subscribe("task_done", bad)
        print(ex4.run([MoveTo((0, 1)), Pick("z")]), len(ex4.errors), ex4.errors[0])
    elif cmd == "planning":
        st, w, clk, ex, log = new(cell=(0, 0), battery=0.3, chargers={(0, 0), (10, 0), (10, 10)})
        tasks = [MoveTo((12, 0)), MoveTo((12, 9))]
        print([repr(t) for t in ex.plan(tasks)])
        r = ex.run(tasks)
        print(r, round(st.battery, 4), st.cell)
        print([l for l in log if "started" in l])
        st2, w2, clk2, ex2, log2 = new(cell=(5, 5), battery=0.2, chargers={(0, 0)})
        print([repr(t) for t in ex2.plan([MoveTo((5, 6)), MoveTo((15, 15))])])
        st3, w3, clk3, ex3, log3 = new(cell=(0, 0), battery=0.16, chargers={(0, 0), (4, 4)})
        print([repr(t) for t in ex3.plan([Charge(0.5), MoveTo((20, 0))])])
    elif cmd == "load":
        import itertools
        items = {f"box{i}": (i % 17, (i * 7) % 13) for i in range(300)}
        st, w, clk, ex, log = new(battery=0.5, items=items, chargers={(0, 0), (16, 12), (8, 6)})
        done = fails = 0
        for i in range(300):
            mission = [MoveTo(items[f"box{i}"]), Pick(f"box{i}"), MoveTo(((i * 3) % 20, (i * 5) % 20)), Place()]
            r = ex.run(mission)
            done += r.done; fails += not r.ok
        print("tasks", done, "failed missions", fails, "time", clk.now(), "battery", round(st.battery, 4), "events", len(log))
```

## Tests
=== sample
pickplace
---
Report(ok=True, reason=None, done=4, time=16)
['0:task_started:MoveTo(3,4)', '7:task_done:MoveTo(3,4)', '7:task_started:Pick(box)', '9:task_done:Pick(box)', '9:task_started:MoveTo(1,1)', '14:task_done:MoveTo(1,1)', '14:task_started:Place', '16:task_done:Place', '16:mission_done']
RobotState(cell=(1, 1), battery=0.88, carrying=None, mode=<Mode.IDLE: 'idle'>) {'box': (1, 1)} Mode.IDLE
['MoveTo(2,5)', 'Pick(x)', 'Place', 'Charge(0.9)', 'Charge(0.75)']
=== hidden
failures
---
Report(ok=False, reason='gripper full', done=3, time=4)
['4:task_done:MoveTo(2,0)', '4:mission_failed:Pick(b):gripper full'] a Mode.IDLE
Report(ok=False, reason='item a not here', done=0, time=0) Report(ok=False, reason='nothing to place', done=0, time=0) Report(ok=True, reason=None, done=1, time=0)
Report(ok=False, reason='not at a charger', done=1, time=2) 2:mission_failed:Charge(0.9):not at a charger
Report(ok=True, reason=None, done=2, time=3) 2 RuntimeError('ui crashed')
=== hidden
planning
---
['MoveTo(12,0)', 'MoveTo(10,0)', 'Charge(0.9)', 'MoveTo(12,9)']
Report(ok=True, reason=None, done=4, time=40) 0.79 (12, 9)
['0:task_started:MoveTo(12,0)', '12:task_started:MoveTo(10,0)', '14:task_started:Charge(0.9)', '29:task_started:MoveTo(12,9)']
['MoveTo(5,6)', 'MoveTo(0,0)', 'Charge(0.9)', 'MoveTo(15,15)']
['Charge(0.5)', 'MoveTo(20,0)']
=== hidden
load
---
tasks 1406 failed missions 0 time 10456 battery 0.26 events 3112

## Hints
- Give `Task` a base class with `check`/`apply`/`__repr__`. The executor only ever calls those three, which is the Command pattern.
- `plan`: keep simulated `(cell, battery)`. For a `MoveTo` with cost `c = 0.01·d`, if `battery − c < 0.15`, find the nearest charger `k`. If `battery − 0.01·dist(cell, k) >= 0`, emit `MoveTo(k)` and `Charge(0.9)`, and update the simulation. Then emit the move.
- `_emit(event, **payload)`: call each subscriber inside `try/except Exception as e: self.errors.append(repr(e))`.
- `Report` can be a frozen dataclass, so `print(report)` shows all four fields.

## Solution
```python
import math
from dataclasses import dataclass
from enum import Enum

RESERVE = 0.15
COST_PER_CELL = 0.01


class Mode(Enum):
    IDLE = "idle"
    EXECUTING = "executing"
    FAULT = "fault"


@dataclass
class RobotState:
    cell: tuple[int, int]
    battery: float
    carrying: str | None = None
    mode: Mode = Mode.IDLE


class World:
    def __init__(self, items: dict[str, tuple[int, int]], chargers: set[tuple[int, int]]):
        self.items, self.chargers = items, chargers


def manhattan(a, b) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class Task:
    def check(self, state: RobotState, world: World) -> str | None:
        return None

    def apply(self, state: RobotState, world: World) -> int:
        raise NotImplementedError


class MoveTo(Task):
    def __init__(self, cell): self.cell = tuple(cell)
    def __repr__(self): return f"MoveTo({self.cell[0]},{self.cell[1]})"
    def check(self, state, world):
        return "battery exhausted" if state.battery - COST_PER_CELL * manhattan(state.cell, self.cell) < 0 else None
    def apply(self, state, world):
        d = manhattan(state.cell, self.cell)
        state.cell = self.cell
        state.battery = round(state.battery - COST_PER_CELL * d, 4)
        return d


class Pick(Task):
    def __init__(self, item): self.item = item
    def __repr__(self): return f"Pick({self.item})"
    def check(self, state, world):
        if state.carrying is not None:
            return "gripper full"
        if world.items.get(self.item) != state.cell:
            return f"item {self.item} not here"
        return None
    def apply(self, state, world):
        state.carrying = self.item
        del world.items[self.item]
        return 2


class Place(Task):
    def __repr__(self): return "Place"
    def check(self, state, world):
        return None if state.carrying is not None else "nothing to place"
    def apply(self, state, world):
        world.items[state.carrying] = state.cell
        state.carrying = None
        return 2


class Charge(Task):
    def __init__(self, target: float = 0.9): self.target = target
    def __repr__(self): return f"Charge({self.target})"
    def check(self, state, world):
        return None if state.cell in world.chargers else "not at a charger"
    def apply(self, state, world):
        if state.battery >= self.target:
            return 0
        seconds = math.ceil(round((self.target - state.battery) / 0.05, 9))
        state.battery = self.target
        return seconds


@dataclass(frozen=True)
class Report:
    ok: bool
    reason: str | None
    done: int
    time: int


class MissionExecutor:
    def __init__(self, state: RobotState, world: World, clock):
        self.state, self.world, self.clock = state, world, clock
        self._subs: dict[str, list] = {}
        self.errors: list[str] = []

    def subscribe(self, event: str, fn) -> None:
        self._subs.setdefault(event, []).append(fn)

    def _emit(self, event: str, **payload) -> None:
        for fn in list(self._subs.get(event, ())):
            try:
                fn(time=self.clock.now(), **payload)
            except Exception as e:                   # observers must not break the mission
                self.errors.append(repr(e))

    def plan(self, tasks: list[Task]) -> list[Task]:
        cell, battery, out = self.state.cell, self.state.battery, []
        for t in tasks:
            if isinstance(t, MoveTo):
                cost = COST_PER_CELL * manhattan(cell, t.cell)
                if battery - cost < RESERVE and self.world.chargers:
                    k = min(self.world.chargers, key=lambda c: (manhattan(cell, c), c))
                    detour = COST_PER_CELL * manhattan(cell, k)
                    if battery - detour >= 0:
                        out += [MoveTo(k), Charge(0.9)]
                        battery = max(round(battery - detour, 4), 0.9)
                        cell = k
                        cost = COST_PER_CELL * manhattan(cell, t.cell)
                battery = round(battery - cost, 4)
                cell = t.cell
            elif isinstance(t, Charge) and cell in self.world.chargers:
                battery = max(battery, t.target)
            out.append(t)
        return out

    def run(self, tasks: list[Task]) -> Report:
        start = self.clock.now()
        self.state.mode = Mode.EXECUTING
        done = 0
        for task in self.plan(tasks):
            reason = task.check(self.state, self.world)
            if reason:
                self.state.mode = Mode.IDLE
                self._emit("mission_failed", task=task, reason=reason)
                return Report(False, reason, done, self.clock.now() - start)
            self._emit("task_started", task=task)
            self.clock.advance(task.apply(self.state, self.world))
            self._emit("task_done", task=task)
            done += 1
        self.state.mode = Mode.IDLE
        self._emit("mission_done")
        return Report(True, None, done, self.clock.now() - start)
```

- **Command objects**: each task encapsulates its preconditions (`check`) and effects (`apply`). The executor runs any task uniformly, so new task types (`Dock`, `Scan`) need no executor changes.
- **Plan before acting**: the planner simulates the mission with the same cost model and inserts charging detours in advance, so execution stays simple and the battery never drops below the reserve on a feasible route.
- **Observers with isolation**: the UI, logs and fleet manager subscribe to events. A crashing subscriber is recorded, and the robot keeps working.
- **Explicit mode transitions** (`IDLE ↔ EXECUTING`) and precise failure reasons make the robot's behaviour inspectable. Injected time makes 300 missions run in milliseconds and reproducibly.
