# Hashing and Prefix Sums

Hash maps and prefix sums turn quadratic scans into linear passes. In C++, the details that matter are:
- choosing between `std::unordered_map`, `std::map` and plain arrays
- writing hash functions for custom keys (pairs, tuples, structs)
- avoiding rehash and adversarial-collision slowdowns
- building prefix-sum arrays with the right integer types, using `std::partial_sum` / `std::inclusive_scan`

## 1. Which associative container?

| Container | Lookup | Ordered iteration | Notes |
|---|---|---|---|
| plain `vector<int>` / `array` indexed by key | O(1), fastest | yes | keys small and dense (≤ ~10⁷) |
| `unordered_map` / `unordered_set` | O(1) average | no | node-based, ~2–5× slower than flat maps; `reserve` up front |
| `map` / `set` | O(log n) | yes | needed for lower_bound, ordered traversal, deterministic output |
| sorted `vector` + `lower_bound` | O(log n) | yes | best for build-once/query-many |
| `std::flat_map` (C++23) | O(log n) | yes | a sorted vector under the hood |

## 2. Counting and complement lookup

```cpp
// two-sum: indices of a pair summing to target
optional<pair<int,int>> two_sum(const vector<int>& a, int target) {
    unordered_map<int, int> seen;
    seen.reserve(a.size() * 2);
    for (int i = 0; i < (int)a.size(); ++i) {
        if (auto it = seen.find(target - a[i]); it != seen.end()) return pair{it->second, i};
        seen.emplace(a[i], i);
    }
    return nullopt;
}
```

> [!WARNING]
> `m[key]` **inserts** a default value if the key is missing. In a "does it exist?" check, that silently grows the map (and is illegal on a `const` map). Use `find`, `contains` (C++20) or `count` for lookups, and `m[key]++` only when insertion is intended.

## 3. Hashing custom keys

`std::unordered_map<pair<int,int>, int>` doesn't compile, because there's no `std::hash<pair>`. Provide one:

```cpp
struct PairHash {
    size_t operator()(const pair<int,int>& p) const noexcept {
        uint64_t x = (uint64_t)(uint32_t)p.first << 32 | (uint32_t)p.second;   // pack two ints into 64 bits
        x ^= x >> 33; x *= 0xff51afd7ed558ccdULL; x ^= x >> 33;                 // mix (murmur finaliser)
        return x;
    }
};
unordered_map<pair<int,int>, int, PairHash> grid_cost;

// for a struct: also define operator== (or a defaulted <=>) so the map can compare keys
struct Cell { int r, c; bool operator==(const Cell&) const = default; };
struct CellHash { size_t operator()(Cell k) const noexcept { return PairHash{}({k.r, k.c}); } };
```

Combining hashes with `h1 ^ h2` is weak (symmetric: `(a, b)` and `(b, a)` collide). Pack the fields or use a mixing step, like `boost::hash_combine`'s `seed ^= h + 0x9e3779b9 + (seed << 6) + (seed >> 2)`.

## 4. Prefix sums in C++

```cpp
vector<long long> P(n + 1, 0);
for (int i = 0; i < n; ++i) P[i + 1] = P[i] + a[i];       // explicit and clear
// or: partial_sum(a.begin(), a.end(), P.begin() + 1);    // careful: accumulates in the OUTPUT element type

auto range_sum = [&](int l, int r) { return P[r] - P[l]; };   // [l, r)
```

### Subarray sum equals k (negatives allowed)

```cpp
long long count_subarrays(const vector<int>& a, long long k) {
    unordered_map<long long, int> cnt;
    cnt.reserve(a.size() * 2);
    cnt[0] = 1;
    long long pre = 0, total = 0;
    for (int x : a) {
        pre += x;
        if (auto it = cnt.find(pre - k); it != cnt.end()) total += it->second;
        ++cnt[pre];
    }
    return total;
}
```

### 2-D prefix sums (integral image)

```cpp
vector<vector<long long>> S(R + 1, vector<long long>(C + 1, 0));
for (int i = 0; i < R; ++i)
    for (int j = 0; j < C; ++j)
        S[i + 1][j + 1] = g[i][j] + S[i][j + 1] + S[i + 1][j] - S[i][j];
auto rect = [&](int r1, int c1, int r2, int c2) {          // rows [r1, r2), cols [c1, c2)
    return S[r2][c2] - S[r1][c2] - S[r2][c1] + S[r1][c1];
};
```

### Difference arrays

```cpp
vector<long long> D(n + 1, 0);
for (auto [l, r, v] : updates) { D[l] += v; D[r] -= v; }    // a[l..r-1] += v
partial_sum(D.begin(), D.end() - 1, D.begin());            // D[i] is now a[i]
```

## 5. Modular prefix tricks

"Count subarrays with a sum divisible by m": C++'s `%` keeps the sign of the dividend, so `-3 % 5 == -3`. Normalise with `((x % m) + m) % m` before using it as a key or index:

```cpp
vector<long long> cnt(m, 0);
cnt[0] = 1;
long long pre = 0, ans = 0;
for (int x : a) {
    pre = ((pre + x) % m + m) % m;
    ans += cnt[pre]++;
}
```

## 6. Exam-ready answers

> [!EXAM]
> **std::unordered_map vs std::map.** `std::unordered_map` is a hash table with buckets of nodes, giving average O(1) insertion, lookup and deletion but O(n) worst case, unordered iteration, and iterator invalidation on rehash; it requires a hash function and equality for the key type. `std::map` is a balanced binary search tree (typically red–black), giving O(log n) operations, iteration in key order, and ordered queries such as `lower_bound`, requiring only a strict weak ordering. The hash map is usually faster for pure lookups, while the ordered map is needed for ordered traversal, range queries or worst-case guarantees; for small dense integer keys, a plain array outperforms both.

## 7. Cheat sheet

| Need | C++ |
|---|---|
| lookup without inserting | `m.find(k)`, `m.contains(k)` |
| count | `++m[k]` |
| pair/struct keys | a custom hasher + `operator==` |
| speed | `reserve`, or an array for dense keys |
| prefix sums | `vector<long long> P(n + 1)` |
| non-negative mod | `((x % m) + m) % m` |

> [!INTERVIEW]
> **"Why might your `unordered_map` solution TLE while the same logic in a `vector` passes?"** Node allocation per element, pointer chasing, rehashing as it grows (call `reserve`), a poor or attackable hash (identity hashing of integers lets crafted inputs collide), and a large constant factor compared with direct indexing. Use an array when the keys are dense, a sorted vector for static data, or a flat hash map from a library.
