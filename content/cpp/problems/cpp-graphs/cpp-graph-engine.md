---
id: cpp-graph-engine
title: "Graph Engine: Dijkstra, Components, MST, Topological Order"
difficulty: Hard
order: 1
tags: Dijkstra, priority_queue, DSU, Kruskal, topological sort, CSR
time_limit: 3
---
## Statement
Implement four graph routines that scale to 200 000 vertices and 600 000 edges:

```cpp
std::vector<long long> dijkstra(int n, const std::vector<std::array<int,3>>& edges, int src);
    // directed edges {u, v, w}, w >= 0; -1 for unreachable vertices
int count_components(int n, const std::vector<std::pair<int,int>>& edges);   // undirected
long long mst_weight(int n, std::vector<std::array<int,3>> edges);           // undirected {u, v, w}; -1 if disconnected
std::vector<int> topo_order(int n, const std::vector<std::pair<int,int>>& edges);
    // lexicographically smallest topological order of the DAG; empty if a cycle exists
```

No recursion: some test graphs are 200 000-vertex paths.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<long long> dijkstra(int n, const vector<array<int,3>>& edges, int src) {
    vector<long long> d(n, LLONG_MAX);
    d[src] = 0;
    for (int it = 0; it < n; ++it)
        for (auto [u, v, w] : edges)
            if (d[u] != LLONG_MAX && d[u] + w < d[v]) d[v] = d[u] + w;
    for (auto& x : d) if (x == LLONG_MAX) x = -1;
    return d;
}
int count_components(int n, const vector<pair<int,int>>& edges) { return n; }
long long mst_weight(int n, vector<array<int,3>> edges) { return -1; }
vector<int> topo_order(int n, const vector<pair<int,int>>& edges) { return {}; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd;
    while (cin >> cmd) {
        if (cmd == "dij") {
            int n, m, s; cin >> n >> m >> s;
            vector<array<int,3>> e(m); for (auto& [u, v, w] : e) cin >> u >> v >> w;
            auto d = dijkstra(n, e, s);
            cout << "dijkstra:"; for (auto x : d) cout << ' ' << x; cout << '\n';
        } else if (cmd == "comp") {
            int n, m; cin >> n >> m;
            vector<pair<int,int>> e(m); for (auto& [u, v] : e) cin >> u >> v;
            cout << "components = " << count_components(n, e) << '\n';
        } else if (cmd == "mst") {
            int n, m; cin >> n >> m;
            vector<array<int,3>> e(m); for (auto& [u, v, w] : e) cin >> u >> v >> w;
            cout << "mst = " << mst_weight(n, e) << '\n';
        } else if (cmd == "topo") {
            int n, m; cin >> n >> m;
            vector<pair<int,int>> e(m); for (auto& [u, v] : e) cin >> u >> v;
            auto t = topo_order(n, e);
            cout << "topo (" << t.size() << "):"; for (int x : t) cout << ' ' << x; cout << '\n';
        } else if (cmd == "gen") {
            int n; unsigned seed; cin >> n >> seed;
            mt19937 rng(seed);
            vector<array<int,3>> e;
            for (int i = 1; i < n; ++i) e.push_back({i - 1, i, int(rng() % 1000) + 1});        // a long path
            for (int i = 0; i < 2 * n; ++i) e.push_back({int(rng() % n), int(rng() % n), int(rng() % 100000)});
            auto d = dijkstra(n, e, 0);
            long long dsum = 0; for (auto x : d) dsum += x;
            vector<pair<int,int>> pe;
            for (int i = 0; i < n / 2; ++i) pe.push_back({int(rng() % n), int(rng() % n)});
            vector<pair<int,int>> dag;
            for (int i = 0; i < 3 * n; ++i) { int a = rng() % n, b = rng() % n; if (a != b) dag.push_back({min(a, b), max(a, b)}); }
            auto t = topo_order(n, dag);
            for (int i = 0; i + 1 < n; ++i) dag.push_back({i, i + 1});   // a chain 0 -> ... -> n-1
            dag.push_back({n - 1, 0});                                     // closes a cycle
            auto t2 = topo_order(n, dag);
            cout << "gen n=" << n << ": dist_sum=" << dsum << " d_last=" << d[n - 1]
                 << " comps=" << count_components(n, pe) << " mst=" << mst_weight(n, e)
                 << " topo_first=" << (t.empty() ? -1 : t[0]) << " topo_len=" << t.size() << " cyclic_len=" << t2.size() << '\n';
        }
    }
}
```

## Tests
=== sample
dij 4 4 0
0 1 4
0 2 1
2 1 2
1 3 1
comp 5 2
0 1
3 4
mst 4 5
0 1 1
1 2 2
0 2 3
2 3 4
1 3 6
topo 4 4
1 0
2 0
3 1
3 2
---
dijkstra: 0 3 1 4
components = 3
mst = 7
topo (4): 3 1 2 0
=== hidden
dij 1 0 0
dij 3 1 0
1 2 5
dij 3 3 2
0 1 1
2 0 0
2 1 9
comp 1 0
comp 4 4
0 1
1 2
2 0
3 3
mst 3 1
0 1 5
mst 1 0
mst 3 4
0 1 5
1 2 5
0 2 5
0 1 1
topo 3 0
topo 2 2
0 1
1 0
topo 3 2
2 1
1 0
---
dijkstra: 0
dijkstra: 0 -1 -1
dijkstra: 0 1 0
components = 1
components = 2
mst = -1
mst = 0
mst = 6
topo (3): 0 1 2
topo (0):
topo (3): 2 1 0
=== hidden
gen 200000 8
---
gen n=200000: dist_sum=10238883217 d_last=53936 comps=100003 mst=98141319 topo_first=0 topo_len=200000 cyclic_len=0

## Hints
- **Dijkstra**: an adjacency list built once, then `priority_queue<pair<long long,int>, vector<...>, greater<>>`, skipping stale entries.
- **Components / MST**: a DSU with path halving and union by size. Components = n − successful unions. Kruskal: sort the edges by weight.
- **Topo order**: Kahn's algorithm with a min-heap of ready vertices (`priority_queue<int, vector<int>, greater<int>>`).
- Build adjacency with `vector<vector<...>>` and `reserve`, or CSR arrays for speed.

## Solution
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<long long> dijkstra(int n, const vector<array<int,3>>& edges, int src) {
    vector<vector<pair<int,int>>> adj(n);
    for (auto [u, v, w] : edges) adj[u].push_back({v, w});
    const long long INF = LLONG_MAX / 4;
    vector<long long> d(n, INF);
    using P = pair<long long, int>;
    priority_queue<P, vector<P>, greater<P>> pq;
    d[src] = 0;
    pq.push({0, src});
    while (!pq.empty()) {
        auto [du, u] = pq.top(); pq.pop();
        if (du != d[u]) continue;
        for (auto [v, w] : adj[u])
            if (du + w < d[v]) { d[v] = du + w; pq.push({d[v], v}); }
    }
    for (auto& x : d) if (x == INF) x = -1;
    return d;
}

struct DSU {
    vector<int> p, sz;
    explicit DSU(int n) : p(n), sz(n, 1) { iota(p.begin(), p.end(), 0); }
    int find(int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }
    bool unite(int a, int b) {
        a = find(a); b = find(b);
        if (a == b) return false;
        if (sz[a] < sz[b]) swap(a, b);
        p[b] = a; sz[a] += sz[b];
        return true;
    }
};

int count_components(int n, const vector<pair<int,int>>& edges) {
    DSU d(n);
    int comps = n;
    for (auto [u, v] : edges) comps -= d.unite(u, v);
    return comps;
}

long long mst_weight(int n, vector<array<int,3>> edges) {
    sort(edges.begin(), edges.end(), [](const auto& a, const auto& b) { return a[2] < b[2]; });
    DSU d(n);
    long long total = 0;
    int used = 0;
    for (auto [u, v, w] : edges)
        if (d.unite(u, v)) { total += w; ++used; }
    return used == n - 1 ? total : -1;
}

vector<int> topo_order(int n, const vector<pair<int,int>>& edges) {
    vector<vector<int>> adj(n);
    vector<int> indeg(n, 0);
    for (auto [u, v] : edges) { adj[u].push_back(v); ++indeg[v]; }
    priority_queue<int, vector<int>, greater<int>> ready;
    for (int v = 0; v < n; ++v) if (!indeg[v]) ready.push(v);
    vector<int> order;
    order.reserve(n);
    while (!ready.empty()) {
        int u = ready.top(); ready.pop();
        order.push_back(u);
        for (int v : adj[u]) if (--indeg[v] == 0) ready.push(v);
    }
    if ((int)order.size() != n) order.clear();        // a cycle
    return order;
}
```

- **Dijkstra** with a binary heap and lazy deletion is O((V + E) log V). The `greater<>` comparator and distance-first pairs give the min-heap. `LLONG_MAX / 4` as infinity can't overflow when added to a weight.
- **The DSU** with path halving and union by size makes both components and Kruskal near-linear after the O(E log E) sort. Self-loops and duplicate edges are harmless, because their unions simply fail.
- **Kahn with a min-heap** emits the smallest available vertex each time, which gives the lexicographically smallest order. A short result means a cycle.

Everything is iterative, so the 200 000-vertex path in the generated test can't overflow the call stack.
