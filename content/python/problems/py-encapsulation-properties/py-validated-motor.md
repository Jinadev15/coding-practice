---
id: py-validated-motor
title: Validated Servo with Properties
difficulty: Medium
order: 1
tags: properties, validation, invariants
---
## Statement
Write a class `Servo` that protects its invariants with **properties**:

- `Servo(name, min_angle=0, max_angle=180)`; requires `min_angle < max_angle`, otherwise `ValueError("bad range")`
- `angle` property (starts at `min_angle`): setting it outside `[min_angle, max_angle]` raises `ValueError("angle out of range")`
- `name` is **read-only** after creation (no setter)
- `radians` is a **computed** read-only property: `angle` in radians, rounded to 4 decimals
- `moves` is read-only: the number of successful angle changes (setting the same angle again doesn't count)

## Starter
```python
import math

class Servo:
    def __init__(self, name, min_angle=0, max_angle=180):
        pass
```

## Driver
```python
s = None
for line in iter(input, "END"):
    cmd, *a = line.split()
    try:
        if cmd == "new":
            s = Servo(a[0], *map(int, a[1:]))
        elif cmd == "set":
            s.angle = float(a[0])
        elif cmd == "rename":
            s.name = a[0]
        print(f"{s.name} angle={s.angle:g} rad={s.radians} moves={s.moves}")
    except (ValueError, AttributeError) as e:
        print(type(e).__name__)
```

## Tests
=== sample
new pan
set 90
set 90
set 200
rename tilt
set 45
END
---
pan angle=0 rad=0.0 moves=0
pan angle=90 rad=1.5708 moves=1
pan angle=90 rad=1.5708 moves=1
ValueError
AttributeError
pan angle=45 rad=0.7854 moves=2
=== hidden
new grip 10 20
set 9.99
set 20
new bad 50 50
END
---
grip angle=10 rad=0.1745 moves=0
ValueError
grip angle=20 rad=0.3491 moves=1
ValueError

## Hints
- Store real values in `_name`, `_angle`, `_moves`, `_min`, `_max`.
- `@property def name(self): return self._name` with no setter makes assigning raise `AttributeError`.
- In the setter, validate, and increase `_moves` only if the value actually changed.

## Solution
Every piece of state is stored privately and exposed through properties: validation lives in exactly one place, and read-only values simply have no setter.

```python
import math

class Servo:
    def __init__(self, name, min_angle=0, max_angle=180):
        if min_angle >= max_angle:
            raise ValueError("bad range")
        self._name = name
        self._min, self._max = min_angle, max_angle
        self._angle = min_angle
        self._moves = 0

    @property
    def name(self):
        return self._name

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        if not self._min <= value <= self._max:
            raise ValueError("angle out of range")
        if value != self._angle:
            self._angle = value
            self._moves += 1

    @property
    def radians(self):
        return round(math.radians(self._angle), 4)

    @property
    def moves(self):
        return self._moves
```

When `new bad 50 50` fails, `s` still refers to the previous servo, because the failed constructor never rebinds the name. Real servo drivers (ROS 2 controllers, Arduino libraries) enforce joint limits exactly like this, because sending an out-of-range angle can damage hardware.
