---
id: cpp-min-swaps-to-sort
title: Minimum Swaps to Sort
difficulty: Medium
order: 8
tags: sorting, cycle decomposition, permutations, index sorting
time_limit: 1
---
## Statement
What is the smallest number of swaps (of any two elements, not necessarily adjacent) that sorts an array of **distinct** integers in ascending order?

```cpp
long long min_swaps(const std::vector<int>& a);
long long min_adjacent_swaps(const std::vector<int>& a);   // swaps of NEIGHBOURS only, n <= 5000
```

For any-pair swaps, think of the array as a **permutation**: element `a[i]` belongs at the position `pos(i)` it has in sorted order. Follow `i → pos(i) → pos(pos(i)) → …` until you return to `i`. That's a **cycle**. A cycle of length `L` needs exactly `L − 1` swaps, so the answer is `n − (number of cycles)`.

For adjacent swaps, every swap fixes exactly one inversion (see insertion sort), so the answer is the number of inversions. An O(n²) count is fine here, since n ≤ 5000. You'll see the O(n log n) method in Divide and Conquer.

**Input:** cases until the end of input: `n` followed by `n` distinct integers (n ≤ 2·10⁵ for `min_swaps`; the adjacent count is printed only when n ≤ 5000, otherwise `-`).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long min_swaps(const vector<int>& a) {
    long long c = 0;
    vector<int> s = a; sort(s.begin(), s.end());
    for (size_t i = 0; i < a.size(); ++i) if (a[i] != s[i]) ++c;    // counts misplaced, not swaps
    return c;
}
long long min_adjacent_swaps(const vector<int>& a) { return 0; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        cout << min_swaps(a) << ' ';
        if (n <= 5000) cout << min_adjacent_swaps(a) << '\n'; else cout << "-\n";
    }
}
```

## Tests
=== sample
4
4 3 2 1
5
1 5 4 3 2
5
2 3 4 5 1
---
2 6
2 6
4 4
=== hidden
1
42
3
1 2 3
6
10 19 6 3 5 99
---
0 0
0 0
2 8
=== hidden
4
-6 -15 -4 13
1
14
1
-3
6
6 -12 1 13 -1 -7
---
1 1
0 0
0 0
5 9
=== hidden
6
-2 9 -15 -18 -20 -19
3
17 0 -16
4
-17 -8 9 -20
3
-1 -16 18
---
3 13
1 3
3 3
1 1
=== hidden
4
19 5 7 -13
1
-10
3
7 10 -15
3
-13 15 -7
---
1 5
0 0
2 2
1 1
=== hidden
@gen 2346844923 big
=== hidden
@gen 2346844924 big
=== hidden
@gen 2346844925 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
if sys.argv[2] == "small":
    for _ in range(4):
        n = r.randint(1, 7); v = r.sample(range(-20, 20), n); print(n); print(*v)
else:
    n = r.choice([5000, 200000]); v = r.sample(range(-10**9, 10**9), n); print(n); print(*v)
```

## Hints
- Sort the indices by value to learn where every element should go.
- Follow `i → idx[i] → …` with a `seen` array. Each cycle of length L needs L−1 swaps.
- Adjacent swaps: each one fixes exactly one inversion, so count the pairs `i < j` with `a[i] > a[j]`.

## Solution
**Sort the indices** by value: `idx[k]` is where the k-th smallest element currently sits. Position `k` needs the element from position `idx[k]`, and that defines a permutation.

Every permutation splits into disjoint **cycles**. One swap can place one element correctly and shorten its cycle by one. The last swap of a cycle places *two* elements at once. So a cycle of length `L` costs `L − 1` swaps, and the total is `Σ (L − 1) = n − #cycles`. No sequence of swaps does better, because each swap increases the number of cycles by at most one, and a sorted array has `n` cycles.

**Adjacent swaps** can only remove one inversion each, and bubble sort shows that `#inversions` swaps are enough. So the answer is exactly the inversion count.

Complexity: O(n log n) for `min_swaps`, O(n²) for the adjacent version (O(n log n) with merge sort later).

```cpp
#include <bits/stdc++.h>
using namespace std;

long long min_swaps(const vector<int>& a) {
    int n = a.size();
    vector<int> idx(n);
    iota(idx.begin(), idx.end(), 0);
    sort(idx.begin(), idx.end(), [&](int i, int j) { return a[i] < a[j]; });
    // idx[k] = original position of the k-th smallest element: position k must receive a[idx[k]]
    vector<bool> seen(n, false);
    long long cycles = 0;
    for (int i = 0; i < n; ++i) {
        if (seen[i]) continue;
        ++cycles;
        for (int j = i; !seen[j]; j = idx[j]) seen[j] = true;   // walk one cycle
    }
    return n - cycles;
}

long long min_adjacent_swaps(const vector<int>& a) {
    long long inv = 0;
    for (size_t i = 0; i < a.size(); ++i)
        for (size_t j = i + 1; j < a.size(); ++j)
            if (a[i] > a[j]) ++inv;
    return inv;
}
```
