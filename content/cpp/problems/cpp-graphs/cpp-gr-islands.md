---
id: cpp-gr-islands
title: Islands: Count and Largest Area
difficulty: Easy
order: 2
tags: graphs, grid graph, flood fill, BFS, connected components
time_limit: 2
---
## Statement
A map is a grid of `R` rows and `C` columns. `'1'` is land and `'0'` is water. An **island** is a maximal group of land cells connected **horizontally or vertically** (not diagonally). Return the number of islands and the area (number of cells) of the largest one (0 if there is no land).

```cpp
std::pair<int,int> islands(const std::vector<std::string>& grid);   // {count, largest area}
```

A grid is a graph in disguise: every cell is a vertex, and it has an edge to each of its up to 4 neighbours that is also land. You never build the adjacency list; you generate neighbours on the fly with direction arrays `dr = {-1,1,0,0}`, `dc = {0,0,-1,1}`. The grid can be 1000 × 1000, so a recursive flood fill could need 10⁶ nested calls. Use an explicit stack or queue.

**Input:** cases until the end of input: `R C`, then `R` rows of `C` characters (1 ≤ R, C ≤ 1000).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

pair<int,int> islands(const vector<string>& grid) {
    int land = 0;
    for (auto& row : grid) for (char c : row) land += c == '1';
    return {land, land > 0 ? 1 : 0};        // TODO: counts cells, not islands
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int R, C;
    while (cin >> R >> C) {
        vector<string> g(R);
        for (auto& row : g) cin >> row;
        auto [cnt, big] = islands(g);
        cout << cnt << ' ' << big << '\n';
    }
}
```

## Tests
=== sample
4 5
11000
11000
00100
00011
2 3
000
000
---
3 4
0 0
=== hidden
1 1
1
3 3
101
010
101
3 4
1111
1001
1111
---
1 1
5 1
1 10
=== hidden
6 3
110
011
101
111
111
110
4 1
0
0
1
0
4 1
0
0
1
1
3 1
0
1
0
6 4
1101
1010
1001
1010
1000
0101
---
1 14
1 1
1 2
1 1
7 6
=== hidden
4 3
010
000
100
010
1 4
0100
4 6
001000
000000
000001
000000
4 5
11010
00111
11111
00010
1 3
001
---
3 1
1 1
2 1
2 10
1 1
=== hidden
4 6
011001
000101
011010
100011
6 4
0010
1001
0011
1011
1010
0101
2 5
00000
01000
1 1
0
5 2
11
01
11
11
11
---
6 3
6 6
1 1
0 0
1 9
=== hidden
@gen 1088328997 big
=== hidden
@gen 1088328998 big
=== hidden
@gen 1088328999 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(5 if not big else 1):
    if not big:
        R, C = r.randint(1, 6), r.randint(1, 6); p = r.random()
        print(R, C)
        for _ in range(R): print("".join("1" if r.random() < p else "0" for _ in range(C)))
    else:
        R = C = 1000
        mode = r.randint(0, 1)
        print(R, C)
        for i in range(R):
            if mode == 0:     # serpentine: one giant snake island
                if i % 2 == 0: row = "1" * C
                elif i % 4 == 1: row = "0" * (C - 1) + "1"
                else: row = "1" + "0" * (C - 1)
            else:
                row = "".join("1" if r.random() < 0.55 else "0" for _ in range(C))
            print(row)
```

## Hints
- Each cell is a vertex; its neighbours are the 4 cells sharing a side. Generate them with direction arrays and a bounds check.
- Scan all cells; an unvisited land cell starts a new island. Flood-fill it and count the cells you visit.
- Use an explicit `vector<int>` stack (or a queue) instead of recursion: one island can contain 10⁶ cells.

## Solution
**The grid is an implicit graph.** Cells are vertices; two land cells are adjacent when they share a side. Islands are exactly the connected components of this graph restricted to land.

**Flood fill.** Scan the cells. An unvisited land cell starts a new island; flood it with a traversal that visits every land cell reachable from it, counting cells as they are popped. The traversal order does not matter for counting, so a plain `vector` used as a stack (DFS order) works as well as a queue (BFS order).

**Why not recursion?** A snake-shaped island in a 1000 × 1000 grid has about 5·10⁵ cells in a single chain. A recursive flood fill would nest that deep and overflow the default 8 MB stack. The explicit stack lives on the heap and has no such limit.

**Encoding.** Storing a cell as the single integer `r·C + c` keeps `seen` a flat array and the stack a `vector<int>`, which is cache-friendly.

Complexity: O(R·C) time and memory: each cell is pushed at most once and looks at 4 neighbours.

```cpp
#include <bits/stdc++.h>
using namespace std;

pair<int,int> islands(const vector<string>& grid) {
    int R = grid.size(), C = grid[0].size();
    const int dr[] = {-1, 1, 0, 0}, dc[] = {0, 0, -1, 1};
    vector<char> seen(R * C, 0);                    // cell (r, c) has id r*C + c
    vector<int> stk;
    int count = 0, best = 0;
    for (int r = 0; r < R; ++r)
        for (int c = 0; c < C; ++c) {
            if (grid[r][c] != '1' || seen[r * C + c]) continue;
            ++count;                                // a new island starts here
            int area = 0;
            stk.push_back(r * C + c); seen[r * C + c] = 1;
            while (!stk.empty()) {                  // iterative flood fill: no recursion depth limit
                int id = stk.back(); stk.pop_back();
                ++area;
                int y = id / C, x = id % C;
                for (int k = 0; k < 4; ++k) {
                    int ny = y + dr[k], nx = x + dc[k];
                    if (ny < 0 || ny >= R || nx < 0 || nx >= C) continue;   // off the map
                    if (grid[ny][nx] != '1' || seen[ny * C + nx]) continue;
                    seen[ny * C + nx] = 1;
                    stk.push_back(ny * C + nx);
                }
            }
            best = max(best, area);
        }
    return {count, best};
}
```
