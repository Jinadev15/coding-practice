# Prefix Sums and Difference Arrays

**Prefix sums** answer "what is the sum of `a[l..r]`?" in O(1) after an O(n) precomputation. **Difference arrays** do the reverse: "add `v` to every element of `a[l..r]`" in O(1), with the final array rebuilt in O(n). Combined with a hash map, prefix sums also count subarrays with a given sum in O(n), **even with negative numbers**, which is exactly where sliding windows fail.

## 1. Prefix sums in 1D

Define `P[0] = 0` and `P[i+1] = P[i] + a[i]`. So `P[i]` is the sum of the first `i` elements.

```text
index i:    0   1   2   3   4
a:          3   1   4   1   5
P:      0   3   4   8   9  14        (P has n+1 entries)
```

**The sum of `a[l..r]` (inclusive) is `P[r+1] − P[l]`.** Everything up to `r`, minus everything before `l`.

```cpp
vector<long long> P(n + 1, 0);
for (int i = 0; i < n; ++i) P[i + 1] = P[i] + a[i];
auto range_sum = [&](int l, int r) { return P[r + 1] - P[l]; };   // O(1)
```

> [!TIP]
> The extra leading 0 removes every special case for `l = 0`. Always build `P` with `n + 1` entries.

The same idea works for any **invertible** operation:

- **XOR:** `x[l..r] = X[r+1] ^ X[l]`.
- **Counts:** a prefix count of vowels, of 1s, of elements equal to `k`.

It doesn't work for `max`/`min`, which have no inverse. Use a sparse table or a segment tree for those (later topics).

## 2. Prefix sums in 2D

For a grid, `S[i][j]` is the sum of the rectangle from `(0,0)` to `(i−1, j−1)`:

```cpp
vector<vector<long long>> S(R + 1, vector<long long>(C + 1, 0));
for (int i = 0; i < R; ++i)
    for (int j = 0; j < C; ++j)
        S[i + 1][j + 1] = g[i][j] + S[i][j + 1] + S[i + 1][j] - S[i][j];   // inclusion–exclusion
```

The sum of the rectangle with rows `r1..r2` and columns `c1..c2` is:

```text
S[r2+1][c2+1] − S[r1][c2+1] − S[r2+1][c1] + S[r1][c1]
```

```text
 ┌────────────┬──────┐
 │     A      │  B   │      wanted = Total − A∪B(top) − A∪C(left) + A
 ├────────────┼──────┤      (A was subtracted twice, so add it back)
 │     C      │ want │
 └────────────┴──────┘
```

## 3. Difference arrays: range updates

You get many updates "add `v` to `a[l..r]`", and you need the final array afterwards. Updating every element is O(n) per update. Instead, record only where the change **starts and stops**:

```cpp
vector<long long> D(n + 1, 0);
void range_add(int l, int r, long long v) { D[l] += v; D[r + 1] -= v; }   // O(1)
// after all updates: the prefix sums of D give the total added to each position
long long run = 0;
for (int i = 0; i < n; ++i) { run += D[i]; a[i] += run; }
```

```text
add 5 to [1..3] on n = 6:   D = [0, +5, 0, 0, −5, 0, 0]
prefix of D:                    [0,  5, 5, 5,  0, 0]   ✓
```

The difference array is the **inverse** of the prefix sum: taking prefix sums of `D` rebuilds the array. Typical uses include flight bookings, "how many intervals cover each point", car pooling, and corporate bonus problems. 2D difference arrays update rectangles with four corner marks.

## 4. Prefix sums + hash map: counting subarrays

**Count subarrays with sum exactly `k`** (values may be negative).

A subarray `a[l..r]` has sum `P[r+1] − P[l]`. We want `P[r+1] − P[l] = k`, which means **`P[l] = P[r+1] − k`**. So while scanning, for each prefix value, ask "how many earlier prefixes equal `current − k`?". A hash map counts the earlier prefixes.

```cpp
long long count_sum_k(const vector<int>& a, long long k) {
    unordered_map<long long, long long> seen;
    seen[0] = 1;                                // the empty prefix
    long long pre = 0, cnt = 0;
    for (int x : a) {
        pre += x;
        auto it = seen.find(pre - k);
        if (it != seen.end()) cnt += it->second;
        ++seen[pre];
    }
    return cnt;
}
```

