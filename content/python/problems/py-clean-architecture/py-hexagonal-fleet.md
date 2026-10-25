---
id: py-hexagonal-fleet
title: Hexagonal Fleet Service (Ports and Adapters)
difficulty: Hard
order: 1
tags: clean architecture, ports and adapters, Protocol, use cases, repositories, dependency injection, fakes
time_limit: 5
---
## Statement
Implement the core of a fleet manager in **ports-and-adapters** style. The use cases depend only on the ports (Protocols) below. The judge wires in its own adapters: a fake clock, a notifier, and its own repository implementation whose `get()` returns **copies**. Changes therefore persist only if your use case calls `save()` / `add()` through the port.

```python
class RobotRepository(Protocol):
    def get(self, robot_id: str) -> Robot | None: ...
    def save(self, robot: Robot) -> None: ...
    def all(self) -> list[Robot]: ...
class MissionRepository(Protocol):
    def get(self, mission_id: str) -> Mission | None: ...
    def add(self, mission: Mission) -> None: ...
    def save(self, mission: Mission) -> None: ...
    def all(self) -> list[Mission]: ...
class Clock(Protocol):
    def now(self) -> float: ...
class Notifier(Protocol):
    def notify(self, event: str, mission_id: str) -> None: ...
```

**Domain** (dataclasses, already declared in the starter): `Robot(id, battery, busy=False)`, and `Mission(id, robot_id, distance, status="active", started=0.0, finished=None, reason=None)`. `DomainError(Exception)` signals rule violations. **Battery use is 0.0005 per metre.**

**`FleetService(robots, missions, clock, notifier, ids)`**, where `ids` is an iterator of mission id strings:

| Method | Rules |
|---|---|
| `register_robot(id, battery)` | `"duplicate robot"` if the id exists. `"battery out of range"` unless `0 <= battery <= 1`. |
| `plan(robot_id, distance) -> str` | Checked in this order: `"unknown robot"`, `"invalid distance"` (≤ 0), `"robot busy"`, `"insufficient battery"` (`battery - distance·0.0005 < 0.2`). Creates an active mission with `started = clock.now()`, marks the robot busy, notifies `"started"`, and returns the id. |
| `complete(mission_id)` | `"unknown mission"`, `"mission not active"`. Sets status `"done"` and `finished = now`. The robot's battery becomes `round(battery - distance·0.0005, 4)`, and the robot is freed. Notifies `"completed"`. |
| `abort(mission_id, reason)` | Same errors as `complete`. Sets status `"aborted"` with `finished` and `reason`, and frees the robot without changing its battery. Notifies `"aborted"`. |
| `abort_overdue(max_seconds) -> list[str]` | Aborts (reason `"timeout"`) every active mission with `now - started > max_seconds`, returning their ids sorted. |
| `report() -> list[dict]` | Per robot, sorted by id: `{"id", "battery", "busy", "done", "distance"}`, where `done` counts completed missions and `distance` is their total. |

Also implement the in-memory adapters `InMemoryRobots` and `InMemoryMissions` that satisfy the ports. The judge uses them in one test.

## Starter
```python
from dataclasses import dataclass
from typing import Protocol


class DomainError(Exception):
    pass


@dataclass
class Robot:
    id: str
    battery: float
    busy: bool = False


@dataclass
class Mission:
    id: str
    robot_id: str
    distance: float
    status: str = "active"
    started: float = 0.0
    finished: float | None = None
    reason: str | None = None


class FleetService:
    def __init__(self, robots, missions, clock, notifier, ids):
        self.robots, self.missions, self.clock, self.notifier, self.ids = robots, missions, clock, notifier, ids

    def register_robot(self, robot_id, battery):
        self.robots.save(Robot(robot_id, battery))

    def plan(self, robot_id, distance):
        robot = self.robots.get(robot_id)
        mid = next(self.ids)
        self.missions.add(Mission(mid, robot_id, distance))
        robot.busy = True
        return mid

    def complete(self, mission_id):
        self.missions.get(mission_id).status = "done"

    def abort(self, mission_id, reason):
        pass

    def abort_overdue(self, max_seconds):
        return []

    def report(self):
        return []


class InMemoryRobots:
    pass


class InMemoryMissions:
    pass
```

