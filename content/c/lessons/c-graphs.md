# Graphs

A **graph** is a set of vertices connected by edges. It models road maps and robot navigation grids, networks, dependencies, state machines, social relations and circuits. Graph algorithms (**BFS**, **DFS**, **topological sort**, **Dijkstra**, union-find) are among the most valuable and most interviewed algorithms in computer science. This lesson covers representations in C and the core algorithms, implemented with plain arrays.

## 1. Representations

| Representation | Memory | Edge check (u, v) | Iterate the neighbours of u | Best for |
|---|---|---|---|---|
| adjacency matrix `int adj[V][V]` | O(V²) | **O(1)** | O(V) | dense graphs, small V |
| adjacency list | O(V + E) | O(deg u) | **O(deg u)** | sparse graphs (most real graphs) |
| edge list `struct {u, v, w}[]` | O(E) | O(E) | O(E) | Kruskal, Bellman-Ford |

A cache-friendly adjacency list in C uses **CSR** (compressed sparse row) arrays instead of a linked list per vertex:

```c
/* the neighbours of u are adj[start[u] .. start[u+1]-1] */
typedef struct {
    int V, E;
    int *start;      /* V + 1 offsets */
    int *adj;        /* E neighbour ids */
    int *w;          /* optional edge weights */
} Graph;

Graph build_csr(int V, int E, const int (*edges)[2]) {
    Graph g = {V, E, calloc(V + 1, sizeof(int)), malloc(E * sizeof(int)), NULL};
    for (int i = 0; i < E; i++) g.start[edges[i][0] + 1]++;            /* count out-degrees */
    for (int v = 0; v < V; v++) g.start[v + 1] += g.start[v];          /* prefix sums give the offsets */
    int *pos = malloc(V * sizeof(int));
    memcpy(pos, g.start, V * sizeof(int));
    for (int i = 0; i < E; i++) g.adj[pos[edges[i][0]]++] = edges[i][1];   /* place the neighbours */
    free(pos);
    return g;
}
```

## 2. Breadth-first search: shortest paths in unweighted graphs

```c
/* dist[v] = number of edges from s, or -1 if unreachable */
void bfs(const Graph *g, int s, int *dist) {
    int *queue = malloc(g->V * sizeof(int));
    int head = 0, tail = 0;
    for (int v = 0; v < g->V; v++) dist[v] = -1;
    dist[s] = 0;
    queue[tail++] = s;
    while (head < tail) {
        int u = queue[head++];
        for (int k = g->start[u]; k < g->start[u + 1]; k++) {
            int v = g->adj[k];
            if (dist[v] == -1) {           /* first time seen = shortest */
                dist[v] = dist[u] + 1;
                queue[tail++] = v;
            }
        }
    }
    free(queue);
}
```

BFS explores in order of distance, so the first visit to a vertex is via a shortest path. It's O(V + E). On a robot's occupancy grid, the cells are vertices and their 4 or 8 neighbours are the edges.

## 3. Depth-first search: structure

DFS goes as deep as possible before backtracking. It's used for connectivity, cycle detection, topological sort, and strongly connected components:

```c
enum { WHITE, GRAY, BLACK };   /* unvisited, on the current path, finished */

int dfs_has_cycle(const Graph *g, int u, int *color) {   /* directed graph */
    color[u] = GRAY;
    for (int k = g->start[u]; k < g->start[u + 1]; k++) {
        int v = g->adj[k];
        if (color[v] == GRAY) return 1;                    /* a back edge: cycle */
        if (color[v] == WHITE && dfs_has_cycle(g, v, color)) return 1;
    }
    color[u] = BLACK;
    return 0;
}
```

> [!WARNING]
> Recursive DFS on a graph with a million vertices in a chain overflows the stack (8 MB default). Use an explicit stack array for large graphs, exactly like the recursive flood fill problem in the Recursion module.

## 4. Topological sort (Kahn's algorithm)

