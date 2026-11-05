---
id: cpp-hs-first-unique-stream
title: First Unique Element of a Stream
difficulty: Medium
order: 5
tags: hashing, queues, streams, counting
time_limit: 2
---
## Statement
Numbers arrive one at a time. After each arrival, report the **first** (earliest-arrived) value that has appeared **exactly once** so far, or −1 if there is none.

```cpp
class FirstUnique {
public:
    void add(int x);
    int first_unique();      // amortised O(1)
};
```

Example stream `2 3 5 2 3 5 7` gives `2 2 2 3 5 -1 7`.

Keep the counts in a hash map and a queue of candidates in arrival order. When asked, pop from the front while the front value's count is above 1. Those values can never become unique again, so discarding them is safe forever. Each value is pushed once and popped at most once, so the total work is O(n).

**Input:** cases until the end of input: `n`, followed by n values (n ≤ 10⁶). Print the answers (the first 30 of them, plus a checksum of all of them).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class FirstUnique {
    vector<int> seen;
public:
    void add(int x) { seen.push_back(x); }
    int first_unique() {
        for (int x : seen) if (count(seen.begin(), seen.end(), x) == 1) return x;   // O(n^2) per call
        return -1;
    }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        FirstUnique fu;
        long long h = 0;
        vector<int> shown;
        for (int i = 0; i < n; ++i) {
            int x; cin >> x;
            fu.add(x);
            int u = fu.first_unique();
            if (i < 30) shown.push_back(u);
            h = (h * 1000003 + u + 2) % 998244353;
        }
        for (int u : shown) cout << u << ' ';
        cout << "| " << h << '\n';
    }
}
```

## Tests
=== sample
7
2 3 5 2 3 5 7
---
2 2 2 3 5 -1 7 | 949200211
=== hidden
1
4
4
1 1 1 1
5
1 2 1 3 2
---
4 | 6
1 -1 -1 -1 | 483866785
1 1 2 2 3 | 674502025
=== hidden
11
6 4 5 1 2 1 2 3 3 2 2
9
4 6 2 6 1 4 2 1 5
6
2 3 5 2 3 2
6
2 1 2 1 4 1
---
6 6 6 6 6 6 6 6 6 6 6 | 437854234
4 4 4 4 4 2 1 -1 5 | 458403973
2 2 2 3 5 5 | 410301113
2 2 1 -1 4 4 | 776683620
=== hidden
4
4 6 3 6
6
2 4 4 1 5 3
8
4 5 1 5 6 6 2 2
13
5 3 6 4 2 3 2 2 6 1 4 5 4
---
4 4 4 4 | 32366798
2 2 2 2 2 2 | 642142798
4 4 4 4 4 4 4 4 | 589942579
5 5 5 5 5 5 5 5 5 5 5 1 1 | 457063764
=== hidden
2
5 2
8
6 4 4 5 1 5 1 6
2
6 4
14
4 5 4 5 3 3 2 6 2 4 5 3 5 5
---
5 5 | 7000028
6 6 6 6 6 6 6 -1 | 121093863
6 6 | 8000032
4 4 5 -1 3 -1 2 2 6 6 6 6 6 6 | 51326255
=== hidden
@gen 1247634694 big
=== hidden
@gen 1247634695 big
=== hidden
@gen 1247634696 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 1):
    n = r.randint(1, 15) if not big else 1000000
    print(n); print(*[r.randint(1, 6) if not big else r.randint(1, 600000) for _ in range(n)])
```

## Hints
- Keep a count per value in a hash map.
- Keep a queue of values in the order they first arrived. Only the first arrival needs to be queued.
- When answering, pop values from the front whose count is above 1. Can they ever come back?

## Solution
**Lazy deletion.** Once a value appears twice, it can never be unique again (counts only grow). So it's safe to drop it from the candidate queue, but only when it reaches the front. Values behind it don't need checking yet.

The queue preserves the arrival order, so the front, after discarding the repeated values, is the earliest value that still has a count of 1.

**Amortised analysis:** each distinct value is pushed once (on its first arrival) and popped at most once, so all the `first_unique` calls together do O(n) pops.

(An alternative is a doubly linked list plus a map from value to list node, which erases eagerly in O(1). It's the same idea as an LRU cache.)

Complexity: amortised O(1) per operation, O(distinct) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

class FirstUnique {
    unordered_map<int, int> cnt;
    queue<int> q;                                   // values in arrival order, possibly stale
public:
    void add(int x) {
        if (++cnt[x] == 1) q.push(x);               // only the first arrival can ever be the answer
    }
    int first_unique() {
        while (!q.empty() && cnt[q.front()] > 1) q.pop();   // repeated: never unique again
        return q.empty() ? -1 : q.front();
    }
};
```
