---
id: cpp-tp-three-sum
title: 3Sum and 3Sum Closest
difficulty: Medium
order: 7
tags: two pointers, sorting, duplicates, k-sum
time_limit: 1
---
## Statement
```cpp
std::vector<std::array<int,3>> three_sum(std::vector<int> a, long long target);
    // all UNIQUE value-triplets {x <= y <= z} from distinct positions with x + y + z == target,
    // sorted lexicographically
long long three_sum_closest(std::vector<int> a, long long target);
    // the sum of three distinct positions closest to target; on a tie, the SMALLER sum
```

n ≤ 3000, so O(n²) is the target. Sort first, fix the first element `i`, and run converging pointers on `a[i+1..]`. Skip equal values of the fixed element, and skip equal neighbours after recording a triplet, so that each value-triplet appears once.

**Input:** cases until the end of input: `n target` + values (n ≥ 3). Print the number of triplets, the first 5 triplets, and the closest sum.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<array<int,3>> three_sum(vector<int> a, long long target) {
    set<array<int,3>> s;
    int n = a.size();
    for (int i = 0; i < n; ++i) for (int j = i + 1; j < n; ++j) for (int k = j + 1; k < n; ++k)
        if ((long long)a[i] + a[j] + a[k] == target) { array<int,3> t{a[i], a[j], a[k]}; sort(t.begin(), t.end()); s.insert(t); }
    return vector<array<int,3>>(s.begin(), s.end());
}
long long three_sum_closest(vector<int> a, long long target) { return 0; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; long long t;
    while (cin >> n >> t) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        auto v = three_sum(a, t);
        cout << v.size() << " triplets:";
        for (size_t i = 0; i < min<size_t>(v.size(), 5); ++i) cout << " (" << v[i][0] << ',' << v[i][1] << ',' << v[i][2] << ')';
        cout << " closest " << three_sum_closest(a, t) << '\n';
    }
}
```

## Tests
=== sample
6 0
-1 0 1 2 -1 -4
4 1
-1 2 1 -4
---
2 triplets: (-1,-1,2) (-1,0,1) closest 0
0 triplets: closest 2
=== hidden
3 0
0 0 0
5 0
0 0 0 0 0
3 100
1 2 3
6 6
1 1 2 2 3 3
5 -2
-1 -1 -1 1 1
---
1 triplets: (0,0,0) closest 0
1 triplets: (0,0,0) closest 0
0 triplets: closest 6
1 triplets: (1,2,3) closest 6
0 triplets: closest -3
=== hidden
8 5
1 1 -3 0 0 2 5 -1
6 0
1 3 -2 4 0 4
4 -6
2 5 2 -5
10 1
-5 2 -5 -2 1 -5 4 1 5 -1
10 3
-3 -5 -2 1 3 1 4 -4 -3 -5
7 4
-5 3 0 0 4 -5 -3
---
2 triplets: (-1,1,5) (0,0,5) closest 5
0 triplets: closest -1
0 triplets: closest -1
5 triplets: (-5,1,5) (-5,2,4) (-2,-1,4) (-2,1,2) (-1,1,1) closest 1
2 triplets: (-4,3,4) (-2,1,4) closest 3
2 triplets: (-3,3,4) (0,0,4) closest 4
=== hidden
9 6
-4 -4 0 -2 -4 -5 2 1 5
3 3
-5 -4 5
8 6
-1 -5 3 -4 4 -1 -3 4
10 3
-3 -4 -3 3 4 -2 -1 -1 -1 1
7 6
-1 -5 1 3 4 -1 -2
3 -1
-5 0 -2
---
1 triplets: (0,1,5) closest 6
0 triplets: closest -4
1 triplets: (-1,3,4) closest 6
3 triplets: (-4,3,4) (-2,1,4) (-1,1,3) closest 3
1 triplets: (-1,3,4) closest 6
0 triplets: closest -7
=== hidden
8 3
3 -1 0 1 -3 -3 -5 5
6 5
-2 -5 0 -4 5 1
7 -5
1 2 -4 4 2 1 2
9 6
4 -5 3 -3 -1 -2 -4 -3 3
4 2
-1 4 -3 -5
5 -1
1 -1 5 2 -2
---
3 triplets: (-5,3,5) (-3,1,5) (-1,1,3) closest 3
0 triplets: closest 4
0 triplets: closest -2
1 triplets: (-1,3,4) closest 6
0 triplets: closest 0
1 triplets: (-2,-1,2) closest -1
=== hidden
@gen 1989238413 big
=== hidden
@gen 1989238414 big
=== hidden
@gen 1989238415 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(3, 10) if not big else 3000
    a = [r.randint(-5, 5) if not big else r.randint(-100000, 100000) for _ in range(n)]
    print(n, r.randint(-6, 6)); print(*a)
```

## Hints
- Sort, then fix the first element and solve "pair with sum `target − a[i]`" with two pointers on the rest.
- To avoid duplicate triplets, skip a fixed value equal to the previous one, and after each hit skip all copies of `a[L]` and `a[R]`.
- For closest: update the best on every sum you see (ties go to the smaller sum), and move the pointer that brings the sum toward the target.

## Solution
**Reduce 3Sum to 2Sum.** After sorting, fix the smallest element `a[i]`. The other two must sum to `target − a[i]` within `a[i+1..]`, which is exactly the sorted pair problem. That's O(n) per `i`, so O(n²) overall.

**Uniqueness without a set.**

1. Skip `i` when `a[i] == a[i−1]`: the same first value would produce the same triplets.
2. After a hit, advance `L` past every copy of `a[L]` and `R` past every copy of `a[R]`.

The `i` loop runs in increasing order, and so do the `L` values, so the output comes out lexicographically sorted.

**Closest.** The same scan applies. Any sum may be the best, so check every one. Move toward the target, because moving away can only make things worse with the fixed `i`.

Complexity: O(n²) time, O(1) extra space (besides the output).

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<array<int,3>> three_sum(vector<int> a, long long target) {
    sort(a.begin(), a.end());
    int n = a.size();
    vector<array<int,3>> out;
    for (int i = 0; i + 2 < n; ++i) {
        if (i > 0 && a[i] == a[i - 1]) continue;            // same first value: same triplets again
        int L = i + 1, R = n - 1;
        while (L < R) {
            long long s = (long long)a[i] + a[L] + a[R];
            if (s < target) ++L;
            else if (s > target) --R;
            else {
                out.push_back({a[i], a[L], a[R]});
                while (L < R && a[L] == a[L + 1]) ++L;          // skip duplicates of the middle value
                while (L < R && a[R] == a[R - 1]) --R;          // and of the last value
                ++L; --R;
            }
        }
    }
    return out;                                                // already lexicographic
}

long long three_sum_closest(vector<int> a, long long target) {
    sort(a.begin(), a.end());
    int n = a.size();
    long long best = (long long)a[0] + a[1] + a[2];
    auto better = [&](long long s) {
        long long ds = llabs(s - target), db = llabs(best - target);
        return ds < db || (ds == db && s < best);
    };
    for (int i = 0; i + 2 < n; ++i) {
        int L = i + 1, R = n - 1;
        while (L < R) {
            long long s = (long long)a[i] + a[L] + a[R];
            if (better(s)) best = s;
            if (s < target) ++L;
            else if (s > target) --R;
            else return s;                                       // can't beat an exact hit
        }
    }
    return best;
}
```
