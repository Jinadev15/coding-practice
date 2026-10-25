# Structural Patterns in Python

Structural patterns compose objects into larger structures: adapting interfaces, adding behaviour, building trees, and controlling access. Python provides first-class tools that make several of them nearly free: **function and class decorators**, **duck typing** with `typing.Protocol`, `__getattr__` delegation, and context managers. This lesson covers Adapter, Decorator (the GoF pattern *and* Python's `@decorator` syntax, which are related but different), Composite, Facade, Proxy and Flyweight, with production-quality decorator implementations.

## 1. Adapter and duck typing

Python code depends on **behaviour**, not declared types. An adapter just needs the right methods:

```python
from typing import Protocol

class RangeSensor(Protocol):
    def range_m(self) -> float | None: ...

class VendorSonar:                          # third-party: centimetres, raises on error
    def get_distance_cm(self) -> int: ...

class SonarAdapter:
    def __init__(self, dev: VendorSonar): self._dev = dev
    def range_m(self) -> float | None:
        try:
            return self._dev.get_distance_cm() / 100
        except IOError:
            return None
```

`SonarAdapter` satisfies `RangeSensor` structurally, with no inheritance needed. A type checker (mypy, pyright) verifies the match statically. `@runtime_checkable` additionally allows `isinstance` checks against the protocol.

## 2. Python decorators

A **decorator** is a callable that takes a function and returns a replacement, applied with `@`. It's ideal for cross-cutting concerns like retries, caching, timing, logging, validation and authorisation:

```python
import functools, time

def retry(times: int = 3, exceptions: tuple[type[BaseException], ...] = (Exception,),
          delay: float = 0.1, sleep=time.sleep):
    def decorator(fn):
        @functools.wraps(fn)                          # keep __name__, __doc__, __wrapped__
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    if attempt == times - 1:
                        raise
                    sleep(delay * 2 ** attempt)
        return wrapper
    return decorator

@retry(times=5, exceptions=(ConnectionError,))
def fetch_map(): ...
```

There are three layers: the **factory** (`retry(...)` takes the options), the **decorator** (takes `fn`), and the **wrapper** (replaces `fn`). Without `functools.wraps`, the decorated function loses its name and docstring, and tools like pytest and Sphinx get confused.

> [!KEY]
> `@deco` on `def f` means exactly `f = deco(f)`. Stacked decorators apply **bottom-up**: in `@a` / `@b` / `def f`, the result is `f = a(b(f))`. Decorators run at **definition time**, and wrappers run at call time.

**Decorators with state** use closures or a class with `__call__`:

```python
def ttl_cache(seconds: float, clock=time.monotonic):
    def decorator(fn):
        store: dict = {}
        @functools.wraps(fn)
        def wrapper(*args):
            now = clock()
            hit = store.get(args)
            if hit is not None and now - hit[1] < seconds:
                return hit[0]
            value = fn(*args)
            store[args] = (value, now)
            return value
        wrapper.cache_clear = store.clear             # functions can carry attributes
        return wrapper
    return decorator
```

The standard library ships `functools.cache`, `lru_cache`, `cached_property`, `singledispatch`, `contextlib.contextmanager`, `dataclasses.dataclass` and `property`. **Class decorators** (like `@dataclass`) take and return a class.

## 3. The GoF Decorator (object wrapping)

GoF Decorator wraps an **object**, adding behaviour behind the same interface. Python's `__getattr__` makes forwarding the untouched methods automatic:

```python
class LoggingSensor:
    def __init__(self, inner, log): self._inner, self._log = inner, log
    def range_m(self):
        v = self._inner.range_m()
        self._log.append(v)
        return v
    def __getattr__(self, name):                  # called only for attributes not found normally
        return getattr(self._inner, name)         # delegate everything else
```

## 4. Composite

```python
from dataclasses import dataclass, field

@dataclass
class Part:
    name: str
    mass: float
    def total_mass(self) -> float: return self.mass
    def walk(self, depth=0):
        yield depth, self

@dataclass
class Assembly:
    name: str
    children: list = field(default_factory=list)
    def total_mass(self) -> float: return sum(c.total_mass() for c in self.children)
    def walk(self, depth=0):
        yield depth, self
        for c in self.children:
            yield from c.walk(depth + 1)          # recursive generators traverse trees elegantly
```

Generators with `yield from` make tree traversal lazy and composable. File-system trees, ASTs (`ast.walk`), URDF link trees and behaviour trees are all composites.

## 5. Facade

A facade module or class wraps a subsystem's complexity: `requests.get` is a facade over urllib3's connection pools, retries and encodings. In your own code, a `Robot` class offering `drive_to(x, y)` can hide localisation, planning and control objects. A package's `__init__.py` re-exporting a small public API is a facade too.

## 6. Proxy

Proxies control access: lazy loading, caching, access checks, remote calls. `__getattr__` makes a transparent lazy proxy short:

```python
class LazyProxy:
    def __init__(self, factory):
        object.__setattr__(self, "_factory", factory)
        object.__setattr__(self, "_obj", None)
    def _target(self):
        if self._obj is None:
            object.__setattr__(self, "_obj", self._factory())
        return self._obj
    def __getattr__(self, name):
        return getattr(self._target(), name)

big_map = LazyProxy(lambda: load_occupancy_grid("site.pgm"))   # loaded on first attribute access
```

Dunder methods (`len()`, `[]`, operators) are looked up on the **type**, not the instance, so `__getattr__` doesn't proxy them. Define them explicitly if they're needed. `weakref.proxy` gives non-owning references, and `unittest.mock` objects are proxies used for testing.

## 7. Flyweight

Share immutable state among many objects: `sys.intern` for strings, small-int caching in CPython, `functools.cache` on a constructor, `__slots__` to shrink per-instance memory. Example: one `TreeModel` shared by 100,000 trees that each store only `(x, y, scale)`, ideally as rows of a NumPy array, which is the ultimate flyweight.

> [!EXAM]
> **Explain Python decorators and how they relate to the GoF Decorator pattern.**
> A Python decorator is syntax for applying a higher-order function at definition time: `@d` above `def f` means `f = d(f)`. The decorator returns a wrapper (decorated with `functools.wraps` to keep the original metadata) that adds behaviour such as retries, caching, timing or validation around calls. Parameterised decorators are factories that return the decorator. The GoF Decorator pattern wraps an *object* to add behaviour while keeping its interface. Both add behaviour by wrapping without modifying the original and can be stacked, but Python decorators operate on functions and classes at definition time, while GoF decorators compose objects at runtime.

## Worked example: Adapter, Decorator and Facade together

You have a third-party sonar library with an awkward interface, and your code expects `read() -> metres`.

```python
class VendorSonar:                       # third-party: centimetres, odd method name
    def get_distance_cm(self) -> int:
        return 153

class SonarAdapter:                      # Adapter: converts the interface
    def __init__(self, sonar: VendorSonar):
        self._s = sonar
    def read(self) -> float:
        return self._s.get_distance_cm() / 100

class Clamped:                           # GoF Decorator: same interface, extra behaviour
    def __init__(self, sensor, lo: float, hi: float):
        self._s, self.lo, self.hi = sensor, lo, hi
    def read(self) -> float:
        return min(self.hi, max(self.lo, self._s.read()))

class ObstacleChecker:                   # Facade: one simple call over several parts
    def __init__(self, sensor, threshold: float):
        self.sensor, self.threshold = sensor, threshold
    def blocked(self) -> bool:
        return self.sensor.read() < self.threshold

sensor = Clamped(SonarAdapter(VendorSonar()), 0.2, 1.0)
print(sensor.read(), ObstacleChecker(sensor, 1.2).blocked())
```

```output
1.0 True
```

| Pattern | Changes the interface? | Purpose |
|---|---|---|
| Adapter | **yes**, to the one you expect | make incompatible code fit |
| Decorator | no, same interface | add behaviour by wrapping |
| Proxy | no, same interface | control access (lazy loading, caching, permissions) |
| Facade | gives a **new, simpler** one | hide a complicated subsystem |

## Common mistakes

- **Confusing Python's `@decorator` syntax with the GoF Decorator.** The first wraps *functions* at definition time; the second wraps *objects* at runtime. They share an idea, not a mechanism.
- **Adapters that leak the adaptee** (returning vendor types). Convert everything at the boundary.
- **A Facade that becomes a god object.** It should delegate, not reimplement the logic.

## Check your understanding

1. You wrap a slow API client so repeated calls return cached results. Which pattern is that?
2. Why can the decorators stack (`Clamped(Smoothed(sensor))`)?

<details><summary>Answers</summary>

1. A (caching) Proxy. It has the same interface and controls access to the real object.
2. Each wrapper has the same interface as the thing it wraps, so any wrapper can wrap any other.

</details>
