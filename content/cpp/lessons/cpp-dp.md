# Dynamic Programming

Dynamic programming in C++ is the same mathematics as in the Python DP lessons (states, transitions, order, answer), but the implementation choices change the outcome. C++ fits tables of 10⁸ cells in memory and time when they're laid out well: flat vectors, `int` instead of `long long` where possible, rolling arrays, the right loop order for the cache, and bitsets that process 64 states per instruction. This lesson presents the classic DPs in idiomatic C++ with those optimisations.

## 1. Table layout and memory

```cpp
// 2-D table as one flat allocation: cache-friendly, single new/delete
int R = 5000, C = 5000;
vector<int> dp((size_t)R * C);
auto at = [&](int r, int c) -> int& { return dp[(size_t)r * C + c]; };
```

| Table | Memory |
|---|---|
| 5000 × 5000 `int` | 100 MB |
| 5000 × 5000 `long long` | 200 MB |
| two rolling rows of 5000 `long long` | 80 KB |

Rolling rows, or a 1-D array with the right iteration direction, are usually the difference between "memory limit exceeded" and accepted.

## 2. Memoisation in C++

```cpp
// top-down with a cache array; sentinel -1 = not computed
vector<long long> memo(n + 1, -1);
auto f = [&](this auto&& self, int i) -> long long {      // C++23 deducing this
    if (i <= 1) return 1;
    long long& r = memo[i];
    if (r != -1) return r;
    return r = self(i - 1) + self(i - 2);
};
```

Before C++23, use `std::function<long long(int)>` (slower, heap allocation) or pass the lambda to itself (`auto f = [&](auto&& self, int i) { ... }; f(f, n);`). Recursion depth is bounded by the stack (often 8 MB, about 10⁵ frames). Prefer bottom-up for deep chains.

## 3. Knapsack family

```cpp
// 0/1 knapsack, O(nW) time, O(W) memory
vector<long long> best(W + 1, 0);
for (int i = 0; i < n; ++i)
    for (int w = W; w >= wt[i]; --w)               // descending: each item once
        best[w] = max(best[w], best[w - wt[i]] + val[i]);

// subset sum with std::bitset: 64 sums per machine word
bitset<100001> reach;
reach[0] = 1;
for (int x : a) reach |= reach << x;
bool can = reach[target];
```

`std::bitset` needs a compile-time size. For runtime sizes, use `vector<uint64_t>` with manual shifts, or a template recursion over size classes. The bitset version of subset sum is about 64× faster than the boolean-array loop.

## 4. LIS in O(n log n)

```cpp
int lis(const vector<int>& a, bool strict = true) {
    vector<int> tails;
    for (int x : a) {
        auto it = strict ? lower_bound(tails.begin(), tails.end(), x)
                         : upper_bound(tails.begin(), tails.end(), x);
        if (it == tails.end()) tails.push_back(x); else *it = x;
    }
    return tails.size();
}
```

## 5. Strings: LCS and edit distance with rolling rows

```cpp
int edit_distance(const string& s, const string& t) {
    int n = s.size(), m = t.size();
    vector<int> prev(m + 1), cur(m + 1);
    iota(prev.begin(), prev.end(), 0);
    for (int i = 1; i <= n; ++i) {
        cur[0] = i;
        for (int j = 1; j <= m; ++j)
            cur[j] = s[i - 1] == t[j - 1] ? prev[j - 1]
                                          : 1 + min({prev[j - 1], prev[j], cur[j - 1]});
        swap(prev, cur);                             // O(1): swaps the buffers, not the elements
    }
    return prev[m];
}
```

`std::min({a, b, c})` takes an initializer list. `swap` on vectors exchanges the internal pointers, so it's constant time.

## 6. Bitmask DP

```cpp
// TSP (Held–Karp), n <= 20: dp[mask][v]
const int INF = 1e9;
vector<vector<int>> dp(1 << n, vector<int>(n, INF));
dp[1][0] = 0;
for (int mask = 1; mask < (1 << n); mask += 2)             // masks containing city 0
    for (int v = 0; v < n; ++v) {
        if (dp[mask][v] == INF) continue;
        for (int u = 0; u < n; ++u)
            if (!(mask >> u & 1))
                dp[mask | 1 << u][u] = min(dp[mask | 1 << u][u], dp[mask][v] + dist[v][u]);
    }
```

For n = 20, that's 2²⁰ · 20 · 20 ≈ 4·10⁸ simple operations, which fits in about 1 s in C++ (never in Python). Use `__builtin_popcount(mask)` and `__builtin_ctz(mask)` (or C++20 `std::popcount`/`std::countr_zero` from `<bit>`) for bit tricks.

## 7. Interval DP and loop order

```cpp
// matrix chain: dp[i][j] over increasing length
for (int len = 2; len <= n; ++len)
    for (int i = 0; i + len - 1 < n; ++i) {
        int j = i + len - 1;
        long long best = LLONG_MAX;
        for (int k = i; k < j; ++k)
            best = min(best, dp[i][k] + dp[k + 1][j] + 1LL * d[i] * d[k + 1] * d[j + 1]);
        dp[i][j] = best;
    }
```

**Knuth's optimisation** (when the optimal split points are monotone, as in optimal BSTs and stone merging) reduces some O(n³) interval DPs to O(n²). **Divide-and-conquer optimisation** and the **convex hull trick** speed up certain transition forms. These are advanced techniques worth knowing exist.

## 8. Counting modulo a prime

```cpp
const int MOD = 1'000'000'007;
// ways to climb n stairs with steps from set S, mod p
vector<int> ways(n + 1, 0);
ways[0] = 1;
for (int i = 1; i <= n; ++i)
    for (int s : S) if (s <= i) { ways[i] += ways[i - s]; if (ways[i] >= MOD) ways[i] -= MOD; }
```

A conditional subtraction instead of `%` after every addition is a cheap speed-up. Products need 64-bit: `1LL * a * b % MOD`.

## 9. Exam-ready answers

> [!EXAM]
> **Space optimisation in dynamic programming.** When each row (or layer) of a DP table depends only on a bounded number of previous rows, the table can be replaced by that many rolling arrays, reducing memory from O(n·m) to O(m) without changing the time complexity. For one-dimensional reformulations, such as the 0/1 knapsack array indexed by capacity, the iteration order determines semantics: iterating capacities in decreasing order reads only values from the previous item, while increasing order allows an item to be reused. The trade-off is that reconstructing an optimal solution generally requires the full table, or additional techniques such as Hirschberg's divide and conquer.

## 10. Cheat sheet

| Need | C++ idiom |
|---|---|
| big 2-D table | flat `vector<int>`, `r * C + c` |
| two rows | `vector` + `swap(prev, cur)` |
| subset sums | `bitset<N>`, `reach \|= reach << x` |
| memoised recursion | a lambda with deducing this (C++23) |
| min of 3 | `min({a, b, c})` |
| bit tricks | `std::popcount`, `std::countr_zero` |
| mod add | conditional subtract |

> [!INTERVIEW]
> **"Your DP is correct but MLEs with a 10⁴ × 10⁴ `long long` table. What now?"** Check whether row i depends only on row i − 1. If so, use two rows (O(m)) or a single row with the correct iteration direction. Shrink the type (`int` instead of `long long` when the values fit, `char`/`bitset` for booleans). And question whether the whole state space is needed: maybe only the states reachable from the start (memoisation), or a different state definition, will do.
