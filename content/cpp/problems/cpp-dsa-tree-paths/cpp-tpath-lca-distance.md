---
id: cpp-tpath-lca-distance
title: Lowest Common Ancestor and Node Distance
difficulty: Medium
order: 5
tags: binary tree, lca, recursion, distance
time_limit: 2
---
## Statement
Values are distinct, and both queried values are always in the tree.

```cpp
TreeNode* lca(TreeNode* root, int p, int q);   // the deepest node that has both p and q in its subtree
int distance(TreeNode* root, int p, int q);    // number of edges on the path between p and q
```

A node counts as its own descendant, so if `p` is an ancestor of `q`, the answer is `p`.

```text
           3            lca(5, 1) = 3      distance(5, 1) = 2
         /   \          lca(5, 4) = 5      distance(5, 4) = 2
        5     1         lca(6, 4) = 5      distance(6, 4) = 3
       / \   / \        lca(7, 7) = 7      distance(7, 7) = 0
      6   2 0   8
         / \
        7   4
```

The classic recursion returns, for each subtree, "the node that answers the question inside this subtree": `p` or `q` if exactly one of them was found, the LCA if both were, `nullptr` if neither. If both the left and right calls return non-null, the current node is the split point. For the distance, `dist(p, q) = depth(p) + depth(q) − 2·depth(lca)`, or measure the two downward distances from the LCA.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input. Each case is a tree line, then a line `k` (1 ≤ k ≤ 10), then `k` lines `p q`. Up to 2·10⁵ nodes. Each query may walk the whole tree.

Trees can be degenerate chains of up to 2·10⁵ nodes. The driver runs your code on a thread with a 256 MB stack, so plain recursion is safe here (on a normal 8 MB stack it would not be).

**Output:** for each query, a line `lca distance`.

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

TreeNode* lca(TreeNode* root, int p, int q) { return root; }
int distance(TreeNode* root, int p, int q) { return p == q ? 0 : 1; }
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
        TreeNode* root = rd_tree();
        int k = (int)rd_ll();
        while (k--) {
            int p = (int)rd_ll(), q = (int)rd_ll();
            TreeNode* a = lca(root, p, q);
            int d = distance(root, p, q);
            cout << (a ? to_string(a->val) : string("null")) << ' ' << d << '\n';
        }
        free_tree(root);
    }
    return 0;
}
```

## Tests
=== sample
11 3 5 1 6 2 0 8 # # 7 4
4
5 1
5 4
6 4
7 7
---
3 2
5 2
5 3
7 0
=== hidden
1 9
1
9 9
---
9 0
=== hidden
5 1 2 # 3 #
3
1 3
3 2
2 1
---
1 2
2 1
1 1
=== hidden
7 1 2 3 4 5 6 7
3
4 7
4 5
6 3
---
1 4
2 2
3 1
=== hidden
3 -1 # -2147483648
1
-2147483648 -1
---
-1 1
=== hidden
19 -11 -4 16 -3 -26 # # -22 # 21 9 # # # -6 11 # # -8
2
-3 21
-26 9
25 28 # -18 # -11 # 21 # -30 # -21 # 3 # -9 # 23 # -8 # 8 # -15 # -25
1
-15 -18
4 -1 # 8 -30
4
-30 -1
8 -1
-30 -30
-30 -1
13 13 -13 # 6 20 -10 # # # -3 29 -27 14
1
-27 29
13 9 -1 # # 27 -26 # # -29 -6 # # 17
4
-6 9
-26 -29
17 -26
9 9
5 12 -27 # # -8
4
-8 -27
-8 -27
-27 -27
-8 -8
---
-4 3
-26 1
-18 10
-1 2
-1 1
-30 0
-1 2
-10 3
9 5
-26 1
-26 3
9 0
-27 1
-27 1
-27 0
-8 0
=== hidden
26 17 -2 # # 27 -28 # # 9 26 # # -30 5 # # -13 11 # # -9 -4 # # -21 -7
3
5 -7
-2 26
17 -4
3 -30 4 -10
1
-30 -10
20 3 -24 # # -6 13 10 # # 5 # -27 14 # # -11 # -3 # 12
4
13 3
-27 5
13 -11
5 14
12 -3 19 -26 8 # 21 # -11 # # # 20
3
-11 20
-3 8
8 21
3 6 # 7
4
6 7
6 7
6 7
6 7
5 20 19 # # -21
3
20 19
20 -21
20 19
---
5 6
-2 4
17 11
-30 1
3 3
5 1
-6 5
5 1
-11 1
-3 2
-3 4
6 1
6 1
6 1
6 1
20 1
20 2
20 1
=== hidden
5 2 0 # # 8
2
8 2
2 0
11 23 -10 -18 # 11 # -21 # -29 # 15
3
23 -21
-29 -29
-18 15
24 28 14 # 26 # 8 # -29 # -1 # -15 # 4 # -3 # -30 # -4 # -5 # -7
2
-4 8
-30 -3
11 11 3 21 # # -22 25 # # # -28
3
11 -28
25 11
-22 11
24 9 -21 # -23 # 29 # -24 # 28 # -29 # -14 # 26 # -7 # -3 # 15 # 19
1
9 -21
10 -6 3 -28 -19 29 13 -14 -5 23 14
2
-14 -6
-14 -19
---
2 2
2 1
23 2
-29 0
-18 2
8 7
-3 1
11 3
11 2
11 2
9 1
-6 2
-6 4
=== hidden
@gen 819084317 big
=== hidden
@gen 819084318 big
=== hidden
@gen 819084319 big

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
for _ in range(6 if not big else 2):
    n = r.randint(1, 14) if not big else 200000
    L, R = shape(n, r.choice(KINDS))
    vals = r.sample(range(-10**9, 10**9) if big else range(-30, 30), n)
    print(tline(vals, L, R))
    k = r.randint(1, 4) if not big else 10
    print(k)
    for _ in range(k): print(r.choice(vals), r.choice(vals))
```

