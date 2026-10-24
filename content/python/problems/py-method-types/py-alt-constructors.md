---
id: py-alt-constructors
title: Alternative Constructors
difficulty: Medium
order: 1
tags: classmethod, staticmethod, inheritance
---
## Statement
Write a class `Vector2` (2D vector) with:

- `__init__(self, x, y)`
- `__repr__` returning `Vector2(x, y)`, numbers formatted with `:g` (so `3.0` shows as `3`)
- classmethods (alternative constructors), each returning `cls(...)`:
  - `from_string(s)` parses `"x,y"`
  - `from_polar(r, deg)` with angle in degrees (round each component to 6 decimals)
  - `zero()`
- staticmethod `parse_ok(s)` returns `True` if `s` is two comma-separated floats
- instance method `length()`

Then write a subclass `Velocity(Vector2)` that adds `speed()` returning the length. The constructors must produce `Velocity` objects when called on `Velocity`, **without** being redefined.

## Starter
```python
import math

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Velocity(Vector2):
    pass
```

## Driver
```python
classes = {"Vector2": Vector2, "Velocity": Velocity}
for line in iter(input, "END"):
    cls_name, method, *args = line.split()
    cls = classes[cls_name]
    if method == "parse_ok":
        print(cls.parse_ok(args[0]))
        continue
    obj = getattr(cls, method)(*([args[0]] if method == "from_string" else map(float, args)))
    extra = f" speed={obj.speed():g}" if isinstance(obj, Velocity) else ""
    print(type(obj).__name__, obj, f"len={obj.length():g}" + extra)
```

## Tests
=== sample
Vector2 from_string 3,4
Velocity from_polar 2 90
Vector2 zero
Vector2 parse_ok 1.5,x
END
---
Vector2 Vector2(3, 4) len=5
Velocity Vector2(0, 2) len=2 speed=2
Vector2 Vector2(0, 0) len=0
False
=== hidden
Velocity from_string -6,8
Velocity zero
Vector2 parse_ok 1,2
Vector2 parse_ok 1,2,3
Vector2 from_polar 1 45
END
---
Velocity Vector2(-6, 8) len=10 speed=10
Velocity Vector2(0, 0) len=0 speed=0
True
False
Vector2 Vector2(0.707107, 0.707107) len=1

## Hints
- `return cls(float(x), float(y))`. Using `Vector2(...)` here would break the subclass.
- `parse_ok`: split on commas, require exactly 2 parts, try `float()` on each, and catch `ValueError`.
- `__repr__` deliberately uses the name `Vector2`, matching the expected output for both classes.

## Solution
```python
import math

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vector2({self.x:g}, {self.y:g})"

    @classmethod
    def from_string(cls, s):
        x, y = s.split(",")
        return cls(float(x), float(y))

    @classmethod
    def from_polar(cls, r, deg):
        a = math.radians(deg)
        return cls(round(r * math.cos(a), 6), round(r * math.sin(a), 6))

    @classmethod
    def zero(cls):
        return cls(0.0, 0.0)

    @staticmethod
    def parse_ok(s):
        parts = s.split(",")
        if len(parts) != 2:
            return False
        try:
            [float(p) for p in parts]
        except ValueError:
            return False
        return True

    def length(self):
        return math.hypot(self.x, self.y)


class Velocity(Vector2):
    def speed(self):
        return self.length()
```

`Velocity.from_polar(2, 90)` returns a `Velocity` because `cls` is `Velocity`. `round(..., 6)` turns `cos(90°) ≈ 1.2e-16` into `0`. Floating-point noise like that is why robotics code rounds or compares with a tolerance.
