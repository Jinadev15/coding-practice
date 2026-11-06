---
id: cpp-tt-iterative-stack
title: The Three Orders with an Explicit Stack
difficulty: Medium
order: 3
tags: binary tree, stack, iteration, traversal
time_limit: 2
---
## Statement
Write the three depth-first traversals **without recursion**:

```cpp
vector<int> preorder_iter(TreeNode* root);
vector<int> inorder_iter(TreeNode* root);
vector<int> postorder_iter(TreeNode* root);
```

Trees can be chains of 5·10⁵ nodes, and your code runs on the **normal 8 MB stack**: a recursive solution overflows it and crashes. Use an explicit stack (or no stack at all). This is the real-world reason iterative traversals exist: production trees (parsed documents, scene graphs, degenerate BSTs) can be far deeper than the call stack.

- **Preorder:** pop a node, record it, push right then left (so left is processed first).
- **Inorder:** "go left as far as possible, pushing every node; pop one, record it, then move to its right child".
- **Postorder** is the trickiest: a node may be recorded only after **both** subtrees are done. Either keep a `last` pointer to the most recently recorded node, or record a modified preorder (node, right, left) and reverse it.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input. Each case is a line `pre`, `in` or `post`, then a tree line. Up to 5·10⁵ nodes per tree.

**Output:** the traversal on one line. Lists of more than 60 numbers are printed as `count=C hash=H` (a fingerprint), shorter ones in full; an empty list prints `(none)`.

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

vector<int> preorder_iter(TreeNode* root) { return {}; }
vector<int> inorder_iter(TreeNode* root) { return {}; }
vector<int> postorder_iter(TreeNode* root) { return {}; }
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
        TreeNode* root = rd_tree();
        vector<int> v = cmd == "pre" ? preorder_iter(root) : cmd == "in" ? inorder_iter(root) : postorder_iter(root);
        cout << show_vec(v) << '\n';
        free_tree(root);
    }
    return 0;
}
```

## Tests
=== sample
pre
5 1 2 3 # 4
---
1 2 4 3
=== sample
in
5 1 2 3 # 4
---
2 4 1 3
=== sample
post
5 1 2 3 # 4
---
4 2 3 1
=== hidden
post
0
in
1 9
---
(none)
9
=== hidden
post
7 1 2 3 4 5 6 7
---
4 5 2 6 7 3 1
=== hidden
post
7 1 # 2 # 3 # 4
---
4 3 2 1
=== hidden
in
7 1 2 # 3 # 4 #
---
4 3 2 1
=== hidden
post
9 8 # 3 # -1 # 6 # 2
---
2 6 -1 3 8
=== hidden
post
13 -35 4 # # 1 # -23 24 # -1 47 # -6
pre
1 0
pre
17 40 # -47 # 42 # -45 # 42 # -31 # -37 # -39 # 46
pre
5 -20 # -40 # 38
in
1 -13
post
12 -6 -15 -19 -15 14 -43 -32 24 -22 -43 19 0
---
-6 -1 47 24 -23 1 4 -35
0
40 -47 42 -45 42 -31 -37 -39 46
-20 -40 38
-13
24 -22 -15 -43 19 14 -15 0 -43 -32 -19 -6
=== hidden
pre
1 -33
in
5 -49 -8 6 -32 -31
in
8 6 -35 -14 -27 42 34 # 50
post
7 47 # -12 -18 # 8 16
pre
13 40 1 -47 # # 9 # -1 -5 -49 # # 1
in
21 2 24 # # -24 -14 # # -45 20 # # -39 -21 # # 2 -27 # # -18
---
-33
-32 -8 -31 -49 6
50 -27 -35 42 6 34 -14
8 16 -18 -12 47
40 1 -47 9 -1 -49 -5 1
24 -14 20 -21 -27 -18 2 -39 -45 -24 2
=== hidden
in
10 41 -46 -9 -30 -39 -15 -35 -8 35 16
post
3 47 -39 -8
pre
22 29 -10 # -8 32 # 29 -40 # # # 49 -22 # 6 34 # # 15 # # 21
pre
0
post
5 -32 0 -10 -17 11
in
9 -34 -9 -1 10 4 # -12 -13 -35
---
-8 -30 35 -46 16 -39 41 -15 -9 -35
-39 -8 47
29 -10 -8 29 32 -40 49 6 15 21 -22 34
(none)
-17 11 0 -10 -32
-13 10 -35 -9 4 -34 -1 -12
=== hidden
@gen 3860048085 big
=== hidden
@gen 3860048086 big
=== hidden
@gen 3860048087 big

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
if not big:
    for _ in range(6):
        vals, L, R = rand_tree(r.randint(0, 12), -50, 50)
        print(r.choice(["pre", "in", "post"])); print(tline(vals, L, R))
else:
    kind = r.choice(["left", "zigzag"])
    vals, L, R = rand_tree(500000, 0, 999, kind)
    print(r.choice(["in", "post", "pre"])); print(tline(vals, L, R))
```

## Hints
- A `std::vector<TreeNode*>` used with `push_back`/`back`/`pop_back` is your stack, and it lives on the heap.
- Inorder: an inner `while (cur)` loop pushes the left spine; after popping, continue from the popped node's right child.
- Postorder: peek at the top. When may it be recorded? Track the last recorded node to tell whether its right subtree has been finished.

## Solution
The explicit stack holds exactly what the call stack would have held: the chain of ancestors still waiting for work.

- **Preorder** records a node when it is popped, then pushes its children right-first so that the left child comes off the stack next.
- **Inorder** pushes the whole left spine, pops the deepest node (its left subtree is empty or finished), records it, and continues with its right child.
- **Postorder** also pushes the left spine, but looks at the top without popping. If the top has a right child that was not just recorded, the right subtree is still pending, so it goes there. Otherwise both subtrees are finished and the node is recorded. The `last` pointer distinguishes "coming back up from the right" from "never visited the right".

Complexity: O(n) time (each node is pushed and popped once), O(h) extra memory for the stack, all on the heap, so a 10⁶-node chain is fine.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

vector<int> preorder_iter(TreeNode* root) {
    vector<int> out;
    vector<TreeNode*> st;
    if (root) st.push_back(root);
    while (!st.empty()) {
        TreeNode* n = st.back(); st.pop_back();
        out.push_back(n->val);
        if (n->right) st.push_back(n->right);   // pushed first, so popped after the left subtree
        if (n->left) st.push_back(n->left);
    }
    return out;
}

vector<int> inorder_iter(TreeNode* root) {
    vector<int> out;
    vector<TreeNode*> st;
    TreeNode* cur = root;
    while (cur || !st.empty()) {
        while (cur) { st.push_back(cur); cur = cur->left; }   // slide down the left spine
        cur = st.back(); st.pop_back();
        out.push_back(cur->val);                               // left subtree finished
        cur = cur->right;                                      // now the right subtree
    }
    return out;
}

vector<int> postorder_iter(TreeNode* root) {
    vector<int> out;
    vector<TreeNode*> st;
    TreeNode* cur = root;
    TreeNode* last = nullptr;                // most recently recorded node
    while (cur || !st.empty()) {
        while (cur) { st.push_back(cur); cur = cur->left; }
        TreeNode* top = st.back();
        if (top->right && top->right != last) {
            cur = top->right;                // right subtree not done yet: go there first
        } else {
            out.push_back(top->val);         // both subtrees done
            last = top;
            st.pop_back();
        }
    }
    return out;
}
```
