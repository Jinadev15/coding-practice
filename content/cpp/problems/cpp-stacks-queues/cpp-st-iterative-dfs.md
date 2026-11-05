---
id: cpp-st-iterative-dfs
title: Deep DFS without Recursion
difficulty: Hard
order: 9
tags: stack, dfs, call stack, recursion elimination, trees
time_limit: 2
---
## Statement
```cpp
std::vector<std::pair<int,int>> euler_times(int n, const std::vector<int>& parent);
```

A rooted tree has nodes `0 … n−1`, root `0`, and `parent[v]` for every `v ≥ 1` (`parent[0] = −1`). Run a depth-first search from the root that visits the children of each node in **increasing** index order, with one shared clock starting at 0:

```text
dfs(v):  tin[v]  = clock++
         for each child c of v, in increasing order: dfs(c)
         tout[v] = clock++
```

Return `{tin[v], tout[v]}` for every node. (Node `u` is an ancestor of `v` exactly when `tin[u] < tin[v]` and `tout[v] < tout[u]`.)

The starter is this recursion, and it is correct. But the tree can be a path of 10⁶ nodes: a recursion one million calls deep overflows the default 8 MB call stack and crashes. Rewrite it with an **explicit stack** that produces exactly the same times.

**Input:** cases until the end of input: `n`, then `n − 1` integers `parent[1] … parent[n−1]` (n ≤ 10⁶). Print `tin tout` for nodes 0 … n−1, one per line.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

static void dfs(int v, const vector<vector<int>>& ch, vector<pair<int,int>>& t, int& clock) {
    t[v].first = clock++;
    for (int c : ch[v]) dfs(c, ch, t, clock);          // recursion depth = tree height
    t[v].second = clock++;
}

vector<pair<int,int>> euler_times(int n, const vector<int>& parent) {
    vector<vector<int>> ch(n);
    for (int v = 1; v < n; ++v) ch[parent[v]].push_back(v);   // increasing v: children come out sorted
    vector<pair<int,int>> t(n);
    int clock = 0;
    dfs(0, ch, t, clock);
    return t;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<int> p(n, -1);
        for (int v = 1; v < n; ++v) cin >> p[v];
        auto t = euler_times(n, p);
        string out;
        for (auto [a, b] : t) { out += to_string(a); out += ' '; out += to_string(b); out += '\n'; }
        cout << out;
    }
}
```

## Tests
=== sample
5
0 0 1 1
4
0 1 2
---
0 9
1 6
7 8
2 3
4 5
0 7
1 6
2 5
3 4
=== hidden
1

6
3 0 0 2 2
7
0 0 0 0 0 0
---
0 1
0 11
8 9
1 6
7 10
2 3
4 5
0 13
1 2
3 4
5 6
7 8
9 10
11 12
=== hidden
7
0 3 0 0 0 3
8
5 3 7 0 7 5 0
8
2 4 6 0 4 4 3
8
0 6 0 1 0 1 0
5
0 1 2 1
---
0 13
1 2
4 5
3 8
9 10
11 12
6 7
0 15
9 10
5 6
4 7
1 2
8 13
11 12
3 14
0 15
3 4
2 5
9 12
1 14
6 7
8 13
10 11
0 15
1 8
5 6
9 10
2 3
11 12
4 7
13 14
0 9
1 8
2 5
3 4
6 7
=== hidden
9
8 0 0 0 6 3 8 0
5
3 0 0 3
2
0
1

6
4 0 2 5 2
---
0 17
12 13
1 2
3 8
9 10
5 6
4 7
14 15
11 16
0 9
4 5
1 2
3 8
6 7
0 3
1 2
0 1
0 11
6 7
1 10
2 3
5 8
4 9
=== hidden
7
0 0 4 5 0 1
2
0
8
7 7 7 0 3 0 6
7
4 6 4 0 2 4
1

---
0 13
1 4
5 6
9 10
8 11
7 12
2 3
0 3
1 2
0 15
5 6
7 8
9 12
1 2
10 11
3 14
4 13
0 13
2 3
7 10
4 5
1 12
8 9
6 11
0 1
=== hidden
@gen 2574686495 big
=== hidden
@gen 2574686496 big
=== hidden
@gen 2574686497 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(5 if not big else 1):
    n = r.randint(1, 10) if not big else 1000000
    kind = r.random()
    perm = list(range(1, n)); r.shuffle(perm); order = [0] + perm   # random labels, root 0
    par = [-1] * n
    for i in range(1, n):
        if big: j = max(0, i - r.choice([1, 1, 1, 2]))           # depth > n/2: far too deep to recurse
        else: j = r.randrange(i)
        par[order[i]] = order[j]
    print(n); print(*par[1:])
```

## Hints
- What does each active call of `dfs` need to remember while its child is running? That is your stack frame.
- A frame `(v, i)` = "node v, and the next child to visit is number i". Look at the top frame: either call the next child, or finish v.
- Do `tin` when pushing, `tout` when popping. Be careful with references into a vector that you then `push_back` into.

## Solution
A recursive call is a **stack frame**: the function's local variables plus the place to resume. Here the only state `dfs(v)` keeps across a call is `v` and *how far its child loop has got*. So a frame is the pair `(v, next child index)`, and an explicit `vector` of frames replaces the call stack:

- **call** `dfs(c)`: do the entry work (`tin[c] = clock++`) and push `(c, 0)`;
- **resume**: look at the top frame; if it has another child, advance its index and call that child;
- **return**: when the child loop is exhausted, do the exit work (`tout[v] = clock++`) and pop.

This produces the same order as the recursion because it *is* the recursion, executed by hand. The explicit stack lives on the heap (a vector of 10⁶ pairs is 8 MB of heap, no problem), while the real call stack is limited to 8 MB in total, and each real frame of `dfs` costs far more than 8 bytes.

A tempting shortcut, "pop a node, push all its children in reverse", gives the right **entry** order but has no moment at which a node's subtree is finished, so it cannot compute `tout`. The `(node, iterator)` frame is the general technique.

The children are stored in one flat array (CSR) instead of `vector<vector<int>>`, which avoids a million small allocations.

Complexity: O(n) time and memory.

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<pair<int,int>> euler_times(int n, const vector<int>& parent) {
    // children in CSR form (one flat array): start[v] .. start[v+1]-1, sorted because v increases
    vector<int> start(n + 1, 0), kids(max(0, n - 1));
    for (int v = 1; v < n; ++v) ++start[parent[v] + 1];
    for (int v = 0; v < n; ++v) start[v + 1] += start[v];
    vector<int> fill(start.begin(), start.end() - 1);
    for (int v = 1; v < n; ++v) kids[fill[parent[v]]++] = v;

    vector<pair<int,int>> t(n);
    vector<pair<int,int>> st;                 // a "stack frame": (node, index of the next child to visit)
    st.reserve(n);
    int clock = 0;
    t[0].first = clock++;
    st.push_back({0, start[0]});
    while (!st.empty()) {
        auto& [v, next] = st.back();
        if (next < start[v + 1]) {            // the loop in dfs(v) has another child: "call" it
            int c = kids[next++];
            t[c].first = clock++;
            st.push_back({c, start[c]});      // invalidates v/next, so they are not used after this
        } else {                              // the loop is finished: "return" from dfs(v)
            t[v].second = clock++;
            st.pop_back();
        }
    }
    return t;
}
```
