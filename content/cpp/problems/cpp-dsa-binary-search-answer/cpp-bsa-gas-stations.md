---
id: cpp-bsa-gas-stations
title: Minimise the Maximum Gap by Adding Stations
difficulty: Hard
order: 7
tags: binary search on real numbers, greedy, minimax
time_limit: 2
compare: float
---
## Statement
Stations stand at sorted positions `x[0] < x[1] < … < x[n−1]` on a road. You may add `K` new stations anywhere, including at non-integer positions. Minimise the largest distance between adjacent stations, and return that distance.

```cpp
double min_max_gap(const std::vector<long long>& x, long long K);
```

Binary search the answer `D` (a real number):

- **Feasible(D):** each existing gap `g` needs `⌈g / D⌉ − 1` new stations to bring every piece down to at most `D`. Feasible if the total is `≤ K`.
- **Monotone:** a larger `D` never needs more stations.

(The integer variant of this problem has an exact answer, but here the positions of new stations are real, so the answer is real too.)

Be careful with `⌈g/D⌉` in floating point: compute `floor(g / D)` and subtract 1 when `g / D` is an exact integer. Simpler, robust version: `needed = (long long)(g / D)`, which counts the stations strictly inside the gap at spacing D.

Print with 6 decimals. Answers within 10⁻⁶ relative or absolute error are accepted.

**Input:** cases until the end of input: `n K` + n positions (n ≤ 10⁵, positions ≤ 10⁸, K ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

double min_max_gap(const vector<long long>& x, long long K) {
    // greedy: repeatedly split the currently largest piece in half -- not optimal
    priority_queue<double> pq;
    for (size_t i = 1; i < x.size(); ++i) pq.push(double(x[i] - x[i - 1]));
    while (K-- > 0 && !pq.empty()) { double g = pq.top(); pq.pop(); pq.push(g / 2); pq.push(g / 2); }
    return pq.empty() ? 0.0 : pq.top();
}
```

## Driver
```cpp
int main() {
    int n; long long K;
    while (cin >> n >> K) {
        vector<long long> x(n);
        for (auto& v : x) cin >> v;
        printf("%.6f\n", min_max_gap(x, K));
    }
}
```

## Tests
=== sample
10 9
1 2 3 4 5 6 7 8 9 10
2 2
0 10
---
0.500000
3.333333
=== hidden
1 5
7
2 0
0 100000000
3 1
0 1 100
4 3
0 7 13 100
---
0.000000
100000000.000000
49.500000
21.750000
=== hidden
3 8
15 21 22
5 2
3 5 9 11 32
2 4
11 23
1 4
37
1 8
4
---
0.750000
7.000000
2.400000
0.000000
0.000000
=== hidden
1 4
8
4 2
30 36 41 48
1 8
14
1 7
31
3 2
18 26 43
---
0.000000
5.000000
0.000000
0.000000
8.000000
=== hidden
3 4
1 28 38
4 1
5 25 29 49
6 0
3 9 10 16 26 43
1 0
42
6 7
8 9 11 14 19 47
---
6.750000
20.000000
17.000000
0.000000
4.000000
=== hidden
@gen 3236826072 big
=== hidden
@gen 3236826073 big
=== hidden
@gen 3236826074 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(5 if not big else 2):
    n = r.randint(1, 6) if not big else 100000
    xs = sorted(r.sample(range(0, 50 if not big else 10**8), n))
    print(n, r.randint(0, 8) if not big else r.randint(0, 10**6)); print(*xs)
```

## Hints
- Halving the biggest gap greedily is not optimal (think of 2 stations in a gap of 10).
- For a candidate maximum gap D, how many stations does a gap g need? Roughly ⌊g / D⌋.
- Binary search D over real numbers between 0 and the largest gap, for about 100 iterations.

## Solution
**Why greedy halving fails:** splitting the largest gap in half each time wastes stations. A gap of 10 with 2 stations is best split into thirds (3.33), not halves and then quarters (5, then 2.5 and 5).

**Binary search on the answer.** For a target maximum gap `D`, a gap `g` needs just enough stations that each of its pieces is `≤ D`. With `(long long)(g/D)` stations, the gap splits into `⌊g/D⌋ + 1` equal pieces of length `g / (⌊g/D⌋ + 1) < D`. At an exact multiple this slightly over-counts by one, but that only affects the check at the single boundary value, and floating-point convergence is unaffected. The total is monotone non-increasing in `D`.

The answer lies in `(0, max gap]`. One hundred real-valued halvings converge to double precision, and the float comparison accepts errors of 10⁻⁶.

Complexity: O(n · 100).

```cpp
#include <bits/stdc++.h>
using namespace std;

static bool feasible(const vector<long long>& x, long long K, double D) {
    long long needed = 0;
    for (size_t i = 1; i < x.size(); ++i) {
        double g = double(x[i] - x[i - 1]);
        needed += (long long)(g / D);            // stations inside the gap so every piece is <= D (count is safe)
        if (needed > K) return false;
    }
    return true;
}

double min_max_gap(const vector<long long>& x, long long K) {
    if (x.size() < 2) return 0.0;
    double lo = 0, hi = 0;
    for (size_t i = 1; i < x.size(); ++i) hi = max(hi, double(x[i] - x[i - 1]));
    for (int it = 0; it < 100; ++it) {           // ~1e8 range: 100 halvings reach machine precision
        double mid = (lo + hi) / 2;
        if (mid > 0 && feasible(x, K, mid)) hi = mid; else lo = mid;
    }
    return hi;
}
```
