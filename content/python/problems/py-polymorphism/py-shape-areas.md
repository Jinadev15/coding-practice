---
id: py-shape-areas
title: Polymorphic Shapes
difficulty: Medium
order: 1
tags: polymorphism, inheritance, abstract methods
---
## Statement
Design a shape hierarchy where **no code outside the shape classes checks types**:

- abstract base `Shape` (use `abc.ABC`) with abstract methods `area()` and `perimeter()`, and a concrete method `describe()` returning `"NAME area=A perimeter=P"` (2 decimals), where NAME is the class name
- `Circle(r)`, `Rect(w, h)`, `Triangle(a, b, c)` (area by Heron's formula; raise `ValueError` if the sides violate the triangle inequality)
- a function `largest(shapes)` returning the shape with the greatest area (first on ties)

The driver builds shapes from lines like `Rect 2 3`, looking up the class **by name** from a dict and calling it with the numbers. Then it prints each `describe()`, the largest one, and the total area.

## Starter
```python
import math
from abc import ABC, abstractmethod

class Shape(ABC):
    pass


def largest(shapes):
    pass
```

## Driver
```python
import inspect
assert inspect.isabstract(Shape), "Shape must be abstract"
classes = {"Circle": Circle, "Rect": Rect, "Triangle": Triangle}
shapes = []
for line in iter(input, "END"):
    name, *nums = line.split()
    try:
        shapes.append(classes[name](*map(float, nums)))
    except ValueError:
        print("invalid", line)
for s in shapes:
    print(s.describe())
print("largest:", type(largest(shapes)).__name__ if shapes else None)
print(f"total={sum(s.area() for s in shapes):.2f}")
```

## Tests
=== sample
Circle 1
Rect 2 3
Triangle 3 4 5
END
---
Circle area=3.14 perimeter=6.28
Rect area=6.00 perimeter=10.00
Triangle area=6.00 perimeter=12.00
largest: Rect
total=15.14
=== hidden
Triangle 1 1 3
Circle 0.5
END
---
invalid Triangle 1 1 3
Circle area=0.79 perimeter=3.14
largest: Circle
total=0.79
=== hidden
END
---
largest: None
total=0.00

## Hints
- `class Shape(ABC):` with `@abstractmethod def area(self): ...`. `describe` uses `type(self).__name__`, `self.area()` and `self.perimeter()`, so it's written once.
- Heron: `s = (a + b + c) / 2; area = sqrt(s(s-a)(s-b)(s-c))`.
- `largest`: `max(shapes, key=lambda s: s.area())`, since `max` keeps the first of equal keys.

## Solution
```python
import math
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self): ...

    @abstractmethod
    def perimeter(self): ...

    def describe(self):
        return f"{type(self).__name__} area={self.area():.2f} perimeter={self.perimeter():.2f}"


class Circle(Shape):
    def __init__(self, r):
        self.r = r
    def area(self):
        return math.pi * self.r ** 2
    def perimeter(self):
        return 2 * math.pi * self.r


class Rect(Shape):
    def __init__(self, w, h):
        self.w, self.h = w, h
    def area(self):
        return self.w * self.h
    def perimeter(self):
        return 2 * (self.w + self.h)


class Triangle(Shape):
    def __init__(self, a, b, c):
        x, y, z = sorted((a, b, c))
        if x + y <= z:
            raise ValueError("not a triangle")
        self.a, self.b, self.c = a, b, c
    def area(self):
        s = self.perimeter() / 2
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))
    def perimeter(self):
        return self.a + self.b + self.c


def largest(shapes):
    return max(shapes, key=lambda s: s.area())
```

`describe` is a **template method**: written once in the base class, it calls methods the subclasses supply. Adding a `Hexagon` needs one new class and one dictionary entry. `largest`, `describe` and the driver loop don't change. That's the open/closed principle in miniature.
