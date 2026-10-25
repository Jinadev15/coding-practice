---
id: py-declarative-models
title: Declarative Models with Descriptors
difficulty: Hard
order: 1
tags: descriptors, __set_name__, __init_subclass__, data model, validation, metaprogramming
time_limit: 5
---
## Statement
Build a miniature pydantic or Django-model layer from Python's own machinery: **descriptors** for validated fields, and `__init_subclass__` to collect them into a schema.

**Fields** are data descriptors. Each takes an optional `default=` (keyword-only), and a field without a default is **required**.

| Field | Accepts | Errors (message format) |
|---|---|---|
| `Integer(min=None, max=None)` | `int`, but not `bool` | `TypeError("<name>: expected int")`, `ValueError("<name>: must be >= <min>")`, `ValueError("<name>: must be <= <max>")` |
| `Float(min=None, max=None)` | `int` or `float` (not `bool`), stored as `float` | `TypeError("<name>: expected float")`, then the same range messages |
| `String(max_len=None, pattern=None)` | `str` (`pattern` must `re.fullmatch`) | `TypeError("<name>: expected str")`, `ValueError("<name>: longer than <max_len>")`, `ValueError("<name>: does not match pattern")` |
| `Choice(*options)` | a value equal to one of `options` | `ValueError("<name>: must be one of <options tuple repr>")` |

Validation runs on **every assignment**, including in `__init__`, and a failed assignment leaves the old value in place. `<name>` is the attribute name (from `__set_name__`). Accessing a field on the class returns the descriptor itself.

**`class Model`**: subclasses get these automatically:
- `cls.fields`: a tuple of field names in definition order, **inherited fields first**. A subclass may redefine a parent's field, and it keeps the parent's position.
- `__init__(**kwargs)`: keyword-only. An unknown name raises `TypeError("unknown field '<n>'")`, checked in sorted order first. A missing required field raises `TypeError("missing field '<n>'")`, in field order. Defaults are assigned through validation.
- `__repr__`: `ClassName(a=1, b='x')` in field order, using `repr` of the values.
- `__eq__`: same class and equal field values. Also `to_dict()`, which returns a dict in field order.

## Starter
```python
import re


class Field:
    def __init__(self, *, default=None):
        self.default = default


class Integer(Field):
    def __init__(self, min=None, max=None, **kw):
        super().__init__(**kw)


class Float(Field):
    def __init__(self, min=None, max=None, **kw):
        super().__init__(**kw)


class String(Field):
    def __init__(self, max_len=None, pattern=None, **kw):
        super().__init__(**kw)


class Choice(Field):
    def __init__(self, *options, **kw):
        super().__init__(**kw)


class Model:
    fields = ()

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
```

