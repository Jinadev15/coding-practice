# Binary Search Trees

A **binary search tree** (BST) keeps its values ordered *in the shape of the tree*. That turns binary search, which on an array needs contiguous sorted storage, into something that also supports fast insertion and deletion. `std::set` and `std::map` are balanced BSTs (red-black trees), and so are the ordered indexes inside many databases, the event queues of simulators and the interval structures of schedulers. This lesson builds BST operations from scratch: search, insert, the three cases of delete, validation, order queries (k-th smallest, successor, predecessor), iterators, two-sum, range queries, trimming, and repairing a corrupted tree.

You need the traversals lesson (especially iterative inorder) and the tree recursion patterns. The node type is the usual one from the traversals lesson. Every code block below assumes it:

```cpp
struct TreeNode {
    int val;
    TreeNode *left, *right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};
```

## 1. The BST property

For **every** node `n`: all values in `n`'s left subtree are smaller than `n->val`, and all values in its right subtree are larger. (We use distinct values; with duplicates you pick a side, for example "equal goes right", and stick to it.)

```text
            8
          /   \
         3     10
        / \      \
       1   6      14
          / \    /
         4   7  13
```

Two consequences drive everything in this lesson:

1. **Inorder traversal gives the values in sorted order:** 1 3 4 6 7 8 10 13 14.
2. **At any node, a comparison tells you which subtree can contain a value.** One whole subtree is discarded at each step, exactly like binary search discards half of an array.

The property is about *whole subtrees*, not just children. This tree is **not** a BST, although every node is correct relative to its parent: 4 is in the right subtree of 5, yet smaller than 5.

```text
      5
     / \
    1   7
       / \
      4   8
```

## 2. Search and insert: one root-to-leaf path

```cpp
bool bst_find(TreeNode* root, int x) {
    while (root && root->val != x)
        root = x < root->val ? root->left : root->right;
    return root != nullptr;
}

TreeNode* bst_insert(TreeNode* root, int x) {
    TreeNode** link = &root;                       // address of the pointer to fill
    while (*link) {
        if (x == (*link)->val) return root;        // already there
        link = x < (*link)->val ? &(*link)->left : &(*link)->right;
    }
    *link = new TreeNode(x);                       // a new value always becomes a leaf
    return root;
}
```

The pointer-to-pointer `link` is the same trick as with linked lists: it points at "the child pointer we will overwrite", so inserting into an empty tree, as a left child or as a right child, is all one line.

**Dry run:** insert 5 into the tree from section 1.

| at node | compare | go | link now points to |
|---|---|---|---|
| 8 | 5 < 8 | left | 8's `left` |
| 3 | 5 > 3 | right | 3's `right` |
| 6 | 5 < 6 | left | 6's `left` |
| 4 | 5 > 4 | right | 4's `right` (null) → new node 5 here |

**Cost: O(h)** where h is the height. And h depends entirely on the insertion order:

| insertion order | shape | height |
|---|---|---|
| random | bushy | about 2.99·log₂ n on average (≈ 53 for 2·10⁵) |
| sorted (1, 2, 3, …) | a chain | n − 1 |
| middle-first (see section 6) | perfectly balanced | ⌊log₂ n⌋ |

Plain BSTs therefore have O(n) worst-case operations. **Self-balancing** BSTs (AVL trees, red-black trees, treaps) restore O(log n) by rotating after updates. That's a later topic, but everything in this lesson works the same on them.

## 3. Delete: three cases

Find the node, then:

1. **Leaf:** just remove it.
2. **One child:** splice it out: its parent adopts the child.
3. **Two children:** you can't simply remove it. Replace its value with its **inorder successor** `s`, the leftmost node of its right subtree, which is the next larger value. `s` has no left child (it is leftmost), so removing `s` is case 1 or 2.

```cpp
TreeNode* bst_delete(TreeNode* root, int x) {
    TreeNode** link = &root;
    while (*link && (*link)->val != x)
        link = x < (*link)->val ? &(*link)->left : &(*link)->right;
    TreeNode* n = *link;
    if (!n) return root;                               // not found
    if (n->left && n->right) {                         // case 3
        TreeNode** s = &n->right;
        while ((*s)->left) s = &(*s)->left;            // leftmost of the right subtree
        n->val = (*s)->val;                            // take the successor's value
        link = s; n = *s;                              // and delete the successor node instead
    }
    *link = n->left ? n->left : n->right;              // cases 1 and 2 in one line
    delete n;
    return root;
}
```

