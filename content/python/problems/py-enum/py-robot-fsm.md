---
id: py-robot-fsm
title: Robot State Machine with Enums
difficulty: Medium
order: 1
tags: Enum, Flag, state machine, transition table
---
## Statement
Implement the state machine of a delivery robot. Use an `Enum` for the states and a `Flag` for active faults.

States: `IDLE`, `NAVIGATING`, `DELIVERING`, `RETURNING`, `CHARGING`, `ESTOP`.

| From | Event | To |
|---|---|---|
| IDLE | `order` | NAVIGATING |
| NAVIGATING | `arrived` | DELIVERING |
| DELIVERING | `handed_over` | RETURNING |
| RETURNING | `docked` | CHARGING |
| CHARGING | `charged` | IDLE |
| NAVIGATING, RETURNING | `low_battery` | RETURNING |
| *any* except ESTOP | `estop` | ESTOP |
| ESTOP | `reset` | IDLE, but **only if no faults are active**; otherwise stay in ESTOP |

Faults (a `Flag`): `MOTOR`, `LIDAR`, `BATTERY`. The events `fault MOTOR` / `fault LIDAR` / `fault BATTERY` set a fault, and **also** force the state to ESTOP (from any state). `clear NAME` clears that fault.

Any other (state, event) combination is **rejected**: the state doesn't change and the robot counts a rejection.

For each event, print `EVENT: OLD -> NEW`, or `EVENT: rejected in STATE`. For `fault`/`clear`, print the active faults after the event: `faults=LIDAR|MOTOR` (sorted by name), or `faults=none`. At the end print `final STATE rejected=N` and `time_in` with the number of events processed while in each state that was ever entered, in Enum definition order, e.g. `time_in IDLE=2 NAVIGATING=1`. The robot starts in IDLE, and IDLE counts as entered. An event counts toward the state the robot was in **when the event arrived**.

## Starter
```python
import sys
from enum import Enum, Flag, auto

for line in sys.stdin.read().split("\n"):
    if not line.strip():
        continue
    parts = line.split()
```

## Tests
=== sample
order
arrived
handed_over
low_battery
docked
charged
docked
---
order: IDLE -> NAVIGATING
arrived: NAVIGATING -> DELIVERING
handed_over: DELIVERING -> RETURNING
low_battery: RETURNING -> RETURNING
docked: RETURNING -> CHARGING
charged: CHARGING -> IDLE
docked: rejected in IDLE
final IDLE rejected=1
time_in IDLE=2 NAVIGATING=1 DELIVERING=1 RETURNING=2 CHARGING=1
=== hidden
estop
order
reset
order
fault LIDAR
reset
clear LIDAR
reset
---
estop: IDLE -> ESTOP
order: rejected in ESTOP
reset: ESTOP -> IDLE
order: IDLE -> NAVIGATING
fault LIDAR: NAVIGATING -> ESTOP faults=LIDAR
reset: ESTOP -> ESTOP
clear LIDAR: ESTOP -> ESTOP faults=none
reset: ESTOP -> IDLE
final IDLE rejected=1
time_in IDLE=2 NAVIGATING=1 ESTOP=5
=== hidden
fault MOTOR
fault BATTERY
clear MOTOR
reset
clear BATTERY
estop
reset
order
low_battery
low_battery
docked
charged
fly
---
fault MOTOR: IDLE -> ESTOP faults=MOTOR
fault BATTERY: ESTOP -> ESTOP faults=BATTERY|MOTOR
clear MOTOR: ESTOP -> ESTOP faults=BATTERY
reset: ESTOP -> ESTOP
clear BATTERY: ESTOP -> ESTOP faults=none
estop: rejected in ESTOP
reset: ESTOP -> IDLE
order: IDLE -> NAVIGATING
low_battery: NAVIGATING -> RETURNING
low_battery: RETURNING -> RETURNING
docked: RETURNING -> CHARGING
charged: CHARGING -> IDLE
fly: rejected in IDLE
final IDLE rejected=2
time_in IDLE=3 NAVIGATING=1 RETURNING=2 CHARGING=1 ESTOP=6

## Hints
- `class Fault(Flag): MOTOR = auto(); LIDAR = auto(); BATTERY = auto()`. Start with `Fault(0)`. Set with `|=`, clear with `&= ~Fault[name]`, test with `bool(faults)`.
- Store the normal transitions in a dict `{(State, event): State}`, and handle `estop`, `reset`, `fault` and `clear` before looking in it.
- List active faults with `sorted(f.name for f in Fault if f in faults)`.
- Track entered states in a dict that preserves insertion order, or count per state and filter at the end by iterating `State` in order.

## Solution
```python
import sys
from enum import Enum, Flag, auto

class State(Enum):
    IDLE = auto()
    NAVIGATING = auto()
    DELIVERING = auto()
    RETURNING = auto()
    CHARGING = auto()
    ESTOP = auto()

class Fault(Flag):
    MOTOR = auto()
    LIDAR = auto()
    BATTERY = auto()

TRANSITIONS = {
    (State.IDLE, "order"): State.NAVIGATING,
    (State.NAVIGATING, "arrived"): State.DELIVERING,
    (State.DELIVERING, "handed_over"): State.RETURNING,
    (State.RETURNING, "docked"): State.CHARGING,
    (State.CHARGING, "charged"): State.IDLE,
    (State.NAVIGATING, "low_battery"): State.RETURNING,
    (State.RETURNING, "low_battery"): State.RETURNING,
}

def fault_str(f):
    names = sorted(x.name for x in Fault if x in f)
    return "faults=" + ("|".join(names) if names else "none")

state, faults, rejected = State.IDLE, Fault(0), 0
time_in = {s: 0 for s in State}
entered = {State.IDLE}
out = []
for line in sys.stdin.read().split("\n"):
    parts = line.split()
    if not parts:
        continue
    event = parts[0]
    time_in[state] += 1
    old = state
    if event == "fault":
        faults |= Fault[parts[1]]
        state = State.ESTOP
    elif event == "clear":
        faults &= ~Fault[parts[1]]
    elif event == "estop" and state is not State.ESTOP:
        state = State.ESTOP
    elif event == "reset" and state is State.ESTOP:
        if not faults:
            state = State.IDLE
    elif (state, event) in TRANSITIONS:
        state = TRANSITIONS[(state, event)]
    else:
        rejected += 1
        out.append(f"{line.strip()}: rejected in {state.name}")
        continue
    entered.add(state)
    msg = f"{line.strip()}: {old.name} -> {state.name}"
    if event in ("fault", "clear"):
        msg += " " + fault_str(faults)
    out.append(msg)
out.append(f"final {state.name} rejected={rejected}")
out.append("time_in " + " ".join(f"{s.name}={time_in[s]}" for s in State if s in entered))
print("\n".join(out))
```

- **States as an `Enum`:** a typo like `State.IDEL` fails immediately, `State` iterates in definition order for reporting, and members are singletons compared with `is`.
- **Faults as a `Flag`:** several faults can be active at once in one value. `|=` sets, `&= ~` clears, and `bool(faults)` asks "any fault?". That's exactly how hardware status registers work, and how ROS diagnostics are often modelled.
- **Table-driven transitions:** the ordinary behaviour is *data* (`TRANSITIONS`), so adding a state means adding table rows, not nested `if`s. The global events (`estop`, `fault`, guarded `reset`) are handled first, because they apply in many states.
- **Rejecting invalid events explicitly** (instead of silently ignoring them) is a safety property: in real robots, rejected commands get logged and monitored.
