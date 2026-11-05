---
id: cpp-hs-nearby-almost-duplicate
title: Nearby Almost-Duplicates with Bucket Hashing
difficulty: Hard
order: 7
tags: hashing, buckets, sliding window
time_limit: 2
---
## Statement
```cpp
bool nearby_duplicate(const std::vector<int>& a, int k);
    // are there i != j with a[i] == a[j] and |i - j| <= k ?
bool nearby_almost_duplicate(const std::vector<int>& a, int k, long long t);
    // are there i != j with |a[i] - a[j]| <= t and |i - j| <= k ?   (t >= 0)
```

The first is a sliding window over a hash set holding the last `k` elements.

For the second, put each value into a **bucket of width `t + 1`**: bucket id = `floor(value / (t+1))`, using floor division even for negative values. Two values in the **same** bucket differ by at most `t`, so you're done immediately. Values in **neighbouring** buckets might qualify, so check them. Keep only the last `k` elements (one per bucket suffices, because a second element in the same bucket would already have triggered the answer).

That's O(n) expected, compared with O(n log k) for an ordered-set solution.

**Input:** cases until the end of input: `n k t` + n values (n ≤ 10⁶, |a[i]| ≤ 2³¹−1, 0 ≤ t ≤ 2³¹). Print both answers.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

bool nearby_duplicate(const vector<int>& a, int k) { return false; }
bool nearby_almost_duplicate(const vector<int>& a, int k, long long t) { return false; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, k; long long t;
    while (cin >> n >> k >> t) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        cout << (nearby_duplicate(a, k) ? "true" : "false") << ' ' << (nearby_almost_duplicate(a, k, t) ? "true" : "false") << '\n';
    }
}
```

## Tests
=== sample
4 3 0
1 2 3 1
6 2 3
1 5 9 1 5 9
4 1 2
-1 3 7 1
---
true true
false false
false false
=== hidden
1 1 0
5
2 0 5
1 1
2 1 0
-2147483648 2147483647
2 1 4294967295
-2147483648 2147483647
3 1 1
-1 1 -1
---
false false
false false
false false
false true
false false
=== hidden
5 0 0
-3 -7 -5 5 -1
9 4 3
0 -8 -1 -8 2 8 -2 4 2
6 3 2
4 -7 -2 1 8 -5
6 3 4
-7 -2 4 0 -8 -7
1 3 1
8
4 4 4
7 3 6 5
5 2 0
-3 3 -2 4 5
9 4 4
3 -6 -2 1 6 4 2 -1 -8
---
false false
true true
false false
false true
false false
false true
false false
false true
=== hidden
5 0 1
-3 6 -7 4 2
4 1 1
-1 1 2 -1
8 3 1
1 0 -1 -3 -4 -4 -6 -1
1 2 3
8
2 3 4
-4 5
3 3 4
-3 -8 4
8 2 2
4 -2 -1 5 -1 8 -5 -7
6 1 0
3 -6 -6 7 -7 -8
---
false false
false true
true true
false false
false false
false false
true true
true true
=== hidden
7 2 2
5 -7 -3 8 3 -8 -6
3 1 2
3 -6 1
9 2 1
-2 -1 7 -1 7 0 -4 4 6
8 4 0
6 8 -1 -8 1 6 7 5
10 0 3
6 1 7 6 -2 -4 -4 6 2 -5
3 4 3
-7 2 2
8 1 1
4 8 -8 -8 -2 2 -2 8
1 1 4
1
---
false true
false false
true true
false false
false false
true true
true true
false false
=== hidden
@gen 3138936640 big
=== hidden
@gen 3138936641 big
=== hidden
@gen 3138936642 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(8 if not big else 2):
    n = r.randint(1, 10) if not big else 1000000
    k = r.randint(0, 4) if not big else r.randint(1, 1000)
    t = r.randint(0, 4) if not big else r.randint(0, 3)
    print(n, k, t); print(*[r.randint(-8, 8) if not big else r.randint(-2**31, 2**31 - 1) for _ in range(n)])
```

## Hints
- The exact-duplicate version is a hash set holding the last k values.
- For "difference ≤ t", use buckets of width t+1: two values in the same bucket always qualify.
- Check the neighbouring buckets too, and use floor division so that negative values land in the right bucket.

## Solution
**Window + set.** A set of the last `k` values answers "does `a[i]` repeat within distance k?" Remove the element that falls out of the window before checking.

**Buckets of width `t+1`:**

- Two values in the same bucket differ by at most `t`, so there's an immediate hit.
- Values two or more buckets apart differ by more than `t`, so they never qualify.
- Only the two neighbouring buckets need an explicit comparison.

So each bucket ever holds **at most one** live value (a second one would have returned `true` already), and a map from bucket id to value suffices.

**Floor division** matters for negative values. With C++'s truncating `/`, −1 and 1 would land in the same bucket 0 for `w = 2`, even though they differ by 2. The helper rounds toward minus infinity. Values reach ±2³¹ and `t + 1` reaches 2³¹ + 1, so do all arithmetic in `long long`.

Complexity: O(n) expected time, O(k) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

bool nearby_duplicate(const vector<int>& a, int k) {
    unordered_set<int> win;
    for (int i = 0; i < (int)a.size(); ++i) {
        if (i > k) win.erase(a[i - k - 1]);          // keep only the last k elements
        if (!win.insert(a[i]).second) return true;   // already present => duplicate within k
    }
    return false;
}

static long long bucket_of(long long v, long long w) {   // floor division, correct for negatives
    return v >= 0 ? v / w : -((-v + w - 1) / w);
}

bool nearby_almost_duplicate(const vector<int>& a, int k, long long t) {
    if (k <= 0) return false;
    long long w = t + 1;
    unordered_map<long long, long long> bucket;          // bucket id -> the value stored there
    bucket.reserve(2 * (size_t)min<long long>(k, (long long)a.size()) + 2);
    for (int i = 0; i < (int)a.size(); ++i) {
        long long v = a[i], id = bucket_of(v, w);
        if (bucket.count(id)) return true;               // same bucket: difference < w
        auto near = [&](long long b) { auto it = bucket.find(b); return it != bucket.end() && llabs(it->second - v) <= t; };
        if (near(id - 1) || near(id + 1)) return true;
        bucket[id] = v;
        if (i >= k) bucket.erase(bucket_of(a[i - k], w));   // slide: drop the element k positions back
    }
    return false;
}
```
