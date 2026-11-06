---
id: cpp-ms-132-pattern
title: The 132 Pattern
difficulty: Hard
order: 8
tags: monotonic stack, patterns, reverse scan
time_limit: 1
---
## Statement
```cpp
bool has_132(const std::vector<int>& a);
```

A **132 pattern** is a triple of indices `i < j < k` with `a[i] < a[k] < a[j]` (small, big, middle; all strict). Return whether one exists.

- `[1, 2, 3, 4]` → no. `[3, 1, 4, 2]` → yes (1, 4, 2). `[-1, 3, 2, 0]` → yes. `[1, 0, 1, -4, -3]` → no.

O(n³) and O(n²) are too slow; aim for **O(n)**.

**Input:** cases until the end of input: `n` + values (n ≤ 10⁶ in total, |a[i]| ≤ 10⁹). Print `yes` or `no` per case.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

bool has_132(const vector<int>& a) {
    int n = a.size();
    int mn = INT_MAX;                              // O(n^2): best "1" before j, then look for a "2" after j
    for (int j = 0; j < n; ++j) {
        if (mn < a[j])
            for (int k = j + 1; k < n; ++k) if (mn < a[k] && a[k] < a[j]) return true;
        mn = min(mn, a[j]);
    }
    return false;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<int> a(n); for (auto& x : a) cin >> x;
        cout << (has_132(a) ? "yes" : "no") << '\n';
    }
}
```

## Tests
=== sample
4
1 2 3 4
4
3 1 4 2
4
-1 3 2 0
5
1 0 1 -4 -3
---
no
yes
yes
no
=== hidden
1
5
3
1 3 2
3
2 3 1
3
1 1 1
6
3 5 0 3 4 2
5
1 3 3 3 2
---
no
yes
no
no
yes
yes
=== hidden
6
1 -2 0 2 2 0
1
1
7
-2 3 1 -2 -3 0 -1
2
0 0
5
2 1 3 0 4
1
0
1
0
3
2 0 1
---
yes
no
yes
no
no
no
no
no
=== hidden
4
3 1 2 0
5
3 -3 3 3 3
6
3 4 5 1 0 2
4
-1 -2 -3 -3
4
3 -1 -1 -2
4
-1 0 -2 2
7
4 5 6 2 1 3 0
9
3 -3 -3 -1 -3 2 3 0 0
---
no
no
no
no
no
no
no
yes
=== hidden
4
2 3 0 1
2
0 1
7
-3 1 -1 -3 2 1 3
5
0 3 3 -3 0
5
1 1 0 0 2
5
2 1 0 1 0
7
6 4 2 3 5 1 0
8
-1 -1 3 0 -3 -2 1 -1
---
no
no
yes
no
no
no
no
yes
=== hidden
@gen 722617018 big
=== hidden
@gen 722617019 big
=== hidden
@gen 722617020 big

## Generator
```python
import random, sys
sys.setrecursionlimit(10000)
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
def avoid(n):
    # random 132-avoiding permutation of 0..n-1: the maximum splits it into a left part with
    # larger values and a right part with smaller values, both 132-avoiding (built iteratively)
    res, work = [], [(n, 0)]
    while work:
        sz, b = work.pop()
        if sz == "x": res.append(b); continue
        if sz == 0: continue
        k = r.randrange(sz)                 # how many elements go left of the maximum
        right = sz - 1 - k
        work.append((right, b))             # processed last: smallest values, on the right
        work.append(("x", b + sz - 1))      # the maximum
        work.append((k, b + right))         # processed first: larger values, on the left
    return res
for _ in range(8 if not big else 1):
    n = r.randint(1, 9) if not big else 1000000
    if r.random() < 0.55:
        p = avoid(n)
        # merge some neighbouring values (a monotone map keeps the pattern-free property)
        step = r.choice([1, 1, 2, 3])
        a = [x // step for x in p]
        if big: a = [x * 1000 - 10**9 for x in a]
        if big and r.random() < 0.5 and n > 10:
            i = r.randrange(n - 3)       # plant a pattern somewhere
            a[i], a[i + 1], a[i + 2] = 0, 2, 1
    else:
        a = [r.randint(-3, 3) if not big else r.randint(-10**9, 10**9) for _ in range(n)]
    print(n); print(*a)
```

## Hints
- Fix the middle element "3" and the best "1" is the smallest value before it. Scanning from the right may be easier.
- Scanning right to left, maintain the largest value that has a bigger element to its left among the scanned ones: the best "2".
- Keep a stack; when `a[i]` is bigger than the top, pop and record the popped value as the "2". Any later `a[i]` below it completes a pattern.

## Solution
Scan **from the right**, and maintain `third`: the largest value that can serve as the "2" of a pattern whose "3" lies to its left (and already scanned). Then a pattern exists as soon as some `a[i] < third`: `a[i]` is the "1".

How to keep `third` as large as possible? Keep a stack of values seen so far (to the right). When `a[i]` arrives, every stack value smaller than `a[i]` can be a "2" with `a[i]` as its "3"; pop them, and `third` becomes the last (largest) one popped. Then push `a[i]`.

```text
a = 3 1 4 2      scan right to left
2   stack [2]                      third = -inf
4   pop 2 (2 < 4): third = 2       stack [4]
1   1 < third = 2  -> yes  (1, 4, 2)
```

**Why it is correct.** Every value ever stored in `third` was popped by a larger element to its **left**, so `third` always comes with a real "3" before it: when `a[i] < third`, the triple (i, the popper, the popped) is a 132 pattern. Conversely, `third` never decreases: a value is popped only by a larger element, and that element is then popped only by a still larger one, so later pops carry larger values. Keeping the largest possible "2" can only make finding a "1" easier, so no pattern is missed.

Each element is pushed and popped once: O(n).

**Simpler O(n log n) idea** (worth knowing): for each `j`, the best "1" is the prefix minimum before `j`; look for a "2" in `(min, a[j])` among the elements to the right with an ordered set.

```cpp
#include <bits/stdc++.h>
using namespace std;

bool has_132(const vector<int>& a) {
    vector<int> st;                       // values to the right of i that are still candidates for a "3"
    st.reserve(a.size());
    long long third = LLONG_MIN;          // the best "2" found so far: the largest value popped by a bigger "3"
    for (int i = (int)a.size() - 1; i >= 0; --i) {
        if (a[i] < third) return true;    // a[i] can be the "1"
        while (!st.empty() && st.back() < a[i]) {   // a[i] is a "3" for each smaller value to its right
            third = st.back();
            st.pop_back();
        }
        st.push_back(a[i]);
    }
    return false;
}
```
