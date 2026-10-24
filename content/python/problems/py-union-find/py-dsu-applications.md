---
id: py-dsu-applications
title: "Union-Find Applications: MST, Accounts Merge, Equations, Islands II"
difficulty: Hard
order: 1
tags: union-find, Kruskal, MST, dynamic connectivity, grouping
time_limit: 3
---
## Statement
Four problems solved with a disjoint-set union (write your own DSU with path compression and union by size).

```python
def mst_cost(n, edges):
    """Undirected weighted edges (u, v, w). Minimum spanning tree total weight, or -1 if disconnected."""

def merge_accounts(accounts):
    """accounts: [name, email1, email2, ...]. Accounts sharing any email belong to the same person.
    Return merged accounts as [name, *sorted unique emails], sorted by (name, first email).
    The name of a merged account is the name of the account that first mentioned its
    alphabetically smallest email (names only differ in the generated tests)."""

def equations_possible(eqs):
    """eqs like "a==b" or "a!=b" over single lowercase letters. True if all can hold at once."""

def islands_after_each(rows, cols, positions):
    """Initially all water. positions turn cells into land one by one (repeats possible).
    Return the number of islands (4-connected) after each step."""
```

Test lines are `(function_name, args)` literals or `gen NAME SEED N`.

## Starter
```python
def mst_cost(n, edges):
    return sum(w for _, _, w in edges)

def merge_accounts(accounts):
    return sorted(accounts)

def equations_possible(eqs):
    return True

def islands_after_each(rows, cols, positions):
    return [0] * len(positions)
```

## Driver
```python
import ast
import random
import sys

FUNCS = {f.__name__: f for f in (mst_cost, merge_accounts, equations_possible, islands_after_each)}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        if name == "mst_cost":
            edges = [(i, rng.randrange(i), rng.randrange(1, 10**6)) for i in range(1, n)]
            edges += [(rng.randrange(n), rng.randrange(n), rng.randrange(1, 10**6)) for _ in range(2 * n)]
            print(name, n, mst_cost(n, edges), mst_cost(n + 1, edges))
        elif name == "merge_accounts":
            acc = []
            for i in range(n):
                k = rng.randrange(1, 4)
                acc.append(["user%d" % rng.randrange(50)] + ["e%d@x.io" % rng.randrange(3 * n) for _ in range(k)])
            r = merge_accounts(acc)
            print(name, n, len(r), r[0][:3], max(len(a) for a in r))
        else:
            R = C = n
            pos = [(rng.randrange(R), rng.randrange(C)) for _ in range(R * C // 2)]
            r = islands_after_each(R, C, pos)
            print(name, n, len(r), max(r), r[-1], sum(r) % 1000003)
        continue
    name, args = ast.literal_eval(line)
    print(name, "->", FUNCS[name](*args))
```

## Tests
=== sample
("mst_cost", (4, [(0, 1, 1), (1, 2, 2), (0, 2, 3), (2, 3, 4)]))
("merge_accounts", ([["John", "j@a.com", "js@b.com"], ["John", "js@b.com", "jx@c.com"], ["Mary", "m@d.com"], ["John", "jn@e.com"]],))
("equations_possible", (["a==b", "b!=a"],))
("islands_after_each", (3, 3, [(0, 0), (0, 1), (1, 2), (2, 1)]))
---
mst_cost -> 7
merge_accounts -> [['John', 'j@a.com', 'js@b.com', 'jx@c.com'], ['John', 'jn@e.com'], ['Mary', 'm@d.com']]
equations_possible -> False
islands_after_each -> [1, 1, 2, 3]
=== hidden
("mst_cost", (1, []))
("mst_cost", (3, [(0, 1, 5)]))
("mst_cost", (3, [(0, 1, 5), (1, 2, 5), (0, 2, 5), (0, 1, 1)]))
("merge_accounts", ([["A", "x@1"], ["B", "x@1"]],))
("merge_accounts", ([["Z", "c", "b", "a"]],))
("merge_accounts", ([["A", "1"], ["A", "2"], ["A", "3", "1"], ["A", "2", "4"]],))
("equations_possible", (["a==b", "b==c", "a==c"],))
("equations_possible", (["a==b", "b!=c", "c==a"],))
("equations_possible", (["c==c", "b==d", "x!=z"],))
("equations_possible", (["a!=a"],))
("islands_after_each", (1, 1, [(0, 0), (0, 0)]))
("islands_after_each", (2, 2, [(0, 0), (1, 1), (0, 1), (1, 0)]))
("islands_after_each", (1, 5, [(0, 0), (0, 2), (0, 4), (0, 1), (0, 3)]))
---
mst_cost -> 0
mst_cost -> -1
mst_cost -> 6
merge_accounts -> [['A', 'x@1']]
merge_accounts -> [['Z', 'a', 'b', 'c']]
merge_accounts -> [['A', '1', '3'], ['A', '2', '4']]
equations_possible -> True
equations_possible -> False
equations_possible -> True
equations_possible -> False
islands_after_each -> [1, 1]
islands_after_each -> [1, 2, 1, 1]
islands_after_each -> [1, 2, 3, 2, 1]
=== hidden
gen mst_cost 1 100000
gen merge_accounts 2 30000
---
mst_cost 100000 19704017021 -1
merge_accounts 30000 13626 ['user0', 'e10091@x.io'] 746
=== hidden
gen islands_after_each 3 300
---
islands_after_each 300 45000 11768 9931 954105

