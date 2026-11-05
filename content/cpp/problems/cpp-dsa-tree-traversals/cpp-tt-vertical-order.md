---
id: cpp-tt-vertical-order
title: Vertical Order Traversal
difficulty: Hard
order: 7
tags: binary tree, bfs, coordinates, sorting
time_limit: 2
---
## Statement
Give every node coordinates: the root is at row 0, column 0; the left child of a node at `(r, c)` is at `(r+1, c−1)` and the right child at `(r+1, c+1)`. Return the **columns from left to right**. Inside a column, order nodes by **row** (top first) and, for nodes at the same row and column, by **value** (smaller first):

```cpp
vector<vector<int>> vertical_order(TreeNode* root);
```

```text
           3                column -2: 4
         /   \              column -1: 9
        9     8             column  0: 3 0 1     (0 and 1 share row 2: sorted by value)
       / \   / \            column  1: 8
      4   1 0   7           column  2: 7
```

This is the strict version of the problem (as on LeetCode 987). The tie rule matters: nodes from different subtrees can land on the same cell, and BFS order alone would list `1` before `0`.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input, one tree line each. Up to 2·10⁵ nodes, values may repeat. Trees can be chains of 2·10⁵ nodes, so don't recurse that deep.

**Output:** a line `columns=C`, then one line per column. Lists of more than 60 numbers are printed as `count=C hash=H` (a fingerprint), shorter ones in full; an empty list prints `(none)`.

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

vector<vector<int>> vertical_order(TreeNode* root) {
    // BFS order inside each column: ignores the same-cell tie rule
    map<int, vector<int>> col;
    queue<pair<TreeNode*, int>> q; if (root) q.push({root, 0});
    while (!q.empty()) {
        auto [n, c] = q.front(); q.pop();
        col[c].push_back(n->val);
        if (n->left) q.push({n->left, c - 1});
        if (n->right) q.push({n->right, c + 1});
    }
    vector<vector<int>> res;
    for (auto& [c, v] : col) res.push_back(v);
    return res;
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
        auto cols = vertical_order(root);
        cout << "columns=" << cols.size() << '\n';
        for (auto& c : cols) cout << show_vec(c) << '\n';
        free_tree(root);
    }
    return 0;
}
```

## Tests
=== sample
7 3 9 8 4 1 0 7
---
columns=5
4
9
3 0 1
8
7
=== sample
7 1 2 3 4 6 5 7
---
columns=5
4
2
1 5 6
3
7
=== hidden
0
---
columns=0
=== hidden
1 5
---
columns=1
5
=== hidden
7 1 2 # 3 # 4 #
---
columns=4
4
3
2
1
=== hidden
9 1 # 2 # 3 # 4 # 5
---
columns=5
1
2
3
4
5
=== hidden
10 5 4 6 # 2 2 # # 1 0
---
columns=3
4 0
5 2 2
6 1
=== hidden
0
11 0 # 1 # 2 # 1 # 4 # 1
22 0 4 5 3 5 5 # 4 # 6 # # 9 # # 4 2 4 # # 1 4
25 8 # 0 # 8 # 6 # 7 # 0 # 4 # 1 # 0 # 4 # 0 # 5 # 4
1 5
16 4 4 # 1 3 # 4 7 9 3 # 7 # 3 1 1
---
columns=0
columns=6
0
1
2
1
4
1
columns=5
4
3 4
4 6 1 4
0 5 5 2 4
5 9
columns=13
8
0
8
6
7
0
4
1
0
4
0
5
4
columns=1
5
columns=6
1
1 3 7
4 4 7
4 3 3
9
1
=== hidden
14 1 7 # # 6 9 # # 0 7 # # 2 1
9 5 4 # # 6 8 # # 4
6 1 8 5 7 # 4
17 7 # 0 # 4 # 9 # 0 # 9 # 5 # 3 # 0
25 8 # 7 # 6 # 1 # 4 # 9 # 6 # 2 # 0 # 0 # 7 # 4 # 6
20 7 4 # 5 # 8 # 1 # 0 # 5 # 8 # 7 # 6 # 7
---
columns=2
7 9 7 1
1 6 0 2
columns=2
4 8
5 6 4
columns=4
7
8
1 4
5
columns=9
7
0
4
9
0
9
5
3
0
columns=13
8
7
6
1
4
9
6
2
0
0
7
4
6
columns=11
7
6
7
8
5
0
1
8
5
4
7
=== hidden
0
7 8 # 2 # 5 # 9
10 9 7 7 4 6 0 4 2 7 4
9 1 # 6 # 0 # 2 # 5
3 7 5 9
4 3 1 # 9
---
columns=0
columns=4
8
2
5
9
columns=6
2
4
7 4 7
9 0 6
7
4
columns=5
1
6
0
2
5
columns=3
5
7
9
columns=3
9
1
3
=== hidden
@gen 4012636754 big
=== hidden
@gen 4012636755 big
=== hidden
@gen 4012636756 big

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
for _ in range(6 if not big else 2):
    n = r.randint(0, 14) if not big else 200000
    vals, L, R = rand_tree(n, 0, 9) if not big else rand_tree(n, 0, 1000, r.choice(["random", "complete", "deep", "zigzag", "left"]))
    print(tline(vals, L, R))
```

## Hints
- Record (column, row, value) for every node. Either BFS or DFS works for labelling, but the depth can be 2·10⁵.
- Sorting tuples compares them lexicographically, which is exactly the required order.
- Group consecutive entries with the same column into one output line.

## Solution
Two steps: **label**, then **sort**.

1. Traverse the tree (BFS here, which needs no recursion) and record a triple `(column, row, value)` for every node.
2. Sort the triples lexicographically. That single sort encodes the whole ordering rule: columns left to right, then rows top to bottom, then values for nodes sharing a cell.
3. Cut the sorted list into groups of equal column.

A common shortcut is to rely on BFS order inside each column. That already gives the rows in order, but it breaks the same-cell tie: two nodes from different subtrees at the same row and column must be ordered by value, not by discovery order.

Complexity: O(n log n) time for the sort, O(n) memory.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

vector<vector<int>> vertical_order(TreeNode* root) {
    if (!root) return {};
    // BFS gives rows in increasing order; record (row, value) per column
    vector<tuple<int, int, int>> cells;                 // (column, row, value)
    vector<tuple<TreeNode*, int, int>> cur{{root, 0, 0}}, next;
    while (!cur.empty()) {
        next.clear();
        for (auto [n, r, c] : cur) {
            cells.emplace_back(c, r, n->val);
            if (n->left) next.emplace_back(n->left, r + 1, c - 1);
            if (n->right) next.emplace_back(n->right, r + 1, c + 1);
        }
        swap(cur, next);
    }
    sort(cells.begin(), cells.end());                    // by column, then row, then value
    vector<vector<int>> res;
    int lastCol = INT_MIN;
    for (auto [c, r, v] : cells) {
        if (c != lastCol) { res.emplace_back(); lastCol = c; }
        res.back().push_back(v);
    }
    return res;
}
```
