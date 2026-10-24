---
id: py-monotonic-suite
title: "Monotonic Stack Suite: Maximal Rectangle, Subarray Minimums, Expression Evaluator"
difficulty: Hard
order: 1
tags: monotonic stack, histogram, contribution technique, shunting-yard
---
## Statement
Implement three stack algorithms.

```python
def maximal_rectangle(grid):
    """grid: list of strings of '0'/'1' (an occupancy map; '1' = free cell).
    Area of the largest axis-aligned rectangle of '1's. O(R*C)."""

def sum_subarray_mins(a):
    """Sum of min(sub) over all non-empty contiguous subarrays, modulo 1_000_000_007. O(n)."""

def evaluate(expr):
    """Evaluate an integer expression with + - * / ( ) and unary minus, spaces allowed.
    / is integer division truncating toward zero (like C). * and / bind tighter than + and -,
    all binary operators are left-associative. No eval()."""
```

Test lines are `(function_name, args)` literals or `gen NAME SEED N`.

## Starter
```python
def maximal_rectangle(grid):
    R = len(grid); C = len(grid[0]) if R else 0
    best = 0
    for r1 in range(R):
        for c1 in range(C):
            for r2 in range(r1, R):
                for c2 in range(c1, C):
                    if all(grid[r][c] == "1" for r in range(r1, r2 + 1) for c in range(c1, c2 + 1)):
                        best = max(best, (r2 - r1 + 1) * (c2 - c1 + 1))
    return best

def sum_subarray_mins(a):
    return sum(min(a[i:j]) for i in range(len(a)) for j in range(i + 1, len(a) + 1)) % 1_000_000_007

def evaluate(expr):
    return 0
```

## Driver
```python
import ast
import random
import sys

FUNCS = {f.__name__: f for f in (maximal_rectangle, sum_subarray_mins, evaluate)}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        if name == "maximal_rectangle":
            g = ["".join("1" if rng.random() < 0.93 else "0" for _ in range(n)) for _ in range(n)]
            print(name, n, maximal_rectangle(g))
        elif name == "sum_subarray_mins":
            a = [rng.randrange(1, 30000) for _ in range(n)]
            print(name, n, sum_subarray_mins(a), sum_subarray_mins(sorted(a)), sum_subarray_mins([5] * n))
        else:
            parts = [str(rng.randrange(1, 100))]
            for _ in range(n):
                parts.append(rng.choice("+-*"))
                parts.append(str(rng.randrange(1, 100)))
            e = "(" + " ".join(parts) + ") / 7 - -(3)"
            print(name, n, evaluate(e))
        continue
    name, args = ast.literal_eval(line)
    print(name, "->", FUNCS[name](*args))
```

## Tests
=== sample
("maximal_rectangle", (["10100", "10111", "11111", "10010"],))
("sum_subarray_mins", ([3, 1, 2, 4],))
("evaluate", ("1 + 2 * 3",))
("evaluate", ("(1 + 2) * 3 - 8 / 3",))
---
maximal_rectangle -> 6
sum_subarray_mins -> 17
evaluate -> 7
evaluate -> 7
=== hidden
("maximal_rectangle", ([],))
("maximal_rectangle", (["0"],))
("maximal_rectangle", (["1"],))
("maximal_rectangle", (["111", "111"],))
("maximal_rectangle", (["0110", "1111", "1111", "0110"],))
("sum_subarray_mins", ([],))
("sum_subarray_mins", ([11, 81, 94, 43, 3],))
("sum_subarray_mins", ([2, 2, 2],))
("evaluate", ("42",))
("evaluate", ("-7 / 2",))
("evaluate", ("7 / -2",))
("evaluate", ("2 - 3 - 4",))
("evaluate", ("100 / 10 / 5",))
("evaluate", ("-(2 + 3) * -(4 - 6)",))
("evaluate", ("((((1))))",))
("evaluate", ("2*(3+4)*5-6/(1+2)",))
("evaluate", ("1 - -1",))
("evaluate", ("2 * -3 + 1",))
("evaluate", ("- - 4 * 2",))
("evaluate", ("-2 * 3 - -6 / 4",))
---
maximal_rectangle -> 0
maximal_rectangle -> 0
maximal_rectangle -> 1
maximal_rectangle -> 6
maximal_rectangle -> 8
sum_subarray_mins -> 0
sum_subarray_mins -> 444
sum_subarray_mins -> 12
evaluate -> 42
evaluate -> -3
evaluate -> -3
evaluate -> -5
evaluate -> 2
evaluate -> -10
evaluate -> 1
evaluate -> 68
evaluate -> 2
evaluate -> -5
evaluate -> 8
evaluate -> -5
=== hidden
gen maximal_rectangle 1 400
gen sum_subarray_mins 2 200000
gen evaluate 3 20000
---
maximal_rectangle 400 182
sum_subarray_mins 200000 701647128 298009014 499300
evaluate 20000 -5653572223252236

