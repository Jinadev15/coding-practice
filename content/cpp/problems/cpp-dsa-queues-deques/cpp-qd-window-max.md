---
id: cpp-qd-window-max
title: Sliding Window Maximum with a Monotonic Deque
difficulty: Medium
order: 5
tags: deque, monotonic deque, sliding window
time_limit: 2
---
## Statement
```cpp
std::vector<int> window_max(const std::vector<int>& a, int k);   // max of a[i..i+k-1] for i = 0 .. n-k
```

`a = [1, 3, -1, -3, 5, 3, 6, 7]`, `k = 3` → `[3, 3, 5, 5, 6, 7]`.

A heap gives O(n log n). Do it in **O(n)** with a deque of indices.

**Input:** cases until the end of input: `n k`, then `n` values (1 ≤ k ≤ n ≤ 10⁶ in total, |a[i]| ≤ 10⁹). Print the n − k + 1 maximums on one line.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> window_max(const vector<int>& a, int k) {
    vector<int> res;
    for (int i = 0; i + k <= (int)a.size(); ++i)                 // O(n*k)
        res.push_back(*max_element(a.begin() + i, a.begin() + i + k));
    return res;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, k;
    while (cin >> n >> k) {
        vector<int> a(n); for (auto& x : a) cin >> x;
        auto r = window_max(a, k);
        string out;
        for (size_t i = 0; i < r.size(); ++i) { if (i) out += ' '; out += to_string(r[i]); }
        cout << out << '\n';
    }
}
```

## Tests
=== sample
8 3
1 3 -1 -3 5 3 6 7
5 1
4 2 12 3 1
---
3 3 5 5 6 7
4 2 12 3 1
=== hidden
1 1
-7
4 4
2 9 9 1
6 2
5 5 5 5 5 5
6 3
6 5 4 3 2 1
6 3
1 2 3 4 5 6
---
-7
9
5 5 5 5 5
6 5 4 3
3 4 5 6
=== hidden
2 2
-2 -3
3 2
-3 -1 -3
1 1
-3
5 1
1 3 2 1 -3
6 4
-2 -3 -2 -2 -3 0
5 1
-2 1 1 0 -2
5 4
-2 1 -1 1 -3
4 2
0 -1 -1 0
---
-2
-1 -1
-3
1 3 2 1 -3
-2 -2 0
-2 1 1 0 -2
1 1
0 -1 0
=== hidden
3 3
3 3 0
7 7
3 -2 1 -3 -1 1 3
8 2
-1 1 -3 3 3 -3 -3 -1
7 6
-3 -3 3 3 3 1 0
3 3
1 -1 -3
3 3
0 -3 3
6 1
0 1 -1 -1 1 3
8 5
1 -1 -2 -2 0 -1 1 -2
---
3
3
1 1 3 3 3 -3 -1
3 3
1
3
0 1 -1 -1 1 3
1 0 1 1
=== hidden
3 3
-2 -2 2
6 3
3 3 2 -1 -1 1
5 4
0 1 2 3 -1
7 5
2 -1 1 -1 3 1 -2
9 9
-3 1 -2 3 -2 1 3 -1 0
1 1
1
5 4
1 1 1 -3 -3
6 1
0 2 2 2 -2 0
---
2
3 3 2 1
3 3
3 3 3
3
1
1 1
0 2 2 2 -2 0
=== hidden
@gen 571877234 big
=== hidden
@gen 571877235 big
=== hidden
@gen 571877236 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(8 if not big else 1):
    n = r.randint(1, 10) if not big else 1000000
    k = r.randint(1, n) if not big else r.choice([300000, 500000])
    if big and r.random() < 0.5: a = sorted((r.randint(-10**9, 10**9) for _ in range(n)), reverse=True)
    else: a = [r.randint(-3, 3) if not big else r.randint(-10**9, 10**9) for _ in range(n)]
    print(n, k); print(*a)
```

## Hints
- If `a[j] ≥ a[i]` with `j > i`, can `a[i]` ever be the maximum of a window that contains `j`?
- Keep candidate indices in a deque with decreasing values; drop dominated ones from the back before pushing.
- The front is the window maximum. Remove it when its index is `≤ i − k`.

## Solution
An element that has a **larger (or equal) element after it** inside the window can never be the maximum of any later window: the larger one stays at least as long. So such elements can be thrown away.

Keep a deque of indices whose values are **strictly decreasing** from front to back:

- **Back:** before pushing `i`, pop every index whose value is `≤ a[i]` (dominated forever).
- **Front:** the front is the maximum of the window; pop it when it leaves (`front ≤ i − k`).

| i | a[i] | pop back | pop front | deque (values) | output |
|---|---|---|---|---|---|
| 0 | 1 | | | 1 | |
| 1 | 3 | 1 | | 3 | |
| 2 | −1 | | | 3 −1 | 3 |
| 3 | −3 | | | 3 −1 −3 | 3 |
| 4 | 5 | −3 −1 | 3 (index 1) | 5 | 5 |
| 5 | 3 | | | 5 3 | 5 |
| 6 | 6 | 3 5 | | 6 | 6 |
| 7 | 7 | 6 | | 7 | 7 |

This is a monotonic stack (the back) combined with expiry (the front), which is why it needs a **deque**. Each index is pushed and popped once: O(n).

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> window_max(const vector<int>& a, int k) {
    deque<int> dq;                       // indices in the window, values strictly decreasing front to back
    vector<int> res;
    res.reserve(a.size() - k + 1);
    for (int i = 0; i < (int)a.size(); ++i) {
        if (!dq.empty() && dq.front() <= i - k) dq.pop_front();          // fell out of the window
        while (!dq.empty() && a[dq.back()] <= a[i]) dq.pop_back();       // can never be a max again
        dq.push_back(i);
        if (i >= k - 1) res.push_back(a[dq.front()]);
    }
    return res;
}
```
