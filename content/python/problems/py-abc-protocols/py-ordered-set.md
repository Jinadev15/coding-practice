---
id: py-ordered-set
title: OrderedSet via collections.abc
difficulty: Medium
order: 1
tags: collections.abc, MutableSet, mixin methods, Protocol
---
## Statement
Implement `OrderedSet`, a set that remembers **insertion order**, by inheriting from `collections.abc.MutableSet` and implementing only the five abstract methods: `__contains__`, `__iter__`, `__len__`, `add` and `discard`. The ABC then gives you `|`, `&`, `-`, `^`, `<=`, `==`, `isdisjoint`, `remove`, `pop`, `clear`, `|=` and more for free.

Also:
- `OrderedSet(iterable=())` keeps the first-seen order, and duplicates are ignored.
- `repr` is `OrderedSet([1, 2, 3])`, and `OrderedSet()` when empty.
- `index(x)` returns the position of x (`ValueError` if absent). Keep `add`, `discard`, `in` and `len` O(1) on average.
- Results of the set operators come back as `OrderedSet`s, because the ABC builds them through the classmethod `_from_iterable`, which by default calls `cls(iterable)`. So it works as long as your constructor accepts an iterable. Their order is whatever the mixin's generator yields: `|`, `-` and `^` list the left operand's elements first, while `&` is built by iterating the **right** operand (read `Set.__and__` in `_collections_abc.py`!).

Finally, define a **Protocol** `SupportsAdd` (with `add(self, x) -> None`), decorated with `@runtime_checkable`, plus a function `add_all(target: SupportsAdd, items) -> int` that adds the items and returns how many there were. The driver passes your `OrderedSet`, a builtin `set` and a custom class that doesn't inherit anything.

## Starter
```python
from collections.abc import MutableSet
from typing import Protocol, runtime_checkable

class OrderedSet(MutableSet):
    pass

class SupportsAdd(Protocol):
    pass

def add_all(target, items):
    return 0
```

