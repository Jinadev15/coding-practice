---
id: cpp-bst-order-queries
title: Kth Smallest, Successor and Predecessor
difficulty: Medium
order: 5
tags: binary search tree, order statistics, successor, predecessor
time_limit: 2
---
## Statement
Answer order queries on a BST with distinct values, **without** parent pointers:

```cpp
int kth_smallest(TreeNode* root, int k);       // 1-based; 1 <= k <= number of nodes
TreeNode* successor(TreeNode* root, int x);    // node with the smallest value  > x, or nullptr
TreeNode* predecessor(TreeNode* root, int x);  // node with the largest value  < x, or nullptr
```

`x` does **not** have to be in the tree. For the tree `20 8 22 4 12 # # # # 10 14`:

```text
          20              kth_smallest(3)  = 10
         /  \             successor(12)    = 14     successor(14) = 20
        8    22           predecessor(10)  = 8      predecessor(4) = none
       / \                successor(13)    = 14     (13 is not in the tree)
      4   12
         /  \
        10   14
```

- **Successor in O(h):** walk down from the root. When the current value is `> x`, it is a candidate: remember it and go **left** to look for a smaller one. Otherwise go **right**. The last candidate is the answer.
- **Predecessor** is symmetric.
- **k-th smallest:** an iterative inorder walk that stops after `k` nodes: O(h + k).

Building the full sorted list for every query is O(n) per query, too slow for 2·10⁵ queries.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input. Each case is a tree line, then `q`, then `q` lines `kth k`, `succ x` or `pred x`. Up to 2·10⁵ nodes and 2·10⁵ queries, of which at most 10 are `kth`. Big trees are random-shaped (height about 40).

**Output:** one line per query: the value, or `none`.

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

static void all(TreeNode* n, vector<int>& v) { if (!n) return; all(n->left, v); v.push_back(n->val); all(n->right, v); }
int kth_smallest(TreeNode* root, int k) { vector<int> v; all(root, v); return v[k - 1]; }
TreeNode* successor(TreeNode* root, int x) { return nullptr; }
TreeNode* predecessor(TreeNode* root, int x) { return nullptr; }
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
        int q = (int)rd_ll();
        string out;
        while (q--) {
            string op = rd_str(); int x = (int)rd_ll();
            if (op == "kth") { out += to_string(kth_smallest(root, x)); }
            else {
                TreeNode* r = op == "succ" ? successor(root, x) : predecessor(root, x);
                out += r ? to_string(r->val) : string("none");
            }
            out += '\n';
        }
        cout << out;
        free_tree(root);
    }
    return 0;
}
```

## Tests
=== sample
11 20 8 22 4 12 # # # # 10 14
8
kth 3
succ 12
succ 14
pred 10
pred 4
succ 13
succ 22
kth 6
---
10
14
20
8
none
14
none
20
=== hidden
1 5
5
kth 1
succ 5
pred 5
succ 4
pred 6
---
5
none
none
5
5
=== hidden
3 2 1 3
6
succ -2147483648
pred 2147483647
succ 3
pred 1
kth 2
kth 3
---
1
3
none
none
2
3
=== hidden
3 -2147483648 # 2147483647
2
succ -2147483648
pred 2147483647
---
2147483647
-2147483648
=== hidden
5 1 # 2 # 3
3
succ 1
pred 3
kth 3
---
2
2
3
=== hidden
3 -13 # 3
3
pred -12
succ -14
succ 2
4 14 12 # -6
3
kth 1
kth 2
pred 12
15 -15 # -14 # -9 # -8 # 6 # 7 # 11 # 17
1
succ 7
13 13 -12 # -20 -6 # # -8 3 # # -1 5
4
succ -8
pred -19
kth 4
kth 6
7 0 -14 12 -17 -1 2 13
6
kth 3
kth 4
pred 348778220
kth 4
succ -16
pred 841137538
5 -7 # 2 # 18
1
succ 17
---
-13
-13
3
-6
12
-6
11
-6
-20
-6
3
-1
0
13
0
-14
13
18
=== hidden
7 -3 -12 3 -18 -4 -2 13
5
succ 12
kth 5
kth 6
kth 7
pred -4
14 -10 -17 -6 # # -9 10 # # 6 17 # # 11
8
succ -10
succ -6
pred 17
kth 6
kth 7
pred 6
kth 8
succ -17
18 -18 # 13 -16 19 -17 8 # # # # 1 # -12 # -14 # -15
3
succ -12
pred 8
succ 20
7 15 -19 # # 0 -9 11
2
kth 1
succ -101841995
1 12
8
kth 1
kth 1
succ 12
pred 12
succ 13
kth 1
pred 12
pred 13
5 -16 # 8 -8 16
7
pred 16
pred -16
kth 2
kth 3
kth 4
kth 1
succ 16
---
13
-2
3
13
-12
-9
6
11
10
11
-6
17
-10
1
1
none
-19
-19
12
12
none
none
none
12
none
12
8
none
-8
8
16
-16
none
=== hidden
13 3 -8 7 -15 # # 11 -19 # # 13 # -16
2
kth 6
succ 3
5 -9 # 0 # 19
8
kth 1
pred -1
succ -9
kth 1
kth 2
kth 2
kth 2
pred -1
10 -8 -15 10 -19 -11 6 13 -20 -18 -14
2
kth 8
kth 2
5 14 -8 # # 7
8
kth 3
kth 1
pred 7
pred 556411121
kth 1
succ 13
succ -9
succ 6
16 8 4 # 1 # -1 # -4 # -8 # -10 # -11 # -18
3
succ -10
succ 4
kth 4
8 -9 -11 -1 -12 # # 13 -19
1
kth 3
---
7
7
-9
-9
0
-9
0
0
0
-9
6
-19
14
-8
-8
14
-8
14
-8
7
-8
8
-8
-11
=== hidden
@gen 2954889063 big
=== hidden
@gen 2954889064 big
=== hidden
@gen 2954889065 big

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
for _ in range(6 if not big else 1):
    n = r.randint(1, 12) if not big else 200000
    L, R = shape(n, r.choice(KINDS) if not big else "random")
    keys = r.sample(range(-10**9, 10**9) if big else range(-20, 20), n)
    vals = bst_vals(L, R, keys)
    print(tline(vals, L, R))
    q = r.randint(1, 8) if not big else 200000
    print(q)
    for i in range(q):
        op = r.choice(["kth", "succ", "pred"]) if (not big or i < 10) else r.choice(["succ", "pred"])
        if op == "kth": print(op, r.randint(1, n))
        else: print(op, r.choice(keys) + r.choice([-1, 0, 0, 1]) if r.random() < 0.9 else r.randint(-10**9, 10**9))
```

