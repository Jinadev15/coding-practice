# The collections Module

The built-in `list`, `dict`, `set` and `tuple` cover most needs. `collections` provides **specialised containers** for patterns that come up constantly: counting things (`Counter`), grouping (`defaultdict`), fast queues at both ends (`deque`), lightweight records (`namedtuple`), order-aware dicts (`OrderedDict`, for LRU caches) and layered lookups (`ChainMap`). Each replaces several lines of error-prone code with one well-tested, C-accelerated type. They show up in almost every coding interview solution in Python.

## 1. `Counter`: counting hashable things

```python
from collections import Counter

c = Counter("mississippi")
print(c)                     # Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
print(c.most_common(2))      # [('i', 4), ('s', 4)]
print(c["z"])                # 0: missing keys count as zero, no KeyError
c.update("ssa")              # add counts from another iterable
words = Counter(text.split())
```

`Counter` is a `dict` subclass mapping element → count, with multiset arithmetic:

```python
a, b = Counter(a=3, b=1), Counter(a=1, b=2)
a + b      # Counter({'a': 4, 'b': 3})
a - b      # Counter({'a': 2}): non-positive results are DROPPED
a & b      # Counter({'a': 1, 'b': 1}): min of counts (intersection)
a | b      # Counter({'a': 3, 'b': 2}): max of counts (union)
```

```python
c = Counter(a=1)
c.subtract({"a": 3})     # subtract() keeps negatives: Counter({'a': -2})
+c                       # unary + drops non-positive counts: Counter()
```

> [!TIP]
> **Anagram check** in one line: `Counter(s) == Counter(t)`, which is O(n), versus O(n log n) for `sorted(s) == sorted(t)`. **Top-k frequent**: `Counter(xs).most_common(k)`, which uses a heap internally when k is given.

## 2. `defaultdict`: dicts with automatic default values

```python
from collections import defaultdict

groups = defaultdict(list)            # the factory is called for each missing key
for word in ["apple", "avocado", "banana", "blueberry", "cherry"]:
    groups[word[0]].append(word)      # no "if key not in dict" boilerplate
print(dict(groups))   # {'a': ['apple', 'avocado'], 'b': ['banana', 'blueberry'], 'c': ['cherry']}

graph = defaultdict(set)              # adjacency sets
graph["a"].add("b")
counts = defaultdict(int)             # int() == 0
counts["x"] += 1
nested = defaultdict(lambda: defaultdict(int))     # 2-level: nested["r1"]["c3"] += 1
```

> [!WARNING]
> **Just reading** a missing key **inserts it**: `if groups["zzz"]:` creates `"zzz": []`. Use `key in d` or `d.get(key)` to test without inserting. Also, `defaultdict` takes a **callable**: `defaultdict(list)`, not `defaultdict([])`.

## 3. `deque`: a double-ended queue

A `list` is fast at the end, but `insert(0, x)` and `pop(0)` are **O(n)** because every element shifts. A `deque` (a doubly linked list of blocks) is **O(1) at both ends**:

```python
from collections import deque

q = deque()
q.append(1); q.append(2)      # enqueue on the right
q.popleft()                   # dequeue from the left: O(1). This is your BFS queue
q.appendleft(0)

recent = deque(maxlen=3)      # bounded: the oldest items fall off automatically
for x in [1, 2, 3, 4]:
    recent.append(x)
print(recent)                 # deque([2, 3, 4], maxlen=3)
recent.rotate(1)              # deque([4, 2, 3], maxlen=3)
```

| Operation | list | deque |
|---|---|---|
| append / pop at the right | O(1) | O(1) |
| insert / pop at the left | **O(n)** | **O(1)** |
| index `x[i]` in the middle | O(1) | O(n) |
| bounded buffer | manual | `maxlen=` |

> [!KEY]
> Use `deque` for **queues (BFS)**, **sliding windows** (a monotonic deque gives O(n) sliding-window maximum), and **"last N items"** buffers (a robot's recent sensor readings, an undo history). Never use `list.pop(0)` in a loop.

## 4. `namedtuple`: tuples with field names

```python
from collections import namedtuple

Point = namedtuple("Point", "x y")       # or ["x", "y"]
p = Point(1, 2)
print(p.x, p[1], p)                      # 1 2 Point(x=1, y=2)
x, y = p                                 # still a tuple: unpacking, hashing, immutable
p2 = p._replace(x=5)                     # Point(x=5, y=2): a NEW tuple
p._asdict()                              # {'x': 1, 'y': 2}
Point._fields                            # ('x', 'y')
```

It's as memory-light as a tuple (no per-instance `__dict__`) and immutable, and it makes code self-documenting: `return Point(x, y)` instead of `return (x, y)`. `typing.NamedTuple` is the typed, class-syntax version. Use `@dataclass` when you need mutability or methods with defaults (Dataclasses lesson).

## 5. `OrderedDict`: order operations

Plain dicts preserve insertion order since Python 3.7. `OrderedDict` adds **reordering** operations and order-sensitive equality:

```python
from collections import OrderedDict
o = OrderedDict(a=1, b=2, c=3)
o.move_to_end("a")            # a moves to the end: b, c, a
o.popitem(last=False)         # ('b', 2): pop from the FRONT (FIFO)
```

That makes it the classic **LRU cache** building block: move a key to the end on every access, and evict from the front when full. (Both operations are O(1).)

## 6. `ChainMap`: layered lookups

```python
from collections import ChainMap
defaults = {"speed": 1.0, "mode": "safe"}
user = {"speed": 2.5}
cfg = ChainMap(user, defaults)       # searched left to right
cfg["speed"], cfg["mode"]            # (2.5, 'safe')
cfg["mode"] = "fast"                 # writes go to the FIRST mapping only (user)
```

It models scopes and configuration layers (CLI args → environment → config file → defaults) without copying dicts.

## 7. Exam-ready answers

> [!EXAM]
> **The `collections` module.** It provides specialised container types. `Counter` is a dict subclass for counting hashable objects, with `most_common` and multiset arithmetic. `defaultdict` calls a factory function to supply values for missing keys, simplifying grouping and counting. `deque` is a double-ended queue with O(1) appends and pops at both ends and an optional maximum length, making it suitable for queues and sliding windows. `namedtuple` creates immutable tuple subclasses with named fields. `OrderedDict` adds order manipulation such as `move_to_end` and `popitem(last=False)`, useful for LRU caches. `ChainMap` groups several mappings into a single view searched in order, with writes going to the first mapping.

## 8. Cheat sheet

| Need | Use |
|---|---|
| count occurrences | `Counter(iterable)` |
| top k | `Counter(xs).most_common(k)` |
| group into lists | `defaultdict(list)` |
| queue / BFS | `deque` with `append` + `popleft` |
| last N items | `deque(maxlen=N)` |
| record type | `namedtuple("P", "x y")` / `typing.NamedTuple` |
| LRU order | `OrderedDict.move_to_end` + `popitem(last=False)` |
| layered config | `ChainMap(override, defaults)` |

> [!INTERVIEW]
> **"Implement an LRU cache with O(1) get and put."** In Python: subclass or wrap `OrderedDict`. `get` does `move_to_end(key)` and returns the value. `put` assigns, calls `move_to_end`, and if `len > capacity` calls `popitem(last=False)`. Interviewers then often ask for the underlying structure, a **hash map + doubly linked list**: the map gives O(1) lookup of the node, and the list gives O(1) reordering and eviction. (For memoising functions, `functools.lru_cache` already does this.)
