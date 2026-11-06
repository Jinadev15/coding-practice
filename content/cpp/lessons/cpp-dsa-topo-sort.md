# Topological Sort and DAG Dynamic Programming

A **topological order** of a directed graph lists its vertices so that every edge `u → v` goes from left to right: `u` appears before `v`. Whenever things depend on other things, you need one. A compiler builds libraries before the programs that link them, `make` and `cmake` order build steps, a package manager installs dependencies first, a spreadsheet recalculates cells after the cells they reference, a university lists prerequisites, a project manager schedules tasks, and a neural-network framework evaluates layers in dependency order. A topological order exists **exactly when the graph has no directed cycle**, so producing one also answers "is there a circular dependency?".

Once you have the order, a second idea follows: **dynamic programming on a DAG**. Processing vertices in topological order guarantees that everything a vertex depends on is already computed. Longest paths, critical paths, counting paths and earliest-start schedules all become one linear pass.

## 1. The idea in a picture

```text
   socks ──→ shoes ←── trousers ←── underwear
                          │
   shirt ──→ tie ──→ jacket ←┘
     └───→ belt ───↗

one valid order:  underwear  socks  trousers  shoes  shirt  belt  tie  jacket
another:          shirt  underwear  trousers  belt  tie  jacket  socks  shoes
```

Usually there are many valid orders. A problem either accepts any of them, or adds a **tie-break** (smallest label first, a priority rule), and then the algorithm has to make the right choice at each step.

A DAG always has at least one **source** (a vertex with in-degree 0): follow edges backwards from any vertex; without cycles you must stop somewhere, and that vertex has no incoming edge. That observation is the whole proof behind Kahn's algorithm.

## 2. Kahn's algorithm (BFS by in-degree)

Repeatedly output a vertex with no remaining incoming edges and delete its outgoing edges.

```cpp
// returns a topological order, or an empty vector if the graph has a cycle
vector<int> kahn(int n, const vector<pair<int,int>>& edges) {
    vector<vector<int>> adj(n);
    vector<int> indeg(n, 0);
    for (auto [u, v] : edges) { adj[u].push_back(v); ++indeg[v]; }
    vector<int> order;
    for (int i = 0; i < n; ++i) if (indeg[i] == 0) order.push_back(i);
    for (size_t h = 0; h < order.size(); ++h)          // `order` doubles as the queue
        for (int v : adj[order[h]])
            if (--indeg[v] == 0) order.push_back(v);   // last incoming edge removed
    if ((int)order.size() < n) return {};              // the rest is on or behind a cycle
    return order;
}
```

### Dry run

Edges `0→2, 1→2, 2→3, 1→4, 4→3`:

| step | pop | output so far | in-degree updates | queue after |
|---|---|---|---|---|
| init | – | – | indeg = [0,0,2,2,1] | 0 1 |
| 1 | 0 | 0 | 2: 2→1 | 1 |
| 2 | 1 | 0 1 | 2: 1→0 (push), 4: 1→0 (push) | 2 4 |
| 3 | 2 | 0 1 2 | 3: 2→1 | 4 |
| 4 | 4 | 0 1 2 4 | 3: 1→0 (push) | 3 |
| 5 | 3 | 0 1 2 4 3 | – | – |

All 5 vertices came out, so the graph is a DAG. If a cycle existed, its vertices would keep a positive in-degree forever, the queue would empty early, and `order.size() < n`.

**Correctness.** A vertex is output only when all its predecessors have been output (its in-degree reached 0), so every edge goes left to right. Conversely, if the graph is a DAG, the remaining graph always has a source, so the queue never empties before all vertices are output. Each vertex is pushed once and each edge decremented once: **O(n + m)**.

## 3. DFS finish order

In a DFS, a vertex **finishes** only after everything reachable from it has finished. For an edge `u → v` in a DAG, when `u` examines it, `v` is either white (it will be explored and finish before `u`) or black (already finished). It can't be grey, because that would be a back edge, i.e. a cycle. So `v` always finishes before `u`, and **reversing the finish order** gives a topological order.

```cpp
// iterative DFS: safe for 2*10^5-long chains; returns {} on a cycle
vector<int> topo_dfs(const vector<vector<int>>& adj) {
    int n = adj.size();
    vector<char> color(n, 0);                  // 0 white, 1 grey, 2 black
    vector<int> it(n, 0), st, post;
    for (int r = 0; r < n; ++r) {
        if (color[r]) continue;
        color[r] = 1; st.push_back(r);
        while (!st.empty()) {
            int u = st.back();
            if (it[u] == (int)adj[u].size()) { color[u] = 2; post.push_back(u); st.pop_back(); continue; }
            int v = adj[u][it[u]++];
            if (color[v] == 0) { color[v] = 1; st.push_back(v); }
            else if (color[v] == 1) return {};   // back edge: cycle
        }
    }
    reverse(post.begin(), post.end());
    return post;
}
```

