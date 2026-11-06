---
id: cpp-bst-recover
title: Recover a BST with Two Swapped Values
difficulty: Hard
order: 9
tags: binary search tree, inorder, morris traversal, in-place
time_limit: 2
---
## Statement
Exactly two nodes of a BST (distinct values) had their **values** swapped by mistake. Repair the tree **in place**: swap the two values back without moving, creating or deleting any node.

```cpp
void recover(TreeNode* root);
```

```text
      3                 2          inorder 1 3 2 4 → the "descents" point at 3 and 2
     / \               / \
    1   4     ──►     1   4        broken:  3 1 4 # # 2   (2 and 3 swapped)
       /                 /         repaired: 2 1 4 # # 3
      2                 3
```

The inorder sequence of a BST is sorted. Swapping two values creates either **one descent** (the two swapped values were neighbours in sorted order) or **two descents**. The first wrong node is the larger value of the **first** descent; the second is the smaller value of the **last** descent. Track the previous node during an inorder walk, record those two nodes, and swap their values at the end. Doing it with Morris traversal gives O(1) extra memory. A stack or recursion is fine here.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input, one tree line each: a BST (at least 2 nodes) with exactly two values swapped. Up to 2·10⁵ nodes.

Trees can be degenerate chains of up to 2·10⁵ nodes. The driver runs your code on a thread with a 256 MB stack, so plain recursion is safe here (on a normal 8 MB stack it would not be).

**Output:** the repaired tree, one line per case, and `NODES CHANGED` on its own line if the set of node addresses changed.

**Tree format (output).** The driver prints a returned tree as its level-order tokens without the count (`1 2 3 # 4`), `empty` for no nodes, and `nodes=N hash=H` (a fingerprint of the same tokens) when there would be more than 60 tokens.

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

