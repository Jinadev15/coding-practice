---
id: cpp-tt-level-order
title: Level Order, Top-Down and Bottom-Up
difficulty: Easy
order: 2
tags: binary tree, bfs, queue, level order
time_limit: 2
---
## Statement
Breadth-first search visits a tree **level by level**. Return the levels as separate lists:

```cpp
vector<vector<int>> level_order(TreeNode* root);          // level 0 (the root) first
vector<vector<int>> level_order_bottom(TreeNode* root);   // deepest level first
```

Each level lists its nodes from left to right. For `5 1 2 3 # 4`: top-down is `[1] [2 3] [4]`, bottom-up is `[4] [2 3] [1]`.

The standard technique: before processing a level, read `q.size()`. That number is exactly how many nodes belong to the current level, because every node already in the queue is on it and every child you push belongs to the next level.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input. Each case is a line `top` or `bottom`, then a tree line. Up to 2·10⁵ nodes. Recursion is not needed here.

**Output:** a line `levels=L`, then one line per level in the requested order. Lists of more than 60 numbers are printed as `count=C hash=H` (a fingerprint), shorter ones in full; an empty list prints `(none)`.

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

vector<vector<int>> level_order(TreeNode* root) { return {}; }
vector<vector<int>> level_order_bottom(TreeNode* root) { return {}; }
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
        auto lv = cmd == "top" ? level_order(root) : level_order_bottom(root);
        cout << "levels=" << lv.size() << '\n';
        for (auto& l : lv) cout << show_vec(l) << '\n';
        free_tree(root);
    }
    return 0;
}
```

## Tests
=== sample
top
5 1 2 3 # 4
---
levels=3
1
2 3
4
=== sample
bottom
5 1 2 3 # 4
---
levels=3
4
2 3
1
=== hidden
top
0
---
levels=0
=== hidden
bottom
1 3
---
levels=1
3
=== hidden
top
7 1 2 3 4 5 6 7
---
levels=3
1
2 3
4 5 6 7
=== hidden
bottom
11 3 9 20 # # 15 7 # # 1 2
---
levels=4
1 2
15 7
9 20
3
=== hidden
top
7 1 # 2 # 3 # 4
---
levels=4
1
2
3
4
=== hidden
top
3 -22 -11 -10
bottom
5 11 -31 48 3 -1
bottom
10 -5 -8 # -4 # -13 # -21 # 18
top
1 -4
top
10 -27 -37 # # -26 -4 # # -49 -44
top
13 0 # 46 # 34 # -34 # 28 # 17 # 42
---
levels=2
-22
-11 -10
levels=3
3 -1
-31 48
11
levels=6
18
-21
-13
-4
-8
-5
levels=1
-4
levels=6
-27
-37
-26
-4
-49
-44
levels=7
0
46
34
-34
28
17
42
=== hidden
top
10 -32 8 # -16 # -8 # 37 # 44
bottom
6 43 20 -26 # # 26
top
5 43 -44 30 -37 -29
top
8 -38 24 -43 8 -50 -24 38 36
top
10 -48 -17 # # 10 -18 # # -4 -1
top
1 -4
---
levels=6
-32
8
-16
-8
37
44
levels=3
26
20 -26
43
levels=3
43
-44 30
-37 -29
levels=4
-38
24 -43
8 -50 -24 38
36
levels=6
-48
-17
10
-18
-4
-1
levels=1
-4
=== hidden
bottom
2 -31 33
bottom
9 -8 -49 # -35 -2 # # 3 -35
top
14 -40 # 0 45 -6 # -15 -10 5 1 # # # 33
bottom
8 16 0 -6 -24 -19 -1 -46 -31
bottom
12 9 -38 27 # # 4 21 # 36 # # 49
top
22 7 -25 # # -24 -38 # # 16 -45 # # -46 -49 # # 34 -20 # # -1 -23
---
levels=2
33
-31
levels=4
3 -35
-35 -2
-49
-8
levels=5
-40
0
45 -6
-15 -10 5
1 33
levels=4
-31
-24 -19 -1 -46
0 -6
16
levels=5
49
36
4 21
-38 27
9
levels=12
7
-25
-24
-38
16
-45
-46
-49
34
-20
-1
-23
=== hidden
@gen 3833442955 big
=== hidden
@gen 3833442956 big
=== hidden
@gen 3833442957 big

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
    n = r.randint(0, 12) if not big else 200000
    vals, L, R = rand_tree(n, -50, 50) if not big else rand_tree(n, 0, 10**6, r.choice(["random", "complete", "deep"]))
    print(r.choice(["top", "bottom"])); print(tline(vals, L, R))
```

## Hints
- Use `std::queue<TreeNode*>`. Push the root, then loop while the queue is not empty.
- At the start of each round, `int width = q.size();` and pop exactly `width` nodes.
- For bottom-up, build top-down and reverse the outer vector once.

## Solution
A FIFO queue processes nodes in the order they were discovered, which for a tree is level by level, left to right. Reading `q.size()` at the start of each round separates the levels without storing depths: the queue then holds exactly the current level.

Bottom-up order is the same list reversed. Reversing a `vector<vector<int>>` swaps the inner vectors in O(1) each, so it is cheap. Inserting each new level at the front would cost O(levels²) instead.

Complexity: O(n) time, O(w) queue memory where w is the widest level (up to n/2 for a complete tree).

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

vector<vector<int>> level_order(TreeNode* root) {
    vector<vector<int>> res;
    if (!root) return res;
    queue<TreeNode*> q;
    q.push(root);
    while (!q.empty()) {
        int width = (int)q.size();               // all nodes of the current level are queued
        vector<int>& level = res.emplace_back();
        for (int i = 0; i < width; ++i) {
            TreeNode* n = q.front(); q.pop();
            level.push_back(n->val);
            if (n->left) q.push(n->left);        // children belong to the next level
            if (n->right) q.push(n->right);
        }
    }
    return res;
}

vector<vector<int>> level_order_bottom(TreeNode* root) {
    auto res = level_order(root);
    reverse(res.begin(), res.end());             // O(number of levels): only the outer vector moves
    return res;
}
```
