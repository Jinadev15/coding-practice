---
id: cpp-rotate-matrix
title: Rotating and Flipping a Square Matrix In Place
difficulty: Medium
order: 4
tags: matrix, transpose, in-place, rotation
time_limit: 1
---
## Statement
Implement in-place transformations of an `n × n` matrix (no second matrix allowed):

```cpp
void transpose(std::vector<std::vector<int>>& m);        // m[i][j] <-> m[j][i]
void rotate_cw(std::vector<std::vector<int>>& m);        // 90° clockwise
void rotate_ccw(std::vector<std::vector<int>>& m);       // 90° counter-clockwise
void apply(std::vector<std::vector<int>>& m, const std::string& ops);
    // ops is a string of 'R' (clockwise), 'L' (counter-clockwise), 'T' (transpose); up to 10^5 ops
```

`apply` gets up to 10⁵ operations on a 500 × 500 matrix. Doing them one by one costs 10⁵ × 2.5·10⁵ steps, far too slow. Notice that rotations **combine**: four clockwise rotations do nothing, and a transpose followed by a transpose does nothing. Compose the operations first, then apply at most a couple of transformations.

**Hint for composing:** every combination of these operations is one of only 8 symmetries of the square (4 rotations, with or without a transpose). Track `(t, r)` meaning "first transpose `t` times (0 or 1), then rotate clockwise `r` times". You need the rule for what happens when a `T` comes after a rotation.

**Input:** cases until the end of input: `n ops`, followed by the matrix. Use `-` for an empty operation list. Print the matrix if n ≤ 6, otherwise a checksum and the four corner values.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

void transpose(vector<vector<int>>& m) {}
void rotate_cw(vector<vector<int>>& m) {}
void rotate_ccw(vector<vector<int>>& m) {}
void apply(vector<vector<int>>& m, const string& ops) {
    for (char c : ops) { if (c == 'R') rotate_cw(m); else if (c == 'L') rotate_ccw(m); else if (c == 'T') transpose(m); }
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; string ops;
    while (cin >> n >> ops) {
        vector<vector<int>> m(n, vector<int>(n));
        for (auto& row : m) for (auto& x : row) cin >> x;
        apply(m, ops == "-" ? string() : ops);
        if (n <= 6) {
            for (auto& row : m) for (int j = 0; j < n; ++j) cout << row[j] << (j + 1 < n ? ' ' : '\n');
        } else {
            long long h = 0;
            for (auto& row : m) for (int x : row) h = (h * 1000003 + x + 7) % 998244353;
            cout << h << " corners " << m[0][0] << ' ' << m[0][n-1] << ' ' << m[n-1][0] << ' ' << m[n-1][n-1] << '\n';
        }
        cout << "--\n";
    }
}
```

## Tests
=== sample
3 R
1 2 3
4 5 6
7 8 9
3 L
1 2 3
4 5 6
7 8 9
3 TR
1 2 3
4 5 6
7 8 9
---
7 4 1
8 5 2
9 6 3
--
3 6 9
2 5 8
1 4 7
--
3 2 1
6 5 4
9 8 7
--
=== hidden
1 RRT
5
2 -
1 2
3 4
2 RT
1 2
3 4
4 LLLLTT
1 2 3 4
5 6 7 8
9 10 11 12
13 14 15 16
3 RTLT
1 2 3
4 5 6
7 8 9
---
5
--
1 2
3 4
--
3 4
1 2
--
1 2 3 4
5 6 7 8
9 10 11 12
13 14 15 16
--
9 8 7
6 5 4
3 2 1
--
=== hidden
1 RTRRTTR
25
6 LRTL
17 1 18 85 74 44
88 81 89 74 35 17
50 52 41 64 41 90
83 83 23 21 61 18
70 83 6 20 98 70
43 8 94 68 20 69
4 TLTT
54 58 97 92
50 57 33 79
12 73 22 46
39 30 22 11
6 RTRRTL
89 45 96 93 48 54
50 68 71 1 62 7
28 10 38 62 75 44
7 6 9 40 82 79
53 38 88 99 96 3
3 62 42 94 16 74
2 LR
85 82
21 21
---
25
--
43 8 94 68 20 69
70 83 6 20 98 70
83 83 23 21 61 18
50 52 41 64 41 90
88 81 89 74 35 17
17 1 18 85 74 44
--
39 30 22 11
12 73 22 46
50 57 33 79
54 58 97 92
--
74 16 94 42 62 3
3 96 99 88 38 53
79 82 40 9 6 7
44 75 62 38 10 28
7 62 1 71 68 50
54 48 93 96 45 89
--
85 82
21 21
--
=== hidden
2 LLLT
17 7
48 47
4 LL
21 45 75 23
17 3 47 50
29 92 12 68
45 40 72 29
2 RLL
14 67
71 73
6 TLLLTL
91 16 1 57 47 58
98 6 52 30 46 49
1 17 56 73 39 70
7 53 56 5 8 29
64 82 4 17 10 60
53 86 15 73 78 97
4 TTTLT
38 25 81 84
87 10 29 85
67 2 51 84
89 39 67 29
---
48 47
17 7
--
29 72 40 45
68 12 92 29
50 47 3 17
23 75 45 21
--
67 73
14 71
--
97 78 73 15 86 53
60 10 17 4 82 64
29 8 5 56 53 7
70 39 73 56 17 1
49 46 30 52 6 98
58 47 57 1 16 91
--
89 67 87 38
39 2 10 25
67 51 29 81
29 84 85 84
--
=== hidden
3 RRLLLL
57 17 9
12 23 96
28 38 62
5 LRTT
52 65 90 94 30
47 91 28 43 62
66 16 11 42 33
19 88 31 13 3
95 43 9 20 86
4 LRLRT
23 57 62 77
97 89 88 18
67 42 25 75
39 15 55 84
5 LTRRRLL
34 3 68 70 30
85 82 77 89 79
84 42 41 50 43
7 53 21 68 33
93 48 35 24 58
1 TLRTLR
92
---
62 38 28
96 23 12
9 17 57
--
52 65 90 94 30
47 91 28 43 62
66 16 11 42 33
19 88 31 13 3
95 43 9 20 86
--
23 97 67 39
57 89 42 15
62 88 25 55
77 18 75 84
--
58 33 43 79 30
24 68 50 89 70
35 21 41 77 68
48 53 42 82 3
93 7 84 85 34
--
92
--
=== hidden
@gen 1980617536 big
=== hidden
@gen 1980617537 big
=== hidden
@gen 1980617538 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(5 if not big else 1):
    n = r.randint(1, 6) if not big else 500
    k = r.randint(0, 8) if not big else 100000
    ops = "".join(r.choice("RLT") for _ in range(k)) or "-"
    print(n, ops)
    for i in range(n): print(*[r.randint(1, 99) for _ in range(n)])
```

