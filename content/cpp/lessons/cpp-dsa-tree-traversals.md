# Binary Trees and Their Traversals

Trees are everywhere in software: the file system, the HTML of every web page (the DOM), the syntax tree a compiler builds from your code, a robot's transform tree (`map → odom → base_link → camera`), a game engine's scene graph, `std::map` (a red-black tree), database indexes (B-trees), decision trees in ML. Almost every tree algorithm starts with the same question: **in what order do I visit the nodes?** This lesson answers it completely: the vocabulary, the three depth-first orders (recursive, with an explicit stack, and with O(1) memory), breadth-first level order and the classic variations interviewers love (zigzag, side views, width, vertical order, boundary).

You should be comfortable with recursion (see *Recursion from Zero*) and with pointers to structs (see the linked list lessons).

## 1. Vocabulary in one picture

```text
                 8          <- root (depth 0)            level 0
               /   \
              3     10      <- children of 8             level 1
             / \      \
            1   6      14   <- 6 is an internal node     level 2
               / \     /
              4   7   13    <- leaves (no children)      level 3
```

- A **binary tree** is either empty, or a **node** holding a value plus a **left** and a **right** subtree, each of which is again a binary tree. That recursive definition is why recursion fits trees so well.
- **Root:** the top node (8). **Parent / child:** 3 is the parent of 1 and 6. **Siblings:** 1 and 6.
- **Leaf:** a node with no children (1, 4, 7, 13). **Internal node:** a node with at least one child.
- **Depth** of a node: the number of edges from the root (depth of 6 is 2). **Level** *d* is the set of nodes with depth *d*.
- **Height** of a tree: the largest depth of any node (3 here). An empty tree has height −1 by the edge convention, or 0 if you count nodes. Always say which convention you use.
- **Subtree** of a node: the node plus all its descendants.
- A tree with *n* nodes has exactly *n − 1* edges (every node except the root has one parent edge).

Shapes you must be able to recognise:

| Shape | Meaning | Height for n nodes |
|---|---|---|
| full | every node has 0 or 2 children | anything |
| complete | all levels full except possibly the last, which fills from the left (a binary heap) | ⌊log₂ n⌋ |
| perfect | all internal nodes have 2 children and all leaves are at the same depth | log₂(n+1) − 1 |
| balanced | the heights of the two subtrees of every node differ by at most 1 | O(log n) |
| degenerate (a chain) | every node has at most one child | n − 1 |

The last row matters a lot in practice: a "tree" can be a chain of a million nodes (for example a BST built from sorted input). Any algorithm whose stack depth is the height then needs a million stack frames.

In C++ we will use this node type throughout the tree module:

```cpp
struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v, TreeNode* l = nullptr, TreeNode* r = nullptr) : val(v), left(l), right(r) {}
};
```

### How trees are written down in the problems

The problems use **level-order with null markers**, the same format LeetCode uses. You list the nodes level by level, left to right, writing `#` where a child is missing. Children are listed only for real nodes, and trailing `#` are dropped. The line starts with the number of tokens:

```text
5 1 2 3 # 4          means          1
                                   / \
                                  2   3
                                   \
                                    4
```

Read it like a queue: `1` is the root; the next two tokens (`2`, `3`) are 1's children; the next two (`#`, `4`) are 2's children; 3's children would come next but the list ended, so they are missing.

## 2. Depth-first traversals: pre, in, post

A depth-first traversal goes as deep as possible before backtracking. At each node, there are three jobs: visit the node itself (N), traverse the left subtree (L), traverse the right subtree (R). With left before right, the three possible positions for N give the three orders:

| Order | Sequence | For the tree in section 1 |
|---|---|---|
| preorder | N L R | 8 3 1 6 4 7 10 14 13 |
| inorder | L N R | 1 3 4 6 7 8 10 13 14 |
| postorder | L R N | 1 4 7 6 3 13 14 10 8 |

Notice the inorder sequence is **sorted**: that tree is a binary search tree, and inorder of a BST is always sorted. That fact powers the whole BST topic.

When to use which:

- **Preorder:** the parent is handled before its children. Use it to copy or serialize a tree, or to pass information **down** (depth, path so far).
- **Inorder:** sorted order of a BST, expression trees printed in infix.
- **Postorder:** the children are finished before the parent. Use it to compute something **up** from the children (height, size, subtree sums), to free a tree (delete the children before the parent), and to evaluate expression trees.

### 2.1 Recursive versions

