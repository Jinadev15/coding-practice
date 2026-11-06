---
id: cpp-tc-maximum-tree
title: Maximum Binary Tree with a Monotonic Stack
difficulty: Medium
order: 6
tags: binary tree, construction, monotonic stack, cartesian tree
time_limit: 2
---
## Statement
The **maximum binary tree** of an array of distinct numbers is defined recursively: the root is the maximum element, its left subtree is the maximum tree of the part **left** of the maximum, and its right subtree is the maximum tree of the part to its **right**.

```cpp
TreeNode* construct_maximum(const vector<int>& a);
```

```text
a = 3 2 1 6 0 5            6
                         /   \
                        3     5
                         \   /
                          2 0
                           \
                            1
```

Following the definition literally costs O(n²) on sorted input (each level scans the whole remaining range). Build it in **O(n)** with a **monotonic stack**. Scan left to right and keep the "right spine" of the tree built so far, with values decreasing from bottom to top. For a new value `x`:

- every stack node smaller than `x` is popped, and the **last popped** one becomes `x`'s **left** child;
- if the stack is still not empty, `x` becomes the **right** child of the new top;
- push `x`.

(This tree is also called a *Cartesian tree*. Its inorder is the original array, and it has the heap property. It is the bridge between "nearest greater element" and range-maximum queries.)

**Input:** cases until the end of input. Each case is a line `n` (1 ≤ n ≤ 2·10⁵), then `n` distinct integers that fit in `int`.

Trees can be degenerate chains of up to 2·10⁵ nodes. The driver runs your code on a thread with a 256 MB stack, so plain recursion is safe here (on a normal 8 MB stack it would not be).

**Output:** the tree, one line per case.

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

TreeNode* construct_maximum(const vector<int>& a) { return nullptr; }
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
        int n = (int)rd_ll();
        vector<int> a(n);
        for (int& x : a) x = (int)rd_ll();
        TreeNode* root = construct_maximum(a);
        bool ok = true;
        cout << show_tree(root, n, &ok) << '\n';
        if (ok) free_tree(root);
        else return 0;
    }
    return 0;
}
```

## Tests
=== sample
6
3 2 1 6 0 5
---
6 3 5 # 2 0 # # 1
=== hidden
1
-5
---
-5
=== hidden
4
1 2 3 4
---
4 3 # 2 # 1
=== hidden
4
4 3 2 1
---
4 # 3 # 2 # 1
=== hidden
7
2 7 1 5 3 6 4
---
7 2 6 # # 5 4 1 3
=== hidden
12
-5 -10 4 -11 19 -14 1 14 -8 17 2 6
3
-13 17 14
9
19 9 -19 -17 11 6 -7 8 -5
6
-19 -3 -15 1 7 -13
8
14 -10 15 -6 3 -14 -20 -11
---
19 4 17 -5 -11 14 6 # -10 # # 1 -8 2 # # # -14
17 -13 14
19 # 11 9 8 # -17 6 -5 -19 # # -7
7 1 -13 -3 # # # -19 -15
15 14 3 # -10 -6 -11 # # # # -14 # # -20
=== hidden
4
1 -12 -9 15
1
14
4
4 9 12 3
5
2 12 3 -2 -9
4
18 6 16 0
---
15 1 # # -9 -12
14
12 9 3 4
12 2 3 # # # -2 # -9
18 # 16 6 0
=== hidden
10
8 3 18 -3 -1 14 -9 -16 2 11
11
-14 18 19 3 14 11 9 -5 5 -8 -3
7
-19 7 -7 19 -16 11 -12
4
17 18 -6 0
12
8 -16 2 0 15 -18 -17 9 -11 -10 7 17
---
18 8 14 # 3 -1 11 # # -3 # 2 # # # -9 # # -16
19 18 14 -14 # 3 11 # # # # # 9 # 5 -5 -3 # # -8
19 7 11 -19 -7 -16 -12
18 17 0 # # -6
17 15 # 8 9 # 2 -17 7 -16 0 -18 # -10 # # # # # # # -11
=== hidden
@gen 4294070542 big
=== hidden
@gen 4294070543 big
=== hidden
@gen 4294070544 big

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
for _ in range(5 if not big else 2):
    n = r.randint(1, 12) if not big else 200000
    a = r.sample(range(-10**9, 10**9) if big else range(-20, 20), n)
    if big and r.random() < 0.6: a.sort(reverse=r.random() < 0.5)
    print(n); print(*a)
```

## Hints
- Keep a stack of nodes with decreasing values. It is the right spine of the tree built so far.
- Pop every node smaller than the new value. The last one popped becomes the new node's left child.
- After popping, if the stack isn't empty, the new node becomes the top's right child. The answer is the bottom of the stack.

## Solution
**Why it works:** look at where `x` ends up. Its parent is the *smaller* of its two nearest greater neighbours (the nearest greater element to the left, and the nearest greater element to the right). The stack maintains exactly the elements that are still candidates as "nearest greater to the left" for future elements, which is the right spine of the tree built so far.

When `x` arrives:

- Nodes on the spine smaller than `x` can't be ancestors of `x`. They belong in `x`'s left subtree, and they are already linked to each other as a right-going chain. So the last one popped (the largest of them) becomes `x->left`, and the rest hang beneath it.
- The new top (if any) is greater than `x` and is its nearest greater element on the left, so `x` becomes its right child (replacing the chain that just moved under `x`).

Each element is pushed once and popped at most once: **O(n)** total, even though one step may pop many nodes (an amortised argument).

Complexity: O(n) time, O(n) stack in the worst case (decreasing input).

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

TreeNode* construct_maximum(const vector<int>& a) {
    vector<TreeNode*> st;                 // right spine, values decreasing bottom -> top
    for (int x : a) {
        TreeNode* n = new TreeNode(x);
        TreeNode* last = nullptr;
        while (!st.empty() && st.back()->val < x) { last = st.back(); st.pop_back(); }
        n->left = last;                   // the popped chain hangs under x on the left
        if (!st.empty()) st.back()->right = n;   // x is the right child of the nearest greater on its left
        st.push_back(n);
    }
    return st.empty() ? nullptr : st.front();    // the bottom of the stack is the global maximum
}
```
