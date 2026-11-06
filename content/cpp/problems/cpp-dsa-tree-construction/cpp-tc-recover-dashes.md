---
id: cpp-tc-recover-dashes
title: Recover a Tree from a Dashed Preorder
difficulty: Hard
order: 8
tags: binary tree, construction, parsing, stack
time_limit: 2
---
## Statement
A tree was printed by a preorder walk that writes, for every node, `D` dashes followed by the node's value, where `D` is the node's depth (the root has depth 0). If a node has only one child, it is the **left** child. Recover the tree:

```cpp
TreeNode* recover_from_dashes(const string& s);
```

```text
s = "1-2--3--4-5--6--7"          1
                               /   \
                              2     5
                             / \   / \
                            3   4 6   7
```

Parse the string into (depth, value) pairs and keep a **stack holding the current root-to-node path**. When a node of depth `D` arrives, pop the stack until it has exactly `D` entries. The top is then the parent: attach the node as its left child if that is free, otherwise as its right child. Then push the node.

**Input:** cases until the end of input, one string per line. Values are integers from 1 to 10⁹. The tree has at most 2·10⁵ nodes, and each string is at most 2·10⁶ characters long.

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

TreeNode* recover_from_dashes(const string& s) { return nullptr; }
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
        string s = rd_str();
        TreeNode* root = recover_from_dashes(s);
        bool ok = true;
        cout << show_tree(root, (long long)s.size() + 1, &ok) << '\n';
        if (ok) free_tree(root);
        else return 0;
    }
    return 0;
}
```

## Tests
=== sample
1-2--3--4-5--6--7
---
1 2 5 3 4 6 7
=== sample
1-401--349---90--88
---
1 401 # 349 88 90
=== hidden
7
---
7
=== hidden
1-2--3---4
---
1 2 # 3 # 4
=== hidden
10-20-30
---
10 20 30
=== hidden
1-2--3--4-5--6
---
1 2 5 3 4 6
=== hidden
68-23--91---36----74---31----31-----70
23-82--29---87
85-99--73---14----12-----86------36-------73--------80---------38
55-98--41---66---36----77-46--36---13----75
61-36
---
68 23 # 91 # 36 31 74 # 31 # # # 70
23 82 # 29 # 87
85 99 # 73 # 14 # 12 # 86 # 36 # 73 # 80 # 38
55 98 46 41 # 36 # 66 36 13 # # # 77 # 75
61 36
=== hidden
82-1--16--89-13
61-79-46--32---49----25--39
39-57-71
84-55--71---89----49-----16------35-------5--------97---------50----------95
51-46--49-62--24
---
82 1 13 16 89
61 79 46 # # 32 39 49 # # # 25
39 57 71
84 55 # 71 # 89 # 49 # 16 # 35 # 5 # 97 # 50 # 95
51 46 62 49 # 24
=== hidden
96-93--80---87----47----18-----61------91
4-99--48---40---36--62-86--57--3
38-98--12---58----62-----11------2-------74--------45---64
26
72-22--98---25----1-----64------12-------56--------48---------94----------92-----------86
---
96 93 # 80 # 87 # 47 18 # # 61 # 91
4 99 86 48 62 57 3 40 36
38 98 # 12 # 58 64 62 # # # 11 # 2 # 74 # 45
26
72 22 # 98 # 25 # 1 # 64 # 12 # 56 # 48 # 94 # 92 # 86
=== hidden
@gen 3291866395 big
=== hidden
@gen 3291866396 big
=== hidden
@gen 3291866397 big

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
def dashed(vals, L, R):
    out, st = [], [(0, 0)]
    while st:
        u, d = st.pop(); out.append("-" * d + str(vals[u]))
        if R[u] >= 0: st.append((R[u], d + 1))
        if L[u] >= 0: st.append((L[u], d + 1))
    return "".join(out)
def leftify(L, R):
    for u in range(len(L)):
        if L[u] < 0 and R[u] >= 0: L[u], R[u] = R[u], -1
    return L, R
for _ in range(5 if not big else 2):
    if not big:
        n = r.randint(1, 12); L, R = leftify(*shape(n, r.choice(KINDS)))
    else:
        if r.random() < 0.5: n = 1900; L, R = leftify(*shape(n, r.choice(["left", "zigzag"])))
        else: n = 200000; L, R = leftify(*shape(n, "random"))
    vals = [r.randint(1, 10**9 if big else 99) for _ in range(n)]
    print(dashed(vals, L, R))
```

## Hints
- First separate the string into (number of dashes, value) pairs.
- Keep a vector holding the current root-to-node path. A node at depth D is a child of the entry at index D − 1.
- Before attaching, shrink the path to size D. Attach as the left child if it is empty, otherwise as the right child.

## Solution
In a preorder walk, when a node at depth `D` is printed, the nodes printed before it that are still "open" form exactly the path from the root to its parent, one per depth `0 … D−1`. Everything deeper than `D−1` on the current path belongs to subtrees that are already finished.

So keep the current path in a vector: `path[d]` is the latest node at depth `d`. On reading `(D, v)`, cut the path back to length `D`. `path[D−1]` is the parent. Preorder visits the left child first, so the first child attached to a node is its left child and the second is its right child. Then push the new node as `path[D]`.

The parse is a single scan over the string: count dashes, read digits.

Complexity: O(|s|) time. The path holds at most height + 1 entries. No recursion is needed, so deep trees are fine.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

TreeNode* recover_from_dashes(const string& s) {
    vector<TreeNode*> path;                       // path[d] = the most recent node at depth d
    size_t i = 0;
    while (i < s.size()) {
        size_t depth = 0;
        while (i < s.size() && s[i] == '-') { ++depth; ++i; }
        long long v = 0;
        while (i < s.size() && isdigit((unsigned char)s[i])) v = v * 10 + (s[i++] - '0');
        TreeNode* n = new TreeNode((int)v);
        path.resize(depth);                       // drop everything deeper than the parent
        if (!path.empty()) {
            TreeNode* parent = path.back();
            (parent->left ? parent->right : parent->left) = n;   // left first, then right
        }
        path.push_back(n);
    }
    return path.empty() ? nullptr : path.front();
}
```
