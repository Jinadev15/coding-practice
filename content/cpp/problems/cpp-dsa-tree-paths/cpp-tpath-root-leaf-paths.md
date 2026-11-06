---
id: cpp-tpath-root-leaf-paths
title: All Root-to-Leaf Paths with a Given Sum
difficulty: Medium
order: 4
tags: binary tree, dfs, backtracking, path sum
time_limit: 2
---
## Statement
List every **root-to-leaf** path whose values add up to `target`, in left-to-right order of their leaves:

```cpp
vector<vector<int>> path_sum(TreeNode* root, long long target);
```

```text
          5              target 22:
         / \               5 → 4 → 11 → 2
        4   8              5 → 8 → 4 → 5
       /   / \
      11  13  4
     /  \    / \
    7    2  5   1
```

Use **backtracking**: keep one `path` vector, push the node on the way down, record a copy when you reach a matching leaf, and **pop on the way back up**. Copying the path into every recursive call works too, but costs O(n·h) memory traffic on its own.

A path must end at a **leaf** (no children). Stopping early when the running sum equals the target is wrong: values may be negative or zero, so a longer path can still match.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input. Each case is a line with `target`, then a tree line. Up to 2·10⁵ nodes; values fit in `int`, sums in `long long`.

Trees can be degenerate chains of up to 2·10⁵ nodes. The driver runs your code on a thread with a 256 MB stack, so plain recursion is safe here (on a normal 8 MB stack it would not be).

**Output:** `paths=K`, then the first (up to) 10 paths one per line (Lists of more than 60 numbers are printed as `count=C hash=H` (a fingerprint), shorter ones in full; an empty list prints `(none)`.), then `all=H`, a fingerprint of every path in order.

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

