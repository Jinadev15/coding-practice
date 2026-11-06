---
id: cpp-tpath-max-path-sum
title: Maximum Path Sum Anywhere in the Tree
difficulty: Hard
order: 8
tags: binary tree, tree dp, postorder, path sum
time_limit: 2
---
## Statement
A **path** is a sequence of nodes where consecutive nodes are parent and child, and no node appears twice. It contains at least one node and does not have to pass through the root. Return the largest sum of a path:

```cpp
long long max_path_sum(TreeNode* root);   // the tree is never empty
```

```text
       -10              best path: 15 → 20 → 7, sum 42
       /  \
      9    20           with all values negative (e.g. -3 alone with children -5 and -7),
          /  \          the answer is the single largest value: -3
         15   7
```

Combine the two ideas of this topic. Like the diameter, every path has a highest node where it "bends", and its sum there is `val + best downward gain on the left + best downward gain on the right`. Like a tree DP, each call returns to its parent the best sum of a path that **starts at this node and goes down one side**, where a negative branch is cut off (`max(0, gain)`).

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input, one non-empty tree line each. Up to 2·10⁵ nodes, values fit in `int`.

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

long long max_path_sum(TreeNode* root) {
    // largest single value: misses paths of several nodes
    long long best = LLONG_MIN;
    vector<TreeNode*> st{root};
    while (!st.empty()) { auto* n = st.back(); st.pop_back(); best = max(best, (long long)n->val); if (n->left) st.push_back(n->left); if (n->right) st.push_back(n->right); }
    return best;
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
        cout << max_path_sum(root) << '\n';
        free_tree(root);
    }
    return 0;
}
```

## Tests
=== sample
7 -10 9 20 # # 15 7
---
42
=== sample
3 -3 -5 -7
---
-3
=== hidden
1 -2147483648
---
-2147483648
=== hidden
1 5
---
5
=== hidden
3 1 2 3
---
6
=== hidden
3 2 -1 -1
---
2
=== hidden
7 -1 5 # 4 # # 3
---
12
=== hidden
9 5 4 8 11 # 13 4 7 2
---
48
=== hidden
7 2147483647 2147483647 2147483647 # # 2147483647 2147483647
---
8589934588
=== hidden
2 7 -1
12 -9 1 # -7 # -5 # -4 # -1 # -9
5 -3 # 1 # 5
22 -4 7 0 # # 7 -7 # -4 -2 2 8 0 -3 # # # # # # # -1
6 2 5 # # 6 1
16 -4 -3 # 5 # -4 # -3 # 3 # -8 # 0 # -7
18 4 0 0 -3 # 4 -4 # # # -8 -5 # # # # 3 -6
24 -5 -5 # -6 # -5 # -8 # -8 # 6 # -4 # 2 # -7 # -4 # -1 # -3
12 9 1 # -4 # -6 # 0 # 3 # -4
15 4 6 -3 # -2 3 # # # -3 5 6 # # 4
---
7
1
6
14
14
5
8
6
10
19
=== hidden
17 7 0 7 # 8 -5 4 # -7 9 # # # # # # -9
10 -1 # -8 8 -5 -1 # # -7 8
17 -6 -4 # -3 5 6 # # # 7 7 -2 # # # # -4
10 -2 6 -6 -4 -8 -6 -6 -2 5 9
10 6 1 # -5 # -2 # 5 # -1
4 6 # 9 -4
19 -4 1 # 3 -3 -5 # 4 -9 # -7 # # # -7 # # # 0
11 6 6 -5 -2 5 # # # # 9 -7
3 1 -3 -8
6 4 -4 # # -1 5
---
26
15
20
9
7
15
5
26
1
5
=== hidden
3 5 # 7
5 1 4 # # 4
1 -4
17 -6 -5 2 8 # 4 1 # # # -8 -3 # # # # -3
20 -4 4 -4 # 3 -2 -3 # -2 # # 5 -1 # 1 # # 7 # 6
21 7 -6 # 2 # 0 4 5 -1 # # # 7 # 6 # # -4 9 # -4
15 7 3 3 7 5 -8 # -8 -2 # # # # # 2
14 0 5 # -8 # 7 # # -9 # -2 # 6 4
19 -3 7 7 0 # # -5 # 4 # -2 -2 # # # # 9 # 1
3 9 # 5
---
12
9
-4
8
12
26
20
10
23
14
=== hidden
@gen 1515132949 big
=== hidden
@gen 1515132950 big
=== hidden
@gen 1515132951 big

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
    n = r.randint(1, 13) if not big else 200000
    vals, L, R = rand_tree(n, -9, 9) if not big else rand_tree(n, -10**9, 10**9)
    print(tline(vals, L, R))
```

## Hints
- Every path has a highest node. Its sum is that node's value plus the best downward gain on each side.
- Return to the parent only a one-sided downward gain. A parent can't use both branches.
- Clamp negative gains to 0, but initialise the answer to `LLONG_MIN` for all-negative trees.

## Solution
Two different quantities live at every node:

1. **What the node reports upward:** the best path that starts at the node and goes **down a single branch**: `val + max(0, left gain, right gain)`. Only one branch, because the parent will attach to this node, and a path can't fork.
2. **What the node offers as a final answer:** the best path whose **highest node** is this one: `val + max(0, left gain) + max(0, right gain)`, which may use both branches.

The global maximum of (2) over all nodes is the answer. Every path has exactly one highest node, so every path is considered.

`max(0, …)` drops branches that would lower the sum. The answer itself starts at `LLONG_MIN`, not 0, so that an all-negative tree returns its largest single value instead of 0. Mixing up (1) and (2), that is returning the two-branch value to the parent, is the classic bug: it builds "paths" that fork.

Complexity: O(n) time, O(h) recursion depth; sums need `long long` (2·10⁵ · 2³¹ overflows `int`).

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

// best sum of a path that starts at n and goes down; updates best with paths that bend at n
static long long gain(TreeNode* n, long long& best) {
    if (!n) return 0;
    long long l = max(0LL, gain(n->left, best));    // a negative branch is better left out
    long long r = max(0LL, gain(n->right, best));
    best = max(best, n->val + l + r);               // the path bends at n
    return n->val + max(l, r);                      // a parent can extend only one side
}

long long max_path_sum(TreeNode* root) {
    long long best = LLONG_MIN;
    gain(root, best);
    return best;
}
```
