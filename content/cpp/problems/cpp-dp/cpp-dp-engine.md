---
id: cpp-dp-engine
title: "DP Engine in C++: LIS, Edit Distance, Bitset Subset Sum, TSP"
difficulty: Hard
order: 1
tags: dynamic programming, LIS, rolling arrays, std::bitset, bitmask DP
time_limit: 3
---
## Statement
```cpp
int lis_strict(const std::vector<int>& a);                       // O(n log n)
int edit_distance(const std::string& s, const std::string& t);   // O(nm) time, O(m) memory; up to 10^4 x 10^4
std::vector<int> reachable_sums(const std::vector<int>& a, int limit);
    // all subset sums s with 0 <= s <= limit (limit <= 200000), ascending; use std::bitset<200001>
int tsp(const std::vector<std::vector<int>>& dist);              // closed tour from city 0, n <= 18
```

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int lis_strict(const vector<int>& a) {
    int n = a.size(), best = 0;
    vector<int> dp(n, 1);
    for (int i = 0; i < n; ++i) { for (int j = 0; j < i; ++j) if (a[j] < a[i]) dp[i] = max(dp[i], dp[j] + 1); best = max(best, dp[i]); }
    return best;
}
int edit_distance(const string& s, const string& t) {
    vector<vector<int>> d(s.size() + 1, vector<int>(t.size() + 1));
    for (size_t i = 0; i <= s.size(); ++i) d[i][0] = i;
    for (size_t j = 0; j <= t.size(); ++j) d[0][j] = j;
    for (size_t i = 1; i <= s.size(); ++i) for (size_t j = 1; j <= t.size(); ++j)
        d[i][j] = s[i-1] == t[j-1] ? d[i-1][j-1] : 1 + min({d[i-1][j-1], d[i-1][j], d[i][j-1]});
    return d[s.size()][t.size()];
}
vector<int> reachable_sums(const vector<int>& a, int limit) { return {0}; }
int tsp(const vector<vector<int>>& dist) { return 0; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd;
    while (cin >> cmd) {
        if (cmd == "lis") {
            int n; cin >> n; vector<int> a(n); for (auto& x : a) cin >> x;
            cout << "lis = " << lis_strict(a) << '\n';
        } else if (cmd == "edit") {
            string s, t; cin >> s >> t;
            if (s == "-") s.clear();
            if (t == "-") t.clear();
            cout << "edit = " << edit_distance(s, t) << '\n';
        } else if (cmd == "sums") {
            int n, lim; cin >> n >> lim; vector<int> a(n); for (auto& x : a) cin >> x;
            auto r = reachable_sums(a, lim);
            cout << "sums (" << r.size() << "):"; for (int x : r) cout << ' ' << x; cout << '\n';
        } else if (cmd == "tsp") {
            int n; cin >> n; vector<vector<int>> d(n, vector<int>(n));
            for (auto& row : d) for (auto& x : row) cin >> x;
            cout << "tsp = " << tsp(d) << '\n';
        } else if (cmd == "gen") {
            int n; unsigned seed; cin >> n >> seed;
            mt19937 rng(seed);
            vector<int> a(n); for (auto& x : a) x = rng() % 1000000;
            string s(10000, 'a'), t(10000, 'a');
            for (auto& c : s) c = char('a' + rng() % 4);
            for (auto& c : t) c = char('a' + rng() % 4);
            vector<int> w(400); for (auto& x : w) x = int(rng() % 2000) + 1;
            auto r = reachable_sums(w, 200000);
            int m = 17;
            vector<vector<int>> d(m, vector<int>(m));
            for (int i = 0; i < m; ++i) for (int j = 0; j < m; ++j) d[i][j] = i == j ? 0 : int(rng() % 1000) + 1;
            cout << "gen: lis=" << lis_strict(a) << " edit=" << edit_distance(s, t) << " sums=" << r.size()
                 << " max_sum=" << (r.empty() ? -1 : r.back()) << " tsp=" << tsp(d) << '\n';
        }
    }
}
```

## Tests
=== sample
lis 8
10 9 2 5 3 7 101 18
edit kitten sitting
sums 3 10
2 3 7
tsp 4
0 10 15 20
10 0 35 25
15 35 0 30
20 25 30 0
---
lis = 4
edit = 3
sums (7): 0 2 3 5 7 9 10
tsp = 80
=== hidden
lis 1
5
lis 4
3 3 3 3
lis 6
1 2 3 4 5 6
edit - abc
edit abc -
edit intention execution
sums 0 5
sums 2 3
5 6
sums 3 4
1 1 1
tsp 1
0
tsp 2
0 3
4 0
tsp 3
0 1 10
10 0 1
1 10 0
---
lis = 1
lis = 1
lis = 6
edit = 3
edit = 3
edit = 5
sums (1): 0
sums (1): 0
sums (4): 0 1 2 3
tsp = 0
tsp = 7
tsp = 3
=== hidden
gen 200000 6
---
gen: lis=878 edit=5155 sums=199982 max_sum=200000 tsp=1730

## Hints
- **LIS**: patience sorting, `lower_bound` on a `tails` vector.
- **edit**: two `vector<int>` rows, swapped with `swap(prev, cur)` (O(1)). `min({a, b, c})` takes an initializer list.
- **reachable_sums**: `bitset<200001> b; b[0] = 1; for (x : a) b |= b << x;`, then collect the set bits ≤ limit. Bits shifted past the end are discarded automatically.
- **TSP**: `dp[mask][v]` over masks containing city 0. For n = 18, that's 2¹⁸·18 ints (about 19 MB). Use a flat `vector<int>` and `INT_MAX / 2` as infinity.

## Solution
```cpp
#include <bits/stdc++.h>
using namespace std;

