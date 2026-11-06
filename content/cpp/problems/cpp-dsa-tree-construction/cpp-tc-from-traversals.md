---
id: cpp-tc-from-traversals
title: Rebuild a Tree from Two Traversals
difficulty: Medium
order: 3
tags: binary tree, construction, divide and conquer, hash map
time_limit: 2
---
## Statement
Values are distinct. Rebuild the unique tree from inorder plus one other traversal:

```cpp
TreeNode* build_pre_in(const vector<int>& pre, const vector<int>& in);
TreeNode* build_post_in(const vector<int>& post, const vector<int>& in);
```

```text
pre  = 3 9 20 15 7           3            post = 9 15 7 20 3
in   = 9 3 15 20 7          / \           in   = 9 3 15 20 7
                           9   20
                              /  \
                             15   7
```

The preorder's **first** value (the postorder's **last**) is the root. Its position in the inorder splits the inorder into the left subtree (before it) and the right subtree (after it), and the sizes of those two parts tell you how to split the other traversal. Searching the inorder linearly costs O(n) per node, so O(n²) on a chain. Precompute a **hash map value → inorder index** to get O(n) overall. Pass index ranges, never copies of sub-vectors.

**Input:** cases until the end of input. Each case is a line `prein n` or `postin n`, then a line with the preorder (or postorder), then a line with the inorder. 1 ≤ n ≤ 2·10⁵, distinct values that fit in `int`, always consistent.

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

TreeNode* build_pre_in(const vector<int>& pre, const vector<int>& in) { return nullptr; }
TreeNode* build_post_in(const vector<int>& post, const vector<int>& in) { return nullptr; }
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
        int n = (int)rd_ll();
        vector<int> a(n), in(n);
        for (int& x : a) x = (int)rd_ll();
        for (int& x : in) x = (int)rd_ll();
        TreeNode* root = cmd == "prein" ? build_pre_in(a, in) : build_post_in(a, in);
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
prein 5
3 9 20 15 7
9 3 15 20 7
---
3 9 20 # # 15 7
=== sample
postin 5
9 15 7 20 3
9 3 15 20 7
---
3 9 20 # # 15 7
=== hidden
prein 1
-1
-1
---
-1
=== hidden
postin 1
4
4
---
4
=== hidden
prein 3
1 2 3
3 2 1
---
1 2 # 3
=== hidden
postin 3
3 2 1
1 2 3
---
1 # 2 # 3
=== hidden
prein 7
4 2 1 3 6 5 7
1 2 3 4 5 6 7
---
4 2 6 1 3 5 7
=== hidden
postin 8
19 -13 4 -20 -25 -1 23 -44
-13 19 4 -44 -25 -20 23 -1
prein 2
-32 -9
-32 -9
postin 6
-35 -10 33 -4 -50 31
33 -35 -10 31 -50 -4
postin 11
-17 10 6 7 39 -5 16 -44 42 -25 -4
-25 -44 -5 7 10 -17 6 39 16 42 -4
prein 4
18 0 -18 40
0 40 -18 18
---
-44 4 23 -13 # -25 -1 # 19 # -20
-32 # -9
31 33 -50 # -10 # -4 -35
-4 -25 # # 42 -44 # # 16 -5 # # 39 7 # # 6 10 # # -17
18 0 # # -18 40
=== hidden
postin 10
-16 11 39 -4 -6 27 48 32 -27 36
-27 48 -6 39 -16 11 -4 27 32 36
prein 6
-13 26 -9 25 7 -6
-9 26 25 7 -13 -6
prein 11
49 -8 9 6 -41 -1 -21 -37 -36 -30 27
-8 49 -41 -1 -21 6 9 -30 -36 27 -37
postin 4
22 32 -42 -18
22 32 -42 -18
postin 3
11 -38 27
27 -38 11
---
36 -27 # # 32 48 # # 27 -6 # # -4 39 # # 11 -16
-13 26 -6 -9 25 # # # # # 7
49 -8 9 # # 6 -37 -41 # -36 # # -1 -30 27 # -21
-18 -42 # 32 # 22
27 # -38 # 11
=== hidden
postin 3
22 -14 8
22 8 -14
postin 1
-27
-27
postin 12
-15 32 -12 5 -39 21 -42 -45 -43 15 19 6
-15 5 32 -12 21 -39 -42 6 19 -45 -43 15
prein 11
-13 9 26 -26 10 42 -43 -46 -24 -33 -37
26 9 10 -26 -13 -43 -24 -46 -33 -37 42
postin 8
-11 -9 49 13 1 25 -7 -38
-38 49 -9 -11 13 -7 25 1
---
8 22 -14
-27
6 -42 19 21 # # 15 5 -39 -43 # -15 -12 # # -45 # # # 32
-13 9 42 26 -26 -43 # # # 10 # # -46 # # -24 -33 # # # -37
-38 # -7 13 25 49 # # 1 # -9 # # # -11
=== hidden
@gen 203775378 big
=== hidden
@gen 203775379 big
=== hidden
@gen 203775380 big

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
def orders(vals, L, R):
    pre, post, st = [], [], [(0, False)] if vals else []
    while st:
        u, done = st.pop()
        if done: post.append(vals[u]); continue
        pre.append(vals[u]); st.append((u, True))
        if R[u] >= 0: st.append((R[u], False))
        if L[u] >= 0: st.append((L[u], False))
    # pre is N L R; post must be L R N
    return pre, post
