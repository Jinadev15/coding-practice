---
id: cpp-gr-nearest-exit-field
title: Distance to the Nearest Exit for Every Cell
difficulty: Medium
order: 5
tags: BFS, multi-source BFS, distance field, grid graph
time_limit: 2
---
## Statement
A building plan is a grid of `'.'` (open floor), `'#'` (wall) and `'E'` (exit). People move between open/exit cells that share a side, one step per move, and cannot enter walls. For **every** cell, compute the number of steps to the **nearest** exit: `0` on an exit, `-1` for walls and for open cells that cannot reach any exit.

```cpp
std::vector<std::vector<int>> exit_distances(const std::vector<std::string>& grid);
```

This is the "distance field" use of multi-source BFS. Computing a BFS from every cell separately costs O((R·C)²). Reverse the question: the distance from cell `x` to its nearest exit is the distance from the **set of exits** to `x`, because moves are symmetric. A single BFS seeded with all exits fills in the whole field.

**Input:** cases until the end of input: `R C`, then `R` rows (1 ≤ R, C ≤ 1000).

**Output (printed by the driver):** the sum of all non-negative distances, the maximum distance, the number of `-1` open cells, and the full field when R·C ≤ 64.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<vector<int>> exit_distances(const vector<string>& grid) {
    int R = grid.size(), C = grid[0].size();
    vector<vector<int>> d(R, vector<int>(C, -1));
    for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) if (grid[r][c] == 'E') d[r][c] = 0;
    return d;                          // TODO: fill in the open cells
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
        auto d = exit_distances(g);
        long long sum = 0; int mx = -1, cut = 0;
        for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) {
            if (d[r][c] >= 0) { sum += d[r][c]; mx = max(mx, d[r][c]); }
            else if (g[r][c] != '#') ++cut;
        }
        cout << "sum " << sum << " max " << mx << " unreachable " << cut << '\n';
        if (R * C <= 64) for (auto& row : d) { for (int c = 0; c < C; ++c) cout << (c ? " " : "") << row[c]; cout << '\n'; }
    }
}
```

## Tests
=== sample
4 5
E...#
.##..
.#..E
...#.
---
sum 26 max 4 unreachable 0
0 1 2 3 -1
1 -1 -1 2 1
2 -1 2 1 0
3 4 3 -1 1
=== sample
2 3
..#
#.#
---
sum 0 max -1 unreachable 3
-1 -1 -1
-1 -1 -1
=== hidden
1 1
E
---
sum 0 max 0 unreachable 0
0
=== hidden
3 3
...
.E.
...
---
sum 12 max 2 unreachable 0
2 1 2
1 0 1
2 1 2
=== hidden
3 4
E#..
.#.E
.#..
---
sum 10 max 2 unreachable 0
0 -1 2 1
1 -1 1 0
2 -1 2 1
=== hidden
3 2
.#
.E
..
1 2
..
2 3
E##
...
3 1
#
.
#
---
sum 6 max 2 unreachable 0
2 -1
1 0
2 1
sum 0 max -1 unreachable 2
-1 -1
sum 6 max 3 unreachable 0
0 -1 -1
1 2 3
sum 0 max -1 unreachable 1
-1
-1
-1
=== hidden
2 3
...
.E#
4 5
.##.#
#E...
##...
##...
3 4
#...
.#EE
....
5 5
#.E.E
.E...
###..
#....
E..E#
---
sum 6 max 2 unreachable 0
2 1 2
1 0 -1
sum 30 max 5 unreachable 1
-1 -1 -1 3 -1
-1 0 1 2 3
-1 -1 2 3 4
-1 -1 3 4 5
sum 15 max 4 unreachable 0
-1 2 1 1
4 -1 0 0
3 2 1 1
sum 20 max 2 unreachable 0
-1 1 0 1 0
1 0 1 2 1
-1 -1 -1 2 2
-1 2 2 1 2
0 1 1 0 -1
=== hidden
6 6
.###.#
####..
..##..
.EE...
E.E.#.
E##..E
6 2
#.
..
#.
.E
.#
#.
4 5
.EE..
.#..E
.E.##
.E#.#
4 5
E.E..
.....
E#EE#
....#
---
sum 34 max 5 unreachable 1
-1 -1 -1 -1 5 -1
-1 -1 -1 -1 4 4
2 1 -1 -1 3 3
1 0 0 1 2 2
0 1 0 1 -1 1
0 -1 -1 2 1 0
sum 12 max 3 unreachable 1
-1 3
3 2
-1 1
1 0
2 -1
-1 -1
sum 10 max 2 unreachable 1
1 0 0 1 1
2 -1 1 1 0
1 0 1 -1 -1
1 0 -1 -1 -1
sum 16 max 2 unreachable 0
0 1 0 1 2
1 2 1 1 2
0 -1 0 0 -1
1 2 1 1 -1
=== hidden
@gen 1414734054 big
=== hidden
@gen 1414734055 big
=== hidden
@gen 1414734056 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 1):
    if not big:
        R, C = r.randint(1, 6), r.randint(1, 6)
        print(R, C)
        for _ in range(R): print("".join(r.choice("....##E") for _ in range(C)))
    else:
        R = C = 1000
        print(R, C)
        k = r.choice([1, 50])
        ex = {(r.randrange(R), r.randrange(C)) for _ in range(k)}
        for i in range(R):
            print("".join("E" if (i, j) in ex else ("#" if r.random() < 0.25 else ".") for j in range(C)))
```

## Hints
- Distances are symmetric: the distance from a cell to an exit equals the distance from that exit to the cell.
- Push every exit into the queue with distance 0 and run one BFS.
- Never enter `'#'`; cells the BFS never reaches stay `-1`.

## Solution
**Reverse the direction.** Each cell wants the distance to its closest exit. Because every move can be undone, "distance from cell to exit" equals "distance from exit to cell". So instead of asking the question once per cell, ask it once for the whole set of exits.

**Multi-source BFS.** Push all exits with distance 0, then run an ordinary BFS. BFS processes cells in increasing distance from the *set* of sources, so the first time a cell is reached, it is reached from its nearest exit. Walls are never entered; open cells never reached keep `-1`.

**Compared with rotting oranges.** There the question was "when does the *last* cell get reached?" (the maximum of the field). Here the whole field is the answer. The same technique solves "distance to the nearest hospital for every town", "nearest 0 in a binary matrix" and "Voronoi-style" labelling (store the source id alongside the distance).

Complexity: O(R·C), versus O((R·C)²) for one BFS per cell.

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<vector<int>> exit_distances(const vector<string>& grid) {
    int R = grid.size(), C = grid[0].size();
    const int dr[] = {-1, 1, 0, 0}, dc[] = {0, 0, -1, 1};
    vector<vector<int>> d(R, vector<int>(C, -1));
    vector<pair<int,int>> q; q.reserve((size_t)R * C);
    for (int r = 0; r < R; ++r)
        for (int c = 0; c < C; ++c)
            if (grid[r][c] == 'E') { d[r][c] = 0; q.push_back({r, c}); }   // every exit is a source
    for (size_t head = 0; head < q.size(); ++head) {
        auto [y, x] = q[head];
        for (int k = 0; k < 4; ++k) {
            int ny = y + dr[k], nx = x + dc[k];
            if (ny < 0 || ny >= R || nx < 0 || nx >= C) continue;
            if (grid[ny][nx] == '#' || d[ny][nx] != -1) continue;
            d[ny][nx] = d[y][x] + 1;
            q.push_back({ny, nx});
        }
    }
    return d;
}
```
