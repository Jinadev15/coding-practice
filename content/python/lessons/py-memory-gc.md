# Memory Management and Garbage Collection

Python manages memory for you, but "automatic" doesn't mean "free" or "magic". CPython uses **reference counting** to free most objects the instant they become unreachable, plus a **cyclic garbage collector** for reference cycles that counting can't handle. Knowing how this works explains why `del` doesn't necessarily free memory, how cycles and caches leak, why `is` sometimes surprises you with small integers and strings, and how to diagnose memory growth in long-running services and robot nodes.

## 1. Everything is an object with a reference count

Every CPython object header contains a **reference count**: the number of references pointing at it (names, container slots, attributes, stack entries). When it drops to zero, the object is freed **immediately**, and its own references are released, possibly cascading.

```python
import sys
a = []
sys.getrefcount(a)      # 2: `a`, plus the temporary argument reference inside getrefcount
b = a
sys.getrefcount(a)      # 3
del b                   # removes a NAME, decrements the count. It doesn't "delete the object"
```

| Operation | Effect on the reference count |
|---|---|
| assign to a name, append to a list, store as an attribute | +1 |
| a name goes out of scope, `del name`, reassignment, removal from a container | −1 |
| the count reaches 0 | freed immediately (`__del__` runs, if defined) |

> [!KEY]
> Reference counting makes deallocation **deterministic**: a file object closed by losing its last reference closes *right then*. But that's an implementation detail of CPython (PyPy uses a different collector), so always use `with` for resources, never rely on refcounting to close files or sockets.

## 2. Reference cycles and the cyclic collector

Reference counting can't free objects that refer to each other:

```python
class Node:
    def __init__(self):
        self.ref = None

n1, n2 = Node(), Node()
n1.ref, n2.ref = n2, n1     # a cycle: each keeps the other's count at ≥ 1
del n1, n2                  # unreachable from the program, but the counts are 1, not 0
import gc
gc.collect()                # the cycle detector finds and frees them
```

The **`gc` module** periodically scans container objects (lists, dicts, class instances: things that can hold references) for groups that are only reachable from each other. CPython organises objects into **generations**: young objects are checked often, and survivors are promoted to older, less frequently scanned generations, based on the observation that most objects die young. Python 3.14 introduced an **incremental** collector that spreads the old-generation work across many small steps, reducing pause times.

```python
gc.get_threshold()          # (2000, 10, 0) in 3.14: the allocation-count triggers
gc.collect()                # force a full collection; returns the number of unreachable objects found
gc.disable()                # turn off AUTOMATIC cycle collection (refcounting still runs)
gc.freeze()                 # move all current objects to a permanent generation (used before fork in servers)
```

> [!WARNING]
> Latency-sensitive code (robot control loops, games, trading) sometimes calls `gc.disable()` and runs `gc.collect()` at safe moments to avoid unpredictable pauses. Doing that requires avoiding cycles carefully, using `weakref` for back-references (parent pointers, observers, caches).

## 3. Interning and caching: why `is` lies

```python
x = 256; y = 256
x is y                       # True: CPython caches the small ints -5..256 as singletons
x = int("257"); y = int("257")
x is y                       # False: separate objects
s1 = "hello"; s2 = "hel" + "lo"
s1 is s2                     # True: the compiler folded the constant, and identifier-like literals are interned
s3 = "".join(["hel", "lo"])
s1 is s3                     # False: built at run time
s1 is sys.intern(s3)         # True: explicit interning
```

> [!DANGER]
> Never use `is` to compare numbers or strings: use `==`. Identity results depend on caching and compiler optimisations that vary across versions and implementations. `is` is only for singletons: `None`, `True`, `False`, sentinel objects, enum members.

`sys.intern` is useful when you hold millions of repeated strings (keys from parsed logs, tokens): equal strings share one object, which saves memory and makes dict lookups faster.

## 4. Where memory actually goes

- **pymalloc:** CPython's small-object allocator (≤ 512 bytes) manages "arenas" and "pools" of fixed-size blocks. Freed blocks are reused by Python but often **not returned to the OS**, so process RSS can stay high after a spike even though Python considers the memory free.
- **Object overhead:** an `int` object is 28 bytes, an empty `list` 56, an empty `dict` 64 (and growing), and a class instance with a `__dict__` around 100+ bytes. Millions of small objects add up, so use `__slots__`, `array`, NumPy, or columnar data.
- **Measuring:** `sys.getsizeof` is shallow. Use **`tracemalloc`** to find which lines allocate:

```python
import tracemalloc
tracemalloc.start()
run_workload()
snapshot = tracemalloc.take_snapshot()
for stat in snapshot.statistics("lineno")[:5]:
    print(stat)              # file:line  size=...  count=...
```

Comparing two snapshots (`snapshot2.compare_to(snapshot1, "lineno")`) shows which lines keep growing: that's how you find leaks.

## 5. Common leak patterns in Python

| Pattern | Fix |
|---|---|
| unbounded caches / global dicts that only grow | `functools.lru_cache(maxsize=N)`, eviction, `WeakValueDictionary` |
| cycles involving objects with `__del__` (old Pythons) or huge graphs | `weakref` for back-references; break cycles explicitly |
| listeners/callbacks never unregistered | weak references or explicit unsubscribe |
| exceptions/tracebacks held in variables | tracebacks reference frames and all their locals: clear them (`e = None`) |
| closures capturing large objects | capture only what's needed |
| C extensions leaking | profile with tools like `memray` (native + Python allocations) |

## 6. Exam-ready answers

> [!EXAM]
> **Memory management in CPython.** CPython manages memory primarily by reference counting: each object records how many references point to it, the count is adjusted as references are created and destroyed, and an object is deallocated immediately when its count reaches zero. Reference counting cannot reclaim reference cycles, so a supplementary cyclic garbage collector (the `gc` module) periodically traverses container objects, organised into generations so that young objects are examined more frequently, and frees groups of objects reachable only from one another. `del` removes a reference, not the object. CPython caches small integers and interns certain strings, so identity comparisons with `is` on values are unreliable. Memory usage is analysed with `tracemalloc`, and weak references avoid cycles and unbounded caches.

## 7. Cheat sheet

| Need | Tool |
|---|---|
| see a reference count | `sys.getrefcount(obj)` (one higher than you'd think) |
| force cycle collection | `gc.collect()` |
| pause-free critical section | `gc.disable()` … `gc.collect()` at a safe point |
| find allocations by line | `tracemalloc` snapshots |
| a reference that doesn't keep alive | `weakref.ref`, `WeakValueDictionary` |
| deduplicate repeated strings | `sys.intern(s)` |
| compare values | `==` (never `is`, except for singletons) |

> [!INTERVIEW]
> **"If Python has garbage collection, how can a Python program leak memory?"** Objects are freed only when unreachable. A "leak" in Python is usually memory that's still **reachable**: an ever-growing cache or global list, listeners registered and never removed, tracebacks stored with their frames, or objects kept alive through closures. The collector correctly keeps all of these. Cycles are reclaimed only when the cyclic GC runs (and not at all if it's disabled). Memory freed by Python may also not be returned to the OS (pymalloc arenas), so RSS can stay high. Diagnose by comparing `tracemalloc` snapshots over time, or use `memray`/`objgraph` to find what's holding references.