Dry run on the same graph, roots in order 0, 1, …:

```text
dfs 0 → 2 → 3      finish 3, finish 2, finish 0
dfs 1 → (2 black) → 4 → (3 black)      finish 4, finish 1
post order:   3 2 0 4 1
reversed:     1 4 0 2 3        check: 0→2 ✓ 1→2 ✓ 2→3 ✓ 1→4 ✓ 4→3 ✓
```

**Kahn or DFS?** Both are O(n + m). Kahn is easier to steer (heaps, levels) and never recurses. DFS fits when you already run a DFS for something else (cycle extraction, strongly connected components, reachability).

## 4. Steering the order

### Smallest label first

Kahn leaves the choice of *which* source to output open. Replace the queue by a **min-heap** and you always output the smallest available vertex, which produces the **lexicographically smallest** topological order (minimising the first position, then the second, …). Cost O(n log n + m).

A FIFO queue is *not* enough. With edges `0 → 3` and `1 → 2`, the queue outputs `0 1 3 2` (3 was freed first), the heap outputs `0 1 2 3`.

### "Most urgent first" is a different problem

Sometimes the goal is to make task 0 as early as possible, then task 1, and so on. The lexicographically smallest order fails: with `2 → 0` and task 1 free, it outputs `1 2 0`, but `2 0 1` places task 0 earlier. The fix is to **fill the order from the back**: reverse all edges, run Kahn with a **max-heap** (the least urgent available task takes the last free slot), then reverse the result. An exchange argument shows that putting the largest available label last never hurts any more urgent task.

### Levels (parallel rounds)

Process Kahn's queue one whole frontier at a time. Round 1 is all sources, round 2 everything they free, and so on. The round number of `v` equals the number of vertices on the longest path ending at `v`. That answers "minimum number of semesters" (unlimited courses per semester) and "how many parallel steps does this build need?".

```cpp
int rounds(int n, const vector<pair<int,int>>& edges) {     // -1 if there is a cycle
    vector<vector<int>> adj(n);
    vector<int> indeg(n, 0);
    for (auto [u, v] : edges) { adj[u].push_back(v); ++indeg[v]; }
    vector<int> cur, nxt;
    for (int i = 0; i < n; ++i) if (!indeg[i]) cur.push_back(i);
    int r = 0, done = 0;
    while (!cur.empty()) {
        ++r; done += cur.size(); nxt.clear();
        for (int u : cur) for (int v : adj[u]) if (--indeg[v] == 0) nxt.push_back(v);
        swap(cur, nxt);
    }
    return done == n ? r : -1;
}
```

## 5. Building the graph from data: alien dictionary

Often the edges are hidden in the input. Given words sorted in an unknown alphabet, each **adjacent pair** gives at most one fact: at the first position where they differ, the earlier word's letter comes first (`"wrt"` < `"wrf"` ⇒ `t` before `f`). If one word is a prefix of the next, nothing is learned, unless the longer word comes first, which is impossible. Then topologically sort the letters. Two mistakes to avoid: drawing edges from *later* positions (they carry no information), and forgetting the prefix check.

## 6. DP on a DAG

Topological order means: when you reach `v`, every predecessor `u` of `v` is already final. So any recurrence of the form "value of `v` from the values of its predecessors" is computed in one pass.

**Longest path** (in general graphs NP-hard, in a DAG linear):

```cpp
// longest path (sum of edge weights) ending anywhere, over a DAG given in topological order
long long longest_path(int n, const vector<vector<pair<int,int>>>& adj, const vector<int>& topo) {
    vector<long long> best(n, 0);              // longest path ending at v
    for (int u : topo)
        for (auto [v, w] : adj[u])
            best[v] = max(best[v], best[u] + w);
    return n ? *max_element(best.begin(), best.end()) : 0;
}
```

**Number of paths** from `s` to every vertex: `ways[s] = 1`, then `ways[v] += ways[u]` in topological order (modulo a prime when counts explode).

**Critical path method (project scheduling).** Tasks with durations `d` and dependencies form a DAG.

- Forward pass in topological order: earliest start `ES[v] = max(ES[u] + d[u])` over predecessors.
- `T = max(ES + d)`: the project length with unlimited parallelism.
- Backward pass in reverse order: latest finish `LF[u] = min(LF[v] − d[v])` over successors (`T` for tasks without successors).
- **Slack** = `LF − d − ES`. Tasks with slack 0 are **critical**; delaying any of them delays the project.

```text
task: A(3) → B(2) → D(1) → E(5)        ES:  A0 B3 C3 D7 E8   T = 13
      A(3) → C(4) → D                   LF:  A3 B7 C7 D8 E13
                C → F(2)                     F: ES 7, LF 13 → slack 4
critical: A C D E                (B has slack 2, F has slack 4)
```

