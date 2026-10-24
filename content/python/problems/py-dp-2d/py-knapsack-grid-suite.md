---
id: py-knapsack-grid-suite
title: "2-D DP Suite: Knapsack with Reconstruction, Target Sum, Partition, Cherry Grid"
difficulty: Hard
order: 1
tags: knapsack, reconstruction, subset sum, bitsets, grid DP
time_limit: 4
---
## Statement
```python
def knapsack_choice(weights, values, W):
    """0/1 knapsack. Return (best_value, chosen_indices_sorted). Among optimal subsets, return the one
    found by this rule: walk items from the LAST to the first and SKIP item i whenever skipping it
    still allows an optimal value with the remaining items and capacity."""

def target_sum_ways(nums, target):
    """Assign + or - to every number (non-negative ints); count assignments whose sum is target."""

def can_partition(nums):
    """Can nums be split into two subsets of equal sum? Sums can reach ~10^6 with n up to 2000:
    use a big-integer bitset."""

def max_gems(grid):
    """grid of non-negative ints. A robot walks from top-left to bottom-right moving only right/down,
    collecting gems. Return the maximum it can collect; cells with -1 are blocked (return -1 if no path)."""
```

Test lines are `(function_name, args)` literals or `gen NAME SEED N`.

## Starter
```python
def knapsack_choice(weights, values, W):
    return (0, [])

def target_sum_ways(nums, target):
    count = 0
    def go(i, s):
        nonlocal count
        if i == len(nums):
            count += s == target
            return
        go(i + 1, s + nums[i]); go(i + 1, s - nums[i])
    go(0, 0)
    return count

def can_partition(nums):
    return sum(nums) % 2 == 0

def max_gems(grid):
    return 0
```

## Driver
```python
import ast
import random
import sys

FUNCS = {f.__name__: f for f in (knapsack_choice, target_sum_ways, can_partition, max_gems)}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        if name == "knapsack_choice":
            w = [rng.randrange(1, 500) for _ in range(n)]
            v = [rng.randrange(1, 1000) for _ in range(n)]
            best, chosen = knapsack_choice(w, v, 20000)
            print(name, n, best, len(chosen), chosen[:6], sum(w[i] for i in chosen) <= 20000, sum(v[i] for i in chosen) == best)
        elif name == "target_sum_ways":
            a = [rng.randrange(0, 20) for _ in range(n)]
            print(name, n, target_sum_ways(a, 7), target_sum_ways(a, 8), target_sum_ways(a, 10**6))
        elif name == "can_partition":
            a = [rng.randrange(1, 1000) for _ in range(n)]
            b = a + [1000 + sum(a) % 2]
            print(name, n, can_partition(a), can_partition(b), can_partition([500] * n))
        else:
            g = [[-1 if rng.random() < 0.1 else rng.randrange(10) for _ in range(n)] for _ in range(n)]
            g[0][0] = g[-1][-1] = 0
            print(name, n, max_gems(g))
        continue
    name, args = ast.literal_eval(line)
    print(name, "->", FUNCS[name](*args))
```

## Tests
=== sample
("knapsack_choice", ([1, 3, 4, 5], [1, 4, 5, 7], 7))
("target_sum_ways", ([1, 1, 1, 1, 1], 3))
("can_partition", ([1, 5, 11, 5],))
("max_gems", ([[0, 1, 1], [1, -1, 1], [1, 1, 0]],))
---
knapsack_choice -> (9, [1, 2])
target_sum_ways -> 5
can_partition -> True
max_gems -> 3
=== hidden
("knapsack_choice", ([], [], 5))
("knapsack_choice", ([5], [10], 4))
("knapsack_choice", ([2, 2, 2], [3, 3, 3], 4))
("knapsack_choice", ([1, 2, 3], [6, 10, 12], 5))
("target_sum_ways", ([], 0))
("target_sum_ways", ([0, 0, 1], 1))
("target_sum_ways", ([2], 3))
("can_partition", ([1, 2, 3, 5],))
("can_partition", ([2, 2],))
("max_gems", ([[0]],))
("max_gems", ([[0, -1], [-1, 0]],))
("max_gems", ([[5, 1, 9], [2, 8, -1], [0, 3, 4]],))
---
knapsack_choice -> (0, [])
knapsack_choice -> (0, [])
knapsack_choice -> (6, [0, 1])
knapsack_choice -> (22, [1, 2])
target_sum_ways -> 1
target_sum_ways -> 4
target_sum_ways -> 0
can_partition -> False
can_partition -> True
max_gems -> 0
max_gems -> -1
max_gems -> 22
=== hidden
gen knapsack_choice 1 300
gen target_sum_ways 2 300
---
knapsack_choice 300 87849 128 [1, 5, 6, 7, 10, 13] True True
target_sum_ways 300 0 8524577311796024442153314728593272233287541049962776371295826271737107967766700125847552 0
=== hidden
gen can_partition 3 2000
gen max_gems 4 400
---
can_partition 2000 False True True
max_gems 400 5293

