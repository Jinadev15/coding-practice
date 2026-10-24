---
id: py-tree-workshop
title: "Tree Workshop: Max Path Sum, Path Counting, Codec, Right View"
difficulty: Hard
order: 1
tags: binary trees, postorder, prefix sums on trees, serialization, BFS
---
## Statement
`TreeNode` (with `val`, `left`, `right`) is provided by the judge. Trees are given in test lines as level-order lists with `None` for missing children (LeetCode style).

```python
def max_path_sum(root):
    """Maximum sum of any non-empty path (a sequence of nodes connected by edges, no node repeated).
    The path need not pass through the root. Values may be negative."""

def count_paths(root, target):
    """Number of DOWNWARD paths (parent -> child direction, any start and end) whose values sum to target. O(n)."""

def right_view(root):
    """Values visible from the right: the last node of each level, top to bottom."""

def serialize(root):
    """Encode the tree as a string."""

def deserialize(data):
    """Rebuild the tree from serialize's output. The judge checks deserialize(serialize(t)) == t."""
```

Trees have up to 100 000 nodes (the judge raises the recursion limit to 20 000).

## Starter
```python
def max_path_sum(root):
    return root.val if root else 0

def count_paths(root, target):
    return 0

def right_view(root):
    return []

def serialize(root):
    return ""

def deserialize(data):
    return None
```

## Driver
```python
import ast
import random
import sys
from collections import deque

sys.setrecursionlimit(20000)

class TreeNode:
    __slots__ = ("val", "left", "right")
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def build(vals):
    if not vals or vals[0] is None:
        return None
    it = iter(vals)
    root = TreeNode(next(it))
    q = deque([root])
    while q:
        node = q.popleft()
        for side in ("left", "right"):
            v = next(it, None)
            if v is not None:
                child = TreeNode(v)
                setattr(node, side, child)
                q.append(child)
    return root

def same(a, b):
    st = [(a, b)]
    while st:
        x, y = st.pop()
        if x is None or y is None:
            if x is not y:
                return False
            continue
        if x.val != y.val:
            return False
        st.append((x.left, y.left)); st.append((x.right, y.right))
    return True

def random_tree(rng, n, deep):
    nodes = [TreeNode(rng.randrange(-50, 60))]
    for i in range(1, n):
        if deep and i % 2:
            parent = nodes[-1]
        else:
            parent = nodes[rng.randrange(len(nodes))]
        side = "left" if rng.random() < 0.5 else "right"
        if getattr(parent, side) is None:
            child = TreeNode(rng.randrange(-50, 60))
            setattr(parent, side, child)
            nodes.append(child)
    return nodes[0]

for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        t = random_tree(rng, n, deep=(name == "deep"))
        rv = right_view(t)
        s = serialize(t)
        print(name, n, max_path_sum(t), count_paths(t, 7), len(rv), sum(rv), same(deserialize(s), t))
        continue
    name, args = ast.literal_eval(line)
    t = build(args[0])
    if name == "max_path_sum":
        print(name, "->", max_path_sum(t))
    elif name == "count_paths":
        print(name, "->", count_paths(t, args[1]))
    elif name == "right_view":
        print(name, "->", right_view(t))
    else:
        s = serialize(t)
        print(name, "-> roundtrip", same(deserialize(s), t), "is_str", isinstance(s, str))
```

