---
id: cpp-tpath-depths
title: Maximum and Minimum Depth
difficulty: Easy
order: 1
tags: binary tree, recursion, depth, bfs
time_limit: 2
---
## Statement
The **depth** of a tree here counts **nodes**: a single node has depth 1 and the empty tree has depth 0.

```cpp
int max_depth(TreeNode* root);   // nodes on the longest root-to-leaf path
int min_depth(TreeNode* root);   // nodes on the shortest root-to-LEAF path
```

```text
      3            max_depth = 3  (3 → 20 → 15)
     / \           min_depth = 2  (3 → 9)
    9   20
       /  \
      15   7
```

**The trap in `min_depth`:** a node with one child is not a leaf. For the chain `1 → 2`, the minimum depth is 2, not 1, because the root's empty side does not end a root-to-leaf path. The "obvious" `1 + min(left, right)` gives 1.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input. Each case is a line `max` or `min`, then a tree line. Up to 2·10⁵ nodes.

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

int max_depth(TreeNode* root) { return root ? 1 : 0; }
int min_depth(TreeNode* root) {
    if (!root) return 0;
    return 1 + min(min_depth(root->left), min_depth(root->right));   // wrong for one-child nodes
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
        string cmd = rd_str();
        TreeNode* root = rd_tree();
        cout << (cmd == "max" ? max_depth(root) : min_depth(root)) << '\n';
        free_tree(root);
    }
    return 0;
}
```

## Tests
=== sample
max
5 3 9 20 15 7
---
3
=== sample
min
5 3 9 20 15 7
---
2
=== sample
min
2 1 2
---
2
=== hidden
max
0
min
0
max
1 4
min
1 4
---
0
0
1
1
=== hidden
min
5 1 # 2 # 3
max
5 1 # 2 # 3
---
3
3
=== hidden
min
9 1 2 3 4 # # 5 # 6
---
3
=== hidden
min
7 1 2 3 4 5 # 6
---
3
=== hidden
min
17 -5 -6 4 # -8 # # # -2 # 6 -4 # # -9 # -8
max
0
max
0
min
27 7 # 6 # 1 # -3 # 7 # -1 # 4 # 2 # -4 # -1 # 1 # 3 # -2 # -6
min
19 8 8 6 2 8 -5 -2 8 -2 # -3 # # -7 -6 # # 7 -8
max
9 5 3 3 # # -4 -1 -7 3
min
1 3
max
15 1 # 1 # -9 # 5 # -9 # -7 # -7 # -6
max
25 -6 -1 # # -7 -4 # # -3 7 # # 8 6 # # 9 -3 # # -6 -9 # # 5
max
1 -4
---
2
0
0
14
3
4
1
8
13
1
=== hidden
max
12 -1 6 2 -6 7 -2 -2 6 7 6 -1 -3
max
0
max
13 -6 5 6 -8 # -3 1 # # # -7 -6 -9
min
13 2 7 # # -9 -9 # # 9 -6 # # -3
min
20 -3 -8 # 7 # 4 # -8 # 2 # -4 # -9 # 8 # -1 # -4
max
11 9 -3 -2 -8 -4 -5 # # # # -9
min
13 -4 1 # # 4 -2 # # -3 3 # # -1
max
23 -8 2 # -1 8 2 -6 3 # 4 6 # # 6 # # # # -9 # -5 # 7
min
11 -2 # -5 -7 4 -8 # # # # 4
max
25 -2 # -6 # 7 # 3 # -3 # 9 # -9 # 1 # 8 # 9 # -2 # 6 # -4
---
4
0
4
7
11
4
7
7
3
13
=== hidden
min
7 -4 -7 # 5 # # 2
min
16 6 6 # -6 # -2 # 0 # -7 # -3 # 1 # 7
max
14 -3 -6 -6 -6 6 -8 7 6 0 -4 8 3 9 -9
min
3 -1 -8 1
min
1 2
min
19 5 -3 -2 -4 # 2 # # # 9 6 -4 # # # -8 # # -6
min
8 -6 -4 -3 -1 -6 -6 -5 9
max
24 6 -5 # 7 # -7 # -1 # 8 # 3 # 3 # 7 # 5 # -7 # -1 # 4
min
22 -9 -4 -7 # # 8 9 # -5 # # 7 -8 # # -6 # # 2 0 # 7
min
15 5 # 3 # 2 # 0 # 3 # 9 # 7 # 2
---
4
9
4
2
1
3
3
13
2
8
=== hidden
@gen 3001120154 big
=== hidden
@gen 3001120155 big
=== hidden
@gen 3001120156 big

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
    vals, L, R = rand_tree(n, -9, 9) if not big else rand_tree(n, 0, 99)
    print(r.choice(["max", "min"])); print(tline(vals, L, R))
```

## Hints
- Max depth: `1 + max(depth(left), depth(right))`, with depth(empty) = 0.
- Min depth: what is the minimum depth of a root that has only a right child?
- Handle "one child missing" before taking `min` of the two sides.

## Solution
**Max depth** is the textbook postorder computation: the depth of a tree is one more than the deeper of its two subtrees, and the empty tree has depth 0.

**Min depth** must end at a **leaf**. If one child is missing, that side contains no leaf at all, so its "depth 0" must not win the minimum. Only when both children exist do you take the smaller. A BFS alternative stops at the first leaf it dequeues, which is faster when a shallow leaf exists in a huge tree.

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

int max_depth(TreeNode* root) {
    if (!root) return 0;
    return 1 + max(max_depth(root->left), max_depth(root->right));   // postorder: children first
}

int min_depth(TreeNode* root) {
    if (!root) return 0;
    if (!root->left) return 1 + min_depth(root->right);   // only one side exists: the path must go there
    if (!root->right) return 1 + min_depth(root->left);
    return 1 + min(min_depth(root->left), min_depth(root->right));
}
```
