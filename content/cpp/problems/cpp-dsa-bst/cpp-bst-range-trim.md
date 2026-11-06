---
id: cpp-bst-range-trim
title: Range Sum and Trimming with Pruning
difficulty: Medium
order: 8
tags: binary search tree, pruning, range query, trim
time_limit: 2
---
## Statement
Two range operations that use the BST order to **skip whole subtrees**:

```cpp
long long range_sum(TreeNode* root, int lo, int hi);   // sum of the values in [lo, hi]
TreeNode* trim(TreeNode* root, int lo, int hi);        // remove every node outside [lo, hi]; return the new root
```

`trim` must keep the relative structure of the remaining nodes (if a kept node was below another kept node, it stays below it) and must `delete` every removed node.

```text
trim to [3, 6]:        5                    5
                     /   \                 / \
                    2     8      ──►      3   6
                   / \   / \               \
                  1   3 6   9               4
                       \
                        4
```

Pruning: if `node->val < lo`, the node **and its whole left subtree** are out of range. Only its right subtree can contribute, and for `trim` that subtree replaces the node. Symmetrically for `> hi`.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input. Each case is a line `sum lo hi` or `trim lo hi` (lo ≤ hi), then a tree line (a valid BST with distinct values). Up to 2·10⁵ nodes. Big trees are random-shaped or chains.

Trees can be degenerate chains of up to 2·10⁵ nodes. The driver runs your code on a thread with a 256 MB stack, so plain recursion is safe here (on a normal 8 MB stack it would not be).

**Output:** for `sum`, the sum. For `trim`, the trimmed tree.

**Tree format (output).** The driver prints a returned tree as its level-order tokens without the count (`1 2 3 # 4`), `empty` for no nodes, and `nodes=N hash=H` (a fingerprint of the same tokens) when there would be more than 60 tokens.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

