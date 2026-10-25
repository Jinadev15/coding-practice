# Graph Algorithms

Graph algorithms are where C++'s speed matters most. Dijkstra on a million edges, union-find over 10⁷ operations, or BFS over a 4000 × 4000 occupancy grid are routine in C++ and painful in Python. This lesson gives tight, idiomatic C++ implementations of the core algorithms: adjacency representations (including the CSR format), BFS/DFS, Dijkstra, Bellman–Ford, Floyd–Warshall, topological sort, DSU, Kruskal and Prim, plus the details that matter in C++ (`priority_queue` ordering, `INF` choices, iterative DFS).

## 1. Representations

```cpp
int n, m;
vector<vector<int>> adj(n);                      // unweighted
vector<vector<pair<int,int>>> wadj(n);           // (neighbour, weight)
for (int i = 0; i < m; ++i) {
    int u, v, w; cin >> u >> v >> w;
    wadj[u].push_back({v, w});
    wadj[v].push_back({u, w});                   // undirected
}
```

**CSR (compressed sparse row)**: two flat arrays, `start[u]..start[u+1]` indexing into `to[]`. That's one allocation and maximal cache locality, and it's the format used by graph libraries and GPU code:

```cpp
vector<int> deg(n + 1, 0), start(n + 1), to(m);
for (auto [u, v] : edges) ++deg[u + 1];
partial_sum(deg.begin(), deg.end(), start.begin());
vector<int> pos(start.begin(), start.end() - 1);
for (auto [u, v] : edges) to[pos[u]++] = v;
// neighbours of u: to[start[u]] … to[start[u+1] - 1]
```

## 2. Dijkstra with `priority_queue`

```cpp
vector<long long> dijkstra(const vector<vector<pair<int,int>>>& g, int s) {
    const long long INF = LLONG_MAX / 4;
    vector<long long> dist(g.size(), INF);
    using P = pair<long long, int>;                       // (distance, vertex)
    priority_queue<P, vector<P>, greater<P>> pq;          // MIN-heap: greater<>
    dist[s] = 0; pq.push({0, s});
    while (!pq.empty()) {
        auto [d, u] = pq.top(); pq.pop();
        if (d != dist[u]) continue;                       // stale entry
        for (auto [v, w] : g[u])
            if (d + w < dist[v]) { dist[v] = d + w; pq.push({dist[v], v}); }
    }
    return dist;
}
```

> [!KEY]
> - `priority_queue` is a **max-heap** by default. Forgetting `greater<>` turns Dijkstra into a slow, incorrect search.
> - Put the distance **first** in the pair, so the ordering is by distance.
> - Use `LLONG_MAX / 4` as INF, so `INF + w` can't overflow during relaxation.

## 3. BFS on grids and 0-1 BFS

```cpp
int dr[] = {1, -1, 0, 0}, dc[] = {0, 0, 1, -1};
vector<int> dist(R * C, -1);
deque<int> dq;                                   // for 0-1 BFS: push_front for weight 0
dist[s] = 0; dq.push_back(s);
while (!dq.empty()) {
    int cur = dq.front(); dq.pop_front();
    int r = cur / C, c = cur % C;
    for (int k = 0; k < 4; ++k) {
        int nr = r + dr[k], nc = c + dc[k];
        if (nr < 0 || nr >= R || nc < 0 || nc >= C || grid[nr][nc] == '#') continue;
        int nxt = nr * C + nc;
        if (dist[nxt] == -1) { dist[nxt] = dist[cur] + 1; dq.push_back(nxt); }
    }
}
```

Encoding cells as a single int (`r * C + c`) keeps the queue light and the arrays flat.

## 4. Iterative DFS and topological sort

Recursive DFS on a 10⁶-vertex path overflows the default 8 MB stack. Use Kahn's algorithm for topological order, or an explicit stack:

