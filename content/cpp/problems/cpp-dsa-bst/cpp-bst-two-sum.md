---
id: cpp-bst-two-sum
title: Two Sum in a BST with Two Iterators
difficulty: Medium
order: 7
tags: binary search tree, two pointers, iterator, stack
time_limit: 2
---
## Statement
Do two **different** nodes of the BST have values that add up to `target`?

```cpp
bool two_sum(TreeNode* root, long long target);
```

On a sorted array you'd use two pointers from both ends. A BST *is* a sorted sequence, so do the same with **two iterators**: a forward one (smallest first, stack of left spines) and a backward one (largest first, stack of right spines). Move the forward iterator when the sum is too small and the backward one when it is too large, and stop when they meet. That's O(n) time and only O(h) memory. (A hash set also gives O(n) time but O(n) memory; that's acceptable here, but the iterator version is the point.)

```text
        5           target 9  → true  (2 + 7, or 3 + 6)
       / \          target 28 → false
      3   6         target 10 → false (5 + 5 would use the same node twice)
     / \   \
    2   4   7
```

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input. Each case is a tree line (a valid BST with distinct values), then a line `k` (1 ≤ k ≤ 5) and a line with `k` targets. Up to 2·10⁵ nodes; values fit in `int`, targets in `long long`.

Trees can be degenerate chains of up to 2·10⁵ nodes. The driver runs your code on a thread with a 256 MB stack, so plain recursion is safe here (on a normal 8 MB stack it would not be).

**Output:** one line per case with `k` answers (`1` = yes, `0` = no) separated by spaces.

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
bool two_sum(TreeNode* root, long long target) {
    vector<int> v; all(root, v);                     // O(n^2) pair check
    for (size_t i = 0; i < v.size(); ++i) for (size_t j = i + 1; j < v.size(); ++j) if ((long long)v[i] + v[j] == target) return true;
    return false;
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
        int k = (int)rd_ll();
        for (int i = 0; i < k; ++i) cout << (i ? " " : "") << (two_sum(root, rd_ll()) ? 1 : 0);
        cout << '\n';
        free_tree(root);
    }
    return 0;
}
```

## Tests
=== sample
7 5 3 6 2 4 # 7
3
9 28 10
---
1 0 1
=== hidden
0
1
0
---
0
=== hidden
1 5
2
10 5
---
0 0
=== hidden
2 1 #
1
1
---
0
=== hidden
3 2147483647 2147483646 #
2
4294967293 4294967294
---
1 0
=== hidden
3 -2147483648 # 2147483647
1
-1
---
1
=== hidden
7 4 2 6 1 3 5 7
5
3 13 14 2 8
---
1 1 0 0 1
=== hidden
5 -2 -16 2 -19 -11
2
-30 -17
11 15 -8 19 -19 -7 18 # # -18 # 7
1
-4
10 -10 -14 -6 # # # -5 # 18 12
3
-24 -16 -24
18 -16 # 19 -12 # # 12 -4 # # -3 # -1 # 2 # 10 5
1
7
0
4
40 9 -4 -12
2 14 -10
2
-20 4
8 3 -6 18 -8 0 9 19 -17
3
-8 13 0
8 -11 -17 7 -18 -12 -2 10 -19
4
-2 -7 -26 8
---
1 1
1
1 1 1
1
0 0 0 0
0 1
1 1 0
1 1 0 1
=== hidden
3 6 -14 9
4
12 18 -3 -28
18 13 12 # -10 # -11 10 -18 # -5 # # # # -3 # 9 2
3
-29 -21 5
4 5 0 # -18
1
-13
19 -19 # 8 4 11 -14 5 # 17 # -6 # # 12 # # # # 13
5
-25 13 23 -5 22
8 10 -8 13 # 5 # # 3
1
4
2 2 -16
4
-14 -14 0 -2
1 -17
3
14 37 41
3 3 # 6
1
-41
---
0 0 0 0
1 1 1
1
1 1 1 0 1
0
1 1 0 0
0 0 0
0
=== hidden
12 -10 # 16 14 18 -2 # # # # 11 2
4
9 -32 -2 16
11 -2 -10 11 -18 -5 4 13 -19 -11 -7 -3
3
6 -36 -21
0
2
-11 22
2 5 -9
2
-4 -4
6 16 11 # 10 # -7
2
21 9
3 -1 # 1
2
0 0
14 16 6 # -16 # -19 -9 # # -12 -1 # # -4
3
-13 35 -38
12 18 16 # 15 # 10 # 0 # -1 # -5
2
36 32
---
1 0 0 1
1 0 1
0 0
1 1
1 1
1 1
1 0 0
0 0
=== hidden
@gen 4219083843 big
=== hidden
@gen 4219083844 big
=== hidden
@gen 4219083845 big

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
for _ in range(8 if not big else 2):
    n = r.randint(0, 12) if not big else 200000
    L, R = shape(n, r.choice(KINDS))
    keys = r.sample(range(-10**9, 10**9) if big else range(-20, 20), n)
    vals = bst_vals(L, R, keys)
    print(tline(vals, L, R))
    k = r.randint(1, 5) if not big else 5
    ts = []
    for _ in range(k):
        if keys and len(keys) > 1 and r.random() < 0.5: a, b = r.sample(keys, 2); ts.append(a + b)
        elif keys and r.random() < 0.5: ts.append(2 * r.choice(keys))
        else: ts.append(r.randint(-41, 41) if not big else 3 * 10**9)
    print(k); print(*ts)
```

## Hints
- On a sorted array this is the classic two-pointer technique. What gives you a BST's values in sorted order, and in reverse order?
- Build a forward and a backward iterator, each with a stack of spine nodes.
- Stop when both iterators reach the same node. Compute the sum in `long long`.

## Solution
The two-pointer argument for sorted arrays carries over unchanged. Let `a` be the smallest unused value and `b` the largest. If `a + b < target`, then `a` can't pair with anything (`b` is already the largest), so discard `a`. If `a + b > target`, discard `b`. Each step discards one value, so at most n − 1 steps happen before the pointers meet.

The "pointers" are BST iterators: a forward one (push left spines, pop, push the right child's left spine) and a mirrored backward one. Both use O(h) memory. Comparing the **nodes** they point at, not the values, guarantees the two values come from different nodes. Since values are distinct, the iterators meet exactly when only one unused node remains.

Sums are computed in `long long`: two values near `INT_MAX` overflow `int`.

Complexity: O(n) time and O(h) memory per target.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

// in-order iterator in either direction, O(h) memory
struct Iter {
    vector<TreeNode*> st;
    bool fwd;
    Iter(TreeNode* root, bool forward) : fwd(forward) { push(root); }
    void push(TreeNode* n) { for (; n; n = fwd ? n->left : n->right) st.push_back(n); }
    TreeNode* peek() const { return st.back(); }
    void advance() { TreeNode* n = st.back(); st.pop_back(); push(fwd ? n->right : n->left); }
};

bool two_sum(TreeNode* root, long long target) {
    if (!root) return false;
    Iter lo(root, true), hi(root, false);
    while (lo.peek() != hi.peek()) {                 // two different nodes
        long long s = (long long)lo.peek()->val + hi.peek()->val;
        if (s == target) return true;
        if (s < target) lo.advance();                 // need a bigger sum
        else hi.advance();                            // need a smaller sum
    }
    return false;
}
```
