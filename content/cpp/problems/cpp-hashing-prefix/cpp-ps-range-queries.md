---
id: cpp-ps-range-queries
title: Range Sum and Range XOR Queries
difficulty: Easy
order: 1
tags: prefix sums, prefix xor, queries
time_limit: 1
---
## Statement
Preprocess an array once, then answer many queries in O(1) each:

```cpp
class RangeQueries {
public:
    explicit RangeQueries(const std::vector<long long>& a);
    long long sum(int l, int r) const;        // a[l] + ... + a[r]   (0-based, inclusive)
    long long xr(int l, int r) const;         // a[l] ^ ... ^ a[r]
    int count_equal(int l, int r, long long v) const;   // occurrences of v in a[l..r]
};
```

Build prefix arrays with a leading zero (`P[0] = 0`, `P[i+1] = P[i] + a[i]`). Then `sum(l, r) = P[r+1] − P[l]`, and XOR works the same way because `x ^ x = 0`.

For `count_equal`, prefix sums per value would need too much memory. Instead, store the sorted list of positions for each value, and count positions inside `[l, r]` with two binary searches.

**Input:** `n`, then n values, then `q`, then q queries `S l r`, `X l r` or `C l r v`. n, q ≤ 2·10⁵, |a[i]| ≤ 10⁹.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class RangeQueries {
    vector<long long> a;
public:
    explicit RangeQueries(const vector<long long>& v) : a(v) {}
    long long sum(int l, int r) const { long long s = 0; for (int i = l; i <= r; ++i) s += a[i]; return s; }
    long long xr(int l, int r) const { long long s = 0; for (int i = l; i <= r; ++i) s ^= a[i]; return s; }
    int count_equal(int l, int r, long long v) const { int c = 0; for (int i = l; i <= r; ++i) c += a[i] == v; return c; }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; cin >> n;
    vector<long long> a(n);
    for (auto& x : a) cin >> x;
    RangeQueries rq(a);
    int q; cin >> q;
    while (q--) {
        char t; int l, r; cin >> t >> l >> r;
        if (t == 'S') cout << rq.sum(l, r) << '\n';
        else if (t == 'X') cout << rq.xr(l, r) << '\n';
        else { long long v; cin >> v; cout << rq.count_equal(l, r, v) << '\n'; }
    }
}
```

## Tests
=== sample
5
3 1 4 1 5
4
S 1 3
X 0 4
C 0 4 1
C 2 4 9
---
6
2
2
0
=== hidden
1
-7
3
S 0 0
X 0 0
C 0 0 -7
---
-7
-7
1
=== hidden
3
-3 1 3
20
C 0 0 -3
S 0 0
C 1 2 1
S 2 2
X 2 2
X 2 2
C 2 2 1
X 0 1
S 0 2
C 0 1 3
C 2 2 -3
S 2 2
C 1 1 3
S 1 1
S 0 2
C 0 2 -3
S 2 2
C 1 1 3
X 0 2
X 1 1
---
1
-3
1
3
3
3
0
-4
1
0
0
3
0
1
1
1
3
0
-1
1
=== hidden
10
-3 -5 5 -3 0 -2 1 -4 3 3
20
C 1 6 -2
S 0 6
C 3 5 -5
S 0 7
S 7 8
C 7 8 1
C 3 6 -5
X 8 8
X 0 6
S 9 9
S 2 6
C 0 7 5
C 4 7 -2
S 8 8
X 2 8
X 2 7
X 3 5
C 7 8 3
C 3 7 5
C 1 2 3
---
1
-7
0
-11
-1
0
0
3
1
3
1
1
1
3
-8
-5
3
1
0
0
=== hidden
5
4 1 -5 -2 3
20
C 4 4 4
C 1 3 3
C 4 4 3
C 4 4 4
S 3 4
S 2 4
C 4 4 -2
X 4 4
X 0 1
S 2 2
C 3 3 -5
S 1 3
S 3 4
X 2 4
X 1 4
C 3 3 1
X 4 4
S 4 4
S 1 1
C 4 4 1
---
0
0
1
0
1
-4
0
3
5
-5
0
-6
1
6
7
0
3
3
1
0
=== hidden
@gen 2638988802 big
=== hidden
@gen 2638988803 big
=== hidden
@gen 2638988804 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
n = r.randint(1, 10) if not big else 200000
a = [r.randint(-5, 5) if not big else r.randint(-10**9, 10**9) % 1000 for _ in range(n)]
print(n); print(*a)
q = 20 if not big else 200000
print(q)
out = []
for _ in range(q):
    l = r.randrange(n); rr = r.randrange(l, n); t = r.choice("SXC")
    out.append(f"{t} {l} {rr}" + (f" {r.choice(a)}" if t == "C" else ""))
print("\n".join(out))
```

## Hints
- Build `P` with n+1 entries and a leading 0. Then a range sum is one subtraction.
- XOR has an inverse too: itself. Build a prefix XOR the same way.
- For counting a value, store the list of indices where each value occurs, and binary-search the range ends.

## Solution
**Prefix sums.** `P[i]` holds the sum of the first `i` elements, so the sum of `a[l..r]` is everything up to `r` minus everything before `l`: `P[r+1] − P[l]`. The leading 0 makes `l = 0` need no special case.

**Prefix XOR.** XOR is its own inverse (`x ^ x = 0`), so `X[r+1] ^ X[l]` cancels the common prefix, exactly like subtraction.

**Counting a value in a range.** Prefix counts for every distinct value would be O(n · distinct) memory. Instead, keep each value's sorted positions. The count in `[l, r]` is `upper_bound(r) − lower_bound(l)`, which is O(log n). (This "positions list + binary search" trick appears often.)

Complexity: O(n) to build, O(1) for sums and XORs, O(log n) for counts.

```cpp
#include <bits/stdc++.h>
using namespace std;

class RangeQueries {
    vector<long long> P, X;                        // prefix sums and prefix XORs, size n+1
    unordered_map<long long, vector<int>> pos;     // value -> sorted positions
public:
    explicit RangeQueries(const vector<long long>& a) : P(a.size() + 1, 0), X(a.size() + 1, 0) {
        for (size_t i = 0; i < a.size(); ++i) {
            P[i + 1] = P[i] + a[i];
            X[i + 1] = X[i] ^ a[i];
            pos[a[i]].push_back((int)i);           // indices arrive in increasing order
        }
    }
    long long sum(int l, int r) const { return P[r + 1] - P[l]; }
    long long xr(int l, int r) const { return X[r + 1] ^ X[l]; }
    int count_equal(int l, int r, long long v) const {
        auto it = pos.find(v);
        if (it == pos.end()) return 0;
        const auto& p = it->second;
        return int(upper_bound(p.begin(), p.end(), r) - lower_bound(p.begin(), p.end(), l));
    }
};
```