```cpp
void preorder(TreeNode* n, vector<int>& out) {
    if (!n) return;              // empty tree: nothing to do
    out.push_back(n->val);       // N
    preorder(n->left, out);      // L
    preorder(n->right, out);     // R
}
void inorder(TreeNode* n, vector<int>& out) {
    if (!n) return;
    inorder(n->left, out);
    out.push_back(n->val);
    inorder(n->right, out);
}
void postorder(TreeNode* n, vector<int>& out) {
    if (!n) return;
    postorder(n->left, out);
    postorder(n->right, out);
    out.push_back(n->val);
}
```

The leap of faith from the recursion lesson applies directly: assume `inorder(n->left, out)` correctly appends the left subtree; then appending `n->val` and the right subtree finishes the job.

**Dry run, inorder on `5 1 2 3 # 4`:**

```text
in(1)
 ├─ in(2)
 │   ├─ in(null)            return
 │   ├─ push 2              out = [2]
 │   └─ in(4)
 │       ├─ in(null)        return
 │       ├─ push 4          out = [2 4]
 │       └─ in(null)        return
 ├─ push 1                  out = [2 4 1]
 └─ in(3)
     ├─ in(null)
     ├─ push 3              out = [2 4 1 3]
     └─ in(null)
```

**Complexity:** every node is entered once and every null child is entered once (there are n + 1 null children), so the time is O(n). The extra memory is the recursion depth, O(h): O(log n) for a balanced tree and O(n) for a chain.

**Why the output vector is passed by reference:** if each call returned its own vector and the caller concatenated them, a chain would copy 1 + 2 + … + n elements: O(n²).

### 2.2 Iterative versions with an explicit stack

Recursion uses the **call stack**, which is small (typically 8 MB). A chain of 10⁶ nodes needs 10⁶ frames and crashes with a segmentation fault. The fix is to keep the stack yourself, in a `std::vector` on the heap.

**Preorder** is the easiest. Pop a node, record it, then push its right child before its left child so that the left one is popped first:

```cpp
vector<int> preorder_iter(TreeNode* root) {
    vector<int> out; vector<TreeNode*> st;
    if (root) st.push_back(root);
    while (!st.empty()) {
        TreeNode* n = st.back(); st.pop_back();
        out.push_back(n->val);
        if (n->right) st.push_back(n->right);
        if (n->left) st.push_back(n->left);
    }
    return out;
}
```

**Inorder** follows the pattern "slide left, pop, step right":

```cpp
vector<int> inorder_iter(TreeNode* root) {
    vector<int> out; vector<TreeNode*> st;
    TreeNode* cur = root;
    while (cur || !st.empty()) {
        while (cur) { st.push_back(cur); cur = cur->left; }   // push the whole left spine
        cur = st.back(); st.pop_back();                       // deepest unfinished node
        out.push_back(cur->val);                              // its left side is done
        cur = cur->right;                                     // continue in its right subtree
    }
    return out;
}
```

Dry run on the section-1 tree (stack written bottom → top):

```text
push 8 3 1          stack [8 3 1]
pop 1, out 1        right of 1 is null
pop 3, out 3        cur = 6 → push 6 4      stack [8 6 4]
pop 4, out 4
pop 6, out 6        cur = 7 → push 7        stack [8 7]
pop 7, out 7
pop 8, out 8        cur = 10 → push 10      stack [10]
pop 10, out 10      cur = 14 → push 14 13   stack [14 13]
pop 13, pop 14      out: 1 3 4 6 7 8 10 13 14
```

**Postorder** is harder, because a node may only be recorded after both subtrees. Two standard solutions:

1. **Reverse trick:** a preorder that goes N R L (push left before right), reversed, is exactly L R N. Simple, but it stores everything before producing anything.
2. **Peek with a `last` pointer:** push the left spine, then look at the top without popping. If it has a right child that we did not just finish, go there; otherwise record it.

```cpp
vector<int> postorder_iter(TreeNode* root) {
    vector<int> out; vector<TreeNode*> st;
    TreeNode* cur = root; TreeNode* last = nullptr;
    while (cur || !st.empty()) {
        while (cur) { st.push_back(cur); cur = cur->left; }
        TreeNode* top = st.back();
        if (top->right && top->right != last) cur = top->right;   // right side still pending
        else { out.push_back(top->val); last = top; st.pop_back(); }
    }
    return out;
}
```

Each node is pushed and popped once: O(n) time and O(h) heap memory.

### 2.3 Morris traversal: O(1) extra memory

