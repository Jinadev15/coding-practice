---
id: cpp-gr-clone-graph
title: Clone a Graph of Pointers
difficulty: Medium
order: 7
tags: graphs, BFS, deep copy, hash map, pointers
time_limit: 2
---
## Statement
A graph is stored as heap-allocated nodes that point to each other:

```cpp
struct Node {
    int val;
    std::vector<Node*> nbrs;          // neighbours, in a fixed order
    explicit Node(int v) : val(v) {}
};
Node* clone_graph(Node* start);
```

Return a **deep copy** of the connected component containing `start`: a brand-new `Node` for every node reachable from `start`, with the same `val` and the same neighbour lists (same order, pointing at the *new* nodes). No pointer in the copy may refer to an original node. `start` is never `nullptr`. The graph is undirected (if `a` lists `b`, `b` lists `a`), may contain cycles, self-loops and repeated neighbours, and can have 2·10⁵ nodes in a single chain, so don't recurse.

The key structure is a map `old node → new node`. It answers two questions at once: "have I already copied this node?" and "where is its copy?"

**Input:** cases until the end of input: `n m s`, then `m` edges `u v` (1 ≤ n ≤ 2·10⁵, m ≤ 4·10⁵). The driver appends `v` to `u`'s list and `u` to `v`'s list for each edge, in input order, and clones from node `s`.

**Output (printed by the driver):** the number of copied nodes and edge entries, or a description of what's wrong with the copy.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct Node {
    int val;
    vector<Node*> nbrs;
    explicit Node(int v) : val(v) {}
};

Node* clone_graph(Node* start) {
    return start;                      // TODO: this is a shallow "copy"
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, m, s;
    while (cin >> n >> m >> s) {
        vector<Node*> orig(n);
        for (int i = 0; i < n; ++i) orig[i] = new Node(i);
        for (int i = 0; i < m; ++i) { int u, v; cin >> u >> v; orig[u]->nbrs.push_back(orig[v]); orig[v]->nbrs.push_back(orig[u]); }
        unordered_set<Node*> origSet; origSet.reserve(2 * n); origSet.insert(orig.begin(), orig.end());
        Node* c = clone_graph(orig[s]);
        // collect the copy
        vector<Node*> cl; unordered_set<Node*> clSet; clSet.reserve(2 * n);
        if (c) { cl.push_back(c); clSet.insert(c); }
        for (size_t i = 0; i < cl.size(); ++i) for (Node* x : cl[i]->nbrs) if (x && clSet.insert(x).second) cl.push_back(x);
        // reference component of s
        vector<int> comp{s}; vector<char> in(n, 0); in[s] = 1;
        for (size_t i = 0; i < comp.size(); ++i) for (Node* x : orig[comp[i]]->nbrs) if (!in[x->val]) { in[x->val] = 1; comp.push_back(x->val); }
        string err;
        bool shared = false;
        for (Node* x : cl) if (origSet.count(x)) shared = true;
        if (!c) err = "null copy";
        else if (shared) err = "copy shares nodes with the original";
        else if (c->val != s) err = "wrong start node";
        else if (cl.size() != comp.size()) err = "wrong number of nodes";
        else {
            vector<Node*> byVal(n, nullptr);
            for (Node* x : cl) { if (x->val < 0 || x->val >= n || !in[x->val] || byVal[x->val]) { err = "bad or duplicated value"; break; } byVal[x->val] = x; }
            if (err.empty()) for (Node* x : cl) {
                auto& a = x->nbrs; auto& b = orig[x->val]->nbrs;
                if (a.size() != b.size()) { err = "wrong neighbour count"; break; }
                for (size_t k = 0; k < a.size(); ++k) if (a[k] != byVal[b[k]->val]) { err = "wrong neighbour"; break; }
                if (!err.empty()) break;
            }
        }
        long long entries = 0; for (Node* x : cl) entries += x->nbrs.size();
        if (err.empty()) cout << "nodes " << cl.size() << " entries " << entries << " ok\n";
        else cout << "error: " << err << '\n';
        for (Node* x : cl) if (!origSet.count(x)) delete x;
        for (Node* x : orig) delete x;
    }
}
```

## Tests
=== sample
4 4 0
0 1
1 2
2 3
3 0
---
nodes 4 entries 8 ok
=== sample
5 2 3
0 1
3 4
---
nodes 2 entries 2 ok
=== hidden
1 0 0
---
nodes 1 entries 0 ok
=== hidden
1 2 0
0 0
0 0
---
nodes 1 entries 4 ok
=== hidden
3 3 2
0 1
0 1
1 2
---
nodes 3 entries 6 ok
=== hidden
3 2 2
1 1
0 1
7 8 6
6 4
6 6
3 1
6 0
3 1
2 2
6 2
2 1
2 1 0
0 1
5 3 4
2 2
4 4
2 1
---
nodes 1 entries 0 ok
nodes 6 entries 16 ok
nodes 2 entries 2 ok
nodes 1 entries 2 ok
=== hidden
2 8 0
1 1
1 1
1 1
0 0
0 1
1 0
1 1
1 1
6 7 4
3 0
3 3
0 3
5 0
2 0
0 0
1 3
7 7 6
3 1
6 2
4 4
5 1
4 2
5 3
5 4
2 2 0
1 0
1 0
---
nodes 2 entries 16 ok
nodes 1 entries 0 ok
nodes 6 entries 14 ok
nodes 2 entries 4 ok
=== hidden
4 6 0
3 2
2 2
3 1
2 3
0 1
2 1
5 5 4
1 1
0 3
4 2
2 3
4 0
3 7 1
2 2
0 2
0 2
0 0
2 0
0 0
0 2
5 5 1
0 3
0 2
3 4
4 2
2 0
---
nodes 4 entries 12 ok
nodes 4 entries 8 ok
nodes 1 entries 0 ok
nodes 1 entries 0 ok
=== hidden
@gen 2985799074 big
=== hidden
@gen 2985799075 big
=== hidden
@gen 2985799076 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 1):
    if not big:
        n = r.randint(1, 7); m = r.randint(0, 9)
        print(n, m, r.randrange(n))
        for _ in range(m): print(r.randrange(n), r.randrange(n))
    else:
        n = 200000
        es = [(i, i + 1) for i in range(n - 1)] + [(r.randrange(n), r.randrange(n)) for _ in range(20000)]
        r.shuffle(es)
        print(n, len(es), r.randrange(n))
        for u, v in es: print(u, v)
```

