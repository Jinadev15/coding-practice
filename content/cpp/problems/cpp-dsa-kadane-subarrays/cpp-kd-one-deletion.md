---
id: cpp-kd-one-deletion
title: Maximum Subarray with at Most One Deletion
difficulty: Medium
order: 7
tags: Kadane, dynamic programming, two states
time_limit: 2
---
## Statement
```cpp
long long max_sum_one_deletion(const std::vector<int>& a);
    // choose a non-empty subarray, then optionally delete ONE element from it; the result must
    // still be non-empty; return the maximum possible sum
```

`[1, −2, 0, 3]` gives 4 (delete −2). `[1, −2, −2, 3]` gives 3. `[−1, −1, −1]` gives −1.

Keep two running states for subarrays ending at `i`:

- `keep`: no deletion used (plain Kadane);
- `del`: exactly one deletion used. Either `a[i]` is the deleted element (take `keep` from position `i−1`), or the deletion happened earlier (extend the previous `del` with `a[i]`).

**Input:** cases until the end of input: `n` + values (n ≤ 10⁶, |a[i]| ≤ 10⁹).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long max_sum_one_deletion(const vector<int>& a) {
    long long cur = a[0], best = a[0];
    for (size_t i = 1; i < a.size(); ++i) { cur = max<long long>(a[i], cur + a[i]); best = max(best, cur); }
    return best;                                         // never deletes anything
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n;
    while (cin >> n) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        cout << max_sum_one_deletion(a) << '\n';
    }
}
```

## Tests
=== sample
4
1 -2 0 3
4
1 -2 -2 3
3
-1 -1 -1
---
4
3
-1
=== hidden
1
-5
2
-5 3
2
3 -5
5
2 -100 3 -100 4
---
-5
3
3
7
=== hidden
3
-2 1 -5
8
2 -5 3 -4 -4 3 -1 -1
5
-2 2 5 5 0
8
4 0 -5 -2 0 -4 4 5
4
-4 4 -4 0
6
3 -2 -2 5 -4 -4
---
1
5
12
9
4
6
=== hidden
6
2 -1 -3 -3 0 2
6
3 -1 5 0 0 4
4
1 3 3 3
2
2 -2
3
-3 -4 2
7
4 4 0 -5 4 -4 -5
---
2
12
10
2
2
12
=== hidden
9
-1 -3 2 1 -4 0 -5 4 -3
8
2 4 4 1 -3 -2 3 -3
6
5 0 1 -5 -2 -5
4
-4 -4 3 5
6
-4 -4 -3 2 1 5
2
-1 -1
---
4
12
6
8
8
-1
=== hidden
@gen 4257211627 big
=== hidden
@gen 4257211628 big
=== hidden
@gen 4257211629 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 1):
    n = r.randint(1, 9) if not big else 1000000
    print(n); print(*[r.randint(-5, 5) if not big else r.randint(-10**9, 10**9) for _ in range(n)])
```

## Hints
- Track two values per index: the best sum ending here with no deletion, and with exactly one deletion.
- With a deletion: either `a[i]` is the one deleted (use the no-deletion value from `i−1`), or the deletion was earlier (add `a[i]` to the previous with-deletion value).
- Start the with-deletion state as "impossible" (a big negative number), and update both states from the previous step's values.

## Solution
**States for subarrays ending at `i`:**

- `keep(i) = max(a[i], keep(i−1) + a[i])`: ordinary Kadane.
- `del(i) = max(keep(i−1), del(i−1) + a[i])`. Either delete `a[i]`, which leaves the best undeleted subarray ending at `i−1`, or keep `a[i]` and extend a subarray where the deletion already happened.

At index 0, a deletion would leave nothing, so `del` starts as "impossible" (a large negative sentinel that won't overflow when added to). `del(1) = keep(0)` correctly represents "keep `a[0]`, delete `a[1]`".

Both states use the previous step's values, so compute the new values into temporaries first.

The answer is the best of either state at any index. The non-empty rule holds automatically, because `del` always keeps at least one element.

Complexity: O(n) time, O(1) space.

```cpp
#include <bits/stdc++.h>
using namespace std;

long long max_sum_one_deletion(const vector<int>& a) {
    const long long NEG = LLONG_MIN / 4;                 // "impossible" state, safe to add to
    long long keep = a[0], del = NEG, best = a[0];
    for (size_t i = 1; i < a.size(); ++i) {
        long long newDel = max(keep, del + a[i]);        // delete a[i], or extend a subarray with an earlier deletion
        long long newKeep = max<long long>(a[i], keep + a[i]);
        keep = newKeep; del = newDel;
        best = max({best, keep, del});
    }
    return best;
}
```