That's O(n) expected. The `seen[0] = 1` line counts subarrays that start at index 0. Forgetting it is the most common bug.

**Variations of the same idea:**

| Question | Key stored in the map |
|---|---|
| Subarray sum = k | prefix sum |
| Sum divisible by m | prefix sum mod m (normalised to `[0, m)`) |
| Longest subarray with sum = k | the **first** index of each prefix value |
| Equal numbers of 0s and 1s | prefix of (+1 for a 1, −1 for a 0); want sum 0 |
| Subarray XOR = k | prefix XOR, looking up `pre ^ k` |

**Modulo with negatives.** In C++, `-7 % 3 == -1`. Normalise with `((x % m) + m) % m` before using it as a key.

## 5. Choosing between prefix sums and a sliding window

| Situation | Tool |
|---|---|
| Many range-sum queries, static array | prefix sums |
| Many range updates, then read everything | difference array |
| Count subarrays with sum = k (any signs) | prefix sums + hash map |
| Longest/shortest subarray, non-negative values, sum constraint | sliding window |
| Updates and queries interleaved | Fenwick tree or segment tree (later) |

## 6. Worked example: the longest subarray with equal 0s and 1s

Replace each 0 with −1. Equal counts means the subarray sum is 0, so `P[r+1] == P[l]`. For each prefix value, store the **first** index where it appeared. The longest subarray ending here starts right after that first occurrence.

```cpp
int longest_balanced(const vector<int>& bits) {
    unordered_map<int, int> first{{0, -1}};      // prefix value -> first index where it occurred
    int pre = 0, best = 0;
    for (int i = 0; i < (int)bits.size(); ++i) {
        pre += bits[i] ? 1 : -1;
        auto [it, inserted] = first.try_emplace(pre, i);
        if (!inserted) best = max(best, i - it->second);
    }
    return best;
}
```

## 7. Complexity

| Operation | Time |
|---|---|
| Build 1D/2D prefix | O(n) / O(R·C) |
| Range-sum query | O(1) |
| Range add (difference array) | O(1), plus an O(n) final pass |
| Count subarrays with sum k | O(n) expected (hash map), or O(n log n) with a sorted map |

## 8. Common mistakes

- **Off-by-one errors.** Use `P` of size `n+1`, and `sum(l..r) = P[r+1] − P[l]`.
- **`int` overflow.** Prefix sums of 10⁶ values up to 10⁹ need `long long`.
- **Forgetting `seen[0] = 1`** (or `first[0] = −1`).
- **Updating the map before querying it.** For sum k = 0 you would count the empty subarray. Query first, then insert.
- **Negative modulo** used as a key without normalisation.
- **Using a sliding window when values can be negative.**

## 9. Interview questions

> [!INTERVIEW] "Count subarrays with sum k when the numbers can be negative."
> A sliding window fails, because validity isn't monotone with negatives. Use prefix sums: a subarray (l, r] has sum P[r] − P[l]. While scanning, count the earlier prefixes equal to P[r] − k in a hash map, seeded with {0: 1} for the empty prefix. That's O(n) expected time and O(n) space.

> [!EXAM] How do you apply q range-add updates to an array of size n and then print the array, in O(n + q)?
> Use a difference array D: for each update (l, r, v), do D[l] += v and D[r+1] −= v. Then a single prefix-sum pass over D gives the total added at each position.

## Check your understanding

1. Using `P = [0, 3, 4, 8, 9, 14]`, what is the sum of `a[1..3]`?
2. Why does the hash map approach query `pre − k` *before* inserting `pre`?
3. How would you count subarrays whose sum is divisible by 5?

<details><summary>Answers</summary>

1. P[4] − P[1] = 9 − 3 = 6 (that's 1 + 4 + 1).
2. Inserting first would let a subarray of length 0 match itself when k = 0, which counts an empty subarray.
3. Store the counts of `pre mod 5` (normalised to 0..4). Two prefixes with the same remainder bound a subarray whose sum is divisible by 5. Seed the map with remainder 0 → 1.

</details>
