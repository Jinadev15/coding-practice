---
id: py-sudoku-and-operators
title: "Backtracking: Sudoku Solver and Expression Operators"
difficulty: Hard
order: 1
tags: backtracking, constraint propagation, bitmasks, MRV heuristic, pruning
time_limit: 4
---
## Statement
Two classic backtracking searches where **pruning** is what makes them fast enough.

```python
def solve_sudoku(board):
    """board: list of 9 strings of 9 chars, digits or '.'. Return the solved board as 9 strings.
    Puzzles have exactly one solution. Includes very hard puzzles: use bitmasks for row/column/box
    candidates and always branch on the empty cell with the FEWEST candidates."""

def add_operators(digits, target):
    """Insert '+', '-' or '*' between the digits (or nothing, concatenating) so the expression
    evaluates to target with normal precedence. Operands can't have leading zeros ("05"),
    though "0" alone is fine. Return all expressions, sorted."""
```

Test lines are `(function_name, args)` literals.

## Starter
```python
def solve_sudoku(board):
    g = [list(r) for r in board]
    def ok(r, c, ch):
        for i in range(9):
            if g[r][i] == ch or g[i][c] == ch:
                return False
            if g[3 * (r // 3) + i // 3][3 * (c // 3) + i % 3] == ch:
                return False
        return True
    def go(k):
        if k == 81:
            return True
        r, c = divmod(k, 9)
        if g[r][c] != ".":
            return go(k + 1)
        for ch in "123456789":
            if ok(r, c, ch):
                g[r][c] = ch
                if go(k + 1):
                    return True
                g[r][c] = "."
        return False
    go(0)
    return ["".join(r) for r in g]

def add_operators(digits, target):
    return []
```

## Driver
```python
import ast
import sys

for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    name, args = ast.literal_eval(line)
    if name == "solve_sudoku":
        res = solve_sudoku(args[0])
        ok = len(res) == 9 and all(sorted(r) == list("123456789") for r in res)
        ok = ok and all(sorted(res[r][c] for r in range(9)) == list("123456789") for c in range(9))
        ok = ok and all(sorted(res[3 * br + i // 3][3 * bc + i % 3] for i in range(9)) == list("123456789")
                        for br in range(3) for bc in range(3))
        ok = ok and all(args[0][r][c] in (".", res[r][c]) for r in range(9) for c in range(9))
        print("sudoku valid:", ok, "| first rows:", res[0], res[1])
    else:
        r = add_operators(*args)
        print("add_operators", args, "->", len(r), r[:8])
```

## Tests
=== sample
("solve_sudoku", (["53..7....", "6..195...", ".98....6.", "8...6...3", "4..8.3..1", "7...2...6", ".6....28.", "...419..5", "....8..79"],))
("add_operators", ("123", 6))
("add_operators", ("232", 8))
---
sudoku valid: True | first rows: 534678912 672195348
add_operators ('123', 6) -> 2 ['1*2*3', '1+2+3']
add_operators ('232', 8) -> 2 ['2*3+2', '2+3*2']
=== hidden
("add_operators", ("105", 5))
("add_operators", ("00", 0))
("add_operators", ("3456237490", 9191))
("add_operators", ("1000000009", 9))
("add_operators", ("2147483648", -2147483648))
("add_operators", ("123456789", 45))
---
add_operators ('105', 5) -> 2 ['1*0+5', '10-5']
add_operators ('00', 0) -> 3 ['0*0', '0+0', '0-0']
add_operators ('3456237490', 9191) -> 0 []
add_operators ('1000000009', 9) -> 3280 ['1*0*0*0*0*0*0*0*0+9', '1*0*0*0*0*0*0*0+0+9', '1*0*0*0*0*0*0*0-0+9', '1*0*0*0*0*0*0+0*0+9', '1*0*0*0*0*0*0+0+0+9', '1*0*0*0*0*0*0+0-0+9', '1*0*0*0*0*0*0-0*0+9', '1*0*0*0*0*0*0-0+0+9']
add_operators ('2147483648', -2147483648) -> 0 []
add_operators ('123456789', 45) -> 121 ['1*2*3*4*5-6-78+9', '1*2*3*4+5+6-7+8+9', '1*2*3+4+5+6+7+8+9', '1*2*3+4+5-6*7+8*9', '1*2*3+4-5*6+7*8+9', '1*2*3+4-5*6-7+8*9', '1*2*3-4*5+6*7+8+9', '1*2*3-4*5-6+7*8+9']
=== hidden
("solve_sudoku", (["8........", "..36.....", ".7..9.2..", ".5...7...", "....457..", "...1...3.", "..1....68", "..85...1.", ".9....4.."],))
("solve_sudoku", (['4.....8.5', '.3.......', '...7.....', '.2.....6.', '....8.4..', '....1....', '...6.3.7.', '5..2.....', '1.4......'],))
---
sudoku valid: True | first rows: 812753649 943682175
sudoku valid: True | first rows: 417369825 632158947
=== hidden
("solve_sudoku", (["1....7.9.", ".3..2...8", "..96..5..", "..53..9..", ".1..8...2", "6....4...", "3......1.", ".4......7", "..7...3.."],))
---
sudoku valid: True | first rows: 162857493 534129678

