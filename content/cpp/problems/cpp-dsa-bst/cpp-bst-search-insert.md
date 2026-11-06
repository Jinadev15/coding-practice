---
id: cpp-bst-search-insert
title: Search and Insert in a BST
difficulty: Easy
order: 1
tags: binary search tree, search, insert, iteration
time_limit: 2
---
## Statement
In a **binary search tree** (BST), every node's value is greater than all values in its left subtree and smaller than all values in its right subtree. Implement the two basic operations:

```cpp
bool bst_find(TreeNode* root, int x);           // is x in the tree?
TreeNode* bst_insert(TreeNode* root, int x);    // insert x as a new leaf (ignore x if already present); return the root
```

Both walk a single root-to-leaf path: compare `x` with the current node and go left if smaller, right if larger. A new value always becomes a **leaf**, attached where the search fell off the tree. Write them **iteratively** (or recursively with care): an insertion order like `1 2 3 …` turns the tree into a chain.

```text
insert 5 3 8 1 4      5
                     / \
                    3   8
                   / \
                  1   4
```

**Input:** cases until the end of input. Each case starts with a line `m`, then `m` lines `insert x` or `find x`, applied in order to an initially empty tree. At most 2·10⁵ operations per case, values fit in `int`. When the input is sorted, at most 5000 operations.

**Output:** for each `find`, `yes` or `no` on its own line; after the case, a line `tree: ` followed by the final tree.

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

bool bst_find(TreeNode* root, int x) { return false; }
TreeNode* bst_insert(TreeNode* root, int x) { return root ? root : new TreeNode(x); }
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
        int m = (int)rd_ll();
        TreeNode* root = nullptr;
        string out;
        for (int i = 0; i < m; ++i) {
            string op = rd_str(); int x = (int)rd_ll();
            if (op == "insert") root = bst_insert(root, x);
            else out += bst_find(root, x) ? "yes\n" : "no\n";
        }
        bool ok = true;
        string t = show_tree(root, m, &ok);
        cout << out << "tree: " << t << '\n';
        if (ok) free_tree(root);
        else return 0;
    }
    return 0;
}
```

## Tests
=== sample
8
insert 5
insert 3
insert 8
find 4
insert 1
insert 4
find 4
find 9
---
no
yes
no
tree: 5 3 8 1 4
=== hidden
2
find 7
find -1
---
no
no
tree: empty
=== hidden
3
insert 2
insert 2
find 2
---
yes
tree: 2
=== hidden
4
insert 1
insert 2
insert 3
find 3
---
yes
tree: 1 # 2 # 3
=== hidden
5
insert -2147483648
insert 2147483647
insert 0
find 2147483647
find -2147483648
---
yes
yes
tree: -2147483648 # 2147483647 0
=== hidden
6
insert 5
insert 4
insert 3
insert 6
find 5
find 2
---
yes
no
tree: 5 4 6 3
=== hidden
7
insert -8
find -1
insert 5
find 5
insert -9
find 2
find 2
8
insert 1
insert -8
insert -8
find 1
find 7
insert -8
insert -9
insert -9
3
insert 4
find -1
insert 6
9
insert 3
insert -9
insert 7
find -5
find 6
find -5
insert 4
insert 2
find -7
10
find -5
insert 0
insert 4
find -3
insert 2
find -5
insert -8
insert -3
insert 2
insert -8
1
find -9
2
insert 5
insert 7
13
find 2
insert -9
insert -8
insert -2
insert -3
insert 0
insert 0
find -5
insert -4
find -8
insert -5
insert 8
find -3
---
no
yes
no
no
tree: -8 -9 5
yes
no
tree: 1 -8 # -9
no
tree: 4 # 6
no
no
no
no
tree: 3 -9 7 # 2 4
no
no
no
tree: 0 -8 4 # -3 2
no
tree: empty
tree: 5 # 7
no
no
yes
yes
tree: -9 # -8 # -2 -3 0 -4 # # 8 -5
=== hidden
1
insert -5
12
find -9
insert -4
find -6
insert -2
insert -6
find -1
find -9
insert 9
insert -5
find 5
find 6
insert 6
2
find 5
insert -6
12
find -2
insert -4
find 2
find 9
insert 9
find 5
insert 2
insert 4
insert 8
insert -3
insert -8
insert -5
3
insert 5
insert 6
insert -4
12
insert 3
insert 4
find -2
find 2
insert 9
insert -8
insert -8
insert 4
find -7
insert 5
insert 4
insert -7
2
insert -6
find 8
1
insert -6
---
tree: -5
no
no
no
no
no
no
tree: -4 -6 -2 # -5 # 9 # # 6
no
tree: -6
no
no
no
no
tree: -4 -8 9 # -5 2 # # # -3 4 # # # 8
tree: 5 -4 6
no
no
no
tree: 3 -8 4 # -7 # 9 # # 5
no
tree: -6
tree: -6
=== hidden
10
insert 2
find 5
insert 2
find -3
insert 6
insert 1
insert 0
insert 6
find 0
insert 8
6
insert 2
insert 0
insert 5
insert -6
insert -7
insert 2
1
insert 4
11
insert -4
insert 4
insert -7
find -5
find -7
find -6
find 9
insert -7
find 3
find -5
insert -4
8
insert 5
insert 6
insert -9
insert -3
insert 6
find -1
insert -7
find 9
12
insert -5
find 9
find -1
insert 9
insert 3
find 4
insert 0
find 8
insert -4
insert -4
insert -5
insert 7
5
insert 2
insert -5
insert -3
insert 2
find 3
3
insert -7
insert 1
insert 0
---
no
no
yes
tree: 2 1 6 0 # # 8
tree: 2 0 5 -6 # # # -7
tree: 4
no
yes
no
no
no
no
tree: -4 -7 4
no
no
tree: 5 -9 6 # -3 # # -7
no
no
no
no
tree: -5 # 9 3 # 0 7 -4
no
tree: 2 -5 # # -3
tree: -7 # 1 0
=== hidden
@gen 3149685809 big
=== hidden
@gen 3149685810 big
=== hidden
@gen 3149685811 big

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
    if not big:
        m = r.randint(1, 14); ops = []
        for _ in range(m):
            ops.append((r.choice(["insert", "insert", "find"]), r.randint(-9, 9)))
    else:
        if r.random() < 0.5:
            m = 5000; xs = sorted(r.sample(range(-10**9, 10**9), m)); ops = [("insert", x) for x in xs[:4000]] + [("find", r.choice(xs)) for _ in range(1000)]
        else:
            m = 200000; xs = [r.randint(-10**9, 10**9) for _ in range(140000)]
            ops = [("insert", x) for x in xs] + [("find", r.choice(xs) + r.choice([0, 0, 1])) for _ in range(60000)]
            r.shuffle(ops)
    print(len(ops))
    for o, x in ops: print(o, x)
```

