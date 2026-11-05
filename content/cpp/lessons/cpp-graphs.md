# Graph Representation, BFS and DFS

A **graph** is a set of things (vertices) and the connections between them (edges). Road maps, social networks, the cells of a maze, web pages and their links, task dependencies, the states of a puzzle, the joints of a robot arm and the pipes of a water network are all graphs. Once you can see a problem as a graph, two traversal algorithms, **breadth-first search (BFS)** and **depth-first search (DFS)**, already solve a surprising number of them: reachability, connected components, shortest paths when every step costs the same, flood fills, cycle detection and ordering. Every later graph topic (topological sort, Dijkstra, spanning trees, strongly connected components) is built on these two.

This lesson starts from zero: vocabulary, the three ways to store a graph in C++, BFS with path reconstruction, DFS (recursive and iterative) with timestamps, components, grids, and graphs you never store at all.

## 1. Vocabulary

```text
        undirected                     directed (digraph)
   0 ─── 1                         0 ──→ 1
   │   ╱ │                         ↑   ↗ │
   │  ╱  │                         │  ╱  ↓
   2 ─── 3      4                  2 ←── 3      4
```

- **Vertex** (node): one of the things. We number them `0 … n−1`. `n = |V|`.
- **Edge**: a connection. `m = |E|`. In an **undirected** graph `{u, v}` goes both ways; in a **directed** graph `u → v` goes one way only.
- **Adjacent / neighbour**: `v` is a neighbour of `u` if there is an edge from `u` to `v`.
- **Degree** `deg(u)`: the number of edges touching `u`. In a digraph there is an **in-degree** and an **out-degree**. The sum of all degrees in an undirected graph is `2m` (every edge has two ends).
- **Weighted** graphs attach a number (length, cost, time) to each edge. This lesson is about **unweighted** graphs, where each edge counts as one step.
- **Path**: a sequence of vertices where each consecutive pair is an edge. Its **length** is the number of edges.
- **Cycle**: a path that returns to its start without reusing an edge. A graph with no cycles is **acyclic**; a connected acyclic undirected graph is a **tree** (exactly `n − 1` edges). A directed acyclic graph is a **DAG**.
- **Connected component**: a maximal set of vertices that can all reach each other (undirected). Vertex `4` above is a component on its own.
- **Self-loop** `u → u` and **parallel edges** (the same pair twice) are legal in many inputs. Your code should not break on them.
- **Sparse** graphs have `m` close to `n` (roads, grids); **dense** graphs have `m` close to `n²`.

## 2. Storing a graph

### Edge list

Just the list of pairs, exactly as the input gives them: `vector<pair<int,int>> edges`. It uses O(m) memory and is the natural format for algorithms that process edges one by one (Kruskal, Bellman-Ford, union-find). But "who are the neighbours of `u`?" costs O(m).

### Adjacency matrix

An `n × n` table, `adj[u][v] = 1` when the edge exists (or the weight).

```text
     0 1 2 3 4
  0 [0 1 1 0 0]
  1 [1 0 1 1 0]
  2 [1 1 0 1 0]
  3 [0 1 1 0 0]
  4 [0 0 0 0 0]
```

Testing one edge is O(1), but the memory is O(n²) and listing `u`'s neighbours costs O(n) even if it has two. With `n = 10⁵` the matrix would need 10¹⁰ cells. Use it only for small, dense graphs (Floyd-Warshall, `n ≤ ~2000`).

### Adjacency list (the default)

For each vertex, a list of its neighbours. Memory O(n + m), and iterating over `u`'s neighbours costs O(deg(u)), so a full traversal costs O(n + m).

```cpp
vector<vector<int>> build_adj(int n, const vector<pair<int,int>>& edges, bool directed) {
    vector<vector<int>> adj(n);
    for (auto [u, v] : edges) {
        adj[u].push_back(v);
        if (!directed) adj[v].push_back(u);      // undirected: store both directions
    }
    return adj;
}
```

