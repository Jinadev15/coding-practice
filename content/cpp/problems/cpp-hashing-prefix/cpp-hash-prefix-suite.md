---
id: cpp-hash-prefix-suite
title: Custom Hashing and Prefix-Sum Counting
difficulty: Hard
order: 1
tags: unordered_map, custom hash, prefix sums, modular arithmetic, pairs
time_limit: 3
---
## Statement
Implement:

```cpp
long long count_divisible(const std::vector<int>& a, int m);
    // subarrays whose sum is divisible by m (values may be negative!); O(n + m)
int longest_balanced(const std::vector<int>& bits);
    // longest subarray with equally many 0s and 1s; O(n)
long long count_same_line_pairs(const std::vector<std::pair<int,int>>& pts);
    // pairs (i<j) where Manhattan distance == Euclidean distance, i.e. same x OR same y
    // (identical points count once). Needs hashing of x, y and (x, y). O(n) expected.
long long count_rect_sum(const std::vector<std::vector<int>>& g, long long target);
    // number of sub-rectangles of the R x C grid with sum == target (R <= C, R <= 60, C <= 600);
    // fix a row pair, then do a 1-D prefix-sum count with a hash map: O(R^2 * C)
```

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long count_divisible(const vector<int>& a, int m) {
    long long c = 0;
    for (size_t i = 0; i < a.size(); ++i) { long long s = 0; for (size_t j = i; j < a.size(); ++j) { s += a[j]; if (s % m == 0) ++c; } }
    return c;
}
int longest_balanced(const vector<int>& bits) { return 0; }
long long count_same_line_pairs(const vector<pair<int,int>>& pts) { return 0; }
long long count_rect_sum(const vector<vector<int>>& g, long long target) { return 0; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd;
    while (cin >> cmd) {
        if (cmd == "div") {
            int n, m; cin >> n >> m;
            vector<int> a(n); for (auto& x : a) cin >> x;
            cout << "count_divisible(m=" << m << ") = " << count_divisible(a, m) << '\n';
        } else if (cmd == "bal") {
            int n; cin >> n;
            vector<int> a(n); for (auto& x : a) cin >> x;
            cout << "longest_balanced = " << longest_balanced(a) << '\n';
        } else if (cmd == "pts") {
            int n; cin >> n;
            vector<pair<int,int>> p(n); for (auto& [x, y] : p) cin >> x >> y;
            cout << "same_line_pairs = " << count_same_line_pairs(p) << '\n';
        } else if (cmd == "rect") {
            int R, C; long long t; cin >> R >> C >> t;
            vector<vector<int>> g(R, vector<int>(C)); for (auto& row : g) for (auto& x : row) cin >> x;
            cout << "rect_sum(" << t << ") = " << count_rect_sum(g, t) << '\n';
        } else if (cmd == "gen") {
            int n; unsigned seed; cin >> n >> seed;
            mt19937 rng(seed);
            vector<int> a(n); for (auto& x : a) x = int(rng() % 2001) - 1000;
            vector<int> b(n); for (auto& x : b) x = rng() % 2;
            vector<pair<int,int>> p(n); for (auto& [x, y] : p) { x = int(rng() % 2000) - 1000000000; y = int(rng() % 2000) * 1000003; }
            vector<vector<int>> g(60, vector<int>(600)); for (auto& row : g) for (auto& x : row) x = int(rng() % 5) - 2;
            cout << "gen n=" << n << ": div7=" << count_divisible(a, 7) << " div1000=" << count_divisible(a, 1000)
                 << " bal=" << longest_balanced(b) << " pairs=" << count_same_line_pairs(p)
                 << " rect0=" << count_rect_sum(g, 0) << '\n';
        }
    }
}
```

## Tests
=== sample
div 6 5
4 5 0 -2 -3 1
bal 7
0 1 1 0 1 1 1
pts 3
1 1
7 5
1 5
rect 2 2 0
1 -1
-1 1
---
count_divisible(m=5) = 7
longest_balanced = 4
same_line_pairs = 2
rect_sum(0) = 5
=== hidden
div 1 3
-3
div 3 2
-1 -1 -1
bal 1
0
bal 4
1 1 0 0
pts 6
0 0
0 1
-2 0
-1 1
0 0
1 1
pts 2
5 5
5 5
rect 1 3 2
1 1 1
rect 3 3 1
1 0 0
0 1 0
0 0 1
---
count_divisible(m=3) = 1
count_divisible(m=2) = 2
longest_balanced = 0
longest_balanced = 4
same_line_pairs = 8
same_line_pairs = 1
rect_sum(2) = 2
rect_sum(1) = 19
=== hidden
gen 200000 9
---
gen n=200000: div7=2857119195 div1000=20001613 bal=176450 pairs=19990370 rect0=2949940

## Hints
- **Divisible**: normalise every prefix with `((p % m) + m) % m`, because C++ `%` can be negative, and count remainders in a `vector<long long>(m)`.
- **Balanced**: map 0 → −1. Then it's the longest zero-sum subarray: store the first index of each prefix value (`unordered_map`, or an offset array of size 2n+1).
- **Same-line pairs**: `pairs(x) + pairs(y) − pairs(x, y)`, where `pairs(key) = Σ c·(c−1)/2` over the groups. The (x, y) map needs a custom hash: pack into a `uint64_t`.
- **Rectangles**: for each top row r1, accumulate column sums down to r2, then count the subarrays of the column-sum array equal to target, using prefix sums + a hash map with `reserve`.

## Solution
```cpp
#include <bits/stdc++.h>
using namespace std;

