---
id: cpp-kd-majority-vote
title: Majority Elements by Voting
difficulty: Medium
order: 4
tags: Boyer-Moore voting, arrays, O(1) space
time_limit: 2
---
## Statement
```cpp
int majority(const std::vector<int>& a);
    // the element appearing MORE than n/2 times, or -1 if there is none
std::vector<int> above_third(const std::vector<int>& a);
    // all elements appearing MORE than n/3 times, in increasing order (at most two)
```

Both use **O(1) extra memory**, so no hash maps: Boyer–Moore voting. For `> n/3`, keep **two** candidates with two counters. A new value either matches a candidate, fills an empty slot, or decrements **both** counters. Voting only finds *candidates*, so always **verify** them with a second counting pass.

**Input:** cases until the end of input: `n` + values (n ≤ 10⁶, 0 ≤ a[i] ≤ 10⁹).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int majority(const vector<int>& a) {
    vector<int> b = a; sort(b.begin(), b.end());
    return b[b.size() / 2];                        // the median: but is it really a majority?
}
vector<int> above_third(const vector<int>& a) { return {}; }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        cout << majority(a) << " |";
        for (int x : above_third(a)) cout << ' ' << x;
        cout << '\n';
    }
}
```

## Tests
=== sample
3
3 2 3
7
2 2 1 1 1 2 2
3
1 2 3
---
3 | 3
2 | 1 2
-1 |
=== hidden
1
5
2
1 2
6
1 1 2 2 3 3
5
4 4 0 0 4
---
5 | 5
-1 | 1 2
-1 |
4 | 0 4
=== hidden
7
3 4 3 1 3 2 3
8
2 1 0 1 0 1 2 3
8
0 0 0 1 0 0 2 0
4
3 2 2 1
7
4 2 3 1 1 0 4
8
1 2 2 2 1 1 3 3
9
5 6 7 6 7 6 7 8 6
---
3 | 3
-1 | 1
0 | 0
-1 | 2
-1 |
-1 | 1 2
-1 | 6
=== hidden
2
1 0
7
1 0 2 0 1 0 3
1
0
7
2 3 2 1 4 0 0
8
0 4 0 0 4 4 2 0
10
3 4 1 0 0 1 4 2 1 4
---
-1 | 0 1
-1 | 0
0 | 0
-1 |
-1 | 0 4
-1 |
=== hidden
9
1 1 2 4 0 1 3 1 1
3
2 4 3
4
2 4 2 1
4
0 3 3 3
4
3 2 2 2
9
1 1 0 4 1 1 2 2 4
---
1 | 1
-1 |
-1 | 2
3 | 3
2 | 2
-1 | 1
=== hidden
2
0 1
8
2 2 3 4 2 1 2 0
1
2
7
0 1 1 2 4 0 0
9
2 3 0 2 0 0 2 3 2
1
3
---
-1 | 0 1
-1 | 2
2 | 2
-1 | 0
-1 | 2
3 | 3
=== hidden
@gen 569618016 big
=== hidden
@gen 569618017 big
=== hidden
@gen 569618018 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(1, 10) if not big else 1000000
    hot = r.randint(0, 3)
    a = [hot if r.random() < r.choice([0.3, 0.4, 0.55]) else r.randint(0, 4 if not big else 10**9) for _ in range(n)]
    print(n); print(*a)
```

## Hints
- Keep one candidate and a counter: adopt a new candidate when the counter is 0, add 1 for a match and subtract 1 otherwise.
- For "more than n/3", keep two candidates and two counters. When the value matches neither and both counters are positive, decrement both.
- Voting proposes candidates but proves nothing. Count their real occurrences in a second pass.

## Solution
**Cancellation view.** A `−1` vote pairs one copy of the candidate with one copy of a different value and throws both away. Removing two different values can't destroy a strict majority. So a value with more than n/2 copies is still standing at the end.

**n/3 version.** A decrement of *both* counters throws away **three distinct values** at once. A value with more than n/3 copies can't be completely removed that way, so it must be one of the two final candidates. Order matters: check the matches first, then empty slots, then cancel.

**Verification** is mandatory. When no majority exists, the final candidate is arbitrary. `[1, 2, 3]` leaves candidate 3, which is not a majority. The starter's "median" trick has the same flaw.

Complexity: O(n) time, O(1) extra space.

```cpp
#include <bits/stdc++.h>
using namespace std;

int majority(const vector<int>& a) {
    int cand = -1, cnt = 0;
    for (int x : a) {
        if (cnt == 0) cand = x;
        cnt += (x == cand) ? 1 : -1;
    }
    long long occ = count(a.begin(), a.end(), cand);         // verify: voting only proposes
    return 2 * occ > (long long)a.size() ? cand : -1;
}

vector<int> above_third(const vector<int>& a) {
    int c1 = -1, c2 = -2, n1 = 0, n2 = 0;                    // two distinct dummy candidates
    for (int x : a) {
        if (x == c1) ++n1;
        else if (x == c2) ++n2;
        else if (n1 == 0) { c1 = x; n1 = 1; }
        else if (n2 == 0) { c2 = x; n2 = 1; }
        else { --n1; --n2; }                                 // cancel a triple of distinct values
    }
    vector<int> out;
    for (int c : {c1, c2}) {
        if (c < 0) continue;
        long long occ = count(a.begin(), a.end(), c);
        if (3 * occ > (long long)a.size()) out.push_back(c);
    }
    sort(out.begin(), out.end());
    out.erase(unique(out.begin(), out.end()), out.end());
    return out;
}
```
