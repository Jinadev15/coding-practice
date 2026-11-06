# Building, Copying and Comparing Trees

The traversals lesson read trees. This lesson **writes** them: rebuild a tree from its traversals, save a tree to a string and load it back, build a BST from its preorder in linear time, assemble a tree from database-style parent links, and decide whether two trees (or a tree and a pattern) are the same. These are everyday engineering tasks. Saving a scene graph to disk, sending an AST between processes, rebuilding a robot's kinematic tree from a URDF file and caching identical subtrees in a compiler are all "construct or compare a tree".

You need the traversal orders (pre/in/post/level) and recursion. We use the same `TreeNode` as before:

```cpp
struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};
```

## 1. Why one traversal is not enough

Write down the preorder of these two trees:

```text
    1          1
   /            \
  2              2
```

Both give `1 2`. Their inorders differ (`2 1` versus `1 2`) and their postorders are both `2 1`. In general, **one traversal without null markers does not determine a tree**. There are two ways out:

1. **Two traversals, one of them inorder** (values distinct). Preorder or postorder tells you *which* node is the root; inorder tells you *what is left and what is right* of it.
2. **One traversal with null markers** (`#` for every missing child). Now the shape is written down explicitly, and values may repeat.

Preorder + postorder is **not** enough in general (the two trees above have the same pair). It works only for *full* trees, where every node has 0 or 2 children.

## 2. Preorder + inorder → tree

```text
pre = 3 9 20 15 7          inorder splits around the root:
in  = 9 3 15 20 7              [9]  3  [15 20 7]
                                left      right
```

The first preorder value, 3, is the root. In the inorder, 3 sits at index 1, so the left subtree has 1 node (`9`) and the right subtree has 3 nodes (`15 20 7`). Recurse on both sides.

Two engineering details turn the O(n²) textbook version into O(n):

- **Find the root's inorder position in O(1):** precompute `unordered_map<int,int> pos` from value to inorder index. A linear search would cost O(n) per node, O(n²) on a chain.
- **Never copy sub-vectors:** pass index ranges. Even better, keep one running index into the preorder. Preorder is N, the whole left subtree, then the whole right subtree, so if you build the left subtree *completely* before the right one, the next unused preorder value is always the root of the subtree you are building.

```cpp
struct PreInBuilder {
    const vector<int>& pre;
    unordered_map<int, int> pos;
    int next = 0;
    PreInBuilder(const vector<int>& p, const vector<int>& in) : pre(p) {
        for (int i = 0; i < (int)in.size(); ++i) pos[in[i]] = i;
    }
    TreeNode* go(int lo, int hi) {              // subtree whose inorder is in[lo..hi]
        if (lo > hi) return nullptr;
        TreeNode* n = new TreeNode(pre[next++]);
        int m = pos[n->val];
        n->left = go(lo, m - 1);                // must come first: it consumes the left part of pre
        n->right = go(m + 1, hi);
        return n;
    }
};
// usage: PreInBuilder b(pre, in); TreeNode* root = b.go(0, (int)in.size() - 1);
```

**Dry run** on the example (`next` starts at 0):

```text
go(0,4): take pre[0]=3, m=1 → left = go(0,0), right = go(2,4)
  go(0,0): take pre[1]=9, m=0 → left go(0,-1)=null, right go(1,0)=null
  go(2,4): take pre[2]=20, m=3 → left = go(2,2), right = go(4,4)
    go(2,2): take pre[3]=15
    go(4,4): take pre[4]=7
```

