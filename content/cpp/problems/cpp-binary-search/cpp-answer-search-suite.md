---
id: cpp-answer-search-suite
title: Binary Search on Answers in C++
difficulty: Hard
order: 1
tags: binary search, lower_bound, monotone predicate, two pointers
time_limit: 3
---
## Statement
```cpp
long long kth_pair_distance(std::vector<int> a, long long k);
    // k-th smallest |a[i]-a[j]| over pairs i<j (1-based k): binary search the distance + two-pointer counting
int min_largest_split(const std::vector<int>& a, int parts);
    // split into `parts` contiguous non-empty pieces minimising the largest piece sum (fits in int)
long long max_min_spacing(std::vector<long long> pos, int robots);
    // place robots at distinct positions maximising the minimum gap (positions up to 1e18)
std::vector<int> range_counts(std::vector<int> a, const std::vector<std::pair<int,int>>& qs);
    // for each query (lo, hi): number of elements with lo <= a[i] <= hi (sort once, then lower/upper_bound)
```

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long kth_pair_distance(vector<int> a, long long k) {
    vector<long long> d;
    for (size_t i = 0; i < a.size(); ++i) for (size_t j = i + 1; j < a.size(); ++j) d.push_back(llabs((long long)a[i] - a[j]));
    sort(d.begin(), d.end());
    return d[k - 1];
}
int min_largest_split(const vector<int>& a, int parts) { return *max_element(a.begin(), a.end()); }
long long max_min_spacing(vector<long long> pos, int robots) { return 0; }
vector<int> range_counts(vector<int> a, const vector<pair<int,int>>& qs) {
    vector<int> out;
    for (auto [lo, hi] : qs) out.push_back(count_if(a.begin(), a.end(), [&](int x) { return lo <= x && x <= hi; }));
    return out;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd;
    while (cin >> cmd) {
        if (cmd == "kth") {
            int n; long long k; cin >> n >> k;
            vector<int> a(n); for (auto& x : a) cin >> x;
            cout << "kth_pair_distance(" << k << ") = " << kth_pair_distance(a, k) << '\n';
        } else if (cmd == "split") {
            int n, p; cin >> n >> p;
            vector<int> a(n); for (auto& x : a) cin >> x;
            cout << "min_largest_split(" << p << ") = " << min_largest_split(a, p) << '\n';
        } else if (cmd == "space") {
            int n, r; cin >> n >> r;
            vector<long long> a(n); for (auto& x : a) cin >> x;
            cout << "max_min_spacing(" << r << ") = " << max_min_spacing(a, r) << '\n';
        } else if (cmd == "range") {
            int n, q; cin >> n >> q;
            vector<int> a(n); for (auto& x : a) cin >> x;
            vector<pair<int,int>> qs(q); for (auto& [l, h] : qs) cin >> l >> h;
            auto r = range_counts(a, qs);
            cout << "range_counts:"; for (int x : r) cout << ' ' << x; cout << '\n';
        } else if (cmd == "gen") {
            int n; unsigned long long seed; cin >> n >> seed;
            mt19937_64 rng(seed);
            vector<int> a(n); for (auto& x : a) x = int(rng() % 1000000000);
            long long total = 1LL * n * (n - 1) / 2;
            vector<long long> pos(n); for (auto& x : pos) x = (long long)(rng() % 1000000000000000000ULL);
            vector<int> w(n); for (auto& x : w) x = int(rng() % 10000);
            vector<pair<int,int>> qs(n);
            for (auto& [l, h] : qs) { int u = int(rng() % 1000000000), v = int(rng() % 1000000000); l = min(u, v); h = max(u, v); }
            auto rc = range_counts(a, qs);
            cout << "gen n=" << n << ": kth_mid=" << kth_pair_distance(a, total / 2) << " kth_1=" << kth_pair_distance(a, 1)
                 << " split=" << min_largest_split(w, 100) << " space=" << max_min_spacing(pos, 1000)
                 << " range_sum=" << accumulate(rc.begin(), rc.end(), 0LL) << '\n';
        }
    }
}
```

## Tests
=== sample
kth 3 1
1 3 1
split 5 2
7 2 5 10 8
space 5 3
1 2 8 4 9
range 5 3
1 3 3 7 9
3 3
0 10
4 6
---
kth_pair_distance(1) = 0
min_largest_split(2) = 18
max_min_spacing(3) = 3
range_counts: 2 5 0
=== hidden
kth 2 1
5 -5
kth 4 6
1 6 1 6
kth 5 7
9 1 4 7 3
split 1 1
42
split 4 4
1 2 3 4
split 3 1
1 2 3
space 2 2
0 1000000000000000000
space 4 4
5 1 3 2
range 1 2
5
5 5
6 10
---
kth_pair_distance(1) = 10
kth_pair_distance(6) = 5
kth_pair_distance(7) = 5
min_largest_split(1) = 42
min_largest_split(4) = 4
min_largest_split(1) = 6
max_min_spacing(2) = 1000000000000000000
max_min_spacing(4) = 1
range_counts: 1 0
=== hidden
gen 200000 21
---
gen n=200000: kth_mid=292284403 kth_1=0 split=10011037 space=996142759225604 range_sum=13343369340

## Hints
- **kth_pair_distance**: sort. `count(d)` = the number of pairs with difference ≤ d, found with two pointers in O(n). Find the smallest d with `count(d) >= k`, searching over `[0, max − min]`.
- **min_largest_split**: the answer is in `[max, sum]`; greedily cut when adding the next value would exceed the candidate.
- **max_min_spacing**: sort; greedy placement is monotone (feasible for small gaps). Search for the largest feasible gap, rounding the midpoint **up**, using `__int128` or careful arithmetic for 10¹⁸.
- **range_counts**: sort a once, then `upper_bound(hi) - lower_bound(lo)` per query.

## Solution
```cpp
#include <bits/stdc++.h>
using namespace std;

