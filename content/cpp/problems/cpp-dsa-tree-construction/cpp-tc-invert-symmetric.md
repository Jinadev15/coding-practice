---
id: cpp-tc-invert-symmetric
title: Mirror a Tree and Test Symmetry
difficulty: Easy
order: 2
tags: binary tree, recursion, mirror, symmetry
time_limit: 2
---
## Statement
Two classic "structure" operations:

```cpp
TreeNode* invert(TreeNode* root);     // mirror the tree IN PLACE (swap left and right everywhere); return the root
bool is_symmetric(TreeNode* root);    // is the tree its own mirror image?
```

```text
      4                  4
    /   \              /   \
   2     7    ──►     7     2
  / \   / \          / \   / \
 1   3 6   9        9   6 3   1
```

`is_symmetric` must **not** modify the tree. The key idea is a helper `mirror(a, b)` that asks "is `a` the mirror image of `b`?": their roots match, `a->left` mirrors `b->right`, and `a->right` mirrors `b->left`.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input. Each case is a line `invert` or `sym`, then a tree line. Up to 2·10⁵ nodes.

Trees can be degenerate chains of up to 2·10⁵ nodes. The driver runs your code on a thread with a 256 MB stack, so plain recursion is safe here (on a normal 8 MB stack it would not be).

**Output:** for `invert`, the mirrored tree. For `sym`, `true` or `false`.

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

TreeNode* invert(TreeNode* root) { return root; }
bool is_symmetric(TreeNode* root) { return root == nullptr || root->left == nullptr; }
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
        string cmd = rd_str();
        TreeNode* root = rd_tree();
        bool ok = true;
        if (cmd == "invert") {
            root = invert(root);
            cout << show_tree(root, NODES_, &ok) << '\n';
        } else {
            string before = show_tree(root, NODES_);
            cout << (is_symmetric(root) ? "true" : "false") << '\n';
            if (show_tree(root, NODES_, &ok) != before) cout << "TREE MODIFIED\n";
        }
        if (ok) free_tree(root);
        else return 0;
    }
    return 0;
}
```

## Tests
=== sample
invert
7 4 2 7 1 3 6 9
---
4 7 2 9 6 3 1
=== sample
sym
7 1 2 2 3 4 4 3
---
true
=== sample
sym
7 1 2 2 # 3 # 3
---
false
=== hidden
invert
0
---
empty
=== hidden
sym
0
---
true
=== hidden
sym
1 5
---
true
=== hidden
invert
3 1 # 2
---
1 2
=== hidden
sym
3 1 2 3
---
false
=== hidden
sym
3 1 2 2
---
true
=== hidden
sym
5 1 2 2 3 #
---
false
=== hidden
sym
12 0 3 1 2 3 0 2 1 0 0 1 0
sym
15 1 1 0 2 3 # 3 2 # # # # # 1 1
sym
3 4 2 3
invert
3 0 # 1
sym
1 3
sym
1 3
---
false
false
false
0 1
true
true
=== hidden
invert
12 0 3 0 0 2 # # # # # 1 3
sym
9 3 1 # # 0 1 # # 1
sym
1 5
sym
1 8
invert
9 0 # 0 1 # # 0 # 2
sym
19 1 3 4 3 # # 3 0 # # 0 1 # # 1 1 # # 1
---
0 0 3 # # 2 0 1 # # # # 3
false
true
true
0 0 # # 1 0 # 2
false
=== hidden
sym
3 5 0 1
sym
15 8 2 2 1 3 3 1 0 1 3 # # 3 2 0
sym
3 6 0 1
invert
11 3 0 # 2 3 # # 1 # # 1
sym
23 8 1 1 2 # # 2 1 # # 1 2 # # 1 3 # # 3 3 # # 3
sym
7 4 3 3 2 # # 2
---
false
false
false
3 # 0 3 2 # 1 # # 1
false
true
=== hidden
@gen 1802755002 big
=== hidden
@gen 1802755003 big
=== hidden
@gen 1802755004 big

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
def mirrored(n):
    # a random tree of about n nodes whose two halves are mirror images, sometimes with one flaw
    vals, L, R = rand_tree(n // 2, 0, 3 if not big else 9)
    m = len(vals); V = [r.randint(0, 9)] + vals + vals; LL = [-1] * (2 * m + 1); RR = [-1] * (2 * m + 1)
    if m:
        LL[0], RR[0] = 1, m + 1
        for u in range(m):
            LL[1 + u] = L[u] + 1 if L[u] >= 0 else -1; RR[1 + u] = R[u] + 1 if R[u] >= 0 else -1
            LL[m + 1 + u] = R[u] + m + 1 if R[u] >= 0 else -1; RR[m + 1 + u] = L[u] + m + 1 if L[u] >= 0 else -1
        if r.random() < 0.4: V[r.randrange(1, 2 * m + 1)] += 1
    return V, LL, RR
for _ in range(6 if not big else 2):
    n = r.randint(0, 13) if not big else 200000
    cmd = r.choice(["invert", "sym", "sym"])
    vals, L, R = mirrored(n) if cmd == "sym" and r.random() < 0.7 else rand_tree(n, 0, 3 if not big else 10**9)
    print(cmd); print(tline(vals, L, R))
```

## Hints
- Invert: swap `root->left` and `root->right`, then invert both children.
- Symmetric: write `bool mirror(TreeNode* a, TreeNode* b)` and call it on the root's two children.
- In `mirror`, compare `a->left` with `b->right` and `a->right` with `b->left`.

## Solution
**Invert:** mirroring a tree means mirroring every node: swap its two child pointers and mirror both subtrees. The order (swap first or recurse first) doesn't matter, as long as each node is swapped exactly once.

**Symmetric:** a tree is symmetric when its left subtree is the mirror of its right subtree. "Is `a` the mirror of `b`?" is itself recursive: the root values are equal, the **outer** pair (`a->left`, `b->right`) are mirrors, and the **inner** pair (`a->right`, `b->left`) are mirrors. The base case handles empty trees: two empty trees are mirrors, but an empty tree and a non-empty one are not.

Comparing only values level by level is not enough. Structure matters: `1 2 2 # 3 # 3` has palindromic levels but is not symmetric.

Complexity: O(n) time, O(h) recursion depth.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

TreeNode* invert(TreeNode* root) {
    if (!root) return nullptr;
    swap(root->left, root->right);    // mirror this node...
    invert(root->left);               // ...then both subtrees
    invert(root->right);
    return root;
}

static bool mirror(TreeNode* a, TreeNode* b) {
    if (!a || !b) return a == b;      // both empty: mirror; only one empty: not
    return a->val == b->val && mirror(a->left, b->right) && mirror(a->right, b->left);
}

bool is_symmetric(TreeNode* root) { return !root || mirror(root->left, root->right); }
```
