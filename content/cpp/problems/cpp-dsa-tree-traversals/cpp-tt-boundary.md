---
id: cpp-tt-boundary
title: Boundary Traversal
difficulty: Hard
order: 8
tags: binary tree, traversal, boundary, case analysis
time_limit: 2
---
## Statement
Return the **boundary** of the tree, anticlockwise, starting at the root, with no node listed twice:

```cpp
vector<int> boundary(TreeNode* root);
```

The boundary is the concatenation of:

1. **the root**;
2. **the left boundary** without the root and without leaves: start at `root->left`; from each node go to its left child if it has one, otherwise to its right child; stop before a leaf. If the root has no left child, this part is empty;
3. **all leaves, left to right** (the root is not a leaf here, even if it has no children; a lone root is listed once, in part 1);
4. **the right boundary, reversed**, without the root and without leaves: start at `root->right` and prefer right children, defined symmetrically.

```text
            1
          /   \             root:            1
         2     3            left boundary:   2 4
        / \     \           leaves:          7 8 5 9 10
       4   5     6          right boundary:  6 3   (reversed)
      / \       / \
     7   8     9   10       answer: 1 2 4 7 8 5 9 10 6 3
```

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input, one tree line each. Up to 2·10⁵ nodes. Trees can be chains of 2·10⁵ nodes, so don't recurse that deep.

**Output:** the boundary on one line. Lists of more than 60 numbers are printed as `count=C hash=H` (a fingerprint), shorter ones in full; an empty list prints `(none)`.

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

vector<int> boundary(TreeNode* root) { return {}; }
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
        TreeNode* root = rd_tree();
        cout << show_vec(boundary(root)) << '\n';
        free_tree(root);
    }
    return 0;
}
```

## Tests
=== sample
13 1 2 3 4 5 # 6 7 8 # # 9 10
---
1 2 4 7 8 5 9 10 6 3
=== sample
9 1 # 2 3 4 # # 5 6
---
1 3 5 6 4 2
=== hidden
0
---
(none)
=== hidden
1 7
---
7
=== hidden
2 1 2
---
1 2
=== hidden
3 1 # 2
---
1 2
=== hidden
7 1 2 # 3 # 4 #
---
1 2 3 4
=== hidden
5 1 2 # # 3
---
1 2 3
=== hidden
7 1 2 3 4 5 6 7
---
1 2 4 5 6 7 3
=== hidden
0
0
2 70 79
4 68 96 90 14
21 52 42 # # 47 58 63 57 72 0 # # # 5 50 # # # # # 9
18 89 82 # 30 # 26 # 16 # 14 # 96 # 98 # 75 # 3
---
(none)
(none)
70 79
68 96 14 90
52 42 47 58 57 5 9 0
89 82 30 26 16 14 96 98 75 3
=== hidden
10 50 63 87 94 32 89 98 43 85 39
25 66 # 44 # 11 # 25 # 69 # 95 # 78 # 51 # 74 # 70 # 92 # 92 # 62
21 95 51 # # 81 45 # # 68 85 # # 9 48 # # 94 70 # # 25
0
11 73 29 65 15 7 24 52 35 91 99 51
5 69 23 90 66 24
---
50 63 94 43 85 39 89 98 87
66 62 92 92 70 74 51 78 95 69 25 11 44
95 51 81 45 68 85 9 48 94 70 25
(none)
73 29 15 35 91 99 51 24 52 65
69 23 66 24 90
=== hidden
14 70 47 # 9 # 54 # 32 # 30 # 37 # 14
5 10 # 14 # 96
14 84 7 9 87 # 80 # # # 72 # 81 # 74
0
9 13 18 58 # # 49 # # 55
9 13 46 49 99 15 52 62 90 92
---
70 47 9 54 32 30 37 14
10 96 14
84 7 87 74 81 72 80 9
(none)
13 18 55 49 58
13 46 99 90 92 15 52 62 49
=== hidden
@gen 1243706837 big
=== hidden
@gen 1243706838 big
=== hidden
@gen 1243706839 big

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
    n = r.randint(0, 14) if not big else 200000
    vals, L, R = rand_tree(n, 0, 99) if not big else rand_tree(n, 0, 1000, r.choice(["random", "complete", "deep", "zigzag", "left", "right"]))
    print(tline(vals, L, R))
```

## Hints
- Produce four separate lists: root, left boundary, leaves, right boundary. Then concatenate.
- Both boundary walks stop before a leaf, so leaves are counted only once.
- Edge cases: a lone root, a root without a left child, and a left boundary that has to step right.

## Solution
Split the boundary into four disjoint parts and produce each with a simple walk:

- **Left boundary:** walk from `root->left`, preferring left children, and stop as soon as you reach a leaf, because leaves belong to part 3.
- **Leaves:** any traversal that visits left before right lists them left to right. An explicit-stack preorder avoids deep recursion.
- **Right boundary:** walk from `root->right` preferring right children, again stopping at a leaf, then append the collected values in reverse (bottom-up, which is anticlockwise).

The disjointness is what prevents duplicates: the root is only in part 1 (part 3 skips it even when it has no children), and the boundary walks stop before leaves. A missing `root->left` makes the left boundary empty. It does **not** mean the walk switches to the right side, which is the most common bug.

Complexity: O(n) time, O(h) memory for the leaf stack.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

static bool is_leaf(TreeNode* n) { return !n->left && !n->right; }

vector<int> boundary(TreeNode* root) {
    vector<int> res;
    if (!root) return res;
    res.push_back(root->val);
    // 2. left boundary, top-down, without leaves
    for (TreeNode* n = root->left; n && !is_leaf(n); n = n->left ? n->left : n->right)
        res.push_back(n->val);
    // 3. leaves, left to right (iterative preorder with left before right)
    if (!is_leaf(root)) {
        vector<TreeNode*> st{root};
        while (!st.empty()) {
            TreeNode* n = st.back(); st.pop_back();
            if (is_leaf(n)) res.push_back(n->val);
            if (n->right) st.push_back(n->right);
            if (n->left) st.push_back(n->left);
        }
    }
    // 4. right boundary, collected top-down then appended reversed
    vector<int> right;
    for (TreeNode* n = root->right; n && !is_leaf(n); n = n->right ? n->right : n->left)
        right.push_back(n->val);
    res.insert(res.end(), right.rbegin(), right.rend());
    return res;
}
```