For weighted graphs store `pair<int,int>` (neighbour, weight). When speed really matters, the flat **CSR** layout (one `start` array of size `n+1` and one `to` array of size `m`) does the same with two allocations and better cache behaviour.

| Need | Edge list | Matrix | Adjacency list |
|---|---|---|---|
| memory | O(m) | O(n²) | O(n + m) |
| is `u–v` an edge? | O(m) | O(1) | O(deg u) |
| neighbours of `u` | O(m) | O(n) | O(deg u) |
| full traversal | — | O(n²) | O(n + m) |

## 3. Breadth-first search

BFS explores a graph **in layers**: first the source, then everything one edge away, then everything two edges away, and so on. It uses a **queue** (first in, first out).

```cpp
vector<int> bfs(const vector<vector<int>>& adj, int s) {
    int n = adj.size();
    vector<int> dist(n, -1);                 // -1 = not discovered yet
    queue<int> q;
    dist[s] = 0; q.push(s);
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v : adj[u])
            if (dist[v] == -1) {             // first discovery is the shortest
                dist[v] = dist[u] + 1;
                q.push(v);
            }
    }
    return dist;
}
```

### Dry run

```text
edges: 0-1 0-2 1-3 2-3 3-4         source 0

  0 ── 1
  │    │
  2 ── 3 ── 4

step  pop  discovers (dist)       queue after
 0    -    0(0)                   [0]
 1    0    1(1) 2(1)              [1 2]
 2    1    3(2)                   [2 3]
 3    2    (3 already seen)       [3]
 4    3    4(3)                   [4]
 5    4    -                      []
dist = [0, 1, 1, 2, 3]
```

### Why BFS gives shortest paths

The queue always contains vertices from at most two consecutive layers, `d` and `d + 1`, with all the `d`s in front. So vertices are popped in non-decreasing distance order. When `v` is first discovered from `u`, every vertex closer than `u` has already been popped and none of them was adjacent to `v` (or `v` would have been discovered earlier). So `dist[u] + 1` is the smallest possible. This argument needs every edge to have the **same** length. With weights, BFS is wrong, and you need Dijkstra (a later topic) or 0-1 BFS.

**Mark when you push, not when you pop.** If you set `dist[v]` only when popping, the same vertex can be pushed many times (once per neighbour that sees it), and the queue can grow to O(m).

### Reconstructing the path

Store how each vertex was reached: `parent[v] = u` when `u` discovers `v`. Walking `parent` back from `t` gives the path in reverse.

```cpp
vector<int> bfs_path(const vector<vector<int>>& adj, int s, int t) {
    int n = adj.size();
    vector<int> parent(n, -2);               // -2 = unvisited, -1 = the source
    queue<int> q; q.push(s); parent[s] = -1;
    while (!q.empty()) {
        int u = q.front(); q.pop();
        if (u == t) break;                   // early exit: t's layer is final
        for (int v : adj[u]) if (parent[v] == -2) { parent[v] = u; q.push(v); }
    }
    if (parent[t] == -2) return {};          // unreachable
    vector<int> path;
    for (int v = t; v != -1; v = parent[v]) path.push_back(v);
    reverse(path.begin(), path.end());
    return path;
}
```

If several shortest paths exist and the problem asks for a specific one (say the lexicographically smallest), parent pointers are not enough, because they fix the choices from the end of the path. Run the BFS from `t` instead: then from `s`, any neighbour with `distT[v] == distT[u] − 1` still completes a shortest path, and you can choose greedily (problem *Shortest Path, Lexicographically Smallest*).

## 4. Depth-first search

DFS goes **as deep as possible** before backing up, like exploring a maze with one hand on the wall. Its natural form is recursive.

```cpp
void dfs(const vector<vector<int>>& adj, int u, vector<char>& seen) {
    seen[u] = 1;
    for (int v : adj[u])
        if (!seen[v]) dfs(adj, v, seen);
}
```