long long count_divisible(const vector<int>& a, int m) {
    vector<long long> cnt(m, 0);
    cnt[0] = 1;
    long long p = 0, total = 0;
    for (int x : a) {
        p = ((p + x) % m + m) % m;               // C++ % keeps the dividend's sign: normalise
        total += cnt[p]++;
    }
    return total;
}

int longest_balanced(const vector<int>& bits) {
    int n = bits.size(), best = 0, p = 0;
    vector<int> first(2 * n + 1, INT_MIN);       // prefix ranges over [-n, n]
    first[n] = -1;
    for (int i = 0; i < n; ++i) {
        p += bits[i] ? 1 : -1;
        if (first[p + n] == INT_MIN) first[p + n] = i;
        else best = max(best, i - first[p + n]);
    }
    return best;
}

struct Pack64 {
    size_t operator()(uint64_t x) const noexcept {
        x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL; x ^= x >> 33;
        return x;
    }
};

long long count_same_line_pairs(const vector<pair<int,int>>& pts) {
    unordered_map<int, long long> xs, ys;
    unordered_map<uint64_t, long long, Pack64> both;
    xs.reserve(pts.size() * 2); ys.reserve(pts.size() * 2); both.reserve(pts.size() * 2);
    long long total = 0;
    for (auto [x, y] : pts) {
        uint64_t key = (uint64_t)(uint32_t)x << 32 | (uint32_t)y;
        total += xs[x]++ + ys[y]++ - both[key]++;   // pairs with every earlier point on the same line
    }
    return total;
}

long long count_rect_sum(const vector<vector<int>>& g, long long target) {
    int R = g.size(), C = R ? g[0].size() : 0;
    long long total = 0;
    vector<long long> col(C);
    unordered_map<long long, int> seen;
    seen.reserve(2 * C + 2);
    for (int r1 = 0; r1 < R; ++r1) {
        fill(col.begin(), col.end(), 0);
        for (int r2 = r1; r2 < R; ++r2) {
            for (int c = 0; c < C; ++c) col[c] += g[r2][c];
            seen.clear();
            seen[0] = 1;
            long long p = 0;
            for (int c = 0; c < C; ++c) {
                p += col[c];
                if (auto it = seen.find(p - target); it != seen.end()) total += it->second;
                ++seen[p];
            }
        }
    }
    return total;
}
```

- **Prefix-remainder counting** relies on normalising C++'s signed `%`. Without it, prefixes of −3 and 2 (both ≡ 2 mod 5) land in different buckets, and a negative remainder used as an index is out of bounds.
- **Balanced subarrays** become zero-sum subarrays after the 0 → −1 mapping. Because prefixes lie in [−n, n], a plain offset array replaces the hash map entirely.
- **Same-line pairs**: points sharing x or y satisfy |dx| + |dy| = √(dx² + dy²). Counting by inclusion–exclusion avoids counting identical points twice. Packing (x, y) into 64 bits with a strong mixer gives a fast, collision-resistant key, where `std::hash<pair>` doesn't exist and `x ^ y` would collide constantly.
- **Rectangles** reduce 2-D to 1-D by fixing the row pair, an O(R²·C) algorithm that's only fast because the hash map is `reserve`d and reused instead of rebuilt.
