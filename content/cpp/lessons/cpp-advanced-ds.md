# Segment Trees, Fenwick Trees and Tries

Range-query structures are a staple of performance C++: order books, leaderboards, interval scheduling, offline query processing and competitive programming. This lesson gives production-quality C++ implementations:
- a Fenwick tree, as a template
- an iterative segment tree, generic over a monoid
- a lazy segment tree
- a sparse table
- a trie, with both array-of-children and map-based nodes
- GCC's policy-based order-statistics tree

The concepts are explained in the Python Segment/Fenwick and Tries lessons.

## 1. Fenwick tree (template)

```cpp
template <class T>
struct Fenwick {
    int n; vector<T> t;
    explicit Fenwick(int n) : n(n), t(n + 1, T{}) {}
    void add(int i, T d) { for (++i; i <= n; i += i & -i) t[i] += d; }
    T prefix(int i) const { T s{}; for (; i > 0; i -= i & -i) s += t[i]; return s; }   // [0, i)
    T range(int l, int r) const { return prefix(r) - prefix(l); }                     // [l, r)
    int lower_bound(T k) const {          // smallest i with prefix(i + 1) >= k (counts must be non-negative)
        int pos = 0;
        for (int pw = std::bit_floor((unsigned)n); pw; pw >>= 1)
            if (pos + pw <= n && t[pos + pw] < k) { pos += pw; k -= t[pos]; }
        return pos;                       // 0-based index
    }
};
```

`lower_bound` on a Fenwick tree of counts gives the **k-th smallest element** in O(log n) by binary lifting (`std::bit_floor` is from `<bit>`, C++20).

## 2. Generic iterative segment tree

```cpp
template <class T, class Op>
struct SegTree {
    int n; vector<T> t; T id; Op op;
    SegTree(const vector<T>& a, T identity, Op op) : n(a.size()), t(2 * a.size(), identity), id(identity), op(op) {
        copy(a.begin(), a.end(), t.begin() + n);
        for (int i = n - 1; i > 0; --i) t[i] = op(t[2 * i], t[2 * i + 1]);
    }
    void set(int i, T v) { for (t[i += n] = v; i > 1; i >>= 1) t[i >> 1] = op(t[i & ~1], t[i | 1]); }
    T query(int l, int r) const {                      // [l, r), order-preserving
        T L = id, R = id;
        for (l += n, r += n; l < r; l >>= 1, r >>= 1) {
            if (l & 1) L = op(L, t[l++]);
            if (r & 1) R = op(t[--r], R);
        }
        return op(L, R);
    }
};

SegTree st(vector<long long>{5, 2, 8, 1, 9}, LLONG_MAX, [](long long a, long long b) { return min(a, b); });
```

Class template argument deduction (C++17) infers `T` and `Op` from the constructor arguments, so a lambda can be passed directly.

> [!KEY]
> The operation must be **associative** and have an **identity** (a monoid): sum/0, min/+∞, max/−∞, gcd/0, matrix product/identity matrix. Commutativity isn't required, because the separate `L`/`R` accumulators preserve order.

## 3. Lazy segment tree (range add, range min/sum)

```cpp
struct LazySeg {
    int n; vector<long long> mn, sum, lz;
    explicit LazySeg(int n) : n(n), mn(4 * n, 0), sum(4 * n, 0), lz(4 * n, 0) {}
    void apply(int x, int len, long long v) { mn[x] += v; sum[x] += v * len; lz[x] += v; }
    void push(int x, int lo, int hi) {
        if (!lz[x]) return;
        int mid = (lo + hi) / 2;
        apply(2 * x, mid - lo, lz[x]); apply(2 * x + 1, hi - mid, lz[x]); lz[x] = 0;
    }
    void add(int l, int r, long long v, int x, int lo, int hi) {
        if (r <= lo || hi <= l) return;
        if (l <= lo && hi <= r) { apply(x, hi - lo, v); return; }
        push(x, lo, hi);
        int mid = (lo + hi) / 2;
        add(l, r, v, 2 * x, lo, mid); add(l, r, v, 2 * x + 1, mid, hi);
        mn[x] = min(mn[2 * x], mn[2 * x + 1]); sum[x] = sum[2 * x] + sum[2 * x + 1];
    }
    pair<long long, long long> query(int l, int r, int x, int lo, int hi) {   // (sum, min)
        if (r <= lo || hi <= l) return {0, LLONG_MAX};
        if (l <= lo && hi <= r) return {sum[x], mn[x]};
        push(x, lo, hi);
        int mid = (lo + hi) / 2;
        auto [s1, m1] = query(l, r, 2 * x, lo, mid);
        auto [s2, m2] = query(l, r, 2 * x + 1, mid, hi);
        return {s1 + s2, min(m1, m2)};
    }
    void add(int l, int r, long long v) { add(l, r, v, 1, 0, n); }
    pair<long long, long long> query(int l, int r) { return query(l, r, 1, 0, n); }
};
```

