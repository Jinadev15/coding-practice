# Python Interview Deep Dive II: Internals

Senior Python interviews go beneath the syntax:
- how CPython executes code and manages memory
- the GIL and its removal (free-threaded 3.13+)
- the attribute-lookup machinery: descriptors, `__getattribute__` and the MRO
- metaclasses and class creation
- performance internals

These explain behaviour that otherwise looks magical, and they're the tools behind dataclasses, ORMs, pydantic and properties.

## 1. How CPython runs code

Source code is compiled to **bytecode** (cached in `__pycache__/*.pyc`), which a stack-based virtual machine loop executes. Inspect it with `dis.dis(func)`. Since 3.11, the **specialising adaptive interpreter** (PEP 659) rewrites hot instructions into type-specialised versions (`BINARY_OP_ADD_INT`, `LOAD_ATTR_INSTANCE_VALUE`), which is the source of 3.11's big speed-up. 3.13 added an experimental JIT.

Every object is a C struct beginning with a **reference count** and a **type pointer**. `id(obj)` is its address in CPython.

## 2. Memory management

- **Reference counting** frees most objects immediately when their count reaches zero (deterministic `__del__` and file closing in CPython).
- A **cyclic garbage collector** finds unreachable reference cycles (`a.self = a`, parent ↔ child), using generations to scan young objects more often. `gc.collect()` forces a pass, and `gc.disable()` is sometimes used in latency-critical loops.
- **`weakref`** references don't increase the count. They're used for caches (`WeakValueDictionary`), observers and parent pointers.
- **pymalloc** serves small objects (≤ 512 bytes) from pools, avoiding `malloc` per object. Memory isn't always returned to the OS.
- Tools: `sys.getsizeof` (shallow size only), `tracemalloc` to find allocation sites, and `__slots__` to shrink instances.

## 3. The GIL and free threading

The **Global Interpreter Lock** lets only one thread execute Python bytecode at a time in standard CPython. It makes reference counting and the interpreter's internals thread-safe cheaply.
- **Threads** still help for **I/O-bound** work (the GIL is released during blocking I/O and in many C extensions such as NumPy and hashlib).
- **CPU-bound** pure-Python code doesn't speed up with threads. Use `multiprocessing` or `concurrent.futures.ProcessPoolExecutor`, vectorised NumPy, or C/Cython/Rust extensions.
- **Free-threaded CPython** (PEP 703: the experimental `python3.13t` build, officially supported in 3.14) removes the GIL using biased reference counting and per-object locks. Data races in *your* code then become real. `list.append` is still atomic, but compound operations like `x += 1` never were.

> [!INTERVIEW] Is `counter += 1` thread-safe in Python?
> No. It compiles to a load, an add and a store: separate bytecodes between which another thread can run, even with the GIL. Protect it with a `threading.Lock`, or use `itertools.count` or queue-based designs.

## 4. Attribute lookup and descriptors

`obj.attr` calls `type(obj).__getattribute__(obj, "attr")`, which does:
1. Find `attr` on the **type**, by walking the MRO. If it's a **data descriptor** (it defines `__set__` or `__delete__`), call its `__get__`.
2. Otherwise, look in the **instance `__dict__`**.
3. Otherwise, if the type attribute is a **non-data descriptor** (only `__get__`, like functions), call `__get__`. If it's a plain value, return it.
4. Otherwise, call `__getattr__` if it's defined, else raise `AttributeError`.

**Descriptors** are objects with `__get__`/`__set__`/`__delete__` stored on a class. They're how `property`, `classmethod`, `staticmethod`, `__slots__`, bound methods and ORM fields work:

```python
class Positive:
    def __set_name__(self, owner, name):        # called at class creation (3.6+)
        self.private = "_" + name
    def __get__(self, obj, objtype=None):
        if obj is None: return self              # accessed on the class
        return getattr(obj, self.private)
    def __set__(self, obj, value):
        if value <= 0: raise ValueError(f"{self.private[1:]} must be > 0")
        setattr(obj, self.private, value)

class Motor:
    max_rpm = Positive()
    def __init__(self, rpm): self.max_rpm = rpm  # goes through Positive.__set__
```

Functions are non-data descriptors: `Motor.method.__get__(motor)` creates the **bound method** that you call. That's why `obj.method is obj.method` is False: a new bound method each time.

## 5. Class creation and metaclasses

The `class` statement:
1. Computes the bases and the metaclass (`type` by default).
2. Calls `metaclass.__prepare__` to get the namespace.
3. Executes the class body in that namespace.
4. Calls `metaclass(name, bases, namespace)`, which runs `type.__new__`. That triggers `__set_name__` on descriptors and `__init_subclass__` on the parent class.
5. Applies class decorators.

`type` is its own metaclass, and every class is an instance of `type`: `isinstance(type, object)` and `isinstance(object, type)` are both True.

**Prefer simpler hooks**, as metaclasses are rarely needed:

| Need | Tool |
|---|---|
| Validate or register subclasses | `__init_subclass__` |
| Per-attribute behaviour | descriptors and `__set_name__` |
| Generate methods (`__init__`, `__repr__`) | a class decorator (how `@dataclass` works) |
| Change class creation itself, custom namespaces, intercept `isinstance` | a metaclass (ABCMeta, Enum, ORM bases) |

## 6. Dataclasses, `__slots__` and the data model

`@dataclass` reads `__annotations__` and **generates source code** for `__init__`, `__repr__` and `__eq__` (plus ordering, hashing, frozen and slots options), then `exec`s it. That's why dataclasses are as fast as hand-written classes. The **data model** dunders let user types integrate with syntax:
- `__len__`, `__getitem__`, `__iter__`, `__contains__`
- `__enter__`/`__exit__` for context managers
- `__call__`, `__add__`/`__radd__`/`__iadd__`
- `__format__`, `__bool__`, `__hash__`, `__lt__` (with `functools.total_ordering`)

## 7. Performance internals

- Local variable access is fast (an array slot), while globals and builtins need dict lookups. That's why hot loops bind `append = out.append` (less necessary since 3.11's specialisation).
- Attribute access on `__slots__` classes uses descriptor slots and is faster and smaller.
- Function calls are relatively expensive. Prefer built-ins and comprehensions (C loops) over Python loops, and vectorise numeric work with NumPy.
- **Profile before optimising**: `cProfile` + `snakeviz`, `line_profiler`, `py-spy` (a sampling profiler that attaches to running processes), and `timeit` for microbenchmarks.

> [!EXAM]
> **What is a descriptor, and how do `property` and methods rely on the descriptor protocol?**
> A descriptor is an object stored as a class attribute that defines `__get__` and optionally `__set__`/`__delete__`. Attribute lookup on an instance consults the type first: a data descriptor (defining `__set__`) takes priority over the instance `__dict__`, while a non-data descriptor is used only if the instance dict lacks the name. `property` is a data descriptor whose `__get__`/`__set__` call the getter and setter functions, giving computed or validated attributes. Plain functions are non-data descriptors whose `__get__` returns a bound method (with the instance bound as `self`), which is how method calls receive `self`. `classmethod` and `staticmethod` are descriptors that bind the class or nothing instead.
