# Dynamic Programming in C

**Dynamic programming (DP)** solves a problem by combining solutions to overlapping subproblems, computing each subproblem **once** and storing it. It turns exponential brute force into polynomial time, and it's everywhere in engineering:
- sequence alignment in bioinformatics
- `diff` and edit distance
- speech recognition (Viterbi)
- shortest paths (Bellman–Ford, Floyd–Warshall)
- optimal control (the Bellman equation behind LQR and reinforcement learning)
- resource allocation (knapsack)

C makes the DP table explicit: you decide its layout, its size and how to shrink it. That's exactly what matters on memory-constrained robots.

## 1. When DP applies

Two properties are required:

| Property | Meaning |
|---|---|
| **Optimal substructure** | an optimal solution is built from optimal solutions of subproblems |
| **Overlapping subproblems** | the same subproblems recur many times in naive recursion |

The canonical demonstration:

```c
long long fib_naive(int n) { return n < 2 ? n : fib_naive(n - 1) + fib_naive(n - 2); }   /* O(φⁿ) calls */

long long fib_dp(int n) {               /* O(n) time, O(1) space */
    long long a = 0, b = 1;
    for (int i = 0; i < n; i++) { long long t = a + b; a = b; b = t; }
    return a;
}
```

`fib_naive(50)` makes about 4 × 10¹⁰ calls. `fib_dp(50)` takes 50 additions.

## 2. A recipe that works every time

1. **Define the state** in words: "`dp[i][w]` = the best value using the first `i` items with capacity `w`."
2. **Write the recurrence**: how a state is computed from smaller states.
3. **Base cases.**
4. **Evaluation order**: every state a recurrence reads must be computed before it.
5. **Answer location**: which cell(s) hold the result.
6. **Optimise space** if each row depends only on the previous one.
7. **Reconstruct** the actual solution, not only its value, if required (store choices or walk the table backwards).

## 3. Top-down (memoisation) vs bottom-up (tabulation)

```c
/* Top-down: recursion + cache. Natural to write; only visits reachable states. */
#define MAXN 92
static long long memo[MAXN + 1];
static bool known[MAXN + 1];

long long fib_memo(int n) {
    if (n < 2) return n;
    if (known[n]) return memo[n];
    known[n] = true;
    return memo[n] = fib_memo(n - 1) + fib_memo(n - 2);
}
```

| | Top-down | Bottom-up |
|---|---|---|
| Writing it | follows the recurrence directly | needs an explicit evaluation order |
| States computed | only those reachable | all of them |
| Overhead | function calls, recursion depth (stack overflow risk in C!) | tight loops, vectorisable |
| Space optimisation | hard | easy (rolling rows) |

> [!WARNING]
> Recursion depth in C is limited by the thread's stack (often 8 MB on Linux, a few KB on microcontrollers). A memoised recursion 10⁶ levels deep will crash. For large inputs, prefer bottom-up.

## 4. Classic 1-D DP: coin change

Minimum number of coins summing to `amount` (unbounded supply):

```c
int min_coins(const int *coins, int k, int amount) {
    int *dp = malloc((size_t)(amount + 1) * sizeof *dp);
    if (!dp) return -2;
    dp[0] = 0;
    for (int s = 1; s <= amount; s++) {
        dp[s] = INT_MAX;
        for (int j = 0; j < k; j++)
            if (coins[j] <= s && dp[s - coins[j]] != INT_MAX && dp[s - coins[j]] + 1 < dp[s])
                dp[s] = dp[s - coins[j]] + 1;
    }
    int r = dp[amount] == INT_MAX ? -1 : dp[amount];
    free(dp);
    return r;
}
```

The `!= INT_MAX` check prevents `INT_MAX + 1`, which is signed overflow and therefore UB. Counting the **number of ways** instead uses `dp[s] += dp[s - c]`, with the coin loop **outside** the sum loop so that combinations aren't counted once per order.

## 5. Classic 2-D DP: 0/1 knapsack, with the space trick

`dp[i][w]` = the best value from the first `i` items with capacity `w`:

`dp[i][w] = max(dp[i-1][w], dp[i-1][w - wt[i]] + val[i])`

Row `i` reads only row `i-1`, so keep one row and iterate `w` **downwards**. That way, `dp[w - wt]` still holds the previous row's value, and each item is used at most once:

```c
long long knapsack(const int *wt, const int *val, int n, int W) {
    long long *dp = calloc((size_t)W + 1, sizeof *dp);
    for (int i = 0; i < n; i++)
        for (int w = W; w >= wt[i]; w--)            /* downwards = 0/1; upwards = unbounded */
            if (dp[w - wt[i]] + val[i] > dp[w]) dp[w] = dp[w - wt[i]] + val[i];
    long long best = dp[W];
    free(dp);
    return best;
}
```

The cost is O(nW) time and O(W) memory. That's **pseudo-polynomial**: polynomial in the *value* of W, which takes log W bits to write down. Knapsack is NP-hard, so no truly polynomial algorithm is known.

## 6. Sequence DP: longest common subsequence and edit distance

Edit distance (Levenshtein), the minimum number of insertions, deletions and substitutions turning `s` into `t`:

```
dp[i][j] = dp[i-1][j-1]                     if s[i-1] == t[j-1]
         = 1 + min(dp[i-1][j],              delete s[i-1]
                   dp[i][j-1],              insert t[j-1]
                   dp[i-1][j-1])            substitute
dp[i][0] = i,  dp[0][j] = j
```

