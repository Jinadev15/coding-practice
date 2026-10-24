---
id: py-dependency-planner
title: "Dependency Planner: Build Order, Semesters, Alien Alphabet"
difficulty: Hard
order: 1
tags: topological sort, Kahn's algorithm, heap, cycle detection
time_limit: 3
---
## Statement
Plan the start-up order of a robot's software modules and related dependency problems.

```python
def build_order(n, deps):
    """Modules 0..n-1; deps: (a, b) means a must start before b.
    Return the lexicographically smallest valid order, or [] if a cycle makes it impossible."""

def min_semesters(n, deps):
    """With unlimited parallelism, each semester runs every module whose prerequisites are done.
    Return the number of semesters needed, or -1 if impossible (n >= 1)."""

def alien_order(words):
    """words are sorted in an unknown alphabet (over the letters they contain).
    Return the lexicographically smallest (by normal letter order) alphabet consistent with
    the list, containing every letter that appears; return "" if the list is inconsistent."""
```

Test lines are `(function_name, args)` literals or `gen NAME SEED N`.

## Starter
```python
def build_order(n, deps):
    return list(range(n))

def min_semesters(n, deps):
    return 1

def alien_order(words):
    return "".join(sorted(set("".join(words))))
```

## Driver
```python
import ast
import random
import sys

FUNCS = {f.__name__: f for f in (build_order, min_semesters, alien_order)}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        perm = list(range(n)); rng.shuffle(perm)
        deps = []
        for _ in range(2 * n):
            i, j = sorted(rng.sample(range(n), 2))
            deps.append((perm[i], perm[j]))           # consistent with perm: acyclic
        chain = [(perm[i], perm[i + 1]) for i in range(0, n - 1, 3)]
        deps += chain
        order = build_order(n, deps)
        print(name, n, len(order), order[:6], min_semesters(n, deps), build_order(n, deps + [(perm[1], perm[0])]) == [])
        continue
    name, args = ast.literal_eval(line)
    print(name, "->", repr(FUNCS[name](*args)))
```

## Tests
=== sample
("build_order", (4, [(1, 0), (2, 0), (3, 1), (3, 2)]))
("build_order", (2, [(0, 1), (1, 0)]))
("min_semesters", (3, [(0, 2), (1, 2)]))
("alien_order", (["wrt", "wrf", "er", "ett", "rftt"],))
---
build_order -> [3, 1, 2, 0]
build_order -> []
min_semesters -> 2
alien_order -> 'wertf'
=== hidden
("build_order", (1, []))
("build_order", (3, []))
("build_order", (3, [(2, 1), (1, 0)]))
("build_order", (3, [(0, 0)]))
("min_semesters", (1, []))
("min_semesters", (4, [(0, 1), (1, 2), (2, 3)]))
("min_semesters", (3, [(0, 1), (1, 2), (2, 0)]))
("min_semesters", (5, [(0, 4), (1, 4), (2, 3), (3, 4)]))
("alien_order", (["z", "x"],))
("alien_order", (["z", "x", "z"],))
("alien_order", (["abc", "ab"],))
("alien_order", (["ab", "abc"],))
("alien_order", (["ba", "bc", "ac", "cab"],))
("alien_order", (["q"],))
---
build_order -> [0]
build_order -> [0, 1, 2]
build_order -> [2, 1, 0]
build_order -> []
min_semesters -> 1
min_semesters -> 4
min_semesters -> -1
min_semesters -> 3
alien_order -> 'zx'
alien_order -> ''
alien_order -> ''
alien_order -> 'abc'
alien_order -> 'bac'
alien_order -> 'q'
=== hidden
gen build_order 1 100000
---
build_order 100000 100000 [12, 19, 21, 22, 41, 45] 30 True
=== hidden
gen build_order 2 50000
---
build_order 50000 50000 [2, 3, 7, 8, 9, 11] 27 True

## Hints
- **build_order**: Kahn's algorithm with a **min-heap** of ready modules (`heapq`) instead of a deque. If fewer than n modules come out, return `[]`.
- **min_semesters**: Kahn processed level by level (all currently ready modules form one semester). Count the levels, and check that all n were processed.
- **alien_order**: for each adjacent pair of words, the first differing letters give an edge `a → b`. If there's no differing letter and the first word is longer (`"abc"` before `"ab"`), the list is invalid. Then run a heap-based Kahn over all letters present.

## Solution
```python
import heapq
from collections import defaultdict

def _kahn_smallest(nodes, edges):
    adj = defaultdict(set)
    indeg = {v: 0 for v in nodes}
    for a, b in edges:
        if b not in adj[a]:
            adj[a].add(b)
            indeg[b] += 1
    ready = [v for v in nodes if indeg[v] == 0]
    heapq.heapify(ready)
    out = []
    while ready:
        u = heapq.heappop(ready)
        out.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(ready, v)
    return out if len(out) == len(nodes) else None

def build_order(n, deps):
    r = _kahn_smallest(range(n), deps)
    return r if r is not None else []

def min_semesters(n, deps):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for a, b in deps:
        adj[a].append(b)
        indeg[b] += 1
    level = [v for v in range(n) if indeg[v] == 0]
    done = semesters = 0
    while level:
        semesters += 1
        done += len(level)
        nxt = []
        for u in level:
            for v in adj[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    nxt.append(v)
        level = nxt
    return semesters if done == n else -1

def alien_order(words):
    letters = sorted(set("".join(words)))
    edges = []
    for w1, w2 in zip(words, words[1:]):
        for a, b in zip(w1, w2):
            if a != b:
                edges.append((a, b))
                break
        else:
            if len(w1) > len(w2):
                return ""                      # a longer word before its own prefix
    r = _kahn_smallest(letters, edges)
    return "".join(r) if r is not None else ""
```

All three are **Kahn's algorithm**, adapted:
- A **min-heap** of ready vertices makes the output the lexicographically smallest order. Greedily taking the smallest available vertex is optimal, because choosing it never blocks anything else.
- **Level-by-level** processing measures the length of the longest dependency chain, which is the parallel makespan in semesters.
- **Alien alphabet** first turns the data into constraints. Only the *first* differing letter of each adjacent pair carries information, and the prefix rule catches a list that's impossible even without a cycle. Duplicate edges are ignored, so in-degrees stay correct.

In every case, a cycle shows up as vertices whose in-degree never reaches zero.
