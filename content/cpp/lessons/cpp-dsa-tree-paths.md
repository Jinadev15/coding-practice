# Paths, Heights and Tree DP

Most tree interview questions are secretly the same question: **what should a recursive function return, and what should it pass down?** Height, diameter, balance, maximum path sum, root-to-leaf sums, lowest common ancestor, "good nodes", the robber on a tree: each is one DFS with the right parameters and the right return value. This lesson teaches that design skill directly, with two patterns (**top-down** and **bottom-up**) and their combination, **tree dynamic programming**.

Real systems use exactly these computations. A file system computes directory sizes bottom-up. A robot's kinematic chain accumulates transforms top-down from the base. A network's diameter bounds broadcast latency. Phylogenetic software finds the lowest common ancestor of two species.

You need traversals (previous lessons) and recursion. The node type is the usual `TreeNode { int val; TreeNode *left, *right; }`.

## 1. Two directions of information flow

```text
           TOP-DOWN (parameters)                 BOTTOM-UP (return values)

                 root                                     root
           depth=0, max=3                          returns f(left), f(right) combined
              /        \                                /        \
     depth=1, max=3   depth=1, max=4          returns height   returns height
          ...             ...                   (from below)     (from below)
```

- **Top-down:** the parent knows something the child needs, like its depth, the sum so far, the maximum on the path or the remaining target. Pass it as a **parameter**. This is preorder-shaped: use the information at the node, then hand it on.
- **Bottom-up:** the parent needs a summary of each child's subtree: height, size, best sum, "is it balanced?". **Return** it. This is postorder-shaped: the children finish before the parent combines.

Many problems use both. The rule of thumb: write down, in one sentence, *exactly* what the function returns for a subtree, and *exactly* what each parameter means. Most bugs come from a vague definition.

## 2. Height and depth (bottom-up, then top-down)

The **height** of a subtree (counting nodes, empty = 0) is a pure bottom-up computation:

```cpp
int height(TreeNode* n) {
    if (!n) return 0;
    return 1 + max(height(n->left), height(n->right));
}
```

**Depth** is the top-down mirror: pass `d` down, and a node at parameter `d` has depth `d`.

**Minimum depth** (the nearest **leaf**) has a trap: a node with one child is not a leaf, so its missing side must not win the `min`.

```cpp
int min_depth(TreeNode* n) {
    if (!n) return 0;
    if (!n->left) return 1 + min_depth(n->right);
    if (!n->right) return 1 + min_depth(n->left);
    return 1 + min(min_depth(n->left), min_depth(n->right));
}
```

## 3. "Return one thing, record another": diameter and balance

The **diameter** is the number of edges on the longest path between any two nodes. That path has a highest node, the node where it bends. If it bends at `n`, its length is `height(n->left) + height(n->right)` (heights in nodes, which equals edges down from `n`). Calling `height` separately at every node costs O(n²) on a chain. Instead, compute heights once and **record** the best bend on the way:

```cpp
int height_and_diameter(TreeNode* n, int& best) {
    if (!n) return 0;
    int l = height_and_diameter(n->left, best);
    int r = height_and_diameter(n->right, best);
    best = max(best, l + r);          // the longest path bending at n
    return 1 + max(l, r);             // what the parent needs: my height
}
```

**Dry run** on the tree below:

```text
        1
       / \
      2   3
     / \
    4   5
```

| node (postorder) | l | r | best after | returns |
|---|---|---|---|---|
| 4 | 0 | 0 | 0 | 1 |
| 5 | 0 | 0 | 0 | 1 |
| 2 | 1 | 1 | 2 | 2 |
| 3 | 0 | 0 | 2 | 1 |
| 1 | 2 | 1 | 3 | 3 |

The diameter is 3 (4 → 2 → 1 → 3).