## Driver
```python
import re
import sys

class Bag:                                  # unrelated class with an add method
    def __init__(self): self.items = []
    def add(self, x): self.items.append(x)

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
s = OrderedSet([3, 1, 3, 2, 1])
s
list(s)
len(s)
2 in s
s.add(0)
s.add(3)
s
s.index(2)
s.index(9)
s.discard(1)
s.discard(42)
s
t = OrderedSet([2, 5, 3])
s | t
s & t
s - t
s ^ t
OrderedSet([3, 2]) <= s
s == OrderedSet([0, 2, 3])
s == OrderedSet([3, 2, 0])
s.isdisjoint([7, 8])
OrderedSet()
add_all(s, [9, 9, 4])
s
b = Bag()
add_all(b, "xy")
b.items
isinstance(b, SupportsAdd)
isinstance(42, SupportsAdd)
---
s -> OrderedSet([3, 1, 2])
list(s) -> [3, 1, 2]
len(s) -> 3
2 in s -> True
s.add(0) -> None
s.add(3) -> None
s -> OrderedSet([3, 1, 2, 0])
s.index(2) -> 2
s.index(9) -> ValueError: 9 is not in OrderedSet
s.discard(1) -> None
s.discard(42) -> None
s -> OrderedSet([3, 2, 0])
s | t -> OrderedSet([3, 2, 0, 5])
s & t -> OrderedSet([2, 3])
s - t -> OrderedSet([0])
s ^ t -> OrderedSet([0, 5])
OrderedSet([3, 2]) <= s -> True
s == OrderedSet([0, 2, 3]) -> True
s == OrderedSet([3, 2, 0]) -> True
s.isdisjoint([7, 8]) -> True
OrderedSet() -> OrderedSet()
add_all(s, [9, 9, 4]) -> 3
s -> OrderedSet([3, 2, 0, 9, 4])
add_all(b, "xy") -> 2
b.items -> ['x', 'y']
isinstance(b, SupportsAdd) -> True
isinstance(42, SupportsAdd) -> False
=== hidden
u = OrderedSet("mississippi")
u
u.pop()
u
u.remove("z")
u.__ior__("spam")
u
sorted(OrderedSet([5, 1]) | {9})
OrderedSet(range(5)) - range(0, 5, 2)
issubclass(OrderedSet, __import__("collections.abc").abc.Set)
x = set()
add_all(x, [1, 2, 2])
isinstance(x, SupportsAdd)
s2 = OrderedSet(range(100000))
s2.index(99999)
len(s2 & OrderedSet(range(50000, 150000)))
u.clear()
u
---
u -> OrderedSet(['m', 'i', 's', 'p'])
u.pop() -> 'm'
u -> OrderedSet(['i', 's', 'p'])
u.remove("z") -> KeyError: 'z'
u.__ior__("spam") -> OrderedSet(['i', 's', 'p', 'a', 'm'])
u -> OrderedSet(['i', 's', 'p', 'a', 'm'])
sorted(OrderedSet([5, 1]) | {9}) -> [1, 5, 9]
OrderedSet(range(5)) - range(0, 5, 2) -> OrderedSet([1, 3])
issubclass(OrderedSet, __import__("collections.abc").abc.Set) -> True
add_all(x, [1, 2, 2]) -> 3
isinstance(x, SupportsAdd) -> True
s2.index(99999) -> 99999
len(s2 & OrderedSet(range(50000, 150000))) -> 50000
u.clear() -> None
u -> OrderedSet()

## Hints
- Store the elements as keys of a plain `dict`. Dicts keep insertion order (3.7+) and give O(1) membership: `self._d = dict.fromkeys(iterable)`.
- `__iter__` is `iter(self._d)`, `add` is `self._d[x] = None`, `discard` is `self._d.pop(x, None)`.
- For an O(1) `index`, keep a separate position map that you rebuild lazily, or accept O(n) with `list(self._d).index(x)` (the tests allow O(n) for `index`).
- `pop()` from `MutableSet` removes an **arbitrary** element: the first one your `__iter__` yields.
- In `__repr__`, use `type(self).__name__` so subclasses print their own name.

## Solution
```python
from collections.abc import MutableSet
from typing import Protocol, runtime_checkable

class OrderedSet(MutableSet):
    __slots__ = ("_d",)

    def __init__(self, iterable=()):
        self._d = dict.fromkeys(iterable)

    def __contains__(self, x):
        return x in self._d

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    def add(self, x):
        self._d[x] = None

    def discard(self, x):
        self._d.pop(x, None)

    def index(self, x):
        for i, y in enumerate(self._d):
            if y == x:
                return i
        raise ValueError(f"{x!r} is not in OrderedSet")

    def __repr__(self):
        name = type(self).__name__
        return f"{name}({list(self._d)})" if self._d else f"{name}()"


@runtime_checkable
class SupportsAdd(Protocol):
    def add(self, x) -> None: ...


def add_all(target: SupportsAdd, items) -> int:
    n = 0
    for item in items:
        target.add(item)
        n += 1
    return n
```

- **The ABC does the heavy lifting.** Five small methods buy the full set algebra, comparisons, `remove`/`pop`/`clear` and the in-place operators, all correct and consistent. `MutableSet` also makes `isinstance(s, collections.abc.Set)` true, so other code recognises it as a set.
- **Equality** comes from `Set.__eq__`, which compares as sets (order-insensitive), matching the builtin `set` semantics: `OrderedSet([0, 2, 3]) == OrderedSet([3, 2, 0])` is `True`.
- **A dict as an ordered hash set** is the idiomatic modern Python trick (and how `OrderedSet` recipes and pandas' `Index` dedup work).
- **The Protocol** accepts *anything* with an `add` method (`OrderedSet`, builtin `set`, the unrelated `Bag`) without inheritance, and the type checker verifies the calls. `@runtime_checkable` makes the shallow `isinstance` check work (it checks only that `add` exists).

