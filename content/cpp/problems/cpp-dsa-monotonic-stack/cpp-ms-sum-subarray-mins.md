---
id: cpp-ms-sum-subarray-mins
title: Sum of Subarray Minimums by Contribution
difficulty: Medium
order: 6
tags: monotonic stack, contribution technique, counting, modular arithmetic
time_limit: 1
---
## Statement
```cpp
long long sum_subarray_mins(const std::vector<int>& a);   // modulo 1'000'000'007
```

Return the sum of `min(a[l..r])` over **all** `n(n+1)/2` contiguous subarrays, modulo 10⁹ + 7.

`[3, 1, 2, 4]`: subarray minimums are 3, 1, 2, 4, 1, 1, 2, 1, 1, 1 → **17**.

Values repeat, so be careful not to count a subarray whose minimum appears twice for both copies. O(n) is required.

**Input:** cases until the end of input: `n` + values (n ≤ 10⁶ in total, 1 ≤ a[i] ≤ 10⁹).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long sum_subarray_mins(const vector<int>& a) {
    const long long MOD = 1'000'000'007;
    long long s = 0;
    for (size_t i = 0; i < a.size(); ++i) {               // O(n^2)
        int mn = INT_MAX;
        for (size_t j = i; j < a.size(); ++j) { mn = min(mn, a[j]); s = (s + mn) % MOD; }
    }
    return s;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<int> a(n); for (auto& x : a) cin >> x;
        cout << sum_subarray_mins(a) << '\n';
    }
}
```

## Tests
=== sample
4
3 1 2 4
5
2 2 2 2 2
---
17
30
=== hidden
1
1000000000
5
11 81 94 43 3
6
1 2 3 4 5 6
6
6 5 4 3 2 1
---
1000000000
444
56
56
=== hidden
1
943369811
2
1 3
6
895318641 909469665 354642489 43354069 118788177 429420528
1
2
10
286288551 555044291 258994558 615308120 206570214 198655365 904383892 545328953 365756902 73217870
6
1 1 2 1 1 1
---
943369811
5
951280096
2
921967811
22
=== hidden
5
660351680 219363683 263721935 996907761 959458718
3
3 3 1
5
1 2 2 1 3
8
110564120 851532729 150784550 101580910 176854223 378455069 880681165 238741704
10
1 1 3 2 2 3 1 2 2 1
5
1 3 3 2 1
---
122252104
12
20
577645654
70
24
=== hidden
10
928696054 848583189 494696175 717667003 760811708 482723937 559730212 401626907 732917252 595608175
2
3 1
8
215515876 105904525 90512276 99965491 387162419 125349065 150124516 81737383
9
360560176 673792441 457299886 510306210 798693810 382353685 998988675 241599352 431370539
2
3 3
5
124888352 722528711 332684960 202472204 744170676
---
189870358
5
877453268
880304803
9
971344270
=== hidden
@gen 929327299 big
=== hidden
@gen 929327300 big
=== hidden
@gen 929327301 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(1, 10) if not big else 1000000
    hi = r.choice([3, 10**9]) if not big else r.choice([5, 10**9])
    a = [r.randint(1, hi) for _ in range(n)]
    print(n); print(*a)
```

## Hints
- Flip the loop: for each element, count the subarrays in which it is the minimum.
- That count is `(i − prevSmaller) × (nextSmaller − i)`; both boundaries come from monotonic stacks.
- With duplicates, use "strictly smaller" on one side and "smaller or equal" on the other, so each subarray is counted once.

## Solution
**Contribution technique.** Instead of looping over subarrays, ask for each element: in how many subarrays is `a[i]` the minimum? Then the answer is `Σ a[i] · count(i)`.

`a[i]` is the minimum of `a[l..r]` when `l` lies after the previous smaller element and `r` before the next smaller element. With `L` and `R` those boundaries, there are `(i − L)` choices of `l` and `(R − i)` choices of `r`.

**Ties.** In `[2, 2]`, the subarray `[2, 2]` would be counted for both copies if both sides used "strictly smaller". Break the tie asymmetrically: stop at a **strictly smaller** element on the left and a **smaller or equal** element on the right. Then every subarray is assigned to exactly one of its minimum positions: the left boundary passes over equal values and the right boundary stops at them, so a subarray belongs to its **rightmost** minimum. Either convention works, as long as the two sides differ.

```text
a = 3 1 2 4
i  L   R   (i-L)(R-i)   contribution
0  -1  1   1*1 = 1      3
1  -1  4   2*3 = 6      6
2  1   4   1*2 = 2      4
3  2   4   1*1 = 1      4      total 17
```

Two monotonic-stack passes compute all boundaries in O(n). Reduce modulo M as you go: `(i − L)(R − i)` can reach 2.5·10¹¹, so reduce it before multiplying by `a[i]`.

```cpp
#include <bits/stdc++.h>
using namespace std;

long long sum_subarray_mins(const vector<int>& a) {
    const long long MOD = 1'000'000'007;
    int n = a.size();
    vector<int> left(n), right(n), st;
    st.reserve(n);
    for (int i = 0; i < n; ++i) {                 // previous STRICTLY smaller
        while (!st.empty() && a[st.back()] >= a[i]) st.pop_back();
        left[i] = st.empty() ? -1 : st.back();
        st.push_back(i);
    }
    st.clear();
    for (int i = n - 1; i >= 0; --i) {            // next smaller OR EQUAL
        while (!st.empty() && a[st.back()] > a[i]) st.pop_back();
        right[i] = st.empty() ? n : st.back();
        st.push_back(i);
    }
    long long total = 0;
    for (int i = 0; i < n; ++i) {
        long long ways = (long long)(i - left[i]) * (right[i] - i) % MOD;   // subarrays where a[i] is "the" minimum
        total = (total + ways * a[i]) % MOD;
    }
    return total;
}
```