## Driver
```python
import sys

def attempt(label, fn):
    try:
        print(f"{label}: {fn()!r}")
    except (TypeError, ValueError) as e:
        print(f"{label}: {type(e).__name__}: {e}")

class Robot(Model):
    name = String(max_len=12, pattern=r"[a-z][a-z0-9-]*")
    battery = Float(min=0, max=1, default=1.0)
    wheels = Integer(min=2, max=8, default=4)
    mode = Choice("idle", "auto", "manual", default="idle")

class Drone(Robot):
    wheels = Integer(min=0, max=0, default=0)
    altitude = Float(min=0, default=0.0)
    rotors = Integer(min=3)

for cmd in sys.stdin.read().split():
    if cmd == "basic":
        print(Robot.fields, Drone.fields)
        print(type(Robot.battery).__name__, Robot.name is Robot.__dict__["name"])
        r = Robot(name="rover-1")
        print(r, r.to_dict())
        r.battery = 0.5; r.mode = "auto"; print(r)
        attempt("int as float", lambda: setattr(r, "battery", 1) or r.battery)
        attempt("battery range", lambda: setattr(r, "battery", 1.5))
        print("unchanged", r.battery)
        attempt("battery bool", lambda: setattr(r, "battery", True))
        attempt("wheels type", lambda: setattr(r, "wheels", 4.0))
        attempt("wheels bool", lambda: setattr(r, "wheels", True))
        attempt("wheels low", lambda: setattr(r, "wheels", 1))
        attempt("wheels high", lambda: setattr(r, "wheels", 9))
        attempt("mode", lambda: setattr(r, "mode", "turbo"))
        attempt("name type", lambda: setattr(r, "name", 7))
        attempt("name long", lambda: setattr(r, "name", "a" * 13))
        attempt("name pattern", lambda: setattr(r, "name", "Rover"))
        print(r == Robot(name="rover-1", battery=1, mode="auto"), r == Robot(name="rover-2"), r == "rover")
    elif cmd == "init":
        attempt("missing", lambda: Robot())
        attempt("unknown", lambda: Robot(name="x", zeta=1, alpha=2))
        attempt("bad default use", lambda: Robot(name="x", wheels=3).to_dict())
        attempt("init validation", lambda: Robot(name="x", battery=-0.1))
        try:
            Robot("x"); print("positional: accepted")
        except TypeError:
            print("positional: TypeError")
        d = Drone(name="quad", rotors=4)
        print(d, d.to_dict())
        attempt("drone wheels", lambda: setattr(d, "wheels", 2))
        attempt("drone missing", lambda: Drone(name="hex"))
        attempt("drone altitude", lambda: Drone(name="hex", rotors=6, altitude=-1))
        a, b = Robot(name="a"), Robot(name="b")
        a.battery = 0.25
        print(a.battery, b.battery, "instances independent")
        class Empty(Model):
            pass
        print(Empty.fields, Empty(), Empty() == Empty())
        attempt("empty unknown", lambda: Empty(x=1))
    elif cmd == "load":
        total = 0.0; errors = 0
        for i in range(30000):
            try:
                r = Robot(name=f"r{i % 500}", battery=(i % 130) / 100, wheels=2 + i % 9, mode=("idle", "auto", "manual", "x")[i % 4])
                total += r.battery * r.wheels
            except ValueError:
                errors += 1
        print(f"{total:.2f} {errors}")
```

## Tests
=== sample
basic
---
('name', 'battery', 'wheels', 'mode') ('name', 'battery', 'wheels', 'mode', 'altitude', 'rotors')
Float True
Robot(name='rover-1', battery=1.0, wheels=4, mode='idle') {'name': 'rover-1', 'battery': 1.0, 'wheels': 4, 'mode': 'idle'}
Robot(name='rover-1', battery=0.5, wheels=4, mode='auto')
int as float: 1.0
battery range: ValueError: battery: must be <= 1
unchanged 1.0
battery bool: TypeError: battery: expected float
wheels type: TypeError: wheels: expected int
wheels bool: TypeError: wheels: expected int
wheels low: ValueError: wheels: must be >= 2
wheels high: ValueError: wheels: must be <= 8
mode: ValueError: mode: must be one of ('idle', 'auto', 'manual')
name type: TypeError: name: expected str
name long: ValueError: name: longer than 12
name pattern: ValueError: name: does not match pattern
True False False
=== hidden
init
---
missing: TypeError: missing field 'name'
unknown: TypeError: unknown field 'alpha'
bad default use: {'name': 'x', 'battery': 1.0, 'wheels': 3, 'mode': 'idle'}
init validation: ValueError: battery: must be >= 0
positional: TypeError
Drone(name='quad', battery=1.0, wheels=0, mode='idle', altitude=0.0, rotors=4) {'name': 'quad', 'battery': 1.0, 'wheels': 0, 'mode': 'idle', 'altitude': 0.0, 'rotors': 4}
drone wheels: ValueError: wheels: must be <= 0
drone missing: TypeError: missing field 'rotors'
drone altitude: ValueError: altitude: must be >= 0
0.25 1.0 instances independent
() Empty() True
empty unknown: TypeError: unknown field 'x'
=== hidden
load
---
34127.20 16346