### Counting topological orders (small n)

The number of orders can be astronomically large, and no polynomial algorithm is known in general. For `n ≤ 20`, note that a partial order's future depends only on **which set** is already placed: `dp[S]` = number of ways to order exactly the set `S`; `dp[S | 1<<v] += dp[S]` whenever all predecessors of `v` are in `S`. That's O(2ⁿ·n), the classic **DP over subsets**.

## 7. Complexity summary

| task | method | time |
|---|---|---|
| any topological order / cycle test | Kahn or DFS finish order | O(n + m) |
| lexicographically smallest order | Kahn + min-heap | O(n log n + m) |
| most-urgent-first order | reversed graph + max-heap, reverse | O(n log n + m) |
| parallel rounds (semesters) | Kahn by frontier | O(n + m) |
| longest path, path counts, critical path | DP in topological order | O(n + m) |
| count all topological orders, n ≤ 20 | DP over subsets | O(2ⁿ · n) |

## 8. Recognising a topological sort

- Words like **prerequisite, depends on, must come before, build order, schedule, compile order, recipe steps**.
- "Is it possible to finish all…?" is cycle detection in a directed graph.
- "Order the …", "earliest time", "minimum number of rounds/semesters", "longest chain" on precedence constraints: topological order, often followed by a DP.
- Tie-break rules in the statement (smallest label, priorities) tell you which heap to use and from which end to build.
- Hidden edges: sorted words, ranking comparisons, "a must be less than b" facts.

## 9. Common mistakes

- **Edge direction.** "a depends on b" means `b → a`. Decide once and write it in a comment.
- **Returning a partial order when there is a cycle.** Always check that all `n` vertices were output.
- **Using a FIFO queue when the statement asks for the smallest order**, or a min-heap when it asks for "most urgent first".
- **Recursive DFS on long chains**: stack overflow at 10⁵+ vertices.
- **Duplicate edges in Kahn.** They are harmless as long as each copy increments the in-degree and each copy decrements it. Deduplicating only one side breaks the counts.
- **DP in the wrong order.** Longest/shortest path needs topological order forward, latest times need reverse order.
- **Overflow** in schedules: 2·10⁵ durations of 10⁹ need `long long`.

## 10. Interview questions

> [!INTERVIEW] "Course schedule: can you finish all courses?"
> Build edges prerequisite → course, run Kahn's algorithm, and check whether all n courses were output. O(n + m). A three-colour DFS works too and can also return the offending cycle.

> [!INTERVIEW] "Why is reverse DFS post-order a topological order?"
> For any edge u → v in a DAG, v finishes before u: if v is white when u examines the edge, v's whole DFS completes inside u's; if v is black it already finished; it can't be grey without a cycle. Sorting by decreasing finish time therefore puts u before v.

> [!EXAM] Longest path is NP-hard in general graphs. Why is it O(n + m) in a DAG?
> In a DAG, processing vertices in topological order guarantees every predecessor's best value is final before it is used, so `best[v] = max(best[u] + w)` is a correct one-pass DP. With cycles there is no such order, and paths could loop.

> [!EXAM] What is the minimum number of semesters for prerequisites 0→1, 1→2, 0→3, 3→2, with any number of courses per semester?
> 3: semester 1 takes {0}, semester 2 takes {1, 3}, semester 3 takes {2}. It's the number of vertices on the longest path 0→1→2.

## Check your understanding

1. Kahn's algorithm stops with 7 of 10 vertices output. What do you know about the other 3?
2. Why does every DAG have at least one vertex of in-degree 0?
3. In the critical-path example, why is task F not critical even though it ends at time 9 < T?
4. Give a 3-vertex example where the lexicographically smallest topological order differs from the "task 0 as early as possible" order.
5. Why does the subset DP count each topological order exactly once?

<details><summary>Answers</summary>

1. Each of them lies on a directed cycle or is reachable from one (its in-degree never reached 0). The graph is not a DAG.
2. Start anywhere and walk backwards along incoming edges. Without cycles you can never repeat a vertex, so the walk must stop after at most n steps, at a vertex with no incoming edge.
3. F's latest finish is T = 13 because nothing depends on it, so it can start as late as 11 instead of 7: slack 4. Only tasks with slack 0 are critical.
4. Edge `2 → 0`, vertex 1 free. Smallest order: `1 2 0`. Most-urgent-first: `2 0 1`, which places 0 at position 1 instead of 2.
5. Each order corresponds to exactly one chain of sets ∅ ⊂ {v₁} ⊂ {v₁, v₂} ⊂ … ⊂ V, and the DP adds exactly one contribution per step along each chain. Different orders give different chains, and every valid chain is a valid order.

</details>