## Hints
- **Maximal rectangle**: for each row, maintain `heights[c]` (consecutive '1's ending at this row), then run largest-rectangle-in-histogram with an increasing stack and a 0 sentinel.
- **Subarray minimums**: element i is the minimum of `left[i] * right[i]` subarrays, where `left` is the distance to the previous **strictly smaller** element and `right` the distance to the next **smaller-or-equal** one. The asymmetry stops equal values being counted twice.
- **evaluate**: tokenise, then use two stacks (numbers and operators). Before pushing a binary operator, apply the stacked operators with **greater or equal** precedence (for left associativity). Treat a `-` as unary when it appears at the start, after `(`, or after another operator. Implement it as `0 - x` with the highest precedence, or push a `"neg"` operator.
- C-style division: `int(a / b)` loses precision for huge numbers. Use `q = abs(a) // abs(b)`, then negate it if the signs differ.

## Solution
```python
MOD = 1_000_000_007

def maximal_rectangle(grid):
    if not grid:
        return 0
    C = len(grid[0])
    heights = [0] * C
    best = 0
    for row in grid:
        for c, ch in enumerate(row):
            heights[c] = heights[c] + 1 if ch == "1" else 0
        st = []                                       # indices with increasing heights
        for i, h in enumerate(heights + [0]):
            while st and heights[st[-1]] >= h:
                height = heights[st.pop()]
                left = st[-1] + 1 if st else 0
                best = max(best, height * (i - left))
            st.append(i)
    return best

def sum_subarray_mins(a):
    n = len(a)
    left, right = [0] * n, [0] * n
    st = []
    for i in range(n):                                # previous strictly smaller
        while st and a[st[-1]] >= a[i]:
            st.pop()
        left[i] = i - st[-1] if st else i + 1
        st.append(i)
    st = []
    for i in range(n - 1, -1, -1):                    # next smaller-or-equal
        while st and a[st[-1]] > a[i]:
            st.pop()
        right[i] = st[-1] - i if st else n - i
        st.append(i)
    return sum(a[i] * left[i] * right[i] for i in range(n)) % MOD

def _cdiv(a, b):
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b > 0) else -q

PREC = {"+": 1, "-": 1, "*": 2, "/": 2, "neg": 3}

def evaluate(expr):
    nums, ops = [], []

    def apply():
        op = ops.pop()
        if op == "neg":
            nums.append(-nums.pop())
            return
        b, a = nums.pop(), nums.pop()
        nums.append(a + b if op == "+" else a - b if op == "-" else a * b if op == "*" else _cdiv(a, b))

    i, n = 0, len(expr)
    expect_operand = True                              # True at the start, after '(' and after an operator
    while i < n:
        ch = expr[i]
        if ch == " ":
            i += 1
            continue
        if ch.isdigit():
            j = i
            while j < n and expr[j].isdigit():
                j += 1
            nums.append(int(expr[i:j]))
            i = j
            expect_operand = False
            continue
        if ch == "(":
            ops.append("(")
            expect_operand = True
        elif ch == ")":
            while ops[-1] != "(":
                apply()
            ops.pop()
            expect_operand = False
        elif ch == "-" and expect_operand:
            ops.append("neg")                          # unary: right-associative, binds tightest
        else:
            while ops and ops[-1] != "(" and PREC[ops[-1]] >= PREC[ch]:
                apply()                                # includes pending unary minus (highest precedence)
            ops.append(ch)
            expect_operand = True
        i += 1
    while ops:
        apply()
    return nums[0]
```

- **Maximal rectangle** reduces a 2-D problem to R histogram problems. Each is O(C) with the increasing stack, because every column index is pushed and popped once per row. On an occupancy grid, this is how you find the largest free rectangular area for docking or placing a robot footprint.
- **Subarray minimums** uses the *contribution technique*. Instead of enumerating O(n²) subarrays, it asks how many subarrays have a[i] as their minimum. Two monotonic passes give the boundaries, and the strict/non-strict asymmetry assigns each subarray with tied minima to exactly one index.
- **The evaluator** is Dijkstra's two-stack (shunting-yard) method. Popping operators of greater or equal precedence before pushing makes the binary operators left-associative (`2 − 3 − 4 = −5`). Unary minus is a separate high-precedence prefix operator that only applies once its operand is complete.
