---
id: cpp-ps-2d-sums
title: 2D Prefix Sums and the Best Square
difficulty: Medium
order: 2
tags: prefix sums, 2D, inclusion-exclusion, matrix
time_limit: 1
---
## Statement
```cpp
class Grid2D {
public:
    explicit Grid2D(const std::vector<std::vector<int>>& g);
    long long rect(int r1, int c1, int r2, int c2) const;   // sum of rows r1..r2, columns c1..c2 (inclusive)
    long long best_square(int k) const;                     // maximum sum of any k x k square
};
```

Build `S[i+1][j+1] = g[i][j] + S[i][j+1] + S[i+1][j] − S[i][j]`. A rectangle query is then four lookups (inclusion–exclusion). `best_square(k)` tries every top-left corner in O(R·C) total.

**Input:** `R C`, the grid (values in [−10⁶, 10⁶], R, C ≤ 1000), then `q` queries: `rect r1 c1 r2 c2` or `square k` (q ≤ 2·10⁵ rect queries; at most 5 square queries).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class Grid2D {
    vector<vector<int>> g;
public:
    explicit Grid2D(const vector<vector<int>>& grid) : g(grid) {}
    long long rect(int r1, int c1, int r2, int c2) const {
        long long s = 0; for (int i = r1; i <= r2; ++i) for (int j = c1; j <= c2; ++j) s += g[i][j]; return s;
    }
    long long best_square(int k) const { return 0; }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int R, C; cin >> R >> C;
    vector<vector<int>> g(R, vector<int>(C));
    for (auto& row : g) for (auto& x : row) cin >> x;
    Grid2D G(g);
    int q; cin >> q;
    while (q--) {
        string t; cin >> t;
        if (t == "rect") { int a, b, c, d; cin >> a >> b >> c >> d; cout << G.rect(a, b, c, d) << '\n'; }
        else { int k; cin >> k; cout << G.best_square(k) << '\n'; }
    }
}
```

## Tests
=== sample
3 4
1 2 3 4
5 6 7 8
9 10 11 12
4
rect 0 0 2 3
rect 1 1 2 2
square 2
square 3
---
78
34
38
63
=== hidden
1 1
-5
3
rect 0 0 0 0
square 1
rect 0 0 0 0
---
-5
-5
-5
=== hidden
6 2
4 3
-2 -8
3 7
2 2
4 -4
-1 2
15
rect 0 0 2 0
square 2
rect 5 1 5 1
square 1
square 2
rect 4 0 5 0
square 2
rect 0 1 2 1
square 1
square 1
square 2
rect 3 1 5 1
rect 1 0 4 0
rect 4 1 5 1
square 1
---
5
14
2
7
14
3
14
2
7
7
14
0
7
-2
7
=== hidden
6 4
8 9 7 2
4 9 3 5
4 6 1 -8
0 -4 -3 -4
-5 8 4 -5
7 -6 -7 8
15
square 1
square 4
rect 0 3 5 3
square 1
rect 2 3 2 3
square 3
square 2
square 1
rect 1 1 1 3
square 2
rect 5 3 5 3
rect 1 1 1 2
rect 1 0 2 1
square 3
rect 5 3 5 3
---
9
39
-2
9
-8
51
30
9
17
30
8
12
23
51
8
=== hidden
6 3
-5 -5 -8
-1 5 6
-8 -1 -4
-4 -7 -9
0 -5 -4
-1 -6 3
15
rect 4 0 5 1
rect 5 1 5 1
rect 4 2 5 2
square 3
square 3
square 1
rect 1 2 1 2
rect 2 1 5 2
rect 0 2 5 2
square 1
rect 5 2 5 2
rect 2 0 3 2
rect 1 1 4 1
square 3
rect 0 2 1 2
---
-12
-6
-1
-21
-21
6
6
-33
-16
6
3
-33
-8
-21
-2
=== hidden
@gen 92344576 big
=== hidden
@gen 92344577 big
=== hidden
@gen 92344578 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
R = r.randint(1, 6) if not big else 1000; C = r.randint(1, 6) if not big else 1000
print(R, C)
for _ in range(R): print(*[r.randint(-9, 9) if not big else r.randint(-10**6, 10**6) for _ in range(C)])
q = 15 if not big else 200005
print(q)
out = []
for i in range(q):
    if (not big and r.random() < 0.3) or (big and i < 5):
        out.append(f"square {r.randint(1, min(R, C))}")
    else:
        r1 = r.randrange(R); r2 = r.randrange(r1, R); c1 = r.randrange(C); c2 = r.randrange(c1, C)
        out.append(f"rect {r1} {c1} {r2} {c2}")
print("\n".join(out))
```

## Hints
- Use an `(R+1) × (C+1)` table with a zero border, so you never check bounds.
- Building: `S[i+1][j+1] = g[i][j] + S[i][j+1] + S[i+1][j] − S[i][j]`.
- Query: total − top strip − left strip + top-left corner. Every k×k square is then one O(1) query.

## Solution
**Building.** The rectangle from `(0,0)` to `(i,j)` is the cell itself, plus the rectangle above, plus the rectangle to the left, minus their overlap (which was counted twice).

**Querying.** Take the big rectangle ending at `(r2, c2)`, remove the strip above row `r1` and the strip left of column `c1`, then add back their overlap, the corner block that was removed twice.

`best_square` is O(1) per candidate square, so O(R·C) overall instead of O(R·C·k²).

Values up to 10⁶ over 10⁶ cells reach 10¹², so use `long long`.

Complexity: O(R·C) build, O(1) per rectangle.

```cpp
#include <bits/stdc++.h>
using namespace std;

class Grid2D {
    int R, C;
    vector<vector<long long>> S;                     // (R+1) x (C+1), S[0][*] = S[*][0] = 0
public:
    explicit Grid2D(const vector<vector<int>>& g) : R(g.size()), C(g[0].size()), S(R + 1, vector<long long>(C + 1, 0)) {
        for (int i = 0; i < R; ++i)
            for (int j = 0; j < C; ++j)
                S[i + 1][j + 1] = g[i][j] + S[i][j + 1] + S[i + 1][j] - S[i][j];
    }
    long long rect(int r1, int c1, int r2, int c2) const {
        return S[r2 + 1][c2 + 1] - S[r1][c2 + 1] - S[r2 + 1][c1] + S[r1][c1];
    }
    long long best_square(int k) const {
        long long best = LLONG_MIN;
        for (int i = 0; i + k <= R; ++i)
            for (int j = 0; j + k <= C; ++j)
                best = max(best, rect(i, j, i + k - 1, j + k - 1));
        return best;
    }
};
```