## Driver
```python
import copy
import itertools
import sys

class CopyingRepo:                                   # judge adapter: like a DB, get() returns a detached copy
    def __init__(self): self._d = {}; self.writes = 0
    def get(self, key): v = self._d.get(key); return copy.deepcopy(v)
    def save(self, obj): self._d[obj.id] = copy.deepcopy(obj); self.writes += 1
    add = save
    def all(self): return [copy.deepcopy(v) for _, v in sorted(self._d.items())]

class FakeClock:
    def __init__(self): self.t = 1000.0
    def now(self): return self.t

class Recorder:
    def __init__(self): self.events = []
    def notify(self, event, mission_id): self.events.append(f"{event}:{mission_id}")

def attempt(label, fn):
    try:
        print(f"{label}: {fn()!r}")
    except DomainError as e:
        print(f"{label}: DomainError {e}")

def make(robots=None, missions=None):
    clock, rec = FakeClock(), Recorder()
    svc = FleetService(robots or CopyingRepo(), missions or CopyingRepo(), clock, rec, (f"m{i}" for i in itertools.count(1)))
    return svc, clock, rec

for cmd in sys.stdin.read().split():
    if cmd == "basic":
        svc, clock, rec = make()
        attempt("reg r1", lambda: svc.register_robot("r1", 0.9))
        attempt("reg r2", lambda: svc.register_robot("r2", 0.3))
        attempt("dup", lambda: svc.register_robot("r1", 0.5))
        attempt("bad battery", lambda: svc.register_robot("r3", 1.2))
        attempt("unknown", lambda: svc.plan("zz", 10))
        attempt("bad distance", lambda: svc.plan("r1", 0))
        attempt("insufficient", lambda: svc.plan("r2", 300))
        attempt("plan r1", lambda: svc.plan("r1", 400))
        attempt("busy", lambda: svc.plan("r1", 10))
        attempt("plan r2", lambda: svc.plan("r2", 100))
        clock.t += 60
        attempt("complete m1", lambda: svc.complete("m1"))
        attempt("again", lambda: svc.complete("m1"))
        attempt("unknown mission", lambda: svc.complete("m9"))
        attempt("abort m2", lambda: svc.abort("m2", "operator"))
        attempt("abort done", lambda: svc.abort("m1", "late"))
        attempt("replan r1", lambda: svc.plan("r1", 200))
        attempt("report", svc.report)
        print("events", rec.events)
        m1 = svc.missions.get("m1"); m2 = svc.missions.get("m2")
        print("m1", m1.status, m1.started, m1.finished, "| m2", m2.status, m2.reason, m2.finished)
    elif cmd == "overdue":
        svc, clock, rec = make()
        for r in ["a", "b", "c", "d"]:
            svc.register_robot(r, 1.0)
        svc.plan("a", 10); clock.t += 100
        svc.plan("b", 10); clock.t += 100
        svc.plan("c", 10); svc.complete("m1")
        clock.t += 50
        attempt("overdue 120", lambda: svc.abort_overdue(120))
        attempt("overdue 120 again", lambda: svc.abort_overdue(120))
        clock.t += 1000
        attempt("overdue 1000", lambda: svc.abort_overdue(1000))
        attempt("report", svc.report)
        print("events", rec.events)
    elif cmd == "inmemory":
        svc, clock, rec = make(InMemoryRobots(), InMemoryMissions())
        svc.register_robot("x", 0.5); svc.register_robot("y", 0.25)
        attempt("plan", lambda: svc.plan("x", 200))
        attempt("y too far", lambda: svc.plan("y", 101))
        attempt("y ok", lambda: svc.plan("y", 100))
        svc.complete("m1"); svc.complete("m2")
        attempt("report", svc.report)
        attempt("missions", lambda: [(m.id, m.status) for m in svc.missions.all()])
    elif cmd == "load":
        robots, missions = CopyingRepo(), CopyingRepo()
        svc, clock, rec = make(robots, missions)
        for i in range(60):
            svc.register_robot(f"r{i:02d}", 1.0)
        errors = {}
        for step in range(3000):
            clock.t += 7
            rid = f"r{step * 7 % 60:02d}"
            try:
                mid = svc.plan(rid, 50 + step % 400)
                if step % 3 == 0:
                    svc.complete(mid)
            except DomainError as e:
                errors[str(e)] = errors.get(str(e), 0) + 1
            if step % 100 == 99:
                svc.abort_overdue(200)
        rep = svc.report()
        print("errors", dict(sorted(errors.items())))
        print("done", sum(r["done"] for r in rep), "busy", sum(r["busy"] for r in rep), "min battery", min(r["battery"] for r in rep))
        print(rep[:2])
        print("events", len(rec.events), "robot writes > 0:", robots.writes > 0, "mission writes > 0:", missions.writes > 0)
```

