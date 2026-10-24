---
id: py-sensor-package
title: Build a Sensor Package
difficulty: Medium
order: 1
tags: packages, __init__.py, relative imports, public API
---
## Statement
Build a small package `robot` with this layout (the files are already open as editor tabs):

```text
robot/__init__.py          re-export: Reading, average, Lidar, Thermometer
robot/model.py             Reading (a plain class: sensor name, value)
robot/stats.py             average(readings) → mean of .value (0.0 if empty)
robot/sensors/__init__.py  re-export Lidar, Thermometer
robot/sensors/lidar.py     Lidar(name).read(raw) → Reading(name, raw / 1000)   (mm → m)
robot/sensors/thermo.py    Thermometer(name).read(raw) → Reading(name, raw * 0.1 - 40)
```

Rules: inside the package use **relative imports** (`from ..model import Reading`, `from .lidar import Lidar`). `main.py` uses only the **public API**: `from robot import Lidar, Thermometer, average`.

Input lines are `kind raw` (`lidar 1500`, `thermo 650`). Print each reading as `name=value` with 2 decimals, then `avg=…`.

## Starter: main.py
```python
import sys
from robot import Lidar, Thermometer, average

devices = {"lidar": Lidar("lidar0"), "thermo": Thermometer("temp0")}
readings = []
for line in sys.stdin.read().splitlines():
    kind, raw = line.split()
    r = devices[kind].read(float(raw))
    readings.append(r)
    print(f"{r.sensor}={r.value:.2f}")
print(f"avg={average(readings):.2f}")
```

## Starter: robot/__init__.py
```python
# re-export the public API here
```

## Starter: robot/model.py
```python
class Reading:
    def __init__(self, sensor, value):
        self.sensor = sensor
        self.value = value
```

## Starter: robot/stats.py
```python
def average(readings):
    pass
```

## Starter: robot/sensors/__init__.py
```python
```

## Starter: robot/sensors/lidar.py
```python
class Lidar:
    pass
```

## Starter: robot/sensors/thermo.py
```python
class Thermometer:
    pass
```

## Tests
=== sample
lidar 1500
thermo 650
---
lidar0=1.50
temp0=25.00
avg=13.25
=== hidden
lidar 0
---
lidar0=0.00
avg=0.00
=== hidden
thermo 0
thermo 400
lidar 2500
---
temp0=-40.00
temp0=0.00
lidar0=2.50
avg=-12.50

## Hints
- `robot/sensors/lidar.py`: `from ..model import Reading` (two dots: up from `robot.sensors` to `robot`).
- `robot/sensors/__init__.py`: `from .lidar import Lidar` and `from .thermo import Thermometer`.
- `robot/__init__.py`: `from .model import Reading`, `from .stats import average`, `from .sensors import Lidar, Thermometer`.

## Solution
Each file holds one concept, internal imports are relative, and the two `__init__.py` files form the public API, so `main.py` never mentions `robot.sensors.lidar`.

## Solution: robot/__init__.py
```python
from .model import Reading
from .stats import average
from .sensors import Lidar, Thermometer

__all__ = ["Reading", "average", "Lidar", "Thermometer"]
```

## Solution: robot/model.py
```python
class Reading:
    def __init__(self, sensor, value):
        self.sensor = sensor
        self.value = value
```

## Solution: robot/stats.py
```python
def average(readings):
    if not readings:
        return 0.0
    return sum(r.value for r in readings) / len(readings)
```

## Solution: robot/sensors/__init__.py
```python
from .lidar import Lidar
from .thermo import Thermometer
```

## Solution: robot/sensors/lidar.py
```python
from ..model import Reading

class Lidar:
    def __init__(self, name):
        self.name = name

    def read(self, raw):
        return Reading(self.name, raw / 1000)
```

## Solution: robot/sensors/thermo.py
```python
from ..model import Reading

class Thermometer:
    def __init__(self, name):
        self.name = name

    def read(self, raw):
        return Reading(self.name, raw * 0.1 - 40)
```

## Solution: main.py
```python
import sys
from robot import Lidar, Thermometer, average

devices = {"lidar": Lidar("lidar0"), "thermo": Thermometer("temp0")}
readings = []
for line in sys.stdin.read().splitlines():
    kind, raw = line.split()
    r = devices[kind].read(float(raw))
    readings.append(r)
    print(f"{r.sensor}={r.value:.2f}")
print(f"avg={average(readings):.2f}")
```
