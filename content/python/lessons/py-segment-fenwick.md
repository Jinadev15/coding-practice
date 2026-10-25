# Segment Trees and Fenwick Trees

Prefix sums answer range queries in O(1), but only on **static** data. When elements change between queries (live sensor buffers, order books, game leaderboards, online judges counting inversions), you need structures that support both **updates and range queries in O(log n)**. The two workhorses are the **Fenwick tree** (binary indexed tree), which is tiny, fast and ideal for prefix sums with point updates, and the **segment tree**, which handles any associative operation (sum, min, max, gcd), range updates with lazy propagation, and custom merges.

## 1. The problem

| Structure | Point update | Range query | Range update | Build |
|---|---|---|---|---|
| plain array | O(1) | O(n) | O(n) | O(n) |
| prefix sums | O(n) | O(1) | O(n) | O(n) |
| Fenwick tree | O(log n) | O(log n) (invertible ops) | O(log n) via a difference trick | O(n) |
| segment tree | O(log n) | O(log n) (any associative op) | O(log n) with lazy propagation | O(n) |
| sparse table | — (static) | O(1) (idempotent ops: min/max/gcd) | — | O(n log n) |

## 2. Fenwick tree (binary indexed tree)

Index i (1-based) stores the sum of the range `(i − lowbit(i), i]`, where `lowbit(i) = i & -i` is the value of the lowest set bit.

```python
class Fenwick:
    def __init__(self, n):
        self.n = n
        self.t = [0] * (n + 1)

    def add(self, i, delta):            # a[i] += delta  (0-based i)
        i += 1
        while i <= self.n:
            self.t[i] += delta
            i += i & -i                 # move to the next node that covers i

    def prefix(self, i):                # sum of a[0..i-1]
        s = 0
        while i > 0:
            s += self.t[i]
            i -= i & -i                 # strip the lowest set bit
        return s

    def range_sum(self, l, r):          # sum of a[l..r-1]
        return self.prefix(r) - self.prefix(l)
```

> [!KEY]
> Both loops touch at most ⌈log₂ n⌉ + 1 nodes: `prefix` removes one set bit per step, and `add` climbs through the nodes whose ranges include i. A Fenwick tree needs the operation to be **invertible** (subtraction exists) for range queries. Sum and XOR work. Min and max don't, except for prefix-min with only decreasing updates.

**O(n) build**: copy the array into `t[1..n]`, then for each i, add `t[i]` into `t[i + lowbit(i)]`.

### Classic uses

- **Counting inversions**: scan from the right, and for each value count the smaller values already seen (`prefix(rank)`), then `add(rank, 1)`. That's O(n log n) after coordinate compression.
- **Range update, point query**: store a difference array in the Fenwick tree. `add(l, v)` and `add(r, -v)`, then the point value is `prefix(i + 1)`.
- **Order statistics**: the k-th smallest present value, by binary lifting over the tree in O(log n).
- **2-D Fenwick**: counts in sub-rectangles of a grid with updates, O(log² n).

## 3. Segment tree

A binary tree over the array. Each node stores the aggregate of a segment, and the children split it in half. An iterative bottom-up version (size `2n`, leaves at `n..2n-1`) is short and fast in Python:

```python
class SegTree:
    def __init__(self, a, op=min, identity=float("inf")):
        self.n = n = len(a)
        self.op, self.e = op, identity
        self.t = [identity] * n + list(a)
        for i in range(n - 1, 0, -1):
            self.t[i] = op(self.t[2 * i], self.t[2 * i + 1])

    def update(self, i, value):          # a[i] = value
        i += self.n
        self.t[i] = value
        while i > 1:
            i //= 2
            self.t[i] = self.op(self.t[2 * i], self.t[2 * i + 1])

    def query(self, l, r):               # aggregate of a[l..r-1]
        resl = resr = self.e
        l += self.n; r += self.n
        while l < r:
            if l & 1:
                resl = self.op(resl, self.t[l]); l += 1
            if r & 1:
                r -= 1; resr = self.op(self.t[r], resr)
            l //= 2; r //= 2
        return self.op(resl, resr)

st = SegTree([5, 2, 8, 1, 9])
st.query(1, 4)     # 1 = min(2, 8, 1)
st.update(3, 7)
st.query(1, 4)     # 2
```

Keeping `resl` and `resr` separate preserves the left-to-right order, so **non-commutative** operations work too (matrix products, string concatenation, "max subarray sum" node merges).

### Custom node merges

Segment trees shine when the node holds a small structure. Example: the **maximum subarray sum in a range** stores `(total, best_prefix, best_suffix, best)` per node:

```python
def merge(a, b):
    tot = a[0] + b[0]
    pre = max(a[1], a[0] + b[1])
    suf = max(b[2], b[0] + a[2])
    best = max(a[3], b[3], a[2] + b[1])
    return (tot, pre, suf, best)
```

