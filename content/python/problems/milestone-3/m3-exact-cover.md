---
id: m3-exact-cover
title: Exact Cover with Algorithm X (Sudoku up to 16×16)
difficulty: Expert
order: 1
tags: backtracking, exact cover, Algorithm X, sets, search heuristics, constraint satisfaction
time_limit: 10
---
## Statement
Sudoku, N-queens, pentomino tiling and scheduling are all instances of **exact cover**: choose rows of a 0/1 matrix so that every column is covered **exactly once**. Donald Knuth's **Algorithm X** solves it by recursive backtracking, always branching on the column with the **fewest candidate rows**.

Implement:

1. **`solve_exact_cover(columns, rows, limit=1) -> list[list]`**
   - `columns` is an iterable of column ids, and `rows` is a dict mapping row id → iterable of column ids.
   - Return up to `limit` solutions. Each solution is a **sorted** list of row ids. The order of solutions: try the candidate rows for a column in **sorted row-id order**, and branch on the column with the fewest candidates (ties go to the smallest column id under `sorted`).
   - Columns no row covers make the problem unsolvable: return `[]`.
2. **`solve_sudoku(grid: list[list[int]]) -> list[list[int]] | None`** for an `n²×n²` grid (n = 2, 3 or 4), where 0 is an empty cell.
   - Return the solution, or None. A puzzle with **conflicting givens** returns None.
   - Model it as exact cover with columns `("cell", r, c)`, `("row", r, v)`, `("col", c, v)`, `("box", b, v)`, and row ids `(r, c, v)`.
3. **`count_sudoku_solutions(grid, limit=2) -> int`**: the number of solutions, stopping at `limit`. This checks uniqueness.

The hidden tests include the hardest-known 9×9 puzzles (where naive backtracking takes seconds) and 16×16 puzzles.

## Starter
```python
def solve_exact_cover(columns, rows, limit=1):
    return []


def solve_sudoku(grid):
    n2 = len(grid)
    g = [row[:] for row in grid]

    def ok(r, c, v):
        return all(g[r][k] != v and g[k][c] != v for k in range(n2))

    def bt(i):
        if i == n2 * n2:
            return True
        r, c = divmod(i, n2)
        if g[r][c]:
            return bt(i + 1)
        for v in range(1, n2 + 1):
            if ok(r, c, v):
                g[r][c] = v
                if bt(i + 1):
                    return True
        g[r][c] = 0
        return False

    return g if bt(0) else None


def count_sudoku_solutions(grid, limit=2):
    return 1 if solve_sudoku(grid) else 0
```

## Driver
```python
import sys

def parse(s):
    n2 = int(round(len(s) ** 0.5))
    vals = [int(ch, 17) if ch not in ".0" else 0 for ch in s]     # digits 1-9, a-g = 10-16
    return [vals[i * n2:(i + 1) * n2] for i in range(n2)]

def valid(grid, sol):
    n2 = len(grid); n = int(round(n2 ** 0.5))
    if sol is None: return False
    full = set(range(1, n2 + 1))
    for i in range(n2):
        if set(sol[i]) != full or {sol[r][i] for r in range(n2)} != full: return False
    for br in range(n):
        for bc in range(n):
            if {sol[br * n + i][bc * n + j] for i in range(n) for j in range(n)} != full: return False
    return all(grid[r][c] in (0, sol[r][c]) for r in range(n2) for c in range(n2))

def show(sol):
    return "".join(format(v, "x") for row in sol for v in row) if sol else None

for line in sys.stdin.read().split("\n"):
    parts = line.split()
    if not parts: continue
    cmd = parts[0]
    if cmd == "cover":
        rows = {"A": [1, 4, 7], "B": [1, 4], "C": [4, 5, 7], "D": [3, 5, 6], "E": [2, 3, 6, 7], "F": [2, 7]}
        print(solve_exact_cover(range(1, 8), rows))
        print(solve_exact_cover(range(1, 8), rows, limit=5))
        print(solve_exact_cover(["x", "y", "z"], {"r1": ["x"], "r2": ["y"]}))
        print(solve_exact_cover(["a", "b"], {"p": ["a", "b"], "q": ["a"], "s": ["b"]}, limit=10))
        tiles = {f"h{r}{c}": [(r, c), (r, c + 1)] for r in range(2) for c in range(3)}
        tiles.update({f"v{c}": [(0, c), (1, c)] for c in range(4)})
        print("2x4 domino tilings:", len(solve_exact_cover([(r, c) for r in range(2) for c in range(4)], tiles, limit=100)))
    elif cmd == "sudoku":
        g = parse(parts[1])
        sol = solve_sudoku(g)
        if len(g) != 9:                        # these may have several solutions: report validity only
            print(f"{len(g)}x{len(g)} givens", sum(v > 0 for row in g for v in row), "valid", valid(g, sol))
        else:
            print(show(sol), valid(g, sol))
    elif cmd == "count":
        print(count_sudoku_solutions(parse(parts[1]), limit=int(parts[2])))
```