### Timestamps

Give DFS a clock. Stamp `tin[u]` when `u` is entered and `tout[u]` when it is left.

```text
digraph: 0→1, 1→2, 0→2, 2→0, 3→1

dfs(0)           tin[0]=0
  dfs(1)         tin[1]=1
    dfs(2)       tin[2]=2
      2→0: 0 is active  → back edge (a cycle!)
    leave 2      tout[2]=3
  leave 1        tout[1]=4
  0→2: 2 finished, tin[0]<tin[2] → forward edge
leave 0          tout[0]=5
dfs(3)           tin[3]=6
  3→1: 1 finished, tin[1]<tin[3] → cross edge
leave 3          tout[3]=7

intervals:  0 [0────────5]   3 [6──7]
            1   [1────4]
            2     [2─3]
```

The **parenthesis theorem**: for any two vertices, their intervals are either nested or disjoint. `u` is an ancestor of `v` in the DFS forest exactly when `tin[u] ≤ tin[v]` and `tout[v] ≤ tout[u]`, an O(1) test. And each edge `u → v` falls into one class, decided when `u` examines it:

| class | condition when examined | meaning |
|---|---|---|
| tree | `v` unvisited | DFS moves into `v` |
| back | `v` active (entered, not left) | points to an ancestor: a **cycle** |
| forward | `v` finished, `tin[u] < tin[v]` | shortcut to a descendant |
| cross | `v` finished, `tin[v] < tin[u]` | to an earlier, finished branch |

In an **undirected** graph only tree and back edges exist. Back edges power cycle detection; finish order powers topological sort; both appear in the next two topics.

### Iterative DFS (no stack overflow)

Every recursive call uses stack memory, and the default stack is about 8 MB. A path of 2·10⁵ vertices (or a snake-shaped region in a 1000 × 1000 grid) nests that many calls and **crashes**. The fix is to manage the stack yourself. To reproduce the recursive order *exactly*, each stack entry needs the vertex and how far it has got through its neighbour list:

```cpp
void dfs_iter(const vector<vector<int>>& adj, int root, vector<int>& tin, vector<int>& tout, int& clock) {
    vector<pair<int,int>> st;                // (vertex, index of the next neighbour)
    tin[root] = clock++; st.push_back({root, 0});
    while (!st.empty()) {
        auto& [u, i] = st.back();
        if (i == (int)adj[u].size()) {       // no neighbours left: "return"
            tout[u] = clock++; st.pop_back();
            continue;
        }
        int v = adj[u][i++];                 // examine ONE edge
        if (tin[v] == -1) { tin[v] = clock++; st.push_back({v, 0}); }   // "recursive call"
    }
}
```

Note the reference `auto& [u, i]` is used before `push_back` can reallocate the vector, which is safe here because we stop using it after the push.

The tempting shortcut "pop `u`, push all its unvisited neighbours" visits every vertex and is fine for **reachability** and **counting**, but it is not a true DFS: it has no finish event and discovers vertices in a different order. Use it only when the order doesn't matter, as in a flood fill.

## 5. Connected components

Scan the vertices; each unvisited one starts a new component, and a traversal from it marks the whole component.

```cpp
int count_components(const vector<vector<int>>& adj, vector<int>& comp) {
    int n = adj.size(), c = 0;
    comp.assign(n, -1);
    vector<int> st;
    for (int s = 0; s < n; ++s) {
        if (comp[s] != -1) continue;
        comp[s] = c; st.push_back(s);
        while (!st.empty()) {
            int u = st.back(); st.pop_back();
            for (int v : adj[u]) if (comp[v] == -1) { comp[v] = c; st.push_back(v); }
        }
        ++c;
    }
    return c;
}
```

Total cost O(n + m): every vertex is pushed once and every adjacency list is scanned once. Afterwards "are `u` and `v` connected?" is `comp[u] == comp[v]`. (When edges arrive online, union-find answers the same question incrementally; that is a later topic.)

