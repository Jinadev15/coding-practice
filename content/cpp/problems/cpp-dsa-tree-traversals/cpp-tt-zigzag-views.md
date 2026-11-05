---
id: cpp-tt-zigzag-views
title: Zigzag Order and the Side Views
difficulty: Medium
order: 5
tags: binary tree, bfs, level order, views
time_limit: 2
---
## Statement
Three variations of level-order traversal:

```cpp
vector<vector<int>> zigzag(TreeNode* root);   // level 0 left→right, level 1 right→left, level 2 left→right, ...
vector<int> right_view(TreeNode* root);       // the last node of every level (what you see from the right)
vector<int> left_view(TreeNode* root);        // the first node of every level
```

```text
        1            zigzag:     [1] [3 2] [4 5 6] [7]
      /   \          right view: 1 3 6 7
     2     3         left view:  1 2 4 7
    / \     \
   4   5     6
      /
     7
```

Note that the right view can contain nodes from the **left** subtree (7 here) when the right side is shorter. "Follow right pointers from the root" is the classic wrong answer.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input. Each case is a line `zigzag`, `right` or `left`, then a tree line. Up to 2·10⁵ nodes.

**Output:** for `zigzag`, a line `levels=L` and then one line per level. For the views, one line with the view. Lists of more than 60 numbers are printed as `count=C hash=H` (a fingerprint), shorter ones in full; an empty list prints `(none)`.

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

vector<vector<int>> zigzag(TreeNode* root) { return {}; }
vector<int> right_view(TreeNode* root) { vector<int> v; for (TreeNode* n = root; n; n = n->right) v.push_back(n->val); return v; }
vector<int> left_view(TreeNode* root) { vector<int> v; for (TreeNode* n = root; n; n = n->left) v.push_back(n->val); return v; }
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
        if (cmd == "zigzag") {
            auto lv = zigzag(root);
            cout << "levels=" << lv.size() << '\n';
            for (auto& l : lv) cout << show_vec(l) << '\n';
        } else {
            cout << show_vec(cmd == "right" ? right_view(root) : left_view(root)) << '\n';
        }
        free_tree(root);
    }
    return 0;
}
```

## Tests
=== sample
zigzag
10 1 2 3 4 5 # 6 # # 7
---
levels=4
1
3 2
4 5 6
7
=== sample
right
10 1 2 3 4 5 # 6 # # 7
---
1 3 6 7
=== sample
left
10 1 2 3 4 5 # 6 # # 7
---
1 2 4 7
=== hidden
zigzag
0
---
levels=0
=== hidden
right
0
---
(none)
=== hidden
right
5 1 2 3 4 #
---
1 3 4
=== hidden
left
5 1 2 3 # 4
---
1 2 4
=== hidden
zigzag
15 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
---
levels=4
1
3 2
4 5 6 7
15 14 13 12 11 10 9 8
=== hidden
zigzag
22 38 -15 # 39 # 0 # -40 # 26 # 8 # -30 # 24 # 1 # 43 # -18
left
22 4 -12 -48 13 # # # 9 -9 38 -17 # # 5 # # 16 1 # # # 9
right
6 30 # -41 # 46 -31
left
8 34 37 -25 22 -39 -46 24 0
right
18 -25 -25 # 1 # -37 # -24 # 32 # -7 # 33 # -24 # -49
left
6 39 -19 # # -46 46
---
levels=12
38
-15
39
0
-40
26
8
-30
24
1
43
-18
4 -12 13 9 38 5 1 9
30 -41 46 -31
34 37 22 0
-25 -25 1 -37 -24 32 -7 33 -24 -49
39 -19 -46 46
=== hidden
zigzag
12 42 -7 # 35 # -14 # -34 # 48 # 48
zigzag
8 38 17 # 42 # 13 # -10
zigzag
4 6 8 -41 -45
zigzag
3 -4 # 32
right
13 9 9 # # 8 46 # # -4 32 # # 22
right
4 -36 -24 21 11
---
levels=7
42
-7
35
-14
-34
48
48
levels=5
38
17
42
13
-10
levels=3
6
-41 8
-45
levels=2
-4
32
9 9 8 46 -4 32 22
-36 21 11
=== hidden
left
7 39 # 20 34 9 # 45
left
21 -14 # 7 # 15 # 39 # -40 # -35 # 39 # 9 # -41 # 31 # 31
left
13 -23 -20 # # -32 -49 12 # # -44 # -14 -39
left
21 -44 35 # # -11 -20 # # -45 20 # # -21 -20 # # -26 11 # # -14
zigzag
19 33 # -39 # 27 # -24 # -29 # 1 # 36 # 47 # 10 # -18
left
14 34 50 # -32 # 44 # -20 # -26 # -50 # -35
---
39 20 34 45
-14 7 15 39 -40 -35 39 9 -41 31 31
-23 -20 -32 -49 -44 -14
-44 35 -11 -20 -45 20 -21 -20 -26 11 -14
levels=10
33
-39
27
-24
-29
1
36
47
10
-18
34 50 -32 44 -20 -26 -50 -35
=== hidden
@gen 2951826456 big
=== hidden
@gen 2951826457 big
=== hidden
@gen 2951826458 big

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
    print(r.choice(["zigzag", "right", "left"])); print(tline(vals, L, R))
```

## Hints
- Run BFS level by level. Each answer is a simple function of one level's node list.
- Zigzag: build the level left to right, then reverse it on every other level.
- The right view's last element can come from the left subtree. Test with a tree whose left side is deeper.

## Solution
All three answers are read off the levels, so one BFS skeleton serves them all. Here it is written with two vectors, `cur` and `next`, which is an alternative to `q.size()` counting.

- **Zigzag:** collect each level left to right as usual and reverse the values of every odd level. Don't try to push children in reverse order instead: that scrambles the order of the next level.
- **Right view:** the last node of each level. **Left view:** the first node.

The right view is about **depth**, not about right pointers: a level's last node can belong to the left subtree when the right subtree is shallower.

A DFS alternative for the views: visit right-first (or left-first) and record a node when its depth equals the current length of the answer. Each depth is then recorded exactly once, by the first node seen at that depth.

Complexity: O(n) time, O(w) memory for the widest level.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

// one BFS pass that hands each level to a callback
template <class F> static void by_levels(TreeNode* root, F f) {
    if (!root) return;
    vector<TreeNode*> cur{root}, next;
    while (!cur.empty()) {
        f(cur);
        next.clear();
        for (TreeNode* n : cur) {
            if (n->left) next.push_back(n->left);
            if (n->right) next.push_back(n->right);
        }
        swap(cur, next);
    }
}

vector<vector<int>> zigzag(TreeNode* root) {
    vector<vector<int>> res;
    bool ltr = true;
    by_levels(root, [&](const vector<TreeNode*>& lv) {
        vector<int>& row = res.emplace_back();
        for (TreeNode* n : lv) row.push_back(n->val);
        if (!ltr) reverse(row.begin(), row.end());   // reverse the VALUES; children are still queued left→right
        ltr = !ltr;
    });
    return res;
}

vector<int> right_view(TreeNode* root) {
    vector<int> v;
    by_levels(root, [&](const vector<TreeNode*>& lv) { v.push_back(lv.back()->val); });
    return v;
}

vector<int> left_view(TreeNode* root) {
    vector<int> v;
    by_levels(root, [&](const vector<TreeNode*>& lv) { v.push_back(lv.front()->val); });
    return v;
}
```
