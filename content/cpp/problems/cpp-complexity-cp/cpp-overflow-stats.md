---
id: cpp-overflow-stats
title: Overflow-Proof Statistics at Scale
difficulty: Medium
order: 1
tags: overflow, long long, __int128, floor division, sorting, two pointers
time_limit: 2
---
## Statement
Sensor logs hold up to 2·10⁶ readings with magnitudes up to 10⁹ (or 10¹⁸ for timestamps). Implement four functions that are **fast** (O(n log n) at most) and **never overflow**:

```cpp
std::string dot_exact(const std::vector<long long>& a, const std::vector<long long>& b);
    // exact Σ a[i]*b[i] as a decimal string; |a[i]|, |b[i]| <= 10^18 (needs __int128 and manual printing)
long long floor_mean(const std::vector<long long>& a);
    // floor(Σa / n) rounding toward MINUS infinity (n >= 1, |a[i]| <= 10^18; the sum may exceed long long)
long long count_close_pairs(std::vector<int> a, long long k);
    // number of pairs i<j with |a[i] - a[j]| <= k (a[i] in [-10^9, 10^9], k up to 4*10^9)
long long sum_of_pair_mins(std::vector<int> a);
    // Σ over all pairs i<j of min(a[i], a[j])  (fits in long long for the test sizes)
```

The driver generates big arrays from a seed.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

string dot_exact(const vector<long long>& a, const vector<long long>& b) {
    long long s = 0;
    for (size_t i = 0; i < a.size(); ++i) s += a[i] * b[i];
    return to_string(s);
}
long long floor_mean(const vector<long long>& a) {
    long long s = 0;
    for (auto x : a) s += x;
    return s / (long long)a.size();
}
long long count_close_pairs(vector<int> a, long long k) {
    long long c = 0;
    for (size_t i = 0; i < a.size(); ++i)
        for (size_t j = i + 1; j < a.size(); ++j)
            if (abs(a[i] - a[j]) <= k) ++c;
    return c;
}
long long sum_of_pair_mins(vector<int> a) {
    long long s = 0;
    for (size_t i = 0; i < a.size(); ++i)
        for (size_t j = i + 1; j < a.size(); ++j) s += min(a[i], a[j]);
    return s;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd;
    while (cin >> cmd) {
        if (cmd == "dot") {
            int n; cin >> n;
            vector<long long> a(n), b(n);
            for (auto& x : a) cin >> x;
            for (auto& x : b) cin >> x;
            cout << "dot = " << dot_exact(a, b) << '\n';
        } else if (cmd == "mean") {
            int n; cin >> n;
            vector<long long> a(n);
            for (auto& x : a) cin >> x;
            cout << "floor_mean = " << floor_mean(a) << '\n';
        } else if (cmd == "close") {
            int n; long long k; cin >> n >> k;
            vector<int> a(n);
            for (auto& x : a) cin >> x;
            cout << "close_pairs(k=" << k << ") = " << count_close_pairs(a, k) << '\n';
        } else if (cmd == "mins") {
            int n; cin >> n;
            vector<int> a(n);
            for (auto& x : a) cin >> x;
            cout << "pair_mins = " << sum_of_pair_mins(a) << '\n';
        } else if (cmd == "gen") {
            int n; unsigned long long seed; cin >> n >> seed;
            mt19937_64 rng(seed);
            vector<long long> a(n), b(n);
            for (auto& x : a) x = (long long)(rng() % 2000000000000000001ULL) - 1000000000000000000LL;
            for (auto& x : b) x = (long long)(rng() % 2000000000000000001ULL) - 1000000000000000000LL;
            vector<int> c(n);
            for (auto& x : c) x = (int)((long long)(rng() % 2000000001ULL) - 1000000000LL);
            vector<int> d(n);
            for (auto& x : d) x = (int)(rng() % 1000) + 1;
            cout << "gen n=" << n << ": dot=" << dot_exact(a, b) << " mean=" << floor_mean(a)
                 << " close=" << count_close_pairs(c, 1000000) << " close_all=" << count_close_pairs(c, 4000000000LL)
                 << " mins=" << sum_of_pair_mins(d) << '\n';
        }
    }
}
```

## Tests
=== sample
dot 3
1 2 3
4 5 6
mean 4
-1 -2 -3 -5
close 5 2
1 5 3 9 4
mins 4
3 1 2 3
---
dot = 32
floor_mean = -3
close_pairs(k=2) = 4
pair_mins = 10
=== hidden
dot 2
1000000000000000000 1000000000000000000
1000000000000000000 1000000000000000000
dot 2
-1000000000000000000 1
1000000000000000000 -7
dot 1
0
5
mean 3
1000000000000000000 1000000000000000000 1000000000000000000
mean 2
-1000000000000000000 -999999999999999999
mean 1
-7
mean 2
3 4
close 3 4000000000
-1000000000 1000000000 0
close 4 0
7 7 7 -7
mins 1
5
mins 3
-5 -5 2
---
dot = 2000000000000000000000000000000000000
dot = -1000000000000000000000000000000000007
dot = 0
floor_mean = 1000000000000000000
floor_mean = -1000000000000000000
floor_mean = -7
floor_mean = 3
close_pairs(k=4000000000) = 3
close_pairs(k=0) = 3
pair_mins = 0
pair_mins = -15
=== hidden
gen 200000 1
---
gen n=200000: dot=-103760673357119511306413196942654691439 mean=-18347344511380697 close=20001663 close_all=19999900000 mins=6649785109565
=== hidden
gen 2000000 7
---
gen n=2000000: dot=775027921199021201088720450941684661562 mean=-18614380315307830 close=1999452965 close_all=1999999000000 mins=668063952049785

## Hints
- **dot_exact**: each product fits in `__int128` (≤ 10³⁶), but the sum of 2·10⁶ of them (≤ 2·10⁴²) exceeds `__int128`'s range (about 1.7·10³⁸). Keep the running sum as two bounded parts, `hi·10¹⁸ + lo`: add `p / 10¹⁸` to hi and `p % 10¹⁸` to lo, and carry when |lo| ≥ 10¹⁸. Print with a manual digit loop, since streams can't print `__int128`.
- **floor_mean**: compute the sum in `__int128`, then floor-divide. C++ `/` truncates toward zero, so adjust when the remainder is non-zero and the signs differ.
- **close pairs**: sort, then two pointers. For each j, advance i while `a[j] - a[i] > k`, using `long long` for the difference (2·10⁹ overflows `int`).
- **pair mins**: sort ascending; element `a[i]` is the minimum of the pairs it forms with every later element: `Σ a[i] * (n - 1 - i)`.

## Solution
```cpp
#include <bits/stdc++.h>
using namespace std;

