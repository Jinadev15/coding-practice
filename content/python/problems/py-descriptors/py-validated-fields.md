---
id: py-validated-fields
title: Reusable Validated Fields with Descriptors
difficulty: Hard
order: 1
tags: descriptors, __set_name__, data vs non-data descriptors, cached property
---
## Statement
Build a small field-validation library with **descriptors**, like the core of an ORM or pydantic:

```python
class Field:                       # base data descriptor
    # __set_name__ records the attribute name.
    # __get__: on the class, return the descriptor itself; on an instance, return the stored value,
    #          or raise AttributeError(f"{name} is not set") if it was never assigned.
    # __set__: call self.validate(name, value), which returns the (possibly converted) value to store.

class Typed(Field):      # Typed(int): value must be an instance of the type (bool is NOT accepted for int)
class Range(Typed):      # Range(lo, hi): a number with lo <= value <= hi (int or float; ints accepted for float fields)
class Choice(Field):     # Choice("idle", "run"): value must be one of the options
class Lazy:              # a NON-data descriptor decorator: computes once per instance, then caches in the instance __dict__
```

Error messages must be exactly:
- `TypeError: NAME must be TYPENAME` (e.g. `speed must be float`)
- `ValueError: NAME must be in [LO, HI]`
- `ValueError: NAME must be one of ('idle', 'run')` (the repr of the options tuple)

Values are stored **per instance** (in the instance's `__dict__` under the field's own name). The driver defines a `Robot` class with these fields and checks per-instance isolation, class-level access, and that `Lazy` runs its function only once per instance.

## Starter
```python
class Field:
    pass

class Typed(Field):
    def __init__(self, typ):
        self.typ = typ

class Range(Typed):
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi

class Choice(Field):
    def __init__(self, *options):
        self.options = options

class Lazy:
    def __init__(self, func):
        self.func = func
```

## Driver
```python
import re
import sys

calls = []

class Robot:
    name = Typed(str)
    wheels = Typed(int)
    speed = Range(0.0, 3.5)
    mode = Choice("idle", "run", "dock")

    def __init__(self, name, wheels):
        self.name = name
        self.wheels = wheels

    @Lazy
    def serial(self):
        calls.append(self.name)
        return f"{self.name.upper()}-{self.wheels:02d}"

SHOW_MESSAGES = True
ASSIGN = re.compile(r"^\s*([A-Za-z_][\w.]*)\s*=(?!=)\s*(.+)$")
env = dict(globals())
for line in sys.stdin.read().splitlines():
    if not line.strip() or line.lstrip().startswith("#"):
        continue
    m = ASSIGN.match(line)
    try:
        if m and "." not in m.group(1):
            env[m.group(1)] = eval(m.group(2), env)
        elif m:
            exec(line.strip(), env)
        else:
            print(line.strip(), "->", repr(eval(line, env)))
    except Exception as e:
        print(line.strip(), "->", type(e).__name__ + (f": {e}" if SHOW_MESSAGES else ""))
```

## Tests
=== sample
r = Robot("rover", 4)
r.name
r.speed
r.speed = 2
r.speed
r.speed = 9
r.speed = "fast"
r.mode = "run"
r.mode
r.mode = "fly"
r.wheels = True
r.wheels = 6
r.wheels
type(Robot.speed).__name__
Robot.speed.name
r.serial
r.serial
calls
"serial" in r.__dict__
---
r.name -> 'rover'
r.speed -> AttributeError: speed is not set
r.speed -> 2.0
r.speed = 9 -> ValueError: speed must be in [0.0, 3.5]
r.speed = "fast" -> TypeError: speed must be float
r.mode -> 'run'
r.mode = "fly" -> ValueError: mode must be one of ('idle', 'run', 'dock')
r.wheels = True -> TypeError: wheels must be int
r.wheels -> 6
type(Robot.speed).__name__ -> 'Range'
Robot.speed.name -> 'speed'
r.serial -> 'ROVER-06'
r.serial -> 'ROVER-06'
calls -> ['rover']
"serial" in r.__dict__ -> True
=== hidden
a = Robot("a", 2)
b = Robot("b", 3)
a.speed = 1.5
b.speed = 3.5
(a.speed, b.speed)
a.name = 42
b.speed = -0.0001
a.serial
b.serial
a.serial
calls
a.__dict__.pop("serial")
a.serial
calls
Robot("x", 1.5)
Robot("y", 2).mode
sorted(k for k in vars(a) if not k.startswith("_"))
---
(a.speed, b.speed) -> (1.5, 3.5)
a.name = 42 -> TypeError: name must be str
b.speed = -0.0001 -> ValueError: speed must be in [0.0, 3.5]
a.serial -> 'A-02'
b.serial -> 'B-03'
a.serial -> 'A-02'
calls -> ['a', 'b']
a.__dict__.pop("serial") -> 'A-02'
a.serial -> 'A-02'
calls -> ['a', 'b', 'a']
Robot("x", 1.5) -> TypeError: wheels must be int
Robot("y", 2).mode -> AttributeError: mode is not set
sorted(k for k in vars(a) if not k.startswith("_")) -> ['name', 'serial', 'speed', 'wheels']

