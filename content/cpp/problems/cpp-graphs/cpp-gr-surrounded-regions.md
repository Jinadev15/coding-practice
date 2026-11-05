---
id: cpp-gr-surrounded-regions
title: Capture Surrounded Regions (Flood From the Border)
difficulty: Medium
order: 6
tags: flood fill, BFS, grid graph, boundary seeding
time_limit: 2
---
## Statement
A board holds `'X'` and `'O'` cells. A region of `'O'` cells (connected horizontally or vertically) is **captured** when none of its cells lies on the border of the board; captured regions are flipped to `'X'`. Regions that touch the border survive. Modify the board in place.

```cpp
void capture(std::vector<std::string>& board);
```

Checking every region separately ("does this region reach the border?") is natural but easy to get wrong. Turn the question around: the survivors are exactly the `'O'` cells **reachable from a border `'O'`**. Flood from all border `'O'` cells at once, mark what you reach, then flip every unmarked `'O'`.

**Input:** cases until the end of input: `R C`, then `R` rows (1 ≤ R, C ≤ 1000).

**Output (printed by the driver):** the number of `'O'` cells left and a checksum of the board, plus the board itself when R·C ≤ 100.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

void capture(vector<string>& board) {
    // wrong idea: flip every 'O' that is not itself on the border
    int R = board.size(), C = board[0].size();
    for (int r = 1; r + 1 < R; ++r) for (int c = 1; c + 1 < C; ++c) if (board[r][c] == 'O') board[r][c] = 'X';
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int R, C;
    while (cin >> R >> C) {
        vector<string> b(R);
        for (auto& row : b) cin >> row;
        capture(b);
        long long o = 0; unsigned long long h = 1469598103934665603ULL;
        for (auto& row : b) for (char ch : row) { o += ch == 'O'; h = (h ^ (unsigned char)ch) * 1099511628211ULL; }
        cout << "O " << o << " | " << h << '\n';
        if (R * C <= 100) for (auto& row : b) cout << row << '\n';
    }
}
```

## Tests
=== sample
4 4
XXXX
XOOX
XXOX
XOXX
---
O 1 | 16666128536851097050
XXXX
XXXX
XXXX
XOXX
=== sample
5 5
XXXXX
XOOOX
XOXOO
XOOOX
XXXXX
---
O 9 | 590845884513107672
XXXXX
XOOOX
XOXOO
XOOOX
XXXXX
=== hidden
1 1
O
---
O 1 | 4953243621002146724
O
=== hidden
3 3
OOO
OXO
OOO
---
O 8 | 3124893640343834017
OOO
OXO
OOO
=== hidden
3 3
XXX
XOX
XXX
---
O 0 | 1793945134010243009
XXX
XXX
XXX
=== hidden
1 1
O
1 3
XXO
1 1
X
6 5
OXOXO
OOOOX
XXXOX
XOXOO
OOOOO
OOOOO
---
O 1 | 4953243621002146724
O
O 1 | 11867502136131605564
XXO
O 0 | 4953260113676569889
X
O 21 | 2224631061602565086
OXOXO
OOOOX
XXXOX
XOXOO
OOOOO
OOOOO
=== hidden
3 1
O
X
O
2 4
XXXX
OOXO
6 6
XOOXOX
OOOXXX
OOXXXO
OOXXOX
XOOXOO
OXOOOX
6 3
XOO
OOO
XOX
OOX
OXX
XXO
---
O 2 | 2505038578593595393
O
X
O
O 3 | 16471341565869264156
XXXX
OOXO
O 20 | 4545609079379379923
XOOXOX
OOOXXX
OOXXXO
OOXXOX
XOOXOO
OXOOOX
O 10 | 5320648610164468367
XOO
OOO
XOX
OOX
OXX
XXO
=== hidden
2 5
XOXXX
OOXXX
5 6
OOOXXO
OOOXOX
OXOOOO
XXOOOO
OOOOOO
1 2
OX
6 3
OXO
OXX
OOO
OOX
XOO
XOO
---
O 3 | 8159834063277311692
XOXXX
OOXXX
O 23 | 8935108400319642700
OOOXXO
OOOXOX
OXOOOO
XXOOOO
OOOOOO
O 1 | 11196371988943476020
OX
O 12 | 4380914751132957881
OXO
OXX
OOO
OOX
XOO
XOO
=== hidden
@gen 45214329 big
=== hidden
@gen 45214330 big
=== hidden
@gen 45214331 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 1):
    if not big:
        R, C = r.randint(1, 6), r.randint(1, 6)
        print(R, C)
        for _ in range(R): print("".join(r.choice("XXOOO") for _ in range(C)))
    else:
        R = C = 1000
        print(R, C)
        for i in range(R):
            print("".join("O" if r.random() < 0.6 else "X" for _ in range(C)))
```

## Hints
- Which `'O'` cells survive? Those connected to an `'O'` on the border.
- Flood fill from all border `'O'` cells at once and mark what you reach.
- Afterwards, flip every unmarked `'O'` to `'X'` and restore the marked ones.

## Solution
**Complement thinking.** A region is captured iff it does *not* touch the border. Instead of testing each region, find the survivors directly: an `'O'` survives exactly when it is connected to some border `'O'`. That is one multi-source flood fill seeded with every border `'O'`.

**Marking in place.** Temporarily relabel reached cells as `'S'`. The label doubles as the visited flag, so no extra array is needed. A final pass turns `'S'` back into `'O'` and every remaining `'O'` (not reached) into `'X'`.

**Why the per-region approach is fragile.** Testing "does my region reach the border?" requires finishing the whole region's flood before deciding, then a second pass to flip it, and a region must not be re-explored from each of its cells (which would be quadratic). Seeding from the border avoids all of that.

Complexity: O(R·C), with an explicit stack so a 10⁶-cell region cannot overflow the call stack.

```cpp
#include <bits/stdc++.h>
using namespace std;

void capture(vector<string>& board) {
    int R = board.size(), C = board[0].size();
    const int dr[] = {-1, 1, 0, 0}, dc[] = {0, 0, -1, 1};
    vector<pair<int,int>> st;
    auto seed = [&](int r, int c) {               // border 'O' cells are the sources
        if (board[r][c] == 'O') { board[r][c] = 'S'; st.push_back({r, c}); }   // 'S' = safe (and visited)
    };
    for (int r = 0; r < R; ++r) { seed(r, 0); seed(r, C - 1); }
    for (int c = 0; c < C; ++c) { seed(0, c); seed(R - 1, c); }
    while (!st.empty()) {
        auto [y, x] = st.back(); st.pop_back();
        for (int k = 0; k < 4; ++k) {
            int ny = y + dr[k], nx = x + dc[k];
            if (ny < 0 || ny >= R || nx < 0 || nx >= C || board[ny][nx] != 'O') continue;
            board[ny][nx] = 'S';
            st.push_back({ny, nx});
        }
    }
    for (auto& row : board)
        for (char& ch : row) ch = ch == 'S' ? 'O' : 'X';   // unmarked 'O' -> captured; safe -> back to 'O'
}
```
