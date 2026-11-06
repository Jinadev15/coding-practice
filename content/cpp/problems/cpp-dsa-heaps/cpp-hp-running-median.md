---
id: cpp-hp-running-median
title: Running Median with Two Heaps
difficulty: Medium
order: 5
tags: heap, two heaps, median, streaming
time_limit: 1
---
## Statement
```cpp
class MedianFinder {
public:
    void add(long long x);
    long long median_times_two() const;   // 2 × median of all values added so far (precondition: at least one)
};
```

The median of an odd count is the middle value; of an even count, the average of the two middle values. Returning **twice** the median keeps everything an integer; the driver prints it as a decimal (`7`, `-1.5`, …).

`add 5` → 5. `add 15` → 10. `add 1` → 5. `add 3` → 4.

Each `add` must be O(log n) and each query O(1).

**Input:** `q`, then `q` values (q ≤ 10⁶, |x| ≤ 10⁹). After each value, print the median.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class MedianFinder {
    vector<long long> v;                                   // kept sorted: O(n) insertion
public:
    void add(long long x) { v.insert(upper_bound(v.begin(), v.end(), x), x); }
    long long median_times_two() const {
        size_t n = v.size();
        return n % 2 ? 2 * v[n / 2] : v[n / 2 - 1] + v[n / 2];
    }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int q; cin >> q;
    MedianFinder mf;
    string out;
    while (q--) {
        long long x; cin >> x;
        mf.add(x);
        long long m2 = mf.median_times_two();
        if (m2 % 2 == 0) out += to_string(m2 / 2);
        else out += (m2 < 0 ? "-" : "") + to_string(llabs(m2) / 2) + ".5";
        out += '\n';
    }
    cout << out;
}
```

## Tests
=== sample
4
5
15
1
3
---
5
10
5
4
=== hidden
1
-7
4
-1
-2
-3
-4
5
1000000000
1000000000
-1000000000
-1000000000
0
6
2
2
2
1
3
2
---
-7
=== hidden
12
-5
-5
-4
-2
-3
3
4
-1
-1
4
2
-1
---
-5
-5
-5
-4.5
-4
-3.5
-3
-2.5
-2
-1.5
-1
-1
=== hidden
28
-4
0
2
-3
-5
3
2
1
-1
-3
2
2
3
-2
0
3
-4
1
-5
-1
1
1
-5
5
5
4
1
-1
---
-4
-2
0
-1.5
-3
-1.5
0
0.5
0
-0.5
0
0.5
1
0.5
0
0.5
0
0.5
0
0
0
0.5
0
0.5
1
1
1
1
=== hidden
16
2
0
-3
0
3
-5
0
-4
5
-1
1
2
-3
2
-2
1
---
2
1
0
0
0
0
0
0
0
0
0
0
0
0
0
0
=== hidden
@gen 3351119022 big
=== hidden
@gen 3351119023 big
=== hidden
@gen 3351119024 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
q = r.randint(1, 30) if not big else 1000000
print(q)
for _ in range(q): print(r.randint(-5, 5) if not big else r.randint(-10**9, 10**9))
```

## Hints
- Split the numbers into a smaller half and a larger half. Which element of each half do you need for the median?
- Smaller half in a max-heap, larger half in a min-heap. Keep their sizes equal or the smaller half one bigger.
- Insert by comparing with `lo.top()`, then move one top across if the sizes are off by more than allowed.

## Solution
Split the values into two halves:

- `lo`: the smaller half, in a **max**-heap (its top is the largest small value),
- `hi`: the larger half, in a **min**-heap (its top is the smallest large value).

Invariants: every element of `lo` ≤ every element of `hi`, and `|lo| = |hi|` or `|lo| = |hi| + 1`. Then the median is `lo.top()` (odd count) or the average of the two tops (even count).

**add(x):** put `x` into `lo` if it is ≤ `lo.top()`, else into `hi` (this keeps the order invariant). Then fix the sizes by moving one top across. Moving a top preserves the order invariant, because it is the boundary element.

| add | lo (max-heap) | hi (min-heap) | median |
|---|---|---|---|
| 5 | 5 | | 5 |
| 15 | 5 | 15 | 10 |
| 1 | 5 1 | 15 | 5 |
| 3 | 3 1 | 5 15 | 4 |

(After adding 3: lo = {5, 3, 1} is too big, so 5 moves to hi.)

Complexity: O(log n) per add, O(1) per query. The starter's sorted vector costs O(n) per insertion because of shifting.

```cpp
#include <bits/stdc++.h>
using namespace std;

class MedianFinder {
    priority_queue<long long> lo;                                         // smaller half, max on top
    priority_queue<long long, vector<long long>, greater<long long>> hi;  // larger half, min on top
public:
    void add(long long x) {
        if (lo.empty() || x <= lo.top()) lo.push(x); else hi.push(x);
        // rebalance so that lo has the same size as hi, or one more
        if (lo.size() > hi.size() + 1) { hi.push(lo.top()); lo.pop(); }
        else if (hi.size() > lo.size()) { lo.push(hi.top()); hi.pop(); }
    }
    long long median_times_two() const {
        return lo.size() > hi.size() ? 2 * lo.top() : lo.top() + hi.top();
    }
};
```