```cpp
vector<int> topo_kahn(int n, const vector<vector<int>>& adj) {
    vector<int> indeg(n, 0), order;
    for (int u = 0; u < n; ++u) for (int v : adj[u]) ++indeg[v];
    queue<int> q;
    for (int u = 0; u < n; ++u) if (!indeg[u]) q.push(u);
    while (!q.empty()) {
        int u = q.front(); q.pop(); order.push_back(u);
        for (int v : adj[u]) if (--indeg[v] == 0) q.push(v);
    }
    return order.size() == (size_t)n ? order : vector<int>{};   // empty = cycle
}
```

## 5. DSU and Kruskal

```cpp
struct DSU {
    vector<int> p, sz;
    DSU(int n) : p(n), sz(n, 1) { iota(p.begin(), p.end(), 0); }
    int find(int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }   // path halving
    bool unite(int a, int b) {
        a = find(a); b = find(b);
        if (a == b) return false;
        if (sz[a] < sz[b]) swap(a, b);
        p[b] = a; sz[a] += sz[b];
        return true;
    }
};

long long kruskal(int n, vector<array<int,3>> edges) {         // {w, u, v}
    sort(edges.begin(), edges.end());
    DSU d(n); long long total = 0; int used = 0;
    for (auto [w, u, v] : edges) if (d.unite(u, v)) { total += w; ++used; }
    return used == n - 1 ? total : -1;
}
```

**Path halving** (`p[x] = p[p[x]]` while walking) gives the same amortised bound as full path compression, without recursion.

## 6. Bellman–Ford and Floyd–Warshall

```cpp
// Floyd–Warshall: k outermost; use INF that survives addition
const long long INF = LLONG_MAX / 4;
for (int k = 0; k < n; ++k)
    for (int i = 0; i < n; ++i) {
        if (d[i][k] == INF) continue;
        for (int j = 0; j < n; ++j)
            d[i][j] = min(d[i][j], d[i][k] + d[k][j]);
    }
```

In C++, Floyd–Warshall handles n ≈ 1000–2000 within a second or two (10⁹ simple operations need tight loops). In Python, it's limited to a few hundred.

## 7. Prim's algorithm with a heap

```cpp
long long prim(const vector<vector<pair<int,int>>>& g) {
    int n = g.size();
    vector<bool> in(n, false);
    priority_queue<pair<int,int>, vector<pair<int,int>>, greater<>> pq;  // (weight, vertex)
    pq.push({0, 0});
    long long total = 0; int taken = 0;
    while (!pq.empty() && taken < n) {
        auto [w, u] = pq.top(); pq.pop();
        if (in[u]) continue;
        in[u] = true; total += w; ++taken;
        for (auto [v, wt] : g[u]) if (!in[v]) pq.push({wt, v});
    }
    return taken == n ? total : -1;
}
```

## 8. Exam-ready answers

> [!EXAM]
> **Implementing Dijkstra's algorithm with std::priority_queue.** Because `std::priority_queue` lacks a decrease-key operation, implementations push a new (distance, vertex) pair whenever a vertex's tentative distance improves and, on extraction, discard entries whose distance no longer matches the stored best ("lazy deletion"). The queue must be a min-heap, obtained with `std::greater`, ordered primarily by distance; with up to E pushes, the running time is O((V + E) log E) = O((V + E) log V). Distances should use a type and infinity value, such as 64-bit integers with infinity `LLONG_MAX / 4`, that can't overflow during relaxation.

## 9. Cheat sheet

| Algorithm | C++ essentials |
|---|---|
| Dijkstra | `priority_queue<P, vector<P>, greater<P>>`, skip stale entries |
| 0-1 BFS | `deque`, `push_front` for 0-weight edges |
| topological sort | Kahn with `queue`; an empty result means a cycle |
| DSU | iterative find with path halving + union by size |
| MST | Kruskal (sort + DSU) or Prim (heap) |
| big graphs | CSR arrays, flat `vector<int>` distances |
| INF | `LLONG_MAX / 4` |

> [!INTERVIEW]
> **"Why `LLONG_MAX / 4` and not `LLONG_MAX` for INF?"** Relaxation computes `dist[u] + w`. With `LLONG_MAX`, any addition overflows (UB, and in practice wraps negative, which then looks like a very short path). Dividing by 4 leaves headroom, so INF + w and even INF + INF stay representable, and the comparison logic stays correct without special cases.
