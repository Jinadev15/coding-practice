---
id: py-fix-circular
title: Break the Circular Import
difficulty: Medium
order: 2
tags: circular imports, module design, refactoring
---
## Statement
A teammate split a tiny robot app into two modules that import each other, and it crashes with `partially initialized module`:

- `robot.py` defines `Robot` and needs `distance()` from `nav.py`
- `nav.py` defines `distance()` but also uses the constant `MAX_SPEED`, which lives in `robot.py`

**Refactor** so nothing is circular: create the module `config.py` holding `MAX_SPEED = 2.0`. `robot.py` and `nav.py` both import from `config`, and `robot.py` imports `nav`, but `nav.py` must **not** import `robot`. Keep the behaviour:

- `nav.distance(a, b)` returns the Euclidean distance between two `(x, y)` points
- `nav.travel_time(a, b)` returns `distance / MAX_SPEED`
- `robot.Robot(name).move_to(point)` returns `"NAME moved D m in T s"` with 2 decimals, and updates its position (start at `(0, 0)`)

The hidden driver checks that `nav` doesn't depend on `robot`.

## Starter: main.py
```python
import sys
from robot import Robot

r = Robot(input().strip())
for line in sys.stdin.read().splitlines():
    x, y = map(float, line.split())
    print(r.move_to((x, y)))

import nav
print("nav imports robot:", "robot" in vars(nav))
```

## Starter: robot.py
```python
import nav

MAX_SPEED = 2.0

class Robot:
    def __init__(self, name):
        self.name = name
        self.pos = (0.0, 0.0)

    def move_to(self, point):
        d = nav.distance(self.pos, point)
        t = nav.travel_time(self.pos, point)
        self.pos = point
        return f"{self.name} moved {d:.2f} m in {t:.2f} s"
```

## Starter: nav.py
```python
import math
import robot

def distance(a, b):
    return math.dist(a, b)

def travel_time(a, b):
    return distance(a, b) / robot.MAX_SPEED
```

## Starter: config.py
```python
# shared constants go here
```

## Tests
=== sample
rover
3 4
3 0
---
rover moved 5.00 m in 2.50 s
rover moved 4.00 m in 2.00 s
nav imports robot: False
=== hidden
arm
0 0
-1 -1
---
arm moved 0.00 m in 0.00 s
arm moved 1.41 m in 0.71 s
nav imports robot: False

## Hints
- Move `MAX_SPEED` into `config.py`.
- In `nav.py`, replace `import robot` with `from config import MAX_SPEED` (or `import config`).
- `robot.py` can keep `import nav`, since the dependency now goes one way: `robot → nav → config`.

## Solution
The shared constant was the hidden third concept. Extracting it into `config.py` turns the cycle `robot ⇄ nav` into a DAG, `robot → nav → config` plus `robot → config`.

## Solution: config.py
```python
MAX_SPEED = 2.0
```

## Solution: nav.py
```python
import math
from config import MAX_SPEED

def distance(a, b):
    return math.dist(a, b)

def travel_time(a, b):
    return distance(a, b) / MAX_SPEED
```

## Solution: robot.py
```python
import nav
from config import MAX_SPEED

class Robot:
    def __init__(self, name):
        self.name = name
        self.pos = (0.0, 0.0)

    def move_to(self, point):
        d = nav.distance(self.pos, point)
        t = nav.travel_time(self.pos, point)
        self.pos = point
        return f"{self.name} moved {d:.2f} m in {t:.2f} s"
```

## Solution: main.py
```python
import sys
from robot import Robot

r = Robot(input().strip())
for line in sys.stdin.read().splitlines():
    x, y = map(float, line.split())
    print(r.move_to((x, y)))

import nav
print("nav imports robot:", "robot" in vars(nav))
```
