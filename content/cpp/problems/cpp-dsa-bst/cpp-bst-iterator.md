---
id: cpp-bst-iterator
title: A BST Iterator with O(h) Memory
difficulty: Medium
order: 6
tags: binary search tree, iterator, stack, amortized analysis
time_limit: 2
---
## Statement
Implement an iterator over a BST in ascending order, like the iterators of `std::set`:

```cpp
class BSTIterator {
public:
    explicit BSTIterator(TreeNode* root);
    bool hasNext();   // is there a next value?
    int next();       // return the next smallest value (only called when hasNext() is true)
};
```

Requirements: `next()` and `hasNext()` run in **amortized O(1)**, and the iterator uses **O(h)** memory, so copying all n values into a vector up front is not allowed in spirit. This is the "paused" version of iterative inorder: the stack holds the left spine still to be visited. `next()` pops a node, then pushes the left spine of its right child.

Trees can be chains of 3·10⁵ nodes, and your code runs on the **normal 8 MB stack**, so keep the traversal iterative: the stack you manage yourself lives on the heap.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input. Each case is a tree line (a valid BST), then a line `m` and a line of `m` operations, each `n` (call `next()`) or `h` (call `hasNext()`). Up to 3·10⁵ nodes and 3·10⁵ operations; `n` is only issued when a next value exists.

**Output:** the results in order (the value for `n`, `1`/`0` for `h`) as one list. Lists of more than 60 numbers are printed as `count=C hash=H` (a fingerprint), shorter ones in full; an empty list prints `(none)`.

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

class BSTIterator {
public:
    explicit BSTIterator(TreeNode* root) : cur(root) {}
    bool hasNext() { return cur != nullptr; }
    int next() { int v = cur->val; cur = cur->right; return v; }   // follows right pointers only
private:
    TreeNode* cur;
};
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
        TreeNode* root = rd_tree();
        int m = (int)rd_ll();
        vector<long long> res; res.reserve(m);
        {
            BSTIterator it(root);
            for (int i = 0; i < m; ++i) {
                string op = rd_str();
                if (op == "n") res.push_back(it.next());
                else res.push_back(it.hasNext() ? 1 : 0);
            }
        }
        cout << show_vec(res) << '\n';
        free_tree(root);
    }
    return 0;
}
```

## Tests
=== sample
7 7 3 15 # # 9 20
11
n n h n h n h n h h h
---
3 7 1 9 1 15 1 20 0 0 0
=== hidden
0
2
h h
---
0 0
=== hidden
1 4
3
h n h
---
1 4 0
=== hidden
5 1 # 2 # 3
4
n n n h
---
1 2 3 0
=== hidden
5 3 2 # 1 #
4
n n n h
---
1 2 3 0
=== hidden
7 4 2 6 1 3 5 7
8
n n n n n n n h
---
1 2 3 4 5 6 7 0
=== hidden
1 23
13
n h h h h h h h h h h h h
0
9
h h h h h h h h h
0
14
h h h h h h h h h h h h h h
15 -24 -27 9 # # -5 12 -12 # # 23 -23 -7 # 25
10
n n h n n n n h n n
14 11 -30 12 # -10 # 23 -27 0 # # # # -1
2
h n
16 -1 -13 9 # -7 0 18 # # # # 13 29 11 14 28
3
n h h
3 -8 # 29
8
n n h h h h h h
20 14 -21 18 -25 -1 # 26 -29 # -17 4 # # # # # -8 2 # -11
11
h n h h n h n n n n n
---
23 0 0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0 0 0 0
-27 -24 1 -23 -12 -7 -5 1 9 12
1 -30
-13 1 1
-8 29 0 0 0 0 0 0
1 -29 1 1 -25 1 -21 -17 -11 -8 -1
=== hidden
15 -9 -30 21 # # 0 29 # 20 25 # 13 # # 27
4
n n n n
6 3 -28 9 # # 5
3
n n n
17 21 -29 # # 11 -19 # # 10 -10 # # 7 0 # # 5
16
n n n n h n n n n h h h h n h h
21 23 -29 27 # -23 # # # 6 1 # -6 # -17 -5 # # # -4 # -1
4
h n n n
13 28 -24 # # 24 -14 # # 19 -5 # # -4
11
n h n h h n n n n n h
9 -20 # 6 # 16 # 27 # 28
11
h n n n n n h h h h h
7 -29 # 3 -13 24 -19 -12
14
n h h n n h n n h n h h h h
20 23 17 # 11 # 9 # 5 # 4 # -19 # -21 # -23 # -28 # -29
3
h h n
---
-30 -9 0 13
-28 3 5
-29 -19 -10 0 1 5 7 10 11 1 1 1 1 21 0 0
1 -29 -23 -17
-24 1 -14 1 1 -5 -4 19 24 28 0
1 -20 6 16 27 28 0 0 0 0 0
-29 1 1 -19 -13 1 -12 3 1 24 0 0 0 0
1 1 -29
=== hidden
5 -11 # -9 # 17
13
n h n n h h h h h h h h h
10 -25 -29 -20 # # # -1 # 10 2
8
n n n n n n h h
9 29 -28 # # 22 -25 # # -13
9
n n n n n h h h h
0
6
h h h h h h
6 -14 # 19 2 # -12
10
h n n n n h h h h h
21 16 -23 # # 11 -19 # # 5 -16 # # 0 -15 # # -4 -7 # # -6
16
n h n h n n h n n n n h n h h h
20 -24 -26 20 -28 -25 10 26 # # # # -10 12 # # -13 # # # -20
4
n h n n
6 -3 -18 22 -23 -15 7
10
n h n n h n n n h h
---
-11 1 -9 17 0 0 0 0 0 0 0 0 0
-29 -25 -20 -1 2 10 0 0
-28 -25 -13 22 29 0 0 0 0
0 0 0 0 0 0
1 -14 -12 2 19 0 0 0 0 0
-23 1 -19 1 -16 -15 1 -7 -6 -4 0 1 5 1 1 1
-28 1 -26 -25
-23 1 -18 -15 1 -3 7 22 0 0
=== hidden
@gen 2253441553 big
=== hidden
@gen 2253441554 big
=== hidden
@gen 2253441555 big

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
def ops_for(n, m):
    ops, left = [], n
    for _ in range(m):
        if left and r.random() < 0.7: ops.append("n"); left -= 1
        else: ops.append("h")
    return ops
for _ in range(8 if not big else 1):
    n = r.randint(0, 12) if not big else 300000
    L, R = shape(n, r.choice(KINDS) if not big else r.choice(["left", "zigzag"]))
    vals = bst_vals(L, R, r.sample(range(-10**9, 10**9) if big else range(-30, 30), n))
    print(tline(vals, L, R))
    m = r.randint(1, 16) if not big else 300000
    o = ops_for(n, m); print(m); print(" ".join(o))
```

