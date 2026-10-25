---
id: py-lru-from-scratch
title: LRU Cache from Scratch
difficulty: Medium
order: 1
tags: interview, LRU, hash map, doubly linked list, O(1), sentinel nodes
time_limit: 6
---
## Statement
The most-asked data-structure interview question: implement an LRU (least recently used) cache with **O(1)** operations, **without** `collections.OrderedDict` or `functools.lru_cache`. The judge inspects your class source to check this. Use a dict plus a doubly linked list.

`class LRUCache(capacity, on_evict=None)`:
- `get(key, default=None)`: returns the value and marks the key **most recently used**. A miss returns `default`.
- `put(key, value)`: inserts or updates, marking the key most recently used. If the size would exceed `capacity`, evict the **least recently used** entry and call `on_evict(key, value)` if it was given. With `capacity == 0` nothing is ever stored, and every put is immediately "evicted" (the callback is called with the new pair).
- `peek(key, default=None)`: like `get`, but **doesn't** change the recency.
- `delete(key) -> bool`: removes the entry, returning False if it was absent. Not an eviction (no callback).
- `__len__`, `__contains__` (doesn't change the recency), `keys()`: a list from **most to least** recently used.
- `capacity < 0` raises `ValueError`.

## Starter
```python
class LRUCache:
    def __init__(self, capacity, on_evict=None):
        self.capacity = capacity
        self.data = {}
        self.order = []

    def get(self, key, default=None):
        if key in self.data:
            self.order.remove(key)
            self.order.append(key)
            return self.data[key]
        return default

    def put(self, key, value):
        if key not in self.data and len(self.data) >= self.capacity:
            old = self.order.pop(0)
            del self.data[old]
        self.data[key] = value
        if key in self.order:
            self.order.remove(key)
        self.order.append(key)

    def keys(self):
        return list(reversed(self.order))
```

## Driver
```python
import inspect
import sys
import time

src = inspect.getsource(LRUCache)
if "OrderedDict" in src or "lru_cache" in src:
    print("forbidden helper used"); sys.exit(0)

for cmd in sys.stdin.read().split():
    if cmd == "basic":
        ev = []
        c = LRUCache(3, on_evict=lambda k, v: ev.append((k, v)))
        c.put("a", 1); c.put("b", 2); c.put("c", 3)
        print(c.keys(), len(c))
        print(c.get("a"), c.keys())
        c.put("d", 4); print("evicted", ev, c.keys())
        print(c.peek("b"), c.keys(), "b" in c, "zz" in c, c.keys())
        c.put("c", 30); print(c.keys(), c.get("c"))
        c.put("e", 5); print("evicted", ev, c.keys())
        print(c.delete("a"), c.delete("a"), c.keys(), len(c), ev)
        print(c.get("missing", "dflt"), c.peek("missing"))
        c.put("f", 6); c.put("g", 7); print(c.keys(), ev)
    elif cmd == "edge":
        ev = []
        z = LRUCache(0, on_evict=lambda k, v: ev.append(k))
        z.put("x", 1); print(len(z), z.get("x"), ev, z.keys())
        one = LRUCache(1)
        one.put(1, "a"); one.put(2, "b"); print(one.keys(), one.get(1), one.get(2))
        one.put(2, "B"); print(one.keys(), one.get(2))
        try:
            LRUCache(-1)
        except ValueError:
            print("negative capacity rejected")
        c = LRUCache(2)
        c.put(None, "none-key"); c.put((1, 2), "tuple"); print(c.get(None), c.keys())
        c.delete(None); c.delete((1, 2)); print(len(c), c.keys()); c.put("z", 0); print(c.keys())
    elif cmd == "big":
        ev = [0]
        c = LRUCache(50000, on_evict=lambda k, v: ev.__setitem__(0, ev[0] + 1))
        hits = 0
        t0 = time.perf_counter()
        x = 12345
        for i in range(600000):
            x = (x * 1103515245 + 12345) & 0x7FFFFFFF
            k = x % 80000
            if i % 3:
                if c.get(k) is not None:
                    hits += 1
            else:
                c.put(k, i)
            if i % 1000 == 0:
                c.delete((x >> 3) % 80000)
        elapsed = time.perf_counter() - t0
        print("hits", hits, "evictions", ev[0], "size", len(c), "head", c.keys()[:3])
        print("fast enough:", elapsed < 4.0)
```

## Tests
=== sample
basic
---
['c', 'b', 'a'] 3
1 ['a', 'c', 'b']
evicted [('b', 2)] ['d', 'a', 'c']
None ['d', 'a', 'c'] False False ['d', 'a', 'c']
['c', 'd', 'a'] 30
evicted [('b', 2), ('a', 1)] ['e', 'c', 'd']
False False ['e', 'c', 'd'] 3 [('b', 2), ('a', 1)]
dflt None
['g', 'f', 'e'] [('b', 2), ('a', 1), ('d', 4), ('c', 30)]
=== hidden
edge
---
0 None ['x'] []
[2] None b
[2] B
negative capacity rejected
none-key [None, (1, 2)]
0 []
['z']
=== hidden
big
---
hits 208388 evictions 45161 size 50000 head [45561, 72768, 53827]
fast enough: True

## Hints
- A node class with `__slots__ = ("key", "value", "prev", "next")`, and two **sentinel** nodes `head` and `tail`, so inserting and unlinking never need `None` checks.
- `self.map[key] -> node`. Then `get` unlinks the node and re-inserts it after `head`. Evict `tail.prev`.
- `list.remove` and `list.pop(0)` are O(n). That's why the starter is too slow for the big test.

## Solution
```python
class _Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key=None, value=None):
        self.key, self.value = key, value
        self.prev = self.next = None


class LRUCache:
    def __init__(self, capacity, on_evict=None):
        if capacity < 0:
            raise ValueError("capacity must be >= 0")
        self.capacity = capacity
        self.on_evict = on_evict
        self._map = {}
        self._head, self._tail = _Node(), _Node()     # sentinels: head.next is MRU, tail.prev is LRU
        self._head.next, self._tail.prev = self._tail, self._head

    def _unlink(self, node):
        node.prev.next, node.next.prev = node.next, node.prev

    def _push_front(self, node):
        node.prev, node.next = self._head, self._head.next
        self._head.next.prev = node
        self._head.next = node

    def get(self, key, default=None):
        node = self._map.get(key)
        if node is None:
            return default
        self._unlink(node)
        self._push_front(node)
        return node.value

    def peek(self, key, default=None):
        node = self._map.get(key)
        return default if node is None else node.value

    def put(self, key, value):
        node = self._map.get(key)
        if node is not None:
            node.value = value
            self._unlink(node)
            self._push_front(node)
            return
        if self.capacity == 0:
            if self.on_evict:
                self.on_evict(key, value)
            return
        node = _Node(key, value)
        self._map[key] = node
        self._push_front(node)
        if len(self._map) > self.capacity:
            lru = self._tail.prev
            self._unlink(lru)
            del self._map[lru.key]
            if self.on_evict:
                self.on_evict(lru.key, lru.value)

    def delete(self, key):
        node = self._map.pop(key, None)
        if node is None:
            return False
        self._unlink(node)
        return True

    def __len__(self):
        return len(self._map)

    def __contains__(self, key):
        return key in self._map

    def keys(self):
        out, node = [], self._head.next
        while node is not self._tail:
            out.append(node.key)
            node = node.next
        return out
```

- **Dict + doubly linked list**: the dict finds a node in O(1), and the list keeps the recency order with O(1) unlink and re-insert. Neither structure alone can do both.
- **Sentinel nodes** remove every edge case (empty list, first or last node), so `_unlink` and `_push_front` are two lines each with no branches.
- **Callbacks fire after** the internal structure is consistent, so an `on_evict` that inspects the cache sees a valid state.
- `__slots__` on the node class saves memory and attribute-lookup time across 50,000+ nodes. This is essentially how `OrderedDict` was implemented in pure Python.
