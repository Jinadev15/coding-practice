---
id: cpp-game-of-life
title: Game of Life In Place
difficulty: Medium
order: 6
tags: matrix, simulation, in-place, bit encoding
time_limit: 2
---
## Statement
Conway's Game of Life runs on a grid of cells that are alive (`1`) or dead (`0`). Every cell looks at its **8 neighbours**. Cells beyond the border count as dead. All cells update **simultaneously**:

- a live cell with 2 or 3 live neighbours survives, and otherwise dies;
- a dead cell with exactly 3 live neighbours becomes alive.

```cpp
void step(std::vector<std::vector<int>>& g);              // one generation, IN PLACE, O(1) extra memory
void run(std::vector<std::vector<int>>& g, int generations);
```

You may not allocate a copy of the grid. Each cell must still be computed from the **old** values of its neighbours, so store both states in the same cell. Bit 0 holds the current state and bit 1 the next state. A final pass shifts every cell right by one.

**Input:** cases until the end of input: `R C G`, then `R` lines of `0`/`1` characters. R, C ≤ 300 and G ≤ 100. Print the final grid if R·C ≤ 400, otherwise the population and a checksum.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

void step(vector<vector<int>>& g) {
    int R = g.size(), C = g[0].size();
    for (int i = 0; i < R; ++i) for (int j = 0; j < C; ++j) {
        int live = 0;
        for (int di = -1; di <= 1; ++di) for (int dj = -1; dj <= 1; ++dj) {
            if (!di && !dj) continue;
            int a = i + di, b = j + dj;
            if (a >= 0 && a < R && b >= 0 && b < C) live += g[a][b];
        }
        g[i][j] = (live == 3 || (g[i][j] && live == 2));   // bug: overwrites values neighbours still need
    }
}
void run(vector<vector<int>>& g, int generations) { while (generations--) step(g); }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int R, C, G;
    while (cin >> R >> C >> G) {
        vector<vector<int>> g(R, vector<int>(C));
        for (int i = 0; i < R; ++i) { string s; cin >> s; for (int j = 0; j < C; ++j) g[i][j] = s[j] - '0'; }
        run(g, G);
        if (R * C <= 400) for (auto& row : g) { for (int x : row) cout << x; cout << '\n'; }
        else {
            long long pop = 0, h = 0;
            for (int i = 0; i < R; ++i) for (int j = 0; j < C; ++j) { pop += g[i][j]; if (g[i][j]) h = (h * 1000003 + i * 1000 + j) % 998244353; }
            cout << "population " << pop << " checksum " << h << '\n';
        }
        cout << "--\n";
    }
}
```

## Tests
=== sample
4 3 1
010
001
111
000
5 5 2
00000
00100
00100
00100
00000
---
000
101
011
010
--
00000
00100
00100
00100
00000
--
=== hidden
1 1 5
1
3 3 1
111
111
111
6 6 4
000000
011000
011000
000110
000110
000000
---
0
--
101
000
101
--
000000
011000
011000
000110
000110
000000
--
=== hidden
7 1 4
0
1
1
1
0
1
0
3 2 4
00
10
00
8 7 3
1001011
0001011
0001100
1101111
0001010
1000101
0001100
0011001
2 9 0
000010010
000000000
---
0
0
0
0
0
0
0
--
00
00
00
--
0000011
0000011
0000000
0110000
0110000
0111000
0000000
0000000
--
000010010
000000000
--
=== hidden
3 1 6
0
0
1
6 3 2
111
100
000
001
001
011
3 2 2
10
00
11
3 6 6
000001
000011
001001
---
0
0
0
--
110
110
000
000
011
011
--
00
00
00
--
000000
000000
000000
--
=== hidden
9 9 2
111100110
010101111
011101111
100110111
110111100
110010111
011001001
001010101
111101111
10 7 4
1000001
0000000
0001000
0000000
0000000
1000000
0000100
0110000
0100000
0001000
7 5 6
00000
00001
00000
00000
00000
10001
01000
10 2 6
00
00
00
00
01
00
01
00
00
01
---
000010000
001010000
110000000
110000000
000000000
000000000
010100011
100000001
011111010
--
0000000
0000000
0000000
0000000
0000000
0000000
0100000
1011000
0100000
0000000
--
00000
00000
00000
00000
00000
00000
00000
--
00
00
00
00
00
00
00
00
00
00
--
=== hidden
@gen 3315917349 big
=== hidden
@gen 3315917350 big
=== hidden
@gen 3315917351 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 1):
    R = r.randint(1, 10) if not big else 300; C = r.randint(1, 10) if not big else 300
    G = r.randint(0, 6) if not big else 100
    p = r.choice([0.2, 0.35, 0.5])
    print(R, C, G)
    for _ in range(R): print("".join("1" if r.random() < p else "0" for _ in range(C)))
```

## Hints
- Updating a cell immediately corrupts its neighbours' counts. You need both the old and the new value of every cell at once.
- A cell is only 0 or 1, so there are spare bits. Keep the current state in bit 0 (`x & 1`) and write the next state into bit 1 (`x |= 2`).
- When counting neighbours, use `g[a][b] & 1`. After the scan, shift every cell right by one.

## Solution
Every cell holds two bits: **bit 0 = now**, **bit 1 = next**. While scanning, read only `cell & 1`, which is unaffected by any bit-1 writes already made to neighbours, and set bit 1 when the cell should be alive next. After the whole scan, `x >>= 1` makes "next" the new "now".

The starter writes the new state over the old one immediately, so cells later in the scan see a mix of generations. That's why it gives wrong answers.

This encoding trick generalises: whenever an in-place update must use old values, pack old and new into spare bits or use sentinel values (for example, 2 = "was alive, will die").

Complexity: O(R·C·9) per generation, O(1) extra space.

```cpp
#include <bits/stdc++.h>
using namespace std;

void step(vector<vector<int>>& g) {
    int R = g.size(), C = g[0].size();
    for (int i = 0; i < R; ++i)
        for (int j = 0; j < C; ++j) {
            int live = 0;
            for (int di = -1; di <= 1; ++di)
                for (int dj = -1; dj <= 1; ++dj) {
                    if (!di && !dj) continue;
                    int a = i + di, b = j + dj;
                    if (a >= 0 && a < R && b >= 0 && b < C) live += g[a][b] & 1;   // OLD state only
                }
            int alive = g[i][j] & 1;
            if (live == 3 || (alive && live == 2)) g[i][j] |= 2;                  // next state in bit 1
        }
    for (auto& row : g) for (auto& x : row) x >>= 1;                              // commit
}

void run(vector<vector<int>>& g, int generations) { while (generations--) step(g); }
```
