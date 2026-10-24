# Dynamic Programming II: Grids and Knapsack

Many DP problems need two indices: a position in a grid, a prefix of items plus a remaining capacity, or two positions in two sequences. This lesson covers **grid DP** (unique paths, minimum path cost, maximal square, dungeon-style backward DP) and the **knapsack family** (0/1, unbounded, subset sum, target sum, partition). It also covers **space optimisation** from O(n·m) to O(m), which matters when tables reach 10⁷ cells in Python.

## 1. Grid DP

Moving only right or down, `dp[r][c]` depends on `dp[r-1][c]` and `dp[r][c-1]`:

```python
def min_path_sum(grid):
    R, C = len(grid), len(grid[0])
    dp = [0] * C                                   # one row, reused
    for r in range(R):
        for c in range(C):
            if r == 0 and c == 0:
                dp[c] = grid[0][0]
            elif r == 0:
                dp[c] = dp[c - 1] + grid[r][c]
            elif c == 0:
                dp[c] = dp[c] + grid[r][c]         # dp[c] still holds the row above
            else:
                dp[c] = min(dp[c], dp[c - 1]) + grid[r][c]
    return dp[-1]

def unique_paths_with_obstacles(grid):
    C = len(grid[0])
    dp = [0] * C
    dp[0] = 1
    for row in grid:
        for c in range(C):
            if row[c] == 1:
                dp[c] = 0                          # obstacle: no paths through here
            elif c > 0:
                dp[c] += dp[c - 1]
    return dp[-1]
```

> [!KEY]
> **Rolling arrays**: when row r depends only on row r − 1 (and earlier cells of row r), a single 1-D array works. Before you overwrite `dp[c]`, it holds the value from the row above, and `dp[c-1]` already holds the current row. That cuts O(R·C) memory to O(C).

### Maximal square of 1s

`dp[r][c]` = the side of the largest all-1 square with its bottom-right corner at (r, c):

```python
def maximal_square(m):
    if not m: return 0
    C = len(m[0])
    dp, best = [0] * (C + 1), 0
    for row in m:
        prev_diag = 0                              # dp[r-1][c-1]
        for c in range(1, C + 1):
            tmp = dp[c]
            dp[c] = min(dp[c], dp[c - 1], prev_diag) + 1 if row[c - 1] == "1" else 0
            best = max(best, dp[c])
            prev_diag = tmp
    return best * best
```

### When the direction matters: backward DP

**Dungeon game**: the minimum initial health needed to reach the bottom-right corner while health stays ≥ 1. Computing forward fails, because you'd need to track two quantities (current health and the minimum seen so far). Computing **backward from the goal** needs only one: `need[r][c] = max(1, min(need[r+1][c], need[r][c+1]) - grid[r][c])`. When forward DP needs too much state, try reversing the direction.

## 2. The 0/1 knapsack

n items with weights wᵢ and values vᵢ, and capacity W. Each item is used at most once. Maximise the total value.

`dp[i][w] = max(dp[i-1][w], dp[i-1][w - wᵢ] + vᵢ)`

```python
def knapsack(weights, values, W):
    dp = [0] * (W + 1)                     # dp[w]: best value with capacity w
    for wt, val in zip(weights, values):
        for w in range(W, wt - 1, -1):     # DOWNWARD: each item is used at most once
            if dp[w - wt] + val > dp[w]:
                dp[w] = dp[w - wt] + val
    return dp[W]
```

> [!KEY]
> In the one-row version, iterating w **downward** reads `dp[w - wt]` before it's updated in this round, i.e. from the previous item. That enforces 0/1. Iterating **upward** lets an item be reused, which gives the **unbounded** knapsack. The same one-line difference appears in every knapsack variant.

The cost is O(n·W) time, which is **pseudo-polynomial** (polynomial in the value of W, not its bit length). Knapsack is NP-hard.

### Variants as knapsack

| Problem | Reduction |
|---|---|
| subset sum (can we hit exactly T?) | boolean dp, `dp[s] \|= dp[s - x]`, descending |
| partition into equal sums | subset sum with T = total/2 |
| target sum (assign ± to reach S) | count subsets with sum (total + S)/2 |
| number of subsets with sum T | `dp[s] += dp[s - x]`, descending |
| last stone weight II | the subset sum closest to total/2 |
| ones and zeroes (two capacities) | 2-D capacity dp, both dimensions descending |
| bounded counts (item i up to kᵢ times) | binary splitting into 1, 2, 4, … copies, then 0/1 |

```python
def can_partition(nums):
    total = sum(nums)
    if total % 2: return False
    target = total // 2
    reach = 1                              # bitset: bit s set = sum s reachable
    for x in nums:
        reach |= reach << x                # all subset sums at once, using big ints
    return (reach >> target) & 1 == 1
```

The bitset trick uses Python's arbitrary-precision integers as a bit array: one shift-or per item processes all sums in parallel, often 50× faster than the list version.

## 3. Reconstructing the choice

To list *which* items were chosen, keep the full 2-D table (or a `took[i][w]` boolean table), then walk back from `(n, W)`: if `dp[i][w] != dp[i-1][w]`, item i was taken, so subtract its weight. Space-optimised tables lose this information. That's the price of O(W) memory.

## 4. Memory planning in Python

A Python list of ints costs about 8 bytes per slot plus the int objects (small ints are cached). A 10⁴ × 10⁴ table is 10⁸ entries, roughly 800 MB or more. Always ask: does row i only need row i − 1? Then use a rolling array. For boolean DP, use big-int bitsets or `bytearray`. NumPy vectorises row updates when the transition is elementwise.

## 5. Exam-ready answers

> [!EXAM]
> **The 0/1 knapsack problem.** Given items with weights and values and a capacity W, the 0/1 knapsack problem asks for a subset of maximum total value whose total weight doesn't exceed W. Dynamic programming defines `dp[i][w]` as the best value achievable with the first i items and capacity w, with `dp[i][w] = max(dp[i−1][w], dp[i−1][w − wᵢ] + vᵢ)`, giving O(nW) time. Because each row depends only on the previous one, a single array indexed by capacity suffices if capacities are processed in decreasing order, which ensures each item is used at most once; processing in increasing order solves the unbounded variant. The algorithm is pseudo-polynomial, consistent with the problem being NP-hard.

## 6. Cheat sheet

| Pattern | Code |
|---|---|
| grid, right/down moves | one row: `dp[c] = min(dp[c], dp[c-1]) + cost` |
| maximal square | `min(up, left, diag) + 1` |
| needs future info | DP backward from the goal |
| 0/1 knapsack | capacity loop **descending** |
| unbounded | capacity loop **ascending** |
| subset sums | big-int bitset `reach \|= reach << x` |
| reconstruct | keep the full table, walk back |

> [!INTERVIEW]
> **"Partition equal subset sum: complexity?"** It's O(n · total/2) time with a boolean array. Mention the pseudo-polynomial caveat (a total of 10⁹ is infeasible), and the bitset optimisation, which processes 64 sums per machine word (or uses Python big ints). If the numbers are huge but n is small (≤ 40), meet-in-the-middle over subset sums is the alternative.