## Hints
- Keep a map from each original node to its copy. It is also your visited set.
- Traverse the original with a queue. On first sight of a neighbour, create its copy and enqueue it.
- For each original neighbour entry of `u`, append the neighbour's copy to `u`'s copy, which preserves order and multiplicities.

## Solution
**Two jobs, one map.** While copying, every time you meet a node you must know whether a copy already exists (to avoid infinite loops on cycles and duplicate copies) and, if it does, where it is (to wire the edge to it). An `unordered_map<Node*, Node*>` from original to clone does both.

**BFS over the original.** Create the clone of `start` and push `start`. When a node `u` is popped, walk its neighbour list in order; for each neighbour `v`, create its clone on first sight and enqueue `v`, then append `copy[v]` to `copy[u]->nbrs`. Every original edge entry is processed exactly once, so neighbour order, repeated neighbours and self-loops all come out identical.

**Why not recursion?** The recursive version (`clone(v)` calls `clone` on each neighbour) is shorter, but a path of 2·10⁵ nodes nests 2·10⁵ calls deep and crashes the stack. The queue lives on the heap.

**Ownership.** The function allocates with `new`; the caller owns the copy and must delete it. In production code you'd return a container of `unique_ptr<Node>` that owns every node.

Complexity: O(V + E) expected time with the hash map, O(V) extra memory.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct Node {
    int val;
    vector<Node*> nbrs;
    explicit Node(int v) : val(v) {}
};

Node* clone_graph(Node* start) {
    unordered_map<Node*, Node*> copy;          // original -> its clone (also the "visited" set)
    copy.reserve(1 << 16);
    vector<Node*> q{start};
    copy[start] = new Node(start->val);
    for (size_t head = 0; head < q.size(); ++head) {
        Node* u = q[head];
        Node* cu = copy[u];
        cu->nbrs.reserve(u->nbrs.size());
        for (Node* v : u->nbrs) {
            auto it = copy.find(v);
            if (it == copy.end()) {                // first time we see v: create its clone, explore later
                it = copy.emplace(v, new Node(v->val)).first;
                q.push_back(v);
            }
            cu->nbrs.push_back(it->second);        // same position, but pointing into the copy
        }
    }
    return copy[start];
}
```