## Hints
- Store the left spine on a stack: the smallest value is the deepest node on the left.
- After popping a node, its successor lives in its right subtree. Which nodes of that subtree should be pushed?
- Count pushes over the whole iteration to see why the average cost is O(1).

## Solution
**Invariant:** the stack holds, from the top, the next node to return and then the ancestors that are still waiting for their turn, each of which will be returned after its left subtree is finished. It is exactly the explicit stack of iterative inorder, frozen between calls.

- **Constructor:** push the left spine of the root. The smallest value ends up on top.
- **`next()`:** pop the top `n`, which is the smallest unvisited value. Its successor is either the leftmost node of `n->right` (push that spine) or, if there is no right child, the next node already on the stack.
- **`hasNext()`:** the stack is not empty.

**Amortized O(1):** each node is pushed once and popped once over the whole iteration. A single `next()` can push h nodes, but n calls push n nodes in total. Memory is O(h), the height of the tree.

The same class gives you a reverse iterator (push right spines, pop, push the left child's right spine). Running one of each from both ends gives two-sum in a BST in O(h) memory.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

class BSTIterator {
public:
    explicit BSTIterator(TreeNode* root) { push_left(root); }
    bool hasNext() { return !st.empty(); }
    int next() {
        TreeNode* n = st.back(); st.pop_back();   // the smallest unvisited value
        push_left(n->right);                      // its successor is the leftmost node of its right subtree
        return n->val;
    }
private:
    vector<TreeNode*> st;                         // left spine still to visit, deepest node on top
    void push_left(TreeNode* n) { for (; n; n = n->left) st.push_back(n); }
};
```