## Hints
- **Reconstruction** needs the full table `dp[i][w]` (best using the first i items with capacity w). Walking back from `(n, W)`: if `dp[i-1][w] == dp[i][w]`, skip item i−1; otherwise take it and subtract its weight. Storing rows as lists of ints for n = 300 and W = 20000 is 6 million entries, which is fine.
- **Target sum**: with P the plus-set, `P − (total − P) = target`, so `P = (total + target) / 2`. Count the subsets with that sum (it's 0 if the parity is wrong or the value is out of range). Zeros double the count automatically if you use `dp[s] += dp[s - x]` with s descending, including s = x.
- **Partition**: `reach = 1; for x in nums: reach |= reach << x`, then test bit total/2.
- **Grid**: a rolling row with `-inf` for unreachable cells.

## Solution
```python
def knapsack_choice(weights, values, W):
    n = len(weights)
    dp = [[0] * (W + 1)]
    for i in range(n):
        prev, wt, val = dp[-1], weights[i], values[i]
        row = prev[:]
        for w in range(wt, W + 1):
            cand = prev[w - wt] + val
            if cand > row[w]:
                row[w] = cand
        dp.append(row)
    chosen, w = [], W
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:                  # skipping item i-1 would lose value: take it
            chosen.append(i - 1)
            w -= weights[i - 1]
    return dp[n][W], sorted(chosen)

def target_sum_ways(nums, target):
    total = sum(nums)
    if (total + target) % 2 or abs(target) > total:
        return 0
    goal = (total + target) // 2
    dp = [1] + [0] * goal
    for x in nums:
        for s in range(goal, x - 1, -1):
            dp[s] += dp[s - x]
    return dp[goal]

def can_partition(nums):
    total = sum(nums)
    if total % 2:
        return False
    reach = 1
    for x in nums:
        reach |= reach << x
    return (reach >> (total // 2)) & 1 == 1

def max_gems(grid):
    NEG = float("-inf")
    C = len(grid[0])
    dp = [NEG] * C
    for r, row in enumerate(grid):
        for c in range(C):
            if row[c] == -1:
                dp[c] = NEG
                continue
            if r == 0 and c == 0:
                best = 0
            else:
                best = max(dp[c], dp[c - 1] if c else NEG)   # dp[c] still holds the cell above
            dp[c] = best + row[c] if best != NEG else NEG
    return dp[-1] if dp[-1] != NEG else -1
```

- **Reconstruction** is the reason to keep the 2-D table. Walking back, a value change between rows i−1 and i means item i−1 must be in the optimum. Checking `dp[i][w] != dp[i-1][w]` from the last item backwards implements the "skip whenever possible" rule exactly.
- **Target sum** becomes a subset-count knapsack through algebra: the plus-set's sum is fixed at `(total + target) / 2`. That turns an O(2ⁿ) search into O(n · total).
- **Partition** uses Python's arbitrary-precision integers as a bitset: one shift-or per item updates every reachable sum at C speed. That's dramatically faster than a boolean list.
- **max_gems** is a rolling-row grid DP. `-inf` propagates "unreachable" through blocked cells naturally.