## 6. Grid graphs

A grid is a graph you never build. Each cell `(r, c)` is a vertex; its neighbours are the 4 cells sharing a side (or 8 with diagonals). Generate them with direction arrays:

```cpp
const int dr[] = {-1, 1, 0, 0}, dc[] = {0, 0, -1, 1};
// for k in 0..3: (r + dr[k], c + dc[k]), skip if off the grid or blocked
```

Encode a cell as the integer `r * C + c` to keep visited arrays flat.

### Flood fill and islands

"Count the islands of `'1'`s" is connected components on the grid. "Paint the region around a clicked pixel" is a single traversal. "Capture regions not touching the border" is a traversal seeded from **all border cells**, followed by flipping what wasn't reached: when the question is about what is *not* connected to something, flood from that something.

### Multi-source BFS

```text
minute 0       minute 1       minute 2       minute 3
R F F          R R F          R R R          R R R
F F .    →     R F .    →     R R .    →     R R .
. F F          . F F          . R F          . R R
```

Rotting spreads from *every* rotten orange at once. Push **all** sources into the queue with distance 0 and run one BFS. It behaves like a BFS from an imaginary super-source connected to all of them. The same trick computes a **distance field**: for every cell, the distance to the nearest exit / zero / hospital, in O(R·C) instead of one BFS per cell. Because grid moves are symmetric, "distance from the cell to the nearest source" equals "distance from the set of sources to the cell".

```cpp
vector<int> nearest_zero(const vector<string>& g) {      // '0' = source, anything else passable
    int R = g.size(), C = g[0].size();
    const int dr[] = {-1, 1, 0, 0}, dc[] = {0, 0, -1, 1};
    vector<int> d(R * C, -1), q;
    for (int i = 0; i < R * C; ++i) if (g[i / C][i % C] == '0') { d[i] = 0; q.push_back(i); }
    for (size_t h = 0; h < q.size(); ++h) {
        int y = q[h] / C, x = q[h] % C;
        for (int k = 0; k < 4; ++k) {
            int ny = y + dr[k], nx = x + dc[k];
            if (ny < 0 || ny >= R || nx < 0 || nx >= C || d[ny * C + nx] != -1) continue;
            d[ny * C + nx] = d[q[h]] + 1;
            q.push_back(ny * C + nx);
        }
    }
    return d;
}
```

A `vector` with a moving `head` index is a perfectly good queue when every vertex is pushed at most once, and it is faster than `std::queue`.

## 7. Implicit graphs: the state space

Many problems never mention a graph. In **word ladder** ("turn `hit` into `cog` changing one letter at a time, every word in the dictionary"), the vertices are words and the edges join words differing in one letter. The edges are never stored: from a word you **generate** the `25·L` candidates and keep those in a hash set. Puzzles (sliding tiles, locks with rotating wheels, water jugs) are the same: a vertex is a *state*, an edge is a *move*, and the fewest moves is a BFS.

```text
hit → hot → dot → dog → cog          (5 words, 4 moves)
         ↘ lot → log ↗
```

Checklist for a state-space BFS: (1) how do I encode a state so it can be hashed or indexed? (2) how do I generate the moves? (3) how many states can there be (is BFS affordable)? (4) mark states as visited when pushed.

## 8. Copying a graph: clone graph

When a graph lives as objects that point to each other (`struct Node { int val; vector<Node*> nbrs; }`), copying it is a traversal plus a map `unordered_map<Node*, Node*>` from each original to its copy. The map is both the visited set and the way to find the copy of a neighbour that has already been created. On first sight of a node create its copy and enqueue it; when processing `u`, append `copy[v]` for each neighbour `v`. Without the map, a cycle would make the copier loop forever.

## 9. Complexity

- BFS and DFS on an adjacency list: O(n + m) time, O(n) extra memory. Each vertex is discovered once; each adjacency list is scanned once (each undirected edge twice).
- On an adjacency matrix: O(n²), because scanning a row costs `n`.
- Grids: O(R·C) since each cell has at most 4 neighbours.
- Implicit graphs: O(states × moves per state × cost of encoding a state).

