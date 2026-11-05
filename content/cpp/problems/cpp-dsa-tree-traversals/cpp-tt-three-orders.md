---
id: cpp-tt-three-orders
title: Preorder, Inorder and Postorder by Recursion
difficulty: Easy
order: 1
tags: binary tree, dfs, recursion, traversal
time_limit: 2
---
## Statement
Write the three depth-first traversals recursively:

```cpp
vector<int> preorder(TreeNode* root);    // node, left subtree, right subtree
vector<int> inorder(TreeNode* root);     // left subtree, node, right subtree
vector<int> postorder(TreeNode* root);   // left subtree, right subtree, node
```

For the tree `5 1 2 3 # 4` (1 with children 2 and 3; 4 is the right child of 2): preorder is `1 2 4 3`, inorder is `2 4 1 3`, postorder is `4 2 3 1`.

The three functions differ only in **where the node's own value is recorded** relative to the two recursive calls. Use a helper that appends into a vector passed by reference, so that you don't copy vectors at every level.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input. Each case is a line `pre`, `in` or `post`, then a tree line. Up to 2·10⁵ nodes per tree, values fit in `int`.

**Output:** the traversal on one line. Lists of more than 60 numbers are printed as `count=C hash=H` (a fingerprint), shorter ones in full; an empty list prints `(none)`.

Trees can be degenerate chains of up to 2·10⁵ nodes. The driver runs your code on a thread with a 256 MB stack, so plain recursion is safe here (on a normal 8 MB stack it would not be).

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

vector<int> preorder(TreeNode* root) { return {}; }
vector<int> inorder(TreeNode* root) { return {}; }
vector<int> postorder(TreeNode* root) { return {}; }
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
        TreeNode* root = rd_tree();
        vector<int> v = cmd == "pre" ? preorder(root) : cmd == "in" ? inorder(root) : postorder(root);
        cout << show_vec(v) << '\n';
        free_tree(root);
    }
    return 0;
}
```

## Tests
=== sample
pre
5 1 2 3 # 4
in
5 1 2 3 # 4
post
5 1 2 3 # 4
---
1 2 4 3
2 4 1 3
4 2 3 1
=== hidden
pre
0
in
1 7
post
7 1 2 3 4 5 6 7
in
7 1 2 # 3 # 4 #
pre
9 8 # 3 # -1 # 6 # 2
post
11 4 9 0 5 1 # # # # # 7
---
(none)
7
4 5 2 6 7 3 1
4 3 2 1
8 3 -1 6 2
5 7 1 9 0 4
=== hidden
in
16 -27 -1 17 # -24 34 -25 # # # # # 23 -33 # 10
post
6 -17 33 # 5 # 41
post
1 -20
pre
10 -47 -1 13 20 -12 3 35 -1 -1 -34
post
11 -16 # -15 47 # 43 14 # # # 22
pre
0
---
-1 -24 -27 34 17 -25 10 -33 23
41 5 33 -17
-20
-47 -1 20 -1 -1 -12 -34 13 3 35
43 22 14 47 -15 -16
(none)
=== hidden
in
4 -21 # 26 -12
in
16 33 -36 # -22 # -39 # -2 # 11 # -28 # 1 # -14
in
12 47 13 # -45 # 39 # -11 # 29 # -14
post
10 29 -31 # # -14 -24 # # 38 40
in
14 -45 -38 34 -10 49 13 # # # 20 # # # -28
in
7 -21 0 -49 47 -12 -1 -23
---
-21 -12 26
-14 1 -28 11 -2 -39 -22 -36 33
-14 29 -11 39 -45 13 47
40 38 -24 -14 -31 29
-10 -38 -28 20 49 -45 13 34
47 0 -12 -21 -1 -49 -23
=== hidden
pre
11 -33 # 11 # 15 # 47 # -34 # 28
in
4 -29 0 6 3
post
12 -15 13 # 2 -36 # -8 # # -49 # 37
post
7 -12 20 -14 # # -48 50
pre
2 45 49
pre
9 19 39 13 # # 11 -47 # -28
---
-33 11 15 47 -34 28
3 0 -29 6
37 -49 -8 2 -36 13 -15
20 -48 50 -14 -12
45 49
19 39 13 11 -28 -47
=== hidden
@gen 2509940669 big
=== hidden
@gen 2509940670 big
=== hidden
@gen 2509940671 big

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
for _ in range(6 if not big else 3):
    n = r.randint(0, 12) if not big else 200000
    vals, L, R = rand_tree(n, -50, 50) if not big else rand_tree(n, -10**9, 10**9)
    print(r.choice(["pre", "in", "post"]))
    print(tline(vals, L, R))
```

## Hints
- Write a helper `void go(TreeNode* n, vector<int>& out)` whose base case is `if (!n) return;`.
- The three orders only move the line `out.push_back(n->val)` relative to the two recursive calls.
- Check yourself on a single node and on a chain: the order of the base case and the push matters.

## Solution
Each traversal is the same recursion: handle the empty tree (base case), recurse into the left subtree, recurse into the right subtree. The only difference is when the current value is appended: **before** both calls (preorder), **between** them (inorder), or **after** both (postorder).

Passing one output vector by reference into a helper avoids building and concatenating a new vector at every node, which would cost O(n²) on a chain.

Complexity: O(n) time (each node is visited once), O(h) stack for a tree of height h, which is O(n) for a chain.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

static void pre_rec(TreeNode* n, vector<int>& out) {
    if (!n) return;                 // empty subtree: nothing to record
    out.push_back(n->val);          // node first
    pre_rec(n->left, out);
    pre_rec(n->right, out);
}
static void in_rec(TreeNode* n, vector<int>& out) {
    if (!n) return;
    in_rec(n->left, out);
    out.push_back(n->val);          // node between the subtrees
    in_rec(n->right, out);
}
static void post_rec(TreeNode* n, vector<int>& out) {
    if (!n) return;
    post_rec(n->left, out);
    post_rec(n->right, out);
    out.push_back(n->val);          // node last
}

vector<int> preorder(TreeNode* root) { vector<int> v; pre_rec(root, v); return v; }
vector<int> inorder(TreeNode* root) { vector<int> v; in_rec(root, v); return v; }
vector<int> postorder(TreeNode* root) { vector<int> v; post_rec(root, v); return v; }
```
