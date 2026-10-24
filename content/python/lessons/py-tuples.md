# Tuples

A tuple is an **immutable, ordered sequence**. It's often described as "a list you can't change", which is true but misses the point. Lists are for **collections of similar things** whose size varies (a list of scores). Tuples are for **fixed-size records whose positions mean something**, like a point `(x, y)`, an RGB colour `(r, g, b)` or a database row `(id, name, age)`. Because tuples are immutable, they can be dictionary keys and set members, can be shared safely, and are a little smaller and faster than lists.

## 1. Creating tuples

```python
point = (3, 4)
rgb = (255, 128, 0)
single = (5,)            # one-element tuple: the COMMA makes it a tuple
empty = ()
packed = 1, 2, 3         # parentheses are optional: commas make tuples
from_list = tuple([1, 2])
chars = tuple("abc")     # ('a', 'b', 'c')
```

> [!DANGER]
> `(5)` is just the integer 5 in grouping parentheses. A one-element tuple needs a **trailing comma**: `(5,)` or `5,`. The comma, not the parentheses, is what makes a tuple. (The only exception is the empty tuple `()`.)

```python
print(type((5)), type((5,)))    # <class 'int'> <class 'tuple'>
```

## 2. Sequence operations: like lists, minus mutation

```python
t = (10, 20, 30, 20)
print(t[0], t[-1], t[1:3])      # 10 20 (20, 30)
print(len(t), 20 in t)          # 4 True
print(t.count(20), t.index(30)) # 2 2     (the only two methods)
print(t + (40,), t * 2)         # new tuples
for x in t:
    print(x, end=" ")
```

No `append`, `remove`, `sort` or item assignment:

```python
# t[0] = 99     → TypeError: 'tuple' object does not support item assignment
t = t + (40,)   # "changing" a tuple = building a new one and rebinding
```

## 3. Immutable, but not necessarily frozen all the way down

A tuple's **slots** can't be rebound, but if a slot holds a **mutable** object, that object can still change:

```python
t = ([1], 2)
t[0].append(9)       # allowed: we mutate the list, not the tuple's slot
print(t)             # ([1, 9], 2)
```

<div class="figure">
<svg viewBox="0 0 520 150" width="520" xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace, monospace" font-size="13">
  <defs><marker id="ta" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="currentColor"/></marker></defs>
  <rect x="20" y="40" width="160" height="50" rx="6" fill="none" stroke="#2f81f7" stroke-width="2"/>
  <line x1="100" y1="40" x2="100" y2="90" stroke="#2f81f7" stroke-width="2"/>
  <text x="30" y="30" fill="#2f81f7" font-size="12">tuple (slots fixed)</text>
  <text x="50" y="70" fill="currentColor">[0]</text><text x="128" y="70" fill="currentColor">[1]</text>
  <rect x="270" y="20" width="130" height="40" rx="6" fill="none" stroke="#3fb950" stroke-width="2"/>
  <text x="285" y="45" fill="currentColor">list [1, 9]</text>
  <text x="410" y="45" fill="#3fb950" font-size="11" font-family="sans-serif">mutable: can change</text>
  <circle cx="320" cy="115" r="18" fill="none" stroke="currentColor" stroke-opacity=".6"/><text x="315" y="120" fill="currentColor">2</text>
  <line x1="60" y1="78" x2="266" y2="42" stroke="currentColor" marker-end="url(#ta)"/>
  <line x1="140" y1="78" x2="300" y2="112" stroke="currentColor" marker-end="url(#ta)"/>
</svg>
<figcaption>The tuple's references can't be rebound, but the list it points to is still mutable.</figcaption>
</div>

That's why such a tuple is **not hashable**:

```python
hash((1, 2))          # fine
hash(([1], 2))        # TypeError: unhashable type: 'list'
```

> [!KEY]
> A tuple is hashable **only if all of its elements are hashable**. Only hashable tuples can be dict keys or set members.

## 4. Tuples as dictionary keys and set members

This is the killer feature. Coordinates, pairs and composite keys:

```python
grid_labels = {(0, 0): "origin", (2, 3): "treasure"}
print(grid_labels[(2, 3)])        # treasure

visited = set()
visited.add((1, 2))               # BFS on a grid stores (row, col) tuples
print((1, 2) in visited)          # True

# a list can't do this:
# {[0, 0]: "x"}  → TypeError: unhashable type: 'list'
```

## 5. Packing and unpacking

**Packing**: listing values with commas builds a tuple. **Unpacking**: assigning a tuple to several names splits it.

