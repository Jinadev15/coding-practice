---
id: cpp-tt-max-width
title: Maximum Width with Heap Indices
difficulty: Medium
order: 6
tags: binary tree, bfs, heap indexing, overflow
time_limit: 2
---
## Statement
The **width** of a level is the number of positions between its leftmost and rightmost nodes, inclusive, **counting the missing positions in between** as if the level were part of a complete tree. Return the maximum width over all levels:

```cpp
long long max_width(TreeNode* root);   // 0 for the empty tree
```

```text
          1                 level 1 (3, 2): width 2
        /   \
       3     2              level 2 has 5 and 9 at positions 0 and 3: width 4
      /       \
     5         9            level 3 has 6 and 7 at positions 0 and 6: width 7
    /         /
   6         7              answer: 7
```

Number the positions like a binary heap: if a node has index `i`, its children have `2i` and `2i+1`. A level's width is `last − first + 1`. Those indices double at every level, so after 64 levels they no longer fit in any integer type, even when the widths are tiny. **Re-base the indices at every level** by subtracting the level's first index before computing children.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input, one tree line each. Up to 2·10⁵ nodes. The answer is guaranteed to be below 2⁶². Trees can be chains of 2·10⁵ nodes, so recursion is not allowed to go that deep. BFS is the natural fit.

**Output:** one line with the maximum width.

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

long long max_width(TreeNode* root) {
    // counts only the real nodes of each level: wrong when there are gaps
    long long best = 0;
    vector<TreeNode*> cur; if (root) cur.push_back(root);
    while (!cur.empty()) {
        best = max(best, (long long)cur.size());
        vector<TreeNode*> nx;
        for (auto* n : cur) { if (n->left) nx.push_back(n->left); if (n->right) nx.push_back(n->right); }
        cur.swap(nx);
    }
    return best;
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
        TreeNode* root = rd_tree();
        cout << max_width(root) << '\n';
        free_tree(root);
    }
    return 0;
}
```

## Tests
=== sample
10 1 3 2 5 # # 9 6 # 7
---
7
=== sample
7 1 3 2 5 3 # 9
---
4
=== hidden
0
---
0
=== hidden
1 4
---
1
=== hidden
5 1 2 # 3 #
---
1
=== hidden
11 1 2 3 4 # # 5 6 # # 7
---
8
=== hidden
15 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15
---
8
=== hidden
25 77 5 80 # 23 14 # # 51 18 # # 49 60 # # 42 31 # # 49 55 # # 23
6 28 24 15 52 39 73
10 25 42 38 # 63 # # 73 # 36
23 43 32 53 51 89 69 79 30 # 87 # 58 23 # # # # # # # # # 67
2 5 89
14 4 55 64 # 70 2 # # # 67 99 # # 28
---
2
3
2
6
1
2
=== hidden
14 45 86 74 # # 29 59 # 50 90 # # # 15
3 94 # 52
23 49 # 95 # 84 # 6 # 90 # 47 # 44 # 16 # 20 # 19 # 2 # 18
14 68 38 # 96 89 1 # 60 55 5 # # 93 93
5 69 20 61 71 88
14 60 97 60 68 20 56 24 97 5 71 96 25 65 76
---
2
1
1
7
2
7
=== hidden
0
24 87 78 29 85 88 84 28 # # 45 68 # # 52 # 35 # # # # # # 42 36
27 61 # 71 # 95 # 65 # 28 # 94 # 23 # 30 # 18 # 89 # 48 # 26 # 27 # 1
16 79 76 93 43 79 17 # # # # # 89 # 26 # 36
22 40 50 57 78 64 31 56 24 47 # 41 14 52 # # # 26 # # # # 59
12 75 5 # 96 # 40 # 92 # 0 # 81
---
0
5
1
3
8
1
=== hidden
@gen 56927737 big
=== hidden
@gen 56927738 big
=== hidden
@gen 56927739 big

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
CAP = 1 << 62
def width_ok(L, R):
    if not L: return True
    cur = [(0, 0)]
    while cur:
        f = cur[0][1]
        if cur[-1][1] - f + 1 >= CAP: return False
        nx = []
        for u, i in cur:
            i -= f
            if L[u] >= 0: nx.append((L[u], 2 * i))
            if R[u] >= 0: nx.append((R[u], 2 * i + 1))
        cur = nx
    return True
def twin(n):
    # root; left child runs down a right-chain, right child down a left-chain: width stays 2 forever
    L = [-1] * n; R = [-1] * n
    if n > 1: L[0] = 1
    if n > 2: R[0] = 2
    a, b = 1, 2
    for i in range(3, n):
        if i % 2: R[a] = i; a = i
        else: L[b] = i; b = i
    return L, R
for _ in range(6 if not big else 2):
    n = r.randint(0, 14) if not big else 200000
    while True:
        k = r.choice(KINDS + ["twin"])
        L, R = twin(n) if k == "twin" else shape(n, k)
        if width_ok(L, R): break
    print(tline([r.randint(0, 99) for _ in range(n)], L, R))
```

## Hints
- Store (node, index) pairs in the BFS. The children of index `i` are `2i` and `2i+1`.
- Width of a level = index of its last node − index of its first node + 1.
- Subtract the level's first index from every index before computing the children, otherwise a deep chain overflows.

## Solution
Give each node its heap index: the root is 0, and the children of `i` are `2i` and `2i+1`. Within one level, these indices are exactly the positions in a complete tree, so the width is `last − first + 1`.

**Overflow:** in a chain of depth 200 000 the raw index would be about 2²⁰⁰⁰⁰⁰. Subtracting the level's first index before computing children keeps only **relative** positions. A level's relative positions are below its width, and the next level's are below twice that, so everything stays below 2⁶³ as long as the answer does. Using `unsigned long long` also makes any intermediate wrap-around well defined instead of undefined behaviour.

Complexity: O(n) time, O(w) memory.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

long long max_width(TreeNode* root) {
    if (!root) return 0;
    long long best = 0;
    vector<pair<TreeNode*, unsigned long long>> cur{{root, 0}}, next;
    while (!cur.empty()) {
        unsigned long long first = cur.front().second;
        best = max(best, (long long)(cur.back().second - first + 1));
        next.clear();
        for (auto [n, idx] : cur) {
            unsigned long long i = idx - first;              // re-base: this level now starts at 0
            if (n->left) next.push_back({n->left, 2 * i});
            if (n->right) next.push_back({n->right, 2 * i + 1});
        }
        swap(cur, next);
    }
    return best;
}
```