## Hints
- `__set_name__(self, owner, name)` stores `self.name = name`. Then `obj.__dict__[self.name]` is per-instance storage that **can't** shadow the descriptor, because a data descriptor (one with `__set__`) takes precedence over the instance dict.
- In `__get__`: `if obj is None: return self`, then `try: return obj.__dict__[self.name] except KeyError: raise AttributeError(...)`.
- `Typed.validate`: `isinstance(value, bool) and self.typ is not bool` is the special case. For float fields, accept ints too (and convert them to float).
- `Range.__init__` should call `super().__init__(float)` (or the type of `lo`), so the type check runs first and the range check second.
- `Lazy` has **only** `__get__`, so it's a non-data descriptor: after you store the result in `obj.__dict__[name]`, normal lookup finds the instance value and never calls `Lazy.__get__` again.

## Solution
```python
class Field:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        try:
            return obj.__dict__[self.name]
        except KeyError:
            raise AttributeError(f"{self.name} is not set") from None

    def __set__(self, obj, value):
        obj.__dict__[self.name] = self.validate(self.name, value)

    def validate(self, name, value):
        return value


class Typed(Field):
    def __init__(self, typ):
        self.typ = typ

    def validate(self, name, value):
        if self.typ is float and isinstance(value, int) and not isinstance(value, bool):
            value = float(value)
        if not isinstance(value, self.typ) or (isinstance(value, bool) and self.typ is not bool):
            raise TypeError(f"{name} must be {self.typ.__name__}")
        return value


class Range(Typed):
    def __init__(self, lo, hi):
        super().__init__(float if isinstance(lo, float) or isinstance(hi, float) else int)
        self.lo, self.hi = lo, hi

    def validate(self, name, value):
        value = super().validate(name, value)          # type check first
        if not self.lo <= value <= self.hi:
            raise ValueError(f"{name} must be in [{self.lo}, {self.hi}]")
        return value


class Choice(Field):
    def __init__(self, *options):
        self.options = options

    def validate(self, name, value):
        if value not in self.options:
            raise ValueError(f"{name} must be one of {self.options!r}")
        return value


class Lazy:
    def __init__(self, func):
        self.func = func
        self.__doc__ = func.__doc__

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        value = self.func(obj)
        obj.__dict__[self.name] = value                # shadows this non-data descriptor from now on
        return value
```

**The mechanics this exercise makes concrete:**
- **One descriptor per field, shared by all instances.** The values live in each instance's `__dict__`, so `a.speed` and `b.speed` are independent.
- **A data descriptor beats the instance dict.** Even though the value is stored in `obj.__dict__["speed"]`, every access still goes through `Field.__get__`/`__set__`, so validation can't be bypassed by normal assignment.
- **A non-data descriptor loses to the instance dict.** `Lazy` caches by writing the instance attribute, after which Python never calls it again (the driver shows `calls` growing only once per robot). That's exactly `functools.cached_property`.
- **The Template Method pattern:** `Field.__set__` is fixed and subclasses override only `validate`, chaining with `super()` (Range = type check + bounds).