## Hints
- `Field.__set_name__(self, owner, name)` stores `self.name = name`. Store values in `obj.__dict__[name]`. A data descriptor on the class takes priority over the instance dict, so reading still goes through `__get__`.
- Put validation in a `validate(self, value) -> value` method that subclasses override, and call it in `__set__` before storing.
- `Model.__init_subclass__`: start from the parent's `fields`, then append the new `Field`s from `cls.__dict__` (dicts preserve definition order) that aren't already listed.
- Use a private sentinel (`MISSING = object()`) for "no default", because `None` might be a legitimate default.

## Solution
```python
import re

MISSING = object()


class Field:
    def __init__(self, *, default=MISSING):
        self.default = default
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self                                   # class access: the descriptor itself
        try:
            return obj.__dict__[self.name]
        except KeyError:
            raise AttributeError(self.name) from None

    def __set__(self, obj, value):
        obj.__dict__[self.name] = self.validate(value)    # validate first: failure keeps the old value

    def validate(self, value):
        return value


class _Ranged(Field):
    def __init__(self, min=None, max=None, **kw):
        super().__init__(**kw)
        self.min, self.max = min, max

    def check_range(self, value):
        if self.min is not None and value < self.min:
            raise ValueError(f"{self.name}: must be >= {self.min}")
        if self.max is not None and value > self.max:
            raise ValueError(f"{self.name}: must be <= {self.max}")
        return value


class Integer(_Ranged):
    def validate(self, value):
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"{self.name}: expected int")
        return self.check_range(value)


class Float(_Ranged):
    def validate(self, value):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError(f"{self.name}: expected float")
        return self.check_range(float(value))


class String(Field):
    def __init__(self, max_len=None, pattern=None, **kw):
        super().__init__(**kw)
        self.max_len = max_len
        self.pattern = re.compile(pattern) if pattern else None

    def validate(self, value):
        if not isinstance(value, str):
            raise TypeError(f"{self.name}: expected str")
        if self.max_len is not None and len(value) > self.max_len:
            raise ValueError(f"{self.name}: longer than {self.max_len}")
        if self.pattern and not self.pattern.fullmatch(value):
            raise ValueError(f"{self.name}: does not match pattern")
        return value


class Choice(Field):
    def __init__(self, *options, **kw):
        super().__init__(**kw)
        self.options = options

    def validate(self, value):
        if value not in self.options:
            raise ValueError(f"{self.name}: must be one of {self.options!r}")
        return value


class Model:
    fields = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        names = list(cls.fields)                          # inherited, in parent order
        for name, value in cls.__dict__.items():
            if isinstance(value, Field) and name not in names:
                names.append(name)
        cls.fields = tuple(names)

    def __init__(self, **kwargs):
        cls = type(self)
        for key in sorted(kwargs):
            if key not in cls.fields:
                raise TypeError(f"unknown field '{key}'")
        for name in cls.fields:
            field = getattr(cls, name)
            if name in kwargs:
                setattr(self, name, kwargs[name])
            elif field.default is not MISSING:
                setattr(self, name, field.default)
            else:
                raise TypeError(f"missing field '{name}'")

    def to_dict(self):
        return {name: getattr(self, name) for name in self.fields}

    def __repr__(self):
        body = ", ".join(f"{n}={getattr(self, n)!r}" for n in self.fields)
        return f"{type(self).__name__}({body})"

    def __eq__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        return self.to_dict() == other.to_dict()

    __hash__ = None                                       # mutable value objects: unhashable
```

- **Data descriptors win** over instance attributes in Python's lookup order. So even though the values live in `obj.__dict__[name]`, every read and write goes through the field, and validation can't be bypassed by normal assignment.
- **`__set_name__`** tells each descriptor its own attribute name at class creation, so `name = String()` needs no repeated `"name"` string. That's how Django model fields and pydantic know their names.
- **`__init_subclass__`** builds the schema once per class, inheriting the parent's field order and letting subclasses override a field in place (`Drone.wheels`). A metaclass would also work, but this hook is simpler.
- **Validate, then store**: a rejected value never replaces a good one, so objects can't be left in an invalid state.
- **`__eq__` returns `NotImplemented`** for foreign types, so Python can try the reflected operation. Setting `__hash__ = None` makes the mutable models explicitly unhashable, which is what defining `__eq__` implies anyway.
