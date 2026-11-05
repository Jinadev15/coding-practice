---
id: cpp-spiral-matrix
title: Spiral Traversal and Spiral Fill
difficulty: Medium
order: 3
tags: matrix, simulation, boundaries
time_limit: 1
---
## Statement
Two classic matrix routines that both use **four shrinking boundaries**:

```cpp
std::vector<int> spiral_order(const std::vector<std::vector<int>>& m);
    // clockwise from the top-left corner: top row → right column → bottom row (reversed) → left column (reversed) → inner layers
std::vector<std::vector<int>> spiral_fill(int R, int C);
    // an R x C matrix filled with 1, 2, ..., R*C in clockwise spiral order
```

Matrices can be non-square, a single row, or a single column. R and C are at most 1000.

**Input:** cases until the end of input: `order R C` followed by the matrix, or `fill R C`. For `order`, print the traversal (the first 30 values when it is longer) and a checksum. For `fill`, print the matrix when R·C ≤ 100, otherwise the checksum and the value at the centre cell `(R/2, C/2)`.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> spiral_order(const vector<vector<int>>& m) {
    vector<int> out;
    for (auto& row : m) for (int x : row) out.push_back(x);   // row by row, not a spiral
    return out;
}
vector<vector<int>> spiral_fill(int R, int C) { return vector<vector<int>>(R, vector<int>(C, 0)); }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd; int R, C;
    while (cin >> cmd >> R >> C) {
        if (cmd == "order") {
            vector<vector<int>> m(R, vector<int>(C));
            for (auto& row : m) for (auto& x : row) cin >> x;
            auto v = spiral_order(m);
            long long h = 0;
            for (size_t i = 0; i < v.size(); ++i) h = (h * 31 + v[i] + 1000) % 1000000007;
            cout << v.size() << ':';
            for (size_t i = 0; i < min<size_t>(v.size(), 30); ++i) cout << ' ' << v[i];
            cout << " | " << h << '\n';
        } else {
            auto m = spiral_fill(R, C);
            if ((long long)R * C <= 100) {
                for (auto& row : m) { for (int j = 0; j < C; ++j) cout << row[j] << (j + 1 < C ? ' ' : '\n'); }
            } else {
                long long h = 0;
                for (auto& row : m) for (int x : row) h = (h * 131 + x) % 1000000007;
                cout << "checksum " << h << " centre " << m[R / 2][C / 2] << '\n';
            }
        }
    }
}
```

## Tests
=== sample
order 3 3
1 2 3
4 5 6
7 8 9
order 3 4
1 2 3 4
5 6 7 8
9 10 11 12
fill 3 4
---
9: 1 2 3 6 9 8 7 4 5 | 491621868
12: 1 2 3 4 8 12 11 10 9 5 6 7 | 283479799
1 2 3 4
10 11 12 5
9 8 7 6
=== hidden
order 1 4
1 2 3 4
order 4 1
1
2
3
4
fill 1 1
fill 5 1
order 2 2
1 2
3 4
---
4: 1 2 3 4 | 30815810
4: 1 2 3 4 | 30815810
1
1
2
3
4
5
4: 1 2 4 3 | 30815840
=== hidden
fill 1000 999
fill 37 1000
---
checksum 615806987 centre 999000
checksum 737592176 centre 36519
=== hidden
order 7 6
-16 69 18 57 28 7
-92 -49 32 -9 -48 49
49 -5 22 80 -8 4
-24 -34 66 84 26 30
-46 26 10 -2 27 7
71 49 94 74 51 -47
-60 -81 38 74 22 58
order 1 1
-99
order 3 5
72 75 50 2 -86
50 -10 26 -92 -86
74 1 -69 -85 81
fill 1 1
order 7 2
16 65
-7 -3
-45 -45
-19 -33
93 -96
57 83
55 -64
---
42: -16 69 18 57 28 7 49 4 30 7 -47 58 22 74 38 -81 -60 71 -46 -24 49 -92 -49 32 -9 -48 -8 26 27 51 | 829785312
1: -99 | 901
15: 72 75 50 2 -86 -86 81 -85 -69 1 74 50 -10 26 -92 | 166590524
1
14: 16 65 -3 -45 -33 -96 83 -64 55 57 93 -19 -45 -7 | 352623993
=== hidden
fill 7 6
order 1 5
58 -4 8 -9 2
order 1 3
-17 23 52
order 3 5
36 59 -18 -73 11
0 -90 81 -41 82
-1 23 89 -99 36
order 6 5
-53 -90 -27 -12 -61
5 23 9 40 8
99 -14 -58 26 -34
21 -81 54 14 40
86 22 -59 78 -65
-94 -74 -50 61 70
---
1 2 3 4 5 6
22 23 24 25 26 7
21 36 37 38 27 8
20 35 42 39 28 9
19 34 41 40 29 10
18 33 32 31 30 11
17 16 15 14 13 12
5: 58 -4 8 -9 2 | 7757458
3: -17 23 52 | 977428
15: 36 59 -18 -73 11 82 36 -99 89 23 -1 0 -90 81 -41 | 713162711
30: -53 -90 -27 -12 -61 8 -34 40 -65 70 61 -50 -74 -94 86 21 99 5 23 9 40 26 14 78 -59 22 -81 -14 -58 54 | 624291757
=== hidden
order 4 1
99
46
29
-86
fill 3 7
order 6 7
38 80 18 -91 -75 -86 56
36 7 60 -19 94 74 -83
-53 -75 57 20 41 79 -98
-65 73 -47 -97 -13 58 -56
96 62 -50 -43 21 26 15
88 -52 52 70 81 -94 18
order 7 5
-19 -21 12 83 55
81 -68 33 -19 68
-24 66 89 35 -62
49 -64 79 22 -29
65 73 -91 90 72
57 97 -17 -50 40
85 -39 -27 28 -68
order 2 5
-81 -60 74 -18 14
-75 99 -41 -70 -91
---
4: 99 46 29 -86 | 33778328
1 2 3 4 5 6 7
16 17 18 19 20 21 8
15 14 13 12 11 10 9
42: 38 80 18 -91 -75 -86 56 -83 -98 -56 15 18 -94 81 70 52 -52 88 96 -65 -53 36 7 60 -19 94 74 79 58 26 | 185355430
35: -19 -21 12 83 55 68 -62 -29 72 40 -68 28 -27 -39 85 57 65 49 -24 81 -68 33 -19 35 22 90 -50 -17 97 73 | 281576541
10: -81 -60 74 -18 14 -91 -70 -41 99 -75 | 139211811
=== hidden
@gen 656359683 big
=== hidden
@gen 656359684 big
=== hidden
@gen 656359685 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(5 if not big else 2):
    R = r.randint(1, 7) if not big else r.randint(500, 1000); C = r.randint(1, 7) if not big else r.randint(500, 1000)
    if r.random() < 0.6:
        print("order", R, C)
        for _ in range(R): print(*[r.randint(-99, 99) for _ in range(C)])
    else: print("fill", R, C)
```

