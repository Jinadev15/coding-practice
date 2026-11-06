---
id: cpp-tc-bst-from-preorder
title: BST from Preorder in Linear Time
difficulty: Medium
order: 5
tags: binary search tree, construction, bounds, monotonic stack
time_limit: 2
---
## Statement
Given the preorder traversal of a **binary search tree** with distinct values, rebuild the tree:

```cpp
TreeNode* bst_from_preorder(const vector<int>& pre);
```

For a BST, the preorder alone is enough, because the inorder is just the sorted values. `8 5 1 7 10 12` gives:

```text
        8
       / \
      5   10
     / \    \
    1   7    12
```

Inserting the values one by one into an empty BST gives the right tree, but costs O(n²) when the input is sorted (every insertion walks the whole chain). Get **O(n)**:

- **Bounds:** `build(bound)` consumes the next preorder value only if it is below `bound`. The left subtree of a node `v` gets bound `v`, and the right subtree inherits the parent's bound. Each value is consumed exactly once.
- Or a **monotonic stack** of the current path (see the solution).

**Input:** cases until the end of input. Each case is a line `n` (1 ≤ n ≤ 2·10⁵), then the preorder. Values are distinct and fit in `int`, and the input is always a valid BST preorder.

Trees can be degenerate chains of up to 2·10⁵ nodes. The driver runs your code on a thread with a 256 MB stack, so plain recursion is safe here (on a normal 8 MB stack it would not be).

**Output:** the tree, one line per case.

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

TreeNode* bst_from_preorder(const vector<int>& pre) { return nullptr; }
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
        int n = (int)rd_ll();
        vector<int> pre(n);
        for (int& x : pre) x = (int)rd_ll();
        TreeNode* root = bst_from_preorder(pre);
        bool ok = true;
        cout << show_tree(root, n, &ok) << '\n';
        if (ok) free_tree(root);
        else return 0;
    }
    return 0;
}
```

## Tests
=== sample
6
8 5 1 7 10 12
---
8 5 10 1 7 # 12
=== hidden
1
2147483647
---
2147483647
=== hidden
3
3 2 1
---
3 2 # 1
=== hidden
3
1 2 3
---
1 # 2 # 3
=== hidden
5
4 2 -2147483648 3 2147483647
---
4 2 2147483647 -2147483648 3
=== hidden
7
50 30 20 40 70 60 80
---
50 30 70 20 40 60 80
=== hidden
8
-23 -28 27 -19 -7 -16 24 16
10
-21 -11 -20 -10 5 -5 26 9 16 19
3
6 -5 21
2
-30 -18
10
-25 -21 -17 -15 -7 -3 -2 2 19 27
---
-23 -28 27 # # -19 # # -7 -16 24 # # 16
-21 # -11 -20 -10 # # # 5 -5 26 # # 9 # # 16 # 19
6 -5 21
-30 # -18
-25 # -21 # -17 # -15 # -7 # -3 # -2 # 2 # 19 # 27
=== hidden
4
-24 -22 25 -10
10
25 -28 22 -26 14 -24 13 -14 8 3
6
27 -23 25 -16 3 -6
11
29 22 20 10 -2 -6 -7 -10 -18 -20 -23
10
26 20 13 10 3 1 -5 -20 -25 -29
---
-24 # -22 # 25 -10
25 -28 # # 22 -26 # # 14 -24 # # 13 -14 # # 8 3
27 -23 # # 25 -16 # # 3 -6
29 22 # 20 # 10 # -2 # -6 # -7 # -10 # -18 # -20 # -23
26 20 # 13 # 10 # 3 # 1 # -5 # -20 # -25 # -29
=== hidden
2
-9 -12
5
-30 -23 -21 -17 17
8
-26 -23 -22 -21 -18 -14 6 15
3
20 -23 16
7
-8 -10 -20 -13 11 1 26
---
-9 -12
-30 # -23 # -21 # -17 # 17
-26 # -23 # -22 # -21 # -18 # -14 # 6 # 15
20 -23 # # 16
-8 -10 11 -20 # 1 26 # -13
=== hidden
@gen 2822311452 big
=== hidden
@gen 2822311453 big
=== hidden
@gen 2822311454 big

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
def pre_of(vals, L, R):
    out, st = [], [0] if vals else []
    while st:
        u = st.pop(); out.append(vals[u])
        if R[u] >= 0: st.append(R[u])
        if L[u] >= 0: st.append(L[u])
    return out
for _ in range(5 if not big else 2):
    n = r.randint(1, 12) if not big else 200000
    L, R = shape(n, r.choice(KINDS))
    vals = bst_vals(L, R, r.sample(range(-10**9, 10**9) if big else range(-30, 30), n))
    print(n); print(*pre_of(vals, L, R))
```

## Hints
- The first value is the root. Which of the following values go into its left subtree?
- Write `build(bound)`: it takes the next value only if it is smaller than `bound`.
- Left child: bound = the node's value. Right child: the bound inherited from the parent. Use a `long long` bound.

## Solution
In a BST preorder, a node is followed by its whole left subtree (all values smaller than it) and then its whole right subtree (values larger than it but smaller than the nearest ancestor for which this node is in the left subtree). That ancestor's value is the **upper bound**.

`build(bound)` looks at the next unused value. If it is not below `bound`, it doesn't belong in this subtree, so return null without consuming it. Otherwise make it a node, build its left subtree with bound = its value, and its right subtree with the inherited bound. The shared index `i` advances once per created node, so the total work is O(n).

The bound is a `long long` starting at `LLONG_MAX`, so that `INT_MAX` itself can be a value.

**Monotonic-stack version (no recursion):** keep the path of nodes whose right child is still open, as a stack with decreasing values from bottom to top. For each new value, pop every node smaller than it; the last popped node gets the new value as its **right** child. If nothing was popped, the new value is the **left** child of the top. Then push it. Each node is pushed and popped once: O(n).

Complexity: O(n) time, O(h) stack.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

// builds the subtree made of the next preorder values that are < bound
static TreeNode* build(const vector<int>& pre, size_t& i, long long bound) {
    if (i == pre.size() || pre[i] >= bound) return nullptr;   // next value belongs to an ancestor's right side
    TreeNode* n = new TreeNode(pre[i++]);
    n->left = build(pre, i, n->val);      // everything smaller than this node, until a larger value appears
    n->right = build(pre, i, bound);      // then values between this node and the inherited bound
    return n;
}

TreeNode* bst_from_preorder(const vector<int>& pre) {
    size_t i = 0;
    return build(pre, i, LLONG_MAX);
}
```