Can we traverse without any stack at all? The stack remembers "where to go back to after the left subtree". Morris's idea is to store that in the tree itself. The **inorder predecessor** of `cur` (the rightmost node of its left subtree) always has an unused `right` pointer. Point it at `cur` temporarily (a "thread"), and you can walk back up later.

```cpp
vector<int> morris_inorder(TreeNode* root) {
    vector<int> out;
    TreeNode* cur = root;
    while (cur) {
        if (!cur->left) { out.push_back(cur->val); cur = cur->right; continue; }
        TreeNode* pred = cur->left;
        while (pred->right && pred->right != cur) pred = pred->right;
        if (!pred->right) { pred->right = cur; cur = cur->left; }               // 1st visit: make thread
        else { pred->right = nullptr; out.push_back(cur->val); cur = cur->right; } // 2nd: remove it
    }
    return out;
}
```

```text
cur = 2 (left child 1):    1's right is null → thread 1 → 2, go to 1
          2                cur = 1: no left child → record 1, follow right (the thread) back to 2
         / \               cur = 2 again: pred 1 points to 2 → remove the thread, record 2, go right
        1   3              cur = 3: no left → record 3
```

Every thread is created once and removed once, and the predecessor searches walk each edge a constant number of times, so the time is still O(n). The tree is exactly restored at the end. For **Morris preorder**, record `cur` when the thread is created instead of when it is removed.

Morris is the answer to "traverse in O(1) space". It is rarely needed in production, and it **modifies the tree temporarily**, so it is unsafe if another thread reads the tree at the same time.

## 3. Breadth-first traversal: level order

BFS visits nodes level by level using a **queue** (first in, first out):

```cpp
vector<vector<int>> level_order(TreeNode* root) {
    vector<vector<int>> res;
    if (!root) return res;
    queue<TreeNode*> q; q.push(root);
    while (!q.empty()) {
        int width = q.size();                  // exactly the nodes of the current level
        vector<int>& level = res.emplace_back();
        for (int i = 0; i < width; ++i) {
            TreeNode* n = q.front(); q.pop();
            level.push_back(n->val);
            if (n->left) q.push(n->left);
            if (n->right) q.push(n->right);
        }
    }
    return res;
}
```

Dry run on the section-1 tree:

```text
queue [8]              width 1 → level [8]        queue [3 10]
queue [3 10]           width 2 → level [3 10]     queue [1 6 14]
queue [1 6 14]         width 3 → level [1 6 14]   queue [4 7 13]
queue [4 7 13]         width 3 → level [4 7 13]   queue []
```

The `width = q.size()` snapshot is the whole trick: at that moment the queue holds one complete level, and everything pushed during the round belongs to the next level. BFS needs O(w) memory where w is the widest level. That can be n/2 for a complete tree, but BFS never recurses, so chains are harmless.

### 3.1 Variations of level order

Once you have the levels, many classic questions are one line each:

- **Zigzag:** reverse every other level's values (don't reverse the order you push children, that scrambles the next level).
- **Right side view:** the last node of each level. **Left view:** the first. The right view can include nodes of the *left* subtree when the right side is shorter, so "follow right pointers" is wrong.
- **Level averages / sums / maximums:** fold each level.
- **Minimum depth:** the first level that contains a leaf. BFS can stop early, DFS cannot.
- **Maximum width (counting gaps):** give every node a heap index (root 0; children of i are 2i and 2i+1). The width of a level is last − first + 1. Indices double every level, so **re-base** them by subtracting the level's first index, or a chain of depth 100 overflows 64 bits.

### 3.2 Coordinates: vertical order

Put the root at row 0, column 0; the left child moves to column − 1, the right child to column + 1. **Vertical order** lists the columns from left to right. When two nodes share a column, order them by row; nodes in the same row and column are ordered by value (LeetCode 987). The clean solution labels every node with `(column, row, value)`, sorts the triples, and cuts the sorted list into columns. That's O(n log n). Variants: **top view** (the first node of each column by row) and **bottom view** (the last).

```text
           3            col −2: 4    col −1: 9    col 0: 3 0 1    col 1: 8    col 2: 7
         /   \
        9     8         0 and 1 are both at (row 2, col 0): the smaller value comes first
       / \   / \
      4   1 0   7
```

### 3.3 Boundary traversal

The anticlockwise boundary is **root + left boundary (no leaves) + all leaves left to right + right boundary reversed (no leaves)**. Build the four parts separately. The boundary walks stop before leaves, so no node appears twice. If the root has no left child, the left boundary is empty: it does *not* switch to the right side.

## 4. Complexity summary and proof ideas

