---
id: cpp-bst-delete
title: Delete from a BST (All Three Cases)
difficulty: Medium
order: 4
tags: binary search tree, delete, successor, pointer surgery
time_limit: 2
---
## Statement
Delete a value from a BST and return the (possibly new) root:

```cpp
TreeNode* bst_delete(TreeNode* root, int x);   // if x is absent, change nothing
```

Find the node, then handle the three cases:

1. **No children:** remove the leaf.
2. **One child:** splice it out by linking its parent directly to its only child.
3. **Two children:** its **inorder successor** `s` (the leftmost node of its right subtree) has no left child. Copy `s->val` into the node, then remove `s` from the right subtree (case 1 or 2).

```text
delete 3:        5                5          3 has two children: its successor is 4.
                / \              / \         Copy 4 into the node and remove the old 4.
               3   8    ──►     4   8
              / \              /
             2   4            2
```

To make the answer unique, the two-children case **must** use the inorder successor (not the predecessor). Removed nodes must be released with `delete`. The checker runs under LeakSanitizer.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input. Each case is a tree line (a valid BST with distinct values), then a line `k` and a line with `k` values to delete, in order. Up to 2·10⁵ nodes and 10⁵ deletions. Trees with more than 5000 nodes are random-shaped (height about 40).

**Output:** the final tree, one line per case.

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

TreeNode* bst_delete(TreeNode* root, int x) { return root; }
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
        long long lim = NODES_;
        int k = (int)rd_ll();
        while (k--) root = bst_delete(root, (int)rd_ll());
        bool ok = true;
        cout << show_tree(root, lim, &ok) << '\n';
        if (ok) free_tree(root);
        else return 0;
        NODES_ = 0;
    }
    return 0;
}
```

## Tests
=== sample
5 5 3 8 2 4
1
3
---
5 4 8 2
=== sample
7 50 30 70 20 40 60 80
3
20 30 50
---
60 40 70 # # # 80
=== hidden
0
1
5
---
empty
=== hidden
1 7
1
7
---
empty
=== hidden
1 7
1
8
---
7
=== hidden
3 2 1 3
3
2 1 3
---
empty
=== hidden
5 1 # 2 # 3
1
1
---
2 # 3
=== hidden
7 4 2 6 1 3 5 7
2
6 4
---
5 2 7 1 3
=== hidden
6 10 5 # # 8 7
1
5
---
10 8 # 7
=== hidden
11 14 -20 16 # -5 # # -11 # # -7
7
-16 16 -4 14 -7 -11 16
13 -16 # -9 # 2 # 7 # 15 # 16 # 19
6
15 -9 -9 7 2 15
5 8 -10 18 -14 -4
4
-14 -10 -10 8
1 17
8
-19 17 17 17 17 17 17 17
6 15 -2 # -4 # -14
7
12 15 -2 -14 -2 -4 -4
21 -9 -14 16 # # 15 # 10 # 9 14 7 # 12 # 2 # # # 0 5
8
14 14 -9 16 2 10 15 5
20 -16 -17 19 # # -6 # -9 -2 -11 -8 -5 8 # # # # # -4 2
0

18 14 7 # 3 # -5 # -6 # -9 # -11 # -12 # -16 # -17
4
20 3 21 7
---
-20 # -5
-16 # 16 # 19
18 -4
empty
empty
0 -14 12 # # 9 # 7
-16 -17 19 # # -6 # -9 -2 -11 -8 -5 8 # # # # # -4 2
14 -5 # -6 # -9 # -11 # -12 # -16 # -17
=== hidden
22 19 -15 # # 17 -12 # # 16 -10 # # 13 -3 # # 12 4 # # 9 8
6
4 -19 19 8 -11 9
20 16 15 # 7 # 2 # 1 # -6 # -7 # -8 # -11 # -14 # -20
1
2
1 -9
0

4 6 -9 # -10
10
-9 -9 -9 4 -12 6 -9 -10 -10 -12
12 15 8 # -13 # -18 0 # # # 7 1
4
-18 0 8 1
10 5 -2 7 -14 4 6 12 -18 -10 1
9
4 6 12 4 7 -10 7 -10 12
9 9 -19 # # 7 -15 # # -2
5
-15 -19 -21 -2 9
8 17 -4 # -16 10 -17 -8 -1
10
12 10 -17 10 10 17 -16 -17 -4 -16
---
-15 # 17 -12 # # 16 -10 # # 13 -3 # # 12
16 15 # 7 # 1 # -6 # -7 # -8 # -11 # -14 # -20
-9
empty
15 -13 # # 7
5 -2 # -14 1 -18
7
-1 -8
=== hidden
11 13 -17 16 -19 -1 # # # # -6 4
2
-19 -19
2 12 4
4
12 4 12 12
5 5 -16 # # -15
4
-15 -15 -16 -16
13 15 -17 # # 8 -16 # # 2 -5 # # -4
9
-17 -17 -16 -5 2 -17 -17 -17 15
13 19 -19 # # 17 -13 # # 5 -6 # # 2
10
-7 -6 -19 -6 -13 -6 5 11 -6 -4
19 -10 -13 7 -14 -12 -8 13 -20 # # # # 3 # # # # -4 6
6
-20 6 -12 -8 -12 7
4 -11 # 2 1
2
2 1
6 13 10 # -5 # -15
6
13 -15 -5 10 -15 1
---
13 -17 16 # -1 # # -6 4
empty
5
8 -4
19 17 # 2
-10 -13 13 -14 # 3 # # # -4
-11
empty
=== hidden
@gen 1410382902 big
=== hidden
@gen 1410382903 big
=== hidden
@gen 1410382904 big

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
for _ in range(8 if not big else 1):
    n = r.randint(0, 12) if not big else 200000
    L, R = shape(n, r.choice(KINDS) if not big else "random")
    keys = r.sample(range(-10**9, 10**9) if big else range(-20, 20), n)
    vals = bst_vals(L, R, keys)
    print(tline(vals, L, R))
    k = r.randint(0, 10) if not big else 100000
    ds = [r.choice(keys) if keys and r.random() < 0.8 else r.randint(-21, 21) for _ in range(k)]
    print(k); print(*ds)
```

