---
id: cpp-heap-sort-trace
title: Heap Sort from Scratch
difficulty: Medium
order: 4
tags: sorting, heap sort, binary heap, sift down
time_limit: 2
---
## Statement
Implement heap sort with an explicit **max-heap** stored in the array itself (the children of index `i` are `2i+1` and `2i+2`):

```cpp
void sift_down(std::vector<int>& a, int i, int n);      // restore the heap property below i, heap = a[0..n)
void build_heap(std::vector<int>& a);                   // bottom-up: sift_down for i = n/2-1 down to 0
void heap_sort(std::vector<int>& a, std::vector<std::string>& trace);
```

Follow these rules, because the trace depends on them:

- `sift_down`: compare node `i` with its children. When both children are larger than the node, use the **larger** child, and on a tie prefer the **left** one. Swap the node with that child and continue from there. Stop when no child is larger.
- `heap_sort`: call `build_heap` and record `"heap: ..."`. Then, for `end = n−1` down to `1`, swap `a[0]` with `a[end]`, call `sift_down(a, 0, end)`, and record the whole array. Record trace lines only when n ≤ 10.

**Input:** cases until the end of input: `n` followed by `n` integers (n ≤ 10⁶). Print the trace, then `sorted`/`NOT sorted` and a checksum.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

void sift_down(vector<int>& a, int i, int n) {}
void build_heap(vector<int>& a) {}
void heap_sort(vector<int>& a, vector<string>& trace) { sort(a.begin(), a.end()); }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        vector<string> tr;
        heap_sort(a, tr);
        for (auto& t : tr) cout << t << '\n';
        long long h = 0;
        for (int i = 0; i < n; ++i) h = (h * 31 + a[i] + 1000000000LL) % 1000000007;
        cout << (is_sorted(a.begin(), a.end()) ? "sorted " : "NOT sorted ") << h << '\n';
    }
}
```

## Tests
=== sample
6
4 10 3 5 1 8
---
heap: 10 5 8 4 1 3
8 5 3 4 1 10
5 4 3 1 8 10
4 1 3 5 8 10
3 1 4 5 8 10
1 3 4 5 8 10
sorted 824439756
=== hidden
1
3
2
1 2
5
7 7 7 7 7
7
1 2 3 4 5 6 7
---
heap: 3
sorted 1000000003
heap: 2 1
1 2
sorted 999999816
heap: 7 7 7 7 7
7 7 7 7 7
7 7 7 7 7
7 7 7 7 7
7 7 7 7 7
sorted 0
heap: 7 5 6 4 2 1 3
6 5 3 4 2 1 7
5 4 3 1 2 6 7
4 2 3 1 5 6 7
3 2 1 4 5 6 7
2 1 3 4 5 6 7
1 2 3 4 5 6 7
sorted 528046791
=== hidden
6
9 2 6 6 8 2
3
8 8 9
8
7 8 5 4 1 1 5 2
3
6 1 6
---
heap: 9 8 6 6 2 2
8 6 6 2 2 9
6 2 6 2 8 9
6 2 2 6 8 9
2 2 6 6 8 9
2 2 6 6 8 9
sorted 852205928
heap: 9 8 8
8 8 9
8 8 9
sorted 994
heap: 8 7 5 4 1 1 5 2
7 4 5 2 1 1 5 8
5 4 5 2 1 1 7 8
5 4 1 2 1 5 7 8
4 2 1 1 5 5 7 8
2 1 1 4 5 5 7 8
1 1 2 4 5 5 7 8
1 1 2 4 5 5 7 8
sorted 453316624
heap: 6 1 6
6 1 6
1 6 6
sorted 999994209
=== hidden
5
6 7 8 1 9
4
4 4 3 2
4
3 4 7 2
2
9 1
---
heap: 9 7 8 1 6
8 7 6 1 9
7 1 6 8 9
6 1 7 8 9
1 6 7 8 9
sorted 994429123
heap: 4 4 3 2
4 2 3 4
3 2 4 4
2 3 4 4
sorted 999847112
heap: 7 4 3 2
4 2 3 7
3 2 4 7
2 3 4 7
sorted 999847115
heap: 9 1
1 9
sorted 999999823
=== hidden
5
3 6 3 6 4
10
1 2 6 8 7 9 7 5 4 8
9
9 4 2 5 4 6 7 5 4
8
8 2 2 2 1 7 8 3
---
heap: 6 6 3 3 4
6 4 3 3 6
4 3 3 6 6
3 3 4 6 6
3 3 4 6 6
sorted 996183844
heap: 9 8 7 5 8 6 1 2 4 7
8 8 7 5 7 6 1 2 4 9
8 7 7 5 4 6 1 2 8 9
7 5 7 2 4 6 1 8 8 9
7 5 6 2 4 1 7 8 8 9
6 5 1 2 4 7 7 8 8 9
5 4 1 2 6 7 7 8 8 9
4 2 1 5 6 7 7 8 8 9
2 1 4 5 6 7 7 8 8 9
1 2 4 5 6 7 7 8 8 9
sorted 471511826
heap: 9 5 7 5 4 6 2 4 4
7 5 6 5 4 4 2 4 9
6 5 4 5 4 4 2 7 9
5 5 4 2 4 4 6 7 9
5 4 4 2 4 5 6 7 9
4 4 4 2 5 5 6 7 9
4 2 4 4 5 5 6 7 9
4 2 4 4 5 5 6 7 9
2 4 4 4 5 5 6 7 9
sorted 256694833
heap: 8 3 8 2 1 7 2 2
8 3 7 2 1 2 2 8
7 3 2 2 1 2 8 8
3 2 2 2 1 7 8 8
2 2 2 1 3 7 8 8
2 1 2 2 3 7 8 8
2 1 2 2 3 7 8 8
1 2 2 2 3 7 8 8
sorted 338915627
=== hidden
@gen 3636579858 big
=== hidden
@gen 3636579859 big
=== hidden
@gen 3636579860 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
if sys.argv[2] == "small":
    for _ in range(4):
        n = r.randint(0, 10); print(n); print(*[r.randint(1, 9) for _ in range(n)])
else:
    n = 1000000; print(n); print(" ".join(str(r.randint(-10**9, 10**9)) for _ in range(n)))
```

