---
id: cpp-bsa-multiplication-table
title: k-th Smallest in a Multiplication Table
difficulty: Hard
order: 4
tags: binary search on value, counting, k-th smallest
time_limit: 2
---
## Statement
The `n × m` multiplication table has entry `i·j` in row `i`, column `j` (1-based). Find the `k`-th smallest entry, counting duplicates.

```cpp
long long kth_in_table(long long n, long long m, long long k);   // n, m <= 3*10^5, 1 <= k <= n*m
```

The table has up to 9·10¹⁰ entries, so you can't build or sort it. **Binary search the value `v`.** The number of entries `≤ v` is

`count(v) = Σ_{i=1..n} min(m, ⌊v / i⌋)`

(row `i` holds `i, 2i, …, m·i`). The answer is the smallest `v` with `count(v) ≥ k`.

**Input:** cases until the end of input: `n m k` (up to 50 cases).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long kth_in_table(long long n, long long m, long long k) {
    vector<long long> all;
    for (long long i = 1; i <= n; ++i) for (long long j = 1; j <= m; ++j) all.push_back(i * j);
    nth_element(all.begin(), all.begin() + (k - 1), all.end());
    return all[k - 1];
}
```

## Driver
```cpp
int main() {
    long long n, m, k;
    while (cin >> n >> m >> k) cout << kth_in_table(n, m, k) << '\n';
}
```

## Tests
=== sample
3 3 5
2 3 6
---
3
6
=== hidden
1 1 1
1 300000 300000
300000 300000 1
300000 300000 90000000000
300000 300000 45000000000
---
1
300000
1
90000000000
16801553175
=== hidden
1 7 4
10 10 16
11 9 74
12 7 48
10 1 5
5 6 16
2 9 5
8 8 35
9 12 46
5 11 29
---
4
7
44
24
5
9
4
18
20
15
=== hidden
12 2 2
5 6 22
10 4 12
5 4 20
12 7 22
8 11 88
8 3 13
2 4 5
8 9 19
12 7 5
---
2
15
6
20
10
88
8
4
8
3
=== hidden
5 11 54
1 12 3
10 11 5
10 3 25
9 5 25
5 1 1
6 12 42
6 6 29
11 4 13
1 2 1
---
50
3
3
18
14
1
22
20
7
1
=== hidden
122384 271292 3454065587
283866 204410 21479504872
45829 54356 2394027256
280404 24842 5825570240
108098 244140 18859605488
45518 157519 4583010010
14883 56493 814687297
202391 103916 18519727741
254095 179697 21296746024
83425 155130 10156431496
65508 172742 6856732666
182608 69054 3632266593
266353 75253 19848964347
262425 17020 2913520270
163219 170378 3143156100
123391 145857 17958793950
253643 102822 7873156571
103007 42418 2378333872
81003 9826 513252061
149351 277932 28780781290
---
713706246
6847113000
1828921550
3382003759
9166432530
2023273728
640220706
11629503945
7638839280
5442050692
2906215376
1038925152
17314594740
1307401068
663837120
16831076580
2295189960
936159068
228196155
13604800700
=== hidden
53728 194742 10448728045
78096 130459 9043647083
299035 194350 40595177114
261214 208208 25459004835
182607 88169 50839861
93068 80159 4325743452
231556 199713 14241634769
107064 161023 13719726742
216976 25478 1080172522
192740 125413 11152473268
83520 95539 5673340438
81639 41342 28932297
63037 161948 8048626256
251181 27260 2280865630
156028 3730 359815087
203103 82175 14367805296
38683 147868 3971708857
219681 31088 691244900
69081 175788 3702076296
38217 58606 1694204402
---
9919658250
5757782710
19317947424
9150296896
5697770
1776593818
4186088452
7472947665
268381725
3976129080
2744299740
3711028
4335789004
693274968
154853289
8699915379
1879917500
141839244
1083621894
871631070
=== hidden
162571 63945 6974150547
135217 166089 11090313327
60378 100123 2643188492
104255 35530 2289810337
99843 27138 2001561838
55337 31643 1038258390
229864 174329 27618757621
45667 107781 4605713465
207948 113191 15204970577
26699 132462 633734757
190807 229122 10986586756
254737 299522 28733784827
81226 220009 2822996072
261673 231155 51651975602
8088 134433 911129583
105779 39390 3899030267
238311 150306 5439654620
20860 57544 366391252
146145 145289 16456527446
121196 13634 851246932
---
3203299832
4110427620
915341574
985116730
1004850565
433210784
12986181509
3266413626
6769142616
153100882
2981110968
9233965164
655766946
30896145786
530450815
2765527842
1248704730
107309858
8693361944
323650164

## Hints
- You can't list 9·10¹⁰ entries. Can you count how many are ≤ some value v?
- Row i holds i, 2i, …, m·i, so it contributes min(m, v / i) entries that are ≤ v.
- Binary search the smallest v with count(v) ≥ k, over [1, n·m].

## Solution
**Count instead of list.** Row `i` contains the multiples of `i` up to `i·m`, so the number of its entries `≤ v` is `min(m, ⌊v/i⌋)`. Summing over the rows takes O(n).

`count(v)` is non-decreasing in `v`, so "at least `k` entries are `≤ v`" is monotone, and the first such `v` is the k-th smallest.

**Why that `v` is a real entry:** `count(v−1) < k ≤ count(v)` means at least one entry equals `v`.

Complexity: O(n · log(n·m)), about 37 × 3·10⁵ operations per case.

```cpp
#include <bits/stdc++.h>
using namespace std;

static long long count_le(long long n, long long m, long long v) {
    long long c = 0;
    for (long long i = 1; i <= n; ++i) {
        long long t = v / i;
        if (t == 0) break;                    // rows below this have no entries <= v
        c += min(m, t);
    }
    return c;
}

long long kth_in_table(long long n, long long m, long long k) {
    long long lo = 1, hi = n * m;             // the largest entry is n*m
    while (lo < hi) {
        long long mid = lo + (hi - lo) / 2;
        if (count_le(n, m, mid) >= k) hi = mid; else lo = mid + 1;
    }
    return lo;
}
```
