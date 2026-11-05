---
id: cpp-tp-two-sum-sorted
title: Pair Sums in a Sorted Array
difficulty: Easy
order: 2
tags: two pointers, sorted arrays, counting
time_limit: 2
---
## Statement
The array is sorted ascending (it may contain duplicates and negative numbers).

```cpp
std::pair<int,int> find_pair(const std::vector<int>& a, long long target);
    // 1-based positions (i < j) of a pair with a[i] + a[j] == target, or {-1,-1}.
    // If several pairs exist, return the one the converging-pointer scan finds first.
long long count_less(const std::vector<int>& a, long long target);
    // number of pairs i < j with a[i] + a[j] < target
```

For `count_less`, when `a[L] + a[R] < target`, then `a[L]` pairs with **every** index in `(L, R]`. That's `R − L` pairs at once, so move `L`. Otherwise move `R`.

**Input:** cases until the end of input: `find n target` or `less n target`, then `n` sorted values (n ≤ 10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

pair<int,int> find_pair(const vector<int>& a, long long target) {
    for (size_t i = 0; i < a.size(); ++i)
        for (size_t j = i + 1; j < a.size(); ++j)
            if ((long long)a[i] + a[j] == target) return {(int)i + 1, (int)j + 1};
    return {-1, -1};
}
long long count_less(const vector<int>& a, long long target) { return 0; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd; int n; long long t;
    while (cin >> cmd >> n >> t) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        if (cmd == "find") { auto [i, j] = find_pair(a, t); cout << i << ' ' << j << '\n'; }
        else cout << count_less(a, t) << '\n';
    }
}
```

## Tests
=== sample
find 5 13
1 3 5 8 9
find 4 100
1 2 3 4
less 5 7
1 2 3 4 5
---
3 4
-1 -1
6
=== hidden
find 1 2
1
less 1 5
1
less 4 0
-1 -1 1 1
find 6 0
-5 -2 0 0 2 5
---
-1 -1
0
1
1 6
=== hidden
less 8 0
-9 -9 -7 2 2 5 6 10
find 9 -17
-9 -5 -4 -3 -1 1 2 5 6
less 4 9
-4 -1 1 2
less 10 8
-6 -4 -1 3 4 5 6 6 8 10
less 3 -2
0 1 4
find 7 -7
-10 -9 -4 -3 8 9 9
---
15
-1 -1
6
24
0
3 4
=== hidden
find 3 -6
7 8 8
less 4 17
-8 -6 -6 0
find 1 13
1
less 1 -17
4
less 4 -15
-10 3 8 10
less 2 3
-4 10
---
-1 -1
6
-1 -1
0
0
0
=== hidden
find 5 10
1 2 5 10 10
less 4 16
-7 0 3 10
find 2 -6
4 9
less 10 0
-9 -7 -7 -4 -2 0 7 8 9 9
less 1 -14
7
less 2 2
-2 6
---
-1 -1
6
-1 -1
17
0
0
=== hidden
@gen 2271077237 big
=== hidden
@gen 2271077238 big
=== hidden
@gen 2271077239 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(1, 10) if not big else 1000000
    a = sorted(r.randint(-10, 10) if not big else r.randint(-10**9, 10**9) for _ in range(n))
    print(r.choice(["find", "less"]), n, r.randint(-20, 20) if not big else r.randint(-10**9, 10**9)); print(*a)
```

## Hints
- Start with `L = 0` and `R = n−1`. Compare the sum with the target and move the pointer that can't be part of any answer.
- For counting: if `a[L] + a[R] < target`, how many partners does `a[L]` have between `L+1` and `R`?
- Add `R − L` and advance `L`. Otherwise decrement `R`. Use `long long` for the count.

## Solution
**Find.** This is the elimination argument from the lesson. When the sum is too small, `a[L]` can't be in any pair (even `a[R]`, the largest remaining value, isn't enough), so drop it. When it's too big, drop `a[R]`. Every step discards one element, so it takes O(n) steps.

**Count.** If `a[L] + a[R] < target`, then because the array is sorted, `a[L] + a[k] < target` for **every** `k` in `L+1..R`. Count all `R − L` of those pairs at once, then move on from `L`. If the sum is too big, `a[R]` forms no valid pair with anything at or after `L`, so drop it.

Counting in batches instead of one pair at a time is what keeps it linear. The answer can reach about 5·10¹¹, so use `long long`.

Complexity: O(n) each.

```cpp
#include <bits/stdc++.h>
using namespace std;

pair<int,int> find_pair(const vector<int>& a, long long target) {
    int L = 0, R = (int)a.size() - 1;
    while (L < R) {
        long long s = (long long)a[L] + a[R];
        if (s == target) return {L + 1, R + 1};
        if (s < target) ++L;         // a[L] is too small even with the largest partner
        else --R;                    // a[R] is too big even with the smallest partner
    }
    return {-1, -1};
}

long long count_less(const vector<int>& a, long long target) {
    long long cnt = 0;
    int L = 0, R = (int)a.size() - 1;
    while (L < R) {
        if ((long long)a[L] + a[R] < target) { cnt += R - L; ++L; }   // a[L] works with all of L+1..R
        else --R;
    }
    return cnt;
}
```
