---
id: cpp-tp-dutch-flag
title: Dutch National Flag and Three-Way Partition
difficulty: Medium
order: 5
tags: two pointers, partitioning, Dutch national flag, invariants
time_limit: 2
---
## Statement
```cpp
void sort_colors(std::vector<int>& a);
    // a contains only 0, 1, 2; sort it in ONE pass, in place, without counting
void partition3(std::vector<int>& a, int lo, int hi);
    // rearrange so that all values < lo come first, then values in [lo, hi], then values > hi;
    // relative order inside groups doesn't matter; ONE pass, in place
```

Keep three regions and an unknown middle: `[0, lt)` holds group 0, `[lt, i)` group 1, `(gt, end]` group 2, and `[i, gt]` is unexamined. Each step classifies `a[i]`.

The driver checks that the result is a valid arrangement and reports the group sizes plus a check that your partition is a permutation of the input. For `sort_colors`, the exact output is also printed for small arrays.

**Input:** cases until the end of input: `colors n` + values, or `part n lo hi` + values (n ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

void sort_colors(vector<int>& a) {}
void partition3(vector<int>& a, int lo, int hi) {}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd; int n;
    while (cin >> cmd >> n) {
        int lo = 1, hi = 1;
        if (cmd == "part") cin >> lo >> hi;
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        vector<int> orig = a;
        if (cmd == "colors") sort_colors(a); else partition3(a, lo, hi);
        auto grp = [&](int x) { return x < lo ? 0 : x <= hi ? 1 : 2; };
        bool ok = true; int c[3] = {0, 0, 0};
        for (int i = 0; i < n; ++i) { ++c[grp(a[i])]; if (i && grp(a[i]) < grp(a[i - 1])) ok = false; }
        sort(orig.begin(), orig.end()); vector<int> b = a; sort(b.begin(), b.end());
        if (b != orig) ok = false;
        cout << (ok ? "valid" : "INVALID") << ' ' << c[0] << ' ' << c[1] << ' ' << c[2];
        if (cmd == "colors" && n <= 20) { cout << " :"; for (int x : a) cout << ' ' << x; }
        cout << '\n';
    }
}
```

## Tests
=== sample
colors 6
2 0 2 1 1 0
part 7 3 5
9 1 4 7 3 2 5
---
valid 2 2 2 : 0 0 1 1 2 2
valid 2 3 2
=== hidden
colors 1
2
colors 3
2 2 2
part 4 10 20
1 2 3 4
part 5 0 0
0 -1 1 0 0
---
valid 0 0 1 : 2
valid 0 0 3 : 2 2 2
valid 4 0 0
valid 1 3 1
=== hidden
part 9 1 3
-2 -5 7 -1 5 8 -1 -5 8
part 3 5 5
7 4 -1
part 11 -4 -3
1 3 2 -5 -3 7 1 3 0 3 -6
part 7 -1 -1
-6 3 6 6 6 0 6
colors 11
2 0 0 2 2 0 0 1 1 2 1
part 1 -3 0
5
---
valid 5 0 4
valid 2 0 1
valid 2 1 8
valid 1 0 6
valid 4 3 4 : 0 0 0 0 1 1 1 2 2 2 2
valid 0 0 1
=== hidden
colors 2
0 0
part 7 1 3
-2 0 -2 6 5 3 -5
part 3 0 0
-6 6 -5
part 12 -3 -3
8 8 -2 -6 3 -5 -8 7 2 -7 4 4
colors 8
0 2 1 2 0 2 2 0
colors 8
0 2 0 2 1 0 0 0
---
valid 2 0 0 : 0 0
valid 4 1 2
valid 2 0 1
valid 4 0 8
valid 3 1 4 : 0 0 0 1 2 2 2 2
valid 5 1 2 : 0 0 0 0 0 1 2 2
=== hidden
part 6 -2 -2
-6 5 7 -6 -7 -5
colors 11
2 2 0 1 1 0 1 0 1 0 0
colors 6
1 2 2 1 0 1
colors 5
0 0 1 1 2
colors 7
2 2 0 0 0 2 0
part 9 -3 -3
0 1 5 8 -6 2 2 5 -8
---
valid 4 0 2
valid 5 4 2 : 0 0 0 0 0 1 1 1 1 2 2
valid 1 3 2 : 0 1 1 1 2 2
valid 2 2 1 : 0 0 1 1 2
valid 4 0 3 : 0 0 0 0 2 2 2
valid 2 0 7
=== hidden
@gen 1350121287 big
=== hidden
@gen 1350121288 big
=== hidden
@gen 1350121289 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(1, 12) if not big else 1000000
    if r.random() < 0.5:
        print("colors", n); print(*[r.randint(0, 2) for _ in range(n)])
    else:
        lo = r.randint(-5, 5); hi = lo + r.randint(0, 4); print("part", n, lo, hi); print(*[r.randint(-8, 8) for _ in range(n)])
```

## Hints
- Maintain `lt`, `i` and `gt`, with regions small | middle | unknown | large.
- Small value: swap with `a[lt]`, and advance both `lt` and `i`. Middle value: advance `i`.
- Large value: swap with `a[gt]` and decrement `gt`, but do **not** advance `i`, because the swapped-in value hasn't been checked.

## Solution
**Invariant:**

| Range | Contents |
|---|---|
| `[0, lt)` | known small values |
| `[lt, i)` | known middle values |
| `[i, gt]` | unknown |
| `(gt, n)` | known large values |

Each step shrinks the unknown part by one:

- **Small:** swap it to `lt`. The value that comes back from `lt` was a middle value (or `i == lt`), so both `lt` and `i` advance.
- **Middle:** just advance `i`.
- **Large:** swap it to `gt` and shrink `gt`. The value swapped in is **unexamined**, so `i` stays.

`sort_colors` is the special case `lo = hi = 1`. This is the same three-way partition that makes quicksort fast on inputs with many duplicates.

Complexity: one pass, O(n) time, O(1) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

void partition3(vector<int>& a, int lo, int hi) {
    int lt = 0, i = 0, gt = (int)a.size() - 1;
    while (i <= gt) {
        if (a[i] < lo) swap(a[lt++], a[i++]);        // incoming a[lt] is a group-1 value (or i == lt)
        else if (a[i] > hi) swap(a[i], a[gt--]);     // incoming value is unexamined: don't advance i
        else ++i;
    }
}

void sort_colors(vector<int>& a) { partition3(a, 1, 1); }
```
