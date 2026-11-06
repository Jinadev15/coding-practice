---
id: cpp-ms-maximal-rectangle
title: Maximal Rectangle in a Binary Matrix
difficulty: Hard
order: 4
tags: monotonic stack, histogram, matrix, reduction
time_limit: 2
---
## Statement
```cpp
long long maximal_rectangle(const std::vector<std::string>& grid);   // rows of '0'/'1'
```

Return the area of the largest axis-aligned rectangle containing only `1`s.

```text
10100
10111
11111
10010      -> 6 (rows 1-2, columns 2-4)
```

Aim for **O(R · C)**.

**Input:** cases until the end of input: `R C`, then `R` rows of length `C` (R · C ≤ 4·10⁶ per case, R, C ≥ 1).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long maximal_rectangle(const vector<string>& grid) {
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
        cout << maximal_rectangle(g) << '\n';
    }
}
```

## Tests
=== sample
4 5
10100
10111
11111
10010
---
6
=== hidden
1 1
0
1 1
1
2 3
111
111
3 1
1
0
1
4 4
0110
1111
1111
0110
---
0
1
6
1
8
=== hidden
3 3
111
010
110
4 5
11111
01111
00111
01001
5 3
001
010
001
100
000
3 5
10100
10100
01110
5 6
100101
101011
001000
011001
010000
---
3
9
1
3
3
=== hidden
3 4
0000
0011
1111
6 2
11
11
11
01
11
11
4 2
11
11
11
11
6 5
11110
11110
11110
11111
11011
11111
5 4
1111
1111
1111
1101
0111
---
4
6
8
16
12
=== hidden
3 1
0
1
0
2 1
0
0
6 4
1111
1111
0001
1001
1111
0100
4 4
0000
1000
1111
1110
2 6
001001
001101
---
1
0
8
6
2
=== hidden
@gen 1486637650 big
=== hidden
@gen 1486637651 big
=== hidden
@gen 1486637652 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(5 if not big else 1):
    R = r.randint(1, 6) if not big else 2000
    C = r.randint(1, 6) if not big else 2000
    p = r.choice([0.5, 0.75, 0.9]) if not big else r.choice([0.97, 0.995])
    print(R, C)
    for _ in range(R):
        print("".join("1" if r.random() < p else "0" for _ in range(C)))
```

## Hints
- Fix the bottom row of the rectangle. What does the part of the grid above it look like, column by column?
- `h[c]` = number of consecutive 1s ending at the current row. Update it in O(1) per cell from the row above.
- Run "largest rectangle in a histogram" on `h` for every row; take the maximum.

## Solution
**Reduce to the histogram problem.** Fix the bottom row `r` of the rectangle. For each column, let `h[c]` be the number of consecutive `1`s ending at row `r` (0 if `grid[r][c]` is `0`). A rectangle whose bottom edge lies on row `r` is exactly a rectangle in the histogram `h`. So:

```text
row 0: 1 0 1 0 0
row 1: 2 0 2 1 1
row 2: 3 1 3 2 2    largest in histogram = 6 (heights 3 2 2 -> 2*3)
row 3: 4 0 0 3 0
```

Updating `h` from the previous row is O(C), and the histogram solve is O(C) with a monotonic stack, so the total is **O(R · C)**. Every rectangle is counted on its bottom row, so nothing is missed.

Reuse one stack buffer across rows to avoid reallocating. A brute force that tries all pairs of corners is O(R²C²) or worse.

```cpp
#include <bits/stdc++.h>
using namespace std;

static long long largest_in_histogram(const vector<int>& h, vector<int>& st) {
    int n = h.size();
    st.clear();
    long long best = 0;
    for (int i = 0; i <= n; ++i) {
        int cur = (i == n) ? -1 : h[i];
        while (!st.empty() && h[st.back()] >= cur) {
            long long height = h[st.back()]; st.pop_back();
            int left = st.empty() ? 0 : st.back() + 1;
            best = max(best, height * (i - left));
        }
        st.push_back(i);
    }
    return best;
}

long long maximal_rectangle(const vector<string>& grid) {
    int R = grid.size(), C = grid[0].size();
    vector<int> h(C, 0), st;
    st.reserve(C + 1);
    long long best = 0;
    for (int r = 0; r < R; ++r) {
        for (int c = 0; c < C; ++c) h[c] = grid[r][c] == '1' ? h[c] + 1 : 0;   // run of 1s ending at row r
        best = max(best, largest_in_histogram(h, st));
    }
    return best;
}
```
