---
id: cpp-tpath-good-nodes
title: Count Good Nodes (Passing State Down)
difficulty: Easy
order: 2
tags: binary tree, dfs, top-down, path maximum
time_limit: 2
---
## Statement
A node is **good** if no node on the path from the root to it (excluding itself) has a **greater** value. The root is always good. Count the good nodes:

```cpp
int good_nodes(TreeNode* root);
```

```text
        3          good: the root 3, the lower 3, 4 and 5: answer 4
       / \         not good: both 1s (the root 3 is above each of them)
      1   4
     /   / \
    3   1   5
```

This is the **top-down** pattern: information (here, the maximum value seen so far on the path) flows from the root **down** to the children as a parameter, unlike height or diameter, where results flow **up** as return values.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input, one tree line each. Up to 2·10⁵ nodes, values fit in `int` (they can be negative).

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

int good_nodes(TreeNode* root) {
    // counts nodes not smaller than their PARENT only: wrong
    if (!root) return 0;
    int c = 1;
    vector<pair<TreeNode*, int>> st{{root, root->val}};
    while (!st.empty()) {
        auto [n, pv] = st.back(); st.pop_back();
        for (TreeNode* ch : {n->left, n->right}) if (ch) { if (ch->val >= n->val) ++c; st.push_back({ch, n->val}); }
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
        TreeNode* root = rd_tree();
        cout << good_nodes(root) << '\n';
        free_tree(root);
    }
    return 0;
}
```

## Tests
=== sample
7 3 1 4 3 # 1 5
---
4
=== sample
5 3 3 # 4 2
---
3
=== hidden
0
---
0
=== hidden
1 -2147483648
---
1
=== hidden
3 5 1 #
---
1
=== hidden
7 5 # 1 # 3 # 9
---
2
=== hidden
7 2 2 2 2 2 2 2
---
7
=== hidden
7 -1 -5 -1 -3 -6 0 -2
---
3
=== hidden
15 0 # -5 # 3 # 0 # -2 # -5 # 3 # -4
3 -2 # -1
1 2
19 -3 -4 4 1 -4 0 -4 -1 # # -4 # # # # # # # -4
7 -2 -4 # 3 2 # -1
0
8 1 -2 5 0 4 2 3 1
9 3 # -4 # 4 # -3 # -5
3 1 # 4
8 -1 1 # -1 # 1 # 0
---
3
2
1
3
3
0
4
2
2
3
=== hidden
7 0 0 4 0 2 -2 0
11 0 3 0 2 1 5 3 # 5 # -5
24 0 2 0 # # 3 # # -2 0 # 3 1 -5 # # # -1 # # 0 # -3 0
9 5 4 -2 3 -4 -5 # # -4
16 -1 4 # -5 # -4 # -1 # 0 # 3 # 2 # -5
6 -2 2 # 4 -4 5
3 3 -4 4
20 -5 -5 -4 5 -3 -2 4 # # 2 # # 0 0 # # # # # 5
13 3 5 1 5 1 1 3 -3 4 -3 0 -5 1
25 -2 # -1 # -1 # -3 # 4 # 4 # -2 # -1 # -1 # -3 # 4 # 1 # 3
---
5
6
5
1
2
4
2
10
4
6
=== hidden
0
2 3 4
3 -4 -4 0
0
1 -4
14 -1 # -4 -3 # 2 3 # # 0 -4 # # -4
8 0 -4 # 0 # -3 # -3
3 5 0 4
9 -4 0 # -5 # -1 2 # -1
13 0 4 # # 4 -3 # # 4 0 # # -3
---
0
2
3
0
1
3
2
1
3
4
=== hidden
@gen 322840219 big
=== hidden
@gen 322840220 big
=== hidden
@gen 322840221 big

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
    vals, L, R = rand_tree(n, -5, 5) if not big else rand_tree(n, -10**9, 10**9)
    print(tline(vals, L, R))
```

## Hints
- Pass a second parameter down the recursion: the largest value on the path from the root.
- A node is good when its value is at least that parameter. Ties count as good.
- Start with a value smaller than any `int`, so the root is always good.

## Solution
Carry the **maximum value seen on the path so far** as a parameter. A node is good when its value is at least that maximum. Then recurse into both children with the updated maximum. The root starts with "minus infinity" (`LLONG_MIN`, so that `INT_MIN` values compare correctly), which makes it good automatically.

Comparing only with the **parent** is the classic bug. In `5 → 1 → 3`, node 3 beats its parent 1 but not the root 5.

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

static int count(TreeNode* n, long long best) {          // best = max value on the path above n
    if (!n) return 0;
    int good = n->val >= best ? 1 : 0;
    long long nb = max(best, (long long)n->val);
    return good + count(n->left, nb) + count(n->right, nb);
}

int good_nodes(TreeNode* root) { return count(root, LLONG_MIN); }
```
