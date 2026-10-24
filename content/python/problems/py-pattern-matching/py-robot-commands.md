---
id: py-robot-commands
title: Robot Command Interpreter with match/case
difficulty: Medium
order: 1
tags: match, case, structural pattern matching, dataclasses, guards
---
## Statement
A robot receives commands as Python literals (one per line, parsed with `ast.literal_eval`): strings, tuples, lists and dicts of various shapes. Write `handle(state, msg) -> str`, which updates `state` (a `Robot` dataclass, provided in the starter) and returns a response. Use **one `match` statement** with these rules, checked in order:

| Message shape | Effect | Response |
|---|---|---|
| `"stop"` or `"halt"` | speed = 0 | `stopped` |
| `("move", dx, dy)` with int/float dx and dy | x += dx, y += dy | `at (X, Y)` |
| `("move", *_)` with any other shape | (nothing) | `bad move` |
| `("turn", angle)` where angle is int/float and -180 ≤ angle ≤ 180 | heading = (heading + angle) % 360 | `heading H` |
| `("turn", _)` | (nothing) | `angle out of range` |
| `{"cmd": "speed", "value": v}` with an int/float v ≥ 0 (extra keys allowed) | speed = v | `speed V` |
| `{"cmd": "speed", **rest}` | (nothing) | `bad speed` |
| `["path", *points]` where points are `(x, y)` tuples | go to the last point (x, y = last); the path length is the sum of segment lengths from the current position, rounded to 2 decimals | `path N points, length L` |
| `["path"]` | (nothing) | `empty path` |
| `Robot(...)` instance (a snapshot object, via a class pattern) | (nothing) | `snapshot speed S` |
| anything else | (nothing) | `unknown: REPR` |

Numbers in responses print with `:g` formatting. `bool` must **not** count as a number (`("move", True, 1)` is a `bad move`).

## Starter
```python
from dataclasses import dataclass
import math

@dataclass
class Robot:
    x: float = 0.0
    y: float = 0.0
    heading: float = 0.0
    speed: float = 0.0

def handle(state, msg):
    return "unknown"
```

## Driver
```python
import ast
import sys

r = Robot()
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    msg = Robot(speed=7.5) if line.strip() == "SNAPSHOT" else ast.literal_eval(line)
    print(handle(r, msg))
print(f"final x={r.x:g} y={r.y:g} heading={r.heading:g} speed={r.speed:g}")
```

## Tests
=== sample
"halt"
("move", 3, 4)
("move", 1)
("move", True, 1)
("turn", 90)
("turn", -270)
("turn", "left")
{"cmd": "speed", "value": 1.5, "source": "remote"}
{"cmd": "speed", "value": -1}
["path", (6, 8), (6, 0)]
["path"]
SNAPSHOT
("dance",)
42
---
stopped
at (3, 4)
bad move
bad move
heading 90
angle out of range
angle out of range
speed 1.5
bad speed
path 2 points, length 13
empty path
snapshot speed 7.5
unknown: ('dance',)
unknown: 42
final x=6 y=0 heading=90 speed=1.5
=== hidden
"stop"
("turn", 180)
("turn", 180)
("turn", -180)
("move", 0.5, -0.25)
{"cmd": "speed"}
{"cmd": "speed", "value": True}
{"cmd": "speed", "value": 0}
["path", (1, 1)]
["path", (1, 1), "x"]
("move", 1, 2, 3)
[]
{"cmd": "jump"}
"STOP"
---
stopped
heading 180
heading 0
heading 180
at (0.5, -0.25)
bad speed
bad speed
speed 0
path 1 points, length 1.35
unknown: ['path', (1, 1), 'x']
bad move
unknown: []
unknown: {'cmd': 'jump'}
unknown: 'STOP'
final x=1 y=1 heading=180 speed=0

## Hints
- Number patterns: `case ("move", int() | float() as dx, int() | float() as dy) if not isinstance(dx, bool) and not isinstance(dy, bool):`. Remember that `bool` is a subclass of `int`.
- Order matters: put the specific `("move", dx, dy)` case **before** the catch-all `("move", *_)`.
- `["path", *points]` binds `points` to a list. Check the shape in a guard, e.g. `all(isinstance(p, tuple) and len(p) == 2 for p in points)`. Note that `["path"]` would also match `["path", *points]` with an empty list, so put the empty-path case first.
- A class pattern `case Robot(speed=s):` matches dataclass instances by attribute.
- `math.dist(p, q)` gives the Euclidean distance between two points.

## Solution
```python
from dataclasses import dataclass
import math

@dataclass
class Robot:
    x: float = 0.0
    y: float = 0.0
    heading: float = 0.0
    speed: float = 0.0

def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)

def handle(state, msg):
    match msg:
        case "stop" | "halt":
            state.speed = 0
            return "stopped"
        case ("move", dx, dy) if _num(dx) and _num(dy):
            state.x += dx
            state.y += dy
            return f"at ({state.x:g}, {state.y:g})"
        case ("move", *_):
            return "bad move"
        case ("turn", angle) if _num(angle) and -180 <= angle <= 180:
            state.heading = (state.heading + angle) % 360
            return f"heading {state.heading:g}"
        case ("turn", _):
            return "angle out of range"
        case {"cmd": "speed", "value": v} if _num(v) and v >= 0:
            state.speed = v
            return f"speed {v:g}"
        case {"cmd": "speed", **rest}:
            return "bad speed"
        case ["path"]:
            return "empty path"
        case ["path", *points] if all(isinstance(p, tuple) and len(p) == 2 and all(map(_num, p)) for p in points):
            pos, length = (state.x, state.y), 0.0
            for p in points:
                length += math.dist(pos, p)
                pos = p
            state.x, state.y = pos
            return f"path {len(points)} points, length {round(length, 2):g}"
        case Robot(speed=s):
            return f"snapshot speed {s:g}"
        case _:
            return f"unknown: {msg!r}"
```

Pattern matching expresses each message format **as its shape**: tuple and list patterns check length and destructure in one step, `*rest` captures variable tails, mapping patterns check required keys and ignore extras, class patterns match dataclass instances by attribute, and guards (`if ...`) add value conditions. Two subtleties are tested:
- **Tuple patterns also match lists, and vice versa** (both are sequence patterns), so `("move", 1, 2)` and `["move", 1, 2]` behave the same. Strings never match sequence patterns, so `"stop"` can't be confused with a sequence.
- **Case order is semantics:** the specific `("move", dx, dy)` must come before the catch-all `("move", *_)`, and `["path"]` before `["path", *points]`.
