# Special Methods: __str__, __repr__, __eq__

Special methods ("dunder" methods, for **d**ouble **under**score) are how your classes plug into Python's syntax and built-ins. Defining `__repr__` controls how an object prints; `__eq__` defines `==`; `__lt__` makes objects sortable; `__hash__` lets them be dict keys and set members. Getting these few right makes your classes feel like built-in types, and the rules connecting `__eq__` and `__hash__` are a frequent interview topic.

## 1. Python calls them for you

You rarely call dunders directly. Python calls them when you use the syntax:

| You write | Python calls |
|---|---|
| `repr(obj)`, REPL echo, inside containers | `obj.__repr__()` |
| `str(obj)`, `print(obj)`, `f"{obj}"` | `obj.__str__()` (falls back to `__repr__`) |
| `a == b` | `a.__eq__(b)` |
| `a < b` | `a.__lt__(b)` |
| `hash(obj)`, dict key, set member | `obj.__hash__()` |
| `len(obj)` | `obj.__len__()` |
| `bool(obj)` | `obj.__bool__()` |

## 2. `__repr__` and `__str__`

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):                       # for developers: unambiguous
        return f"Point({self.x!r}, {self.y!r})"

    def __str__(self):                        # for users: readable
        return f"({self.x}, {self.y})"

p = Point(1, 2)
print(p)            # (1, 2)             ← __str__
print(repr(p))      # Point(1, 2)        ← __repr__
print([p])          # [Point(1, 2)]      ← containers use repr of their elements
print(f"{p!r}")     # Point(1, 2)
```

> [!KEY]
> - **Always define `__repr__`.** It's what you see while debugging, in logs and in containers. A good `__repr__` looks like the constructor call that recreates the object (`eval(repr(p)) == p` when practical).
> - `__str__` is optional. If it's missing, `str()` uses `__repr__`.
> - The default repr, `<__main__.Point object at 0x7f3a…>`, tells you almost nothing.

## 3. `__eq__`: value equality

By default, `==` on objects compares **identity** (the same as `is`):

```python
class P:
    def __init__(self, x): self.x = x
print(P(1) == P(1))        # False: two different objects
```

Define `__eq__` for **value** semantics:

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented             # let Python try other.__eq__, or fall back
        return (self.x, self.y) == (other.x, other.y)

print(Point(1, 2) == Point(1, 2))   # True
print(Point(1, 2) == (1, 2))        # False (no crash)
print(Point(1, 2) != Point(1, 3))   # True: __ne__ is derived from __eq__ automatically
```

> [!WARNING]
> Return the special singleton **`NotImplemented`** (not `False`, and not raising) for types you don't handle. Python then tries the reflected operation on the other operand, and if that's also unhandled, `==` falls back to identity (`False`). Don't confuse it with the exception `NotImplementedError`.

## 4. The `__eq__` / `__hash__` contract

> [!KEY]
> **Objects that compare equal must have equal hashes.** Dicts and sets find entries by hash first and confirm with `==`. If two equal objects had different hashes, a set could contain "duplicates" and lookups would fail.

Python enforces part of this: **defining `__eq__` sets `__hash__` to `None`**, which makes instances unhashable, unless you also define `__hash__`:

```python
class NoHash:
    def __eq__(self, other): return True
print(NoHash.__hash__)              # None
# {NoHash()}                        → TypeError: unhashable type: 'NoHash'
```

Define `__hash__` from the **same fields** that `__eq__` uses, and only if those fields never change while the object is in a set or dict:

```python
class Point:
    ...
    def __hash__(self):
        return hash((self.x, self.y))       # hash the same tuple __eq__ compares

print({Point(1, 2), Point(1, 2)})           # {Point(1, 2)}: one element
```

| Your class | `__eq__` | `__hash__` |
|---|---|---|
| identity semantics (default) | inherited (identity) | inherited (identity-based) ✓ |
| value semantics, **immutable** | define | define from the same fields ✓ |
| value semantics, **mutable** | define | leave as `None` (unhashable), which is the correct choice |

Mutable objects with value equality shouldn't be hashable: if a field changed after insertion into a set, the object's hash would change and it would be "lost" in the wrong bucket.

## 5. Ordering: `__lt__` and friends

`sorted()`, `min()` and `max()` need `<`:

```python
class Version:
    def __init__(self, major, minor):
        self.major, self.minor = major, minor
    def __repr__(self):
        return f"Version({self.major}, {self.minor})"
    def __eq__(self, other):
        return (self.major, self.minor) == (other.major, other.minor)
    def __lt__(self, other):
        return (self.major, self.minor) < (other.major, other.minor)

print(sorted([Version(2, 0), Version(1, 9)]))   # [Version(1, 9), Version(2, 0)]
```

Comparing **tuples of fields** is the idiomatic way to implement ordering. `@functools.total_ordering` derives `<=`, `>`, `>=` from `__eq__` and `__lt__`.

## 6. `@dataclass` writes these for you

```python
from dataclasses import dataclass

@dataclass(frozen=True, order=True)
class Point:
    x: float
    y: float

p = Point(1, 2)
print(p, p == Point(1, 2), {p}, sorted([Point(2, 0), p]))
# Point(x=1, y=2) True {Point(x=1, y=2)} [Point(x=1, y=2), Point(x=2, y=0)]
```

`@dataclass` generates `__init__`, `__repr__` and `__eq__`. `frozen=True` makes instances immutable **and** hashable, and `order=True` adds comparisons. Learn the manual versions first (you need them in C++ too), then use dataclasses in practice (Dataclasses lesson).

## 7. Exam-ready answers

> [!EXAM]
> **Special (magic) methods.** Special methods are methods with double-underscore names, such as `__init__`, `__repr__`, `__str__`, `__eq__`, `__lt__`, `__hash__`, `__len__` and `__add__`, that Python invokes implicitly to implement language syntax and built-in functions for user-defined classes. `__repr__` returns an unambiguous developer-oriented representation used by `repr()` and in containers; `__str__` returns a readable representation used by `str()` and `print()`, falling back to `__repr__`. `__eq__` implements `==`, returning `NotImplemented` for unsupported operand types.

> [!EXAM]
> **The relationship between `__eq__` and `__hash__`.** Hash-based collections require that objects which compare equal have the same hash value. Defining `__eq__` in a class sets its `__hash__` to `None`, making instances unhashable unless `__hash__` is also defined. A consistent `__hash__` is computed from the same immutable fields used by `__eq__`. Mutable objects with value-based equality should generally remain unhashable.

## 8. Cheat sheet

| Need | Code |
|---|---|
| debug print | `def __repr__(self): return f"Cls({self.a!r})"` |
| user print | `def __str__(self): ...` |
| value equality | `__eq__` with `isinstance` check, returning `NotImplemented` |
| hashable value object | `__hash__ = hash((fields...))` (immutable fields only) |
| sortable | `__lt__` comparing tuples, + `@total_ordering` |
| all of it, generated | `@dataclass(frozen=True, order=True)` |

> [!INTERVIEW]
> **"I added `__eq__` to my class and now I can't put instances in a set. Why?"** Defining `__eq__` implicitly sets `__hash__ = None`, because the inherited identity hash would break the rule that equal objects must hash equally. Define `__hash__` over the same fields as `__eq__`, and only if they're immutable (or use `@dataclass(frozen=True)`). Explain the bucket-lookup reason: the hash is used to find the bucket, and equality to confirm the match.