Order the vertices of a **DAG** so every edge goes forward: build order, task scheduling, course prerequisites.

```c
int topo_sort(const Graph *g, int *order) {        /* returns the number of vertices placed; < V means a cycle */
    int *indeg = calloc(g->V, sizeof(int)), *q = malloc(g->V * sizeof(int));
    int head = 0, tail = 0, n = 0;
    for (int u = 0; u < g->V; u++)
        for (int k = g->start[u]; k < g->start[u + 1]; k++) indeg[g->adj[k]]++;
    for (int v = 0; v < g->V; v++) if (indeg[v] == 0) q[tail++] = v;
    while (head < tail) {
        int u = q[head++];
        order[n++] = u;
        for (int k = g->start[u]; k < g->start[u + 1]; k++)
            if (--indeg[g->adj[k]] == 0) q[tail++] = g->adj[k];
    }
    free(indeg); free(q);
    return n;
}
```

## 5. Weighted shortest paths and friends

| Problem | Algorithm | Complexity |
|---|---|---|
| single source, non-negative weights | **Dijkstra** with a binary heap | O((V + E) log V) |
| negative weights / detect negative cycles | Bellman-Ford | O(V·E) |
| all pairs (small V) | Floyd-Warshall | O(V³) |
| goal-directed search with a heuristic | **A*** (robot path planning) | depends on the heuristic |
| minimum spanning tree | Kruskal (sort + union-find) or Prim (heap) | O(E log E) |
| dynamic connectivity | **union-find** (disjoint sets) with path compression and union by rank | ~O(α(n)) per operation |

```c
/* union-find: an essential tool */
int find(int *parent, int x) {
    while (parent[x] != x) {
        parent[x] = parent[parent[x]];      /* path halving */
        x = parent[x];
    }
    return x;
}
void unite(int *parent, int *rank, int a, int b) {
    a = find(parent, a); b = find(parent, b);
    if (a == b) return;
    if (rank[a] < rank[b]) { int t = a; a = b; b = t; }
    parent[b] = a;
    if (rank[a] == rank[b]) rank[a]++;
}
```

## 6. Exam-ready answers

> [!EXAM]
> **Graphs and traversal.** A graph consists of vertices and edges, which may be directed or undirected and weighted or unweighted. It is represented by an adjacency matrix, giving constant-time edge queries in O(V²) space, or by adjacency lists, using O(V + E) space and allowing efficient iteration over neighbours, which suits sparse graphs. Breadth-first search uses a queue to visit vertices in order of increasing distance from the source, finding shortest paths in unweighted graphs in O(V + E) time. Depth-first search explores as far as possible along each branch, using recursion or an explicit stack, and supports cycle detection (via back edges), connectivity analysis and topological sorting. Kahn's algorithm produces a topological order of a directed acyclic graph by repeatedly removing vertices with zero in-degree. Dijkstra's algorithm computes shortest paths with non-negative weights using a priority queue.

## 7. Cheat sheet

| Need | Algorithm |
|---|---|
| fewest steps, unweighted | BFS |
| reachability, components, cycles | DFS (iterative for big graphs) |
| dependency order | Kahn's topological sort |
| weighted shortest path | Dijkstra (non-negative weights) |
| path planning with a heuristic | A* |
| "are a and b connected?" with merges | union-find |
| compact adjacency in C | CSR arrays (`start[]`, `adj[]`) |

> [!INTERVIEW]
> **"Number of islands in a grid."** Treat the land cells as vertices, adjacent horizontally and vertically. Scan the grid, and for each unvisited land cell start a BFS/DFS that marks its whole island visited, then increment the count. That's O(rows × cols). Use an explicit stack or queue instead of recursion for big grids. Alternatives: union-find over the land cells (counting components). Follow-ups: the largest island's size, islands with diagonals, and the dynamic version (cells turning into land one by one, which is where union-find shines).