long long kth_pair_distance(vector<int> a, long long k) {
    sort(a.begin(), a.end());
    auto count_le = [&](long long d) {
        long long c = 0;
        for (size_t i = 0, j = 0; j < a.size(); ++j) {
            while ((long long)a[j] - a[i] > d) ++i;
            c += (long long)(j - i);
        }
        return c;
    };
    long long lo = 0, hi = (long long)a.back() - a.front();
    while (lo < hi) {
        long long mid = lo + (hi - lo) / 2;
        if (count_le(mid) >= k) hi = mid; else lo = mid + 1;
    }
    return lo;
}

int min_largest_split(const vector<int>& a, int parts) {
    auto ok = [&](long long cap) {
        int used = 1; long long cur = 0;
        for (int x : a) {
            if (cur + x > cap) { ++used; cur = 0; }
            cur += x;
        }
        return used <= parts;
    };
    long long lo = *max_element(a.begin(), a.end()), hi = accumulate(a.begin(), a.end(), 0LL);
    while (lo < hi) {
        long long mid = lo + (hi - lo) / 2;
        if (ok(mid)) hi = mid; else lo = mid + 1;
    }
    return (int)lo;
}

long long max_min_spacing(vector<long long> pos, int robots) {
    sort(pos.begin(), pos.end());
    auto fits = [&](long long gap) {
        int placed = 1; long long last = pos[0];
        for (size_t i = 1; i < pos.size() && placed < robots; ++i)
            if (pos[i] - last >= gap) { ++placed; last = pos[i]; }
        return placed >= robots;
    };
    long long lo = 0, hi = pos.back() - pos.front();
    while (lo < hi) {
        long long mid = lo + (hi - lo + 1) / 2;       // round up: we move lo = mid
        if (fits(mid)) lo = mid; else hi = mid - 1;
    }
    return lo;
}

vector<int> range_counts(vector<int> a, const vector<pair<int,int>>& qs) {
    sort(a.begin(), a.end());
    vector<int> out;
    out.reserve(qs.size());
    for (auto [lo, hi] : qs)
        out.push_back(int(upper_bound(a.begin(), a.end(), hi) - lower_bound(a.begin(), a.end(), lo)));
    return out;
}
```

All four reduce to **"find the boundary of a monotone predicate"**:
- **k-th pair distance** never enumerates the n²/2 pairs (2·10¹⁰ for n = 2·10⁵). It binary-searches the *value* and counts pairs with a linear two-pointer sweep, giving O(n log n + n log V).
- **Split and spacing** are classic search-on-the-answer problems. Note the round-up midpoint in the maximisation, and that no arithmetic exceeds `long long` even with positions up to 10¹⁸ (`hi − lo` and `lo + (hi − lo + 1)/2` stay in range).
- **range_counts** uses `upper_bound − lower_bound` on a sorted copy, the idiomatic STL range count.
