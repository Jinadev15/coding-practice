# Hashing Patterns

Python's `dict` and `set` give **average O(1)** insert, delete and lookup. Replacing a linear search with a hash lookup is the most common way to turn an O(n²) algorithm into O(n). This lesson collects the recurring patterns (complement lookup, frequency counting, grouping by a canonical key, deduplication, first/last occurrence, and hashing state for cycle detection), explains how hashing works underneath, and covers the pitfalls: hashability, mutability, and the worst case.

## 1. How hash tables work (in one minute)

A hash table stores entries in an array of slots. `hash(key)` picks a slot, and collisions are resolved by probing (CPython uses **open addressing** with a perturbation scheme). Keys are compared with `==` only when hashes match. When the table gets about 2/3 full, it **resizes** (doubling), which keeps operations amortised O(1).

> [!KEY]
> - Only **hashable** objects can be dict keys or set members: immutable built-ins (`int`, `str`, `tuple` of hashables, `frozenset`) and objects whose `__hash__` is consistent with `__eq__`. Lists, dicts and sets aren't hashable: convert them with `tuple(lst)`, `frozenset(s)` or `tuple(sorted(d.items()))`.
> - The **invariant**: `a == b` implies `hash(a) == hash(b)`. Break it, by mutating a key after insertion or with a bad `__hash__`, and lookups silently fail.
> - The **worst case** is O(n) per operation, if all keys collide. CPython randomises `str`/`bytes` hashing per process (`PYTHONHASHSEED`) to defeat collision-flooding attacks.
> - Dicts preserve **insertion order** (guaranteed since 3.7). Sets don't guarantee any order.

## 2. Pattern: complement lookup (two-sum)

```python
def two_sum(nums, target):
    seen = {}                                 # value -> index
    for i, x in enumerate(nums):
        if target - x in seen:
            return seen[target - x], i
        seen[x] = i                           # insert AFTER checking: an element can't pair with itself
    return None
```

That's one pass, O(n). The general shape is "for each element, ask whether its partner was already seen". It covers pairs with a given difference, "contains duplicate within distance k" (store the last index), and 4-sum counting with pair sums (`Counter(a + b for a in A for b in B)` gives O(n²) instead of O(n⁴)).

## 3. Pattern: frequency counting

```python
from collections import Counter

Counter("mississippi").most_common(2)            # [('i', 4), ('s', 4)]

def is_anagram(a, b):
    return Counter(a) == Counter(b)              # O(n) vs sorting O(n log n)

def first_unique_char(s):
    c = Counter(s)
    return next((i for i, ch in enumerate(s) if c[ch] == 1), -1)

def majority_element(nums):                      # appears > n/2 times: Boyer–Moore, O(1) space
    cand, count = None, 0
    for x in nums:
        if count == 0:
            cand = x
        count += 1 if x == cand else -1
    return cand
```

`Counter` supports arithmetic: `c1 - c2` (keeps positives), `c1 & c2` (min), `c1 | c2` (max), and `c.total()` (3.10+).

## 4. Pattern: group by a canonical key

When items that "belong together" share some normalised form, make that form the dict key:

```python
from collections import defaultdict

def group_anagrams(words):
    groups = defaultdict(list)
    for w in words:
        groups[tuple(sorted(w))].append(w)       # or a 26-count tuple: O(len) instead of O(len log len)
    return list(groups.values())

group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
# [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
```

Other canonical keys:
- the shape of a pattern: `"egg"` and `"add"` both become `(0, 1, 1)`
- the differences between consecutive letters (shifted strings)
- the normalised slope of a line through two points: `(dy // g, dx // g)` with sign fixing, for "max points on a line"
- a sorted tuple of a polygon's edge lengths

## 5. Pattern: seen-set for O(1) membership

```python
def longest_consecutive(nums):                   # O(n): only start counting at sequence starts
    s = set(nums)
    best = 0
    for x in s:
        if x - 1 not in s:                       # x starts a run
            y = x
            while y + 1 in s:
                y += 1
            best = max(best, y - x + 1)
    return best

longest_consecutive([100, 4, 200, 1, 3, 2])      # 4  (1, 2, 3, 4)
```

Each element is visited by the `while` loop only from its run's start, so the total is O(n), even though the loops are nested.

## 6. Pattern: hashing states (cycle detection, memoisation)

```python
def is_happy(n):
    seen = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = sum(int(d) ** 2 for d in str(n))
    return n == 1
```

Simulations that might repeat (robot command loops, cellular automata, the "prison cells after N days" problem) store each state, as a tuple or `bytes`, mapped to the step at which it first appeared. When a state repeats, you've found the cycle length and can jump ahead with modular arithmetic. `functools.cache` is the same idea for function arguments.

## 7. Pattern: index maps for O(1) updates

Combining a list and a dict gives structures that a plain set can't offer:

```python
import random

class RandomizedSet:                              # insert, remove, get_random all O(1)
    def __init__(self):
        self.items, self.pos = [], {}
    def insert(self, x):
        if x in self.pos: return False
        self.pos[x] = len(self.items); self.items.append(x); return True
    def remove(self, x):
        if x not in self.pos: return False
        i, last = self.pos[x], self.items[-1]
        self.items[i], self.pos[last] = last, i   # move the last element into the hole
        self.items.pop(); del self.pos[x]; return True
    def get_random(self):
        return random.choice(self.items)
```

An LRU cache is a dict plus a doubly linked list. In Python, `OrderedDict.move_to_end` and `popitem(last=False)` do both.

## 8. Custom keys: `__hash__` and `__eq__`

```python
from dataclasses import dataclass

@dataclass(frozen=True)                    # frozen → generates __hash__ consistent with __eq__
class Cell:
    row: int
    col: int

visited = {Cell(0, 0), Cell(0, 1)}
Cell(0, 1) in visited                      # True
```

> [!DANGER]
> A plain `@dataclass` (with `eq=True`, the default, and not frozen) sets `__hash__ = None`, so instances are unhashable. That's on purpose: mutable objects whose equality depends on fields mustn't be keys. If you mutate a key that's already in a set, it's stranded in the wrong slot and `in` returns `False`.

## 9. Exam-ready answers

> [!EXAM]
> **Hash tables.** A hash table stores key–value pairs in an array indexed by a hash of the key, resolving collisions by chaining or open addressing and resizing to keep the load factor bounded, so that insertion, deletion and lookup take O(1) time on average and O(n) in the worst case. Python's `dict` and `set` are hash tables requiring keys to be hashable, with hashes consistent with equality and unchanging while the key is stored. Algorithmically, hashing replaces repeated linear searches with constant-time membership tests, enabling single-pass solutions such as complement lookup for two-sum, frequency counting, grouping by canonical keys and detecting repeated states.

## 10. Cheat sheet

| Pattern | Structure |
|---|---|
| seen it before? | `set` |
| where did I see it? | `dict` value → index |
| how many times? | `Counter` / `defaultdict(int)` |
| group items | `defaultdict(list)` keyed by a canonical form |
| unhashable key | `tuple(...)`, `frozenset(...)` |
| O(1) random + delete | list + index dict |
| LRU | `OrderedDict` |

> [!INTERVIEW]
> **"What's the worst case of a dict lookup, and can it happen?"** O(n), if every key lands in the same probe sequence. Attackers once exploited this with crafted HTTP parameters, which is why Python randomises string hashes per process. With well-distributed hashes, operations are O(1) average and amortised over resizes. Also mention that a custom `__hash__` returning a constant is legal but degrades every operation to O(n).