static string i128_to_string(__int128 v) {
    if (v == 0) return "0";
    bool neg = v < 0;
    unsigned __int128 u = neg ? -(unsigned __int128)v : (unsigned __int128)v;
    string s;
    while (u) { s += char('0' + int(u % 10)); u /= 10; }
    if (neg) s += '-';
    reverse(s.begin(), s.end());
    return s;
}

string dot_exact(const vector<long long>& a, const vector<long long>& b) {
    // value = hi * 10^18 + lo, with |lo| < 10^18 kept small so nothing overflows
    const __int128 BASE = (__int128)1000000000000000000LL;
    __int128 hi = 0, lo = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        __int128 p = (__int128)a[i] * b[i];          // |p| <= 10^36
        hi += p / BASE;                              // <= 10^18 per term: hi stays < 10^25
        lo += p % BASE;
        if (lo >= BASE || lo <= -BASE) { hi += lo / BASE; lo %= BASE; }
    }
    __int128 total_hi = hi + lo / BASE;
    lo %= BASE;
    if (total_hi > 0 && lo < 0) { total_hi -= 1; lo += BASE; }   // normalise signs
    if (total_hi < 0 && lo > 0) { total_hi += 1; lo -= BASE; }
    if (total_hi == 0) return i128_to_string(lo);
    string low = i128_to_string(lo < 0 ? -lo : lo);
    return i128_to_string(total_hi) + string(18 - low.size(), '0') + low;
}

long long floor_mean(const vector<long long>& a) {
    __int128 s = 0;
    for (auto x : a) s += x;
    __int128 n = (__int128)a.size();
    __int128 q = s / n;
    if (s % n != 0 && (s < 0)) q -= 1;              // truncation went toward zero: step down
    return (long long)q;
}

long long count_close_pairs(vector<int> a, long long k) {
    sort(a.begin(), a.end());
    long long cnt = 0;
    for (size_t i = 0, j = 0; j < a.size(); ++j) {
        while ((long long)a[j] - a[i] > k) ++i;
        cnt += (long long)(j - i);
    }
    return cnt;
}

long long sum_of_pair_mins(vector<int> a) {
    sort(a.begin(), a.end());
    long long n = a.size(), s = 0;
    for (long long i = 0; i < n; ++i) s += (long long)a[i] * (n - 1 - i);
    return s;
}
```

**Overflow is a design decision, not an accident.** Each function picks a representation wide enough for its worst case:
- **Exact dot product**: 2·10⁶ products of size 10³⁶ sum to about 10⁴², beyond even `__int128` (about 1.7·10³⁸). So the sum is kept as `hi·10¹⁸ + lo` with both parts bounded. The value is printed manually, because there's no standard `operator<<` for `__int128`.
- **floor_mean**: the sum of 10¹⁸-sized values needs 128 bits, and C++'s truncating division needs a correction for negative quotients to round toward −∞.
- **Pairs** use the sort-then-sweep pattern. Two pointers count the pairs within k in O(n), and in sorted order each element's contribution as a minimum is a closed form. Every difference and product is widened before it can overflow (`(long long)a[j] - a[i]`), since 10⁹ − (−10⁹) doesn't fit in `int`.
