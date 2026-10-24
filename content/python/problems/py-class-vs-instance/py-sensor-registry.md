---
id: py-sensor-registry
title: Sensor Registry with Shared State
difficulty: Medium
order: 1
tags: class attributes, instance attributes, registries
---
## Statement
Write a class `Sensor` that uses **class attributes** for shared state and **instance attributes** for per-sensor state:

- class attribute `DEFAULT_RATE = 10` (Hz)
- every created sensor gets a unique, increasing `id` starting at 1 (a shared counter on the class)
- `Sensor(name, rate=None)`: `rate` defaults to the **current** `Sensor.DEFAULT_RATE` at creation time
- each sensor keeps its **own** list of readings: `add(value)` appends; `mean()` returns the average, or `None`
- class-level registry: `Sensor.by_name(name)` returns the sensor with that name (a classmethod reading a class dict)
- `Sensor.count()` returns how many sensors exist

The driver also changes `Sensor.DEFAULT_RATE` midway to check that existing sensors keep their own rate.

## Starter
```python
class Sensor:
    DEFAULT_RATE = 10
```

## Driver
```python
for line in iter(input, "END"):
    cmd, *a = line.split()
    if cmd == "new":
        s = Sensor(a[0]) if len(a) == 1 else Sensor(a[0], int(a[1]))
        print(f"{s.name} id={s.id} rate={s.rate}")
    elif cmd == "default":
        Sensor.DEFAULT_RATE = int(a[0])
    elif cmd == "add":
        Sensor.by_name(a[0]).add(float(a[1]))
    elif cmd == "mean":
        print(a[0], Sensor.by_name(a[0]).mean())
print("count", Sensor.count())
```

## Tests
=== sample
new lidar
new imu 100
default 50
new cam
add lidar 1
add lidar 3
mean lidar
mean imu
END
---
lidar id=1 rate=10
imu id=2 rate=100
cam id=3 rate=50
lidar 2.0
imu None
count 3
=== hidden
default 1
new a
new b
add a 5
add b 7
mean a
mean b
END
---
a id=1 rate=1
b id=2 rate=1
a 5.0
b 7.0
count 2

## Hints
- `_next_id = 1` and `_registry = {}` as class attributes. Update them through the class (`Sensor._next_id += 1`), not `self`.
- `self.readings = []` in `__init__`. A list in the class body would be shared by every sensor.
- `rate if rate is not None else Sensor.DEFAULT_RATE`, evaluated inside `__init__` (not as a default parameter value, which would freeze it at definition time).

## Solution
```python
class Sensor:
    DEFAULT_RATE = 10
    _next_id = 1
    _registry = {}

    def __init__(self, name, rate=None):
        self.name = name
        self.rate = rate if rate is not None else Sensor.DEFAULT_RATE
        self.id = Sensor._next_id
        Sensor._next_id += 1
        self.readings = []
        Sensor._registry[name] = self

    def add(self, value):
        self.readings.append(value)

    def mean(self):
        return sum(self.readings) / len(self.readings) if self.readings else None

    @classmethod
    def by_name(cls, name):
        return cls._registry[name]

    @classmethod
    def count(cls):
        return len(cls._registry)
```

`def __init__(self, name, rate=Sensor.DEFAULT_RATE)` couldn't even work (the class doesn't exist yet when its body runs), and a default like `rate=10` would ignore later changes to `DEFAULT_RATE`. Reading the class attribute at call time keeps the default live. The `_registry` dict is a **deliberately** shared mutable class attribute, modified only through class-level code.
