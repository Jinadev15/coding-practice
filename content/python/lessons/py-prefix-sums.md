# Prefix Sums and Difference Arrays

A **prefix sum** array precomputes running totals, so the sum of any subarray becomes a single subtraction: O(1) per query after O(n) preparation. Its mirror image, the **difference array**, turns "add v to every element in a range" into two O(1) updates. Together they solve range-sum queries, subarray-sum counting, 2-D region sums (integral images in computer vision), and batched range updates (booking systems, sweep lines). And they're the discrete versions of integration and differentiation.

## 1. 1-D prefix sums

Define `P[0] = 0` and `P[i] = a[0] + … + a[i-1]` (length n + 1). Then:

`sum(a[l:r]) = P[r] - P[l]`

```python
from itertools import accumulate

a = [3, 1, 4, 1, 5, 9, 2]
P = [0, *accumulate(a)]          # [0, 3, 4, 8, 9, 14, 23, 25]
def range_sum(l, r):             # half-open [l, r)
    return P[r] - P[l]
range_sum(2, 5)                  # 4 + 1 + 5 = 10
```

> [!KEY]
> The extra leading 0 removes every special case: the sum of the empty range is `P[l] - P[l] = 0`, and the sum from the start is `P[r] - P[0]`. Always build prefix arrays of length n + 1 with half-open queries.

## 2. Subarray sum equals k: prefix sums plus hashing

A subarray `a[l:r]` sums to k exactly when `P[r] - P[l] = k`, i.e. `P[l] = P[r] - k`. Scan r left to right, count how many earlier prefixes equal `P[r] - k`:

```python
from collections import defaultdict

def count_subarrays_sum_k(a, k):
    seen = defaultdict(int)
    seen[0] = 1                    # the empty prefix
    total = running = 0
    for x in a:
        running += x
        total += seen[running - k]
        seen[running] += 1
    return total

count_subarrays_sum_k([1, -1, 1, 1], 1)    # 5
```

That's O(n), and unlike a sliding window it works with **negative numbers**. Variations:

| Question | Hash map stores |
|---|---|
| count subarrays with sum k | count of each prefix value |
| longest subarray with sum k | the **first** index of each prefix value |
| subarray sum divisible by m | count of `prefix % m` (Python's `%` is non-negative) |
| equal number of 0s and 1s | map 0 → −1, then "sum = 0" |
| count subarrays with XOR k | prefix XOR, the same idea (`P[l] = P[r] ^ k`) |

## 3. 2-D prefix sums (summed-area table, integral image)

`S[i][j]` = the sum of the rectangle `grid[0:i][0:j]`. Build it with inclusion–exclusion:

```python
def build_2d(g):
    R, C = len(g), len(g[0])
    S = [[0] * (C + 1) for _ in range(R + 1)]
    for i in range(R):
        row = 0
        for j in range(C):
            row += g[i][j]
            S[i + 1][j + 1] = S[i][j + 1] + row
    return S

def rect_sum(S, r1, c1, r2, c2):        # rows [r1, r2), cols [c1, c2)
    return S[r2][c2] - S[r1][c2] - S[r2][c1] + S[r1][c1]
```

Any rectangle sum is O(1). This is the **integral image** behind Viola–Jones face detection (Haar features in constant time), box blur filters, and fast occupancy queries on robot maps ("how many obstacle cells in this footprint?").

## 4. Difference arrays: O(1) range updates

The difference array `D[i] = a[i] - a[i-1]` is the inverse of the prefix sum. Adding v to `a[l:r]` changes only two differences:

```python
def apply_range_adds(n, updates):        # updates: (l, r, v) meaning a[l:r] += v
    D = [0] * (n + 1)
    for l, r, v in updates:
        D[l] += v
        D[r] -= v                        # stop adding at r
    out, running = [], 0
    for i in range(n):
        running += D[i]
        out.append(running)
    return out

apply_range_adds(5, [(0, 3, 2), (1, 5, 1)])   # [2, 3, 3, 1, 1]
```

q updates and one final pass cost O(n + q), instead of O(n·q).

Applications:
- flight bookings, "car pooling" capacity checks
- counting how many intervals cover each point
- painting/brightness updates
- the **sweep line**: sort the +1/−1 events at interval starts and ends to find the maximum overlap (meeting rooms) in O(n log n) for real-valued coordinates

2-D difference arrays work the same way: add v at (r1, c1), subtract at (r1, c2) and (r2, c1), and add back at (r2, c2), then take a 2-D prefix sum.

## 5. Other prefix "sums"

Any associative operation with an inverse supports range queries the same way:
- **XOR**: `x ^ x = 0` is its own inverse.
- **Products**: when there are no zeros, or track the zero count separately.
- **Counts per category**: one prefix array per letter, so "how many 'a's in s[l:r]" costs O(1).

Operations **without** an inverse (min, max, gcd) need different structures: sparse tables (O(1) queries, static data) or segment trees (supports updates; covered later).

### Prefix and suffix products: "product except self"

```python
def product_except_self(a):
    n = len(a)
    out = [1] * n
    left = 1
    for i in range(n):
        out[i] = left
        left *= a[i]
    right = 1
    for i in range(n - 1, -1, -1):
        out[i] *= right
        right *= a[i]
    return out
```

That's O(n) with no division, so zeros are handled naturally.

## 6. Exam-ready answers

> [!EXAM]
> **Prefix sums.** A prefix sum array stores `P[i]`, the sum of the first i elements, computed in O(n), so that the sum of any contiguous range `[l, r)` is `P[r] − P[l]` in O(1). Combined with a hash map of previously seen prefix values, it counts or finds subarrays with a given sum in O(n) even when values are negative. The two-dimensional analogue (a summed-area table) answers rectangle sums in O(1) by inclusion–exclusion. The inverse construction, a difference array, records range additions as two point updates and recovers the final array with a single prefix-sum pass, processing q range updates in O(n + q).

## 7. Cheat sheet

| Need | Tool |
|---|---|
| many range-sum queries, static | `P = [0, *accumulate(a)]` |
| count/longest subarray with sum k | prefix + dict |
| rectangle sums | 2-D prefix (integral image) |
| many range additions, then read all | difference array |
| max overlap of intervals | sweep line of ±1 events |
| range min/max, static | sparse table |
| sums with point updates | Fenwick / segment tree |

> [!INTERVIEW]
> **"Count subarrays summing to k, with negatives allowed."** A sliding window fails because removing a negative element can *increase* the sum, so validity isn't monotone. Use prefix sums: a subarray `(l, r]` sums to k iff `P[l] = P[r] − k`, so count the earlier prefixes in a dict initialised with `{0: 1}`. That's O(n) time and O(n) space. Mention the `{0: 1}` initialisation explicitly, because it's the common bug.
