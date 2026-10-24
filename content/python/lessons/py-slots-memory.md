# __slots__ and Object Memory

Every ordinary Python object carries a **`__dict__`**, a hash table holding its attributes. That's flexible (you can add attributes at any time) but costly: a dict per object adds about 100+ bytes. When you create **millions** of small objects (points in a cloud, nodes in a graph, particles, events), that overhead dominates memory and hurts cache performance. **`__slots__`** replaces the per-instance dict with fixed storage. This lesson also covers measuring memory and `weakref` for caches that don't keep objects alive.

## 1. The cost of `__dict__`

```python
import sys
class D:                       # normal class
    def __init__(self, x, y): self.x, self.y = x, y
class S:                       # slotted class
    __slots__ = ("x", "y")
    def __init__(self, x, y): self.x, self.y = x, y

d, s = D(1, 2), S(1, 2)
sys.getsizeof(s)                                    # 48 bytes
sys.getsizeof(d) + sys.getsizeof(d.__dict__)        # several times larger (the dict dominates)
```

> [!KEY]
> `sys.getsizeof` is **shallow**: it measures the object itself, not the objects it references (the dict, list elements, strings). For real totals, use `tracemalloc` (allocations by line) or third-party tools like `pympler.asizeof`.

## 2. How `__slots__` works

```python
class Point:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(1, 2)
p.z = 3        # AttributeError: 'Point' object has no attribute 'z' and no __dict__ for setting new attributes
hasattr(p, "__dict__")    # False
```

At class creation, Python allocates fixed slots in the instance layout and creates a **member descriptor** on the class for each name (`Point.x` is a `member_descriptor`, a data descriptor, from the Descriptors lesson). Attribute access goes straight to a fixed offset instead of a hash lookup.

| | Regular class | `__slots__` class |
|---|---|---|
| Memory per instance | object + dict | object only (much less) |
| Attribute access speed | dict lookup | fixed offset (slightly faster) |
| Add new attributes at run time | yes | **no** |
| `__weakref__` support | yes | only if `"__weakref__"` is listed in the slots |
| Class-level defaults for slot names | fine | conflict: `ValueError` |

## 3. Rules and gotchas

```python
class Base:
    __slots__ = ("id",)
class Child(Base):
    __slots__ = ("name",)        # only the NEW names; the parent's slots are inherited
class Loose(Base):
    pass                         # no __slots__: instances get a __dict__ again (savings lost)
```

- **Every class in the hierarchy** must define `__slots__` (even an empty `()`) to avoid a `__dict__`.
- Multiple inheritance from two bases that both have **non-empty** slots raises a layout conflict `TypeError`.
- You can't give a slot a class-level default value (`x = 0` alongside `__slots__ = ("x",)` raises `ValueError`). Set defaults in `__init__`.
- Pickling and `copy` work in modern Python. Code that relies on `obj.__dict__` (some serializers) won't.
- `@dataclass(slots=True)` (3.10+) generates slots for you, so it's the easiest way to get the benefit.

> [!TIP]
> Use slots for **many small, fixed-shape objects**: tree and graph nodes, geometric primitives, records in a simulation, ASTs. Don't bother for a handful of objects. The win is memory and locality at scale, not speed per access. For millions of *numeric* records, a NumPy structured array or columnar arrays (SoA) beat even slotted objects by 10×.

## 4. `weakref`: references that don't keep objects alive

A normal reference keeps an object alive (its reference count stays above zero). A **weak reference** refers to an object without owning it. When the last strong reference disappears, the object is collected and the weak reference returns `None`:

```python
import weakref

class Sensor:
    def __init__(self, name): self.name = name

s = Sensor("lidar")
r = weakref.ref(s)
r() is s          # True
del s             # the last strong reference is gone
r()               # None: the object was freed

cache = weakref.WeakValueDictionary()     # entries vanish automatically when their values die
```

Use them for **caches** that shouldn't extend lifetimes, for **observer lists** (a subject holding weak references to its listeners doesn't leak listeners that were otherwise discarded), and to **break reference cycles** in parent-child trees (child → parent as a weak reference).

## 5. Exam-ready answers

> [!EXAM]
> **`__slots__`.** Declaring `__slots__` in a class replaces the per-instance `__dict__` with a fixed set of attribute slots, implemented as member descriptors on the class. This reduces memory per instance substantially and slightly speeds up attribute access, but prevents adding attributes not listed in `__slots__`, disables weak references unless `__weakref__` is included, and requires every class in an inheritance chain to define `__slots__` for the savings to apply. `sys.getsizeof` reports only an object's own size, not that of referenced objects. Weak references (`weakref.ref`, `WeakValueDictionary`) refer to objects without increasing their reference counts, so they don't prevent garbage collection; they are used for caches, observer registries and breaking reference cycles.

## 6. Cheat sheet

| Need | Code |
|---|---|
| fixed attributes, low memory | `__slots__ = ("a", "b")` |
| a slotted dataclass | `@dataclass(slots=True)` |
| a slotted subclass | `__slots__ = ("new_attr",)` |
| allow weakrefs with slots | include `"__weakref__"` |
| shallow size | `sys.getsizeof(obj)` |
| allocation tracking | `tracemalloc.start()`, then snapshots |
| a non-owning reference | `weakref.ref(obj)` |
| a self-cleaning cache | `weakref.WeakValueDictionary()` |

> [!INTERVIEW]
> **"Your Python service creates 10 million small `Point` objects and runs out of memory. What do you do?"** First measure (`tracemalloc`) to confirm the Points dominate. Then remove the per-instance `__dict__` with `__slots__` (or `@dataclass(slots=True)`), which typically cuts per-object memory by more than half. If the data is numeric and processed in bulk, go further with a columnar representation: NumPy arrays of x and y (16 bytes per point instead of ~50+), which also enables vectorised computation. Also check for accidental retention, such as caches that never evict or reference cycles kept alive, and use `weakref` where ownership isn't intended.
