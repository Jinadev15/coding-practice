# Abstract Base Classes and Protocols

Python is **duck-typed**: if an object has the methods you call, it works, whatever its class. That flexibility needs structure in larger systems: how do you define an interface, make sure implementations are complete, and let type checkers verify usage? Python offers two complementary answers. **Abstract Base Classes** (ABCs) give **nominal** interfaces that classes explicitly inherit and that are enforced at instantiation. **Protocols** (PEP 544) give **structural** interfaces that any class with the right methods satisfies, checked statically. Knowing when to use each is a mark of senior Python design.

## 1. ABCs with `abc.ABC` and `@abstractmethod`

```python
from abc import ABC, abstractmethod

class Sensor(ABC):
    @abstractmethod
    def read(self) -> float:
        """Return the latest measurement."""

    @property
    @abstractmethod
    def unit(self) -> str: ...

    def read_many(self, n: int) -> list[float]:      # a concrete "template" method built on the abstract one
        return [self.read() for _ in range(n)]

Sensor()
# TypeError: Can't instantiate abstract class Sensor without an implementation for abstract methods 'read', 'unit'

class Thermometer(Sensor):
    def read(self) -> float: return 21.5
    @property
    def unit(self) -> str: return "°C"

Thermometer().read_many(2)     # [21.5, 21.5]
```

> [!KEY]
> Enforcement happens at **instantiation**, not at class definition: a subclass that forgets an abstract method can be defined, but creating an instance raises `TypeError`. Abstract methods can still have a body (called via `super()`). ABCs mix interface (abstract methods) with shared implementation (concrete methods).

## 2. The `collections.abc` interfaces

The standard library defines ABCs for the container protocols, with **mixin methods** you get for free:

| ABC | You implement | You get for free |
|---|---|---|
| `Iterable` | `__iter__` | |
| `Iterator` | `__next__` (and `__iter__`) | |
| `Sized`, `Container` | `__len__` / `__contains__` | |
| `Sequence` | `__getitem__`, `__len__` | `__contains__`, `__iter__`, `__reversed__`, `index`, `count` |
| `MutableSequence` | + `__setitem__`, `__delitem__`, `insert` | `append`, `extend`, `pop`, `remove`, `+=` |
| `Mapping` | `__getitem__`, `__iter__`, `__len__` | `get`, `keys`, `items`, `values`, `__eq__`, `__contains__` |
| `MutableMapping` | + `__setitem__`, `__delitem__` | `pop`, `setdefault`, `update`, `clear` |
| `Set` | `__contains__`, `__iter__`, `__len__` | `&`, `\|`, `-`, `^`, comparisons |

```python
from collections.abc import MutableMapping

class LowerDict(MutableMapping):            # a case-insensitive dict in ~10 lines
    def __init__(self, *args, **kw):
        self._d = {}
        self.update(*args, **kw)            # update() comes free from MutableMapping
    def __getitem__(self, k): return self._d[k.lower()]
    def __setitem__(self, k, v): self._d[k.lower()] = v
    def __delitem__(self, k): del self._d[k.lower()]
    def __iter__(self): return iter(self._d)
    def __len__(self): return len(self._d)
```

> [!TIP]
> Prefer inheriting from `collections.abc.MutableMapping` over subclassing `dict` directly. `dict`'s C implementation of `update` and `__init__` **bypasses** your overridden `__setitem__`, so a `dict` subclass silently skips your logic. The ABC routes everything through your five methods.

### Checking interfaces

```python
from collections.abc import Sequence, Iterable, Mapping
isinstance([], Sequence)         # True
isinstance({}, Mapping)          # True
isinstance("abc", Iterable)      # True
issubclass(dict, Sequence)       # False
```

Some ABCs check structurally via `__subclasshook__` (`Iterable` checks for `__iter__`). Others need inheritance or explicit registration with `Sequence.register(MyType)`. One subtlety: a class with only `__getitem__` is iterable by `iter()` but **not** `isinstance(..., Iterable)`.

## 3. Protocols: structural typing

```python
from typing import Protocol, runtime_checkable

class SupportsArea(Protocol):
    def area(self) -> float: ...

class Square:                       # does NOT inherit from SupportsArea
    def __init__(self, s): self.s = s
    def area(self) -> float: return self.s ** 2

def total_area(shapes: list[SupportsArea]) -> float:
    return sum(s.area() for s in shapes)

total_area([Square(2)])             # OK for both the interpreter and the type checker (mypy, pyright)
```

A Protocol says "anything with these methods", which is duck typing made **statically checkable**. Classes don't need to know about the protocol, so it works with third-party classes you can't modify. Adding `@runtime_checkable` enables `isinstance(obj, SupportsArea)`, but that only checks that the method *names* exist, not their signatures.

| | ABC (nominal) | Protocol (structural) |
|---|---|---|
| Implementations must inherit | yes (or `register`) | **no** |
| Checked | at run time when instantiating | by the static type checker |
| Can provide shared implementation | yes (mixins) | possible, but not typical |
| Works with third-party classes | only via `register` | automatically |
| Best for | frameworks and plugin bases with shared behaviour | interfaces for parameters, decoupling modules |

## 4. Design guidance

> [!KEY]
> - Use a **Protocol** to type a function parameter ("needs something with `.read()`"). It's the lowest coupling and Pythonic duck typing, with type safety.
> - Use an **ABC** when you're building a framework and want to provide shared behaviour, force implementers to fill in hooks, and fail fast on incomplete classes.
> - Don't build deep inheritance hierarchies of ABCs. Composition plus small interfaces is clearer (the Interface Segregation Principle in the Master OOP module).

## 5. Exam-ready answers

> [!EXAM]
> **Abstract base classes and protocols.** An abstract base class, created by inheriting from `abc.ABC` (or using `ABCMeta`), defines an interface through methods decorated with `@abstractmethod`; a class with unimplemented abstract methods cannot be instantiated, so subclasses must implement them, while the ABC may also provide concrete methods. The `collections.abc` module defines ABCs for container protocols, such as `Sequence` and `MutableMapping`, which supply mixin methods once the required abstract methods are implemented, and support `isinstance` checks. Protocols from `typing` (PEP 544) define structural interfaces: any class providing the specified methods and attributes is considered compatible by static type checkers without inheriting from the protocol, formalising duck typing; `@runtime_checkable` allows limited `isinstance` checks.

## 6. Cheat sheet

| Need | Tool |
|---|---|
| a required method in subclasses | `@abstractmethod` in an `ABC` |
| an abstract property | `@property` above `@abstractmethod` |
| a custom dict-like class | `collections.abc.MutableMapping` |
| a custom list-like class | `collections.abc.MutableSequence` |
| "anything with method m" | `class P(Protocol): def m(self) -> T: ...` |
| a runtime check against a protocol | `@runtime_checkable` + `isinstance` |
| declare an existing class as implementing an ABC | `ABC.register(Cls)` |

> [!INTERVIEW]
> **"What's the difference between an ABC and a Protocol in Python?"** An ABC is nominal: classes must explicitly inherit from it (or be registered), and the interpreter enforces it, refusing to instantiate classes with missing abstract methods. ABCs can also share implementation through concrete methods. A Protocol is structural: a type satisfies it just by having the right methods and signatures, with no inheritance, and the check is done by static type checkers (plus an optional shallow runtime check). Use Protocols to type loosely coupled interfaces, including third-party classes, and ABCs for framework base classes with shared behaviour.
