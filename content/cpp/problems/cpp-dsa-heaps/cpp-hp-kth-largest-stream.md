---
id: cpp-hp-kth-largest-stream
title: K-th Largest in a Stream
difficulty: Easy
order: 2
tags: heap, priority queue, streaming, top-k
time_limit: 1
---
## Statement
```cpp
class KthLargest {
public:
    explicit KthLargest(int k);
    long long add(long long x);   // add x; return the k-th largest value added so far,
                                  // or LLONG_MIN if fewer than k values have been added
};
```

Duplicates count separately: after adding `5, 5, 3` the 2nd largest is 5.

Use O(k) memory and O(log k) per `add`.

**Input:** `k q`, then `q` values to add (1 ≤ k ≤ q ≤ 10⁶, |x| ≤ 10¹⁸). Print each answer on its own line (`none` for LLONG_MIN).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class KthLargest {
    int k;
    vector<long long> all;
public:
    explicit KthLargest(int k) : k(k) {}
    long long add(long long x) {
        all.push_back(x);
        if ((int)all.size() < k) return LLONG_MIN;
        vector<long long> c = all;                              // O(n log n) per call
        sort(c.rbegin(), c.rend());
        return c[k - 1];
    }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int k, q; cin >> k >> q;
    KthLargest kl(k);
    string out;
    while (q--) {
        long long x; cin >> x;
        long long r = kl.add(x);
        out += r == LLONG_MIN ? string("none") : to_string(r);
        out += '\n';
    }
    cout << out;
}
```

## Tests
=== sample
3 6
4
5
8
2
3
9
---
none
none
4
4
4
5
=== hidden
1 4
-5
-7
10
10
---
-5
-5
10
10
=== hidden
2 5
5
5
3
5
6
---
none
5
5
5
5
=== hidden
4 4
1000000000000000000
-1000000000000000000
0
0
---
none
none
none
-1000000000000000000
=== hidden
4 27
6
-5
-4
2
0
4
1
0
-3
5
-2
-3
6
-1
0
4
-6
3
6
4
-5
-4
-1
5
-2
5
3
---
none
none
none
-5
-4
0
1
1
1
2
2
2
4
4
4
4
4
4
5
5
5
5
5
5
5
5
5
=== hidden
7 11
-2
6
-2
5
3
-2
-3
-6
-2
-6
6
---
none
none
none
none
none
none
-3
-3
-2
-2
-2
=== hidden
4 4
-5
4
-6
-4
---
none
none
none
-6
=== hidden
@gen 3202385508 big
=== hidden
@gen 3202385509 big
=== hidden
@gen 3202385510 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
q = r.randint(1, 30) if not big else 1000000
k = r.randint(1, q) if not big else r.choice([1, 1000, 500000])
print(k, q)
for _ in range(q): print(r.randint(-6, 6) if not big else r.randint(-10**18, 10**18))
```

## Hints
- You only ever need the k largest values. Which one of them is the answer?
- Keep them in a min-heap of size k: the top is the k-th largest.
- When full, push a new value only if it beats the top (and pop the top). A value that loses can be discarded forever.

## Solution
Keep exactly the **k largest values seen so far** in a **min**-heap. Its top is the smallest of them, which is precisely the k-th largest overall.

When `x` arrives and the heap is full: if `x` is larger than the top, it belongs to the top k and the old top drops out (pop, push). Otherwise `x` is not among the k largest and can be forgotten forever: it will never re-enter, because values only get pushed out of the top k, never back in.

```text
k = 3: add 4 5 8 2 3 9
4      heap [4]            none
5      [4 5]               none
8      [4 5 8]             4
2      2 < 4: ignore       4
3      ignore              4
9      pop 4, push 9       [5 8 9] -> 5
```

The counter-intuitive part: the **k largest** use a **min**-heap, because the element you must compare against and evict is the smallest of them.

Complexity: O(log k) per add, O(k) memory. (`std::priority_queue` is a max-heap by default; `greater<>` makes it a min-heap.)

```cpp
#include <bits/stdc++.h>
using namespace std;

class KthLargest {
    int k;
    priority_queue<long long, vector<long long>, greater<long long>> mn;   // the k largest; top = smallest of them
public:
    explicit KthLargest(int k) : k(k) {}
    long long add(long long x) {
        if ((int)mn.size() < k) mn.push(x);
        else if (x > mn.top()) { mn.pop(); mn.push(x); }   // x displaces the weakest of the top k
        return (int)mn.size() < k ? LLONG_MIN : mn.top();
    }
};
```