```text
delete 3 (two children):      8                    8
                            /   \                /   \
                           3     10    ──►      4     10
                          / \      \           / \      \
                         1   6      14        1   6      14
                            / \                    \
                           4   7                    7
```

The successor 4 moves up into 3's node, and the old 4 (a leaf) is removed. Why order is preserved: 4 is larger than everything in the left subtree (1) and smaller than everything else in the right subtree (6, 7). Using the **predecessor** (rightmost of the left subtree) is equally correct, but gives a different tree, so problems usually say which one to use.

## 4. Validation: bounds, not neighbours

Checking `left->val < val < right->val` at every node accepts the broken tree from section 1. The correct check passes down an **open interval** that every value in the subtree must lie in:

```cpp
bool valid(TreeNode* n, long long lo, long long hi) {
    if (!n) return true;
    if (n->val <= lo || n->val >= hi) return false;
    return valid(n->left, lo, n->val) && valid(n->right, n->val, hi);
}
// valid(root, LLONG_MIN, LLONG_MAX)
```

The bounds are `long long` so that `INT_MIN` and `INT_MAX` are legal values. Equivalent alternative: an inorder walk must be strictly increasing, so compare each value with the previous one.

## 5. Order queries

### 5.1 Successor and predecessor of any value

The **successor** of `x` is the smallest value greater than `x`, whether or not `x` is in the tree. Walk down from the root keeping the best candidate:

```cpp
TreeNode* successor(TreeNode* root, int x) {
    TreeNode* best = nullptr;
    while (root) {
        if (root->val > x) { best = root; root = root->left; }   // candidate; look for a smaller one
        else root = root->right;
    }
    return best;
}
```

Dry run: successor of 5 in the section-1 tree.

| node | val > 5? | best | next |
|---|---|---|---|
| 8 | yes | 8 | left (3) |
| 3 | no | 8 | right (6) |
| 6 | yes | 6 | left (4) |
| 4 | no | 6 | right (null) |

Answer: 6. The predecessor is symmetric (`val < x`: record, go right). This is exactly what `std::set::upper_bound` does internally.

### 5.2 k-th smallest

Run iterative inorder and stop after k pops: O(h + k). For many queries on a changing tree, store each node's **subtree size** and descend: if `size(left) ≥ k` go left; if `size(left) + 1 == k` answer the node; otherwise go right with `k − size(left) − 1`. That's an *order-statistic tree*, O(h) per query.

## 6. Building a balanced BST from sorted data

Pick the middle element as the root and recurse on both halves. The result has height ⌈log₂(n+1)⌉ − 1 and inorder equal to the array.

```cpp
TreeNode* build(const vector<int>& a, int lo, int hi) {
    if (lo > hi) return nullptr;
    int mid = lo + (hi - lo) / 2;
    return new TreeNode(a[mid], build(a, lo, mid - 1), build(a, mid + 1, hi));
}
```

To **rebalance** a degenerate BST: take its inorder (sorted) and rebuild with `build`. That's O(n), the idea behind scapegoat trees.

## 7. Iterators: inorder, paused

`std::set` iterators walk in sorted order with O(1) amortised `++`. Our version keeps a stack of the left spine still to visit:

```cpp
class BSTIterator {
public:
    explicit BSTIterator(TreeNode* root) { push_left(root); }
    bool hasNext() const { return !st.empty(); }
    int next() {
        TreeNode* n = st.back(); st.pop_back();
        push_left(n->right);            // the successor is the leftmost node of the right subtree
        return n->val;
    }
private:
    vector<TreeNode*> st;
    void push_left(TreeNode* n) { for (; n; n = n->left) st.push_back(n); }
};
```

Every node is pushed once and popped once over the whole iteration, so n calls cost O(n): **amortised O(1)** each, with O(h) memory. (Real `std::set` iterators use parent pointers instead of a stack, so they need O(1) memory.)

**Two-sum in a BST** then becomes the sorted-array two-pointer technique: a forward iterator from the smallest value and a mirrored backward iterator (push *right* spines) from the largest. Advance the forward one when the sum is too small and the backward one when it is too large, and stop when they reach the same node. That's O(n) time and O(h) memory.

## 8. Range queries and trimming: prune whole subtrees

If `n->val < lo`, the node and its entire left subtree are below the range. Only the right subtree matters:

```cpp
long long range_sum(TreeNode* n, int lo, int hi) {
    if (!n) return 0;
    if (n->val < lo) return range_sum(n->right, lo, hi);
    if (n->val > hi) return range_sum(n->left, lo, hi);
    return n->val + range_sum(n->left, lo, hi) + range_sum(n->right, lo, hi);
}
```

