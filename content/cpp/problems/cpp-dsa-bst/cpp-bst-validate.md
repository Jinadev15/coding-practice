---
id: cpp-bst-validate
title: Validate a BST with Bounds
difficulty: Medium
order: 3
tags: binary search tree, validation, bounds, inorder
time_limit: 2
---
## Statement
Is the tree a valid BST? Every node must be **strictly** greater than **all** values in its left subtree and strictly smaller than **all** values in its right subtree (so no duplicates):

```cpp
bool is_valid_bst(TreeNode* root);
```

```text
      5            NOT a BST, although every node is correct relative to its parent:
     / \           4 is in the RIGHT subtree of 5, but 4 < 5.
    1   7
       / \
      4   8
```

Checking only `left->val < node->val < right->val` misses exactly that case. Two correct approaches:

- **Bounds:** pass down an open interval `(lo, hi)` that every value in the subtree must lie in. Going left sets `hi = node->val`; going right sets `lo = node->val`. Values can be `INT_MIN` and `INT_MAX`, so use `long long` bounds (or "no bound" flags), never `INT_MIN`/`INT_MAX` as sentinels.
- **Inorder:** a BST's inorder sequence is strictly increasing. Compare each visited value with the previous one.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input, one tree line each. Up to 2·10⁵ nodes, values fit in `int`.

Trees can be degenerate chains of up to 2·10⁵ nodes. The driver runs your code on a thread with a 256 MB stack, so plain recursion is safe here (on a normal 8 MB stack it would not be).

**Output:** `true` or `false` per case.

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

bool is_valid_bst(TreeNode* root) {
    // compares each node with its children only: misses violations deeper down
    if (!root) return true;
    if (root->left && root->left->val >= root->val) return false;
    if (root->right && root->right->val <= root->val) return false;
    return is_valid_bst(root->left) && is_valid_bst(root->right);
}
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
        cout << (is_valid_bst(root) ? "true" : "false") << '\n';
        free_tree(root);
    }
    return 0;
}
```

## Tests
=== sample
7 5 1 7 # # 4 8
---
false
=== sample
3 2 1 3
---
true
=== hidden
0
---
true
=== hidden
1 -2147483648
---
true
=== hidden
3 2147483647 # 2147483647
---
false
=== hidden
3 -2147483648 # 2147483647
---
true
=== hidden
3 1 1 #
---
false
=== hidden
7 10 5 15 # # 6 20
---
false
=== hidden
7 10 5 15 1 11 12 20
---
false
=== hidden
7 3 1 5 0 2 4 6
---
true
=== hidden
18 18 -19 # # 17 -14 # # 15 -3 # # 6 3 # # 5 4
6 4 -7 # # 1 1
17 16 12 19 10 # # # 3 # 1 4 -9 # # # -4 -15
12 1 -13 12 -18 -1 6 17 -20 -15 -8 0 5
9 -17 # 1 -16 6 # # 1 13
13 4 -6 14 -14 -2 8 19 -16 -12 -5 0 6 10
2 -5 19
8 6 1 7 -10 # # # -11
3 -11 -8 -17
9 -13 -19 -6 # # # -1 # 9
---
true
false
false
true
false
true
false
true
false
true
=== hidden
18 6 -17 13 -18 4 # 17 # # -14 5 # # # -8 # # -13
3 -15 # -15
13 16 -19 # # -8 -9 # # 7 -8 # # 6
5 13 -20 # # -8
9 18 -13 # # 12 -11 # # -6
25 19 -19 # # 14 19 # # 13 -12 # # 10 -10 # # 2 -7 # # -2 -5 # # -3
6 13 -17 -14 # # -3
8 -2 -3 # # -16 -10 # -11
19 -20 # -1 -11 10 -12 -10 3 13 -19 # # -3 5 0 # # # -15
16 15 10 # 6 # 4 # -3 # -4 # -6 # -16 # -17
---
true
false
false
true
true
false
false
false
false
true
=== hidden
3 -17 -17 14
1 -14
5 6 6 # # 2
20 -7 -8 18 -18 # 11 # -20 -17 -4 14 # # # -9 -5 -3 # # -14
13 -15 # -14 # -11 -12 -5 # # # 1 # 15
10 2 -11 8 -18 1 5 14 -20 -14 -5
19 -11 # -5 # -1 # 17 # 2 # 3 # 5 # 8 # 1 # 19
15 -17 # -7 -14 17 # -13 15 # # # 3 # # 5
21 19 -20 # # 10 -18 # # 6 -15 # # 4 -14 # # 0 -13 # # -11
22 -2 -3 16 -6 # 3 # -20 # # 10 # 16 4 # -19 -10 # # # # -13
---
false
true
false
true
true
true
false
true
true
false
=== hidden
@gen 2268291735 big
=== hidden
@gen 2268291736 big
=== hidden
@gen 2268291737 big

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
    n = r.randint(1, 13) if not big else 200000
    L, R = shape(n, r.choice(KINDS))
    vals = bst_vals(L, R, r.sample(range(-10**9, 10**9) if big else range(-20, 20), n))
    k = r.random()
    if n >= 2 and k < 0.3:
        i, j = r.sample(range(n), 2); vals[i], vals[j] = vals[j], vals[i]
    elif n >= 2 and k < 0.5:
        i, j = r.sample(range(n), 2); vals[i] = vals[j]
    elif k < 0.6:
        i = r.randrange(n); vals[i] += r.choice([-1, 1])
    print(tline(vals, L, R))
```

## Hints
- A node must be compared with all its ancestors, not only its parent. Which ancestors give the tightest limits?
- Pass an open interval (lo, hi) down: the left child gets (lo, val), the right child gets (val, hi).
- Values may be `INT_MIN` or `INT_MAX`: use `long long` bounds that start outside that range.

## Solution
The BST property is about **whole subtrees**, not just children. Every ancestor constrains a node: if the node is in the left subtree of `a`, it must be below `a`; if in the right subtree of `b`, above `b`. The tightest of these constraints form an interval `(lo, hi)`, which is exactly what the recursion passes down. Going left tightens `hi`, going right tightens `lo`.

Using `long long` bounds that start outside the `int` range means `INT_MIN` and `INT_MAX` are legal values. A version that starts with `INT_MIN` and uses strict comparisons wrongly rejects a node with value `INT_MIN`.

**Equivalent check:** inorder traversal must be strictly increasing. That needs only a "previous value" variable and works iteratively too.

Complexity: O(n) time, O(h) recursion depth.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

// every value in n's subtree must lie strictly inside (lo, hi)
static bool ok(TreeNode* n, long long lo, long long hi) {
    if (!n) return true;
    if (n->val <= lo || n->val >= hi) return false;
    return ok(n->left, lo, n->val) && ok(n->right, n->val, hi);
}

bool is_valid_bst(TreeNode* root) { return ok(root, LLONG_MIN, LLONG_MAX); }
```
