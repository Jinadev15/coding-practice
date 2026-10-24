# Metaclasses and Class Creation

In Python, **classes are objects too**, created at run time by executing the `class` statement. The object that creates a class is its **metaclass**, `type` by default. Metaclasses let you customise class creation itself: registering plugins, validating class definitions, adding methods automatically, or building DSLs like Django models and SQLAlchemy's declarative base. Tim Peters' famous warning applies ("Metaclasses are deeper magic than 99% of users should ever worry about"), so this lesson also teaches the simpler tools that usually suffice: **`__init_subclass__`** and **class decorators**.

## 1. Classes are instances of `type`

```python
class A: pass
type(A)              # <class 'type'>: A is an instance of type
type(type)           # <class 'type'>: type is its own metaclass
isinstance(A, type)  # True

# The class statement is (roughly) sugar for a call to type(name, bases, namespace):
B = type("B", (A,), {"greet": lambda self: "hi", "x": 1})
B().greet()          # 'hi'
```

What `class C(Base): body` does:
1. Determine the metaclass (from `metaclass=`, or from the bases, defaulting to `type`).
2. Prepare a namespace (`metaclass.__prepare__`, normally a dict).
3. **Execute the class body** in that namespace. `def`s become functions, assignments become entries.
4. Call `metaclass(name, bases, namespace)`, which runs `__new__`, then `__init__`.
5. Bind the resulting class object to the name `C`.

```mermaid
flowchart LR
    S["class statement"] --> P["metaclass.__prepare__"] --> E["execute body into namespace"] --> N["metaclass.__new__(mcls, name, bases, ns)"] --> I["metaclass.__init__"] --> C["class object bound to name"]
```

## 2. `__new__` vs `__init__` (for any class)

| | `__new__(cls, ...)` | `__init__(self, ...)` |
|---|---|---|
| Role | **creates** and returns the instance | **initialises** an existing instance |
| Kind | a static method (implicitly) | an instance method |
| Returns | the new object | `None` |
| Needed for | immutable types (subclassing `int`, `str`, `tuple`), singletons, caching | almost everything else |

```python
class Celsius(float):
    def __new__(cls, value):
        if value < -273.15:
            raise ValueError("below absolute zero")
        return super().__new__(cls, value)    # floats are immutable: the value must be set in __new__
```

## 3. Writing a metaclass

```python
class PluginMeta(type):
    registry: dict[str, type] = {}

    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace)
        if bases:                                    # skip the abstract base itself
            if "run" not in namespace:
                raise TypeError(f"plugin {name} must define run()")
            mcls.registry[name.lower()] = cls
        return cls

class Plugin(metaclass=PluginMeta):
    pass

class Lidar(Plugin):
    def run(self): return "scanning"

PluginMeta.registry                    # {'lidar': <class 'Lidar'>}
# class Broken(Plugin): pass          # TypeError at CLASS DEFINITION time
```

The check runs when the class is **defined** (at import time), not when it's used. That's a powerful way to catch mistakes early.

> [!WARNING]
> Metaclass conflicts: a class can only have one metaclass. Inheriting from two bases with unrelated metaclasses raises `TypeError: metaclass conflict`. Metaclasses also propagate to every subclass. This is why the simpler tools below are preferred.

## 4. `__init_subclass__`: the 90% solution (3.6+)

A hook on the **base class** that runs whenever a subclass is created, with no metaclass needed:

```python
class Plugin:
    registry = {}
    def __init_subclass__(cls, /, key=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if key is None:
            raise TypeError(f"{cls.__name__} needs key=")
        cls.key = key
        Plugin.registry[key] = cls

class Lidar(Plugin, key="lidar"): ...
class Camera(Plugin, key="camera"): ...
Plugin.registry          # {'lidar': <class 'Lidar'>, 'camera': <class 'Camera'>}
```

Class keyword arguments (`key="lidar"`) are passed straight to `__init_subclass__`. This covers registries, validation, and automatic attribute setup.

## 5. Class decorators

A function that receives the finished class and returns it (possibly modified):

```python
def register(cls):
    REGISTRY[cls.__name__] = cls
    return cls

def add_repr(cls):
    fields = list(cls.__annotations__)
    def __repr__(self):
        return f"{cls.__name__}(" + ", ".join(f"{f}={getattr(self, f)!r}" for f in fields) + ")"
    cls.__repr__ = __repr__
    return cls

@register
@add_repr
class Pose:
    x: float
    y: float
    def __init__(self, x, y): self.x, self.y = x, y
```

`@dataclass` is a class decorator. It reads `__annotations__` and generates methods.

| Tool | Runs | Affects subclasses? | Use for |
|---|---|---|---|
| class decorator | once, on the decorated class | no (unless re-applied) | adding or generating methods, registration |
| `__init_subclass__` | for every subclass | yes | registries, validation of subclasses |
| metaclass | for the class and every subclass, at every stage of creation | yes | `__prepare__` tricks, class-level operators, DSLs (ORMs, enums) |

> [!TIP]
> `enum.Enum` uses a metaclass (`EnumType`) because it needs to change how the class body's assignments are interpreted (turning them into members) and to make the class itself iterable (`for c in Color`). That requires metaclass-level methods: `__iter__` defined on the metaclass makes the **class** iterable.

## 6. Exam-ready answers

> [!EXAM]
> **Metaclasses.** In Python, classes are objects created at run time, and a metaclass is the class of a class: the callable that constructs class objects, `type` by default. When a class statement executes, the body runs in a namespace prepared by the metaclass, and the metaclass is then called with the class name, base classes and namespace; overriding its `__new__` or `__init__` customises class creation, for example to register, validate or modify classes. `__new__` creates an instance and is required for customising immutable types, while `__init__` initialises an existing instance. Simpler alternatives are `__init_subclass__`, a hook on a base class invoked for each new subclass, and class decorators, which receive and may modify a finished class. Metaclasses are used by frameworks such as ORMs and the `enum` module.

## 7. Cheat sheet

| Need | Tool |
|---|---|
| create a class dynamically | `type(name, bases, dict)` |
| customise instance creation | `__new__` |
| a registry of subclasses | `__init_subclass__` |
| validate subclasses at definition time | `__init_subclass__` (or a metaclass) |
| modify one class | a class decorator |
| make a class iterable or subscriptable | a metaclass method, or `__class_getitem__` |
| custom class-body namespace | `metaclass.__prepare__` |

> [!INTERVIEW]
> **"What's the difference between `__new__` and `__init__`, and when must you use `__new__`?"** `__new__` is called first with the class and constructs and returns the instance. `__init__` then receives that instance and initialises it, returning `None`. You need `__new__` when the instance's value must be fixed at creation, which means subclassing immutable built-ins like `int`, `str` and `tuple`, and when controlling *whether* a new object is created at all: singletons, interning and caching, or returning an instance of a different class. If `__new__` returns an object that isn't an instance of the class, `__init__` isn't called.
