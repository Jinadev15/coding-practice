---
id: cpp-ps-2d-difference
title: Rectangle Stamps with a 2D Difference Array
difficulty: Hard
order: 6
tags: difference array, 2D, prefix sums, inclusion-exclusion
time_limit: 1
---
## Statement
A blank `R × C` canvas receives `q` rectangular stamps. Each stamp adds `v` to every cell in rows `r1..r2` and columns `c1..c2`. After all the stamps:

```cpp
std::vector<std::vector<long long>> apply_stamps(int R, int C,
        const std::vector<std::array<long long,5>>& stamps);    // {r1, c1, r2, c2, v}
```

Then the driver reports how many cells have a value of at least `t`, the maximum cell value, and a checksum.

Updating every cell of every stamp is O(q·R·C). A **2D difference array** makes each stamp O(1). Mark four corners:

```text
D[r1][c1] += v,  D[r1][c2+1] −= v,  D[r2+1][c1] −= v,  D[r2+1][c2+1] += v
```

Then take 2D prefix sums once.

**Input:** `R C q t`, then `q` lines `r1 c1 r2 c2 v` (R, C ≤ 1000, q ≤ 2·10⁵, |v| ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<vector<long long>> apply_stamps(int R, int C, const vector<array<long long,5>>& stamps) {
    vector<vector<long long>> g(R, vector<long long>(C, 0));
    for (auto& s : stamps)
        for (long long i = s[0]; i <= s[2]; ++i)
            for (long long j = s[1]; j <= s[3]; ++j) g[i][j] += s[4];
    return g;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int R, C, q; long long t;
    cin >> R >> C >> q >> t;
    vector<array<long long,5>> st(q);
    for (auto& s : st) for (auto& x : s) cin >> x;
    auto g = apply_stamps(R, C, st);
    long long cnt = 0, mx = LLONG_MIN, h = 0;
    for (auto& row : g) for (long long x : row) { cnt += x >= t; mx = max(mx, x); h = (h * 1000003 + (x % 998244353 + 998244353)) % 998244353; }
    cout << cnt << ' ' << mx << ' ' << h << '\n';
}
```

## Tests
=== sample
3 4 2 2
0 0 1 2 1
1 1 2 3 1
---
2 2 710946396
=== hidden
1 1 1 5
0 0 0 0 5
---
1 5 5
=== hidden
2 2 3 0
0 0 1 1 -2
0 0 0 0 3
1 1 1 1 1
---
1 1 41423311
=== hidden
6 3 6 3
3 0 5 1 3
2 1 2 2 2
5 1 5 1 2
2 0 5 2 -3
0 0 5 1 1
1 1 3 1 1
---
1 3 385401472
=== hidden
3 3 7 2
1 1 2 2 1
0 1 0 1 -1
2 1 2 1 2
1 2 1 2 -2
2 0 2 1 1
2 2 2 2 3
1 0 2 0 2
---
4 4 161053277
=== hidden
5 6 6 1
2 4 3 4 1
1 2 3 2 1
0 2 2 3 0
4 0 4 4 -2
3 2 4 4 -2
1 0 4 2 3
---
12 4 849362228
=== hidden
@gen 1921726323 big
=== hidden
@gen 1921726324 big
=== hidden
@gen 1921726325 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
R = r.randint(1, 6) if not big else 1000; C = r.randint(1, 6) if not big else 1000
q = r.randint(1, 8) if not big else 200000
print(R, C, q, r.randint(-2, 3))
for _ in range(q):
    r1 = r.randrange(R); r2 = r.randrange(r1, R); c1 = r.randrange(C); c2 = r.randrange(c1, C)
    print(r1, c1, r2, c2, r.randint(-3, 3) if not big else r.randint(-10**6, 10**6))
```

## Hints
- In 1D you mark `+v` at `l` and `−v` at `r+1`. In 2D, a mark spreads right and down when you take 2D prefix sums.
- Mark four corners: `+v`, `−v`, `−v`, `+v`. Draw the four quadrants to see why the last one is `+`.
- Allocate `(R+1) × (C+1)`, so `r2+1` and `c2+1` never go out of bounds.

## Solution
In 1D, a range update marks `+v` at the start and `−v` after the end, and prefix sums propagate it. In 2D, the 2D prefix sum spreads a mark at `(r, c)` to **every cell below and to the right** of it. So:

1. `+v` at `(r1, c1)` covers the whole quadrant from the top-left corner.
2. `−v` at `(r1, c2+1)` cancels everything right of the rectangle.
3. `−v` at `(r2+1, c1)` cancels everything below it.
4. The region below and to the right was cancelled twice, so `+v` at `(r2+1, c2+1)` restores it.

That's four O(1) marks per stamp, and one O(R·C) prefix pass at the end. The total is O(q + R·C) instead of O(q·R·C).

Complexity: O(q + R·C) time, O(R·C) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<vector<long long>> apply_stamps(int R, int C, const vector<array<long long,5>>& stamps) {
    vector<vector<long long>> D(R + 1, vector<long long>(C + 1, 0));
    for (auto& s : stamps) {
        long long r1 = s[0], c1 = s[1], r2 = s[2], c2 = s[3], v = s[4];
        D[r1][c1] += v;                    // switch on at the top-left corner
        D[r1][c2 + 1] -= v;                // switch off to the right
        D[r2 + 1][c1] -= v;                // switch off below
        D[r2 + 1][c2 + 1] += v;            // undo the double switch-off
    }
    vector<vector<long long>> g(R, vector<long long>(C, 0));
    for (int i = 0; i < R; ++i)
        for (int j = 0; j < C; ++j) {
            long long up = i ? g[i - 1][j] : 0, left = j ? g[i][j - 1] : 0, diag = (i && j) ? g[i - 1][j - 1] : 0;
            g[i][j] = D[i][j] + up + left - diag;      // 2D prefix sum of D
        }
    return g;
}
```