## Tests
=== sample
basic
---
reg r1: None
reg r2: None
dup: DomainError duplicate robot
bad battery: DomainError battery out of range
unknown: DomainError unknown robot
bad distance: DomainError invalid distance
insufficient: DomainError insufficient battery
plan r1: 'm1'
busy: DomainError robot busy
plan r2: 'm2'
complete m1: None
again: DomainError mission not active
unknown mission: DomainError unknown mission
abort m2: None
abort done: DomainError mission not active
replan r1: 'm3'
report: [{'id': 'r1', 'battery': 0.7, 'busy': True, 'done': 1, 'distance': 400.0}, {'id': 'r2', 'battery': 0.3, 'busy': False, 'done': 0, 'distance': 0.0}]
events ['started:m1', 'started:m2', 'completed:m1', 'aborted:m2', 'started:m3']
m1 done 1000.0 1060.0 | m2 aborted operator 1060.0
=== hidden
overdue
---
overdue 120: ['m2']
overdue 120 again: []
overdue 1000: ['m3']
report: [{'id': 'a', 'battery': 0.995, 'busy': False, 'done': 1, 'distance': 10.0}, {'id': 'b', 'battery': 1.0, 'busy': False, 'done': 0, 'distance': 0.0}, {'id': 'c', 'battery': 1.0, 'busy': False, 'done': 0, 'distance': 0.0}, {'id': 'd', 'battery': 1.0, 'busy': False, 'done': 0, 'distance': 0.0}]
events ['started:m1', 'started:m2', 'started:m3', 'completed:m1', 'aborted:m2', 'aborted:m3']
=== hidden
inmemory
---
plan: 'm1'
y too far: DomainError insufficient battery
y ok: 'm2'
report: [{'id': 'x', 'battery': 0.4, 'busy': False, 'done': 1, 'distance': 200.0}, {'id': 'y', 'battery': 0.2, 'busy': False, 'done': 1, 'distance': 100.0}]
missions: [('m1', 'done'), ('m2', 'done')]
=== hidden
load
---
errors {'insufficient battery': 836, 'robot busy': 800}
done 164 busy 0 min battery 0.2
[{'id': 'r00', 'battery': 0.205, 'busy': False, 'done': 9, 'distance': 1590.0}, {'id': 'r01', 'battery': 1.0, 'busy': False, 'done': 0, 'distance': 0.0}]
events 2728 robot writes > 0: True mission writes > 0: True

## Hints
- Treat repositories like a database: `robot = self.robots.get(id)`, mutate the copy, then `self.robots.save(robot)`. Mutating an object you fetched is **not** enough with a real database.
- Write two helpers, `_robot(id)` and `_active_mission(id)`, that raise the right `DomainError`s, and share them between `complete` and `abort`.
- `abort_overdue`: collect the ids first (`[m.id for m in self.missions.all() if ...]`), then abort each one.
- In-memory adapters: a dict keyed by id, with `all()` sorted by id. They may store the objects themselves.

