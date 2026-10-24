---
id: py-weak-sprite-cache
title: Slotted Objects and a Weak-Reference Cache
difficulty: Medium
order: 1
tags: __slots__, weakref, WeakValueDictionary, memory, gc
---
## Statement
A simulation creates millions of tiny `Particle` objects and loads expensive `Mesh` resources shared by many entities. Implement:

1. **`Particle`** with `__slots__ = ("x", "y", "vx", "vy")`. `step(dt)` advances the position, and `__repr__` gives `Particle(x=…, y=…)` with 2 decimals. Instances must have **no `__dict__`**, and assigning an unknown attribute must raise `AttributeError`.
2. **`Mesh`**: a slotted class with `name` and `vertices` attributes, which must still be **weak-referenceable** (hint: `"__weakref__"`). A class-level counter `Mesh.loads` counts constructions.
3. **`MeshCache`**: `get(name)` returns the cached `Mesh` if it's still alive somewhere, otherwise "loads" a new `Mesh(name, vertices=len(name) * 100)`. The cache must **not keep meshes alive**: use `weakref.WeakValueDictionary`. `alive()` returns the sorted list of names currently cached.

The driver deletes references and checks that meshes disappear from the cache (CPython frees an object as soon as its reference count drops to zero, so this is deterministic).

## Starter
```python
import weakref

class Particle:
    def __init__(self, x, y, vx, vy):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy

class Mesh:
    loads = 0
    def __init__(self, name, vertices):
        self.name, self.vertices = name, vertices

class MeshCache:
    def __init__(self):
        self._cache = {}
    def get(self, name):
        if name not in self._cache:
            self._cache[name] = Mesh(name, len(name) * 100)
        return self._cache[name]
    def alive(self):
        return sorted(self._cache)
```

## Driver
```python
import re
import sys
import gc

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
p = Particle(0.0, 0.0, 1.0, 2.0)
p.step(0.5)
p
hasattr(p, "__dict__")
p.z = 1
cache = MeshCache()
a = cache.get("rover")
b = cache.get("rover")
a is b
Mesh.loads
cache.alive()
a = None
cache.alive()
b = None
cache.alive()
c = cache.get("rover")
Mesh.loads
c.vertices
---
p.step(0.5) -> None
p -> Particle(x=0.50, y=1.00)
hasattr(p, "__dict__") -> False
p.z = 1 -> AttributeError: 'Particle' object has no attribute 'z' and no __dict__ for setting new attributes
a is b -> True
Mesh.loads -> 1
cache.alive() -> ['rover']
cache.alive() -> ['rover']
cache.alive() -> []
Mesh.loads -> 2
c.vertices -> 500
=== hidden
ps = [Particle(i, 0, 1, 1) for i in range(1000)]
[q.step(2) for q in ps][:1]
ps[999]
Particle.__slots__
cache = MeshCache()
keep = [cache.get(n) for n in ("arm", "wheel", "arm", "lidar")]
Mesh.loads
cache.alive()
del_me = keep.pop()
del_me = None
cache.alive()
keep = []
cache.alive()
hasattr(Mesh("m", 1), "__dict__")
import_weakref = __import__("weakref").ref(cache.get("solo"))
import_weakref() is None
x = cache.get("solo2")
__import__("weakref").ref(x)() is x
Mesh.loads
---
[q.step(2) for q in ps][:1] -> [None]
ps[999] -> Particle(x=1001.00, y=2.00)
Particle.__slots__ -> ('x', 'y', 'vx', 'vy')
Mesh.loads -> 3
cache.alive() -> ['arm', 'lidar', 'wheel']
cache.alive() -> ['arm', 'wheel']
cache.alive() -> []
hasattr(Mesh("m", 1), "__dict__") -> False
import_weakref() is None -> True
__import__("weakref").ref(x)() is x -> True
Mesh.loads -> 6

## Hints
- `__slots__ = ("name", "vertices", "__weakref__")`. Without `__weakref__`, `weakref.ref(mesh)` raises `TypeError: cannot create weak reference to 'Mesh' object`.
- `self._cache = weakref.WeakValueDictionary()`. Entries vanish automatically when the last strong reference to the value disappears.
- In `get`, look up the entry **and keep a local strong reference** before checking it, so the object can't vanish between the check and the return: `m = self._cache.get(name)`, and `if m is None: m = self._cache[name] = Mesh(...)`.
- A class attribute like `loads` is fine alongside `__slots__`, as long as its name isn't one of the slots.

## Solution
```python
import weakref

class Particle:
    __slots__ = ("x", "y", "vx", "vy")

    def __init__(self, x, y, vx, vy):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy

    def step(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def __repr__(self):
        return f"Particle(x={self.x:.2f}, y={self.y:.2f})"


class Mesh:
    __slots__ = ("name", "vertices", "__weakref__")
    loads = 0

    def __init__(self, name, vertices):
        self.name = name
        self.vertices = vertices
        Mesh.loads += 1


class MeshCache:
    def __init__(self):
        self._cache = weakref.WeakValueDictionary()

    def get(self, name):
        mesh = self._cache.get(name)            # a local strong reference while we decide
        if mesh is None:
            mesh = Mesh(name, vertices=len(name) * 100)
            self._cache[name] = mesh
        return mesh

    def alive(self):
        return sorted(self._cache.keys())
```

- **`__slots__`** removes the per-instance `__dict__`, which is the dominant memory cost for small objects (a slotted `Particle` is a fraction of the size of a regular one), and blocks accidental new attributes.
- **`"__weakref__"` in the slots** re-adds the hidden pointer slot that weak references need. Slotted classes drop it by default.
- **`WeakValueDictionary`** implements a cache that *observes* rather than *owns*: a mesh stays cached exactly as long as some entity uses it, and once the last user lets go, it's freed and removed from the cache automatically. With a normal dict (the starter), every mesh ever loaded would stay in memory forever, which is a classic leak in long-running simulations and games.