## Hints
- At each node, compare x with the value: equal means found, smaller means go left, larger means go right.
- Insert = search until you fall off the tree, then hang a new node there.
- A `TreeNode**` that points at "the child pointer to fill" removes all special cases, including the empty tree.

## Solution
**Search** is binary search on a linked structure: at each node, the BST property tells you which subtree could contain `x`, so the other one is discarded. The loop follows one path, so it takes O(h) steps.

**Insert** searches for `x` and attaches a new leaf where the search ran off the tree. The pointer-to-pointer `link` holds the address of the child pointer to fill (or of `root` itself), so the empty tree and the "attach as left" / "attach as right" cases are all one line, with no special case and no parent pointer.

Height matters: inserting random values gives an expected height of about 2.99·log₂ n, but sorted input gives a chain (h = n). Self-balancing trees (AVL, red-black, which is what `std::map` uses) fix that by rotating.

Complexity: O(h) per operation, O(1) extra memory with the loops.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

bool bst_find(TreeNode* root, int x) {
    while (root && root->val != x)
        root = x < root->val ? root->left : root->right;   // discard the half that can't contain x
    return root != nullptr;
}

TreeNode* bst_insert(TreeNode* root, int x) {
    TreeNode** link = &root;                 // the pointer that will hold the new node
    while (*link) {
        if (x == (*link)->val) return root;  // already present
        link = x < (*link)->val ? &(*link)->left : &(*link)->right;
    }
    *link = new TreeNode(x);                 // works for the empty tree too: link == &root
    return root;
}
```