## Solution
```python
from dataclasses import dataclass
from typing import Protocol

ENERGY_PER_M = 0.0005
RESERVE = 0.2


class DomainError(Exception):
    pass


@dataclass
class Robot:
    id: str
    battery: float
    busy: bool = False

    def can_drive(self, distance: float) -> bool:
        return self.battery - distance * ENERGY_PER_M >= RESERVE


@dataclass
class Mission:
    id: str
    robot_id: str
    distance: float
    status: str = "active"
    started: float = 0.0
    finished: float | None = None
    reason: str | None = None

    def finish(self, status: str, now: float, reason: str | None = None) -> None:
        if self.status != "active":
            raise DomainError("mission not active")
        self.status, self.finished, self.reason = status, now, reason


# ---- ports (structural; adapters never import these) ----
class RobotRepository(Protocol):
    def get(self, robot_id: str) -> Robot | None: ...
    def save(self, robot: Robot) -> None: ...
    def all(self) -> list[Robot]: ...


class MissionRepository(Protocol):
    def get(self, mission_id: str) -> Mission | None: ...
    def add(self, mission: Mission) -> None: ...
    def save(self, mission: Mission) -> None: ...
    def all(self) -> list[Mission]: ...


class Clock(Protocol):
    def now(self) -> float: ...


class Notifier(Protocol):
    def notify(self, event: str, mission_id: str) -> None: ...


# ---- application layer ----
class FleetService:
    def __init__(self, robots: RobotRepository, missions: MissionRepository, clock: Clock,
                 notifier: Notifier, ids):
        self.robots, self.missions, self.clock, self.notifier, self.ids = robots, missions, clock, notifier, ids

    def _robot(self, robot_id: str) -> Robot:
        robot = self.robots.get(robot_id)
        if robot is None:
            raise DomainError("unknown robot")
        return robot

    def _mission(self, mission_id: str) -> Mission:
        mission = self.missions.get(mission_id)
        if mission is None:
            raise DomainError("unknown mission")
        return mission

    def register_robot(self, robot_id: str, battery: float) -> None:
        if self.robots.get(robot_id) is not None:
            raise DomainError("duplicate robot")
        if not 0 <= battery <= 1:
            raise DomainError("battery out of range")
        self.robots.save(Robot(robot_id, battery))

    def plan(self, robot_id: str, distance: float) -> str:
        robot = self._robot(robot_id)
        if distance <= 0:
            raise DomainError("invalid distance")
        if robot.busy:
            raise DomainError("robot busy")
        if not robot.can_drive(distance):
            raise DomainError("insufficient battery")
        mission = Mission(next(self.ids), robot_id, distance, started=self.clock.now())
        robot.busy = True
        self.missions.add(mission)
        self.robots.save(robot)
        self.notifier.notify("started", mission.id)
        return mission.id

    def _end(self, mission_id: str, status: str, reason: str | None) -> None:
        mission = self._mission(mission_id)
        mission.finish(status, self.clock.now(), reason)
        robot = self._robot(mission.robot_id)
        if status == "done":
            robot.battery = round(robot.battery - mission.distance * ENERGY_PER_M, 4)
        robot.busy = False
        self.missions.save(mission)
        self.robots.save(robot)
        self.notifier.notify("completed" if status == "done" else "aborted", mission_id)

    def complete(self, mission_id: str) -> None:
        self._end(mission_id, "done", None)

    def abort(self, mission_id: str, reason: str) -> None:
        self._end(mission_id, "aborted", reason)

    def abort_overdue(self, max_seconds: float) -> list[str]:
        now = self.clock.now()
        overdue = sorted(m.id for m in self.missions.all() if m.status == "active" and now - m.started > max_seconds)
        for mid in overdue:
            self.abort(mid, "timeout")
        return overdue

    def report(self) -> list[dict]:
        stats: dict[str, list] = {}
        for m in self.missions.all():
            if m.status == "done":
                s = stats.setdefault(m.robot_id, [0, 0.0])
                s[0] += 1
                s[1] += m.distance
        return [{"id": r.id, "battery": r.battery, "busy": r.busy,
                 "done": stats.get(r.id, [0, 0.0])[0], "distance": stats.get(r.id, [0, 0.0])[1]}
                for r in sorted(self.robots.all(), key=lambda r: r.id)]


# ---- adapters ----
class InMemoryRobots:
    def __init__(self):
        self._d: dict[str, Robot] = {}
    def get(self, robot_id): return self._d.get(robot_id)
    def save(self, robot): self._d[robot.id] = robot
    def all(self): return [self._d[k] for k in sorted(self._d)]


class InMemoryMissions:
    def __init__(self):
        self._d: dict[str, Mission] = {}
    def get(self, mission_id): return self._d.get(mission_id)
    def add(self, mission): self._d[mission.id] = mission
    save = add
    def all(self): return [self._d[k] for k in sorted(self._d)]
```

- **Rules live in the domain**: the battery reserve is `Robot.can_drive`, and "only active missions finish" is `Mission.finish`. The service orchestrates, and the entities protect their invariants.
- **Ports are Protocols**, so the judge's `CopyingRepo` satisfies them without importing anything. That's the point of hexagonal architecture: adapters depend on the core, never the reverse.
- **Explicit persistence**: real repositories (SQL, an HTTP service) return detached objects. Mutating `robot.busy` without `save()` is the classic bug that only appears when the in-memory fake is swapped for the database. The copying adapter exposes it in tests.
- **Injected clock, id generator and notifier** make every behaviour, including timeouts, deterministic and fast to test, with no real time, database or message broker.
- **One `_end` path** for complete and abort keeps their validation and side effects identical, apart from the battery and the event name.
