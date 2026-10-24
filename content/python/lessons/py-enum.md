# Enums

Magic values like `state = 2` or `mode = "fast"` are fragile: typos aren't caught, the valid set isn't documented, and `2` means nothing to a reader. An **enumeration** is a type with a fixed set of named, unique members: `Color.RED`, `RobotState.DOCKED`. Python's `enum` module provides `Enum`, `IntEnum`, `StrEnum`, `Flag` and `auto()`. Enums are the backbone of **state machines**, protocol message types, configuration choices and permission bit sets.

## 1. Defining and using an Enum

```python
from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

print(Color.RED)            # Color.RED
print(repr(Color.RED))      # <Color.RED: 1>
print(Color.RED.name, Color.RED.value)   # RED 1
Color(2)                    # Color.GREEN: lookup by VALUE
Color["BLUE"]               # Color.BLUE: lookup by NAME
list(Color)                 # [<Color.RED: 1>, <Color.GREEN: 2>, <Color.BLUE: 3>]: definition order
Color(9)                    # ValueError: 9 is not a valid Color
```

> [!KEY]
> - Members are **singletons**: compare with `is` (or `==`). `Color.RED is Color(1)` is `True`.
> - A plain `Enum` member is **not equal to its value**: `Color.RED == 1` is `False`. That's deliberate type safety, so you can't mix up colors with integers.
> - Members are immutable and hashable, so they make good dict keys.

## 2. `auto()` and duplicate values

```python
from enum import Enum, auto, unique

class State(Enum):
    IDLE = auto()       # 1
    MOVING = auto()     # 2
    DOCKED = auto()     # 3

class Weird(Enum):
    X = 1
    Y = 1               # an ALIAS: Weird.Y is Weird.X, and list(Weird) == [<Weird.X: 1>]

@unique                  # turns aliases into an error
class Strict(Enum):
    A = 1
    B = 1                # ValueError: duplicate values found in <enum 'Strict'>: B -> A
```

When the values don't matter (and usually they don't), use `auto()`.

## 3. Enums with behaviour

Enums are classes, so they can have methods and properties:

```python
class Planet(Enum):
    MERCURY = (3.303e23, 2.4397e6)
    EARTH = (5.976e24, 6.37814e6)

    def __init__(self, mass, radius):     # the value tuple is unpacked into __init__
        self.mass = mass
        self.radius = radius

    @property
    def gravity(self):
        return 6.674e-11 * self.mass / self.radius ** 2

print(round(Planet.EARTH.gravity, 2))     # 9.8
```

## 4. `IntEnum`, `StrEnum`, `Flag`

```python
from enum import IntEnum, StrEnum, Flag, auto

class Priority(IntEnum):        # members ARE ints
    LOW = 1
    HIGH = 2
Priority.LOW == 1, Priority.HIGH > Priority.LOW, Priority.LOW + 1     # True True 2

class Mode(StrEnum):            # members ARE strs (3.11+); auto() gives the lowercase name
    IDLE = auto()
    RUN = auto()
Mode.IDLE == "idle"             # True: convenient for JSON, CLI args and config files

class Perm(Flag):               # bit flags combinable with | & ~
    R = auto()                  # 1
    W = auto()                  # 2
    X = auto()                  # 4
rw = Perm.R | Perm.W
print(rw, Perm.R in rw, Perm.X in rw, rw.value)     # Perm.R|W True False 3
```

| Type | Equal to raw values? | Use for |
|---|---|---|
| `Enum` | no (type-safe) | the default: states, kinds, choices |
| `IntEnum` | yes (it's an int) | interop with C APIs, protocols, sorting by level |
| `StrEnum` | yes (it's a str) | JSON/YAML/CLI values |
| `Flag` / `IntFlag` | combinable bits | permissions, hardware status registers, feature sets |

> [!WARNING]
> `IntEnum` gives up type safety: `Priority.HIGH == Color.GREEN.value` and `Priority.LOW + 5` both work, so an `IntEnum` can silently mix with unrelated integers. Use it only when integer interop is actually required.

## 5. Enums and state machines

```python
from enum import Enum, auto

class Robot(Enum):
    IDLE = auto()
    MOVING = auto()
    CHARGING = auto()
    FAULT = auto()

TRANSITIONS = {                           # (state, event) -> new state
    (Robot.IDLE, "go"): Robot.MOVING,
    (Robot.MOVING, "arrive"): Robot.IDLE,
    (Robot.MOVING, "low_battery"): Robot.CHARGING,
    (Robot.CHARGING, "charged"): Robot.IDLE,
}

def step(state: Robot, event: str) -> Robot:
    if event == "error":
        return Robot.FAULT
    return TRANSITIONS.get((state, event), state)    # ignore invalid events
```

Combined with `match` (the Pattern Matching lesson), enum members can be matched by name with `case Robot.IDLE:`. Type checkers verify that every member is handled (exhaustiveness checking with `assert_never`).

## 6. Exam-ready answers

> [!EXAM]
> **Enumerations.** The `enum` module defines enumerations: classes whose members are a fixed set of named, unique, immutable singleton constants, each with a `name` and a `value`. Members are accessed as attributes (`Color.RED`), by value (`Color(1)`) or by name (`Color["RED"]`), are iterable in definition order, and compare by identity; plain `Enum` members are not equal to their raw values, which provides type safety. `auto()` assigns values automatically, duplicate values create aliases unless `@unique` is applied, and enums can define methods and properties. `IntEnum` and `StrEnum` members are also integers or strings for interoperability, and `Flag` members can be combined with bitwise operators to represent sets of options. Enums replace magic numbers and strings, notably in state machines.

## 7. Cheat sheet

| Need | Code |
|---|---|
| define | `class S(Enum): A = auto(); B = auto()` |
| name / value | `S.A.name`, `S.A.value` |
| from a value / name | `S(1)`, `S["A"]` |
| iterate | `for s in S:` |
| forbid aliases | `@unique` |
| string-valued | `class M(StrEnum)` |
| bit flags | `class P(Flag)`, `P.R \| P.W`, `P.R in perms` |
| transition table | `dict[(State, event)] -> State` |

> [!INTERVIEW]
> **"Why use an Enum instead of string constants for a robot's state?"** Typos become attribute errors at the point of use (`State.MOVNG` fails loudly, while `"movng"` silently never matches). The full set of valid states is documented and iterable. Type checkers can verify that functions receive and return states and that `match` statements are exhaustive. Members are singletons, so comparisons are fast identity checks. When you do need string interop (JSON, ROS parameters), `StrEnum` keeps both benefits.