| Method | Time | Extra memory | Deep chains (10⁶)? |
|---|---|---|---|
| recursive DFS | O(n) | O(h) call stack | crashes on an 8 MB stack |
| iterative DFS | O(n) | O(h) heap | fine |
| Morris | O(n) | O(1) | fine (modifies the tree temporarily) |
| BFS | O(n) | O(w) queue | fine |

Proof idea for O(n): every traversal does O(1) work per node plus O(1) per edge, and a tree has n nodes and n − 1 edges. For Morris, the extra predecessor walks traverse each edge at most twice more (once to create a thread, once to find it again).

## 5. Recognising the pattern

- "Process children before the parent" (sizes, heights, freeing, evaluating): **postorder**.
- "Pass something down from the root" (depth, path, running maximum): **preorder** (or DFS with parameters).
- "Sorted order" in a BST, or "k-th smallest": **inorder**.
- "Level", "depth by depth", "nearest", "minimum depth", "view", "width": **BFS**.
- "Column", "vertical", "top/bottom view": coordinates plus BFS or sorting.
- "O(1) extra space": **Morris**.
- "The tree can be 10⁶ deep" or "no recursion": an **explicit stack** or BFS.

## 6. Common mistakes

1. **Forgetting the base case** `if (!n) return;`: dereferencing null crashes immediately.
2. **Returning vectors by value at every level and concatenating them:** O(n²) on chains.
3. **Recursing on a degenerate tree** in production code: a stack overflow is a crash, not an exception you can catch.
4. **Zigzag by reversing the order children are pushed:** it scrambles the order of the next level. Reverse the values instead.
5. **Right view = follow right pointers:** wrong whenever the left side is deeper.
6. **Width without re-basing indices:** silent overflow after 63 levels.
7. **Vertical order relying only on BFS order:** it breaks the same-cell tie rule.
8. **Boundary traversal counting a leaf twice** (once as boundary, once as leaf), or listing a lone root twice.
9. **Morris traversal that returns early** (for example "stop at the k-th element") without removing the remaining threads: the tree stays corrupted.

## 7. Interview questions

**Q: Can you reconstruct a tree from its preorder traversal alone?** No. `[1, 2]` could be 2 as the left child or as the right child of 1. You need two traversals, one of which is inorder (next lesson), or a traversal with null markers.

**Q: Which traversal deletes a tree safely?** Postorder: both children are freed before their parent. Iteratively, any order works if you push a node's children before deleting it.

**Q: What is the space complexity of recursive inorder?** O(h), which is between O(log n) and O(n). Not O(1): the stack frames count.

**Q: BFS or DFS for "minimum depth"?** BFS, because it can stop at the first leaf. DFS must explore everything.

**Q: Why is Morris traversal O(n) and not O(n log n) or O(n²)?** Each edge is walked a bounded number of times: the predecessor walks for different nodes cover disjoint right spines.

**Q: How much memory does BFS need on a complete tree of n nodes?** About n/2 for the last level. DFS needs only O(log n) there. On a chain it is the opposite: BFS needs O(1) and DFS O(n).

## Check your understanding

1. Write the preorder, inorder and postorder of the tree `6 7 5 9 # 6 8`. Draw it first, reading the tokens like a queue.
2. A tree has preorder `A B D E C` and inorder `D B E A C`. What is its postorder?
3. Why does iterative preorder push the right child before the left?
4. What does the stack contain, at any moment of iterative inorder?
5. Give a tree where the right view contains a node of the root's left subtree.
6. In max-width, why is subtracting the level's first index enough to avoid overflow?

<details>
<summary>Answers</summary>

1. The tree is 7 with children 5 and 9; 6 is the right child of 5; 8 is the left child of 9. Preorder `7 5 6 9 8`, inorder `5 6 7 8 9`, postorder `6 5 8 9 7`.
2. The root is A (first in preorder). In inorder, `D B E` is left of A and `C` is right. The left part's preorder is `B D E`, so B is its root with D left and E right. Postorder: `D E B C A`.
3. A stack is last-in-first-out: the child pushed last is processed first, and preorder must handle the left subtree first.
4. The ancestors of the current position whose node has not been recorded yet: exactly what the recursive version keeps in its pending call frames.
5. `1` with left child `2` and right child `3`, where 2 has a child `4` (either side). Levels are [1], [2 3], [4]. The right view is `1 3 4`, and 4 is in the left subtree.
6. After re-basing, a level's indices lie in [0, width). The children's indices are at most 2·width, so all values stay below twice the answer, which is guaranteed to fit.

</details>