## Hints
- In `sift_down`, pick the larger child (the left one wins ties). If it is bigger than `a[i]`, swap and continue from that child.
- Build the heap by calling `sift_down` for `i` from `n/2 − 1` down to 0.
- Extraction: swap `a[0]` with `a[end]`, then sift down within the heap of size `end` (not `n`).

## Solution
**The heap property** (every parent ≥ its children) means `a[0]` is always the maximum of the heap region.

**Building bottom-up.** Positions `n/2 … n−1` are leaves, which are trivially heaps. Calling `sift_down` from `n/2 − 1` back to 0 makes each subtree a heap once both of its children's subtrees already are. The total work is O(n): a node of height h does at most h swaps, and most nodes have small height.

**Sorting.** Swap the maximum into the last slot of the heap region. That slot is now final, so shrink the region and repair the root with `sift_down`. Each repair is O(log n).

Heap sort is in place and guaranteed O(n log n), but it isn't stable, and its jumps around memory make it slower than quicksort in practice.

Complexity: O(n) build plus O(n log n) extraction, O(1) extra space.

```cpp
#include <bits/stdc++.h>
using namespace std;

void sift_down(vector<int>& a, int i, int n) {
    while (true) {
        int big = i, l = 2 * i + 1, r = 2 * i + 2;
        if (l < n && a[l] > a[big]) big = l;
        if (r < n && a[r] > a[big]) big = r;          // strictly larger: ties keep the left child
        if (big == i) return;
        swap(a[i], a[big]);
        i = big;
    }
}

void build_heap(vector<int>& a) {
    int n = a.size();
    for (int i = n / 2 - 1; i >= 0; --i) sift_down(a, i, n);   // leaves are already heaps
}

static string show(const vector<int>& a, const string& prefix) {
    string s = prefix;
    for (size_t i = 0; i < a.size(); ++i) s += (i || !prefix.empty() ? " " : "") + to_string(a[i]);
    return s;
}

void heap_sort(vector<int>& a, vector<string>& trace) {
    int n = a.size();
    build_heap(a);
    if (n <= 10) trace.push_back(show(a, "heap:"));
    for (int end = n - 1; end > 0; --end) {
        swap(a[0], a[end]);              // current max goes to its final place
        sift_down(a, 0, end);            // heap shrinks to a[0..end)
        if (n <= 10) trace.push_back(show(a, ""));
    }
}
```
