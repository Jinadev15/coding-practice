---
id: cpp-gr-rotting-oranges
title: Rotting Oranges (Multi-Source BFS)
difficulty: Medium
order: 4
tags: BFS, multi-source BFS, grid graph, levels
time_limit: 2
---
## Statement
A grid holds `'.'` (empty), `'F'` (fresh orange) and `'R'` (rotten orange). Every minute, each fresh orange that shares a side with a rotten one becomes rotten. Return the number of minutes until no fresh orange remains, `0` if there are no fresh oranges at the start, or `-1` if some fresh orange can never rot.

```cpp
int minutes_to_rot(const std::vector<std::string>& grid);
```

All rotten oranges spread **at the same time**. Running a separate BFS from each rotten orange would be far too slow. Instead, put **every** rotten orange into the queue at minute 0. One BFS then processes the grid in rounds: round `k` contains exactly the oranges that rot at minute `k`.

**Input:** cases until the end of input: `R C`, then `R` rows (1 ≤ R, C ≤ 1000).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int minutes_to_rot(const vector<string>& grid) {
    // naive: simulate minute by minute, rescanning the whole grid each minute (too slow)
    vector<string> g = grid;
    int R = g.size(), C = g[0].size(), minutes = 0;
    while (true) {
        vector<pair<int,int>> nxt;
        for (int r = 0; r < R; ++r) for (int c = 0; c < C; ++c) if (g[r][c] == 'F') {
            bool adj = (r > 0 && g[r-1][c] == 'R') || (r + 1 < R && g[r+1][c] == 'R') || (c > 0 && g[r][c-1] == 'R') || (c + 1 < C && g[r][c+1] == 'R');
            if (adj) nxt.push_back({r, c});
        }
        if (nxt.empty()) break;
        for (auto [r, c] : nxt) g[r][c] = 'R';
        ++minutes;
    }
    for (auto& row : g) for (char ch : row) if (ch == 'F') return -1;
    return minutes;
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
        cout << minutes_to_rot(g) << '\n';
    }
}
```

## Tests
=== sample
3 3
RFF
FF.
.FF
---
4
=== sample
3 3
RFF
.FF
F.F
---
-1
=== sample
1 2
.R
---
0
=== hidden
1 1
F
---
-1
=== hidden
2 2
RF
FR
---
1
=== hidden
1 5
FFRFF
---
2
=== hidden
3 5
R...R
.....
..F..
---
-1
=== hidden
3 1
F
.
.
3 4
FF..
.FFR
RF..
5 4
..FF
F.FF
.RFR
.FFF
...F
4 5
RF.FR
.F...
.RFFF
..FFF
4 3
RRF
.FF
.R.
..F
---
-1
4
-1
4
-1
=== hidden
6 2
FR
RF
F.
F.
FF
FR
1 3
FR.
5 5
FF..F
FFF.F
.FFFF
.F.FR
.FRF.
3 4
F.FR
FFFF
FFF.
5 4
RFFF
..FF
...F
RFFF
FF..
---
2
1
6
5
4
=== hidden
2 6
FFF...
FFFF.R
3 1
F
.
F
4 3
.FR
F.R
..F
...
2 5
.FFFR
...FF
5 5
FFFRF
..FFR
FFR..
..FFR
F.RFF
---
-1
-1
-1
3
-1
=== hidden
@gen 702432123 big
=== hidden
@gen 702432124 big
=== hidden
@gen 702432125 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(5 if not big else 1):
    if not big:
        R, C = r.randint(1, 6), r.randint(1, 6)
        print(R, C)
        for _ in range(R): print("".join(r.choice("..FFFFR") for _ in range(C)))
    else:
        R = C = 1000
        print(R, C)
        mode = r.randint(0, 1)
        for i in range(R):
            if mode == 0:     # serpentine corridor of fresh oranges, one rotten at the start
                if i % 2 == 0: row = "F" * C
                elif i % 4 == 1: row = "." * (C - 1) + "F"
                else: row = "F" + "." * (C - 1)
                if i == 0: row = "R" + row[1:]
            else:
                row = "".join(r.choice("FFFFFFFFF.R" if r.random() < 0.001 else "FFFFFFFFF.") for _ in range(C))
            print(row)
```

## Hints
- Rotting spreads from all rotten oranges simultaneously. Put every rotten orange into the queue at time 0.
- Record each cell's rotting time as `time[parent] + 1` when you push it. The largest recorded time is the answer.
- Count fresh oranges up front and decrement when one rots. Anything left over means `-1`.

## Solution
**A super-source.** Imagine an extra vertex connected to every rotten orange with an edge of length 0. The minute at which a fresh orange rots is its BFS distance from that super-source. Pushing all rotten oranges into the queue at distance 0 is exactly a BFS from the super-source, with the super-source itself skipped.

**Why one BFS is right.** BFS pops vertices in non-decreasing distance order. Every orange that rots at minute `k` is discovered from one that rots at minute `k − 1`, and it is discovered by the *first* such orange, because the queue holds all minute-`k−1` oranges before any minute-`k` ones. So `t[v]` equals the real rotting time.

**Answer.** The time of the last orange discovered is the maximum distance. Count the fresh oranges at the start and decrement on discovery; if any remain, they are cut off (surrounded by empty cells or the border), so the answer is `-1`.

The naive simulation rescans the whole grid every minute: O((R·C) · minutes), which is about 10¹¹ steps on a 1000 × 1000 snake.

Complexity: O(R·C).

```cpp
#include <bits/stdc++.h>
using namespace std;

int minutes_to_rot(const vector<string>& grid) {
    int R = grid.size(), C = grid[0].size();
    const int dr[] = {-1, 1, 0, 0}, dc[] = {0, 0, -1, 1};
    vector<int> t(R * C, -1);              // minute at which the cell rots (-1 = not yet)
    vector<int> q; q.reserve(R * C);
    int fresh = 0;
    for (int r = 0; r < R; ++r)
        for (int c = 0; c < C; ++c) {
            if (grid[r][c] == 'R') { t[r * C + c] = 0; q.push_back(r * C + c); }   // ALL sources at once
            else if (grid[r][c] == 'F') ++fresh;
        }
    int last = 0;
    for (size_t head = 0; head < q.size(); ++head) {
        int id = q[head], y = id / C, x = id % C;
        for (int k = 0; k < 4; ++k) {
            int ny = y + dr[k], nx = x + dc[k];
            if (ny < 0 || ny >= R || nx < 0 || nx >= C) continue;
            int nid = ny * C + nx;
            if (grid[ny][nx] != 'F' || t[nid] != -1) continue;
            t[nid] = t[id] + 1;            // one minute after the orange that infected it
            last = t[nid];
            --fresh;
            q.push_back(nid);
        }
    }
    return fresh > 0 ? -1 : last;
}
```
