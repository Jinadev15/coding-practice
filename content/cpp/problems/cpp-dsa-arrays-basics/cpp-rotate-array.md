---
id: cpp-rotate-array
title: Rotate an Array In Place
difficulty: Easy
order: 1
tags: arrays, reversal, in-place, rotation
time_limit: 2
---
## Statement
Rotate an array **right** by `k` positions, in place with O(1) extra memory: every element moves `k` places to the right, and elements that fall off the end wrap around to the front.

```cpp
void rotate_right(std::vector<int>& a, long long k);    // k can be negative: rotate LEFT by |k|
```

For example, `[1,2,3,4,5,6,7]` rotated by 3 becomes `[5,6,7,1,2,3,4]`, and rotated by −2 it becomes `[3,4,5,6,7,1,2]`.

`|k|` can be up to 10¹⁸, and `n` up to 10⁶. An empty array stays empty.

**Input:** cases until the end of input. Each case is `n k` followed by `n` integers. The driver prints the first 10 elements of the result (or all of them if there are fewer), then a checksum Σ (i+1)·a[i] mod 10⁹+7.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

void rotate_right(vector<int>& a, long long k) {
    // shifting by one position k times is O(n·k): far too slow
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    long long n, k;
    while (cin >> n >> k) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        rotate_right(a, k);
        long long h = 0;
        for (long long i = 0; i < n; ++i) h = (h + (i + 1) % 1000000007 * ((a[i] % 1000000007 + 1000000007) % 1000000007)) % 1000000007;
        for (long long i = 0; i < min(n, 10LL); ++i) cout << a[i] << ' ';
        cout << "| " << h << '\n';
    }
}
```

## Tests
=== sample
7 3
1 2 3 4 5 6 7
7 -2
1 2 3 4 5 6 7
---
5 6 7 1 2 3 4 | 98
3 4 5 6 7 1 2 | 105
=== hidden
0 5
---
| 0
=== hidden
1 1000000000000000000
42
---
42 | 42
=== hidden
5 10
1 2 3 4 5
---
1 2 3 4 5 | 55
=== hidden
6 -1000000000000000001
1 2 3 4 5 6
---
6 1 2 3 4 5 | 76
=== hidden
0 18

0 25

0 -22

8 -3
5 4 0 6 4 -5 4 8
7 5
-6 6 -3 1 -8 -3 0
---
| 0
| 0
| 0
6 4 -5 4 8 5 4 0 | 113
-3 1 -8 -3 0 -6 6 | 999999976
=== hidden
1 28
-8
0 1

9 17
-7 -7 -9 6 9 -3 4 8 -7
4 2
4 -3 -7 5
0 -30

---
-8 | 999999999
| 0
-7 -9 6 9 -3 4 8 -7 -7 | 999999982
-7 5 4 -3 | 3
| 0
=== hidden
0 -7

7 12
8 -6 0 7 4 -8 -5
3 -13
1 -2 2
3 18
5 8 -7
4 -8
8 4 -1 -8
---
| 0
0 7 4 -8 -5 8 -6 | 999999982
-2 2 1 | 5
5 8 -7 | 0
8 4 -1 -8 | 999999988
=== hidden
@gen 128597027 big
=== hidden
@gen 128597028 big
=== hidden
@gen 128597029 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
if sys.argv[2] == "small":
    for _ in range(5):
        n = r.randint(0, 9); print(n, r.randint(-30, 30)); print(*[r.randint(-9, 9) for _ in range(n)])
else:
    n = 1000000; print(n, r.randint(-10**18, 10**18)); print(" ".join(str(r.randint(-10**9, 10**9)) for _ in range(n)))
```

## Hints
- First reduce `k` with `k % n`, and fix negative remainders by adding `n`.
- Reverse the whole array. Where did the last `k` elements end up?
- Then reverse the first `k` elements and the remaining `n − k` separately.

## Solution
**Normalise first.** Rotating by `n` does nothing, so use `k mod n`. In C++, `%` of a negative number is negative (or zero), so add `n` to turn a left rotation into the equivalent right rotation.

**Three reversals.** Reversing the whole array puts the last `k` elements at the front, but backwards. Reversing each of the two parts then fixes their internal order. Every element is moved twice.

Complexity: O(n) time, O(1) extra space.

```cpp
#include <bits/stdc++.h>
using namespace std;

void rotate_right(vector<int>& a, long long k) {
    long long n = a.size();
    if (n == 0) return;
    k %= n;
    if (k < 0) k += n;                       // left by |k| == right by n - |k|
    reverse(a.begin(), a.end());             // [7 6 5 4 3 2 1]
    reverse(a.begin(), a.begin() + k);       // [5 6 7 | 4 3 2 1]
    reverse(a.begin() + k, a.end());         // [5 6 7 | 1 2 3 4]
}
```
