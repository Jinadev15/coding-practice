---
id: cpp-qd-multi-source-bfs
title: Spreading Rot - Multi-Source BFS with a Queue
difficulty: Medium
order: 4
tags: queue, bfs, multi-source, grid
time_limit: 1
---
## Statement
```cpp
int minutes_to_rot(std::vector<std::string>& grid);
```

A grid holds `.` (empty), `F` (fresh fruit) and `R` (rotten fruit). Every minute, each rotten fruit makes its fresh **4-neighbours** (up, down, left, right) rotten. Return the number of minutes until no fresh fruit is left, `0` if there is none at the start, or `-1` if some fresh fruit can never rot.

```text
start    minute 1   minute 2
RF.      RR.        RR.
FF.      RF.        RR.
..F      ..F        ..F
```

After minute 2 nothing changes, but the `F` at row 2, column 2 has no neighbour that ever rots, so the answer is **−1**. Without that cell the answer would be 2.

**Input:** cases until the end of input: `R C`, then `R` rows (R · C ≤ 10⁶ per case).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int minutes_to_rot(vector<string>& grid) {
    return 0;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int r, c;
    while (cin >> r >> c) {
        vector<string> g(r); for (auto& row : g) cin >> row;
        cout << minutes_to_rot(g) << '\n';
    }
}
```

## Tests
=== sample
3 3
RF.
FF.
..F
3 3
RFF
FF.
.FF
1 3
...
---
-1
4
0
=== hidden
1 1
R
1 1
F
2 2
RR
RR
1 5
FFRFF
3 3
FFF
FRF
FFF
2 4
RFFF
...R
---
0
-1
0
2
2
2
=== hidden
1 5
.FFFF
5 1
F
F
F
F
F
2 3
FFR
RFF
1 3
FFF
4 3
FRF
F.F
FF.
.FF
5 3
FFF
.FF
FFF
FFF
FFF
4 2
.F
FF
FF
..
4 5
FFFFF
.FRFF
...F.
FFFF.
---
-1
-1
1
-1
6
-1
-1
6
=== hidden
5 3
F.F
FFF
FFF
RRF
RR.
3 1
F
F
R
5 3
FFR
.FF
FFF
FFR
FFF
4 5
FFFF.
.FR.F
..FRF
F.FFR
1 3
RFR
5 4
.FFF
FFFF
FFF.
FFFF
RFFF
3 5
FFFF.
R..FF
F.FFR
4 4
FF.F
FFFF
RFFF
FFF.
---
4
2
3
-1
1
7
3
5
=== hidden
5 1
F
F
F
F
F
4 2
FF
FF
FR
FF
5 1
F
F
F
F
F
4 1
.
F
F
.
3 2
.F
F.
FR
5 5
FFFF.
FFFFF
F..FF
FFRFR
.FFFF
4 4
FFR.
.RRF
FFFR
RFFF
1 5
.FF.F
---
-1
3
-1
-1
-1
6
2
-1
=== hidden
@gen 2324783238 big
=== hidden
@gen 2324783239 big
=== hidden
@gen 2324783240 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(8 if not big else 1):
    R = r.randint(1, 5) if not big else 1000
    C = r.randint(1, 5) if not big else 1000
    pe, pr = (r.choice([0.1, 0.25]), r.choice([0.05, 0.2])) if not big else (0.02, 0.00001)
    print(R, C)
    rows = []
    for _ in range(R):
        rows.append("".join("." if (x := r.random()) < pe else "R" if x < pe + pr else "F" for _ in range(C)))
    if big:
        rows[0] = "R" + rows[0][1:]
    print("\n".join(rows))
```

## Hints
- Rot spreads from all rotten fruit simultaneously, one step per minute: that is BFS. What should the queue hold at the start?
- Push every initial `R` first, then process the queue in levels; each level is one minute.
- Count fresh fruit at the start, decrease it as fruit rots, and return −1 if some remain. Mark cells when you enqueue them.

## Solution
Rot spreads one step per minute from **all** rotten fruit at once. That is breadth-first search with several sources: put every initial `R` in the queue at distance 0, then process the queue **level by level**. A FIFO queue guarantees that all cells at distance d are handled before any cell at distance d + 1, so the minute a fruit rots equals its BFS distance to the nearest rotten fruit.

```text
level 0: initial R cells
level 1: fresh neighbours of level 0   (minute 1)
level 2: fresh neighbours of level 1   (minute 2)
...
```

Processing in levels: remember `level_end = q.size()` before the level starts; everything enqueued during the level belongs to the next one. Stop when no fresh fruit is left (so a final empty level does not add a minute). Mark a cell rotten **when it is enqueued**, not when it is dequeued, otherwise it can be enqueued twice.

Running one BFS per rotten fruit and taking minimums would be O(#R · R·C); multi-source BFS is O(R·C).

A `vector` with a moving `head` index is a fast queue when the total number of pushes is known (here ≤ R·C).

```cpp
#include <bits/stdc++.h>
using namespace std;

int minutes_to_rot(vector<string>& grid) {
    int R = grid.size(), C = grid[0].size();
    vector<int> q;                               // a queue as a vector + head index (cells = r*C + c)
    q.reserve((size_t)R * C);
    int fresh = 0;
    for (int r = 0; r < R; ++r)
        for (int c = 0; c < C; ++c) {
            if (grid[r][c] == 'R') q.push_back(r * C + c);     // ALL sources start at distance 0
            else if (grid[r][c] == 'F') ++fresh;
        }
    int minutes = 0;
    size_t head = 0;
    const int dr[] = {1, -1, 0, 0}, dc[] = {0, 0, 1, -1};
    while (head < q.size() && fresh > 0) {
        size_t level_end = q.size();             // everything currently queued rots this minute's neighbours
        ++minutes;
        for (; head < level_end; ++head) {
            int r = q[head] / C, c = q[head] % C;
            for (int d = 0; d < 4; ++d) {
                int nr = r + dr[d], nc = c + dc[d];
                if (nr < 0 || nr >= R || nc < 0 || nc >= C || grid[nr][nc] != 'F') continue;
                grid[nr][nc] = 'R';              // mark when ENQUEUED, so no cell is queued twice
                --fresh;
                q.push_back(nr * C + nc);
            }
        }
    }
    return fresh == 0 ? minutes : -1;
}
```
