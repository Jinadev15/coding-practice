---
id: py-consistent-hash-ring
title: Consistent Hashing with Virtual Nodes and Replication
difficulty: Hard
order: 1
tags: system design, consistent hashing, virtual nodes, bisect, sharding, replication
time_limit: 8
---
## Statement
Build the partitioning layer of a distributed telemetry store: a **consistent-hash ring** with weighted virtual nodes and replica placement.

```python
def default_hash(s: str) -> int:   # given: first 8 bytes of MD5, big-endian
    return int.from_bytes(hashlib.md5(s.encode()).digest()[:8], "big")
```

`class HashRing(vnodes=64, hash_fn=default_hash)`:
- `add_node(name, weight=1)`: places `vnodes * weight` points, hashing the labels `f"{name}#{i}"` for i = 0, 1, …. A duplicate name raises `ValueError`, and so does `weight < 1`.
- `remove_node(name)` removes all its points. An unknown name raises `KeyError`.
- `get_node(key)`: the owner of the first point **clockwise** from `hash_fn(key)`, meaning the smallest point hash strictly greater than the key hash, wrapping around to the first point. An empty ring raises `LookupError`.
- `get_nodes(key, n)`: up to `n` **distinct** nodes, walking clockwise from the key's position (the owner first). These are the replica locations. If `n` exceeds the number of nodes, return all of them in walk order.
- `nodes()` (sorted names), `__len__` (the number of nodes), and `distribution(keys) -> dict` (node → key count, every node included).

On ties between point hashes (only possible with a weak custom `hash_fn`), the point added earlier comes first.

## Starter
```python
import hashlib


def default_hash(s: str) -> int:
    return int.from_bytes(hashlib.md5(s.encode()).digest()[:8], "big")


class HashRing:
    def __init__(self, vnodes=64, hash_fn=default_hash):
        self.hash_fn = hash_fn
        self.names = []

    def add_node(self, name, weight=1):
        self.names.append(name)

    def remove_node(self, name):
        self.names.remove(name)

    def get_node(self, key):
        return self.names[self.hash_fn(key) % len(self.names)]

    def get_nodes(self, key, n):
        return [self.get_node(key)]

    def nodes(self):
        return sorted(self.names)

    def __len__(self):
        return len(self.names)

    def distribution(self, keys):
        out = {n: 0 for n in self.names}
        for k in keys:
            out[self.get_node(k)] += 1
        return out
```

## Driver
```python
import sys

def attempt(label, fn):
    try:
        print(f"{label}: {fn()!r}")
    except (ValueError, KeyError, LookupError) as e:
        print(f"{label}: {type(e).__name__}")

keys = [f"robot-{i}/telemetry" for i in range(20000)]
for cmd in sys.stdin.read().split():
    if cmd == "small":
        toy = lambda s: sum(map(ord, s)) * 2654435761 % 1000          # deterministic toy hash
        r = HashRing(vnodes=2, hash_fn=toy)
        attempt("empty", lambda: r.get_node("x"))
        for n in ["A", "B", "C"]:
            r.add_node(n)
        print("points", sorted((toy(f"{n}#{i}"), n) for n in "ABC" for i in range(2)))
        for k in ["k1", "k2", "zz", "robot"]:
            print(k, toy(k), r.get_node(k), r.get_nodes(k, 2), r.get_nodes(k, 5))
        attempt("dup", lambda: r.add_node("A"))
        attempt("weight", lambda: r.add_node("D", weight=0))
        attempt("remove unknown", lambda: r.remove_node("Q"))
        r.remove_node("B"); print(r.nodes(), len(r), r.get_nodes("k1", 3))
    elif cmd == "movement":
        r = HashRing(vnodes=128)
        for n in ["s1", "s2", "s3", "s4"]:
            r.add_node(n)
        before = {k: r.get_node(k) for k in keys}
        r.add_node("s5")
        after = {k: r.get_node(k) for k in keys}
        moved = [k for k in keys if before[k] != after[k]]
        print("moved on add", len(moved), "all to s5:", all(after[k] == "s5" for k in moved))
        r.remove_node("s2")
        after2 = {k: r.get_node(k) for k in keys}
        moved2 = [k for k in keys if after[k] != after2[k]]
        print("moved on remove", len(moved2), "all from s2:", all(after[k] == "s2" for k in moved2))
        print("modulo would move", sum((hash_mod := (lambda k, n: default_hash(k) % n))(k, 4) != hash_mod(k, 5) for k in keys))
    elif cmd == "balance":
        r = HashRing(vnodes=200)
        for n in ["a", "b", "c", "d"]:
            r.add_node(n)
        r.add_node("big", weight=3)
        d = r.distribution(keys)
        print(d)
        print("big share ~3x", round(d["big"] / (sum(d.values()) - d["big"]) * 4, 2))
        reps = [r.get_nodes(k, 3) for k in keys[:5000]]
        print("replicas distinct", all(len(set(x)) == 3 for x in reps), "owner first", all(x[0] == r.get_node(k) for x, k in zip(reps, keys)))
        print(r.get_nodes("robot-7/telemetry", 9))
```