## Hints
- Base case: an empty tree, or a node that is p or q, returns itself.
- If the left and right recursive calls both return something, the current node is the LCA.
- Distance = edges from the LCA down to p + edges from the LCA down to q.

## Solution
**LCA.** Define `lca(n)` as: "if both `p` and `q` are in `n`'s subtree, return their LCA; if exactly one is, return that node; otherwise null."

- If `n` itself is `p` or `q`, return `n`. Either the other value is below it (so `n` is the LCA), or it is elsewhere and an ancestor will combine the results.
- Otherwise recurse left and right. Two non-null results mean `p` and `q` were found on different sides, so `n` is the deepest node above both. One non-null result is passed up unchanged.

This relies on both values being present. If one could be missing, the function would return the other one as a false LCA, and you'd need to verify both exist.

**Distance.** Every path between two nodes goes up to their LCA and down again, so the distance is (LCA → p) + (LCA → q), each found by a downward search from the LCA.

Complexity: O(n) per query, O(h) recursion depth. (For many queries, precompute depths and binary-lifting tables: O(log n) per query. That comes later in the course.)

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

TreeNode* lca(TreeNode* root, int p, int q) {
    if (!root || root->val == p || root->val == q) return root;   // found one (or nothing here)
    TreeNode* l = lca(root->left, p, q);
    TreeNode* r = lca(root->right, p, q);
    if (l && r) return root;          // p and q are on different sides: root is the split point
    return l ? l : r;                 // pass up whatever was found
}

// depth (in edges) of value v below n, or -1 if absent
static int depth_of(TreeNode* n, int v, int d) {
    if (!n) return -1;
    if (n->val == v) return d;
    int l = depth_of(n->left, v, d + 1);
    return l >= 0 ? l : depth_of(n->right, v, d + 1);
}

int distance(TreeNode* root, int p, int q) {
    TreeNode* a = lca(root, p, q);
    return depth_of(a, p, 0) + depth_of(a, q, 0);   // down from the LCA to each node
}
```
