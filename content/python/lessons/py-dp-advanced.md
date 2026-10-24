# Dynamic Programming IV: Bitmask, Trees, Intervals

The final DP lesson covers three state shapes beyond sequences and grids:
- **Bitmask DP**: the state includes a *set* of used items (travelling salesman, assignment, covering)
- **Tree DP**: states live on the nodes of a tree (independent sets, tree diameters, rerooting)
- **Interval DP**: the state is a subrange `[i, j]` (matrix-chain order, burst balloons, optimal merge)

We'll also see **digit DP** for counting numbers with digit constraints. These solve exponential-looking problems in polynomial or "small exponential" time, and appear in robotics (visiting waypoints optimally), compilers (instruction scheduling) and combinatorics.

## 1. Bitmask DP

Represent a subset of n ≤ ~20 elements as an integer: bit i is set iff element i is in the set.

| Operation | Code |
|---|---|
| element i in mask? | `mask >> i & 1` |
| add i | `mask \| (1 << i)` |
| remove i | `mask & ~(1 << i)` |
| size of the set | `mask.bit_count()` (3.10+) |
| iterate over the submasks of m | `s = m; while s: ...; s = (s - 1) & m` |
| full set | `(1 << n) - 1` |

### Travelling salesman (Held–Karp)

`dp[mask][v]` = the minimum cost of a path that starts at 0, visits exactly the set `mask` and ends at v:

```python
def tsp(dist):
    n = len(dist)
    INF = float("inf")
    full = 1 << n
    dp = [[INF] * n for _ in range(full)]
    dp[1][0] = 0                                    # only city 0 visited, standing at 0
    for mask in range(full):
        if not mask & 1:
            continue                                # every path starts at 0
        row = dp[mask]
        for v in range(n):
            cur = row[v]
            if cur == INF:
                continue
            for u in range(n):
                if not mask >> u & 1:
                    nm = mask | (1 << u)
                    if cur + dist[v][u] < dp[nm][u]:
                        dp[nm][u] = cur + dist[v][u]
    return min(dp[full - 1][v] + dist[v][0] for v in range(n))   # return to the start
```

That's O(2ⁿ · n²) instead of O(n!): for n = 16, about 1.7·10⁷ steps versus 2·10¹³. Robotics uses it to order a few dozen inspection waypoints or pick-and-place targets exactly (with heuristics like 2-opt beyond that).

### Assignment: n workers to n jobs

`dp[mask]` = the minimum cost of assigning the jobs in `mask` to the first `popcount(mask)` workers, so the worker is implied by the size of the mask. That's O(2ⁿ · n). (The Hungarian algorithm does it in O(n³).)

### Submask enumeration: O(3ⁿ) total

`for mask in all: for sub in submasks(mask)` visits 3ⁿ pairs in total (each element is in sub, in mask but not sub, or not in mask). Use it for "partition a set into groups" DPs, such as the minimum number of sessions or fair work distribution.

## 2. Tree DP

Root the tree, then compute each node's state from its children's states (a postorder traversal).

### Maximum independent set (the "house robber III" pattern)

```python
def max_independent(adj, values, root=0):
    """Max total value of nodes with no two adjacent. Iterative postorder (safe for deep trees)."""
    n = len(values)
    parent = [-1] * n
    order, st = [], [root]
    seen = [False] * n
    seen[root] = True
    while st:
        u = st.pop()
        order.append(u)
        for v in adj[u]:
            if not seen[v]:
                seen[v] = True
                parent[v] = u
                st.append(v)
    take = values[:]                        # best in u's subtree with u chosen
    skip = [0] * n                          # best with u not chosen
    for u in reversed(order):               # children before parents
        p = parent[u]
        if p >= 0:
            take[p] += skip[u]
            skip[p] += max(take[u], skip[u])
    return max(take[root], skip[root])
```

> [!KEY]
> **Iterative tree DP**: produce a DFS order with a stack, then process it in reverse, so every node is handled after all its children. That avoids Python's recursion limit on 10⁵-node trees (paths can be that deep).

### Rerooting: answers for every root in O(n)