Allocating `4n` nodes is the standard safe bound for a recursive segment tree on arbitrary n.

## 4. Sparse table

```cpp
struct SparseMin {
    vector<vector<int>> sp;
    explicit SparseMin(const vector<int>& a) {
        int n = a.size(), K = __lg(n) + 1;
        sp.assign(K, a);
        for (int k = 1; k < K; ++k)
            for (int i = 0; i + (1 << k) <= n; ++i)
                sp[k][i] = min(sp[k - 1][i], sp[k - 1][i + (1 << (k - 1))]);
    }
    int query(int l, int r) const {                 // [l, r), r > l
        int k = __lg(r - l);
        return min(sp[k][l], sp[k][r - (1 << k)]);
    }
};
```

## 5. Tries in C++

```cpp
struct Trie {
    struct Node { array<int, 26> next; int cnt = 0; bool end = false; Node() { next.fill(-1); } };
    vector<Node> t{1};                              // node 0 = root; index-based: no pointers to invalidate
    void insert(const string& s) {
        int cur = 0;
        for (char ch : s) {
            int c = ch - 'a';
            if (t[cur].next[c] < 0) { t[cur].next[c] = t.size(); t.emplace_back(); }
            cur = t[cur].next[c];
            ++t[cur].cnt;
        }
        t[cur].end = true;
    }
    int count_prefix(const string& p) const {
        int cur = 0;
        for (char ch : p) { cur = t[cur].next[ch - 'a']; if (cur < 0) return 0; }
        return t[cur].cnt;
    }
};
```

> [!WARNING]
> In `insert`, don't keep a reference like `Node& node = t[cur]` across `t.emplace_back()`, because reallocation invalidates it. The code above re-indexes `t[cur]` after each push. Array-of-26 nodes are fast but memory hungry (about 110 bytes per node). For large alphabets, use `unordered_map<char,int>` or sorted small vectors of (char, child) pairs.

**Binary trie for max XOR**: `array<int, 2> next` per node, with 31 levels per number.

## 6. Policy-based order statistics (GCC)

```cpp
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>
using namespace __gnu_pbds;
template <class T>
using ordered_set = tree<T, null_type, less<T>, rb_tree_tag, tree_order_statistics_node_update>;

ordered_set<int> os;
os.insert(5); os.insert(1); os.insert(9);
*os.find_by_order(1);        // 5  (the k-th smallest, 0-based)
os.order_of_key(6);          // 2  (number of elements < 6)
```

For a multiset, store pairs `(value, unique_id)`. This GCC extension isn't standard C++, but it's invaluable in contests.

## 7. Exam-ready answers

> [!EXAM]
> **Segment trees in C++.** A segment tree over n elements can be stored in an array of 2n nodes (iteratively, with leaves at positions n to 2n − 1 and node i's children at 2i and 2i + 1) or up to 4n nodes (recursively, for arbitrary n). Each internal node holds the combination of its children under an associative operation with an identity element, so point updates recompute the O(log n) ancestors and range queries combine O(log n) canonical nodes. Range updates are supported by lazy propagation, where a node fully covered by an update records a pending tag that is pushed to its children only when they are next accessed. Generic implementations take the value type and operation as template parameters.

## 8. Cheat sheet

| Need | Structure |
|---|---|
| prefix sums with updates | `Fenwick<long long>` |
| k-th smallest with updates | Fenwick + binary lifting, or a pbds tree |
| range min/max/gcd + point updates | iterative `SegTree` |
| range add + range sum/min | `LazySeg` |
| static RMQ | `SparseMin` |
| prefix counting | index-based trie |
| rank / select on a set | `__gnu_pbds::tree` |

> [!INTERVIEW]
> **"Iterative or recursive segment tree?"** The iterative bottom-up version (2n nodes) is shorter, faster (no recursion, better locality) and perfect for point updates with range queries over any monoid. The recursive version is easier to extend with lazy propagation, segment-tree descent ("first index where the prefix sum ≥ k") and persistence. Pick based on the operations required.
