# Case Study: Robot Controller

This case study designs the mission layer of a warehouse robot in Python:
- a **mission executor** that runs a queue of tasks (move, pick, place, charge) against a **world model**;
- tasks as **command objects** with preconditions and effects;
- **events** for observers (UI, logging, fleet manager);
- a simple **state machine** for robot modes;
- **injected time and hardware**, so everything runs deterministically in tests.

It combines the module's principles into a structure similar to real fleet software.

## 1. Requirements

- The robot has a position on a grid (cell coordinates), a battery fraction, an optional carried item, and a mode: `IDLE`, `EXECUTING`, `CHARGING`, `FAULT`.
- Tasks:
  - `MoveTo(cell)` costs Manhattan distance × 0.01 battery and takes 1 s per cell;
  - `Pick(item)` requires an empty gripper, with the item at the robot's cell;
  - `Place(cell)` requires carrying an item, at the robot's cell;
  - `Charge(target)` raises the battery to the target at 0.05 per second, and must happen at a charger cell.
- Before each task, check its **preconditions**. A failure stops the mission with a reason, and the robot returns to `IDLE` (or `FAULT` for hardware errors).
- If the battery would drop below 0.15 during a `MoveTo`, insert a detour to the nearest charger, plus a `Charge(0.9)`, automatically. That's a planning rule.
- Emit events: `task_started`, `task_done`, `mission_failed` and `mission_done`, with timestamps from the injected clock.

## 2. Design

```mermaid
classDiagram
    class Task { <<abstract>> +check(state, world) str|None; +apply(state, world) float }
    class MoveTo
    class Pick
    class Place
    class Charge
    Task <|-- MoveTo
    Task <|-- Pick
    Task <|-- Place
    Task <|-- Charge
    class MissionExecutor { +run(tasks) Report; +subscribe(event, fn) }
    class RobotState { cell; battery; carrying; mode }
    class World { items; chargers; shelves }
    MissionExecutor --> Task
    MissionExecutor --> RobotState
    MissionExecutor --> World
```

- **Command pattern**: each task knows how to check its preconditions (`check` returns `None` or a reason) and how to apply its effects (`apply` returns the elapsed seconds). The executor doesn't care which task it's running.
- **The world model is separate from the robot state**, because items and chargers belong to the warehouse.
- **Observer**: `subscribe(event_name, callback)`. The executor publishes, and the UI, logger and fleet manager listen without coupling.
- **Time** comes from a clock that the executor advances by the seconds each task reports. A wall clock in production, simulated in tests.

## 3. The executor loop

```python
def run(self, tasks: list[Task]) -> Report:
    queue = deque(self._plan(tasks))                 # planning step: inserts charging detours
    self.state.mode = Mode.EXECUTING
    while queue:
        task = queue.popleft()
        reason = task.check(self.state, self.world)
        if reason:
            self.state.mode = Mode.IDLE
            self._emit("mission_failed", task=task, reason=reason)
            return Report(ok=False, reason=reason)
        self._emit("task_started", task=task)
        self.clock.advance(task.apply(self.state, self.world))
        self._emit("task_done", task=task)
    self.state.mode = Mode.IDLE
    self._emit("mission_done")
    return Report(ok=True)
```

**Planning** before execution is a separate, testable step. It simulates battery use along the task list and inserts `MoveTo(charger)` plus `Charge(0.9)` before any move that would breach the reserve, which keeps the execution logic simple.

## 4. Testing

Every scenario is deterministic:
- a pick-and-place mission succeeds, and the event log equals the expected sequence;
- picking with a full gripper fails with a precise reason;
- a long route triggers exactly one detour, and the battery never drops below the reserve;
- subscribers that raise exceptions don't break the executor (errors are isolated).

> [!EXAM]
> **Why model robot tasks as command objects with separate `check` and `apply` methods?**
> Command objects make each task a self-contained unit that the executor can queue, plan, log, retry or reorder without knowing its type, which is open/closed: new task types don't change the executor. Separating `check` (preconditions, which inspect state without changing it) from `apply` (effects) lets the executor validate a task before committing to it, report precise failure reasons, and lets a planner simulate a mission ahead of time, such as inserting charging detours, using the same model. Injected time and world state keep the whole mission deterministic and testable.

## Worked example: commands as objects

The core idea of this case study is that **each command is an object** with an `execute(robot)` method, and the controller just runs them in order. Here is a stripped-down version you can run:

```python
from dataclasses import dataclass
from typing import Protocol

@dataclass
class Robot:
    x: int = 0
    y: int = 0
    heading: str = "N"

class Command(Protocol):
    def execute(self, r: Robot) -> None: ...

TURN_LEFT = {"N": "W", "W": "S", "S": "E", "E": "N"}
STEP = {"N": (0, 1), "E": (1, 0), "S": (0, -1), "W": (-1, 0)}

@dataclass
class Forward:
    n: int
    def execute(self, r: Robot) -> None:
        dx, dy = STEP[r.heading]
        r.x += dx * self.n; r.y += dy * self.n

class Left:
    def execute(self, r: Robot) -> None:
        r.heading = TURN_LEFT[r.heading]

def run(program: list[Command]) -> Robot:
    r = Robot()
    for cmd in program:
        cmd.execute(r)
    return r

print(run([Forward(2), Left(), Forward(3)]))
```

```output
Robot(x=-3, y=2, heading='W')
```

Why this design?

- New commands (`Wait`, `Scan`) are new classes. The executor never changes.
- A program is **data**: you can log it, validate it before running it, or replay it.
- Tests can check one command at a time against a fresh `Robot`.

## Common mistakes

- **A giant `if cmd == "forward" ... elif ...` loop.** This is the design that commands as objects replace.
- **Letting commands reach into globals.** Pass everything they need (robot, map, clock) explicitly so tests can supply fakes.
- **Mixing parsing and executing.** Parse the text into command objects first, then run them. Syntax errors are found before the robot moves.

## Check your understanding

1. How would you add "undo"?
2. Where should a collision check live?

<details><summary>Answers</summary>

1. Give each command an `undo(robot)` method (or have `execute` return an inverse command) and keep a history stack.
2. In a map or world object that commands consult (`world.is_free(x, y)`), passed in alongside the robot, not hard-coded in every command.

</details>