long long range_sum(TreeNode* root, int lo, int hi) { return 0; }
TreeNode* trim(TreeNode* root, int lo, int hi) { return root; }
```

## Driver
```cpp
// ===== driver helpers (iterative everywhere, so 10^6-deep chains are safe) =====
#include <pthread.h>
static string IN_; static size_t POS_ = 0;
static void load_input() { static char buf[1 << 16]; size_t k; while ((k = fread(buf, 1, sizeof buf, stdin)) > 0) IN_.append(buf, k); }
[[maybe_unused]] static bool tok(string_view& t) {
    while (POS_ < IN_.size() && isspace((unsigned char)IN_[POS_])) ++POS_;
    if (POS_ >= IN_.size()) return false;
    size_t b = POS_;
    while (POS_ < IN_.size() && !isspace((unsigned char)IN_[POS_])) ++POS_;
    t = string_view(IN_).substr(b, POS_ - b);
    return true;
}
[[maybe_unused]] static long long num(string_view t) {
    long long x = 0; size_t i = (t[0] == '-');
    for (; i < t.size(); ++i) x = x * 10 + (t[i] - '0');
    return t[0] == '-' ? -x : x;
}
[[maybe_unused]] static bool more() { string_view t; size_t save = POS_; bool ok = tok(t); POS_ = save; return ok; }
[[maybe_unused]] static long long rd_ll() { string_view t; tok(t); return num(t); }
[[maybe_unused]] static string rd_str() { string_view t; tok(t); return string(t); }
static long long NODES_ = 0;   // nodes created by rd_tree (an upper bound for sanity checks)
// tree: "k t1 .. tk" in level order, '#' = missing child
[[maybe_unused]] static TreeNode* rd_tree() {
    long long k = rd_ll();
    vector<string_view> t(k);
    for (auto& x : t) tok(x);
    if (k == 0 || t[0] == "#") return nullptr;
    TreeNode* root = new TreeNode((int)num(t[0])); ++NODES_;
    vector<TreeNode*> q{root}; size_t h = 0, i = 1;
    while (h < q.size() && i < t.size()) {
        TreeNode* p = q[h++];
        if (i < t.size() && t[i] != "#") { p->left = new TreeNode((int)num(t[i])); q.push_back(p->left); ++NODES_; }
        ++i;
        if (i < t.size() && t[i] != "#") { p->right = new TreeNode((int)num(t[i])); q.push_back(p->right); ++NODES_; }
        ++i;
    }
    return root;
}
[[maybe_unused]] static void free_tree(TreeNode* root) {
    vector<TreeNode*> st; if (root) st.push_back(root);
    while (!st.empty()) {
        TreeNode* p = st.back(); st.pop_back();
        if (p->left) st.push_back(p->left);
        if (p->right) st.push_back(p->right);
        delete p;
    }
}
// level-order tokens; returns false if more than `limit` nodes are reachable (a cycle or shared nodes)
[[maybe_unused]] static bool tree_tokens(TreeNode* root, long long limit, vector<long long>& out, long long& cnt) {
    const long long NUL = LLONG_MIN;
    out.clear(); cnt = 0;
    if (!root) return true;
    vector<TreeNode*> q{root}; size_t h = 0; out.push_back(root->val); cnt = 1;
    while (h < q.size()) {
        TreeNode* p = q[h++];
        for (TreeNode* c : {p->left, p->right}) {
            if (!c) { out.push_back(NUL); continue; }
            if (++cnt > limit) return false;
            out.push_back(c->val); q.push_back(c);
        }
    }
    while (!out.empty() && out.back() == NUL) out.pop_back();
    return true;
}
// prints the tree in level order without the count ("empty" for no nodes); more than 60 tokens -> a fingerprint
[[maybe_unused]] static string show_tree(TreeNode* root, long long limit, bool* ok = nullptr) {
    vector<long long> t; long long cnt;
    bool good = tree_tokens(root, limit, t, cnt);
    if (ok) *ok = good;
    if (!good) return "INVALID (cycle or shared nodes)";
    if (t.empty()) return "empty";
    if (t.size() <= 60) {
        string s;
        for (size_t i = 0; i < t.size(); ++i) { if (i) s += ' '; s += t[i] == LLONG_MIN ? string("#") : to_string(t[i]); }
        return s;
    }
    unsigned long long hs = 0;
    for (long long x : t) hs = hs * 1000003ULL + (x == LLONG_MIN ? 977ULL : (unsigned long long)(x + 3000000000LL));
    return "nodes=" + to_string(cnt) + " hash=" + to_string(hs);
}
// a list of numbers: printed in full up to 60 values, otherwise as count + fingerprint
template <class T> [[maybe_unused]] static string show_vec(const vector<T>& v) {
    if (v.empty()) return "(none)";
    string s;
    if (v.size() <= 60) { for (size_t i = 0; i < v.size(); ++i) { if (i) s += ' '; s += to_string(v[i]); } return s; }
    unsigned long long hs = 0;
    for (auto x : v) hs = hs * 1000003ULL + (unsigned long long)((long long)x + 3000000000LL);
    return "count=" + to_string(v.size()) + " hash=" + to_string(hs);
}
static int real_main();
static void* real_main_thread(void*) { real_main(); return nullptr; }
int main() {
    // Recursion over a 2*10^5-deep chain needs more than the default 8 MB stack, so the driver
    // runs everything on a thread with a 256 MB stack.
    pthread_attr_t a; pthread_attr_init(&a); pthread_attr_setstacksize(&a, size_t(256) << 20);
    pthread_t th;
    if (pthread_create(&th, &a, real_main_thread, nullptr) != 0) return real_main();
    pthread_join(th, nullptr);
    return 0;
}
static int real_main() {
    load_input();
    while (more()) {
        string cmd = rd_str();
        int lo = (int)rd_ll(), hi = (int)rd_ll();
        TreeNode* root = rd_tree();
        long long lim = NODES_; NODES_ = 0;
        if (cmd == "sum") {
            cout << range_sum(root, lo, hi) << '\n';
            free_tree(root);
        } else {
            root = trim(root, lo, hi);
            bool ok = true;
            cout << show_tree(root, lim, &ok) << '\n';
            if (ok) free_tree(root);
            else return 0;
        }
    }
    return 0;
}
```

## Tests
=== sample
trim 3 6
11 5 2 8 1 3 6 9 # # # 4
---
5 3 6 # 4
=== sample
sum 3 6
11 5 2 8 1 3 6 9 # # # 4
---
18
=== hidden
sum 0 10
0
---
0
=== hidden
trim 0 10
0
---
empty
=== hidden
trim 1 1
3 2 1 3
---
1
=== hidden
trim 4 9
3 2 1 3
---
empty
=== hidden
sum -2147483648 2147483647
3 2147483647 -2147483648 #
---
-1
=== hidden
trim 2 3
5 1 # 2 # 3
---
2 # 3
=== hidden
trim 1 2
5 3 2 # 1 #
---
2 1
=== hidden
sum 3 3
7 4 2 6 1 3 5 7
---
3
=== hidden
trim -12 5
11 -16 # 4 -4 7 # # # 9 # 11
trim 7 18
6 19 -7 # -14 3 -15
trim -7 3
5 18 -5 # # 8
sum -22 -9
13 -17 -19 6 # -18 -12 8 # # -13 4 # 14
sum 17 19
12 5 -12 19 -19 2 17 # # # 0 3 16
sum -20 22
0
trim 10 10
0
trim -3 21
1 -8
sum -20 -1
9 3 -3 9 -16 2 8 18 -17 -9
sum -6 -2
21 -19 # -13 # -12 # -10 # -9 # -3 # 2 # 6 # 8 # 10 # 14
---
4 -4
empty
-5
-79
36
0
empty
empty
-45
-3
=== hidden
sum -18 -17
6 16 -12 # # 5 -2
trim 6 21
21 -13 # 7 3 13 -11 # # # # 2 0 # -7 1 -9 # # # # -8
sum -18 5
9 8 -5 17 -13 2 12 19 -14 -12
sum -14 -8
0
sum -6 -2
4 10 -10 17 -20
trim -21 -7
1 -12
sum 4 13
1 17
sum 4 12
0
sum 9 16
5 7 -11 14 # 6
sum -18 17
12 -18 # 11 -14 18 # -3 # # -4 4 -6
---
0
7 # 13
-42
0
0
-12
0
0
14
-30
=== hidden
sum -16 -2
6 -6 -10 18 -16 -9 13
sum -1 22
1 17
sum -3 16
15 16 13 17 -11 15 # # -16 5 # # -19 # # 7
sum -2 19
6 7 -12 # # -6 -10
sum 1 5
7 -15 # 4 # 13 # 14
sum 7 20
8 7 2 16 -1 3 12 17 -20
trim -13 1
0
trim -11 12
0
sum -22 15
10 14 -10 # # 13 -8 # # 9 -7
trim -22 -2
2 10 -20
---
-41
17
56
7
4
52
empty
empty
11
-20
=== hidden
@gen 1072729106 big
=== hidden
@gen 1072729107 big
=== hidden
@gen 1072729108 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"

def shape(n, kind="random"):
    """children arrays L, R for nodes 0..n-1 (root 0)"""
    L = [-1] * n; R = [-1] * n
    if kind in ("random", "deep"):
        slots = [(0, 0), (0, 1)] if n else []
        for i in range(1, n):
            j = r.randrange(len(slots)) if kind == "random" else len(slots) - 1 - r.randrange(min(3, len(slots)))
            p, s = slots[j]; slots[j] = slots[-1]; slots.pop()
            (L if s == 0 else R)[p] = i
            slots.append((i, 0)); slots.append((i, 1))
    elif kind == "left":
        for i in range(1, n): L[i - 1] = i
    elif kind == "right":
        for i in range(1, n): R[i - 1] = i
    elif kind == "zigzag":
        for i in range(1, n): (L if i % 2 else R)[i - 1] = i
    elif kind == "complete":
        for i in range(n):
            if 2 * i + 1 < n: L[i] = 2 * i + 1
            if 2 * i + 2 < n: R[i] = 2 * i + 2
    return L, R

KINDS = ["random", "random", "random", "deep", "left", "right", "zigzag", "complete"]

def ser(vals, L, R):
    if not vals: return []
    out = [str(vals[0])]; q = [0]; h = 0
    while h < len(q):
        u = q[h]; h += 1
        for c in (L[u], R[u]):
            if c < 0: out.append("#")
            else: out.append(str(vals[c])); q.append(c)
    while out and out[-1] == "#": out.pop()
    return out

def tline(vals, L, R):
    t = ser(vals, L, R)
    return " ".join([str(len(t))] + t)

def inorder(L, R):
    n = len(L); res = []; st = []; u = 0 if n else -1
    while st or u >= 0:
        while u >= 0: st.append(u); u = L[u]
        u = st.pop(); res.append(u); u = R[u]
    return res

def bst_vals(L, R, keys):
    """assign sorted keys in inorder -> a valid BST of this shape"""
    vals = [0] * len(L)
    for k, u in zip(sorted(keys), inorder(L, R)): vals[u] = k
    return vals

def rand_tree(n, lo, hi, kind=None):
    kind = kind or r.choice(KINDS)
    L, R = shape(n, kind)
    return [r.randint(lo, hi) for _ in range(n)], L, R
for _ in range(10 if not big else 2):
    n = r.randint(0, 12) if not big else 200000
    L, R = shape(n, r.choice(KINDS) if not big else r.choice(["random", "random", "left"]))
    keys = r.sample(range(-10**9, 10**9) if big else range(-20, 20), n)
    vals = bst_vals(L, R, keys)
    a, b = sorted([r.randint(-22, 22), r.randint(-22, 22)]) if not big else sorted([r.randint(-10**9, 10**9), r.randint(-10**9, 10**9)])
    print(r.choice(["sum", "trim"]), a, b); print(tline(vals, L, R))
```