## Tests
=== sample
("max_path_sum", ([-10, 9, 20, None, None, 15, 7],))
("count_paths", ([10, 5, -3, 3, 2, None, 11, 3, -2, None, 1], 8))
("right_view", ([1, 2, 3, None, 5, None, 4],))
("codec", ([1, 2, 3, None, None, 4, 5],))
---
max_path_sum -> 42
count_paths -> 3
right_view -> [1, 3, 4]
codec -> roundtrip True is_str True
=== hidden
("max_path_sum", ([-3],))
("max_path_sum", ([-2, -1],))
("max_path_sum", ([2, -1, -2],))
("max_path_sum", ([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1],))
("count_paths", ([], 0))
("count_paths", ([0, 0, 0], 0))
("count_paths", ([1, -1, 1, None, 1], 1))
("right_view", ([],))
("right_view", ([1, 2],))
("codec", ([],))
("codec", ([-5],))
("codec", ([1, None, 2, None, 3, None, 4],))
---
max_path_sum -> -3
max_path_sum -> -1
max_path_sum -> 2
max_path_sum -> 48
count_paths -> 0
count_paths -> 5
count_paths -> 4
right_view -> []
right_view -> [1, 2]
codec -> roundtrip True is_str True
codec -> roundtrip True is_str True
codec -> roundtrip True is_str True
=== hidden
gen wide 1 100000
gen deep 2 6000
---
wide 100000 1234 4297 38 233 True
deep 6000 1085 406 47 249 True

## Hints
- **max_path_sum**: `gain(n)` returns the best downward path starting at n, which is `n.val + max(0, gain(left), gain(right))`. At each node, update the global best with `n.val + max(0, gl) + max(0, gr)`.
- **count_paths**: DFS carrying the running prefix sum and a dict of prefix counts on the current root-to-node path (start with `{0: 1}`). Add `counts[prefix - target]`, recurse, then decrement the current prefix's count when leaving (backtrack).
- **right_view**: BFS level by level, recording the last node of each level.
- **codec**: preorder with a marker for `None` (`"#"`), comma separated. Deserialise with an iterator over the tokens. A recursive codec is fine here at depth 3000; an iterative one is safer.

## Solution
```python
from collections import deque, defaultdict

def max_path_sum(root):
    best = float("-inf")
    def gain(n):
        nonlocal best
        if n is None:
            return 0
        gl = max(0, gain(n.left))
        gr = max(0, gain(n.right))
        best = max(best, n.val + gl + gr)       # the path bending at n
        return n.val + max(gl, gr)               # the path continuing up to the parent
    gain(root)
    return best

def count_paths(root, target):
    counts = defaultdict(int)
    counts[0] = 1
    total = 0
    def dfs(n, prefix):
        nonlocal total
        if n is None:
            return
        prefix += n.val
        total += counts[prefix - target]
        counts[prefix] += 1
        dfs(n.left, prefix)
        dfs(n.right, prefix)
        counts[prefix] -= 1                      # backtrack: leave the current path
    dfs(root, 0)
    return total

def right_view(root):
    if not root:
        return []
    out, q = [], deque([root])
    while q:
        for i in range(len(q)):
            n = q.popleft()
            if n.left: q.append(n.left)
            if n.right: q.append(n.right)
        out.append(n.val)                         # the last node of the level
    return out

def serialize(root):
    out, st = [], [root]
    while st:                                     # iterative preorder with null markers
        n = st.pop()
        if n is None:
            out.append("#")
            continue
        out.append(str(n.val))
        st.append(n.right)
        st.append(n.left)
    return ",".join(out)

def deserialize(data):
    tokens = iter(data.split(","))
    first = next(tokens)
    if first == "#":
        return None
    root = TreeNode(int(first))
    st = [(root, 0)]                              # (node, children filled so far)
    for tok in tokens:
        while st and st[-1][1] == 2:
            st.pop()
        parent, filled = st.pop()
        child = None if tok == "#" else TreeNode(int(tok))
        if filled == 0:
            parent.left = child
        else:
            parent.right = child
        st.append((parent, filled + 1))
        if child:
            st.append((child, 0))
    return root
```

- **max_path_sum** separates what is *returned* (the best downward path, which a parent can extend) from what is *recorded* (the best path bending at a node). Negative gains are clipped to 0, which means "don't take that branch".
- **count_paths** is the array trick "subarray sum = k via prefix sums" moved onto a tree. The dict holds only the prefixes on the current root-to-node path, and backtracking removes them on the way out. That's O(n) instead of O(n·h).
- **The codec** is preorder with null markers, which makes the encoding unambiguous. Both directions are iterative, so very deep trees can't hit the recursion limit.
