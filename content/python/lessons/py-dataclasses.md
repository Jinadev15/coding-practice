# Dataclasses

Classes that mainly **hold data** need the same boilerplate every time: `__init__` assigning each field, a readable `__repr__`, `__eq__` comparing fields, maybe ordering and hashing. The `@dataclass` decorator (Python 3.7+) **generates all of it from type-annotated class attributes**. Dataclasses are the standard way to model records, configuration objects, messages, poses, ML experiment configs and DTOs in modern Python, and they show you how decorators can write code for you.

## 1. The basics

```python
from dataclasses import dataclass

@dataclass
class Pose:
    x: float
    y: float
    theta: float = 0.0           # fields with defaults must come after fields without

p = Pose(1.0, 2.0)
print(p)                         # Pose(x=1.0, y=2.0, theta=0.0): generated __repr__
print(p == Pose(1.0, 2.0, 0.0))  # True: generated __eq__ compares fields in order
p.x = 5.0                        # mutable by default
```

Generated for you: `__init__(self, x, y, theta=0.0)`, `__repr__` and `__eq__`. The annotations define the fields, **in order**. Type hints aren't enforced at run time (`Pose("a", None)` works). Use validation in `__post_init__`, or pydantic, if you need checking.

## 2. Decorator options

| Option | Effect |
|---|---|
| `order=True` | generates `<`, `<=`, `>`, `>=` comparing fields as a tuple, in order |
| `frozen=True` | assigning to fields raises `FrozenInstanceError`; the instance becomes hashable |
| `slots=True` (3.10+) | generates `__slots__`: less memory, faster attribute access, no new attributes |
| `kw_only=True` (3.10+) | every field must be passed by keyword |
| `eq=False` | keep identity-based `==` |

```python
@dataclass(order=True)
class Version:
    major: int
    minor: int = 0
Version(1, 2) < Version(2, 0)          # True

@dataclass(frozen=True, slots=True)
class GridCell:
    row: int
    col: int
visited = {GridCell(0, 0), GridCell(0, 1)}    # hashable: usable in sets and as dict keys
c = GridCell(0, 0)
# c.row = 3                            # FrozenInstanceError: cannot assign to field 'row'
```

> [!KEY]
> Hashing rules: a plain `@dataclass` (with `eq=True`) sets `__hash__ = None`, so instances are **unhashable**, because mutable objects that compare by value mustn't be dict keys. `frozen=True` (with `eq=True`) generates a field-based `__hash__`. Use frozen dataclasses as keys and set members (grid cells, graph nodes, cache keys).

## 3. Mutable defaults and `field()`

```python
@dataclass
class Bad:
    items: list = []
# ValueError: mutable default <class 'list'> for field items is not allowed: use default_factory
```

Dataclasses refuse the classic shared-mutable-default bug. Use `field(default_factory=...)`:

```python
from dataclasses import dataclass, field

@dataclass
class Robot:
    name: str
    sensors: list[str] = field(default_factory=list)       # a NEW list per instance
    log: dict[str, float] = field(default_factory=dict, repr=False)   # hidden from repr
    _id: int = field(init=False, default=0, compare=False) # not an __init__ parameter
```

`field()` options: `default`, `default_factory`, `init`, `repr`, `compare`, `hash`, `kw_only`, `metadata`.

## 4. `__post_init__`: validation and derived fields

The generated `__init__` calls `__post_init__` after assigning fields:

```python
@dataclass
class Order:
    items: list[int] = field(default_factory=list)
    total: int = field(init=False, default=0)

    def __post_init__(self):
        if any(x < 0 for x in self.items):
            raise ValueError("negative item price")
        self.total = sum(self.items)

print(Order([1, 2, 3]))          # Order(items=[1, 2, 3], total=6)
```

For a **frozen** class, assign derived fields in `__post_init__` with `object.__setattr__(self, "total", ...)`, since normal assignment is blocked.

## 5. Utilities

```python
from dataclasses import asdict, astuple, replace, fields

asdict(p)            # {'x': 5.0, 'y': 2.0, 'theta': 0.0}: recursive, good for JSON
astuple(p)           # (5.0, 2.0, 0.0)
replace(p, x=0.0)    # a NEW instance with some fields changed (essential for frozen classes)
[f.name for f in fields(Pose)]    # ['x', 'y', 'theta']: introspection
```

## 6. Inheritance and field order

```python
@dataclass
class Base:
    id: int
    tag: str = "x"

@dataclass
class Child(Base):
    extra: int          # TypeError: non-default argument 'extra' follows default argument 'tag'
```

Fields accumulate base-first, so the generated `__init__` would need a non-default parameter after a default one. Fix it with `kw_only=True` on the child (or on that field), or give `extra` a default.

## 7. Choosing a record type

| Type | Mutable | Hashable | Methods and defaults | Memory | Best for |
|---|---|---|---|---|---|
| `tuple` | no | yes | no | smallest | quick multi-return |
| `namedtuple` / `NamedTuple` | no | yes | limited | small | immutable records, tuple compatibility |
| `@dataclass` | yes (or frozen) | if frozen | full class | normal (small with slots) | domain objects, configs |
| `TypedDict` | (it's a dict) | no | no | dict | typing JSON-like dicts |
| pydantic `BaseModel` | yes | optional | validation + parsing | larger | untrusted input, APIs |

## 8. Exam-ready answers

> [!EXAM]
> **Dataclasses.** The `@dataclass` decorator from the `dataclasses` module generates special methods for classes that primarily store data, based on class attributes declared with type annotations. By default it generates `__init__`, `__repr__` and `__eq__`; `order=True` adds ordering comparisons, `frozen=True` makes instances immutable and hashable, and `slots=True` adds `__slots__`. Mutable default values must be supplied through `field(default_factory=...)` so that each instance gets its own object. `__post_init__` is called after the generated initialiser for validation or computing derived fields, and helper functions such as `asdict`, `astuple`, `replace` and `fields` support conversion and introspection. Type annotations define fields but are not enforced at run time.

## 9. Cheat sheet

| Need | Code |
|---|---|
| a record | `@dataclass class P: x: int; y: int = 0` |
| sortable | `@dataclass(order=True)` |
| immutable + hashable | `@dataclass(frozen=True)` |
| low memory | `@dataclass(slots=True)` |
| list/dict default | `field(default_factory=list)` |
| computed field | `field(init=False)` + `__post_init__` |
| validation | raise in `__post_init__` |
| copy with changes | `replace(obj, x=1)` |
| to a dict/JSON | `asdict(obj)` |

> [!INTERVIEW]
> **"Why can't a regular dataclass instance be used as a dict key, and how do you fix it?"** With `eq=True` (the default), the dataclass defines value equality, and since its fields are mutable, Python sets `__hash__` to `None`. A key whose hash could change after insertion would corrupt the dict. Making it `frozen=True` generates a hash from the fields and blocks mutation, so equal objects keep equal hashes. Alternatively, `unsafe_hash=True` forces a hash on a mutable class (risky), or `eq=False` falls back to identity hashing.
