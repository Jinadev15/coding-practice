---
id: cpp-tc-codec
title: Serialize and Deserialize a Tree
difficulty: Medium
order: 4
tags: binary tree, serialization, codec, preorder
time_limit: 2
---
## Statement
Design a **codec**: turn a tree into a string and back.

```cpp
string serialize(TreeNode* root);
TreeNode* deserialize(const string& data);
```

The format is yours. The driver serializes the tree, **frees the original**, deserializes the string, and prints the result, which must be identical to the original. Values can be negative and repeat, and the tree can be any shape, so a traversal *without* null markers is not enough. Two standard designs:

- **Preorder with null markers:** `1 2 # 4 # # 3 # #`. Deserialize with a recursive "read one token: `#` → null, otherwise make a node, then read the left subtree, then the right".
- **Level order with null markers**, like the input format of these problems, deserialized with a queue.

Make deserialization O(n) overall: parse with an index or a `string_view`, and don't create substrings over and over.

**Tree format (input).** A tree is one line `k t1 t2 … tk`: `k` level-order (BFS) tokens, each an integer value or `#` for a missing child. Children are listed only for real nodes and trailing `#` are dropped, so `0` is the empty tree. Example: `5 1 2 3 # 4` is the tree below (4 is the right child of 2).

```text
    1
   / \
  2   3
   \
    4
```

**Input:** cases until the end of input, one tree line each. Up to 2·10⁵ nodes, values fit in `int`.

Trees can be degenerate chains of up to 2·10⁵ nodes. The driver runs your code on a thread with a 256 MB stack, so plain recursion is safe here (on a normal 8 MB stack it would not be).

**Output:** the deserialized tree, one line per case.

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

string serialize(TreeNode* root) { return ""; }
TreeNode* deserialize(const string& data) { return nullptr; }
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
        TreeNode* root = rd_tree();
        long long n = NODES_;
        string data = serialize(root);
        free_tree(root);                      // the codec must not rely on the old nodes
        TreeNode* copy = deserialize(data);
        bool ok = true;
        cout << show_tree(copy, n + 1, &ok) << '\n';
        if (ok) free_tree(copy);
        else return 0;
        NODES_ = 0;
    }
    return 0;
}
```

## Tests
=== sample
7 1 2 3 # # 4 5
---
1 2 3 # # 4 5
=== hidden
0
---
empty
=== hidden
1 -7
---
-7
=== hidden
7 1 1 # 1 # 1 #
---
1 1 # 1 # 1
=== hidden
3 -2147483648 # 2147483647
---
-2147483648 # 2147483647
=== hidden
7 1 2 3 4 5 6 7
---
1 2 3 4 5 6 7
=== hidden
11 -6 # -4 # 1 # -5 # 3 # -1
23 -5 # 5 # 5 -7 # 4 # -9 # # 4 -6 # -2 # 2 0 # # # 0
21 -6 # 3 # -1 # -7 # 8 # -1 # 4 # -7 # -4 # 6 # 5
9 6 # 0 # 0 2 # # 3
0
21 5 # -4 -1 -3 -5 # # -9 2 # # # 6 -7 # -3 # -4 # -3
---
-6 # -4 # 1 # -5 # 3 # -1
-5 # 5 # 5 -7 # 4 # -9 # # 4 -6 # -2 # 2 0 # # # 0
-6 # 3 # -1 # -7 # 8 # -1 # 4 # -7 # -4 # 6 # 5
6 # 0 # 0 2 # # 3
empty
5 # -4 -1 -3 -5 # # -9 2 # # # 6 -7 # -3 # -4 # -3
=== hidden
6 -5 -8 -9 # -8 -5
1 8
13 -6 9 # # -3 7 # # 4 5 # # 7
10 1 7 # 4 # 7 # -6 # -3
11 9 -5 4 # # -5 -9 # # -5 -5
7 -2 -2 # 8 5 -9 -8
---
-5 -8 -9 # -8 -5
8
-6 9 # # -3 7 # # 4 5 # # 7
1 7 # 4 # 7 # -6 # -3
9 -5 4 # # -5 -9 # # -5 -5
-2 -2 # 8 5 -9 -8
=== hidden
1 6
6 7 -2 -1 0 -4 -4
4 -3 -8 # -6
1 8
18 1 -1 # # -7 7 # # 5 -2 # # 9 6 # # 5 4
9 -4 -8 6 # # # 1 # -3
---
6
7 -2 -1 0 -4 -4
-3 -8 # -6
8
1 -1 # # -7 7 # # 5 -2 # # 9 6 # # 5 4
-4 -8 6 # # # 1 # -3
=== hidden
@gen 4111433269 big
=== hidden
@gen 4111433270 big
=== hidden
@gen 4111433271 big

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
    n = r.randint(0, 12) if not big else 200000
    vals, L, R = rand_tree(n, -9, 9) if not big else rand_tree(n, -2**31, 2**31 - 1)
    print(tline(vals, L, R))
```

## Hints
- Encode null children explicitly, otherwise different trees give the same string.
- Preorder with markers can be decoded by a recursive function that reads one token and then decodes left and right.
- Thread a single read position through the recursive decoder.

## Solution
**Why null markers:** a plain preorder `1 2` doesn't say whether 2 is a left or a right child. With markers, every node is followed by exactly two subtree encodings, and each one is either `#` or a complete encoding. So the string parses in exactly one way: it is a *prefix code*.

**Serialize:** preorder, writing `#` for every null child. A tree of n nodes produces n values and n + 1 markers.

**Deserialize** mirrors the encoder: read one token; `#` means an empty subtree, otherwise create the node, then **recursively read its left subtree and then its right subtree** from the same position `i`. Because the encoder wrote the left subtree completely before the right, the reader consumes them in the same order.

Passing a shared index (`size_t& i`) keeps parsing linear. Splitting the string into substrings at every call would be O(n²).

Complexity: O(n) time and string size for both directions, O(h) recursion depth.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};

// preorder with '#' for null, tokens separated by spaces
static void enc(TreeNode* n, string& out) {
    if (!n) { out += "# "; return; }
    out += to_string(n->val);
    out += ' ';
    enc(n->left, out);
    enc(n->right, out);
}
string serialize(TreeNode* root) { string s; enc(root, s); return s; }

static TreeNode* dec(const string& s, size_t& i) {
    while (i < s.size() && s[i] == ' ') ++i;
    if (i >= s.size()) return nullptr;
    if (s[i] == '#') { ++i; return nullptr; }
    bool neg = s[i] == '-'; if (neg) ++i;
    long long v = 0;
    while (i < s.size() && isdigit((unsigned char)s[i])) v = v * 10 + (s[i++] - '0');
    TreeNode* n = new TreeNode((int)(neg ? -v : v));
    n->left = dec(s, i);            // the left subtree's tokens come next...
    n->right = dec(s, i);           // ...then the right subtree's
    return n;
}
TreeNode* deserialize(const string& data) { size_t i = 0; return dec(data, i); }
```
