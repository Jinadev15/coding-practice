---
id: cpp-tc-parent-links
title: Build a Tree from Parent Links
difficulty: Easy
order: 1
tags: binary tree, construction, hash map, root finding
time_limit: 2
---
## Statement
A tree arrives as a list of links, in **arbitrary order**: `(parent, child, is_left)` means the node with value `child` is the left (`is_left = 1`) or right (`is_left = 0`) child of the node with value `parent`. Values are distinct. Build the tree and return its root:

```cpp
TreeNode* build_from_links(const vector<array<int, 3>>& links);   // each link is {parent, child, is_left}
```

Two things to work out: **which node is the root** (the only value that never appears as a child), and how to find the `TreeNode*` for a value in O(1) (a hash map from value to node, creating nodes the first time a value is seen). This is how trees really arrive from databases and file formats: as rows of parent/child pairs (an org chart, a category table, a URDF robot description).

**Input:** cases until the end of input. Each case is a line `m` (1 ≤ m < 2·10⁵, the number of links), then `m` lines `parent child is_left`. Values are distinct positive integers up to 10⁹, and the links always describe one valid binary tree.

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

TreeNode* build_from_links(const vector<array<int, 3>>& links) { return nullptr; }
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
        int m = (int)rd_ll();
        vector<array<int, 3>> links(m);
        for (auto& l : links) for (int& x : l) x = (int)rd_ll();
        TreeNode* root = build_from_links(links);
        bool ok = true;
        cout << show_tree(root, m + 1, &ok) << '\n';
        if (ok) free_tree(root);
        else return 0;
    }
    return 0;
}
```

## Tests
=== sample
4
20 15 1
20 17 0
50 20 1
50 80 0
---
50 20 80 15 17
=== hidden
1
1 2 0
---
1 # 2
=== hidden
1
5 3 1
---
5 3
=== hidden
3
3 4 1
1 2 1
2 3 0
---
1 2 # # 3 4
=== hidden
6
4 6 0
1 2 1
1 3 0
2 4 1
3 5 1
4 7 1
---
1 2 3 4 # 5 # 7 6
=== hidden
9
86 33 0
68 97 0
9 68 1
33 48 1
93 66 1
49 71 1
48 49 0
97 86 1
66 9 0
3
79 77 1
68 79 1
82 68 1
7
59 75 0
17 79 1
79 35 0
75 3 1
35 38 1
3 17 0
49 59 1
7
29 41 0
41 25 1
33 40 1
29 88 1
88 33 1
88 68 0
41 74 0
4
7 2 1
72 93 1
93 7 0
2 16 0
---
93 66 # # 9 68 # # 97 86 # # 33 48 # # 49 71
82 68 # 79 # 77
49 59 # # 75 3 # # 17 79 # # 35 38
29 88 41 33 68 25 74 40
72 93 # # 7 2 # # 16
=== hidden
1
74 76 1
8
80 17 0
87 38 0
17 83 1
38 62 0
87 94 1
62 90 0
17 34 0
90 80 0
7
84 7 0
43 11 0
53 84 1
46 53 0
25 46 1
11 33 1
7 43 1
6
6 26 1
23 6 1
4 24 1
13 23 1
5 4 1
26 5 1
8
1 26 1
34 1 1
34 60 0
14 37 0
37 64 1
14 34 1
37 95 0
1 8 0
---
74 76
87 94 38 # # # 62 # 90 # 80 # 17 83 34
25 46 # # 53 84 # # 7 43 # # 11 33
13 23 # 6 # 26 # 5 # 4 # 24
14 34 37 1 60 64 95 26 8
=== hidden
5
4 45 1
4 27 0
52 34 1
45 94 1
52 4 0
6
92 90 1
19 47 0
90 80 0
26 92 0
19 26 1
47 63 1
4
60 43 0
97 60 1
14 24 0
43 14 1
11
26 60 1
68 18 1
5 96 1
18 26 1
67 8 1
73 5 1
8 73 1
96 62 1
75 68 1
62 75 1
60 95 1
1
51 29 0
---
52 34 4 # # 45 27 94
19 26 47 # 92 63 # 90 # # # # 80
97 60 # # 43 14 # # 24
67 8 # 73 # 5 # 96 # 62 # 75 # 68 # 18 # 26 # 60 # 95
51 # 29
=== hidden
@gen 2466586178 big
=== hidden
@gen 2466586179 big
=== hidden
@gen 2466586180 big

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
for _ in range(5 if not big else 1):
    n = r.randint(2, 12) if not big else 200000
    L, R = shape(n, r.choice(KINDS))
    vals = r.sample(range(1, 10**9 if big else 100), n)
    links = [(vals[u], vals[c], s) for u in range(n) for c, s in ((L[u], 1), (R[u], 0)) if c >= 0]
    r.shuffle(links)
    print(len(links))
    for l in links: print(*l)
```

## Hints
- Keep `unordered_map<int, TreeNode*>`: look a value up, and create the node only if it isn't there yet.
- Every link sets exactly one pointer: `parent->left` or `parent->right`.
- The root never appears in the "child" column.

## Solution
Two passes over the links:

1. **Wire the nodes.** A hash map from value to node creates each node exactly once, the first time its value appears, either as a parent or as a child. That is why the order of the links doesn't matter: a child can be mentioned before its parent. Each link then sets one pointer.
2. **Find the root.** Every node except the root appears exactly once as a child. Record the children in a set; the root is the parent that is not in it.

An alternative for step 2 is to count in-degrees, or to XOR or sum all parents and all children. Every value except the root cancels out.

Complexity: O(m) expected time and memory with hashing.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

TreeNode* build_from_links(const vector<array<int, 3>>& links) {
    unordered_map<int, TreeNode*> node;           // value -> its node, created on first sight
    unordered_set<int> children;                  // every value that has a parent
    node.reserve(links.size() * 2 + 2);
    auto get = [&](int v) {
        auto [it, fresh] = node.try_emplace(v, nullptr);
        if (fresh) it->second = new TreeNode(v);
        return it->second;
    };
    for (auto& [p, c, isLeft] : links) {
        TreeNode* parent = get(p);
        TreeNode* child = get(c);
        (isLeft ? parent->left : parent->right) = child;
        children.insert(c);
    }
    for (auto& [p, c, isLeft] : links)            // the root is the only parent that is never a child
        if (!children.count(p)) return node[p];
    return nullptr;
}
```