## Hints
- Keep four boundaries: `top`, `bottom`, `left`, `right`. After walking an edge, move that boundary inward.
- The bottom-row and left-column passes need an `if`: on a 1×N or N×1 remainder they would revisit cells.
- For the fill, simulate a walker with direction arrays `dr = {0,1,0,-1}`, `dc = {1,0,-1,0}` that turns right when blocked.

## Solution
**Traversal with boundaries.** Keep `top`, `bottom`, `left` and `right`. Take the top row and move `top` down, then the right column and move `right` left. The bottom row and the left column must be guarded. When only one row (or one column) remains, the top-row pass already took it, and without the checks you would read it again backwards.

**Fill by simulation.** This is a different technique for the same shape: walk with a direction index and turn right (`d = (d+1) % 4`) whenever the next cell is outside the grid or already filled. The direction arrays `dr`/`dc` replace four separate cases.

Both approaches touch each cell once: O(R·C).

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> spiral_order(const vector<vector<int>>& m) {
    vector<int> out;
    if (m.empty() || m[0].empty()) return out;
    int top = 0, bottom = (int)m.size() - 1, left = 0, right = (int)m[0].size() - 1;
    while (top <= bottom && left <= right) {
        for (int c = left; c <= right; ++c) out.push_back(m[top][c]);
        ++top;
        for (int r = top; r <= bottom; ++r) out.push_back(m[r][right]);
        --right;
        if (top <= bottom) {                                   // a row is still left
            for (int c = right; c >= left; --c) out.push_back(m[bottom][c]);
            --bottom;
        }
        if (left <= right) {                                   // a column is still left
            for (int r = bottom; r >= top; --r) out.push_back(m[r][left]);
            ++left;
        }
    }
    return out;
}

vector<vector<int>> spiral_fill(int R, int C) {
    vector<vector<int>> m(R, vector<int>(C, 0));
    const int dr[4] = {0, 1, 0, -1}, dc[4] = {1, 0, -1, 0};
    int r = 0, c = 0, d = 0;
    for (int v = 1; v <= R * C; ++v) {
        m[r][c] = v;
        int nr = r + dr[d], nc = c + dc[d];
        if (nr < 0 || nr >= R || nc < 0 || nc >= C || m[nr][nc] != 0) {   // blocked: turn right
            d = (d + 1) % 4;
            nr = r + dr[d]; nc = c + dc[d];
        }
        r = nr; c = nc;
    }
    return m;
}
```
