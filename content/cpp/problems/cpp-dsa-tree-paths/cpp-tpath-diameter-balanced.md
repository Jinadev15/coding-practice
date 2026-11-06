---
id: cpp-tpath-diameter-balanced
title: Diameter and Balance from One Height Pass
difficulty: Medium
order: 3
tags: binary tree, postorder, height, diameter, balanced
time_limit: 2
---
## Statement
Two questions answered by the same trick, "compute heights bottom-up and record something on the way":

```cpp
int diameter(TreeNode* root);      // number of EDGES on the longest path between any two nodes (0 for 0 or 1 node)
bool is_balanced(TreeNode* root);  // for EVERY node, do the heights of its two subtrees differ by at most 1?
```

```text
        1             diameter = 3: the path 4 → 2 → 1 → 3 (or 5 → 2 → 1 → 3)
       / \
      2   3           balanced: yes (every node's subtrees differ by at most 1)
     / \
    4   5
```

The longest path does **not** have to pass through the root. It passes through some "top" node, and its length there is `height(left) + height(right)`. Calling a separate `height()` from every node costs O(n²) on a chain. Instead, let one postorder function return the height and update the answer as a side effect. For balance, return `−1` as a "not balanced" signal that propagates upward.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input. Each case is a line `diam` or `bal`, then a tree line. Up to 2·10⁵ nodes.

Trees can be degenerate chains of up to 2·10⁵ nodes. The driver runs your code on a thread with a 256 MB stack, so plain recursion is safe here (on a normal 8 MB stack it would not be).

**Output:** the diameter, or `true` / `false`.

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

static int h(TreeNode* n) { return n ? 1 + max(h(n->left), h(n->right)) : 0; }
int diameter(TreeNode* root) { return root ? h(root->left) + h(root->right) : 0; }   // only paths through the root
bool is_balanced(TreeNode* root) { return !root || abs(h(root->left) - h(root->right)) <= 1; }   // root only
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
        if (cmd == "diam") cout << diameter(root) << '\n';
        else cout << (is_balanced(root) ? "true" : "false") << '\n';
        free_tree(root);
    }
    return 0;
}
```

## Tests
=== sample
diam
5 1 2 3 4 5
---
3
=== sample
bal
5 1 2 3 4 5
---
true
=== sample
diam
13 1 2 # 3 4 5 # # 6 7 # # 8
---
6
=== hidden
diam
0
bal
0
diam
1 5
bal
1 5
---
0
true
0
true
=== hidden
bal
3 1 2 #
---
true
=== hidden
bal
5 1 2 # 3 #
---
false
=== hidden
bal
11 1 2 2 3 # # 3 4 # # 4
---
false
=== hidden
diam
7 1 # 2 # 3 # 4
---
3
=== hidden
bal
7 1 2 3 4 5 6 7
---
true
=== hidden
bal
6 7 8 9 6 8 2
bal
12 2 8 2 # # 8 3 # # 9 # 3
diam
0
bal
4 1 7 7 1
diam
0
diam
1 2
bal
12 3 6 3 9 6 5 2 9 8 7 7 9
bal
20 5 # 8 9 7 9 9 3 # # 2 # # 7 8 # 5 8 # 8
diam
9 5 # 9 5 2 # # # 3
bal
13 2 6 2 5 9 9 5 2 0 4 0 6 8
---
true
false
0
true
0
0
true
false
3
true
=== hidden
diam
10 3 # 1 7 # 6 8 9 # 0
diam
2 8 3
bal
8 9 3 # 9 # 9 # 1
diam
9 0 # 0 # 5 # 3 # 0
diam
21 5 # 7 # 8 # 9 # 7 # 3 # 1 # 1 # 8 # 7 # 9
diam
27 0 0 8 7 3 1 6 # # 2 # # 3 7 # 6 # # # # 2 # # # 6 # 7
bal
25 2 # 7 # 5 1 # # 2 6 # 6 # # 8 7 # 4 0 6 # # # # 7
bal
2 1 5
diam
11 0 1 0 0 4 6 4 8 0 7 6
diam
9 3 5 # # 0 0 # # 9
---
4
1
false
4
10
10
false
true
5
4
=== hidden
diam
16 3 8 # 6 9 4 3 8 9 # # # 1 # # 5
bal
25 5 6 5 # 6 # # 9 6 # # 9 # # 4 7 # # 2 1 # # 1 7 3
bal
0
bal
8 7 5 # 4 # 4 # 7
bal
18 9 9 # 7 # 2 # 5 # 8 # 1 # 1 # 5 # 0
diam
26 0 3 # # 1 8 # # 4 8 # # 0 8 # # 9 4 # # 0 8 # # 8 7
diam
7 5 5 3 6 7 7 6
bal
4 2 1 3 5
bal
8 3 5 6 7 6 0 8 8
diam
6 9 # 8 2 8 9
---
6
false
true
false
false
13
4
true
true
3
=== hidden
@gen 1487910137 big
=== hidden
@gen 1487910138 big
=== hidden
@gen 1487910139 big

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
    kinds = KINDS if not big else ["random", "deep", "complete", "zigzag"]
    vals, L, R = rand_tree(n, 0, 9, r.choice(kinds + ["complete"] * 2))
    print(r.choice(["diam", "bal"])); print(tline(vals, L, R))
```

## Hints
- One recursive function returns the height. The answer is updated on the side (pass it by reference).
- Diameter through node n = height(left) + height(right), counting heights in nodes.
- For balance, return −1 to mean "unbalanced". Check it right after each recursive call.

## Solution
Both answers need the height of every subtree, and heights are computed bottom-up (postorder) in O(n) total.

**Diameter.** Every path has a unique highest node. A path whose top is `n` goes down into the left subtree at most `height(left)` edges and into the right at most `height(right)` edges, where height counts nodes. So the longest path topped at `n` has `l + r` edges. The function returns the height to its parent and, as a side effect, keeps the maximum `l + r` seen anywhere.

**Balanced.** A tree is balanced if both subtrees are balanced **and** their heights differ by at most 1. Return `−1` as a sentinel for "unbalanced somewhere below". It propagates straight up, so each node is still visited at most once. Checking only the root's two heights is the common bug: both sides can have equal height while being badly unbalanced inside.

Complexity: O(n) time, O(h) recursion depth, versus O(n²) when `height()` is recomputed at every node.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

// returns the height in nodes (0 for empty) and updates best with the longest path through n
static int height_diam(TreeNode* n, int& best) {
    if (!n) return 0;
    int l = height_diam(n->left, best);
    int r = height_diam(n->right, best);
    best = max(best, l + r);              // edges of the longest path whose top is n
    return 1 + max(l, r);
}
int diameter(TreeNode* root) { int best = 0; height_diam(root, best); return best; }

// height, or -1 if some subtree is unbalanced
static int height_bal(TreeNode* n) {
    if (!n) return 0;
    int l = height_bal(n->left);
    if (l < 0) return -1;                 // early exit: the answer is already known
    int r = height_bal(n->right);
    if (r < 0 || abs(l - r) > 1) return -1;
    return 1 + max(l, r);
}
bool is_balanced(TreeNode* root) { return height_bal(root) >= 0; }
```
