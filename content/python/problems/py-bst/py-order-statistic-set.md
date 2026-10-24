---
id: py-order-statistic-set
title: An Order-Statistic Set (Treap)
difficulty: Hard
order: 1
tags: BST, treap, rotations, order statistics, floor/ceiling
time_limit: 4
---
## Statement
Python has no balanced BST. Build one. Implement `OrderedSet`, a set of distinct integers with **expected O(log n)** operations. A randomised **treap** (a BST by key + a heap by random priority) is recommended, but any balanced design works.

```python
class OrderedSet:
    def add(self, x) -> bool: ...         # False if already present
    def remove(self, x) -> bool: ...      # False if absent
    def __contains__(self, x) -> bool: ...
    def __len__(self) -> int: ...
    def kth(self, k): ...                 # k-th smallest, 0-based; IndexError if out of range
    def rank(self, x) -> int: ...         # number of elements < x
    def floor(self, x): ...               # largest element <= x, or None
    def ceiling(self, x): ...             # smallest element >= x, or None
    def __iter__(self): ...               # ascending order
```

The driver runs scripted operations, then a 150 000-operation random workload, checking against a reference. Sorted-list solutions with `insort` pass the small tests but are O(n) per insert. The large test is sized so that a well-implemented treap finishes comfortably.

## Starter
```python
import bisect

class OrderedSet:
    def __init__(self):
        self.a = []
    def add(self, x):
        i = bisect.bisect_left(self.a, x)
        if i < len(self.a) and self.a[i] == x:
            return False
        self.a.insert(i, x)
        return True
    def remove(self, x):
        return False
    def __contains__(self, x):
        i = bisect.bisect_left(self.a, x)
        return i < len(self.a) and self.a[i] == x
    def __len__(self):
        return len(self.a)
    def kth(self, k):
        return self.a[k]
    def rank(self, x):
        return bisect.bisect_left(self.a, x)
    def floor(self, x):
        return None
    def ceiling(self, x):
        return None
    def __iter__(self):
        return iter(self.a)
```

## Driver
```python
import random
import sys

def run_script(lines):
    s = OrderedSet()
    for line in lines:
        op, *args = line.split()
        args = [int(a) for a in args]
        if op == "add": print("add", args[0], s.add(args[0]))
        elif op == "remove": print("remove", args[0], s.remove(args[0]))
        elif op == "has": print("has", args[0], args[0] in s)
        elif op == "len": print("len", len(s))
        elif op == "kth":
            try: print("kth", args[0], s.kth(args[0]))
            except IndexError: print("kth", args[0], "IndexError")
        elif op == "rank": print("rank", args[0], s.rank(args[0]))
        elif op == "floor": print("floor", args[0], s.floor(args[0]))
        elif op == "ceiling": print("ceiling", args[0], s.ceiling(args[0]))
        elif op == "list": print("list", list(s))

def workload(seed, n):
    rng = random.Random(seed)
    s = OrderedSet()
    acc = 0
    for i in range(n):
        x = rng.randrange(10**6)
        r = rng.random()
        if r < 0.45: acc += s.add(x)
        elif r < 0.6: acc += 3 * s.remove(x)
        elif r < 0.7 and len(s): acc += s.kth(rng.randrange(len(s))) % 97
        elif r < 0.8: acc += s.rank(x) % 89
        elif r < 0.9: f = s.floor(x); acc += (f or 0) % 83
        else: c = s.ceiling(x); acc += (c or 0) % 79
    lst = list(s)
    print("workload", n, len(s), acc, lst[:3], lst == sorted(set(lst)))

data = sys.stdin.read().split("\n")
if data[0].startswith("workload"):
    _, seed, n = data[0].split()
    workload(int(seed), int(n))
else:
    run_script([l for l in data if l.strip()])
```

## Tests
=== sample
add 5
add 1
add 9
add 5
len
kth 0
kth 2
rank 6
floor 6
ceiling 6
list
---
add 5 True
add 1 True
add 9 True
add 5 False
len 3
kth 0 1
kth 2 9
rank 6 2
floor 6 5
ceiling 6 9
list [1, 5, 9]
=== hidden
floor 3
ceiling 3
kth 0
add 10
add 20
add 30
remove 20
remove 20
has 20
has 30
rank 10
rank 31
floor 10
floor 9
ceiling 31
ceiling 30
kth 1
kth 2
kth -1
add -4
list
remove 10
remove 30
remove -4
len
list
---
floor 3 None
ceiling 3 None
kth 0 IndexError
add 10 True
add 20 True
add 30 True
remove 20 True
remove 20 False
has 20 False
has 30 True
rank 10 0
rank 31 2
floor 10 10
floor 9 None
ceiling 31 None
ceiling 30 30
kth 1 30
kth 2 IndexError
kth -1 IndexError
add -4 True
list [-4, 10, 30]
remove 10 True
remove 30 True
remove -4 True
len 0
list []
=== hidden
workload 7 150000
---
workload 150000 64383 2663095 [8, 9, 18] True
=== hidden
workload 8 60000
---
workload 60000 26470 1057097 [66, 77, 97] True