## Tests
=== sample
cover
sudoku 1.....2..3.....4
sudoku 53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79
---
[['B', 'D', 'F']]
[['B', 'D', 'F']]
[]
[['p'], ['q', 's']]
2x4 domino tilings: 5
4x4 givens 4 valid True
534678912672195348198342567859761423426853791713924856961537284287419635345286179 True
=== hidden
sudoku 8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4..
sudoku ..53.....8......2..7..1.5..4....53...1..7...6..32...8..6.5....9..4....3......97..
sudoku 11..................................................................................
count ..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3.. 5
count ........................................................................2........ 3
---
812753649943682175675491283154237896369845721287169534521974368438526917796318452 True
145327698839654127672918543496185372218473956753296481367542819984761235521839764 True
None False
1
3
=== hidden
sudoku 4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......
sudoku .......1.4.........2...........5.4.7..8...3....1.9....3..4..2...5.1........8.6...
---
417369825632158947958724316825437169791586432346912758289643571573291684164875293 True
693784512487512936125963874932651487568247391741398625319475268856129743274836159 True
=== hidden
sudoku ..8a.3.41f.52..df.5.a..8.cd2.7.bcg..e1.5..b..9....4....2.9a85f1..9b.3...f........7............f...eg1f5a7.3..896.f..698b.2ge.4.3g.c...1...8..........a....4.7...6..58.37e..fc.d4.b78.d....59f......7.2e18..3....b8..74dg.a.6.e2c..6.98.32.c1gd.7......a.4d7.3...
---
16x16 givens 116 valid True

## Hints
- Use Knuth's dict-of-sets formulation (Ali Assaf's version is about 30 lines). `X[col]` is the set of rows covering `col`, and `Y[row]` is the list of columns in `row`.
- `select(X, Y, r)`: for every column `j` of row `r`, for every row `i` in `X[j]`, remove `i` from all the *other* columns of `i`, then pop `X[j]` (saving it). `deselect` undoes this in reverse order.
- Search: if `X` is empty, record a solution. Otherwise pick `c = min(X, key=lambda c: (len(X[c]), c))` (with sortable column ids), then try `for r in sorted(X[c])`.
- Sudoku: put each given into the partial solution by `select`ing its row first. If the given's row is no longer available (a conflict), return None.
- `limit` lets `count_sudoku_solutions` stop at 2, which proves uniqueness without enumerating every solution.

## Solution
```python
def _select(X, Y, r):
    cols = []
    for j in Y[r]:
        for i in X[j]:
            for k in Y[i]:
                if k != j:
                    X[k].remove(i)
        cols.append(X.pop(j))
    return cols


def _deselect(X, Y, r, cols):
    for j in reversed(Y[r]):
        X[j] = cols.pop()
        for i in X[j]:
            for k in Y[i]:
                if k != j:
                    X[k].add(i)


def _search(X, Y, partial, out, limit):
    if not X:
        out.append(sorted(partial))
        return len(out) >= limit
    c = min(X, key=lambda col: (len(X[col]), col))     # MRV heuristic: fewest candidates first
    for r in sorted(X[c]):
        partial.append(r)
        cols = _select(X, Y, r)
        if _search(X, Y, partial, out, limit):
            _deselect(X, Y, r, cols)
            partial.pop()
            return True
        _deselect(X, Y, r, cols)
        partial.pop()
    return False


def _build(columns, rows):
    Y = {r: list(cs) for r, cs in rows.items()}
    X = {c: set() for c in columns}
    for r, cs in Y.items():
        for c in cs:
            X[c].add(r)
    return X, Y


def solve_exact_cover(columns, rows, limit=1):
    X, Y = _build(columns, rows)
    if any(not s for s in X.values()):
        return []
    out = []
    _search(X, Y, [], out, limit)
    return out


def _sudoku_model(grid):
    n2 = len(grid)
    n = int(round(n2 ** 0.5))
    cols = ([("cell", r, c) for r in range(n2) for c in range(n2)] +
            [("row", r, v) for r in range(n2) for v in range(1, n2 + 1)] +
            [("col", c, v) for c in range(n2) for v in range(1, n2 + 1)] +
            [("box", b, v) for b in range(n2) for v in range(1, n2 + 1)])
    rows = {}
    for r in range(n2):
        for c in range(n2):
            b = (r // n) * n + c // n
            for v in range(1, n2 + 1):
                rows[(r, c, v)] = [("cell", r, c), ("row", r, v), ("col", c, v), ("box", b, v)]
    return cols, rows


def _solve(grid, limit):
    cols, rows = _sudoku_model(grid)
    X, Y = _build(cols, rows)
    givens = []
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            if v:
                if (r, c, v) not in X.get(("cell", r, c), ()):        # conflicting givens
                    return []
                _select(X, Y, (r, c, v))
                givens.append((r, c, v))
    out = []
    _search(X, Y, list(givens), out, limit)
    return out


def solve_sudoku(grid):
    sols = _solve(grid, 1)
    if not sols:
        return None
    n2 = len(grid)
    result = [[0] * n2 for _ in range(n2)]
    for r, c, v in sols[0]:
        result[r][c] = v
    return result


def count_sudoku_solutions(grid, limit=2):
    return len(_solve(grid, limit))
```

- **One algorithm, many puzzles**: once a problem is phrased as "cover every constraint exactly once", Algorithm X solves it. Sudoku has 4 constraint families (cell, row-value, column-value, box-value), giving 324 columns for 9×9 and 1,024 for 16×16.
- **The MRV heuristic** (branch on the column with the fewest remaining rows) is what makes it fast: forced moves are taken first and dead ends are detected immediately. The "hardest" 9×9 puzzles take a few hundred nodes instead of the millions of naive backtracking.
- **Reversible updates**: `_select` and `_deselect` remove and restore rows in exactly mirrored order. That's the dict-of-sets equivalent of Knuth's *Dancing Links*, with no copying of the matrix at each level.
- **Givens are pre-selected rows**, and a given whose row has already been eliminated proves the puzzle inconsistent, so it returns None with no search.
- **Limited enumeration** (`limit=2`) is how puzzle generators verify uniqueness.
