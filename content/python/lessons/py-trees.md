# Binary Trees and Traversals

A **tree** is a connected acyclic graph with a designated root. Every node except the root has exactly one parent. In a **binary tree**, each node has at most two children: left and right. Trees model hierarchies (file systems, scene graphs, robot kinematic chains in URDF, ASTs in compilers, decision trees) and underpin search structures (BSTs, heaps, tries, segment trees). Almost every tree problem is solved by choosing the right **traversal** and deciding what each recursive call returns.

## 1. Vocabulary

| Term | Meaning |
|---|---|
| depth of a node | number of edges from the root |
| height of a tree | the maximum depth (an empty tree has height −1, a single node 0; some texts count nodes instead) |
| leaf | node with no children |
| full binary tree | every node has 0 or 2 children |
| complete | all levels full except possibly the last, which is filled from the left (heap shape) |
| perfect | all internal nodes have 2 children, all leaves at the same depth: 2^(h+1) − 1 nodes |
| balanced | the heights of the subtrees differ by at most 1 everywhere (AVL definition) |

A binary tree with n nodes has height between ⌊log₂ n⌋ (complete) and n − 1 (a degenerate "linked list").

## 2. Representation

```python
class TreeNode:
    __slots__ = ("val", "left", "right")
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def build_level_order(vals):
    """[1, 2, 3, None, 4] → tree (LeetCode-style; None marks a missing child)."""
    if not vals or vals[0] is None:
        return None
    it = iter(vals)
    root = TreeNode(next(it))
    q = [root]
    for node in q:                          # q grows while we iterate: BFS order
        for side in ("left", "right"):
            v = next(it, None)
            if v is not None:
                child = TreeNode(v)
                setattr(node, side, child)
                q.append(child)
    return root
```

## 3. Depth-first traversals

```python
def preorder(n):   return [n.val] + preorder(n.left) + preorder(n.right) if n else []   # root, L, R
def inorder(n):    return inorder(n.left) + [n.val] + inorder(n.right) if n else []     # L, root, R
def postorder(n):  return postorder(n.left) + postorder(n.right) + [n.val] if n else [] # L, R, root
```

(These list-concatenating one-liners are O(n²) in the worst case. Real code appends to one shared list or yields.)

| Order | Typical use |
|---|---|
| preorder | copy/serialise a tree, print a hierarchy, prefix expressions |
| inorder | **sorted order of a BST**, infix expressions |
| postorder | delete/free a tree, evaluate an expression tree, compute subtree sizes and heights (children first) |
| level order (BFS) | shortest depth, per-level aggregates, right-side view |

### Iterative inorder (an explicit stack)

```python
def inorder_iter(root):
    out, st, cur = [], [], root
    while cur or st:
        while cur:                 # go left as far as possible
            st.append(cur)
            cur = cur.left
        cur = st.pop()
        out.append(cur.val)
        cur = cur.right
    return out
```

Use an explicit stack when the tree may be deep (degenerate trees with 10⁵ nodes exceed Python's recursion limit). **Morris traversal** does inorder in O(1) extra space by temporarily threading right pointers. It's elegant but rarely needed.

## 4. Level order (BFS)

```python
from collections import deque

def level_order(root):
    if not root:
        return []
    out, q = [], deque([root])
    while q:
        level = []
        for _ in range(len(q)):
            n = q.popleft()
            level.append(n.val)
            if n.left: q.append(n.left)
            if n.right: q.append(n.right)
        out.append(level)
    return out
```

Variants include zigzag order (reverse alternate levels), right-side view (the last node of each level), the minimum depth (the first leaf reached), and level averages.

## 5. The recursive mindset: what does a call return?

Most tree problems are solved by a function that returns information **about the subtree**, combining the children's answers:

```python
def height(n):
    return -1 if n is None else 1 + max(height(n.left), height(n.right))

def diameter(root):
    """Longest path (in edges) between any two nodes; it may not pass through the root."""
    best = 0
    def h(n):                               # returns the height in nodes, updates best as a side effect
        nonlocal best
        if not n:
            return 0
        l, r = h(n.left), h(n.right)
        best = max(best, l + r)             # the path that bends at n
        return 1 + max(l, r)
    h(root)
    return best

def is_balanced(root):
    def check(n):                           # height, or -1 meaning "unbalanced": an early-exit sentinel
        if not n:
            return 0
        l = check(n.left)
        if l < 0: return -1
        r = check(n.right)
        if r < 0 or abs(l - r) > 1: return -1
        return 1 + max(l, r)
    return check(root) >= 0
```

> [!KEY]
> The pattern behind diameter, maximum path sum and "longest univalue path": the function **returns** the best path that goes *down* from a node (so the parent can extend it) and **records** the best path that *bends* at the node (left + node + right) in an outer variable. Separating "what I return to my parent" from "the global answer" is the crux of these problems.

### Lowest common ancestor (general binary tree)

```python
def lca(root, p, q):
    if root is None or root is p or root is q:
        return root
    left, right = lca(root.left, p, q), lca(root.right, p, q)
    if left and right:
        return root                         # p and q are on different sides
    return left or right
```

### Paths with a target sum: prefix sums on a tree

Counting downward paths summing to k uses the same `{prefix: count}` dict as for arrays. Add the current prefix when entering a node and remove it when leaving (backtracking), which gives O(n).

## 6. Serialisation and reconstruction

- Preorder **with null markers** uniquely determines a tree: `"1,2,#,#,3,4,#,#,#"`. Deserialise by consuming tokens recursively.
- **Preorder + inorder** (distinct values) reconstruct a tree: the preorder head is the root, and its position in the inorder sequence splits the left and right subtrees. With an index dict, that's O(n).
- Inorder alone does **not** determine a tree.

## 7. Exam-ready answers

> [!EXAM]
> **Tree traversals.** A binary tree can be traversed depth-first in preorder (node, left subtree, right subtree), inorder (left, node, right) or postorder (left, right, node), or breadth-first in level order using a queue. Each visits every node once in O(n) time, using O(h) space for the recursion or stack in depth-first orders, where h is the tree's height, and O(w) for the queue in level order, where w is the maximum width. Inorder traversal of a binary search tree yields its keys in sorted order; postorder suits computations that need the children's results first, such as heights or freeing memory.

## 8. Cheat sheet

| Problem | Approach |
|---|---|
| height / balanced / diameter | postorder, return the height |
| max path sum | return the best downward path, record the bending path |
| level aggregates, min depth | BFS with `for _ in range(len(q))` |
| BST sorted output | inorder |
| LCA | return a found node from each side |
| serialise | preorder with null markers |
| deep trees | iterative with an explicit stack |

> [!INTERVIEW]
> **"What's the space complexity of recursive DFS on a tree?"** O(h), the recursion depth. That's O(log n) for a balanced tree but O(n) for a degenerate one, and in Python a degenerate tree with more than about 1000 nodes hits `RecursionError`. Mention `sys.setrecursionlimit` with caution (the C stack can still overflow), or convert to an explicit stack.
