# Study guide: Special quiz 3

These three problems come from real research and robotics systems. Each one uses an algorithm you may not have met before, so read the whole section first.

## 1. Exact cover and Algorithm X

**Exact cover:** you have a set of items and a collection of subsets. Choose some subsets so that **every item is covered exactly once**.

Sudoku is an exact cover problem. Placing digit `d` at `(r, c)` covers four constraints:

| Constraint | Meaning | How many |
|---|---|---|
| cell `(r,c)` | the cell is filled | N² |
| row `r` has `d` | each digit once per row | N² |
| column `c` has `d` | each digit once per column | N² |
| box `b` has `d` | each digit once per box | N² |

Each candidate placement is one subset of 4 constraints, and a solution is a set of placements that covers all 4N² constraints exactly once.

**Algorithm X** (Knuth) is backtracking with one clever rule:

```text
solve():
    if no constraints remain: record solution; return
    pick the constraint c with the FEWEST candidate rows   ← the key heuristic
    for each row r that covers c:
        choose r
        for each constraint j covered by r:
            remove j, and remove every other row that also covers j
        solve()
        undo the removals (in reverse order)
```

Picking the constraint with the fewest options ("minimum remaining values") cuts the search tree from astronomically large down to something tiny. If any constraint has **zero** options, the branch is dead, so you backtrack immediately.

In Python, a neat implementation uses `dict[constraint, set[row]]` (`X`) and `dict[row, list[constraint]]` (`Y`):

```python
def select(X, Y, r):
    cols = []
    for j in Y[r]:
        for i in X[j]:
            for k in Y[i]:
                if k != j: X[k].remove(i)
        cols.append(X.pop(j))
    return cols

def deselect(X, Y, r, cols):
    for j in reversed(Y[r]):
        X[j] = cols.pop()
        for i in X[j]:
            for k in Y[i]:
                if k != j: X[k].add(i)
```

To **count** solutions (or detect "not unique"), keep searching after the first one and stop at 2.

## 2. Kalman filters and multi-target tracking

A **Kalman filter** tracks a hidden state (for example, position and velocity) from noisy measurements. It keeps a **mean** `x` and a **covariance** `P` (how unsure it is), and alternates two steps:

```text
Predict:  x = F x            P = F P Fᵀ + Q      (motion makes us less sure)
Update:   y = z − H x                            (innovation: measured − expected)
          S = H P Hᵀ + R                         (innovation covariance)
          K = P Hᵀ S⁻¹                           (Kalman gain)
          x = x + K y        P = (I − K H) P     (measurement makes us more sure)
```

For constant velocity in 2D with time step `dt`: `x = [px, py, vx, vy]` and `F = [[1,0,dt,0],[0,1,0,dt],[0,0,1,0],[0,0,0,1]]`. Because you only measure position, `H = [[1,0,0,0],[0,1,0,0]]`.

**Multiple targets.** Each frame brings several detections, and you don't know which detection belongs to which track. Two tools solve that:

- **Gating:** the squared Mahalanobis distance `d² = yᵀ S⁻¹ y` measures how surprising a detection is, given the track's uncertainty. If `d²` exceeds a chi-square threshold (9.21 for 2D at 99%), the pair is impossible.
- **Global nearest neighbour (GNN):** build a cost matrix of `d²` over the allowed pairs, then solve the **assignment problem** with `scipy.optimize.linear_sum_assignment`. This minimises the **total** cost. It is better than greedy matching, which can steal a detection that another track needed more.

Track management:

- Unmatched detections start new **tentative** tracks.
- A track is **confirmed** after a few hits.
- A track is **deleted** after several misses.

> [!WARNING]
> Use `np.linalg.solve(S, y)` instead of `inv(S) @ y`; it is more accurate. Keep `P` symmetric with `P = (P + P.T) / 2` after updates.

## 3. Optimal task allocation — Hungarian algorithm and bottleneck matching

**Assignment problem:** given an n × n cost matrix (robot i doing task j costs `C[i][j]`), choose one task per robot to **minimise the total cost**. Trying all n! permutations is hopeless, but the **Hungarian algorithm** solves it in O(n³). Its key ideas are:

1. Subtracting a constant from a whole row or column doesn't change *which* assignment is optimal.
2. Keep "potentials" `u[i]` and `v[j]` with `u[i] + v[j] <= C[i][j]`. The edges where this holds with equality are "tight".
3. Repeatedly find an augmenting path that uses only tight edges. When you get stuck, adjust the potentials by the smallest slack, which makes a new edge tight.

The compact O(n³) version (with `u`, `v`, `p`, `way` arrays) is about 30 lines. Verify it against brute force on small n.

**Bottleneck assignment:** minimise the **largest** single cost instead of the sum, so that the slowest robot finishes as early as possible. Use **binary search on the answer**:

```text
sort the distinct costs
binary search for the smallest threshold T such that
    a perfect matching exists using only edges with cost <= T
```

"Does a perfect matching exist?" is **bipartite matching**. Hopcroft–Karp answers it in O(E√V): it uses BFS to build layers, then DFS to find many shortest augmenting paths at once. A simpler augmenting-path (Kuhn) matching in O(VE) also works for moderate sizes.