## 10. Recognising BFS vs DFS

- **"Fewest steps / moves / minimum number of operations"**, all steps equal: **BFS**.
- **"Spreads simultaneously / nearest X for every cell"**: **multi-source BFS**.
- **"Is it reachable / how many groups / size of each region"**: either; pick the simpler one (iterative stack).
- **"Order of finishing, ancestors, cycles, back edges"**: **DFS** with timestamps or colours.
- **Grids, words, puzzle states**: an implicit graph; generate neighbours on the fly.
- Weighted edges: BFS is **not** enough (shortest-paths topic).

## 11. Common mistakes

- **Marking visited on pop** instead of push: vertices enter the queue many times; memory and time blow up.
- **Recursion on big inputs**: 10⁵+ nested calls overflow the stack. Use an explicit stack.
- **Forgetting the reverse edge** in an undirected graph, or adding it in a directed one.
- **Bounds checks after the access**: check `0 ≤ ny < R` before reading `grid[ny][nx]`.
- **Using BFS on weighted graphs.**
- **Re-running BFS from every source** when one multi-source BFS would do.
- **Assuming the graph is connected**: loop over all vertices to start new traversals.
- **Off-by-one in "length"**: some problems count vertices (word ladder), others count edges.

## 12. Interview questions

> [!INTERVIEW] "Why does BFS find shortest paths but DFS doesn't?"
> BFS pops vertices in non-decreasing distance order, so a vertex's first discovery comes from a vertex one layer closer; nothing shorter can appear later. DFS follows one branch as deep as it goes, so it may reach a vertex first through a long detour.

> [!INTERVIEW] "Adjacency list or matrix?"
> List for sparse graphs: O(n + m) memory and O(deg) neighbour iteration. Matrix only for small dense graphs or when you need O(1) edge tests (Floyd-Warshall, bitset tricks).

> [!EXAM] Give the complexity of counting islands in an R × C grid and justify it.
> O(R·C): every cell is pushed at most once (marked on push) and examines 4 neighbours, so the total work is at most 4·R·C plus the scan.

> [!INTERVIEW] "Your recursive DFS crashes on the large test. What do you do?"
> Replace recursion with an explicit stack that stores (vertex, next-neighbour index), which reproduces the recursive order; or use the simpler push-all-neighbours stack when order doesn't matter.

## Check your understanding

1. In an undirected graph with `n` vertices and `m` edges stored as adjacency lists, how many entries do the lists hold in total?
2. Why must the rotting-oranges BFS start with *all* rotten oranges in the queue rather than running BFS from each?
3. During DFS on a digraph, `u` examines `u → v` and `v` has been entered but not left. What does that tell you?
4. Why does setting `dist[v]` on pop (instead of on push) still give correct distances but hurt performance?
5. Word ladder: what are the vertices, the edges, and why don't you store the edges?

<details><summary>Answers</summary>

1. `2m`: each undirected edge appears in both endpoints' lists (a self-loop added twice to the same list also gives 2).
2. All sources spread simultaneously. One BFS from the set of sources gives each cell its distance to the *nearest* source, in O(R·C). Separate BFS runs cost O(sources · R·C) and then still need a minimum per cell.
3. `v` is an ancestor of `u` on the current DFS path (a back edge), so the graph has a directed cycle `v → … → u → v`.
4. Distances are still correct, because the first time `v` is popped it has the smallest value, but `v` may be pushed once per neighbour that sees it before it's popped, so the queue can hold O(m) entries and the work grows.
5. Vertices are dictionary words (plus `begin`); edges join words that differ in exactly one position. Storing them would take O(n²·L) time to compute; generating the 25·L one-letter variants of the current word and looking them up in a hash set finds the same neighbours in O(L²·25) per word.

</details>
