---
id: cpp-ms-next-greater
title: Next Greater Element, Linear and Circular
difficulty: Easy
order: 1
tags: monotonic stack, next greater element, circular array
time_limit: 2
---
## Statement
```cpp
std::vector<int> next_greater_index(const std::vector<int>& a);
    // res[i] = the smallest j > i with a[j] > a[i], or -1
std::vector<int> next_greater_circular(const std::vector<int>& a);
    // the array is circular (after a[n-1] comes a[0]): res[i] = the VALUE of the first strictly
    // greater element met when walking forward from i (wrapping around at most once), or -1
```

`a = [2, 1, 2, 4, 3]`: indices `[3, 2, 3, -1, -1]`; circular values `[4, 2, 4, -1, 4]` (from the 3, wrap around to 2, 1, 2, then 4).

Both must run in **O(n)**.

**Input:** cases until the end of input: `n` + `n` values (n ≤ 10⁶ total, |a[i]| ≤ 10⁹). Print two lines per case: the indices, then the circular values.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> next_greater_index(const vector<int>& a) {
    int n = a.size(); vector<int> r(n, -1);
    for (int i = 0; i < n; ++i)
        for (int j = i + 1; j < n; ++j) if (a[j] > a[i]) { r[i] = j; break; }   // O(n^2) on decreasing input
    return r;
}
vector<int> next_greater_circular(const vector<int>& a) {
    return vector<int>(a.size(), -1);
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<int> a(n); for (auto& x : a) cin >> x;
        auto p = next_greater_index(a), q = next_greater_circular(a);
        string out;
        for (int i = 0; i < n; ++i) { if (i) out += ' '; out += to_string(p[i]); }
        out += '\n';
        for (int i = 0; i < n; ++i) { if (i) out += ' '; out += to_string(q[i]); }
        out += '\n';
        cout << out;
    }
}
```

## Tests
=== sample
5
2 1 2 4 3
4
5 5 5 5
---
3 2 3 -1 -1
4 2 4 -1 4
-1 -1 -1 -1
-1 -1 -1 -1
=== hidden
1
7
6
6 5 4 3 2 1
6
1 2 3 4 5 6
7
-3 -1 -2 -1 -5 0 -10
---
-1
-1
-1 -1 -1 -1 -1 -1
-1 6 6 6 6 6
1 2 3 4 5 -1
2 3 4 5 6 -1
1 5 3 5 5 -1 -1
-1 0 -1 0 0 -1 -3
=== hidden
9
2 -2 1 0 -3 0 3 -2 3
2
0 2
8
4 -3 -3 -3 3 -3 -4 0
3
-3 4 0
10
2 4 -4 -2 0 -3 4 -1 -2 2
3
-1 -3 -3
---
6 2 6 6 5 6 -1 8 -1
3 1 3 3 0 3 -1 3 -1
1 -1
2 -1
-1 4 4 4 -1 7 7 -1
-1 3 3 3 4 0 0 4
1 -1 -1
4 -1 4
1 -1 3 4 6 6 -1 9 9 -1
4 -1 -2 0 4 4 -1 2 2 4
-1 -1 -1
-1 -1 -1
=== hidden
9
4 4 4 4 0 1 3 1 -1
1
2
2
1 0
3
-2 2 -4
6
-2 -4 -1 -4 -2 -4
5
1 -2 3 -4 -3
---
-1 -1 -1 -1 5 6 -1 -1 -1
-1 -1 -1 -1 1 3 4 4 4
-1
-1
-1 -1
-1 1
1 -1 -1
2 -1 -2
2 2 -1 4 -1 -1
-1 -1 -1 -2 -1 -2
2 2 -1 4 -1
3 3 -1 -3 1
=== hidden
6
0 -4 2 3 -4 0
1
3
9
0 -4 -1 0 -4 0 2 -3 0
9
-3 0 2 4 3 3 -4 -1 3
4
1 -1 -4 4
9
4 4 1 4 2 -4 4 1 -4
---
2 2 3 -1 5 -1
2 2 3 -1 0 2
-1
-1
6 2 3 6 5 6 -1 8 -1
2 -1 0 2 0 2 -1 0 2
1 2 3 -1 -1 -1 7 8 -1
0 2 4 -1 4 4 -1 3 4
3 3 3 -1
4 4 4 -1
-1 -1 3 -1 6 6 -1 -1 -1
-1 -1 4 -1 4 4 -1 4 4
=== hidden
@gen 3232152378 big
=== hidden
@gen 3232152379 big
=== hidden
@gen 3232152380 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(1, 10) if not big else 1000000
    if big and r.random() < 0.5:
        a = sorted((r.randint(-10**9, 10**9) for _ in range(n)), reverse=True)
    else:
        a = [r.randint(-4, 4) if not big else r.randint(-10**9, 10**9) for _ in range(n)]
    print(n); print(*a)
```

## Hints
- Keep the indices that are still waiting for an answer. What order do their values have?
- When a new value arrives, pop every waiting index with a smaller value: the new index is their answer.
- For the circular version, iterate `2n` times using `i % n`, but push only in the first `n` steps.

## Solution
Keep a stack of indices whose answer is **not known yet**. Their values are non-increasing from bottom to top: if a smaller value sat below a larger one, the larger one would already have answered it.

When `a[i]` arrives, every waiting element smaller than `a[i]` has just found its next greater element, and they are exactly the ones on top. Pop and answer them; then `a[i]` itself starts waiting.

```text
a = 2 1 2 4 3
i=0 (2): stack [0]
i=1 (1): 1 < 2, push         [0 1]
i=2 (2): pop 1 (1<2) res[1]=2; a[0]=2 is not < 2, stop; push  [0 2]
i=3 (4): pop 2 res[2]=3, pop 0 res[0]=3; push   [3]
i=4 (3): push                [3 4]   -> 3 and 4 stay -1
```

**Circular:** walk indices `0 … 2n−1` modulo n. The second lap lets elements near the end find answers near the start. Push only during the first lap, so no element waits twice.

Each index is pushed once and popped at most once: O(n) total, despite the inner `while`.

```cpp
#include <bits/stdc++.h>
using namespace std;

vector<int> next_greater_index(const vector<int>& a) {
    int n = a.size();
    vector<int> res(n, -1), st;              // st: indices still waiting, values non-increasing
    st.reserve(n);
    for (int i = 0; i < n; ++i) {
        while (!st.empty() && a[st.back()] < a[i]) {   // a[i] is the answer for everything smaller on top
            res[st.back()] = i;
            st.pop_back();
        }
        st.push_back(i);
    }
    return res;                              // whatever is left has no greater element
}

vector<int> next_greater_circular(const vector<int>& a) {
    int n = a.size();
    vector<int> res(n, -1), st;
    st.reserve(n);
    for (int k = 0; k < 2 * n; ++k) {        // walk the array twice: the second lap only resolves
        int i = k % n;
        while (!st.empty() && a[st.back()] < a[i]) { res[st.back()] = a[i]; st.pop_back(); }
        if (k < n) st.push_back(i);          // push each index once, during the first lap
    }
    return res;
}
```