int lis_strict(const vector<int>& a) {
    vector<int> tails;
    for (int x : a) {
        auto it = lower_bound(tails.begin(), tails.end(), x);
        if (it == tails.end()) tails.push_back(x); else *it = x;
    }
    return tails.size();
}

int edit_distance(const string& s, const string& t) {
    int n = s.size(), m = t.size();
    vector<int> prev(m + 1), cur(m + 1);
    iota(prev.begin(), prev.end(), 0);
    for (int i = 1; i <= n; ++i) {
        cur[0] = i;
        const char si = s[i - 1];
        for (int j = 1; j <= m; ++j)
            cur[j] = si == t[j - 1] ? prev[j - 1] : 1 + min({prev[j - 1], prev[j], cur[j - 1]});
        swap(prev, cur);
    }
    return prev[m];
}

vector<int> reachable_sums(const vector<int>& a, int limit) {
    static bitset<200001> b;
    b.reset();
    b[0] = 1;
    for (int x : a) if (x <= 200000) b |= b << x;
    vector<int> out;
    for (int s = 0; s <= limit; ++s) if (b[s]) out.push_back(s);
    return out;
}

int tsp(const vector<vector<int>>& dist) {
    int n = dist.size();
    if (n == 1) return 0;
    const int INF = INT_MAX / 2, FULL = 1 << n;
    vector<int> dp((size_t)FULL * n, INF);
    auto at = [&](int mask, int v) -> int& { return dp[(size_t)mask * n + v]; };
    at(1, 0) = 0;
    for (int mask = 1; mask < FULL; mask += 2) {
        for (int v = 0; v < n; ++v) {
            int cur = at(mask, v);
            if (cur >= INF) continue;
            for (int u = 1; u < n; ++u)
                if (!(mask >> u & 1)) {
                    int& nx = at(mask | 1 << u, u);
                    nx = min(nx, cur + dist[v][u]);
                }
        }
    }
    int best = INF;
    for (int v = 1; v < n; ++v) best = min(best, at(FULL - 1, v) + dist[v][0]);
    return best;
}
```

- **LIS**: `lower_bound` keeps `tails` strictly increasing, giving O(n log n).
- **Edit distance** with rolling rows uses O(m) memory: 40 KB instead of the 400 MB a 10⁴ × 10⁴ `int` table would need. That's the difference between running and a memory-limit error. Swapping the two vectors costs a pointer exchange.
- **Bitset subset sums**: each item is one 200 001-bit shift-or, processing 64 sums per machine word. 400 items cost about 1.25 million word operations instead of 80 million boolean updates.
- **TSP** uses a flat `dp` array indexed `mask·n + v` (one allocation, cache-friendly) and only odd masks (city 0 always visited). For n = 18, that's about 2·10⁷ transitions per layer of u, comfortably within the time limit in C++.
