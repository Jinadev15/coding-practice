# Backtracking

**Backtracking** systematically explores a tree of partial solutions. Extend a candidate one choice at a time, and as soon as it can't lead to a valid solution, undo the last choice and try the next one. It's the general method for **enumeration** (all subsets, permutations, combinations), **constraint satisfaction** (N-queens, Sudoku, graph colouring, scheduling) and **search with pruning** (word search, path finding with constraints). The running time is often exponential. The art is in **pruning** early and keeping each step O(1) with incremental state.

## 1. The template

```python
def backtrack(state, choices):
    if is_complete(state):
        record(state)
        return
    for choice in choices(state):
        if is_valid(state, choice):        # prune: don't descend into dead branches
            apply(state, choice)           # make the choice
            backtrack(state, choices)      # explore
            undo(state, choice)            # un-make it (restore the state exactly)
```

> [!KEY]
> Modify **one shared state** in place and undo after the recursive call (`path.append(x)` … `path.pop()`). Copying the state at each level is simpler but multiplies the cost by the state size. When recording a solution, record a **copy** (`out.append(path[:])`), because the shared list keeps changing.

## 2. The three classic enumerations

```python
def subsets(nums):                        # 2^n subsets
    out, path = [], []
    def go(i):
        if i == len(nums):
            out.append(path[:]); return
        go(i + 1)                         # skip nums[i]
        path.append(nums[i]); go(i + 1); path.pop()   # take nums[i]
    go(0)
    return out

def permutations(nums):                   # n! orderings
    out, path, used = [], [], [False] * len(nums)
    def go():
        if len(path) == len(nums):
            out.append(path[:]); return
        for i, x in enumerate(nums):
            if not used[i]:
                used[i] = True; path.append(x)
                go()
                path.pop(); used[i] = False
    go()
    return out

def combinations(n, k):                   # C(n, k) choices of k from 1..n
    out, path = [], []
    def go(start):
        if len(path) == k:
            out.append(path[:]); return
        for x in range(start, n + 1):
            if n - x + 1 < k - len(path):
                break                     # prune: not enough numbers left
            path.append(x); go(x + 1); path.pop()
    go(1)
    return out
```

| Space | Size | Branching | Python `itertools` |
|---|---|---|---|
| subsets | 2ⁿ | take/skip | `chain.from_iterable(combinations(s, r) for r in ...)` |
| permutations | n! | any unused | `permutations` |
| combinations | C(n, k) | increasing start index | `combinations` |
| combinations with repetition | C(n+k−1, k) | start index stays | `combinations_with_replacement` |

### Duplicates in the input

Sort first, then skip a value equal to the previous one **at the same depth**:

```python
def subsets_with_dup(nums):
    nums.sort()
    out, path = [], []
    def go(start):
        out.append(path[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue                  # the same value was already tried at this level
            path.append(nums[i]); go(i + 1); path.pop()
    go(0)
    return out
```

## 3. Constraint satisfaction: N-queens

Place n queens so that none attack each other. Choose one column per row, tracking used columns and diagonals in sets for O(1) checks:

```python
def n_queens(n):
    cols, d1, d2 = set(), set(), set()    # r - c is constant on "\" diagonals, r + c on "/"
    out, placement = [], []
    def go(r):
        if r == n:
            out.append(placement[:]); return
        for c in range(n):
            if c in cols or (r - c) in d1 or (r + c) in d2:
                continue
            cols.add(c); d1.add(r - c); d2.add(r + c); placement.append(c)
            go(r + 1)
            cols.remove(c); d1.remove(r - c); d2.remove(r + c); placement.pop()
    go(0)
    return out

len(n_queens(8))    # 92
```

Bitmasks make this several times faster: `avail = ~(cols | d1 | d2) & full`, iterating over the low set bits.

## 4. Pruning strategies

| Strategy | Example |
|---|---|
| feasibility check before descending | queens conflict sets, the Sudoku candidate check |
| bound: give up when the best possible ≤ the best found | branch and bound for knapsack/TSP |
| sorted choices + early break | combination sum: stop when the candidate exceeds the remaining target |
| most-constrained variable first | Sudoku: fill the cell with the fewest candidates (the MRV heuristic) |
| symmetry breaking | N-queens: only try the first-row queen in the left half, then mirror |
| memoisation | when subproblems repeat, backtracking becomes DP |

```python
def combination_sum(cands, target):       # each candidate is reusable
    cands.sort()
    out, path = [], []
    def go(start, remain):
        if remain == 0:
            out.append(path[:]); return
        for i in range(start, len(cands)):
            if cands[i] > remain:
                break                     # sorted: everything after is bigger too
            path.append(cands[i]); go(i, remain - cands[i]); path.pop()
    go(0, target)
    return out
```

## 5. Grid search: word search

```python
def exist(board, word):
    R, C = len(board), len(board[0])
    def go(r, c, k):
        if k == len(word):
            return True
        if not (0 <= r < R and 0 <= c < C) or board[r][c] != word[k]:
            return False
        board[r][c] = "#"                 # mark visited in place
        found = any(go(r + dr, c + dc, k + 1) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        board[r][c] = word[k]             # undo
        return found
    return any(go(r, c, 0) for r in range(R) for c in range(C))
```

Searching **many** words at once uses a trie to prune all of them in one traversal (Tries lesson).

## 6. Complexity

The running time is roughly (number of nodes in the search tree) × (work per node). Subsets: O(n · 2ⁿ) including the copies. Permutations: O(n · n!). Good pruning can cut the explored tree by orders of magnitude, but the worst-case bound usually stays exponential, because these problems are often NP-hard (exact cover, SAT, graph colouring).

## 7. Exam-ready answers

> [!EXAM]
> **Backtracking.** Backtracking is a depth-first search over a tree of partial candidate solutions: at each step, it extends the current candidate with one choice, recursively explores, and then undoes the choice to try alternatives. Whenever a partial candidate violates a constraint, or a bound shows it can't improve on the best solution found, the subtree is pruned. It enumerates combinatorial structures such as subsets, permutations and combinations, and solves constraint-satisfaction problems such as N-queens and Sudoku. Its worst-case running time is generally exponential, but pruning, good choice ordering and incremental constraint checks make it practical for many instances.

## 8. Cheat sheet

| Problem | Key trick |
|---|---|
| subsets | take/skip, or loop from `start` |
| permutations | `used[]` flags |
| combinations / sums | `start` index, sorted + break |
| duplicates | sort + `if i > start and a[i] == a[i-1]: continue` |
| N-queens | column and diagonal sets (`r-c`, `r+c`) or bitmasks |
| grid paths | mark/unmark in place |
| record a solution | append a **copy** |

> [!INTERVIEW]
> **"Generate all valid parentheses strings of n pairs."** Backtrack on the string being built: add `(` if `open < n`, and add `)` if `close < open`. The constraints guarantee that only valid strings are ever built, so there's no filtering. The count is the n-th Catalan number, C(2n, n)/(n+1), and the time is O(4ⁿ/√n). Point out that the pruning conditions make every leaf a valid answer, which is the hallmark of a good backtracking design.