void recover(TreeNode* root) {
    // swaps the first descent only: misses swaps of non-adjacent values
    vector<TreeNode*> st, order; TreeNode* c = root;
    while (c || !st.empty()) { while (c) { st.push_back(c); c = c->left; } c = st.back(); st.pop_back(); order.push_back(c); c = c->right; }
    for (size_t i = 1; i < order.size(); ++i) if (order[i - 1]->val > order[i]->val) { swap(order[i - 1]->val, order[i]->val); return; }
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
static vector<TreeNode*> addrs(TreeNode* root) {
    vector<TreeNode*> v, st; if (root) st.push_back(root);
    while (!st.empty()) { TreeNode* p = st.back(); st.pop_back(); v.push_back(p); if (p->left) st.push_back(p->left); if (p->right) st.push_back(p->right); }
    sort(v.begin(), v.end());
    return v;
}
static int real_main() {
    load_input();
    while (more()) {
        TreeNode* root = rd_tree();
        auto before = addrs(root);
        recover(root);
        bool ok = true;
        cout << show_tree(root, NODES_, &ok) << '\n';
        if (!ok) return 0;
        if (addrs(root) != before) cout << "NODES CHANGED\n";
        free_tree(root);
        NODES_ = 0;
    }
    return 0;
}
```

## Tests
=== sample
6 3 1 4 # # 2
---
2 1 4 # # 3
=== sample
5 1 3 # # 2
---
3 1 # # 2
=== hidden
2 1 2
---
2 1
=== hidden
3 2 # 1
---
1 # 2
=== hidden
3 1 2 3
---
2 1 3
=== hidden
7 4 6 2 1 3 5 7
---
4 2 6 1 3 5 7
=== hidden
7 4 2 6 7 3 5 1
---
4 2 6 1 3 5 7
=== hidden
4 1 2 # 2147483647
---
2147483647 2 # 1
=== hidden
3 -2147483648 2147483647 #
---
2147483647 -2147483648
=== hidden
15 28 -19 9 # # 8 20 -9 # 12 -17 # # # 13
12 0 # 3 # 29 5 # 7 19 # # 8
7 -25 # 8 # 3 # 25
22 27 17 # 12 # 3 # 2 # -7 # -14 # -10 # -17 # -25 # -28 # -30
16 8 -10 29 -3 -7 12 # -21 # # -16 # 26 # -17 -5
9 28 15 29 5 24 # # -15 -8
9 -2 -15 -29 2 -12 # # # -25
10 -20 13 -25 # # -11 # # 12 5
7 8 7 17 -29 4 10 25
21 -14 -23 9 -27 -22 4 -29 12 # # # -5 # # 23 # # # # 14 29
---
-17 -19 9 # # 8 20 -9 # 12 28 # # # 13
0 # 3 # 29 7 # 5 19 # # 8
-25 # 3 # 8 # 25
27 17 # 12 # 3 # 2 # -7 # -10 # -14 # -17 # -25 # -28 # -30
8 -10 29 -16 -7 12 # -21 # # -3 # 26 # -17 -5
28 15 29 -8 24 # # -15 5
-2 -15 2 -29 -12 # # # -25
-20 -25 13 # # -11 # # 12 5
8 4 17 -29 7 10 25
-14 -23 9 -27 -22 4 12 -29 # # # -5 # # 23 # # # # 14 29
=== hidden
3 22 # -11
2 -14 0
11 -29 -24 # 19 2 # # -9 # -19 -8
20 6 -7 16 -14 -4 10 24 # -13 # # # 22 15 # # # # # 21
2 -21 14
10 4 -13 19 -20 2 9 25 -29 -12 -16
4 15 -13 -26 18
14 27 6 # 16 # 2 # -5 # -6 # -7 # -14
13 -5 -11 -6 -24 # # 9 -29 -14 # # # -28
6 27 7 # 22 # 25
---
-11 # 22
0 -14
19 -24 # -29 2 # # -9 # -19 -8
6 -7 16 -14 -4 10 24 # -13 # # # 15 22 # # # # # 21
14 -21
4 -13 19 -20 2 9 25 -29 -16 -12
15 -13 18 -26
27 16 # 6 # 2 # -5 # -6 # -7 # -14
-6 -11 -5 -24 # # 9 -29 -14 # # # -28
27 25 # 22 # 7
=== hidden
3 -9 -2 17
21 -23 -29 24 # -25 -3 19 # # -14 0 15 10 -18 # # # # # # 25
23 26 # -26 # -22 # -11 # -4 # 2 # 9 # 11 # 18 # 21 # 25 # -27
20 24 -30 # # -1 -4 17 -10 -2 5 # # # # # # 6 11 # 12
13 -20 -30 -7 # # # 26 15 # 6 17 -12 9
6 6 -18 # -20 8 -28
21 -29 # -17 # -4 # 0 # 7 # 10 # 18 # 12 # 11 # 23 # 26
4 -4 -26 9 -11
18 29 23 # 22 # 8 # 6 # 4 # -13 # 3 # -14 # -22
19 -22 # -21 # 24 # -18 # -16 # -8 # -4 # -1 # 0 # -20
---
-2 -9 17
-23 -29 10 # -25 -3 19 # # -14 0 15 24 -18 # # # # # # 25
-27 # -26 # -22 # -11 # -4 # 2 # 9 # 11 # 18 # 21 # 25 # 26
24 -30 # # -1 -4 17 -10 -2 5 # # # # # # 12 11 # 6
-20 -30 -12 # # # 26 15 # 6 17 -7 9
8 -18 # -20 6 -28
-29 # -17 # -4 # 0 # 7 # 10 # 11 # 12 # 18 # 23 # 26
-4 -11 9 -26
29 23 # 22 # 8 # 6 # 4 # 3 # -13 # -14 # -22
-22 # -21 # -20 # -18 # -16 # -8 # -4 # -1 # 0 # 24
=== hidden
@gen 1498006562 big
=== hidden
@gen 1498006563 big
=== hidden
@gen 1498006564 big

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
    n = r.randint(2, 13) if not big else 200000
    L, R = shape(n, r.choice(KINDS))
    vals = bst_vals(L, R, r.sample(range(-10**9, 10**9) if big else range(-30, 30), n))
    order = inorder(L, R)
    if r.random() < 0.4:
        k = r.randrange(n - 1); i, j = order[k], order[k + 1]
    else:
        i, j = r.sample(range(n), 2)
    vals[i], vals[j] = vals[j], vals[i]
    print(tline(vals, L, R))
```

## Hints
- The inorder sequence of a valid BST is strictly increasing. What does a swap of two values do to it?
- Track the previous node in inorder. At each place where prev > current, update your two candidates.
- First candidate: prev at the FIRST descent. Second candidate: current at the LAST descent. Then swap the values.

## Solution
In sorted order, swapping two values `a < b` (at positions i < j) produces:

- **Two descents** when they are not neighbours: `… b … a …`. `b` is followed by something smaller, and `a` is preceded by something larger. The first descent's **left** element is `b`, and the last descent's **right** element is `a`.
- **One descent** when they are neighbours: `… b a …`. Its left element is `b` and its right element is `a`.

So during the inorder walk, at every descent `prev > cur`: set `first = prev` the first time, and always set `second = cur`. Both cases are handled by the same two lines. Swap the two values at the end. The nodes themselves never move, which is what "in place" means here.

The walk uses Morris traversal, so the extra memory is O(1) and the temporary threads are removed before the function returns. With a stack or recursion it would be O(h).

Complexity: O(n) time, O(1) extra memory.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

void recover(TreeNode* root) {
    TreeNode *first = nullptr, *second = nullptr, *prev = nullptr;
    auto visit = [&](TreeNode* n) {
        if (prev && prev->val > n->val) {      // a descent in the inorder sequence
            if (!first) first = prev;          // larger value of the first descent
            second = n;                        // smaller value of the latest descent
        }
        prev = n;
    };
    // Morris inorder: O(1) extra memory, tree restored as we go
    TreeNode* cur = root;
    while (cur) {
        if (!cur->left) { visit(cur); cur = cur->right; continue; }
        TreeNode* pred = cur->left;
        while (pred->right && pred->right != cur) pred = pred->right;
        if (!pred->right) { pred->right = cur; cur = cur->left; }
        else { pred->right = nullptr; visit(cur); cur = cur->right; }
    }
    swap(first->val, second->val);
}
```
