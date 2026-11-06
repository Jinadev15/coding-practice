---
id: cpp-hp-top-k-frequent
title: Top K Frequent Elements
difficulty: Medium
order: 3
tags: heap, hashing, top-k, custom comparator
time_limit: 1
---
## Statement
```cpp
std::vector<int> top_k_frequent(const std::vector<int>& a, int k);
```

Return the `k` values that occur most often in `a`, ordered by **frequency descending**, ties broken by **smaller value first**. `1 ≤ k ≤ number of distinct values`.

`a = [1, 1, 1, 2, 2, 3]`, `k = 2` → `[1, 2]`. `a = [4, 4, 7, 7, 5]`, `k = 2` → `[4, 7]` (both twice; 4 < 7).

Aim for O(n + d log k) with d distinct values, using a heap of size k and a **custom comparator**.

**Input:** cases until the end of input: `n k`, then `n` values (n ≤ 10⁶ in total, |a[i]| ≤ 10⁹).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> top_k_frequent(const vector<int>& a, int k) {
    return {};
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, k;
    while (cin >> n >> k) {
        vector<int> a(n); for (auto& x : a) cin >> x;
        auto r = top_k_frequent(a, k);
        string out;
        for (size_t i = 0; i < r.size(); ++i) { if (i) out += ' '; out += to_string(r[i]); }
        cout << out << '\n';
    }
}
```

## Tests
=== sample
6 2
1 1 1 2 2 3
5 2
4 4 7 7 5
---
1 2
4 7
=== hidden
1 1
-9
5 5
5 4 3 2 1
6 1
-1 -1 2 2 3 3
7 3
1000000000 -1000000000 7 7 1000000000 -1000000000 0
---
-9
1 2 3 4 5
-1
-1000000000 7 1000000000
=== hidden
8 1
1 -2 -2 0 -1 0 -1 0
7 6
5 -4 0 0 -1 3 6
2 2
6 0
4 2
0 -1 3 3
12 4
-1 -2 0 2 0 0 -1 -2 -1 -1 3 -1
3 1
5 -6 -3
10 6
1 2 3 4 -1 3 -2 -2 -6 -5
12 4
-2 0 -6 -1 2 -3 6 2 4 2 -3 -6
---
0
0 -4 -1 3 5 6
0 6
3 -1
-1 0 -2 2
-6
-2 3 -6 -5 -1 1
2 -6 -3 -2
=== hidden
2 1
-1 0
7 3
4 -4 5 -4 6 -4 -4
4 3
0 -4 5 1
5 3
6 -5 1 0 -4
12 1
-2 -2 1 -2 3 1 -1 -3 3 2 1 0
10 5
1 -4 -1 1 2 5 -2 -1 -5 -1
12 4
4 0 -1 4 -3 0 0 4 5 4 -1 -2
9 1
2 2 3 -1 3 3 -1 3 0
---
-1
-4 4 5
-4 0 1
-5 -4 0
-2
-1 1 -5 -4 -2
4 0 -1 -3
3
=== hidden
12 7
-6 0 -1 -3 -2 0 -5 -2 -5 5 -4 2
1 1
2
10 4
2 -4 3 6 5 4 2 1 -2 -3
7 4
-5 4 3 -2 1 1 5
11 6
-1 0 -1 1 0 -2 5 -3 6 1 3
3 1
3 3 -1
12 4
6 2 -5 3 6 -4 -2 -1 3 -5 -4 -4
9 7
3 -3 2 -2 0 1 -3 1 -1
---
-5 -2 0 -6 -4 -3 -1
2
2 -4 -3 -2
1 -5 -2 3
-1 0 1 -3 -2 3
3
-4 -5 3 6
-3 1 -2 -1 0 2 3
=== hidden
@gen 3358342344 big
=== hidden
@gen 3358342345 big
=== hidden
@gen 3358342346 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(8 if not big else 1):
    n = r.randint(1, 12) if not big else 1000000
    hi = r.choice([3, 6]) if not big else r.choice([1000, 10**9])
    a = [r.randint(-hi, hi) for _ in range(n)]
    d = len(set(a))
    k = r.randint(1, d) if not big else min(d, r.choice([10, 1000]))
    print(n, k); print(*a)
```

## Hints
- First count the occurrences of each value with a hash map.
- Keep the k best (count, value) pairs in a heap whose top is the worst of them, so you can evict it in O(log k).
- `priority_queue`'s comparator answers "does a have lower priority than b?". Pass "a is better than b" to keep the worst on top, and fill the result from the back.

## Solution
1. **Count** with a hash map: O(n).
2. **Select** the k best `(count, value)` pairs with a heap of size k whose top is the **worst** of the kept pairs. Push each pair; when the heap has k + 1 elements, pop the worst. O(d log k).
3. Popping the heap yields the kept pairs from worst to best, so fill the result **from the back**.

**The comparator.** `std::priority_queue<T, C, Cmp>` puts on top the element that is "largest" according to `Cmp`, where `Cmp(a, b)` means "a has lower priority than b". Passing `better` (a is better than b) as `Cmp` therefore makes the **worst** pair the top, exactly what eviction needs. This inversion confuses everyone at first; test it on a tiny example.

```text
counts: 1->3, 2->2, 3->1, k = 2
push (3,1)           heap {(3,1)}
push (2,2)           heap {(3,1),(2,2)}    top = worst = (2,2)
push (1,3) -> size 3: pop the worst (1,3)
pop order: (2,2), (3,1)  -> fill from the back: [1, 2]
```

Alternatives: sort all d pairs (O(d log d)), `nth_element` (O(d) average), or bucket sort by count (O(n)). The heap wins when k is small and the data arrives as a stream.

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> top_k_frequent(const vector<int>& a, int k) {
    unordered_map<int,int> cnt;
    cnt.reserve(a.size() * 2 + 1);
    for (int x : a) ++cnt[x];
    // "better" = higher count, then smaller value. The heap keeps the k best with the WORST on top.
    auto better = [](const pair<int,int>& x, const pair<int,int>& y) {     // (count, value)
        return x.first != y.first ? x.first > y.first : x.second < y.second;
    };
    priority_queue<pair<int,int>, vector<pair<int,int>>, decltype(better)> heap(better);
    for (auto [v, c] : cnt) {
        heap.push({c, v});
        if ((int)heap.size() > k) heap.pop();          // evict the worst of k + 1
    }
    vector<int> res(heap.size());
    for (int i = (int)res.size() - 1; i >= 0; --i) { res[i] = heap.top().second; heap.pop(); }   // worst comes out first
    return res;
}
```