**Balanced** (every node's subtree heights differ by at most 1) uses the same skeleton with a sentinel: return −1 for "unbalanced below", and check it right after each call so that the failure propagates without extra work.

```cpp
int balanced_height(TreeNode* n) {
    if (!n) return 0;
    int l = balanced_height(n->left);  if (l < 0) return -1;
    int r = balanced_height(n->right); if (r < 0 || abs(l - r) > 1) return -1;
    return 1 + max(l, r);
}
```

## 4. Top-down with state: good nodes and root-to-leaf paths

A node is **good** if nothing above it on its path is larger. Pass the path maximum down:

```cpp
int good(TreeNode* n, long long best) {
    if (!n) return 0;
    long long nb = max(best, (long long)n->val);
    return (n->val >= best) + good(n->left, nb) + good(n->right, nb);
}
// good(root, LLONG_MIN)
```

**Root-to-leaf path sums** pass the remaining target down. To *list* the paths, use **backtracking**: one shared `path` vector, push on entry, pop on exit, copy at a matching leaf.

```cpp
void paths(TreeNode* n, long long rem, vector<int>& path, vector<vector<int>>& out) {
    if (!n) return;
    path.push_back(n->val);
    rem -= n->val;
    if (!n->left && !n->right) { if (rem == 0) out.push_back(path); }
    else { paths(n->left, rem, path, out); paths(n->right, rem, path, out); }
    path.pop_back();                   // undo before returning to the parent
}
```

Two classic bugs: checking the sum at a node that is not a leaf, and stopping as soon as the running sum hits the target (negative values can bring it back later).

## 5. Prefix sums on a tree: paths that start anywhere

"Count downward paths with sum `k`" allows any start and any end. On an array, "subarrays with sum k" is solved with prefix sums and a hash map. A root-to-node path in a tree *is* an array, so the same trick works if the map holds only the prefixes of the **current path**:

```cpp
long long count_from(TreeNode* n, long long sum, long long k, unordered_map<long long, int>& seen) {
    if (!n) return 0;
    sum += n->val;
    long long res = seen.count(sum - k) ? seen[sum - k] : 0;   // paths ending at n
    ++seen[sum];
    res += count_from(n->left, sum, k, seen) + count_from(n->right, sum, k, seen);
    --seen[sum];                                                // n leaves the path
    return res;
}
// seen = {{0, 1}}; count_from(root, 0, k, seen)
```

The `--seen[sum]` is the backtracking step: a sibling subtree must not see prefixes from this branch. That's O(n) instead of O(n·h).

## 6. Lowest common ancestor

The **LCA** of `p` and `q` is the deepest node with both in its subtree (a node is its own descendant). Define the recursion's return value carefully: *"the LCA if both are below me, the one I found if only one is, null if neither."*

```cpp
TreeNode* lca(TreeNode* n, int p, int q) {
    if (!n || n->val == p || n->val == q) return n;
    TreeNode* l = lca(n->left, p, q);
    TreeNode* r = lca(n->right, p, q);
    if (l && r) return n;             // one on each side: n is where their paths split
    return l ? l : r;
}
```

This version assumes both values exist. If one may be missing, the function returns the other one as a false answer, so verify both first. The **distance** between two nodes is `depth(p) + depth(q) − 2·depth(lca)`: every path goes up to the LCA and down again. For many queries, preprocess with binary lifting (O(log n) per query), which is covered later in the course.

## 7. Tree DP: several numbers per node

Sometimes one return value is not enough for the parent to decide. The **robber on a tree** chooses nodes with no parent–child pair both chosen, maximising the sum. The parent must know whether the child was taken, so each node returns **two** values:

```cpp
pair<long long, long long> rob(TreeNode* n) {          // {best if n taken, best if n skipped}
    if (!n) return {0, 0};
    auto [lt, ls] = rob(n->left);
    auto [rt, rs] = rob(n->right);
    return {n->val + ls + rs, max(lt, ls) + max(rt, rs)};
}
```

Dry run on `3 4 5 1 3 # 1` (3 with children 4 and 5; 4 has children 1 and 3; 5 has right child 1):

| node | take | skip |
|---|---|---|
| 1 (under 4) | 1 | 0 |
| 3 (under 4) | 3 | 0 |
| 4 | 4 + 0 + 0 = 4 | 1 + 3 = 4 |
| 1 (under 5) | 1 | 0 |
| 5 | 5 + 0 = 5 | 1 |
| 3 (root) | 3 + 4 + 1 = 8 | 4 + 5 = 9 |

The answer is max(8, 9) = 9: take 4 and 5.

This is the general recipe of tree DP: **define a state per node** (often "with / without this node", or "covered / not covered"), express it through the children's states, and compute everything in one postorder pass. Naive recursion over "children or grandchildren" recomputes subtrees and becomes exponential.

### 7.1 The hardest classic: maximum path sum

Paths may start and end anywhere, and values may be negative. Combine sections 3 and 7:

```cpp
long long gain(TreeNode* n, long long& best) {
    if (!n) return 0;
    long long l = max(0LL, gain(n->left, best));    // drop negative branches
    long long r = max(0LL, gain(n->right, best));
    best = max(best, n->val + l + r);               // path bending at n: may use both sides
    return n->val + max(l, r);                      // path continuing to the parent: one side only
}
// best = LLONG_MIN; gain(root, best);
```

The distinction between **what you record** (two branches) and **what you return** (one branch) is the whole problem. Start `best` at `LLONG_MIN` so that an all-negative tree gives its largest value, not 0.

## 8. Complexity

Every algorithm in this lesson is a single DFS: **O(n) time and O(h) recursion depth**. The exceptions are the outputs themselves: listing all root-to-leaf paths can produce O(n·h) numbers, and LCA is O(n) *per query*. The O(n²) traps are recomputing `height()` at every node, recounting paths from every start node, and copying the path vector into every call.

On a degenerate tree (h = n), recursion depth is n. A 10⁵–10⁶ node chain overflows the default 8 MB stack. In production, use an explicit stack, or run the work on a thread with a bigger stack. The practice drivers do the latter, so you can focus on the recursion design.

## 9. Recognising the pattern

| The question mentions… | Use |
|---|---|
| depth, path so far, maximum/sum from the root, "good" relative to ancestors | top-down parameter |
| height, size, subtree sum, "is every subtree …" | bottom-up return value |
| longest/best path anywhere, diameter | return the height or gain, record the bend |
| choose nodes with constraints between parent and child | tree DP with several states per node |
| downward paths with sum k, starting anywhere | prefix sums + hash map + backtracking |
| list all paths | backtracking with one shared vector |
| common ancestor, distance between nodes | LCA recursion (or binary lifting for many queries) |

## 10. Common mistakes

1. **A vague return value.** "Returns the diameter" vs "returns the height and records the diameter": only the second composes.
2. **Recomputing heights in a loop over nodes:** O(n²).
3. **Min depth through a missing child** (returns 1 for a chain).
4. **Checking path sums at non-leaves**, or stopping early when the sum matches.
5. **Forgetting to pop / decrement** when backtracking, so siblings see stale state.
6. **Returning a two-branch value to the parent** in max path sum.
7. **`int` overflow:** sums of 2·10⁵ values up to 10⁹ need `long long`; counts of paths can reach about n²/2.
8. **Comparing only with the parent** in "good nodes" instead of with the whole path.

## 11. Interview questions

**Q: Why is the diameter not always `height(left) + height(right)` at the root?** The longest path may lie entirely inside one subtree, for example a root with one huge left subtree and nothing on the right.

**Q: What is the time complexity of checking balance by calling `height()` from every node?** O(n log n) on a balanced tree and O(n²) on a chain. The sentinel version is O(n).

**Q: How would you find the LCA in a BST?** Walk from the root: if both values are smaller, go left; if both are larger, go right; otherwise you are at the LCA. That's O(h) without visiting other subtrees.

**Q: Path Sum III in O(n): why must the prefix-sum count be decremented?** The map must describe only the current root-to-node path. Prefixes from a finished branch would create "paths" that jump between siblings.

**Q: What does "tree DP" mean?** Computing, for every node, a small fixed set of values that summarise its subtree under different assumptions, from the children's values, in one postorder pass.

## Check your understanding

1. What does `height_and_diameter` return for a chain of 4 nodes, and what is `best`?
2. In `good(n, best)`, why is the initial `best` `LLONG_MIN` and not `INT_MIN` or 0?
3. For the tree `1` with children `-2` and `3`, what is the maximum path sum, and which path achieves it?
4. Why does the LCA recursion return `n` immediately when `n->val == p`, even if `q` might be below?
5. Robber: why can't a single number per node (the best total for the subtree) be enough?

<details>
<summary>Answers</summary>

1. It returns 4 (the height in nodes) and `best` is 3 (edges between the two ends).
2. With 0, a negative root would not count as good. `INT_MIN` works for `>=` comparisons too, but `LLONG_MIN` makes "smaller than every value" obviously true and keeps the comparison in `long long` without surprises. The key point is that the root must always be good.
3. 4, from the path `1 → 3`. At the root, `l = max(0, −2) = 0` and `r = 3`, so the bend value is 1 + 0 + 3 = 4.
4. If `q` is below `p`, then `p` is the LCA and returning it is correct. If `q` is elsewhere, an ancestor receives `p` from one side and `q` from the other and returns itself. Either way, searching below `p` is unnecessary.
5. The parent's choice depends on whether the child was taken: taking the parent forbids taking the child. The best total alone hides that, so the parent can't combine correctly.

</details>
