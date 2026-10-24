# Dynamic Programming I: 1D

**Dynamic programming** solves problems whose optimal answer is built from optimal answers to smaller, **overlapping** subproblems, by computing each subproblem once. In Python, the two styles are **memoised recursion** (`functools.cache`) and **bottom-up tabulation** (a list filled in order). This lesson covers the method and the 1-D family: climbing stairs, house robber, coin change, decode ways, word break, the longest increasing subsequence and maximum subarray. These are the patterns every later DP builds on.

## 1. The method in five questions

1. **State**: what does `dp[i]` mean? Write it as a sentence: "`dp[i]` = the maximum loot from houses 0..i".
2. **Transition**: how is `dp[i]` computed from smaller states?
3. **Base cases**.
4. **Order**: compute the dependencies first (increasing i for most 1-D DPs).
5. **Answer**: which state, or what aggregate (`dp[n]`, `max(dp)`)?

## 2. Top-down vs bottom-up in Python

```python
from functools import cache

@cache
def stairs(n):                         # ways to climb n steps taking 1 or 2 at a time
    if n <= 1:
        return 1
    return stairs(n - 1) + stairs(n - 2)

def stairs_bottom_up(n):               # O(n) time, O(1) space
    a, b = 1, 1                        # dp[i-2], dp[i-1]
    for _ in range(n - 1):
        a, b = b, a + b
    return b
```

> [!WARNING]
> `@cache` recursion is limited by Python's recursion depth (about 1000 frames by default). `stairs(5000)` raises `RecursionError`. For large n, tabulate, or warm the cache bottom-up (`for i in range(n): stairs(i)`). Memoised functions also keep their cache forever: call `stairs.cache_clear()` between independent test cases.

## 3. The classic 1-D problems

### House robber (no two adjacent)

`dp[i] = max(dp[i-1], dp[i-2] + a[i])`: either skip house i, or rob it on top of the best up to i−2.

```python
def rob(a):
    take = skip = 0                    # best ending with/without robbing the previous house
    for x in a:
        take, skip = skip + x, max(take, skip)
    return max(take, skip)
```

The circular variant (first and last adjacent) is `max(rob(a[1:]), rob(a[:-1]))`.

### Coin change: minimum coins and number of ways

```python
def min_coins(coins, amount):
    INF = float("inf")
    dp = [0] + [INF] * amount          # dp[s] = fewest coins summing to s
    for s in range(1, amount + 1):
        for c in coins:
            if c <= s and dp[s - c] + 1 < dp[s]:
                dp[s] = dp[s - c] + 1
    return dp[amount] if dp[amount] < INF else -1

def count_ways(coins, amount):          # combinations (order doesn't matter)
    dp = [1] + [0] * amount
    for c in coins:                    # coins OUTER: each combination counted once
        for s in range(c, amount + 1):
            dp[s] += dp[s - c]
    return dp[amount]
```

> [!KEY]
> Loop order changes the meaning. With coins in the **outer** loop, you count **combinations** ({1,2} once). With sums in the outer loop and coins inner, you count **sequences** (1+2 and 2+1 separately), which is what "climbing stairs with steps from a set" wants.

### Decode ways ("12" → "AB" or "L")

```python
def decode_ways(s):
    prev2, prev1 = 1, 1 if s and s[0] != "0" else 0   # dp[i-2], dp[i-1]
    for i in range(1, len(s)):
        cur = 0
        if s[i] != "0":
            cur += prev1                                 # single digit 1-9
        if 10 <= int(s[i - 1:i + 1]) <= 26:
            cur += prev2                                 # two digits 10-26
        prev2, prev1 = prev1, cur
    return prev1 if s else 0
```

### Word break

```python
def word_break(s, words):
    ws, L = set(words), max(map(len, words), default=0)
    ok = [True] + [False] * len(s)                       # ok[i]: s[:i] can be segmented
    for i in range(1, len(s) + 1):
        for j in range(max(0, i - L), i):                # only look back as far as the longest word
            if ok[j] and s[j:i] in ws:
                ok[i] = True
                break
    return ok[len(s)]
```

### Maximum subarray (Kadane)

`best_ending_here = max(x, best_ending_here + x)`: either extend the previous run or start fresh.

```python
def max_subarray(a):
    cur = best = a[0]
    for x in a[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best
```

The maximum *product* subarray tracks both the max and the min ending here, because a negative times a negative flips them.

## 4. Longest increasing subsequence: O(n²) → O(n log n)

The straightforward DP is `dp[i] = 1 + max(dp[j] for j < i if a[j] < a[i])`, which is O(n²). The **patience sorting** method keeps `tails[k]` = the smallest possible tail of an increasing subsequence of length k + 1:

```python
from bisect import bisect_left

def lis_length(a):
    tails = []
    for x in a:
        i = bisect_left(tails, x)      # bisect_right for non-decreasing subsequences
        if i == len(tails):
            tails.append(x)            # extends the longest subsequence
        else:
            tails[i] = x               # a better (smaller) tail for length i + 1
    return len(tails)

lis_length([10, 9, 2, 5, 3, 7, 101, 18])   # 4  (2, 3, 7, 18)
```

`tails` is always sorted, so each element costs O(log n). To reconstruct the subsequence, store for each element the index of its predecessor (the element at `tails[i-1]` when it was placed).

## 5. Recognising 1-D DP

| Phrase | Likely state |
|---|---|
| "number of ways to reach / form" | `dp[i]` = count, summing over transitions |
| "minimum cost / steps to reach i" | `dp[i]` = min over predecessors |
| "maximum without adjacent / with a cooldown" | `dp[i]` plus a small state machine (take/skip, hold/sold) |
| "can the prefix be …" | boolean `dp[i]` |
| subsequence with an order constraint | LIS-style `dp[i]` or a patience structure |

**State machines**: stock-trading problems with a cooldown or fee keep two or three variables per day (holding, not holding, cooling) and update them all at once each day.

## 6. Exam-ready answers

> [!EXAM]
> **Memoisation vs tabulation.** Memoisation implements dynamic programming top-down: a recursive function caches each subproblem's result the first time it is computed, so only the subproblems actually reached are solved, at the cost of recursion overhead and depth limits. Tabulation works bottom-up: subproblem results are stored in an array filled in an order such that each entry's dependencies are already computed, which avoids recursion and often allows space optimisation by keeping only the most recent entries. Both have the same asymptotic time, the number of states multiplied by the cost of each transition.

## 7. Cheat sheet

| Problem | Recurrence | Time / space |
|---|---|---|
| climbing stairs | `dp[i] = dp[i-1] + dp[i-2]` | O(n) / O(1) |
| house robber | `max(dp[i-1], dp[i-2] + a[i])` | O(n) / O(1) |
| min coins | `min(dp[s-c] + 1)` | O(n·S) / O(S) |
| count combinations | coins outer, `dp[s] += dp[s-c]` | O(n·S) / O(S) |
| decode ways | one-digit + two-digit transitions | O(n) / O(1) |
| word break | `ok[i] = any(ok[j] and s[j:i] in words)` | O(n·L) |
| max subarray | Kadane | O(n) / O(1) |
| LIS | patience + bisect | O(n log n) |

> [!INTERVIEW]
> **"How do you know it's DP and not greedy?"** Try to find a counterexample to the greedy choice. Coin change with {1, 3, 4} and amount 6: greedy takes 4+1+1 (3 coins), but 3+3 needs 2. When a locally best choice can hurt later options, and the problem decomposes into overlapping subproblems with optimal substructure, it's DP. State the subproblem definition explicitly before writing code.