The same run as a table (`m` is the root's inorder index):

| call `go(lo,hi)` | `next` before | root taken | `m` | left range | right range |
|---|---|---|---|---|---|
| go(0,4) | 0 | 3 | 1 | 0..0 | 2..4 |
| go(0,0) | 1 | 9 | 0 | empty | empty |
| go(2,4) | 2 | 20 | 3 | 2..2 | 4..4 |
| go(2,2) | 3 | 15 | 2 | empty | empty |
| go(4,4) | 4 | 7 | 4 | empty | empty |

**Postorder + inorder** is the mirror image. Postorder is L R N, so read it **from the end** (N R L), and build the **right** subtree before the left.

Complexity: O(n) time and memory; recursion depth O(h).

## 3. Serialization: a tree to a string and back

A **codec** must turn any tree, with repeated values and any shape, into a string and back. Preorder with null markers is the simplest correct design:

```text
    1
   / \          serialize → "1 2 # # 3 4 # # 5 # #"
  2   3
     / \
    4   5
```

```cpp
void enc(TreeNode* n, string& out) {
    if (!n) { out += "# "; return; }
    out += to_string(n->val) + ' ';
    enc(n->left, out);
    enc(n->right, out);
}

TreeNode* dec(const string& s, size_t& i) {          // i = shared read position
    while (s[i] == ' ') ++i;
    if (s[i] == '#') { ++i; return nullptr; }
    size_t used; int v = stoi(s.substr(i, 12), &used); i += used;
    TreeNode* n = new TreeNode(v);
    n->left = dec(s, i);                             // left subtree's tokens come first
    n->right = dec(s, i);
    return n;
}
```

Why decoding is unambiguous: every node is followed by exactly two complete subtree encodings, each either `#` or another node with its two subtrees. Such a code is a **prefix code**: the decoder always knows where a subtree ends. A tree of n nodes produces n values and n + 1 markers.

The level-order format used in these problems (`1 2 3 # # 4 5`) is the other standard choice. Encode with BFS, writing `#` for missing children, and decode with a queue that hands out the next two tokens as children of the next real node.

Pitfalls: a delimiter is required (`12` versus `1 2`), negative numbers must parse, and building substrings at every recursive call turns O(n) into O(n²).

## 4. A BST from its preorder in O(n)

For a binary search tree, preorder alone is enough: the inorder is the sorted values. But calling "sort, then preorder + inorder" costs O(n log n), and inserting the values one by one costs O(n²) on sorted input. The linear solution uses **bounds**:

```cpp
TreeNode* build(const vector<int>& pre, size_t& i, long long bound) {
    if (i == pre.size() || pre[i] >= bound) return nullptr;   // belongs to an ancestor's right side
    TreeNode* n = new TreeNode(pre[i++]);
    n->left = build(pre, i, n->val);        // smaller than this node
    n->right = build(pre, i, bound);        // between this node and the inherited bound
    return n;
}
// root = build(pre, i = 0, LLONG_MAX)
```

```text
pre = 8 5 1 7 10 12

build(∞):  8
  left  build(8):  5
     left  build(5):  1   (left build(1): 7 ≥ 1 → null; right build(5): 7 ≥ 5 → null)
     right build(8):  7   (children: 10 ≥ 7 → null, 10 ≥ 8 → null)
  right build(∞): 10
     left build(10): 12 ≥ 10 → null
     right build(∞): 12
```

Each call either consumes a value or returns null immediately, and there are at most 2n + 1 calls, so the time is O(n). A `long long` bound lets `INT_MAX` be a value.

## 5. Monotonic stacks build trees too

The **maximum binary tree** (root = the maximum, left/right = the maximum trees of the two sides) is a *Cartesian tree*. The literal definition is O(n²) on sorted input. A stack holding the current right spine (decreasing values) builds it in O(n):

```cpp
TreeNode* construct_maximum(const vector<int>& a) {
    vector<TreeNode*> st;
    for (int x : a) {
        TreeNode* n = new TreeNode(x), *last = nullptr;
        while (!st.empty() && st.back()->val < x) { last = st.back(); st.pop_back(); }
        n->left = last;                          // smaller nodes go under x, on its left
        if (!st.empty()) st.back()->right = n;   // x hangs to the right of the nearest greater element
        st.push_back(n);
    }
    return st.empty() ? nullptr : st.front();
}
```

The same "path stack" idea parses a preorder printed with depths (`1-2--3--4-5--6--7`): keep the root-to-current path in a vector. A node of depth D is the child of `path[D-1]`, so truncate the path to size D, attach the node (left first, then right), and push it.

## 6. From parent links

Data often arrives as rows `(parent, child, is_left)` in arbitrary order. Use a hash map `value → TreeNode*` that creates nodes on first sight. Every link then sets one pointer, and the **root is the only value that never appears as a child**. That's O(n) with hashing, with no recursion and no ordering assumptions.

## 7. Comparing trees

**Identical:** same shape and values. Recursively: both empty → true; one empty → false; otherwise compare the values and both pairs of children.

```cpp
bool same(TreeNode* a, TreeNode* b) {
    if (!a || !b) return a == b;
    return a->val == b->val && same(a->left, b->left) && same(a->right, b->right);
}
```

**Mirror / symmetric:** the same recursion with crossed children: `mirror(a->left, b->right) && mirror(a->right, b->left)`. **Invert** a tree by swapping the children of every node.

**Subtree:** is `sub` identical to the complete subtree under some node of `root`? Calling `same` at every node is O(n·m). That's fine for small inputs and quadratic for two long chains of equal values. The linear method reuses section 3: serialize both trees in preorder **with null markers**, as integer tokens. `sub` is a subtree exactly when its token sequence occurs contiguously inside `root`'s, and KMP finds that in O(n + m).

Why a match can't be a false positive: the pattern starts with a value (not a marker), so the match starts at a node; and because the code is a prefix code, the block from that node to the end of the match is exactly its full subtree. Without null markers, `4 1 2` would match the top of a larger subtree.

Another linear approach is **Merkle hashing**: compute a hash for every subtree bottom-up from (value, hash(left), hash(right)) and compare hashes, verifying candidates to rule out collisions. Git uses the same idea to detect identical directories.

## 8. Complexity summary

| Task | Naive | Good |
|---|---|---|
| pre + in → tree | O(n²) (linear search, copies) | O(n) with a hash map and a running index |
| BST from preorder | O(n²) by insertion | O(n) with bounds or a stack |
| maximum binary tree | O(n²) | O(n) with a monotonic stack |
| serialize / deserialize | O(n²) with substrings | O(n) with a shared index |
| subtree check | O(n·m) | O(n + m) with serialization + KMP |

## 9. Recognising the pattern

- "Construct from traversals": find the root in one traversal and split with inorder. Use a value → index map.
- "Preorder of a BST": bounds recursion.
- "Root is the maximum / minimum of a range": Cartesian tree, monotonic stack.
- "Depth markers", "indentation", "nested parentheses": a path stack.
- "Same structure", "subtree", "duplicate subtrees": serialization or subtree hashing.
- "Store / send / cache a tree": a codec with null markers.

## 10. Common mistakes

1. **Serializing without null markers** (or without delimiters): different trees give the same string.
2. **Building the right subtree before the left** while consuming preorder with a running index. That's correct only for postorder read backwards.
3. **Linear search for the root in the inorder**: O(n²) on chains.
4. **Using `int` bounds** for the BST-from-preorder recursion: `INT_MAX` as a value breaks it.
5. **Assuming distinct values** where the problem doesn't promise them. Traversal pairs need distinct values; codecs don't.
6. **Subtree check that matches only the top part** of a subtree (forgetting that the leaves of `sub` must be leaves in `root` too).
7. **Recursion on degenerate inputs** in production. A codec run on a 10⁶-node chain needs an iterative encoder and decoder.

## 11. Interview questions

**Q: Can you rebuild a tree from preorder and postorder?** Only if it's full (every node has 0 or 2 children). Otherwise a single child can be on either side.

**Q: How many null markers does a preorder serialization contain?** n + 1 for n nodes: every node has two child slots (2n), and n − 1 of them are filled by real nodes.

**Q: Why is deserialization with a shared index O(n)?** Each token is read exactly once, and each call does O(1) work besides its recursive calls.

**Q: How do you find all duplicate subtrees?** Serialize every subtree bottom-up (or give it an integer id from (value, id(left), id(right)) through a hash map). Equal ids mean identical subtrees. That's O(n) with ids, and O(n²) if you store full strings.

**Q: Why does the monotonic-stack construction run in O(n) when one step can pop many nodes?** Each node is pushed once and popped at most once, so the total number of pops is at most n (an amortised argument).

## Check your understanding

1. Build the tree from `pre = 1 2 4 5 3 6` and `in = 4 2 5 1 3 6`, and give its postorder.
2. Serialize `5 1 2 3 # 4` (level-order input) in preorder with `#` markers.
3. In `build(pre, i, bound)`, why does the right child inherit `bound` instead of using the node's value?
4. Give two different trees with the same preorder and postorder.
5. Why must the subtree pattern be serialized with markers on the *leaf* children too?

<details>
<summary>Answers</summary>

1. The root is 1. Inorder `4 2 5 | 1 | 3 6`: the left part has root 2 with children 4 and 5; the right part has root 3 with right child 6. Postorder: `4 5 2 6 3 1`.
2. The tree is 1 with children 2 and 3, and 4 is the right child of 2. Preorder with markers: `1 2 # 4 # # 3 # #`.
3. The right subtree of `v` holds values greater than `v`, but they must still be smaller than the ancestor that bounds `v`'s whole subtree. The lower bound `v` is implied automatically, because smaller values were already consumed by the left subtree.
4. `1` with a left child `2`, and `1` with a right child `2`: both have preorder `1 2` and postorder `2 1`.
5. The markers under the pattern's leaves force the matching nodes in `root` to be leaves too. Without them, the pattern would also match a subtree that continues below.

</details>
