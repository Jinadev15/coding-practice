# Instance, Class and Static Methods

A method defined in a class can relate to **one object**, to **the class as a whole**, or to **neither**: just a helper that belongs to the class conceptually. Python expresses these as instance methods, `@classmethod` and `@staticmethod`. The most important practical use is the **alternative constructor** pattern (`datetime.fromisoformat`, `dict.fromkeys`, `Path.cwd`), which you'll use constantly when designing classes.

## 1. The three kinds side by side

```python
class Temperature:
    UNITS = ("C", "F")

    def __init__(self, celsius):
        self.celsius = celsius

    # 1. instance method: works on ONE object, receives it as self
    def to_fahrenheit(self):
        return self.celsius * 9 / 5 + 32

    # 2. class method: works on the CLASS, receives it as cls
    @classmethod
    def from_fahrenheit(cls, f):
        return cls((f - 32) * 5 / 9)        # build and return a new instance

    # 3. static method: receives neither; a plain function namespaced in the class
    @staticmethod
    def is_valid(celsius):
        return celsius >= -273.15

t = Temperature.from_fahrenheit(212)
print(t.celsius, t.to_fahrenheit(), Temperature.is_valid(-300))   # 100.0 212.0 False
```

| | Instance method | `@classmethod` | `@staticmethod` |
|---|---|---|---|
| First parameter | `self` (the instance) | `cls` (the class) | none |
| Can access instance data | yes | no | no |
| Can access class data | yes (`type(self)`) | yes (`cls`) | only by naming the class |
| Called as | `obj.m()` | `Cls.m()` or `obj.m()` | `Cls.m()` or `obj.m()` |
| Typical use | behaviour of an object | alternative constructors, class-level state | utilities related to the class |

## 2. Class methods as alternative constructors

`__init__` can have only one signature. Class methods give you **named constructors** for other input forms:

```python
from datetime import date

class Reading:
    def __init__(self, sensor, value):
        self.sensor = sensor
        self.value = value

    @classmethod
    def from_csv(cls, line):
        sensor, value = line.split(",")
        return cls(sensor, float(value))

    @classmethod
    def zero(cls, sensor):
        return cls(sensor, 0.0)

r = Reading.from_csv("lidar,2.5")
print(r.sensor, r.value)          # lidar 2.5
```

> [!KEY]
> Use `cls(...)`, **not** `Reading(...)`, inside a class method. Then subclasses inherit a working constructor: `SpecialReading.from_csv(...)` returns a `SpecialReading`, because `cls` is whichever class the method was called on.

```python
class Calibrated(Reading):
    pass

print(type(Calibrated.from_csv("imu,1.0")).__name__)   # Calibrated
```

Standard-library examples: `dict.fromkeys`, `int.from_bytes`, `datetime.fromtimestamp`, `Path.home`.

## 3. Class methods for class-level state

```python
class Motor:
    _instances = 0

    def __init__(self):
        type(self)._register()

    @classmethod
    def _register(cls):
        cls._instances += 1

    @classmethod
    def instances(cls):
        return cls._instances
```

## 4. Static methods

A static method is an ordinary function placed in the class namespace because it's **logically related** to the class, while needing neither the instance nor the class:

```python
class Geometry:
    @staticmethod
    def distance(a, b):
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
```

> [!TIP]
> In Python, a module-level function is often just as good as a static method. Use `@staticmethod` when the function is a natural part of the class's interface (like validation helpers), or when you want subclasses to be able to override it.

## 5. How it works underneath (preview)

Functions defined in a class are **descriptors**. Accessing `obj.method` produces a **bound method** that remembers `obj` and inserts it as the first argument when called:

```python
t = Temperature(20)
m = t.to_fahrenheit           # bound method: the function plus t
print(m())                    # 68.0
print(m.__self__ is t)        # True
```

`classmethod` binds the class instead of the instance, and `staticmethod` binds nothing. The Descriptors lesson in the Advanced module shows how these decorators are implemented.

## 6. Exam-ready answers

> [!EXAM]
> **Instance, class and static methods.** An instance method takes the instance as its first parameter (`self`) and operates on that object's state. A class method, declared with `@classmethod`, receives the class as its first parameter (`cls`) and can access or modify class-level state; it is commonly used to implement alternative constructors that return `cls(...)`, which work correctly for subclasses. A static method, declared with `@staticmethod`, receives no implicit first argument and behaves like a plain function placed in the class's namespace because it is logically related to the class. Class and static methods can be called on the class or on an instance.

## 7. Cheat sheet

| Need | Code |
|---|---|
| object behaviour | `def m(self): ...` |
| alternative constructor | `@classmethod def from_x(cls, x): return cls(...)` |
| class-level counter | `@classmethod def inc(cls): cls.n += 1` |
| related helper | `@staticmethod def valid(v): ...` |
| bound method | `f = obj.m; f()` |

> [!INTERVIEW]
> **"Why should alternative constructors be classmethods rather than staticmethods?"** A classmethod receives `cls`, the class it was called on, so `return cls(...)` builds the right type even for subclasses. A staticmethod would have to hard-code `return Temperature(...)`, so `Kelvin.from_fahrenheit(...)` would wrongly return a `Temperature`. That breaks inheritance.

## Worked example: all three in one class

```python
from datetime import date

class Reading:
    count = 0                                   # class-level state shared by all instances

    def __init__(self, sensor: str, value: float, day: date):
        self.sensor, self.value, self.day = sensor, value, day
        Reading.count += 1

    def in_range(self, lo: float, hi: float) -> bool:      # instance method: uses self
        return lo <= self.value <= hi

    @classmethod
    def from_csv(cls, line: str) -> "Reading":              # alternative constructor: uses cls
        sensor, value, day = line.split(",")
        return cls(sensor, float(value), date.fromisoformat(day))

    @staticmethod
    def celsius_to_f(c: float) -> float:                    # helper: needs neither
        return c * 9 / 5 + 32

r = Reading.from_csv("temp1,21.5,2026-10-26")
print(r.sensor, r.value, r.in_range(15, 25))
print(Reading.celsius_to_f(r.value), Reading.count)
```

```output
temp1 21.5 True
70.7 1
```

**How to choose:**

| Needs the object's data? | Needs the class? | Use |
|---|---|---|
| yes | – | instance method |
| no | yes (to construct, or for class-wide state) | `@classmethod` |
| no | no | `@staticmethod`, or a plain module-level function |

`cls(...)` in `from_csv` matters for inheritance: `SubReading.from_csv(...)` builds a `SubReading`, not a `Reading`.

## Common mistakes

- **Writing `Reading(...)` instead of `cls(...)`** inside a classmethod. That breaks subclasses.
- **Modifying a mutable class attribute through `self`** (`self.items.append(x)` where `items = []` is defined on the class). Every instance shares that one list.
- **Using `@staticmethod` for everything** because "it doesn't use self yet". A module-level function is often clearer.

## Check your understanding

1. What is printed by `Reading.count` after creating three readings?
2. Why is `dict.fromkeys` a classmethod?

<details><summary>Answers</summary>

1. `3`. It is shared class state, incremented in `__init__`.
2. It's an alternative constructor. Called on a `dict` subclass, it returns an instance of that subclass.

</details>
