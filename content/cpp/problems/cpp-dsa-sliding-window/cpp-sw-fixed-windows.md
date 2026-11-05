---
id: cpp-sw-fixed-windows
title: Fixed-Size Window Statistics
difficulty: Easy
order: 1
tags: sliding window, fixed window, running sums
time_limit: 2
---
## Statement
For a window size `k`, compute three statistics over **all** windows of `k` consecutive elements:

```cpp
long long max_window_sum(const std::vector<int>& a, int k);
int count_avg_at_least(const std::vector<int>& a, int k, long long threshold);   // windows with average >= threshold
int max_vowels(const std::string& s, int k);                                     // max vowels (a,e,i,o,u) in any length-k substring
```

1 ≤ k ≤ n ≤ 10⁶. Each window must be updated from the previous one in O(1): add the element entering on the right, and subtract the one leaving on the left.

To compare an average with the threshold **without floating point**, compare `sum ≥ threshold × k`.

**Input:** cases until the end of input: `nums n k threshold` + n integers, or `vowels k s`.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long max_window_sum(const vector<int>& a, int k) {
    long long best = LLONG_MIN;
    for (size_t i = 0; i + k <= a.size(); ++i) { long long s = 0; for (int j = 0; j < k; ++j) s += a[i + j]; best = max(best, s); }
    return best;
}
int count_avg_at_least(const vector<int>& a, int k, long long threshold) { return 0; }
int max_vowels(const string& s, int k) { return 0; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd;
    while (cin >> cmd) {
        if (cmd == "nums") {
            int n, k; long long t; cin >> n >> k >> t;
            vector<int> a(n); for (auto& x : a) cin >> x;
            cout << max_window_sum(a, k) << ' ' << count_avg_at_least(a, k, t) << '\n';
        } else {
            int k; string s; cin >> k >> s;
            cout << max_vowels(s, k) << '\n';
        }
    }
}
```

## Tests
=== sample
nums 6 3 3
2 1 5 1 3 2
vowels 3 abciiidef
---
9 1
3
=== hidden
nums 1 1 5
5
nums 5 5 -2
-1 -2 -3 -4 -5
vowels 2 xyz
vowels 1 a
nums 4 2 0
0 0 -1 1
---
5 1
-15 0
0
1
0 2
=== hidden
vowels 1 uaiiaxaz
nums 5 4 1
-7 3 1 1 1
nums 9 9 -3
-9 -6 -4 -7 -2 -1 -9 3 -5
nums 4 3 -3
-1 9 0 3
nums 9 4 1
0 -9 0 -2 7 -5 -4 -1 -9
nums 9 6 5
3 3 0 6 -8 0 -3 -9 -4
---
1
6 1
-40 0
12 2
0 0
4 0
=== hidden
nums 1 1 -4
4
nums 8 6 5
2 -2 7 -1 7 4 -4 -9
vowels 1 iuu
vowels 1 yz
vowels 1 y
vowels 1 bio
---
4 1
17 0
1
0
0
1
=== hidden
nums 7 6 -1
-3 0 2 -6 -2 -8 7
vowels 1 be
vowels 5 yzyuobaebi
nums 4 1 -3
-6 -1 -3 -4
nums 5 1 2
-6 5 7 -9 -9
nums 5 2 3
7 -8 8 -1 -3
---
-7 0
1
4
-1 2
7 2
7 1
=== hidden
@gen 1684761716 big
=== hidden
@gen 1684761717 big
=== hidden
@gen 1684761718 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(1, 10) if not big else 1000000
    k = r.randint(1, n)
    if r.random() < 0.6:
        print("nums", n, k, r.randint(-5, 5)); print(*[r.randint(-9, 9) if not big else r.randint(-10**9, 10**9) for _ in range(n)])
    else:
        print("vowels", k, "".join(r.choice("abeiouxyz") for _ in range(n)))
```

## Hints
- Keep a running total. Add `a[R]` as it enters, and subtract `a[R−k]` once the window is longer than `k`.
- A window is complete once `R ≥ k − 1`. Only measure then.
- Compare `sum >= threshold * k` (in `long long`) instead of computing an average.

## Solution
All three are the same loop. `R` scans once. The element at `R` enters the window, and once `R ≥ k`, the element at `R − k` leaves. From `R = k − 1` on, the window holds exactly `k` elements and can be measured.

Multiplying instead of dividing (`sum ≥ t·k`) keeps everything exact: no floating point and no rounding. With `|a[i]|, |t| ≤ 10⁹` and `k ≤ 10⁶`, `t·k ≤ 10¹⁵` fits in `long long`.

Complexity: O(n) time, O(1) extra space for each.

```cpp
#include <bits/stdc++.h>
using namespace std;

long long max_window_sum(const vector<int>& a, int k) {
    long long sum = 0, best = LLONG_MIN;
    for (int R = 0; R < (int)a.size(); ++R) {
        sum += a[R];                          // enters
        if (R >= k) sum -= a[R - k];          // leaves
        if (R >= k - 1) best = max(best, sum);
    }
    return best;
}

int count_avg_at_least(const vector<int>& a, int k, long long threshold) {
    long long sum = 0; int cnt = 0;
    for (int R = 0; R < (int)a.size(); ++R) {
        sum += a[R];
        if (R >= k) sum -= a[R - k];
        if (R >= k - 1 && sum >= threshold * k) ++cnt;     // average >= t  <=>  sum >= t*k
    }
    return cnt;
}

int max_vowels(const string& s, int k) {
    auto vowel = [](char c) { return c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u'; };
    int cur = 0, best = 0;
    for (int R = 0; R < (int)s.size(); ++R) {
        cur += vowel(s[R]);
        if (R >= k) cur -= vowel(s[R - k]);
        if (R >= k - 1) best = max(best, cur);
    }
    return best;
}
```
