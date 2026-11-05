---
id: cpp-set-matrix-zeroes
title: Set Matrix Zeroes in O(1) Space
difficulty: Medium
order: 5
tags: matrix, in-place, marker technique, space optimization
time_limit: 1
---
## Statement
If a cell of an `R × C` matrix is 0, set its **entire row and column** to 0. The decisions must be based on the **original** zeros only, not on cells that became zero during the process.

```cpp
void set_zeroes(std::vector<std::vector<int>>& m);
```

Using two extra arrays (one for rows, one for columns) is the easy O(R + C) solution. Do it with **O(1) extra space**: use the matrix's own first row and first column as the marker arrays, plus two booleans that remember whether the first row and the first column originally contained a zero.

**Input:** cases until the end of input: `R C` followed by the matrix (R, C ≤ 1000). Print the matrix if R·C ≤ 60, otherwise the number of zeros and a checksum.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

void set_zeroes(vector<vector<int>>& m) {
    int R = m.size(), C = m[0].size();
    for (int i = 0; i < R; ++i)
        for (int j = 0; j < C; ++j)
            if (m[i][j] == 0) {                       // bug: zeros we create here cascade
                for (int k = 0; k < C; ++k) m[i][k] = 0;
                for (int k = 0; k < R; ++k) m[k][j] = 0;
            }
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int R, C;
    while (cin >> R >> C) {
        vector<vector<int>> m(R, vector<int>(C));
        for (auto& row : m) for (auto& x : row) cin >> x;
        set_zeroes(m);
        if (R * C <= 60) for (auto& row : m) for (int j = 0; j < C; ++j) cout << row[j] << (j + 1 < C ? ' ' : '\n');
        else {
            long long z = 0, h = 0;
            for (auto& row : m) for (int x : row) { z += x == 0; h = (h * 1000003 + x + 1000) % 998244353; }
            cout << z << " zeros, checksum " << h << '\n';
        }
        cout << "--\n";
    }
}
```

## Tests
=== sample
3 3
1 1 1
1 0 1
1 1 1
3 4
0 1 2 0
3 4 5 2
1 3 1 5
---
1 0 1
0 0 0
1 0 1
--
0 0 0 0
0 4 5 0
0 3 1 0
--
=== hidden
1 1
0
1 1
5
2 3
1 2 3
4 0 6
3 1
1
0
2
2 2
1 0
1 1
---
0
--
5
--
1 0 3
0 0 0
--
0
0
0
--
0 0
1 0
--
=== hidden
3 3
4 6 9
8 0 4
0 7 0
4 1
2
0
9
8
6 2
6 2
0 0
5 0
2 0
5 5
0 0
6 6
8 4 0 8 0 0
7 0 3 6 3 0
2 0 7 1 7 9
8 7 0 1 4 2
0 9 0 0 8 7
5 0 0 0 0 3
6 2
8 3
2 9
7 5
9 5
1 7
1 0
5 5
9 9 9 9 7
0 5 8 0 0
4 2 5 1 2
3 8 2 5 0
6 0 9 6 4
---
0 0 0
0 0 0
0 0 0
--
0
0
0
0
--
0 0
0 0
0 0
0 0
0 0
0 0
--
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
--
8 0
2 0
7 0
9 0
1 0
0 0
--
0 0 9 0 0
0 0 0 0 0
0 0 5 0 0
0 0 0 0 0
0 0 0 0 0
--
=== hidden
4 4
9 0 8 4
4 8 8 5
3 6 7 8
3 0 0 5
4 6
0 0 6 3 4 0
0 6 0 0 0 8
0 0 1 6 0 0
0 0 0 1 0 0
5 4
4 9 7 9
6 2 7 2
8 6 2 2
8 0 4 1
8 8 5 8
4 4
3 8 4 1
2 1 0 0
0 3 0 7
8 8 0 2
3 6
9 4 2 0 0 0
0 0 2 9 0 0
0 5 0 0 9 7
6 6
5 0 8 0 0 7
2 0 2 0 7 2
0 9 2 0 5 8
0 0 3 0 2 8
0 2 8 7 5 9
0 1 3 0 0 0
---
0 0 0 0
4 0 0 5
3 0 0 8
0 0 0 0
--
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
--
4 0 7 9
6 0 7 2
8 0 2 2
0 0 0 0
8 0 5 8
--
0 8 0 0
0 0 0 0
0 0 0 0
0 0 0 0
--
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
--
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
--
=== hidden
2 4
8 8 2 5
2 4 0 1
3 2
5 4
0 1
1 7
6 2
7 7
6 3
7 0
2 0
4 4
8 7
5 1
2
4
1
5
3
4 6
3 1 3 3 4 7
8 0 7 9 1 0
2 2 8 7 1 9
0 1 2 4 5 8
6 3
2 5 1
9 3 1
6 4 8
0 1 5
6 2 1
0 1 7
---
8 8 0 5
0 0 0 0
--
0 4
0 0
0 7
--
7 0
6 0
0 0
0 0
4 0
8 0
--
2
4
1
5
3
--
0 0 3 3 4 0
0 0 0 0 0 0
0 0 8 7 1 0
0 0 0 0 0 0
--
0 5 1
0 3 1
0 4 8
0 0 0
0 2 1
0 0 0
--
=== hidden
@gen 1021454931 big
=== hidden
@gen 1021454932 big
=== hidden
@gen 1021454933 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    R = r.randint(1, 6) if not big else 1000; C = r.randint(1, 6) if not big else 1000
    p = r.choice([0.05, 0.2, 0.5]) if not big else 0.000003
    print(R, C)
    for _ in range(R): print(*[0 if r.random() < p else r.randint(1, 9) for _ in range(C)])
```

## Hints
- Zeroing immediately while you scan is wrong, because new zeros cascade. Separate *marking* from *applying*.
- The first row and first column can store the marks for every column and row.
- Save whether row 0 and column 0 originally had a zero in two booleans, and zero them last.

## Solution
Row 0 and column 0 become the marker arrays: `m[i][0] == 0` means "row `i` must be zeroed", and `m[0][j] == 0` means "column `j` must be zeroed".

They are also real data, though, so first record in `row0` and `col0` whether they **originally** contained a zero. Then:

1. Mark: for every inner cell that is 0, zero its row marker and its column marker.
2. Apply: zero every inner cell whose row or column is marked.
3. Handle row 0 and column 0 last, from the two booleans. Doing them earlier would destroy the markers.

The starter's bug, zeroing immediately as you scan, is the reason for the two-phase design. Newly created zeros would trigger further zeroing.

Complexity: O(R·C) time, O(1) extra space.

```cpp
#include <bits/stdc++.h>
using namespace std;

void set_zeroes(vector<vector<int>>& m) {
    int R = m.size(), C = m[0].size();
    bool row0 = false, col0 = false;
    for (int j = 0; j < C; ++j) if (m[0][j] == 0) row0 = true;   // remember before overwriting
    for (int i = 0; i < R; ++i) if (m[i][0] == 0) col0 = true;
    for (int i = 1; i < R; ++i)                                   // mark using row 0 / column 0
        for (int j = 1; j < C; ++j)
            if (m[i][j] == 0) m[i][0] = m[0][j] = 0;
    for (int i = 1; i < R; ++i)                                   // apply to the inner cells
        for (int j = 1; j < C; ++j)
            if (m[i][0] == 0 || m[0][j] == 0) m[i][j] = 0;
    if (row0) for (int j = 0; j < C; ++j) m[0][j] = 0;            // finally the borders
    if (col0) for (int i = 0; i < R; ++i) m[i][0] = 0;
}
```