```python
point = 3, 4          # packing
x, y = point          # unpacking
a, b = b, a           # swap = pack the right side, unpack into the left

def min_max(xs):
    return min(xs), max(xs)     # "returning several values" = returning ONE tuple
lo, hi = min_max([3, 9, 1])

first, *rest = (1, 2, 3, 4)     # star unpacking: first=1, rest=[2, 3, 4] (a list!)
```

The number of names must match the length, or you get `ValueError: too many values to unpack`. The Unpacking lesson covers the full rules.

### Unpacking in loops

```python
pairs = [("Ada", 36), ("Linus", 54)]
for name, age in pairs:
    print(f"{name} is {age}")

for i, (name, age) in enumerate(pairs):   # nested unpacking
    print(i, name)
```

## 6. Comparison and sorting

Tuples compare **lexicographically**, element by element. This makes them perfect **multi-key sort keys**:

```python
print((1, 2) < (1, 3))           # True
print((2,) > (1, 9, 9))          # True: decided at index 0
print(sorted([(2, "b"), (1, "z"), (2, "a")]))   # [(1, 'z'), (2, 'a'), (2, 'b')]

students = [("Ada", 90), ("Bob", 85), ("Cy", 90)]
# sort by score descending, then name ascending:
print(sorted(students, key=lambda s: (-s[1], s[0])))
```

```output
[('Ada', 90), ('Cy', 90), ('Bob', 85)]
```

## 7. Named tuples: tuples with field names

`point[0]` is cryptic. `collections.namedtuple` gives positions names while staying a tuple (immutable, hashable, unpackable):

```python
from collections import namedtuple
Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(p, p.x, p[1])            # Point(x=3, y=4) 3 4
x, y = p                       # still unpacks
q = p._replace(x=9)            # "modify" = new tuple: Point(x=9, y=4)
print(p._asdict())             # {'x': 3, 'y': 4}
```

The typed modern form is `typing.NamedTuple`:

```python
from typing import NamedTuple
class Point(NamedTuple):
    x: float
    y: float = 0.0
```

For mutable records with many fields, use a **dataclass** (its own lesson).

## 8. Why use a tuple instead of a list?

| Reason | Detail |
|---|---|
| **Intent** | Signals a fixed-structure record, not a growable collection |
| **Hashable** | Can be a dict key or set element (if its elements are hashable) |
| **Safety** | Can't be modified by accident when passed around |
| **Memory/speed** | Smaller (no spare capacity), slightly faster to create; constant tuples are built once at compile time |

```python
import sys
print(sys.getsizeof((1, 2, 3)), sys.getsizeof([1, 2, 3]))   # 72 88 on CPython 3.14
```

## 9. Exam-ready answers

> [!EXAM]
> **Tuples.** A tuple is an immutable ordered sequence of objects, written with commas and usually enclosed in parentheses; a one-element tuple requires a trailing comma, `(x,)`. Tuples support indexing, slicing, concatenation, repetition, membership tests, iteration, and the methods `count` and `index`, but no element assignment, insertion or deletion. A tuple is hashable when all of its elements are hashable, so it can be used as a dictionary key or set element. Tuples are typically used for fixed-size heterogeneous records and for returning multiple values from a function.

> [!EXAM]
> **List vs tuple.** Lists are mutable, support in-place modification (`append`, `remove`, `sort`), are unhashable, and are used for homogeneous collections of varying length. Tuples are immutable, hashable when their contents are, slightly more memory-efficient, and used for fixed collections whose positions carry meaning. Both are ordered sequences supporting indexing and slicing.

## 10. Cheat sheet

| Need | Code |
|---|---|
| one-element tuple | `(x,)` |
| return several values | `return a, b` → `x, y = f()` |
| swap | `a, b = b, a` |
| composite dict key | `d[(row, col)] = v` |
| multi-key sort | `key=lambda r: (r.score, r.name)` |
| descending + ascending | `key=lambda r: (-r.score, r.name)` |
| record with names | `namedtuple("P", "x y")` |
| "append" | `t = t + (x,)` (new tuple) |

> [!INTERVIEW]
> **"Can a tuple be modified?"** Its slots can't be rebound, so there's no item assignment or `append`. But if a slot references a mutable object, that object can change. The puzzle `t = ([],); t[0] += [1]` mutates the list **and then** raises `TypeError`. `+=` first extends the list in place, then tries to store the result back into the tuple slot, which fails. Afterwards `t` is `([1],)`.
