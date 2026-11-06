---
id: cpp-topo-parallel-courses
title: Parallel Courses: Minimum Number of Semesters
difficulty: Medium
order: 6
tags: topological sort, Kahn's algorithm by levels, longest path, DAG
time_limit: 2
---
## Statement
`n` courses with prerequisite pairs `u v` (`u` must be passed in an **earlier** semester than `v`). In one semester you may take **any number** of courses whose prerequisites are all passed. Return the minimum number of semesters needed to pass all courses, or `-1` if it's impossible.

```cpp
int min_semesters(int n, const std::vector<std::pair<int,int>>& pre);       // -1 if impossible
int largest_semester(int n, const std::vector<std::pair<int,int>>& pre);    // only called when possible
```

`largest_semester` returns the number of courses in the busiest semester when every course is taken **as early as possible**.

Run Kahn's algorithm **in rounds**: round 1 takes every course with in-degree 0, round 2 every course freed by round 1, and so on. Taking every available course as early as possible is optimal, and the number of rounds equals the number of vertices on the **longest path** of the DAG.

**Input:** cases until the end of input: `n m`, then `m` pairs `u v` (1 ≤ n ≤ 2·10⁵, 0 ≤ m ≤ 4·10⁵).

**Output (printed by the driver):** the number of semesters and the size of the largest semester (in the as-early-as-possible schedule), or `-1`.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int min_semesters(int n, const vector<pair<int,int>>& pre) {
    return pre.empty() ? 1 : 2;        // TODO
}
int largest_semester(int n, const vector<pair<int,int>>& pre) {
    return n;                          // TODO
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, m;
    while (cin >> n >> m) {
        vector<pair<int,int>> p(m);
        for (auto& [u, v] : p) cin >> u >> v;
        int s = min_semesters(n, p);
        if (s < 0) cout << -1 << '\n';
        else cout << s << ' ' << largest_semester(n, p) << '\n';
    }
}
```

## Tests
=== sample
3 2
0 2
1 2
---
2 2
=== sample
3 3
0 1
1 2
2 0
---
-1
=== hidden
1 0
---
1 1
=== hidden
4 0
---
1 4
=== hidden
5 4
0 1
1 2
2 3
3 4
---
5 1
=== hidden
6 6
0 3
1 3
2 4
3 5
4 5
0 5
---
3 3
=== hidden
4 2
0 2
0 1
7 10
5 2
2 1
2 0
6 2
0 3
4 1
2 3
6 3
2 0
1 5
1 0
7 5
5 1
6 1
5 4
0 3
1 0
2 2
0 1
0 1
2 5
0 1
0 1
0 1
0 1
0 1
---
2 2
-1
1 1
4 3
2 1
2 1
=== hidden
7 7
1 6
1 5
6 4
4 2
0 5
1 4
6 4
4 4
0 1
1 2
0 1
3 1
8 2
5 7
6 3
8 3
6 2
0 7
4 3
5 11
3 1
4 2
4 3
3 1
4 3
3 1
3 1
3 1
1 0
1 2
0 4
7 2
2 3
4 0
---
4 3
3 2
2 6
2 5
-1
2 5
=== hidden
5 2
3 0
3 1
7 5
4 5
0 5
0 5
6 5
1 3
8 3
1 5
7 1
1 5
4 0
2 3
1 0
1 0
0 1
8 0
---
2 3
2 5
3 6
1 4
-1
1 8
=== hidden
@gen 3923715473 big
=== hidden
@gen 3923715474 big
=== hidden
@gen 3923715475 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    if not big:
        n = r.randint(1, 8); m = r.randint(0, 10)
        dag = r.random() < 0.8
    else:
        n = 200000; m = 400000; dag = r.random() < 0.8
    perm = list(range(n)); r.shuffle(perm)
    es = []
    for _ in range(m):
        a, b = r.randrange(n), r.randrange(n)
        if a == b: continue
        if a > b: a, b = b, a
        if big and r.random() < 0.95: b = min(n - 1, a + r.randint(1, 20))
        if a == b: continue
        es.append((perm[a], perm[b]))
    if not dag and n > 1: es.append((perm[n - 1], perm[0]))
    print(n, len(es))
    for u, v in es: print(u, v)
```

## Hints
- A course can't be taken before 1 + (the latest semester of its prerequisites).
- Run Kahn's algorithm one whole frontier at a time; each frontier is one semester.
- If some courses are never freed, there's a cycle: answer -1.

## Solution
**Levels.** Define `level(v)` = 1 if `v` has no prerequisites, otherwise 1 + max level of its prerequisites. Course `v` can't be passed before semester `level(v)` (induction along the longest chain ending at `v`), and taking every course exactly in semester `level(v)` is valid, since all prerequisites have smaller levels. So the answer is the maximum level: the number of vertices on the longest path.

**Kahn by rounds computes levels.** Keep the current frontier (in-degree 0 now). Removing the whole frontier at once frees exactly the courses whose last prerequisite was in this round, which is level + 1. The number of rounds is the answer; courses never freed mean a cycle, so `-1`.

**Why greedy is safe here.** With unlimited capacity, taking a course early never blocks anything. (With "at most k courses per semester" the problem becomes NP-hard in general, and greedy rules can fail.)

Complexity: O(n + m).

```cpp
#include <bits/stdc++.h>
using namespace std;

// returns the size of each semester in the as-early-as-possible schedule, or {} on a cycle
static vector<int> semesters(int n, const vector<pair<int,int>>& pre) {
    vector<vector<int>> adj(n);
    vector<int> indeg(n, 0);
    for (auto [u, v] : pre) { adj[u].push_back(v); ++indeg[v]; }
    vector<int> cur, nxt, sizes;
    for (int i = 0; i < n; ++i) if (!indeg[i]) cur.push_back(i);
    int taken = 0;
    while (!cur.empty()) {                       // one iteration = one semester
        sizes.push_back(cur.size());
        taken += cur.size();
        nxt.clear();
        for (int u : cur) for (int v : adj[u]) if (--indeg[v] == 0) nxt.push_back(v);
        swap(cur, nxt);
    }
    if (taken < n) return {};
    return sizes;
}
int min_semesters(int n, const vector<pair<int,int>>& pre) {
    auto s = semesters(n, pre);
    return s.empty() ? -1 : (int)s.size();
}
int largest_semester(int n, const vector<pair<int,int>>& pre) {
    auto s = semesters(n, pre);
    return s.empty() ? 0 : *max_element(s.begin(), s.end());
}
```