vector<vector<int>> path_sum(TreeNode* root, long long target) { return {}; }
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
        long long target = rd_ll();
        TreeNode* root = rd_tree();
        auto ps = path_sum(root, target);
        cout << "paths=" << ps.size() << '\n';
        unsigned long long hs = 0;
        for (size_t i = 0; i < ps.size(); ++i) {
            if (i < 10) cout << show_vec(ps[i]) << '\n';
            for (int v : ps[i]) hs = hs * 1000003ULL + (unsigned long long)((long long)v + 3000000000LL);
            hs = hs * 1000003ULL + 17;
        }
        cout << "all=" << hs << '\n';
        free_tree(root);
    }
    return 0;
}
```

## Tests
=== sample
22
13 5 4 8 11 # 13 4 7 2 # # 5 1
---
paths=2
5 4 11 2
5 8 4 5
all=7211413847319476338
=== sample
3
3 1 2 3
---
paths=1
1 2
all=11648461095060638240
=== hidden
0
0
---
paths=0
all=0
=== hidden
5
1 5
---
paths=1
5
all=3000009005000032
=== hidden
-5
1 5
---
paths=0
all=0
=== hidden
1
3 1 2 #
---
paths=0
all=0
=== hidden
0
7 0 0 0 0 0 0 0
---
paths=4
0 0 0
0 0 0
0 0 0
0 0 0
all=1001607320270679588
=== hidden
2
9 1 # 1 # 1 # -1 # 1
---
paths=0
all=0
=== hidden
-2147483648
3 -2147483648 # 0
---
paths=1
-2147483648 0
all=3974239724145272849
=== hidden
2
6 -2 2 2 -2 # 0
-1
2 2 -1
1
16 -2 2 1 # 1 # # -2 2 # 2 2 -1 # # 2
1
23 2 # 2 -2 -1 # # -1 # 2 1 # 0 2 # # # 0 # # 0 # 0
2
2 1 0
-2
23 -1 # 1 # 2 # 2 # 1 # 1 # 0 # 0 # -1 # 0 # 1 # -1
-1
13 0 2 0 2 2 0 0 0 1 # -2 # -1
-1
0
1
21 0 0 # # 0 0 # # -1 -2 # # -2 0 # # 0 -2 # # 0
-1
4 -1 1 -2 2
---
paths=0
all=0
paths=0
all=0
paths=1
-2 2 1 -2 2
all=5236457145148892828
paths=0
all=0
paths=0
all=0
paths=0
all=0
paths=1
0 0 0 -1
all=6931994057995308494
paths=0
all=0
paths=0
all=0
paths=0
all=0
=== hidden
-2
20 -1 1 -1 -1 -2 -2 # -1 2 -2 # 1 # # 1 # # 2 # -2
-2
12 -1 2 0 # -1 # # -1 -1 # # 2
1
1 -1
-1
22 0 -2 # # -2 -2 # # 2 1 # # 2 2 # # -1 2 # # -1 -1
1
22 -2 -2 # 1 # 0 # 0 # -2 # -1 # -1 # -1 # 2 # -2 # -2
-3
4 -2 # -1 -1
0
5 1 2 # # 1
-2
10 1 # -2 0 0 # # 1 # 0
1
17 -1 1 1 -1 0 # # # -1 1 -1 # 0 0 0 # -2
1
27 0 # -1 # -2 # 0 # 1 # -2 # 2 # 0 # -1 # 2 # -2 # 2 # 0 # -1
---
paths=1
-1 1 -2 -2 2
all=2685824846309399789
paths=0
all=0
paths=0
all=0
paths=0
all=0
paths=0
all=0
paths=0
all=0
paths=0
all=0
paths=0
all=0
paths=2
-1 1 0 1 0
-1 1 0 1 0
all=95189994492652720
paths=0
all=0
=== hidden
-2
17 0 -2 1 # # -1 # # -2 -2 # -1 # # -1 # 0
2
14 1 2 0 1 -2 -2 -1 2 0 -1 2 1 -2 -2
0
11 -1 0 -2 # # 1 # -1 -2 # -1
-1
8 -2 # 2 -2 2 # # 2
-1
17 -2 -2 # # 0 1 # # 0 2 # # -1 2 # # 1
-2
25 0 0 # 2 -2 # # -1 # # 2 1 1 # # -1 # # 2 1 # 0 # 2 0
3
13 -1 # 0 # -1 # -1 # -1 # -1 # -2
-1
4 0 -1 # -1
3
7 0 -2 2 # -2 2 1
3
20 -2 2 # 1 # 0 # 2 # 0 # 1 # -1 # -2 # 1 # 1
---
paths=1
0 -2
all=11648460095050638219
paths=0
all=0
paths=0
all=0
paths=0
all=0
paths=0
all=0
paths=0
all=0
paths=0
all=0
paths=0
all=0
paths=1
0 2 1
all=3350185856658165606
paths=1
-2 2 1 0 2 0 1 -1 -2 1 1
all=18427368438536036766
=== hidden
@gen 2513167784 big
=== hidden
@gen 2513167785 big
=== hidden
@gen 2513167786 big

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
    n = r.randint(0, 14) if not big else 200000
    vals, L, R = rand_tree(n, -2, 2) if not big else rand_tree(n, -1, 1, r.choice(["random", "complete", "left"]))
    print(r.randint(-3, 3)); print(tline(vals, L, R))
```

## Hints
- Keep one path vector: push when entering a node, pop when leaving it.
- Pass the remaining sum down; at a leaf, check whether it reached exactly 0.
- Only leaves (no children at all) can end a path.

## Solution
This is **DFS with backtracking**: the shared `path` vector always holds exactly the nodes from the root to the current node. Push on entry, pop on exit, and copy the path only when a leaf matches. The **remaining** target travels down as a parameter, so no sum is recomputed.

Leaves are reached in left-to-right order because the left subtree is explored before the right.

Pitfalls: recording at a node that is not a leaf; stopping early because the running sum already equals the target (negative values can bring it back); forgetting the `pop_back` (the path then grows forever).

Complexity: O(n·h) in the worst case because of the copies (the output itself can be that large); O(n) without matches. Recursion depth O(h).

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

static void dfs(TreeNode* n, long long remaining, vector<int>& path, vector<vector<int>>& out) {
    if (!n) return;
    path.push_back(n->val);                       // choose
    remaining -= n->val;
    if (!n->left && !n->right) {
        if (remaining == 0) out.push_back(path);  // a leaf with the right sum: record a copy
    } else {
        dfs(n->left, remaining, path, out);       // explore
        dfs(n->right, remaining, path, out);
    }
    path.pop_back();                              // un-choose
}

vector<vector<int>> path_sum(TreeNode* root, long long target) {
    vector<vector<int>> out;
    vector<int> path;
    dfs(root, target, path, out);
    return out;
}
```