## Hints
- **MST (Kruskal)**: sort the edges by weight and union the endpoints; add the weight when the union succeeds. Connected iff there were exactly n − 1 successful unions.
- **Accounts**: map each email to an id (the first account that mentions it) and union all emails within one account. Group the emails by root and attach the name. Record, for each email, the name of the first account that mentions it; a group's name comes from its smallest email.
- **Equations**: first union every `==` pair, then check that no `!=` pair has the same root. `"a!=a"` is impossible.
- **Islands II**: add a cell as a new set (`count += 1`), then union it with each land neighbour, decrementing the count on every successful union. Ignore repeated positions.

## Solution
```python
class DSU:
    def __init__(self, n=0):
        self.parent = list(range(n))
        self.size = [1] * n

    def add(self):
        self.parent.append(len(self.parent))
        self.size.append(1)
        return len(self.parent) - 1

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        return True

def mst_cost(n, edges):
    d = DSU(n)
    total = joined = 0
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        if d.union(u, v):
            total += w
            joined += 1
    return total if joined == n - 1 else -1

def merge_accounts(accounts):
    d = DSU()
    eid, name_of = {}, {}
    for acc in accounts:
        name, emails = acc[0], acc[1:]
        ids = []
        for e in emails:
            if e not in eid:
                eid[e] = d.add()
                name_of[e] = name
            ids.append(eid[e])
        for i in ids[1:]:
            d.union(ids[0], i)
    groups = {}
    for e, i in eid.items():
        groups.setdefault(d.find(i), []).append(e)
    out = []
    for emails in groups.values():
        emails.sort()
        out.append([name_of[emails[0]], *emails])
    return sorted(out, key=lambda a: (a[0], a[1]))

def equations_possible(eqs):
    d = DSU(26)
    idx = lambda c: ord(c) - 97
    for e in eqs:
        if e[1] == "=":
            d.union(idx(e[0]), idx(e[3]))
    return all(d.find(idx(e[0])) != d.find(idx(e[3])) for e in eqs if e[1] == "!")

def islands_after_each(rows, cols, positions):
    d = DSU(rows * cols)
    land = [False] * (rows * cols)
    count, out = 0, []
    for r, c in positions:
        i = r * cols + c
        if not land[i]:
            land[i] = True
            count += 1
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < rows and 0 <= nc < cols and land[nr * cols + nc]:
                    if d.union(i, nr * cols + nc):
                        count -= 1
        out.append(count)
    return out
```

Each problem is **dynamic grouping**, which is what union-find is for:
- **Kruskal** adds edges lightest-first and skips any edge whose endpoints are already connected. The cut property guarantees optimality.
- **Accounts merge** treats emails as elements and each account as a set of unions. Sharing is transitive, and the DSU computes that transitive closure in near-linear time.
- **Equations** need two passes: merge every equality first, then verify the inequalities. Checking an inequality early would miss equalities that arrive later.
- **Islands II** is *incremental* connectivity. Each new land cell starts a component, and each successful union with a neighbour merges two components. That's O(α) per step, where re-running a flood fill after every step would cost O(R·C).