## Tests
=== sample
small
---
empty: LookupError
points [(150, 'B'), (150, 'C'), (389, 'A'), (389, 'B'), (628, 'A'), (911, 'C')]
k1 716 C ['C', 'B'] ['C', 'B', 'A']
k2 477 A ['A', 'C'] ['A', 'C', 'B']
zz 684 C ['C', 'B'] ['C', 'B', 'A']
robot 550 A ['A', 'C'] ['A', 'C', 'B']
dup: ValueError
weight: ValueError
remove unknown: KeyError
['A', 'C'] 2 ['C', 'A']
=== hidden
movement
---
moved on add 3668 all to s5: True
moved on remove 4024 all from s2: True
modulo would move 15916
=== hidden
balance
---
{'a': 2714, 'b': 2766, 'big': 8735, 'c': 3084, 'd': 2701}
big share ~3x 3.1
replicas distinct True owner first True
['d', 'c', 'big', 'b', 'a']

## Hints
- Keep a sorted list of `(point_hash, seq, node)` tuples, where `seq` is a global insertion counter that makes ties deterministic. Keep a parallel list of just the hashes for `bisect`.
- `i = bisect.bisect_right(hashes, h)`, and if `i == len(hashes)`, wrap to 0.
- `get_nodes`: walk forward from `i` (mod the number of points), collecting unseen node names until you have `n` or have visited every point.
- Rebuild the arrays on add and remove (O(P log P)), and keep lookups O(log P).

## Solution
```python
import bisect
import hashlib
import itertools


def default_hash(s: str) -> int:
    return int.from_bytes(hashlib.md5(s.encode()).digest()[:8], "big")


class HashRing:
    def __init__(self, vnodes=64, hash_fn=default_hash):
        self.vnodes = vnodes
        self.hash_fn = hash_fn
        self._seq = itertools.count()
        self._points = []          # sorted (hash, seq, node)
        self._hashes = []          # parallel list of hashes for bisect
        self._weights = {}

    def _rebuild(self):
        self._points.sort()
        self._hashes = [p[0] for p in self._points]

    def add_node(self, name, weight=1):
        if name in self._weights:
            raise ValueError(f"duplicate node {name!r}")
        if weight < 1:
            raise ValueError("weight must be >= 1")
        self._weights[name] = weight
        for i in range(self.vnodes * weight):
            self._points.append((self.hash_fn(f"{name}#{i}"), next(self._seq), name))
        self._rebuild()

    def remove_node(self, name):
        if name not in self._weights:
            raise KeyError(name)
        del self._weights[name]
        self._points = [p for p in self._points if p[2] != name]
        self._rebuild()

    def _start(self, key):
        if not self._points:
            raise LookupError("empty ring")
        i = bisect.bisect_right(self._hashes, self.hash_fn(key))
        return 0 if i == len(self._points) else i

    def get_node(self, key):
        return self._points[self._start(key)][2]

    def get_nodes(self, key, n):
        i = self._start(key)
        out, seen = [], set()
        for step in range(len(self._points)):
            node = self._points[(i + step) % len(self._points)][2]
            if node not in seen:
                seen.add(node)
                out.append(node)
                if len(out) == n:
                    break
        return out

    def nodes(self):
        return sorted(self._weights)

    def __len__(self):
        return len(self._weights)

    def distribution(self, keys):
        out = dict.fromkeys(sorted(self._weights), 0)
        for k in keys:
            out[self.get_node(k)] += 1
        return out
```

- **Only neighbours move**: adding `s5` only steals keys that now fall just before its points, so every moved key goes *to* `s5` (about 1/5 of the keys). Removing `s2` only reassigns `s2`'s keys. Modulo hashing reshuffles about 80% of the keys for the same change.
- **Virtual nodes** smooth out the load: with 200 points per node, the shares are close to even, and a node of weight 3 gets roughly three times the keys, which is how heterogeneous hardware is handled.
- **Replica placement** walks clockwise, skipping repeated nodes, so the replicas land on distinct machines. This is Dynamo/Cassandra's "preference list". Production systems also skip nodes in the same rack or zone.
- **Lookups are O(log P)** with `bisect` on a sorted array, and membership changes rebuild in O(P log P), which is a fine trade-off because lookups vastly outnumber topology changes.
- **Deterministic ties** (insertion sequence) make the ring identical on every client, which is essential when many routers must agree on ownership without coordinating.
