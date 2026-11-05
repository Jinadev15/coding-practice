---
id: cpp-sw-product-less
title: Subarrays with Product Less Than k
difficulty: Medium
order: 8
tags: sliding window, counting, products, overflow
time_limit: 2
---
## Statement
```cpp
long long count_product_less(const std::vector<int>& a, long long k);
    // number of contiguous subarrays whose product is strictly less than k (all a[i] >= 1)
```

`[10, 5, 2, 6]` with k = 100 gives 8: [10], [5], [2], [6], [10,5], [5,2], [2,6], [5,2,6].

All values are positive, so the product grows as the window extends, and the window is monotone. After shrinking until the product is below `k`, every subarray ending at `R` and starting in `[L, R]` qualifies.

**Overflow:** with values up to 1000 and k up to 10¹⁸, the product could exceed 64 bits before you shrink. Keep the product below `k` at all times, and check `prod > (k − 1) / a[R]` before multiplying, or shrink first and then multiply in `unsigned __int128`.

**Input:** cases until the end of input: `n k` + n values (n ≤ 10⁶, 1 ≤ a[i] ≤ 1000, 0 ≤ k ≤ 10¹⁸).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long count_product_less(const vector<int>& a, long long k) {
    long long cnt = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        long long p = 1;
        for (size_t j = i; j < a.size(); ++j) { p *= a[j]; if (p < k) ++cnt; else break; }
    }
    return cnt;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n; long long k;
    while (cin >> n >> k) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        cout << count_product_less(a, k) << '\n';
    }
}
```

## Tests
=== sample
4 100
10 5 2 6
3 0
1 2 3
---
8
0
=== hidden
1 2
1
5 1
1 1 1 1 1
5 2
1 1 1 1 1
3 1000000000000000000
1000 1000 1000
---
1
0
15
6
=== hidden
2 194
913 2
9 54
2 1 2 2 280 2 1 1 2
5 156
191 1 1 866 1
10 1
2 1 1 1 1 2 1 2 2 1
8 450481093889853361
2 1 2 1 1 51 2 1
3 1
1 1 2
---
1
20
4
0
36
0
=== hidden
6 0
1 1 1 1 2 1
8 0
1 759 1 1 2 1 2 1
1 1
1
6 1
1 1 906 2 2 1
3 0
1 1 1
1 1
675
---
0
0
0
0
0
0
=== hidden
5 1
1 1 986 371 1
7 1
1 769 1 1 1 1 1
5 1
1 1 1 1 1
9 190058650426770869
1 1 1 2 1 855 1 1 1
9 946056416440366954
1 1 103 1 1 1 2 2 1
2 0
2 799
---
0
0
0
45
45
0
=== hidden
@gen 2103950579 big
=== hidden
@gen 2103950580 big
=== hidden
@gen 2103950581 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(6 if not big else 2):
    n = r.randint(1, 10) if not big else 1000000
    print(n, r.choice([0, 1, r.randint(1, 200), r.randint(1, 10**18)])); print(*[r.choice([1, 1, 2, r.randint(1, 1000)]) for _ in range(n)])
```

## Hints
- With positive numbers, extending a window never decreases its product, so a shrinking window works.
- After shrinking until the product is below k, how many valid subarrays end at R?
- Guard against overflow: the product is below k before each multiplication, so a 128-bit integer can hold product × a[R].

## Solution
Positive values make the product monotone in the window length, so this is the standard counting window: grow `R`, shrink `L` while the product is at least `k`, then add `R − L + 1`.

**The product stays bounded.** Before multiplying, the product is below `k ≤ 10¹⁸`, and after multiplying by at most 1000 it is below 10²¹. That fits easily in `unsigned __int128`, and dividing exactly removes `a[L]`, because the product is the exact product of the window. Without the 128-bit type, the starter's `long long` product overflows on long runs (undefined behaviour), and its O(n²) loop is too slow anyway.

When `L` passes `R`, the window is empty and the product is back to 1, which is consistent.

**Alternative:** use logarithms (`Σ log a[i] < log k`) with prefix sums and binary search. It's O(n log n), and floating-point rounding needs care.

Complexity: O(n).

```cpp
#include <bits/stdc++.h>
using namespace std;

long long count_product_less(const vector<int>& a, long long k) {
    if (k <= 1) return 0;                               // every product is >= 1
    unsigned __int128 prod = 1;
    long long cnt = 0; int L = 0;
    for (int R = 0; R < (int)a.size(); ++R) {
        prod *= a[R];                                   // prod < k <= 1e18 before, so < 1e21 now: fits in 128 bits
        while (prod >= (unsigned __int128)k) prod /= a[L++];
        cnt += R - L + 1;
    }
    return cnt;
}
```
