---
id: cpp-maximum-gap
title: Maximum Gap in Linear Time
difficulty: Hard
order: 7
tags: sorting, bucket sort, pigeonhole principle, radix sort
time_limit: 1
---
## Statement
Given `n` integers in `[0, 10⁹]`, find the **largest difference between consecutive elements of the sorted order**, without sorting by comparisons.

```cpp
long long maximum_gap(const std::vector<int>& a);      // 0 if n < 2
```

Sorting is O(n log n). Do it in **O(n)** with the bucket idea:

- With minimum `lo` and maximum `hi`, the maximum gap is at least `⌈(hi − lo) / (n − 1)⌉`. That's the average gap, and the pigeonhole principle says some gap is at least that big.
- Make buckets of that width. Then **no gap inside a single bucket can be the answer**, so you only need each bucket's minimum and maximum, and the answer is the largest jump from one non-empty bucket's max to the next non-empty bucket's min.

You'll also implement **LSD radix sort** (base 256, 4 passes) as a second linear-time approach, and check that both agree:

```cpp
void radix_sort(std::vector<unsigned>& a);
```

**Input:** cases until the end of input: `n` + values, or `gen n seed mode`. The driver prints the gap and whether your radix sort sorted correctly.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long maximum_gap(const vector<int>& a) { return 0; }
void radix_sort(vector<unsigned>& a) {}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string first;
    while (cin >> first) {
        vector<int> a;
        if (first == "gen") {
            int n; unsigned seed; string mode; cin >> n >> seed >> mode;
            mt19937 rng(seed);
            a.resize(n);
            for (auto& x : a) x = mode == "wide" ? (int)(rng() % 1000000001u) : (int)(rng() % 1000u) * 1000000;
        } else {
            a.resize(stoi(first));
            for (auto& x : a) cin >> x;
        }
        vector<unsigned> u(a.begin(), a.end());
        radix_sort(u);
        bool ok = is_sorted(u.begin(), u.end()) && u.size() == a.size();
        long long s1 = 0, s2 = 0;
        for (int x : a) s1 += x;
        for (unsigned x : u) s2 += x;
        cout << maximum_gap(a) << (ok && s1 == s2 ? " radix-ok" : " radix-wrong") << '\n';
    }
}
```

## Tests
=== sample
4
3 6 9 1
1
10
---
3 radix-ok
0 radix-ok
=== hidden
2
0 1000000000
5
7 7 7 7 7
6
1 1 1 1 1 1000000000
---
1000000000 radix-ok
0 radix-ok
999999999 radix-ok
=== hidden
gen 1000000 3 wide
gen 1000000 4 clustered
---
15232 radix-ok
1000000 radix-ok
=== hidden
4
100 7 63 66
3
380421635 307687319 541476009
3
335559593 42599735 543738946
2
9 25
2
14 50
---
56 radix-ok
161054374 radix-ok
292959858 radix-ok
16 radix-ok
36 radix-ok
=== hidden
8
71 12 59 47 22 6 27 32
12
433181468 419442657 455554309 926413610 610712695 738889778 90532729 726160424 388334758 837005848 138538204 523968267
7
700604733 980862377 136995370 242404207 131356447 377540457 372889639
4
922391017 491501131 764379778 680446801
12
38 81 73 41 4 37 89 66 54 71 21 42
---
15 radix-ok
249796554 radix-ok
323064276 radix-ok
188945670 radix-ok
17 radix-ok
=== hidden
7
925182187 911198693 536147281 575799230 575912210 107129285 953550726
1
73791129
3
93 21 31
4
489487233 747036984 493529559 556287496
2
7 43
---
429017996 radix-ok
0 radix-ok
62 radix-ok
190749488 radix-ok
36 radix-ok
=== hidden
gen 1000000 453943 wide
---
14270 radix-ok
=== hidden
gen 1000000 987832 wide
---
14309 radix-ok
=== hidden
gen 1000000 866025 wide
---
16058 radix-ok

## Hints
- The maximum gap can't be smaller than `⌈(max − min)/(n − 1)⌉`. Why?
- Use buckets of that width. Two numbers in the same bucket can't form the answer, so store only each bucket's min and max.
- The answer is the largest `min(next non-empty bucket) − max(previous non-empty bucket)`. For radix sort, do 4 stable counting passes on 8-bit digits.

## Solution
**Why the buckets work.** There are `n − 1` gaps that add up to `hi − lo`, so the largest gap is at least the average, `⌈(hi−lo)/(n−1)⌉`. With buckets of exactly that width, two numbers in the same bucket differ by **less** than the width. So the answer always crosses from one bucket to a later one, and only the minimum and maximum of each bucket matter. That's one O(n) pass to fill the buckets, and one pass over the buckets.

**Radix sort.** A stable counting sort by each byte, least significant byte first. After pass `k`, the numbers are sorted by their lowest `k` bytes. Stability is what preserves that order through later passes. Four passes of O(n + 256) each sort any 32-bit unsigned values.

Both approaches avoid comparisons between elements entirely, which is how they get around the Ω(n log n) lower bound.

Complexity: O(n) time for both, O(n) extra space.

```cpp
#include <bits/stdc++.h>
using namespace std;

long long maximum_gap(const vector<int>& a) {
    int n = a.size();
    if (n < 2) return 0;
    auto [mn, mx] = minmax_element(a.begin(), a.end());
    long long lo = *mn, hi = *mx;
    if (lo == hi) return 0;
    long long width = max(1LL, (hi - lo + n - 2) / (n - 1));     // ceil((hi-lo)/(n-1))
    int buckets = (int)((hi - lo) / width) + 1;
    vector<long long> bmin(buckets, LLONG_MAX), bmax(buckets, LLONG_MIN);
    for (int x : a) {
        int b = (int)((x - lo) / width);
        bmin[b] = min(bmin[b], (long long)x);
        bmax[b] = max(bmax[b], (long long)x);
    }
    long long best = 0, prev = lo;                               // prev = max of the last non-empty bucket
    for (int b = 0; b < buckets; ++b) {
        if (bmin[b] == LLONG_MAX) continue;                      // empty bucket
        best = max(best, bmin[b] - prev);
        prev = bmax[b];
    }
    return best;
}

void radix_sort(vector<unsigned>& a) {
    vector<unsigned> tmp(a.size());
    for (int shift = 0; shift < 32; shift += 8) {                // least significant byte first
        array<size_t, 257> cnt{};
        for (unsigned x : a) ++cnt[((x >> shift) & 255) + 1];
        for (int i = 0; i < 256; ++i) cnt[i + 1] += cnt[i];      // prefix sums = start positions
        for (unsigned x : a) tmp[cnt[(x >> shift) & 255]++] = x; // stable placement
        a.swap(tmp);
    }
}
```
