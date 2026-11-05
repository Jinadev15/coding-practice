---
id: cpp-next-permutation
title: Next and Previous Permutation
difficulty: Medium
order: 8
tags: arrays, permutations, in-place, lexicographic order
time_limit: 1
---
## Statement
Implement the lexicographic successor and predecessor of an arrangement, in place, **without** `std::next_permutation`:

```cpp
bool next_perm(std::vector<int>& a);   // rearrange into the next arrangement; if a is the LAST one,
                                       // turn it into the first (sorted ascending) and return false
bool prev_perm(std::vector<int>& a);   // the previous arrangement; if a is the FIRST one,
                                       // turn it into the last (sorted descending) and return false
```

Values may repeat: the next arrangement of `[1,1,2]` is `[1,2,1]`.

**Algorithm (next):**

1. Find the rightmost `i` with `a[i] < a[i+1]`.
2. Find the rightmost `j > i` with `a[j] > a[i]`, and swap them.
3. Reverse `a[i+1..]`.

`prev_perm` mirrors this with the comparisons flipped.

**Input:** cases until the end of input: `next k n` or `prev k n`, followed by `n` values. Apply the operation `k` times (k ≤ 1000, n ≤ 10⁵), and print the final array (the first 15 values when it is longer) plus how many of the k calls returned `false`.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

bool next_perm(vector<int>& a) { return false; }
bool prev_perm(vector<int>& a) { return false; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd; int k, n;
    while (cin >> cmd >> k >> n) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        int wraps = 0;
        for (int t = 0; t < k; ++t) wraps += !(cmd == "next" ? next_perm(a) : prev_perm(a));
        for (int i = 0; i < min(n, 15); ++i) cout << a[i] << ' ';
        cout << "| wraps " << wraps << '\n';
    }
}
```

## Tests
=== sample
next 1 3
1 2 3
next 1 3
3 2 1
prev 1 3
1 3 2
next 3 3
1 1 2
---
1 3 2 | wraps 0
1 2 3 | wraps 1
1 2 3 | wraps 0
1 1 2 | wraps 1
=== hidden
next 1 1
5
prev 1 1
5
next 6 3
1 2 3
prev 7 3
1 2 3
next 1000 8
1 2 3 4 5 6 7 8
---
5 | wraps 1
5 | wraps 1
1 2 3 | wraps 1
3 2 1 | wraps 2
1 3 5 4 7 8 2 6 | wraps 0
=== hidden
prev 13 5
3 1 3 1 2
next 23 2
2 2
prev 15 1
2
prev 21 5
3 1 3 3 1
next 26 2
3 3
prev 13 2
3 2
next 21 2
3 4
prev 8 2
4 4
---
1 3 2 3 1 | wraps 0
2 2 | wraps 23
2 | wraps 15
3 1 3 1 3 | wraps 2
3 3 | wraps 26
2 3 | wraps 6
4 3 | wraps 10
4 4 | wraps 8
=== hidden
prev 6 2
1 2
prev 5 1
2
prev 16 3
4 3 3
prev 9 3
4 4 4
prev 11 5
3 4 3 4 4
next 29 6
1 4 4 1 1 4
prev 6 2
3 3
next 6 5
2 2 4 2 1
---
1 2 | wraps 3
2 | wraps 5
3 4 3 | wraps 5
4 4 4 | wraps 9
3 3 4 4 4 | wraps 1
4 4 1 1 1 4 | wraps 1
3 3 | wraps 6
4 2 2 1 2 | wraps 0
=== hidden
next 24 6
4 4 3 2 2 3
prev 11 1
4
prev 29 4
2 3 1 4
next 16 3
4 1 4
prev 19 1
3
next 25 5
1 1 1 2 1
prev 15 6
3 2 2 4 4 1
prev 10 1
4
---
2 4 3 2 3 4 | wraps 1
4 | wraps 11
1 3 4 2 | wraps 1
4 4 1 | wraps 5
3 | wraps 19
1 1 1 2 1 | wraps 5
2 4 4 2 1 3 | wraps 0
4 | wraps 10
=== hidden
@gen 3018569539 big
=== hidden
@gen 3018569540 big
=== hidden
@gen 3018569541 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(8 if not big else 2):
    n = r.randint(1, 6) if not big else 100000
    k = r.randint(1, 30) if not big else 1000
    print(r.choice(["next", "prev"]), k, n)
    print(*[r.randint(1, 4 if not big else 10**9) for _ in range(n)])
```

## Hints
- Scan from the right for the first position `i` where `a[i] < a[i+1]`. If there's none, the array is the last arrangement.
- Swap `a[i]` with the rightmost element greater than it, then reverse everything after `i`.
- Use `>=`/`<=` in the scans so that equal values are handled correctly. `prev_perm` flips every comparison.

## Solution
Think of the array as a number written in digits. To get the *next larger* number, change as far to the **right** as possible:

1. The longest decreasing suffix is already the largest it can be, so the change must happen just before it, at `i`, the rightmost position with `a[i] < a[i+1]`.
2. Replace `a[i]` with the **smallest** suffix value that is larger than it. Scanning from the right, the first `a[j] > a[i]` is that value, because the suffix is decreasing.
3. The suffix is still decreasing after the swap. Reversing it gives the smallest possible tail.

Using `>=` and `<=` (instead of `>` and `<`) in the scans makes duplicates work: equal values never count as an ascent.

Each call is O(n). Over many calls, the amortised cost is O(1), because long suffixes rarely change. The step count of `k` calls is still bounded by O(k·n) here.

```cpp
#include <bits/stdc++.h>
using namespace std;

bool next_perm(vector<int>& a) {
    int n = a.size(), i = n - 2;
    while (i >= 0 && a[i] >= a[i + 1]) --i;          // rightmost ascent
    if (i < 0) { reverse(a.begin(), a.end()); return false; }   // last -> first
    int j = n - 1;
    while (a[j] <= a[i]) --j;                         // rightmost element bigger than a[i]
    swap(a[i], a[j]);
    reverse(a.begin() + i + 1, a.end());              // decreasing suffix -> increasing
    return true;
}

bool prev_perm(vector<int>& a) {
    int n = a.size(), i = n - 2;
    while (i >= 0 && a[i] <= a[i + 1]) --i;          // rightmost descent
    if (i < 0) { reverse(a.begin(), a.end()); return false; }   // first -> last
    int j = n - 1;
    while (a[j] >= a[i]) --j;                         // rightmost element smaller than a[i]
    swap(a[i], a[j]);
    reverse(a.begin() + i + 1, a.end());              // increasing suffix -> decreasing
    return true;
}
```
