---
id: cpp-hs-boomerangs
title: Counting Boomerangs and Collinear Points
difficulty: Medium
order: 6
tags: hashing, geometry, composite keys, counting
time_limit: 2
---
## Statement
Points have integer coordinates, and all points are distinct.

```cpp
long long boomerangs(const std::vector<std::pair<int,int>>& p);
    // ordered triples (i, j, k) with dist(i,j) == dist(i,k), j != k
int max_points_on_line(const std::vector<std::pair<int,int>>& p);
    // largest number of points that lie on one straight line
```

- **Boomerangs:** fix the middle point `i` and hash the **squared** distances to all other points (integers, so no floating point). A distance shared by `m` points gives `m·(m−1)` ordered pairs.
- **Lines:** fix a point and hash the **direction** to every other point, as a reduced fraction `(dx/g, dy/g)` with a normalised sign. Equal directions mean collinear with the fixed point. Never hash the slope as a `double`.

**Input:** cases until the end of input: `n` + n points `x y` (n ≤ 1500, |coordinate| ≤ 10⁴).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long boomerangs(const vector<pair<int,int>>& p) { return 0; }
int max_points_on_line(const vector<pair<int,int>>& p) { return min<int>(p.size(), 2); }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<pair<int,int>> p(n);
        for (auto& [x, y] : p) cin >> x >> y;
        cout << boomerangs(p) << ' ' << max_points_on_line(p) << '\n';
    }
}
```

## Tests
=== sample
3
0 0
1 0
2 0
6
1 1
3 2
5 3
4 1
2 3
1 4
---
2 3
12 4
=== hidden
1
5 5
2
0 0
-3 7
4
0 0
0 1
0 2
0 -5
---
0 1
0 2
2 4
=== hidden
6
2 -2
0 -3
-2 -2
-3 1
3 1
0 -2
8
2 -2
1 2
0 -3
-2 -2
-3 1
-1 3
1 -3
3 2
1
-1 0
3
3 3
1 2
2 1
---
8 3
14 2
0 1
2 2
=== hidden
5
0 1
0 -3
0 0
0 3
3 0
3
-1 -2
3 3
-2 -1
8
2 -1
-3 -2
1 1
3 3
-1 3
-2 3
-2 2
0 -2
5
-1 -3
-3 0
-3 3
-1 2
0 -2
---
8 4
2 2
12 3
2 2
=== hidden
5
3 1
-1 1
1 1
0 2
-1 2
7
0 1
-1 -1
-1 -2
-1 1
3 0
-2 0
-1 2
7
2 -1
-3 1
-3 -3
-2 -3
1 -1
1 -2
1 -3
2
2 -1
-2 3
---
6 3
18 4
10 3
0 2
=== hidden
@gen 952283521 big
=== hidden
@gen 952283522 big
=== hidden
@gen 952283523 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 1):
    n = r.randint(1, 9) if not big else 1500
    lim = 3 if not big else 10000
    pts = set()
    while len(pts) < n:
        if big and r.random() < 0.3: t = r.randint(-100, 100); pts.add((t * 3, t * 7))
        else: pts.add((r.randint(-lim, lim), r.randint(-lim, lim)))
        if not big and len(pts) >= (2*lim+1)**2: break
    pts = list(pts)
    print(len(pts))
    for x, y in pts: print(x, y)
```

## Hints
- Boomerangs: fix the middle point, then count the other points by squared distance. Each group of size m adds m·(m−1).
- Lines: from a fixed point, the direction to another point identifies the line. Reduce `(dx, dy)` by their gcd.
- Normalise the sign of the direction, and pack `(dx, dy)` into a single `long long` key.

## Solution
**Boomerangs.** For a fixed apex `i`, the triples `(i, j, k)` with equal distances are ordered pairs of distinct points from the same distance group: `m·(m−1)` of them. Squared distances are exact integers. Using `sqrt` would bring rounding into a hash key. The distance-0 entry is the point itself, so skip it.

**Collinear points.** The points on a line through `p[i]` share a direction from `p[i]`. Reduce `(dx, dy)` by their gcd, and fix the sign so that `(1,2)` and `(−1,−2)` become the same key. That gives an exact canonical form for the slope, vertical lines included (`dx = 0`). Comparing only the points after `i` is enough: the best line is found from its first point.

**Packing a pair into one integer key** avoids writing a custom hash. The reduced components lie in `[−20000, 20000]`, so `(dx + 20001)·40003 + (dy + 20001)` is unique.

Complexity: O(n²) expected for both.

```cpp
#include <bits/stdc++.h>
using namespace std;

long long boomerangs(const vector<pair<int,int>>& p) {
    long long total = 0;
    unordered_map<long long, int> cnt;
    cnt.reserve(p.size() * 2);
    for (auto& [xi, yi] : p) {
        cnt.clear();
        for (auto& [xj, yj] : p) {
            long long dx = xi - xj, dy = yi - yj;
            ++cnt[dx * dx + dy * dy];                 // squared distance: exact integer key
        }
        for (auto& [d, m] : cnt) if (d) total += 1LL * m * (m - 1);
    }
    return total;
}

int max_points_on_line(const vector<pair<int,int>>& p) {
    int n = p.size();
    if (n <= 2) return n;
    int best = 2;
    unordered_map<long long, int> dir;
    dir.reserve(n * 2);
    for (int i = 0; i < n; ++i) {
        dir.clear();
        for (int j = i + 1; j < n; ++j) {
            int dx = p[j].first - p[i].first, dy = p[j].second - p[i].second;
            int g = gcd(abs(dx), abs(dy));
            dx /= g; dy /= g;
            if (dx < 0 || (dx == 0 && dy < 0)) { dx = -dx; dy = -dy; }   // one sign per direction
            long long key = (long long)(dx + 20001) * 40003 + (dy + 20001);  // pack the pair into one integer
            best = max(best, ++dir[key] + 1);         // +1 for point i itself
        }
    }
    return best;
}
```
