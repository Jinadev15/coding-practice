---
id: cpp-tpath-tree-rob
title: Tree DP Intro: The Robber on a Tree
difficulty: Medium
order: 7
tags: binary tree, tree dp, postorder, independent set
time_limit: 2
---
## Statement
Each node holds an amount of money (≥ 0). Choose a set of nodes with **no two directly connected** (no node together with its parent) to maximise the total:

```cpp
long long rob(TreeNode* root);
```

```text
        3               take 3, 3 and 1 → 7          3
       / \              (2 and 3 below the root     / \
      2   3              would be adjacent to it)  4   5     take 4 and 5 → 9
       \   \                                      / \   \
        3   1                                    1   3   1
```

Greedy rules ("take every other level", "take the larger child") fail. This is the first **tree DP**: for every node compute **two** numbers bottom-up.

- `take[n]` = best total in `n`'s subtree **if `n` is chosen** = `n->val + skip[left] + skip[right]`
- `skip[n]` = best total **if `n` is not chosen** = `max(take, skip)[left] + max(take, skip)[right]`

Return the pair from one postorder function. Recursing "with and without the grandchildren" instead recomputes subtrees exponentially often.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input, one tree line each. Up to 2·10⁵ nodes, values from 0 to 10⁹.

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

long long rob(TreeNode* root) {
    // takes even levels or odd levels, whichever is larger: not always optimal
    long long a[2] = {0, 0}; int d = 0;
    vector<TreeNode*> cur; if (root) cur.push_back(root);
    while (!cur.empty()) { vector<TreeNode*> nx; for (auto* n : cur) { a[d & 1] += n->val; if (n->left) nx.push_back(n->left); if (n->right) nx.push_back(n->right); } cur.swap(nx); ++d; }
    return max(a[0], a[1]);
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
        cout << rob(root) << '\n';
        free_tree(root);
    }
    return 0;
}
```

## Tests
=== sample
7 3 2 3 # 3 # 1
---
7
=== sample
7 3 4 5 1 3 # 1
---
9
=== hidden
0
---
0
=== hidden
1 7
---
7
=== hidden
1 0
---
0
=== hidden
3 1 # 9
---
9
=== hidden
7 10 1 1 1 1 1 1
---
14
=== hidden
5 2 1 3 # 4
---
7
=== hidden
7 1000000000 1000000000 1000000000 # 1000000000 # 1000000000
---
3000000000
=== hidden
2 3 9
13 1 # 7 # 1 # 1 # 0 # 0 # 1
18 3 2 # # 6 9 # # 2 9 # # 2 0 # # 7 7
13 6 # 8 # 9 # 4 # 7 # 4 # 8
13 2 7 0 2 # # # 9 2 # # 2 9
10 9 8 4 0 # 9 # # # 5
22 8 9 # # 0 2 # # 8 0 # # 5 4 # # 6 5 # # 4 8
3 9 7 6
9 9 # 6 9 0 # # # 0
23 8 4 2 4 0 # 8 9 6 # # # 9 2 3 # # 9 # # # # 6
---
9
9
28
30
27
18
36
13
18
46
=== hidden
15 0 7 0 4 8 # # # # # 0 5 # # 6
2 0 9
3 9 0 6
14 1 8 3 3 9 7 8 # # # # 7 # 0
1 6
15 7 0 # 0 3 6 # # 5 # # 3 # # 3
3 7 7 0
1 1
1 0
17 3 6 0 # 3 2 7 # # # 4 9 3 # # # 2
---
18
9
9
28
6
21
7
1
0
22
=== hidden
24 0 6 6 # 3 # 2 # # 4 9 3 # # # # 9 # 8 8 # 9 # 9
25 3 5 6 7 # 6 # 0 # # # # 6 5 # 0 7 3 # # # 0 # # 2
7 5 4 # # 3 5 7
0
10 3 9 # 3 # 5 # 2 # 7
14 8 8 # 4 # 5 # 0 # 8 # 8 # 2
15 1 # 5 6 5 # # 7 # 0 0 # # # 8
24 2 0 # 2 # 0 # 9 # 2 # 2 # 1 # 4 # 1 # 8 # 5 # 3
2 7 0
21 0 0 8 # # 9 # 8 6 2 # # 2 1 # # # # 4 # 5
---
51
34
17
0
21
23
22
30
7
28
=== hidden
@gen 171671357 big
=== hidden
@gen 171671358 big
=== hidden
@gen 171671359 big

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
    n = r.randint(0, 13) if not big else 200000
    vals, L, R = rand_tree(n, 0, 9) if not big else rand_tree(n, 0, 10**9)
    print(tline(vals, L, R))
```

## Hints
- One number per node is not enough. What does the parent need to know about the child?
- Return a pair: (best if this node is taken, best if it is not).
- Taken → children skipped. Skipped → each child takes its better option.

## Solution
**State design is the heart of tree DP.** "The best answer for this subtree" alone is not enough information for the parent: the parent needs to know whether the child was taken. So every node returns two values, best-with-me and best-without-me.

- If `n` is taken, neither child may be taken: `take = val + skip(left) + skip(right)`.
- If `n` is skipped, each child independently picks its better option: `skip = max(take, skip)(left) + max(take, skip)(right)`.

One postorder pass computes both values for every node, so the time is O(n). The naive recursion "rob(n) = max(val + rob(grandchildren), rob(children))" recomputes the same subtrees over and over: exponential time on a deep tree.

This is the maximum-weight **independent set** on a tree, a problem that is NP-hard on general graphs but linear on trees, because subtrees interact only through their root.

Complexity: O(n) time, O(h) recursion depth; sums up to 2·10¹⁴ need `long long`.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

// {best if n is taken, best if n is skipped}
static pair<long long, long long> best(TreeNode* n) {
    if (!n) return {0, 0};
    auto [lt, ls] = best(n->left);
    auto [rt, rs] = best(n->right);
    long long take = n->val + ls + rs;                // children must be skipped
    long long skip = max(lt, ls) + max(rt, rs);       // children are free to choose
    return {take, skip};
}

long long rob(TreeNode* root) {
    auto [t, s] = best(root);
    return max(t, s);
}
```
