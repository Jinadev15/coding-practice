---
id: cpp-kd-first-missing-positive
title: First Missing Positive in O(n) Time and O(1) Space
difficulty: Hard
order: 6
tags: cyclic sort, index as hash, in-place
time_limit: 2
---
## Statement
```cpp
int first_missing_positive(std::vector<int> a);   // smallest positive integer NOT present in a
```

`[1,2,0]` gives 3. `[3,4,−1,1]` gives 2. `[7,8,9,11,12]` gives 1.

The answer is always in `1..n+1`, where `n = a.size()`. **Why?** With only `n` values, at most `n` of the numbers `1..n` can be present. So values `≤ 0` or `> n` can be ignored, and the rest can be placed into slots `0..n−1` by cyclic sort. Then scan for the first slot `i` with `a[i] != i+1`.

You must use O(1) extra memory. Sorting is O(n log n), and a hash set is O(n) memory: neither is allowed here (and the judge's big tests are sized so that sorting is noticeably slower).

**Input:** cases until the end of input: `n` + values (n ≤ 2·10⁶).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int first_missing_positive(vector<int> a) {
    for (int v = 1; ; ++v)
        if (find(a.begin(), a.end(), v) == a.end()) return v;     // O(n^2)
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        cout << first_missing_positive(std::move(a)) << '\n';
    }
}
```

## Tests
=== sample
3
1 2 0
4
3 4 -1 1
5
7 8 9 11 12
---
3
2
1
=== hidden
1
1
1
2
3
1 1 1
5
2 3 4 5 6
4
-2147483648 0 2147483647 1
---
2
1
2
1
2
=== hidden
1
2
1
-1
2
-3 3
9
-3 1 11 5 3 -3 10 8 -2
10
8 11 2 8 6 4 0 9 6 2
10
2 3 -3 8 7 1 11 11 4 1
---
1
1
1
2
1
5
=== hidden
7
1 5 4 4 7 9 -2
8
10 -1 5 3 1 -2 -1 4
6
-2 7 -2 5 -1 0
7
-3 9 8 -1 3 -3 1
7
7 2 -3 4 3 6 9
8
9 9 1 5 8 5 10 -2
---
2
2
1
2
1
2
=== hidden
9
-3 3 6 8 7 4 -1 -1 -3
1
0
3
-3 -2 3
2
1 1
7
4 3 3 -2 5 4 9
5
6 -2 -1 5 6
---
1
1
1
2
1
1
=== hidden
@gen 1050973428 big
=== hidden
@gen 1050973429 big
=== hidden
@gen 1050973430 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(1, 10) if not big else 2000000
    if big:
        a = list(range(1, n + 1)); r.shuffle(a); a[r.randrange(n)] = -5
    else:
        a = [r.randint(-3, n + 2) for _ in range(n)]
    print(n); print(*a)
```

## Hints
- The answer is between 1 and n+1. Values outside 1..n can be ignored.
- Put each value v in 1..n at index v−1 by swapping. Don't swap when the target already holds v.
- After placing, the first index i with a[i] ≠ i+1 gives the answer. Otherwise it's n+1.

## Solution
**Pigeonhole bound.** Among `n` values, the numbers `1..n+1` can't all be present, so the answer is in that range. Only values in `1..n` matter, which is why they can be indexed directly.

**Cyclic placement.** Swap each in-range value into its home slot `v−1`. A value already at home (or with a copy already there) stays put, which prevents infinite loops on duplicates. Each swap fixes at least one value permanently, so there are O(n) swaps in total.

**Scan.** The first slot not holding its own number gives the answer. If every slot is correct, the array holds exactly `1..n`, and the answer is `n+1`.

Complexity: O(n) time, O(1) extra space (beyond the input copy).

```cpp
#include <bits/stdc++.h>
using namespace std;

int first_missing_positive(vector<int> a) {
    int n = a.size();
    for (int i = 0; i < n; ) {
        int v = a[i];
        if (v >= 1 && v <= n && a[v - 1] != v) swap(a[i], a[v - 1]);   // move v to slot v-1
        else ++i;                                                       // out of range, or already placed/duplicate
    }
    for (int i = 0; i < n; ++i) if (a[i] != i + 1) return i + 1;
    return n + 1;
}
```