## Hints
- Clockwise rotation = transpose + reverse every row. Check it on a 2×2 example.
- Applying 10⁵ operations one by one is too slow. Four `R`s cancel out, and so do two `T`s.
- Keep the state as `(t, r)`, meaning "transpose `t` times, then rotate `r` times". Work out what `T` does to `r` when it comes after the rotations.

## Solution
**The building blocks.**

- *Transpose* swaps across the main diagonal. Loop over `j > i` only, otherwise every pair gets swapped back.
- *Clockwise* = transpose, then reverse each row.
- *Counter-clockwise* = reverse each row, then transpose.

Each is O(n²) with O(1) extra space.

**Composing operations.** The 8 symmetries of a square form a group, so any sequence of operations collapses to "transpose `t` times, then rotate `r` times". Rotations just add to `r` (mod 4).

A transpose appended after `r` rotations needs the identity `T ∘ Rotʳ = Rot⁻ʳ ∘ T`. Transposing a rotated square is the same as rotating the transposed square the opposite way. So `t` flips and `r` becomes `−r mod 4`.

At the end, apply at most one transpose and three rotations, no matter how long the operation string was.

Complexity: O(len(ops) + n²).

```cpp
#include <bits/stdc++.h>
using namespace std;

void transpose(vector<vector<int>>& m) {
    int n = m.size();
    for (int i = 0; i < n; ++i)
        for (int j = i + 1; j < n; ++j) swap(m[i][j], m[j][i]);
}
void rotate_cw(vector<vector<int>>& m) {                 // transpose, then mirror each row
    transpose(m);
    for (auto& row : m) reverse(row.begin(), row.end());
}
void rotate_ccw(vector<vector<int>>& m) {                // mirror each row, then transpose
    for (auto& row : m) reverse(row.begin(), row.end());
    transpose(m);
}

void apply(vector<vector<int>>& m, const string& ops) {
    // State: the result equals "transpose t times, then rotate clockwise r times".
    // A transpose AFTER r rotations equals: transpose first, then rotate (4 - r) times,
    // because T∘Rot^r = Rot^(-r)∘T for the symmetries of a square.
    int t = 0, r = 0;
    for (char c : ops) {
        if (c == 'R') r = (r + 1) % 4;
        else if (c == 'L') r = (r + 3) % 4;
        else { t ^= 1; r = (4 - r) % 4; }
    }
    if (t) transpose(m);
    for (int i = 0; i < r; ++i) rotate_cw(m);
}
```
