---
id: cpp-divisor-queries
title: A Million Divisor Queries
difficulty: Medium
order: 6
tags: complexity, precomputation, sieve, harmonic series
time_limit: 1
---
## Statement
Answer up to 3·10⁶ queries "how many divisors does `x` have?", with `1 ≤ x ≤ 10⁶`.

```cpp
void prepare(int maxv);         // called once before any query, with maxv = 10^6
int divisors(int x);            // number of positive divisors of x
```

Trial division up to `√x` costs about 1000 steps per query. Over 3·10⁶ queries that is 3·10⁹ steps: too slow. Instead, **precompute** the answer for every number once, then answer each query in O(1).

The harmonic pattern from the lesson does the precomputation: for every `d`, add 1 to each multiple of `d`. That costs `n/1 + n/2 + … ≈ n ln n` steps.

**Input:** cases until the end of input.

- `q x₁ … x_q`: print each answer on its own line.
- `gen q seed`: the driver makes `q` random queries and prints the sum of their answers, plus the largest single answer.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

void prepare(int maxv) {}

int divisors(int x) {
    int c = 0;
    for (int d = 1; (long long)d * d <= x; ++d)
        if (x % d == 0) c += (d * d == x) ? 1 : 2;
    return c;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    prepare(1000000);
    string first;
    while (cin >> first) {
        if (first == "gen") {
            int q; unsigned seed; cin >> q >> seed;
            mt19937 rng(seed);
            long long sum = 0; int best = 0;
            for (int i = 0; i < q; ++i) {
                int d = divisors((int)(rng() % 1000000) + 1);
                sum += d; best = max(best, d);
            }
            cout << "sum=" << sum << " max=" << best << '\n';
        } else {
            int q = stoi(first);
            while (q--) { int x; cin >> x; cout << divisors(x) << '\n'; }
        }
    }
}
```

## Tests
=== sample
6 1 2 12 36 97 720720
---
1
2
6
9
2
240
=== hidden
gen 3000000 1
---
sum=41892440 max=240
=== hidden
gen 3000000 2025
---
sum=41872240 max=240
=== hidden
5 1000000 999983 524288 1 831600
---
49
2
20
1
240
=== hidden
30 65 413 399 1225 506 1604 340 596 482 766 319 284 158 309 1193 565 214 1246 745 1536 1878 1292 666 1303 1301 670 241 434 590 1970
---
4
4
8
9
8
6
12
6
4
4
4
6
4
4
2
4
4
8
4
20
8
12
12
2
2
8
2
8
8
8
=== hidden
30 1270 1769 1026 1062 1546 1161 1413 1563 1278 682 769 1099 868 1936 105 186 782 1465 997 1825 255 849 1117 403 1194 355 1232 862 767 1637
---
8
4
16
12
4
8
6
4
12
8
2
4
12
15
8
8
8
4
2
6
8
4
2
4
8
4
20
4
4
2
=== hidden
30 1670 1173 1944 363 1344 421 645 1256 313 1624 1937 940 1767 136 306 1386 4 193 534 1215 782 1319 758 1832 1366 1305 1545 3 1241 552
---
8
8
24
6
28
2
8
8
2
16
4
12
8
8
12
24
3
2
8
12
8
2
4
8
4
12
8
2
4
16
=== hidden
gen 3000000 357809037
---
sum=41903441 max=240
=== hidden
gen 3000000 517807031
---
sum=42016247 max=240
=== hidden
gen 3000000 493183097
---
sum=41897778 max=240

## Hints
- 10⁶ queries × 1000 steps is 10⁹. Move the work out of the queries.
- For every `d` from 1 to 10⁶, loop over the multiples of `d` and add 1 to each one's count.
- That double loop is O(n log n) thanks to the harmonic series. Store the counts in a global vector.

## Solution
Precompute once and answer cheaply. That is the whole lesson of this problem: **when the queries outnumber the possible inputs, compute the answer for every input in advance.**

The double loop visits each `(d, multiple of d)` pair once. That totals `Σ n/d ≈ n ln n ≈ 1.4·10⁷` steps for n = 10⁶, and each query is then a single array lookup.

A faster O(n) alternative uses a linear sieve with the multiplicative formula `d(p^a · m) = (a+1) · d(m)`. You'll meet it in the number theory topic.

Complexity: O(n log n) preparation, O(1) per query, O(n) memory.

```cpp
#include <bits/stdc++.h>
using namespace std;

static vector<int> cnt;

void prepare(int maxv) {
    cnt.assign(maxv + 1, 0);
    for (int d = 1; d <= maxv; ++d)            // n/1 + n/2 + ... + n/n = O(n log n)
        for (int m = d; m <= maxv; m += d) ++cnt[m];
}

int divisors(int x) { return cnt[x]; }
```
