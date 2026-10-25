---
id: py-two-module-app
title: Split Into Modules
difficulty: Easy
order: 1
tags: modules, imports, multi-file
---
## Statement
Your first **multi-file** program. Three files are provided as tabs in the editor:

- `geometry.py`: implement `circle_area(r)`, `rect_area(w, h)` and a constant `PI = 3.141592653589793`
- `formatting.py`: implement `fmt(x)`, which returns `x` formatted with exactly 3 decimals
- `main.py`: read shapes from stdin (`circle r` or `rect w h`), and print each area with `fmt`, then the total area

`main.py` must **import** the other two modules (don't copy the code). `geometry.py` must not print anything when imported, but when run directly (`python3 geometry.py`) it may run a self-test. Guard that with `if __name__ == "__main__":`.

## Starter: main.py
```python
import sys
import geometry
from formatting import fmt

total = 0.0
for line in sys.stdin.read().splitlines():
    pass
```

## Starter: geometry.py
```python
PI = 3.141592653589793

def circle_area(r):
    pass

def rect_area(w, h):
    pass

if __name__ == "__main__":
    print("self-test:", circle_area(1))
```

## Starter: formatting.py
```python
def fmt(x):
    pass
```

## Tests
=== sample
circle 1
rect 2 3
---
3.142
6.000
total 9.142
=== hidden
circle 0
---
0.000
total 0.000
=== hidden
rect 1.5 2
circle 2
rect 10 0.1
---
3.000
12.566
1.000
total 16.566

## Hints
- Each file is a module: `import geometry` makes `geometry.circle_area` available in `main.py`; `from formatting import fmt` imports one name.
- Code at the top level of a module runs on import, so keep self-tests under `if __name__ == "__main__":`.
- `fmt(x)` is just `f"{x:.3f}"`; keep a running `total` in `main.py`.

## Solution
Each module has one responsibility: maths, presentation, and orchestration. `main.py` only wires them together.

## Solution: main.py
```python
import sys
import geometry
from formatting import fmt

total = 0.0
for line in sys.stdin.read().splitlines():
    kind, *nums = line.split()
    nums = list(map(float, nums))
    if kind == "circle":
        area = geometry.circle_area(*nums)
    else:
        area = geometry.rect_area(*nums)
    total += area
    print(fmt(area))
print("total", fmt(total))
```

## Solution: geometry.py
```python
PI = 3.141592653589793

def circle_area(r):
    return PI * r * r

def rect_area(w, h):
    return w * h

if __name__ == "__main__":
    print("self-test:", circle_area(1))
```

## Solution: formatting.py
```python
def fmt(x):
    return f"{x:.3f}"
```
