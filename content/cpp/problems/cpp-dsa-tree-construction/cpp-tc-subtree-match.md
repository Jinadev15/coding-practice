---
id: cpp-tc-subtree-match
title: Identical Trees and Subtree Matching in Linear Time
difficulty: Hard
order: 7
tags: binary tree, serialization, kmp, string matching
time_limit: 2
---
## Statement
```cpp
bool same_tree(TreeNode* a, TreeNode* b);          // same shape and same values?
bool is_subtree(TreeNode* root, TreeNode* sub);  // is `sub` identical to the subtree rooted at some node of `root`?
```

A **subtree** of a node means the node with **all** of its descendants. A pattern that matches only the top part of a subtree doesn't count:

```text
root:     3            sub:   4        is_subtree = true
         / \                 / \
        4   5               1   2
       / \
      1   2                (with a 0 under the 2 in root, the answer becomes false)
```

The direct approach calls `same_tree` at every node of `root`: O(n·m), which is 10¹⁰ steps on two long chains of equal values. Make it **O(n + m)**: serialize both trees in **preorder with null markers** into integer sequences. Then `sub` is a subtree of `root` exactly when `sub`'s sequence occurs as a contiguous block inside `root`'s. Find it with KMP (or Z-function, or rolling hashes with care).

**Input:** cases until the end of input. Each case is a line `same` or `sub`, then two tree lines (`a` then `b`, or `root` then `sub`). Up to 2·10⁵ nodes per tree, values fit in `int`. For `sub`, `sub` is never empty.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

Trees can be chains of 2·10⁵ nodes and your code runs on the normal 8 MB stack: serialize iteratively.

**Output:** `true` or `false` per case.

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

bool same_tree(TreeNode* a, TreeNode* b) {
    if (!a || !b) return a == b;
    return a->val == b->val && same_tree(a->left, b->left) && same_tree(a->right, b->right);
}
bool is_subtree(TreeNode* root, TreeNode* sub) {   // O(n*m), and recursive
    if (!root) return false;
    return same_tree(root, sub) || is_subtree(root->left, sub) || is_subtree(root->right, sub);
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
        string cmd = rd_str();
        TreeNode* a = rd_tree();
        TreeNode* b = rd_tree();
        bool r = cmd == "same" ? same_tree(a, b) : is_subtree(a, b);
        cout << (r ? "true" : "false") << '\n';
        free_tree(a); free_tree(b);
    }
    return 0;
}
```

## Tests
=== sample
sub
5 3 4 5 1 2
3 4 1 2
---
true
=== sample
sub
9 3 4 5 1 2 # # # 0
3 4 1 2
---
false
=== sample
same
3 1 2 3
3 1 2 3
---
true
=== hidden
same
0
0
---
true
=== hidden
same
2 1 2
3 1 # 2
---
false
=== hidden
sub
1 1
1 1
---
true
=== hidden
sub
3 12 # 2
1 2
---
true
=== hidden
sub
2 1 2
3 1 # 2
---
false
=== hidden
sub
7 1 1 # 1 # 1 #
3 1 1 #
---
true
=== hidden
sub
1 0
1 0
same
13 2 2 # # 1 1 # # 2 1 # # 1
13 2 2 # # 1 1 # # 2 1 # # 1
sub
7 0 # 0 # 0 # 0
1 0
sub
9 0 2 2 1 1 0 2 0 2
1 1
sub
5 0 1 # # 2
5 0 1 # # 2
same
18 0 2 # # 2 1 # # 0 1 # # 0 2 # # 0 0
18 0 2 # # 2 1 # # 0 1 # # 0 2 # # 0 0
---
true
true
true
true
true
true
=== hidden
sub
17 2 # 1 # 0 # 1 # 0 # 0 # 0 # 0 # 0
1 0
sub
11 0 # 1 0 0 1 # 1 2 # 2
1 0
same
17 1 0 1 # # 2 1 # # 0 1 # 0 # # # 2
15 2 # 2 0 # 0 # # 1 2 2 # # 0 1
sub
4 2 # 0 0
1 0
sub
10 0 2 # 0 # 1 # 1 # 2
2 2 2
sub
7 1 0 1 2 0 1 1
3 1 1 1
---
true
false
false
true
false
true
=== hidden
sub
14 1 1 2 2 2 # 1 0 # 2 2 # # 0
8 2 2 2 0 # 2 2 0
sub
14 1 1 # 2 # 0 # 0 # 1 # 1 # 1
3 2 # 0
same
19 2 # 1 # 0 # 0 # 0 # 2 # 1 # 2 # 2 # 2
19 2 # 1 # 0 # 0 # 0 # 2 # 1 # 2 # 2 # 2
same
6 1 0 # # 2 0
6 1 0 # # 2 0
sub
13 1 1 # # 1 1 # # 1 0 # # 0
5 1 0 # # 0
sub
12 2 0 # 1 # 0 # 1 # 1 # 2
7 0 2 1 # # # 2
---
false
false
true
true
true
false
=== hidden
@gen 2716798534 big
=== hidden
@gen 2716798535 big
=== hidden
@gen 2716798536 big

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
def sub_of(vals, L, R):
    if not vals: return [], [], []
    u = r.randrange(len(vals)); ids = []; st = [u]
    while st:
        x = st.pop(); ids.append(x)
        for c in (L[x], R[x]):
            if c >= 0: st.append(c)
    m = {x: i for i, x in enumerate(ids)}
    v2 = [vals[x] for x in ids]; L2 = [m[L[x]] if L[x] >= 0 else -1 for x in ids]; R2 = [m[R[x]] if R[x] >= 0 else -1 for x in ids]
    if r.random() < 0.4: v2[r.randrange(len(v2))] += 1
    return v2, L2, R2
if not big:
    for _ in range(6):
        cmd = r.choice(["same", "sub", "sub"])
        vals, L, R = rand_tree(r.randint(1 if cmd == "sub" else 0, 10), 0, 2)
        if cmd == "same":
            a = tline(vals, L, R)
            b = a if r.random() < 0.5 else tline(*rand_tree(len(vals), 0, 2))
        else:
            a = tline(vals, L, R)
            sv, sl, sr = sub_of(vals, L, R) if r.random() < 0.7 else rand_tree(r.randint(1, 4), 0, 2)
            b = tline(sv, sl, sr)
        print(cmd); print(a); print(b)
else:
    # adversarial: long chains of equal values (naive matching is quadratic)
    n = 120000; m = 60000
    kind = r.choice(["left", "right"])
    L, R = shape(n, kind)
    vals = [1] * n
    print("sub"); print(tline(vals, L, R))
    L2, R2 = shape(m, kind)
    v2 = [1] * m
    if r.random() < 0.5: v2[-1] = 2
    print(tline(v2, L2, R2))
    print("same"); print(tline(vals, L, R)); vals[-1] = r.choice([1, 3]); print(tline(vals, L, R))
```