Other node types: the count of distinct values in some offline problems, (min, count of min), sorted lists ("merge sort tree" for k-th smallest in a range), hashes for substring comparison.

## 4. Lazy propagation: range updates

To support "add v to every element in [l, r)" plus range sums in O(log n), each node keeps a **pending** update that hasn't been pushed to its children yet:

```python
class LazySegTree:                       # range add, range sum (recursive for clarity)
    def __init__(self, n):
        self.n = n
        self.sum = [0] * (4 * n)
        self.lazy = [0] * (4 * n)

    def _apply(self, node, length, v):
        self.sum[node] += v * length
        self.lazy[node] += v

    def _push(self, node, lo, mid, hi):
        if self.lazy[node]:
            self._apply(2 * node, mid - lo, self.lazy[node])
            self._apply(2 * node + 1, hi - mid, self.lazy[node])
            self.lazy[node] = 0

    def add(self, l, r, v, node=1, lo=0, hi=None):
        hi = self.n if hi is None else hi
        if r <= lo or hi <= l:
            return
        if l <= lo and hi <= r:
            self._apply(node, hi - lo, v)          # fully covered: stop here, remember the pending add
            return
        mid = (lo + hi) // 2
        self._push(node, lo, mid, hi)
        self.add(l, r, v, 2 * node, lo, mid)
        self.add(l, r, v, 2 * node + 1, mid, hi)
        self.sum[node] = self.sum[2 * node] + self.sum[2 * node + 1]

    def query(self, l, r, node=1, lo=0, hi=None):
        hi = self.n if hi is None else hi
        if r <= lo or hi <= l:
            return 0
        if l <= lo and hi <= r:
            return self.sum[node]
        mid = (lo + hi) // 2
        self._push(node, lo, mid, hi)
        return self.query(l, r, 2 * node, lo, mid) + self.query(l, r, 2 * node + 1, mid, hi)
```

The recursion depth is only log₂ n (about 20), so recursion is safe here. Lazy tags compose (add after add, assign then add), and getting that composition right is the main difficulty in "range assign + range add" variants.

## 5. Sparse table: O(1) static range min

For **idempotent** operations (min, max, gcd: overlapping doesn't matter), precompute `sp[k][i]` = the aggregate of `a[i .. i + 2^k)`. A query covers [l, r) with two overlapping power-of-two blocks:

```python
def build_sparse(a):
    sp = [a[:]]
    k = 1
    while (1 << k) <= len(a):
        prev = sp[-1]
        half = 1 << (k - 1)
        sp.append([min(prev[i], prev[i + half]) for i in range(len(a) - (1 << k) + 1)])
        k += 1
    return sp

def range_min(sp, l, r):                 # [l, r), r > l
    k = (r - l).bit_length() - 1
    return min(sp[k][l], sp[k][r - (1 << k)])
```

That's O(n log n) to build and O(1) per query, used for LCA via an Euler tour and in suffix-array LCP queries.

## 6. Coordinate compression

Values up to 10⁹ but only n of them? Map them to ranks 0..n−1 first: `rank = {v: i for i, v in enumerate(sorted(set(vals)))}`. Then build the tree over ranks. That's essential for inversion counting, "count smaller after self", and sweep-line problems.

## 7. Exam-ready answers

> [!EXAM]
> **Fenwick trees and segment trees.** A Fenwick (binary indexed) tree stores, at index i, the sum of a range of length equal to the lowest set bit of i, so that point updates and prefix sums each traverse O(log n) indices by repeatedly adding or removing the lowest set bit; range sums are differences of prefix sums. A segment tree is a binary tree whose nodes store an associative aggregate (sum, minimum, maximum and so on) of contiguous segments; any range decomposes into O(log n) nodes, giving O(log n) queries and point updates, and lazy propagation defers range updates to children until needed, giving O(log n) range updates. Fenwick trees are simpler and more compact, while segment trees support non-invertible and non-commutative operations and richer node data.

## 8. Cheat sheet

| Need | Structure |
|---|---|
| prefix/range sums + point updates | Fenwick |
| range add + point query | Fenwick on differences |
| range min/max + point updates | segment tree |
| range add/assign + range sum/min | lazy segment tree |
| static range min, many queries | sparse table |
| inversions / count smaller | Fenwick + coordinate compression |
| max subarray in a range | segment tree with 4-tuple nodes |

> [!INTERVIEW]
> **"Count, for each element, how many smaller elements are to its right."** Compress the values to ranks, scan from right to left, and use a Fenwick tree of counts: the answer for a[i] is `prefix(rank[a[i]])` (the ranks strictly smaller), then `add(rank[a[i]], 1)`. That's O(n log n). An alternative is merge sort, counting the right-half elements that move ahead of each left element. Mention both, and compare memory and constant factors.