## Hints
- If `val < lo`, can anything in the left subtree be in range?
- For trim, an out-of-range node is replaced by the trimmed version of its one useful subtree.
- Remember to `delete` the removed node and to free the subtree you discard.

## Solution
Both functions use the same observation: when a node is below `lo`, everything in its left subtree is smaller still, so the whole left subtree can be skipped (for the sum) or discarded (for the trim). When it is above `hi`, the same holds for the right subtree.

**Range sum** recurses only into subtrees that can contain in-range values. On a balanced tree it visits O(log n + k) nodes, where k is the number of values reported. The pruning matters most when ranges are narrow.

**Trim** returns the root of the trimmed subtree. If the node is out of range on the low side, the answer is the trimmed right subtree, which takes the node's place in its parent. That keeps the relative order and the ancestor relations of the survivors. If the node is in range, trim both children and keep it. Discarded subtrees are freed with an iterative helper, so a long discarded chain is fine.

Complexity: range sum O(h + k) nodes visited in the pruned search, plus the skipped parts; trim O(n) in the worst case because every removed node must be freed. Recursion depth O(h).

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

long long range_sum(TreeNode* n, int lo, int hi) {
    if (!n) return 0;
    if (n->val < lo) return range_sum(n->right, lo, hi);    // the left subtree is even smaller: skip it
    if (n->val > hi) return range_sum(n->left, lo, hi);
    return n->val + range_sum(n->left, lo, hi) + range_sum(n->right, lo, hi);
}

static void destroy(TreeNode* n) {                           // free a whole removed subtree, iteratively
    vector<TreeNode*> st; if (n) st.push_back(n);
    while (!st.empty()) { TreeNode* p = st.back(); st.pop_back(); if (p->left) st.push_back(p->left); if (p->right) st.push_back(p->right); delete p; }
}

TreeNode* trim(TreeNode* n, int lo, int hi) {
    if (!n) return nullptr;
    if (n->val < lo) {                                       // n and its left subtree are out
        TreeNode* r = n->right;
        destroy(n->left); delete n;
        return trim(r, lo, hi);
    }
    if (n->val > hi) {                                       // n and its right subtree are out
        TreeNode* l = n->left;
        destroy(n->right); delete n;
        return trim(l, lo, hi);
    }
    n->left = trim(n->left, lo, hi);                         // n stays: fix both sides
    n->right = trim(n->right, lo, hi);
    return n;
}
```