def post_order(vals, L, R):
    out, st = [], [0]
    while st:
        u = st.pop(); out.append(vals[u])
        if L[u] >= 0: st.append(L[u])
        if R[u] >= 0: st.append(R[u])
    return out[::-1]
for _ in range(5 if not big else 2):
    n = r.randint(1, 12) if not big else 200000
    L, R = shape(n, r.choice(KINDS))
    vals = r.sample(range(-10**9, 10**9) if big else range(-50, 50), n)
    cmd = r.choice(["prein", "postin"])
    a = orders(vals, L, R)[0] if cmd == "prein" else post_order(vals, L, R)
    print(cmd, n); print(*a); print(*[vals[u] for u in inorder(L, R)])
```

## Hints
- The first preorder value is the root. Where is it in the inorder, and what lies on each side?
- Precompute `unordered_map<int,int>` from value to inorder index, and recurse on index ranges.
- Keep a global "next preorder index" and build left before right. For postorder, walk from the end and build right before left.

## Solution
**Divide and conquer on the inorder.** The root of any subtree is the first element of its preorder segment. Locate it in the inorder: everything to its left is the left subtree, everything to its right is the right subtree.

Instead of computing preorder segment boundaries, use a running index `next` into the preorder. The preorder lists N, then the whole left subtree, then the whole right subtree, so if you build the left subtree **completely** before the right, the next unused preorder value is always the root of the subtree you're building. The inorder range `[lo, hi]` says when a subtree is empty (`lo > hi`).

**Postorder** is L R N. Read it **backwards** (N R L), build the right subtree before the left, and the same reasoning applies.

The hash map makes each root lookup O(1). With a linear search, a chain-shaped tree costs O(n²).

Why preorder + postorder alone is not enough: `pre = 1 2`, `post = 2 1` fits both "2 is the left child" and "2 is the right child". Inorder is what separates left from right.

Complexity: O(n) expected time and memory, O(h) recursion depth.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

struct Builder {
    const vector<int>& order;               // preorder or postorder
    unordered_map<int, int> pos;            // value -> index in the inorder
    int next;                               // next root to take from `order`
    bool fromPre;
    Builder(const vector<int>& ord, const vector<int>& in, bool pre) : order(ord), fromPre(pre) {
        pos.reserve(in.size() * 2);
        for (int i = 0; i < (int)in.size(); ++i) pos[in[i]] = i;
        next = pre ? 0 : (int)ord.size() - 1;
    }
    // builds the subtree whose inorder is in[lo..hi]
    TreeNode* go(int lo, int hi) {
        if (lo > hi) return nullptr;
        int v = order[next];
        next += fromPre ? 1 : -1;
        TreeNode* n = new TreeNode(v);
        int m = pos[v];
        if (fromPre) { n->left = go(lo, m - 1); n->right = go(m + 1, hi); }   // pre: N L R
        else { n->right = go(m + 1, hi); n->left = go(lo, m - 1); }          // post read backwards: N R L
        return n;
    }
};

TreeNode* build_pre_in(const vector<int>& pre, const vector<int>& in) {
    Builder b(pre, in, true);
    return b.go(0, (int)in.size() - 1);
}
TreeNode* build_post_in(const vector<int>& post, const vector<int>& in) {
    Builder b(post, in, false);
    return b.go(0, (int)in.size() - 1);
}
```