"For every node, the sum of distances to all other nodes": a first pass computes subtree sizes and the answer for root 0. A second, top-down pass moves the root from u to child v: `ans[v] = ans[u] - size[v] + (n - size[v])`, because v's subtree gets 1 closer and everything else gets 1 farther. Rerooting turns O(n²) "run the DP from every root" into O(n).

## 3. Interval DP

The state is a range `[i, j]`, computed in order of increasing length, and each state chooses a split point k.

### Matrix-chain multiplication

Multiplying matrices A₁…Aₙ with dimensions `d[0]×d[1], d[1]×d[2], …`: the order of multiplication changes the cost (associativity) but not the result.

```python
def matrix_chain(d):
    n = len(d) - 1
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = min(dp[i][k] + dp[k + 1][j] + d[i] * d[k + 1] * d[j + 1] for k in range(i, j))
    return dp[0][n - 1]

matrix_chain([10, 30, 5, 60])      # 4500: (A1·A2)·A3
```

That's O(n³). The same shape solves "burst balloons" (choose the **last** balloon k to burst in `(i, j)`, so that its neighbours are fixed at i and j), "minimum cost to merge stones", optimal BST construction, and polygon triangulation.

> [!TIP]
> In interval DP, decide what k means: the *first* or *last* operation in the interval. "Last" often makes the subproblems independent (burst balloons), while "first" doesn't.

## 4. Digit DP

"Count the integers in [0, N] whose digits satisfy a property" (no two adjacent equal digits, digit sum divisible by k, contains 7, …). Walk the digits of N from the most significant, with state `(position, tight, property state)`, where **tight** means "the prefix so far equals N's prefix, so the next digit is capped by N's digit":

```python
from functools import cache

def count_digit_sum(N, k):
    """How many x in [0, N] have digit sum divisible by k."""
    digits = list(map(int, str(N)))

    @cache
    def go(pos, tight, rem):
        if pos == len(digits):
            return 1 if rem == 0 else 0
        limit = digits[pos] if tight else 9
        return sum(go(pos + 1, tight and d == limit, (rem + d) % k) for d in range(limit + 1))

    return go(0, True, 0)
```

That's O(digits × 2 × states × 10). Counting over a range [L, R] is `f(R) − f(L − 1)`.

## 5. Choosing the state

| Clue | State |
|---|---|
| "visit all", n ≤ 20 | bitmask of visited + current position |
| assignment / matching, n ≤ 20 | bitmask of used jobs |
| tree, choose nodes with neighbour constraints | (node, chosen?) |
| an answer for every node as the root | rerooting |
| merging/splitting contiguous segments | interval `[i, j]` + split point |
| count numbers up to N with digit rules | (pos, tight, …) digit DP |

## 6. Exam-ready answers

> [!EXAM]
> **Bitmask dynamic programming.** When a problem's state must include a subset of a small set of n elements, the subset can be encoded as an n-bit integer and used as a DP index. The Held–Karp algorithm for the travelling salesman problem defines `dp[S][v]` as the minimum cost of a path starting at a fixed vertex, visiting exactly the vertices in S and ending at v, with transitions extending the path by one unvisited vertex; this gives O(2ⁿ n²) time and O(2ⁿ n) space instead of the O(n!) of enumerating permutations. Such algorithms are exponential but practical for n up to about 20.

## 7. Cheat sheet

| Pattern | Complexity |
|---|---|
| TSP (Held–Karp) | O(2ⁿ n²) |
| assignment bitmask | O(2ⁿ n) |
| all submasks of all masks | O(3ⁿ) |
| tree DP | O(n), iterative postorder |
| rerooting | O(n), two passes |
| interval DP | O(n³) (by length, then split) |
| digit DP | O(len × states × 10) |

> [!INTERVIEW]
> **"Burst balloons: why choose the last balloon?"** If you choose the *first* balloon to burst in an interval, its neighbours change afterwards, so the left and right parts aren't independent. If k is the *last* balloon burst in the open interval (i, j), then while bursting the others, i and k bound the left side and k and j the right side. The subproblems become independent, giving `dp[i][j] = max(dp[i][k] + dp[k][j] + a[i]·a[k]·a[j])` in O(n³).