## Hints
- Serialize both trees in preorder **with null markers**, as integer sequences.
- Then the question becomes: does the pattern sequence occur contiguously inside the text sequence?
- Use KMP for linear-time matching, and serialize with an explicit stack, not recursion.

## Solution
**Why serialization works.** Preorder with null markers is a *prefix code*: the encoding of a subtree is a contiguous block that starts at its root and ends exactly when that subtree is complete. If `sub`'s full encoding appears as a block of `root`'s encoding, the block must start at a node (a block can't start at a marker, because `sub` is non-empty so its first token is a value). From that node, the parse consumes exactly the block, so the subtree there is identical to `sub`. Conversely, every subtree's encoding is a block of the whole encoding.

The null markers are essential. Without them, `1 2` matches both "2 is the left child" and "2 is the right child", and a pattern could match the top of a bigger subtree. Using integer tokens, not characters, also avoids false matches like value `12` matching a `2`.

**Matching:** KMP finds the pattern in O(n + m). Its failure function says how far the pattern can fall back after a mismatch, so the text index never moves backwards.

**Identical trees** is the special case where the encodings are equal.

The encoder uses an explicit stack, so chains of 2·10⁵ nodes are fine on the normal stack.

Complexity: O(n + m) time and memory. (A Merkle-style alternative hashes every subtree bottom-up and compares hashes. It is also linear, but needs collision handling.)

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

// preorder with a null marker, iteratively; values are widened to long long so the marker can't collide
static vector<long long> encode(TreeNode* root) {
    const long long NUL = LLONG_MIN;
    vector<long long> out;
    vector<TreeNode*> st{root};
    while (!st.empty()) {
        TreeNode* n = st.back(); st.pop_back();
        if (!n) { out.push_back(NUL); continue; }
        out.push_back(n->val);
        st.push_back(n->right);           // right pushed first: left subtree is encoded first
        st.push_back(n->left);
    }
    return out;
}

bool same_tree(TreeNode* a, TreeNode* b) { return encode(a) == encode(b); }

bool is_subtree(TreeNode* root, TreeNode* sub) {
    vector<long long> t = encode(root), p = encode(sub);
    // KMP failure function of the pattern
    vector<int> fail(p.size(), 0);
    for (size_t i = 1, k = 0; i < p.size(); ++i) {
        while (k && p[i] != p[k]) k = fail[k - 1];
        if (p[i] == p[k]) ++k;
        fail[i] = (int)k;
    }
    for (size_t i = 0, k = 0; i < t.size(); ++i) {
        while (k && t[i] != p[k]) k = fail[k - 1];
        if (t[i] == p[k]) ++k;
        if (k == p.size()) return true;
    }
    return false;
}
```