## Hints
- Locate the node and keep track of the pointer that points to it (or its parent).
- 0 or 1 child: replace the node by its only child (or by nullptr).
- 2 children: copy the value of the leftmost node of the right subtree, then delete that node, which has no left child.

## Solution
**Find** the node with a pointer-to-pointer `link`, the address of the pointer that refers to it (`&root` or a parent's `left`/`right`). Then the removal itself is one assignment.

- **Leaf or one child:** `*link = n->left ? n->left : n->right`. The parent now points at the only child (or at `nullptr`). Then `delete n`.
- **Two children:** removing `n` directly would leave two orphan subtrees. Its inorder successor `s` (go right once, then left as far as possible) is the smallest value larger than `n`, so putting that value in `n` keeps the BST order. `s` has no left child (otherwise that child would be smaller), so deleting `s` is the easy case. We just repeat the splice on `s`'s link.

Why the successor keeps the order: every value in `n`'s left subtree is smaller than `n` < `s`, and every other value in the right subtree is larger than `s`.

Complexity: O(h) per deletion. Each deleted node is freed exactly once.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

TreeNode* bst_delete(TreeNode* root, int x) {
    TreeNode** link = &root;                          // the pointer that points at the current node
    while (*link && (*link)->val != x)
        link = x < (*link)->val ? &(*link)->left : &(*link)->right;
    TreeNode* n = *link;
    if (!n) return root;                              // not found
    if (n->left && n->right) {                        // case 3: two children
        TreeNode** s = &n->right;                     // leftmost node of the right subtree
        while ((*s)->left) s = &(*s)->left;
        n->val = (*s)->val;                           // take over the successor's value
        link = s; n = *s;                             // ...and delete the successor instead (it has no left child)
    }
    *link = n->left ? n->left : n->right;             // cases 1 and 2: splice out
    delete n;
    return root;
}
```