## Hints
- Node fields: `key`, `prio` (`random.random()`), `left`, `right`, `size`. Keep `size` updated after every structural change: `n.size = 1 + size(n.left) + size(n.right)`.
- The simplest treap is built on **split** and **merge**. `split(t, x)` returns (keys < x, keys ≥ x). `merge(a, b)` (all of a < all of b) picks the root with the higher priority. Then `add` is split + merge with a new node, and `remove` is split(x), split(x+1), and merge of the outer parts.
- Implement split and merge iteratively, or note that the expected depth is O(log n) (about 40 for 10⁵), so recursion is fine.
- `kth`: at node n with `ls = size(n.left)`: if k < ls go left; if k == ls return n.key; else go right with `k -= ls + 1`. Reject a negative k explicitly.

## Solution
```python
import random

class _Node:
    __slots__ = ("key", "prio", "left", "right", "size")
    def __init__(self, key):
        self.key, self.prio = key, random.random()
        self.left = self.right = None
        self.size = 1

def _size(n):
    return n.size if n else 0

def _fix(n):
    n.size = 1 + _size(n.left) + _size(n.right)

def _split(t, x):
    """(keys < x, keys >= x)"""
    if t is None:
        return None, None
    if t.key < x:
        a, b = _split(t.right, x)
        t.right = a
        _fix(t)
        return t, b
    a, b = _split(t.left, x)
    t.left = b
    _fix(t)
    return a, t

def _merge(a, b):
    """every key in a < every key in b"""
    if a is None or b is None:
        return a or b
    if a.prio > b.prio:
        a.right = _merge(a.right, b)
        _fix(a)
        return a
    b.left = _merge(a, b.left)
    _fix(b)
    return b

class OrderedSet:
    def __init__(self):
        self.root = None

    def __contains__(self, x):
        n = self.root
        while n:
            if x == n.key:
                return True
            n = n.left if x < n.key else n.right
        return False

    def add(self, x):
        if x in self:
            return False
        a, b = _split(self.root, x)
        self.root = _merge(_merge(a, _Node(x)), b)
        return True

    def remove(self, x):
        if x not in self:
            return False
        a, b = _split(self.root, x)
        _, c = _split(b, x + 1)               # the middle part is exactly the node with key x
        self.root = _merge(a, c)
        return True

    def __len__(self):
        return _size(self.root)

    def kth(self, k):
        if not 0 <= k < len(self):
            raise IndexError(k)
        n = self.root
        while True:
            ls = _size(n.left)
            if k < ls:
                n = n.left
            elif k == ls:
                return n.key
            else:
                k -= ls + 1
                n = n.right

    def rank(self, x):
        r, n = 0, self.root
        while n:
            if n.key < x:
                r += _size(n.left) + 1
                n = n.right
            else:
                n = n.left
        return r

    def floor(self, x):
        best, n = None, self.root
        while n:
            if n.key <= x:
                best, n = n.key, n.right
            else:
                n = n.left
        return best

    def ceiling(self, x):
        best, n = None, self.root
        while n:
            if n.key >= x:
                best, n = n.key, n.left
            else:
                n = n.right
        return best

    def __iter__(self):
        st, n = [], self.root
        while st or n:
            while n:
                st.append(n)
                n = n.left
            n = st.pop()
            yield n.key
            n = n.right
```

A **treap** is a BST ordered by key whose nodes are also heap-ordered by a random priority. For a given set of keys and priorities, the shape is unique, and it's the BST you'd get by inserting the keys in random order. So its expected depth is O(log n) **whatever order the operations arrive in**, which avoids the sorted-insertion degeneration of plain BSTs without AVL or red–black case analysis.

**Split and merge** are the only structural operations. Insertion and deletion are just compositions of them, and every touched node re-computes `size`. That size augmentation turns the treap into an **order-statistic tree**: `kth` and `rank` walk a single root-to-leaf path. `floor` and `ceiling` track the best candidate while descending, exactly as in an ordinary BST.