## Hints
- **Sudoku**: keep three lists of 9-bit masks of used digits (`rows`, `cols`, `boxes`). The candidates for (r, c) are `~(rows[r] | cols[c] | boxes[b]) & 0x1FF`. Pick the empty cell with the smallest `candidates.bit_count()` (if it's 0, backtrack immediately), try each candidate bit, and undo afterwards.
- **add_operators**: recurse with `(pos, expr, value, last)`, where `last` is the most recent multiplicative term. For `*`, the new value is `value - last + last * operand`, which undoes the last term and re-applies it multiplied. A leading `'0'` may only form the operand `"0"`.

## Solution
```python
def solve_sudoku(board):
    g = [list(r) for r in board]
    rows, cols, boxes = [0] * 9, [0] * 9, [0] * 9
    for r in range(9):
        for c in range(9):
            if g[r][c] != ".":
                bit = 1 << (int(g[r][c]) - 1)
                rows[r] |= bit; cols[c] |= bit; boxes[r // 3 * 3 + c // 3] |= bit

    def go():
        best, best_mask, best_cnt = None, 0, 10
        for r in range(9):                           # MRV: find the most constrained empty cell
            for c in range(9):
                if g[r][c] == ".":
                    m = ~(rows[r] | cols[c] | boxes[r // 3 * 3 + c // 3]) & 0x1FF
                    cnt = m.bit_count()
                    if cnt < best_cnt:
                        best, best_mask, best_cnt = (r, c), m, cnt
                        if cnt == 0:
                            return False             # dead end: prune immediately
        if best is None:
            return True                              # no empty cells left
        r, c = best
        b = r // 3 * 3 + c // 3
        m = best_mask
        while m:
            bit = m & -m
            m ^= bit
            rows[r] |= bit; cols[c] |= bit; boxes[b] |= bit
            g[r][c] = str(bit.bit_length())
            if go():
                return True
            rows[r] ^= bit; cols[c] ^= bit; boxes[b] ^= bit
        g[r][c] = "."
        return False

    go()
    return ["".join(row) for row in g]

def add_operators(digits, target):
    out = []
    n = len(digits)

    def go(pos, expr, value, last):
        if pos == n:
            if value == target:
                out.append(expr)
            return
        for end in range(pos + 1, n + 1):
            s = digits[pos:end]
            if len(s) > 1 and s[0] == "0":
                break                                 # no multi-digit operands with a leading zero
            x = int(s)
            if pos == 0:
                go(end, s, x, x)
            else:
                go(end, expr + "+" + s, value + x, x)
                go(end, expr + "-" + s, value - x, -x)
                go(end, expr + "*" + s, value - last + last * x, last * x)

    go(0, "", 0, 0)
    return sorted(out)
```

- **Sudoku** uses two ingredients that make hard puzzles fast. *Bitmask candidate sets* give O(1) feasibility checks. The *minimum-remaining-values* heuristic always branches on the most constrained cell, which forces long chains of single-candidate cells and detects contradictions (a cell with 0 candidates) immediately. The naive left-to-right search can take millions of steps on "platinum blonde"-style puzzles, while MRV typically needs a few hundred.
- **add_operators** handles precedence without an expression parser. Tracking the last multiplicative term lets `*` retroactively rebind it: `value − last + last·x`. The leading-zero rule prunes with `break`, because every longer operand starting with '0' is invalid too.