## Hints
- Successor: if the current value is greater than x, it is a candidate. Where could an even better candidate be?
- Keep the best candidate so far while walking down a single path. Equal values are not candidates.
- k-th smallest: iterative inorder with an explicit stack, stopping after k pops.

## Solution
**Successor** (smallest value greater than `x`). At each node, either:

- `val > x`: this node qualifies. Any better (smaller) answer must be in its left subtree, so record it and go left.
- `val ≤ x`: this node and its whole left subtree are too small, so go right.

The last recorded candidate is the answer. This works whether or not `x` is in the tree, and it needs no parent pointers. The textbook alternative ("leftmost node of the right subtree, otherwise the nearest ancestor for which we are in the left subtree") is the same walk seen from the node.

**Predecessor** mirrors it. **k-th smallest** runs iterative inorder and stops at the k-th popped node: O(h + k). For many k-th queries on a changing tree, store subtree sizes in each node (an *order-statistic tree*) to answer in O(h).

Complexity: O(h) per successor or predecessor query, O(h + k) per k-th query.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

int kth_smallest(TreeNode* root, int k) {
    vector<TreeNode*> st;
    TreeNode* cur = root;
    while (true) {
        while (cur) { st.push_back(cur); cur = cur->left; }
        cur = st.back(); st.pop_back();
        if (--k == 0) return cur->val;          // the k-th node in sorted order
        cur = cur->right;
    }
}

TreeNode* successor(TreeNode* root, int x) {
    TreeNode* best = nullptr;
    while (root) {
        if (root->val > x) { best = root; root = root->left; }   // candidate; try to find a smaller one
        else root = root->right;                                 // too small: everything on the left is too
    }
    return best;
}

TreeNode* predecessor(TreeNode* root, int x) {
    TreeNode* best = nullptr;
    while (root) {
        if (root->val < x) { best = root; root = root->right; }
        else root = root->left;
    }
    return best;
}
```