On a balanced tree this visits O(log n + k) nodes for k reported values. **Trimming** a BST to `[lo, hi]` uses the same case split: an out-of-range node is replaced by the trimmed version of its one useful subtree (and the removed nodes are freed), and an in-range node keeps itself and trims both children.

## 9. Repairing a BST with two swapped values

Swapping two values breaks the sorted inorder sequence in one place (if they were neighbours) or two places. Walk inorder with a `prev` pointer. At every descent `prev->val > cur->val`, set `first = prev` the first time, and set `second = cur` every time. Swap the two values at the end. With Morris traversal (see the traversals lesson) this needs O(1) extra memory.

```text
inorder 1 [6] 3 4 5 [2] 7      descents: 6>3 (first = 6) and 5>2 (second = 2)
inorder 1 [3 2] 4              one descent: 3>2 → first = 3, second = 2
```

## 10. Complexity summary

| Operation | Time | Notes |
|---|---|---|
| search, insert, delete, successor, predecessor | O(h) | h = O(log n) if balanced, O(n) worst case |
| validate, inorder, two-sum, trim | O(n) | one traversal |
| k-th smallest | O(h + k) | O(h) with subtree sizes |
| range sum | O(h + k) visited nodes on balanced trees | k = values in range |
| iterator `next()` | amortised O(1) | O(h) memory |
| sorted array → balanced BST | O(n) | |

## 11. Recognising the pattern

- "Sorted order", "k-th smallest", "closest value", "next larger": inorder or a guided walk.
- "Is it a valid BST?": bounds passed down, or a strictly increasing inorder.
- "Two values with sum k": two iterators from both ends.
- "Values in a range": prune subtrees outside the range.
- "Make it balanced": inorder plus build-from-middle.
- "Two values were swapped": descents in the inorder sequence.
- "LCA in a BST": walk from the root until p and q fall on different sides. That's O(h), no full traversal.

## 12. Common mistakes

1. **Validating only against the parent** instead of all ancestors.
2. **`INT_MIN`/`INT_MAX` as sentinels** while those values may appear in the tree.
3. **Two-children delete that "just removes" the node**, orphaning a subtree, or forgets to `delete` the successor.
4. **Forgetting that the root can change** (deleting the root, inserting into an empty tree): always return and reassign the root, or use a `TreeNode**`.
5. **Assuming O(log n)** for a plain BST: sorted input makes it O(n) per operation.
6. **Successor that requires `x` to be in the tree**, or treats equal values as candidates.
7. **Two-sum that pairs a node with itself** (`5 + 5` when only one 5 exists).
8. **Trimming without freeing** the removed subtrees: a leak.

## 13. Interview questions

**Q: What is the worst-case height of a BST with n nodes, and when does it happen?** n − 1, when the values are inserted in sorted (or reverse-sorted) order.

**Q: Why does the inorder successor of a node with two children have no left child?** It is the leftmost node of the right subtree. A left child would be smaller and further left.

**Q: How does `std::map` guarantee O(log n)?** It is a red-black tree: rotations and recolouring after each insert or erase keep the height at most about 2·log₂(n+1).

**Q: How do you find the k-th smallest element quickly if the tree changes often?** Augment every node with its subtree size, update the sizes on insert and delete, and descend by comparing k with the left size.

**Q: Can you validate a BST without recursion and in O(1) memory?** Yes: Morris inorder with a `prev` value.

## Check your understanding

1. Insert 50, 30, 70, 20, 40, 60, 80 into an empty BST. Draw it and give its height in edges.
2. In that tree, delete 50. Which value replaces it, and what does the tree look like?
3. What is the successor of 45 in that original tree, and the predecessor of 20?
4. Why does the `range_sum` function skip the left subtree when `n->val < lo`?
5. The inorder of a broken BST is `1 5 3 4 2 6`. Which two values were swapped?

<details>
<summary>Answers</summary>

1. 50 is the root with children 30 and 70; 30 has 20 and 40; 70 has 60 and 80. The height is 2.
2. The successor of 50 is 60 (leftmost of the right subtree). 60 moves into the root, and the old 60 leaf is removed: the root is 60 with children 30 (20, 40) and 70 (right child 80 only).
3. The successor of 45 is 50 (the walk records 50, goes left to 30, right to 40, right to null). 20 has no predecessor: nothing smaller exists.
4. Every value in the left subtree is smaller than `n->val`, which is already below `lo`, so none of them can be in the range.
5. The descents are 5 > 3 and 4 > 2, so first = 5 and second = 2. Swap 5 and 2 to get `1 2 3 4 5 6`.

</details>