```c
int edit_distance(const char *s, const char *t) {
    size_t n = strlen(s), m = strlen(t);
    int *prev = malloc((m + 1) * sizeof *prev), *cur = malloc((m + 1) * sizeof *cur);
    for (size_t j = 0; j <= m; j++) prev[j] = (int)j;
    for (size_t i = 1; i <= n; i++) {
        cur[0] = (int)i;
        for (size_t j = 1; j <= m; j++) {
            if (s[i - 1] == t[j - 1]) cur[j] = prev[j - 1];
            else {
                int best = prev[j] < cur[j - 1] ? prev[j] : cur[j - 1];
                if (prev[j - 1] < best) best = prev[j - 1];
                cur[j] = best + 1;
            }
        }
        int *tmp = prev; prev = cur; cur = tmp;      /* roll the rows: swap pointers, no copying */
    }
    int d = prev[m];
    free(prev); free(cur);
    return d;
}
```

That's O(nm) time and O(m) space. If you need the actual edit script, keep the full table (or use Hirschberg's divide and conquer, which recovers the alignment in O(m) space).

### Storing a 2-D table in C

```c
/* one contiguous block, row-major: cell (i, j) at i * cols + j */
int *dp = malloc((size_t)rows * cols * sizeof *dp);
#define DP(i, j) dp[(size_t)(i) * cols + (j)]

/* or a pointer to a VLA type (C99), when sizes are runtime values but you want dp[i][j] syntax */
int (*t)[cols] = malloc(sizeof(int[rows][cols]));
t[i][j] = 0;
free(t);
```

A single allocation is cache-friendly, and you free it once. An array of row pointers costs `rows + 1` allocations and scatters rows across the heap.

## 7. Interval DP and DP over subsets

- **Interval DP** (e.g. matrix-chain multiplication, optimal BST, burst balloons): `dp[i][j]` covers the range `[i, j]` and is computed in order of increasing length, so `O(n³)`.
- **Bitmask DP** (travelling salesman on ≤ 20 cities, assignment): `dp[mask][v]` = the cheapest path visiting exactly the set `mask` and ending at `v`, so `O(2ⁿ n²)`. Bit operations (next lesson) make the subsets cheap.

```c
/* Held–Karp TSP: dist is n×n, n <= 20 */
for (unsigned mask = 1; mask < (1u << n); mask++)
    for (int v = 0; v < n; v++) {
        if (!(mask & (1u << v)) || dp[mask][v] == INF) continue;
        for (int u = 0; u < n; u++)
            if (!(mask & (1u << u))) {
                unsigned nm = mask | (1u << u);
                if (dp[mask][v] + dist[v][u] < dp[nm][u]) dp[nm][u] = dp[mask][v] + dist[v][u];
            }
    }
```

## 8. DP in robotics and AI

| Algorithm | The DP inside it |
|---|---|
| Dijkstra / Bellman–Ford | `dist[v] = min(dist[u] + w(u, v))` |
| Viterbi (HMM decoding, speech, localisation) | `best[t][s] = max over s' of best[t-1][s'] · P(s'→s) · P(obs_t \| s)` |
| Dynamic Time Warping (gesture or trajectory matching) | the edit-distance recurrence on real-valued sequences |
| Value iteration (MDPs, RL) | `V(s) = max_a [R(s,a) + γ Σ P(s'\|s,a) V(s')]`: the Bellman equation |
| LQR (optimal control) | backward Riccati recursion: DP over time steps |

## 9. Exam-ready answers

> [!EXAM]
> **Dynamic programming.** Dynamic programming is an algorithm design technique for problems with optimal substructure and overlapping subproblems. The problem is expressed as a recurrence over states; each state's value is computed once and stored, either top-down by memoising a recursive function or bottom-up by filling a table in an order in which every dependency is computed first. This reduces exponential naive recursion to time proportional to the number of states multiplied by the work per state. Space can often be reduced by keeping only the parts of the table that later states still need, such as the previous row. Unlike greedy algorithms, DP considers all choices for each subproblem, so it finds optimal solutions even when locally optimal choices fail.

## 10. Cheat sheet

| Problem | State | Time | Space (optimised) |
|---|---|---|---|
| Fibonacci, climbing stairs | `dp[i]` | n | 1 |
| coin change (min coins) | `dp[sum]` | n·S | S |
| 0/1 knapsack | `dp[w]`, w descending | n·W | W |
| unbounded knapsack | `dp[w]`, w ascending | n·W | W |
| LCS / edit distance | `dp[i][j]` | n·m | min(n, m) |
| longest increasing subsequence | `tails[]` + binary search | n log n | n |
| matrix chain | `dp[i][j]` by length | n³ | n² |
| TSP | `dp[mask][v]` | 2ⁿ n² | 2ⁿ n |

> [!INTERVIEW]
> **"Greedy or DP?"** Greedy commits to the locally best choice and never revisits it. That's correct only when you can prove the greedy-choice property (activity selection, Huffman codes, Dijkstra with non-negative weights). Coins `{1, 3, 4}` with amount 6 break greedy (4+1+1 = 3 coins, but 3+3 = 2), so DP is needed. Give a counterexample like this to show you know why.
