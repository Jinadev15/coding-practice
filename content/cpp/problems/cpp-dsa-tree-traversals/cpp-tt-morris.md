---
id: cpp-tt-morris
title: Morris Traversal in O(1) Extra Space
difficulty: Medium
order: 4
tags: binary tree, morris traversal, threaded tree, constant space
time_limit: 2
---
## Statement
Traverse a tree with **no stack and no recursion**, using O(1) extra memory besides the output:

```cpp
vector<int> morris_inorder(TreeNode* root);
vector<int> morris_preorder(TreeNode* root);
```

The trick (Morris, 1979): before descending into `cur->left`, find `cur`'s **inorder predecessor** `pred` (the rightmost node of the left subtree) and set the temporary "thread" `pred->right = cur`. When the walk later arrives back at `cur` through that thread, you know the left subtree is finished: remove the thread and move right.

**The tree must be exactly as it was when your function returns.** The driver checks this and prints `TREE MODIFIED` otherwise.

Trees can be chains of 5·10⁵ nodes, and your code runs on the **normal 8 MB stack**: a recursive solution overflows it and crashes. Use an explicit stack (or no stack at all).

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input. Each case is a line `in` or `pre`, then a tree line. Up to 5·10⁵ nodes per tree.

**Output:** the traversal on one line (Lists of more than 60 numbers are printed as `count=C hash=H` (a fingerprint), shorter ones in full; an empty list prints `(none)`.), followed by `TREE MODIFIED` on its own line if the tree changed.

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

vector<int> morris_inorder(TreeNode* root) { return {}; }
vector<int> morris_preorder(TreeNode* root) { return {}; }
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
int main() { return real_main(); }   // the normal 8 MB stack: deep recursion crashes here
static int real_main() {
    load_input();
    while (more()) {
        string cmd = rd_str();
        TreeNode* root = rd_tree();
        string before = show_tree(root, NODES_);
        vector<int> v = cmd == "in" ? morris_inorder(root) : morris_preorder(root);
        cout << show_vec(v) << '\n';
        bool ok = true;
        string after = show_tree(root, NODES_, &ok);
        if (after != before) cout << "TREE MODIFIED\n";
        if (ok) free_tree(root);
        else return 0;   // a cycle was left behind: freeing would loop
    }
    return 0;
}
```

## Tests
=== sample
in
5 1 2 3 # 4
---
2 4 1 3
=== sample
pre
5 1 2 3 # 4
---
1 2 4 3
=== hidden
in
0
---
(none)
=== hidden
pre
1 5
---
5
=== hidden
in
7 4 2 6 1 3 5 7
---
1 2 3 4 5 6 7
=== hidden
pre
7 4 2 6 1 3 5 7
---
4 2 1 3 6 5 7
=== hidden
in
7 1 2 # 3 # 4 #
---
4 3 2 1
=== hidden
pre
9 1 # 2 # 3 # 4 # 5
---
1 2 3 4 5
=== hidden
pre
4 -43 # 49 12
pre
4 -11 -36 -21 -42
pre
2 43 -19
in
0
in
9 8 9 -31 6 -44 -40 -10 45 44
pre
9 -22 -37 # # 5 -2 # # 32
---
-43 49 12
-11 -36 -42 -21
43 -19
(none)
45 6 44 9 -44 8 -40 -31 -10
-22 -37 5 -2 32
=== hidden
pre
9 -9 -12 -35 -20 -22 39 32 36 -22
pre
5 49 -18 22 -19 5
in
17 -21 1 -11 23 # # 29 -48 # # # 39 20 # 48 11 21
pre
7 16 43 -2 # # # -21
in
2 -26 29
in
11 -30 # -21 # 19 # 44 # -18 # 25
---
-9 -12 -20 36 -22 -22 -35 39 32
49 -18 -19 5 22
39 48 -48 11 20 21 23 1 -21 -11 29
16 43 -2 -21
29 -26
-30 -21 19 44 -18 25
=== hidden
pre
2 28 50
pre
3 38 # -4
in
6 -18 20 -17 # 48 13
pre
1 -22
in
13 -27 # 41 # -13 # 49 # -8 # -11 # 41
in
8 -15 16 -35 48 # # 7 -34
---
28 50
38 -4
20 48 -18 13 -17
-22
-27 41 -13 49 -8 -11 41
-34 48 16 -15 -35 7
=== hidden
@gen 807406809 big
=== hidden
@gen 807406810 big
=== hidden
@gen 807406811 big

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
if not big:
    for _ in range(6):
        vals, L, R = rand_tree(r.randint(0, 12), -50, 50)
        print(r.choice(["in", "pre"])); print(tline(vals, L, R))
else:
    kind = r.choice(["left", "zigzag", "deep", "random"])
    vals, L, R = rand_tree(500000, 0, 999, kind)
    print(r.choice(["in", "pre"])); print(tline(vals, L, R))
```

## Hints
- If `cur` has no left child, record it (both orders) and move to `cur->right`.
- Otherwise, find the rightmost node of `cur->left`, stopping early if its `right` already points to `cur`.
- No thread yet: create it and go left. Thread found: delete it and go right. Inorder records at the second step, preorder at the first.

## Solution
A recursive or stack-based traversal remembers "where to return to" after the left subtree. Morris stores that information **inside the tree**: the rightmost node of the left subtree (the inorder predecessor) has an unused `right` pointer, so it temporarily points back to `cur`.

Every node with a left child is reached twice:

1. **First arrival:** the predecessor's `right` is `nullptr`. Create the thread and go left.
2. **Second arrival** (following the thread): the predecessor's `right == cur`. Remove the thread, and go right.

Inorder records a node on the second arrival (its left subtree is finished), preorder on the first. Nodes without a left child are recorded once and the walk goes right, which may be a thread.

**Why O(n) time:** finding predecessors walks down right spines of left subtrees. Each edge is walked at most a constant number of times (twice per thread: once to create it and once to remove it), so the total is O(n).

Complexity: O(n) time, O(1) extra memory. The tree is restored exactly because every thread created is removed on the second arrival.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

vector<int> morris_inorder(TreeNode* root) {
    vector<int> out;
    TreeNode* cur = root;
    while (cur) {
        if (!cur->left) {                    // nothing on the left: visit, go right
            out.push_back(cur->val);
            cur = cur->right;
            continue;
        }
        TreeNode* pred = cur->left;          // rightmost node of the left subtree
        while (pred->right && pred->right != cur) pred = pred->right;
        if (!pred->right) {                  // first arrival: leave a thread back to cur
            pred->right = cur;
            cur = cur->left;
        } else {                             // second arrival (via the thread): left side is done
            pred->right = nullptr;           // restore the tree
            out.push_back(cur->val);
            cur = cur->right;
        }
    }
    return out;
}

vector<int> morris_preorder(TreeNode* root) {
    vector<int> out;
    TreeNode* cur = root;
    while (cur) {
        if (!cur->left) {
            out.push_back(cur->val);
            cur = cur->right;
            continue;
        }
        TreeNode* pred = cur->left;
        while (pred->right && pred->right != cur) pred = pred->right;
        if (!pred->right) {
            out.push_back(cur->val);         // preorder: record on the FIRST arrival
            pred->right = cur;
            cur = cur->left;
        } else {
            pred->right = nullptr;
            cur = cur->right;
        }
    }
    return out;
}
```
