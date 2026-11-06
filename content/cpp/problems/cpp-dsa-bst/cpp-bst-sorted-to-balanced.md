---
id: cpp-bst-sorted-to-balanced
title: Sorted Array to a Height-Balanced BST
difficulty: Easy
order: 2
tags: binary search tree, divide and conquer, balanced, construction
time_limit: 2
---
## Statement
Turn a strictly increasing array into a **height-balanced** BST (the subtree heights of every node differ by at most 1):

```cpp
TreeNode* sorted_to_bst(const vector<int>& a);
```

Make the middle element the root, and build the two halves recursively. To make the answer unique, the root of `a[lo..hi]` is **`a[lo + (hi − lo) / 2]`** (the lower middle when the length is even).

```text
a = -10 -3 0 5 9          0
                         / \
                      -10   5
                         \   \
                         -3   9
```

The height is ⌈log₂(n+1)⌉, so the recursion depth is only about 18 for n = 2·10⁵. This is also how you **rebalance** a degenerate BST: inorder → sorted array → this function.

**Input:** cases until the end of input. Each case is a line `n` (0 ≤ n ≤ 2·10⁵), then the `n` strictly increasing values (they fit in `int`).

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

TreeNode* sorted_to_bst(const vector<int>& a) {
    // a chain: correct BST, not balanced
    TreeNode* root = nullptr;
    for (int i = (int)a.size() - 1; i >= 0; --i) root = new TreeNode(a[i], nullptr, root);
    return root;
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
int main() { return real_main(); }   // the normal 8 MB stack: deep recursion crashes here
static int real_main() {
    load_input();
    while (more()) {
        int n = (int)rd_ll();
        vector<int> a(n);
        for (int& x : a) x = (int)rd_ll();
        TreeNode* root = sorted_to_bst(a);
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
5
-10 -3 0 5 9
---
0 -10 5 # -3 # 9
=== sample
4
1 2 3 4
---
2 1 3 # # # 4
=== hidden
0
---
empty
=== hidden
1
-2147483648
---
-2147483648
=== hidden
2
1 2
---
1 # 2
=== hidden
3
1 2 3
---
2 1 3
=== hidden
7
1 2 3 4 5 6 7
---
4 2 6 1 3 5 7
=== hidden
2
-2147483648 2147483647
---
-2147483648 # 2147483647
=== hidden
13
-50 -47 -40 -15 -14 -11 -10 -8 20 23 31 38 42
5
-4 9 24 28 33
14
-48 -35 -31 -21 -20 -11 8 14 16 21 30 34 40 47
4
-28 16 20 47
1
1
2
-21 -15
7
-23 -6 3 10 25 30 37
6
7 10 15 35 38 43
7
-50 -38 -24 11 24 36 39
0

---
-10 -40 23 -50 -14 -8 38 # -47 -15 -11 # 20 31 42
24 -4 28 # 9 # 33
8 -31 30 -48 -20 16 40 # -35 -21 -11 14 21 34 47
16 -28 20 # # # 47
1
-21 # -15
10 -6 30 -23 3 25 37
15 7 38 # 10 35 43
11 -38 36 -50 -24 24 39
empty
=== hidden
4
-49 -23 -17 -8
14
-46 -45 -44 -39 -38 -28 -12 -5 4 13 18 35 41 49
1
18
9
-44 -41 -10 -7 6 10 18 32 43
1
-38
14
-44 -37 -32 -24 -15 -6 10 19 22 23 24 27 29 43
3
-46 3 31
13
-33 -19 -2 4 7 8 14 24 27 32 34 38 49
14
-36 -11 -2 12 13 16 19 20 30 31 32 37 43 44
3
-47 -4 -1
---
-23 -49 -17 # # # -8
-12 -44 18 -46 -38 4 41 # -45 -39 -28 -5 13 35 49
18
6 -41 18 -44 -10 10 32 # # # -7 # # # 43
-38
10 -32 24 -44 -15 22 29 # -37 -24 -6 19 23 27 43
3 -46 31
14 -2 32 -33 7 24 38 # -19 4 8 # 27 34 49
19 -2 32 -36 13 30 43 # -11 12 16 20 31 37 44
-4 -47 -1
=== hidden
3
-14 5 37
8
-50 -30 -27 -10 24 25 33 37
5
-32 -5 0 30 45
8
-43 -11 9 15 18 26 34 44
2
-23 -7
12
-50 -49 -45 -40 -12 -3 16 27 30 33 35 46
10
-45 -37 -12 -11 -7 -3 -2 10 14 28
10
-34 -25 -23 -20 -14 -1 9 23 33 38
14
-50 -44 -40 -36 -27 -21 -16 4 7 8 15 38 41 49
1
23
---
5 -14 37
-10 -30 25 -50 -27 24 33 # # # # # # # 37
0 -32 30 # -5 # 45
15 -11 26 -43 9 18 34 # # # # # # # 44
-23 # -7
-3 -45 30 -50 -40 16 35 # -49 # -12 # 27 33 46
-7 -37 10 -45 -12 -3 14 # # # -11 # -2 # 28
-14 -25 23 -34 -23 -1 33 # # # -20 # 9 # 38
-16 -40 15 -50 -27 7 41 # -44 -36 -21 4 8 38 49
23
=== hidden
@gen 368576860 big
=== hidden
@gen 368576861 big
=== hidden
@gen 368576862 big

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
    a = sorted(r.sample(range(-10**9, 10**9) if big else range(-50, 50), n))
    print(n); print(*a)
```

## Hints
- The root should be the middle element, so that both sides have about the same size.
- Recurse on index ranges `[lo, mid−1]` and `[mid+1, hi]`; an empty range gives `nullptr`.
- Use exactly `mid = lo + (hi − lo) / 2`.

## Solution
Choosing the middle element as the root splits the remaining elements into two halves whose sizes differ by at most one. Recursing on each half gives two balanced subtrees whose heights differ by at most one, so the whole tree is balanced (an induction on n). Inorder of the result is the array, so it is a valid BST.

The midpoint rule fixes which of the several balanced BSTs you build. `lo + (hi − lo) / 2` is the lower middle; `(lo + hi + 1) / 2` would give the upper middle and a different (also valid) tree.

Each element becomes exactly one node: O(n) time. The recursion depth is O(log n), so it is safe even for huge arrays.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

static TreeNode* build(const vector<int>& a, int lo, int hi) {
    if (lo > hi) return nullptr;
    int mid = lo + (hi - lo) / 2;                  // lower middle
    return new TreeNode(a[mid], build(a, lo, mid - 1), build(a, mid + 1, hi));
}

TreeNode* sorted_to_bst(const vector<int>& a) { return build(a, 0, (int)a.size() - 1); }
```
