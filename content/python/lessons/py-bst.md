# Binary Search Trees

A **binary search tree (BST)** keeps keys ordered. For every node, all keys in its left subtree are smaller and all keys in its right subtree are larger. That one invariant makes search, insertion, deletion, minimum/maximum, predecessor/successor and range queries all **O(h)**, where h is the height. That's O(log n) if the tree stays balanced, and O(n) if it degenerates. BSTs (in their self-balancing forms) power ordered maps: C++ `std::map`, Java `TreeMap`, database indexes (B-trees), and interval and k-d trees in robotics for spatial queries.

## 1. The invariant and search

```python
class Node:
    __slots__ = ("key", "left", "right")
    def __init__(self, key):
        self.key, self.left, self.right = key, None, None

def search(root, key):
    while root and root.key != key:
        root = root.left if key < root.key else root.right
    return root
```

> [!KEY]
> The invariant is about **whole subtrees**, not just immediate children. A tree where every node is greater than its left child and smaller than its right child can still be invalid. In `5 → left 3 → right 7`, the node 7 is in 5's left subtree but larger than 5. Validate by passing down bounds:

```python
def is_valid_bst(n, lo=float("-inf"), hi=float("inf")):
    if n is None:
        return True
    if not (lo < n.key < hi):
        return False
    return is_valid_bst(n.left, lo, n.key) and is_valid_bst(n.right, n.key, hi)
```

Equivalent check: the inorder traversal is strictly increasing.

## 2. Insertion

```python
def insert(root, key):
    if root is None:
        return Node(key)
    cur = root
    while True:
        if key < cur.key:
            if cur.left is None: cur.left = Node(key); break
            cur = cur.left
        elif key > cur.key:
            if cur.right is None: cur.right = Node(key); break
            cur = cur.right
        else:
            break                          # duplicate: ignore (or keep a count)
    return root
```

Insertion order determines the shape. Inserting sorted keys produces a **chain** of height n − 1, so every operation becomes O(n). That's why production trees self-balance.

## 3. Deletion: three cases

```python
def delete(root, key):
    if root is None:
        return None
    if key < root.key:
        root.left = delete(root.left, key)
    elif key > root.key:
        root.right = delete(root.right, key)
    else:
        if root.left is None:              # cases 1 and 2: zero or one child: splice out
            return root.right
        if root.right is None:
            return root.left
        succ = root.right                  # case 3: two children: replace with the inorder successor
        while succ.left:
            succ = succ.left
        root.key = succ.key
        root.right = delete(root.right, succ.key)
    return root
```

The successor (the minimum of the right subtree) has no left child, so deleting it falls into case 1 or 2.

## 4. Ordered queries

| Query | Method | Cost |
|---|---|---|
| min / max | go left/right to the end | O(h) |
| floor (largest ≤ x) | track the last node where you went right | O(h) |
| ceiling (smallest ≥ x) | track the last node where you went left | O(h) |
| successor of a node | the min of the right subtree, else the nearest ancestor of which it's in the left subtree | O(h) |
| range [lo, hi] | inorder, pruning subtrees outside the range | O(h + k) |
| k-th smallest | inorder with a counter, or O(h) with subtree sizes | |
| rank of x | O(h) with subtree sizes | |

```python
def floor(root, x):
    best = None
    while root:
        if root.key == x: return x
        if root.key < x:
            best = root.key                # a candidate; try for a larger one on the right
            root = root.right
        else:
            root = root.left
    return best

def range_keys(n, lo, hi, out):
    if n is None: return
    if lo < n.key: range_keys(n.left, lo, hi, out)       # the left subtree may contain keys >= lo
    if lo <= n.key <= hi: out.append(n.key)
    if n.key < hi: range_keys(n.right, lo, hi, out)
```

**Order-statistic tree**: store `size` (the number of nodes in the subtree) in every node. Then the k-th smallest is found by comparing k with `size(left) + 1` at each step, in O(h).

## 5. Balanced BSTs

| Tree | Balance rule | Height guarantee | Used in |
|---|---|---|---|
| AVL | subtree heights differ by ≤ 1, fixed by rotations | ≤ 1.44 log₂ n | lookup-heavy workloads |
| Red–black | colouring rules; no red-red, equal black heights | ≤ 2 log₂(n + 1) | `std::map`, Java `TreeMap`, the Linux kernel |
| Treap | BST by key + heap by random priority | expected O(log n) | simple to implement |
| Splay | move the accessed node to the root | amortised O(log n) | caches |
| B-tree / B+ tree | many keys per node, all leaves at the same depth | log_B n | databases, filesystems (disk-friendly) |

All balance using **rotations**, O(1) pointer rewirings that preserve inorder order:

```python
def rotate_right(y):
    x = y.left
    y.left = x.right       # x's right subtree (keys between x and y) moves under y
    x.right = y
    return x               # x is the new subtree root
```

## 6. Ordered sets in Python

Python has no built-in balanced BST. The options are:
- **`bisect` on a sorted list**: O(log n) search but O(n) insert. Fine up to about 10⁵ inserts.
- **`sortedcontainers.SortedList` / `SortedDict`** (third party, pure Python, very fast): O(log n) insert, delete and index, with `bisect_left` and `irange`.
- **`heapq`** if you only need the minimum.

## 7. Exam-ready answers

> [!EXAM]
> **Binary search trees.** A binary search tree is a binary tree in which every key in a node's left subtree is less than the node's key and every key in its right subtree is greater. Search, insertion and deletion follow a single root-to-leaf path, taking O(h) time for height h, and inorder traversal visits the keys in sorted order. Deletion of a node with two children replaces it by its inorder successor or predecessor. Because insertion order determines the height, which ranges from about log₂ n to n − 1, self-balancing variants such as AVL and red–black trees use rotations to keep the height O(log n), guaranteeing logarithmic operations.

## 8. Cheat sheet

| Need | Approach |
|---|---|
| validate | bounds passed down, or a strictly increasing inorder |
| delete with 2 children | copy the successor, delete the successor |
| floor / ceiling | track the candidate while descending |
| k-th smallest | inorder counter, or subtree sizes |
| LCA in a BST | descend until p and q split: `p < node < q` |
| sorted array → BST | middle element as root, recurse (height-balanced) |
| ordered set in Python | `sortedcontainers.SortedList` |

> [!INTERVIEW]
> **"Lowest common ancestor in a BST?"** Use the ordering, without searching both sides. From the root, if both p and q are smaller, go left; if both are larger, go right; otherwise the current node is where they split, so it's the LCA. That's O(h) time and O(1) space iteratively, compared with the general binary-tree LCA that must explore both subtrees.
