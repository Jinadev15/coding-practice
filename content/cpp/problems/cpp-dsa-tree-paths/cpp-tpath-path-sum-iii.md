---
id: cpp-tpath-path-sum-iii
title: Downward Paths with a Given Sum (Prefix Sums on a Tree)
difficulty: Medium
order: 6
tags: binary tree, prefix sums, hash map, backtracking
time_limit: 2
---
## Statement
Count the paths whose values add up to `target`. A path may start and end **anywhere**, but it must go **downward** (from a node to one of its descendants, possibly a single node):

```cpp
long long count_paths(TreeNode* root, long long target);
```

```text
           10              target 8: three paths
          /  \               5 → 3
         5   -3              5 → 2 → 1
        / \    \            -3 → 11
       3   2    11
      / \   \
     3  -2   1
```

Trying every start node and walking down costs O(n·h), which is O(n²) on a chain. Instead, reuse the array trick "subarrays with sum k" (*Hashing and prefix sums*): along the current root-to-node path, keep a hash map `count[s]` = how many path prefixes have sum `s`. At a node with prefix sum `S`, the number of good paths ending here is `count[S − target]`. Add `S` to the map before visiting the children, and **remove it when you return** (backtracking), because a sibling's subtree must not see this path.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input. Each case is a line `target`, then a tree line. Up to 2·10⁵ nodes, values fit in `int`. The answer can exceed 2³¹.

Trees can be degenerate chains of up to 2·10⁵ nodes. The driver runs your code on a thread with a 256 MB stack, so plain recursion is safe here (on a normal 8 MB stack it would not be).

**Output:** one number per case.

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

long long count_paths(TreeNode* root, long long target) {
    // only paths that start at the root: incomplete
    long long c = 0;
    vector<pair<TreeNode*, long long>> st; if (root) st.push_back({root, 0});
    while (!st.empty()) {
        auto [n, s] = st.back(); st.pop_back();
        s += n->val; if (s == target) ++c;
        if (n->left) st.push_back({n->left, s});
        if (n->right) st.push_back({n->right, s});
    }
    return c;
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
        long long target = rd_ll();
        TreeNode* root = rd_tree();
        cout << count_paths(root, target) << '\n';
        free_tree(root);
    }
    return 0;
}
```

## Tests
=== sample
8
11 10 5 -3 3 2 # 11 3 -2 # 1
---
3
=== sample
0
3 1 -1 0
---
2
=== hidden
0
0
---
0
=== hidden
5
1 5
---
1
=== hidden
0
1 0
---
1
=== hidden
0
7 0 # 0 # 0 # 0
---
10
=== hidden
-2147483648
6 2147483647 1 # -2147483648 # -1
---
2
=== hidden
2
7 1 1 1 1 1 1 1
---
6
=== hidden
3
9 3 2 # -2 2 -2 3 # 1
-3
21 1 -1 -3 0 2 # # # -1 # # # 3 # -3 2 1 -3 # # -1
-3
2 -1 3
-1
5 0 # 3 # 2
4
5 0 # -2 1 0
-3
0
3
9 1 1 -1 # # 1 # 1 0
-2
18 -3 -2 # -1 2 # # # -1 1 # -1 # # -1 -1 # 2
4
14 0 3 # # -2 -2 # # -1 3 # # 3 3
-4
20 0 2 -1 -1 1 3 # # # 2 -1 # 2 -1 1 # -1 # # -1
---
5
5
0
0
0
0
0
6
3
0
=== hidden
2
4 -1 -3 0 -3
-3
11 2 3 -3 -2 # # 1 # # # -2
2
11 -3 # -2 # 0 # 2 # 0 # -2
-2
25 -3 # 2 # -3 # -3 # 3 # -1 # 0 # -1 # -1 # 1 # -2 # -1 # 2
2
8 3 -1 0 # # 3 # 2
-2
23 3 # 3 # 1 -3 -2 # # -2 # -3 # 2 # 3 # 1 # 0 # # 0
2
3 -3 # -3
0
16 0 2 # -3 # 3 # -1 # -3 # 0 # 3 # 0
-2
3 0 1 3
0
0
---
0
1
4
14
2
4
0
6
0
0
=== hidden
4
6 2 -1 1 -2 -2 0
3
7 2 -2 -2 -2 0 2 1
-4
19 2 1 -1 # # -1 3 1 -2 # 1 # 2 # # # # -1 -2
-2
15 1 # 1 # 3 # -3 # -3 # -2 # -1 # -3
-1
11 -3 # -2 # 0 3 0 2 1 # -1
3
11 1 0 -1 # # # 2 1 # -2 -1
3
8 0 1 2 3 1 3 3 1
-4
10 -1 # -2 0 -3 3 # # # -3
1
4 3 # -2 3
3
16 -1 0 # -3 # 2 # 2 1 # # 1 -2 # # -1
---
0
0
1
2
4
2
3
0
2
1
=== hidden
@gen 3316289117 big
=== hidden
@gen 3316289118 big
=== hidden
@gen 3316289119 big

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
    if big and r.random() < 0.5:
        L, R = shape(n, r.choice(["left", "zigzag"])); vals = [0] * n; t = 0
    else:
        vals, L, R = rand_tree(n, -3, 3) if not big else rand_tree(n, -5, 5, r.choice(["random", "deep"])); t = r.randint(-4, 4)
    print(t); print(tline(vals, L, R))
```

## Hints
- A downward path's sum is a difference of two root-prefix sums on the same root-to-node line.
- Keep a hash map of prefix-sum counts for the current path only, seeded with `{0: 1}`.
- Insert the node's prefix before recursing, and remove it after both children return. The answer needs `long long`.

## Solution
A downward path from `u` to `v` has sum `prefix(v) − prefix(parent of u)`, where `prefix(x)` is the sum from the root to `x`. So the number of good paths **ending at** `v` is the number of ancestors-or-root-prefixes with prefix sum `prefix(v) − target`.

The DFS keeps a multiset (a hash map of counts) of the prefix sums on the current root-to-node path, starting with `0` for the empty prefix (paths that start at the root itself).

- On entering `v`: count `seen[S − target]`, then insert `S`.
- Recurse into the children.
- On leaving `v`: remove `S`. This is the backtracking step: once we return, `v` is no longer on the path, and paths in a sibling subtree must not start below `v`.

Order matters: look up before inserting `S`, otherwise `target = 0` would count the empty path at `v`.

Complexity: O(n) expected time, O(h) map entries and recursion depth. The count is a `long long`: a chain of 2·10⁵ zeros with target 0 has about 2·10¹⁰ paths.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

static long long dfs(TreeNode* n, long long sum, long long target, unordered_map<long long, int>& seen) {
    if (!n) return 0;
    sum += n->val;                                 // prefix sum from the root to n
    auto it = seen.find(sum - target);
    long long here = it == seen.end() ? 0 : it->second;   // paths ending at n
    ++seen[sum];
    here += dfs(n->left, sum, target, seen) + dfs(n->right, sum, target, seen);
    if (--seen[sum] == 0) seen.erase(sum);         // backtrack: siblings must not see this prefix
    return here;
}

long long count_paths(TreeNode* root, long long target) {
    unordered_map<long long, int> seen;
    seen.reserve(1 << 16);
    seen[0] = 1;                                   // the empty prefix: paths starting at the root
    return dfs(root, 0, target, seen);
}
```
