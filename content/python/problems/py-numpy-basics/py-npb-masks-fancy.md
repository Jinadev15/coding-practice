---
id: py-npb-masks-fancy
title: Boolean Masking and Fancy Indexing
difficulty: Easy
order: 3
tags: numpy, boolean masks, fancy indexing, argsort, lookup tables
time_limit: 3
---
## Statement
A warehouse stores its inventory as a 2-D float array `items` with one row per item and the columns `[id, price, stock]`. Implement these with masks and integer-array ("fancy") indexing, with **no Python loops over elements**:

```python
def in_band(x, lo, hi):
    """Number of elements with lo <= x < hi (x is a 1-D array)."""

def restock_list(items, threshold):
    """Rows whose stock < threshold, ordered by stock ascending; ties keep their original row order.
    Return the selected rows (a 2-D array, possibly with 0 rows)."""

def top_k(x, k):
    """Indices of the k largest values of x, largest first; equal values -> smaller index first.
    Return an int array of length min(k, len(x))."""

def relabel(labels, mapping):
    """labels: int array (any shape) with values in [0, len(mapping)). mapping: list of ints.
    Return the array with each value v replaced by mapping[v] (same shape)."""
```

**Input:** one call per line as a Python tuple `("name", args)`. A line `gen N SEED` runs a large check with N = 10⁶ values.

**Output:** arrays print as `dtype shape v1 v2 ...` (shape joined by `x`, floats to 2 decimals, row-major). `in_band` prints the count.

## Starter
```python
import numpy as np

def in_band(x, lo, hi):
    return int(((x >= lo) and (x < hi)).sum())

def restock_list(items, threshold):
    return items[items[:, 2] < threshold]

def top_k(x, k):
    return np.argsort(x)[-k:]

def relabel(labels, mapping):
    out = labels.copy()
    for i, m in enumerate(mapping):
        out[labels == i] = m
    return out
```

## Driver
```python
import ast
import sys
import numpy as np

def show(a):
    a = np.asarray(a)
    shape = "x".join(map(str, a.shape)) or "scalar"
    if a.dtype.kind == "f":
        vals = " ".join(f"{v:.2f}" for v in a.ravel().tolist())
    else:
        vals = " ".join(str(int(v)) for v in a.ravel().tolist())
    return f"{a.dtype.kind} {shape} {vals}".rstrip()

for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, n, seed = line.split()
        n, rng = int(n), np.random.default_rng(int(seed))
        x = rng.integers(0, 1000, n).astype(float)
        items = np.c_[np.arange(n), rng.uniform(1, 100, n).round(2), rng.integers(0, 500, n)].astype(float)
        rs = restock_list(items, 20)
        tk = top_k(x, 50)
        lab = rng.integers(0, 256, size=(1000, n // 1000))
        mp = rng.permutation(256).tolist()
        rl = relabel(lab, mp)
        print("gen", in_band(x, 100, 250), rs.shape, int(rs[:, 0][:5].sum()), int(rs[:, 0][-5:].sum()),
              tk.tolist()[:10], int(rl.sum()), int(rl[17, 42]))
        continue
    name, args = ast.literal_eval(line)
    if name == "in_band":
        print(in_band(np.array(args[0], dtype=float), args[1], args[2]))
    elif name == "restock_list":
        print(show(restock_list(np.array(args[0], dtype=float).reshape(-1, 3), args[1])))
    elif name == "top_k":
        print(show(top_k(np.array(args[0], dtype=float), args[1])))
    else:
        print(show(relabel(np.array(args[0], dtype=np.int64), args[1])))
```

## Tests
=== sample
("in_band", ([1, 5, 10, 15, 20], 5, 15))
("restock_list", ([[1, 9.5, 30], [2, 3.25, 4], [3, 12.0, 4], [4, 1.0, 50], [5, 7.0, 2]], 10))
("top_k", ([3, 9, 1, 9, 4], 3))
("relabel", ([[0, 1], [2, 1]], [10, 20, 30]))
---
2
f 3x3 5.00 7.00 2.00 2.00 3.25 4.00 3.00 12.00 4.00
i 3 1 3 4
i 2x2 10 20 30 20
=== hidden
("in_band", ([], 0, 1))
("in_band", ([1, 2, 3], 3, 3))
("in_band", ([-5, -1, 0, 0.5], -1, 0.5))
("restock_list", ([[1, 1, 100]], 10))
("restock_list", ([[7, 2, 0], [8, 3, 0], [9, 1, 0]], 1))
("restock_list", ([[1, 5, 3], [2, 5, 1], [3, 5, 2], [4, 5, 1]], 3))
("top_k", ([5, 5, 5, 5], 2))
("top_k", ([1, 2], 5))
("top_k", ([-1, -3, -2, 0], 1))
("top_k", ([2, 8, 8, 1, 8], 4))
("relabel", ([3, 3, 0], [1, 2, 3, 0]))
("relabel", ([[[1]], [[0]]], [5, 6]))
("relabel", ([0, 1, 2], [1, 2, 0]))
---
0
0
2
f 0x3
f 3x3 7.00 2.00 0.00 8.00 3.00 0.00 9.00 1.00 0.00
f 3x3 2.00 5.00 1.00 4.00 5.00 1.00 3.00 5.00 2.00
i 2 0 1
i 2 1 0
i 1 3
i 4 1 2 4 0
i 3 0 0 1
i 2x1x1 6 5
i 3 1 2 0
=== hidden
gen 1000000 11
---
gen 149965 (40064, 3) 6338 4991819 [172, 1844, 2358, 2528, 3820, 4481, 4589, 5160, 5584, 6522] 127636409 7

## Hints
- Build each condition separately, `(x >= lo)` and `(x < hi)`, then combine them with `&`.
- `np.argsort` returns indices. Pass `kind="stable"` so ties keep their order, and sort `-x` to get descending order.
- Turn `mapping` into an array `lut`. What does `lut[labels]` compute?

## Solution
- **Masks combine with `&`, `|`, `~`.** Python's `and` asks for the truth value of a whole array and raises `ValueError: The truth value of an array ... is ambiguous`. Each comparison needs parentheses because `&` binds tighter than `<`. `np.count_nonzero(mask)` counts the `True` values.
- **Filter, then reorder.** `items[mask]` keeps the matching rows. `np.argsort(..., kind="stable")` returns the permutation that sorts them, and indexing with that integer array applies it. The default quicksort is *not* stable, so equal stocks could be shuffled.
- **Descending order with stable ties.** Sorting `-x` stably puts the largest first and keeps equal values in index order. Reversing an ascending argsort (the starter) breaks the tie rule and also returns the list in the wrong direction.
- **Lookup tables.** `lut[labels]` replaces every element by `lut[element]` in one gather. It works for any shape and costs O(size), whereas the starter makes one full pass per mapping entry, and its sequential in-place updates can relabel values twice.

Complexity: `in_band` and `relabel` are O(n); `restock_list` and `top_k` are O(n log n). (`np.argpartition` finds the top k in O(n), but you then still have to sort those k.)

```python
import numpy as np

def in_band(x, lo, hi):
    return int(np.count_nonzero((x >= lo) & (x < hi)))     # & with parentheses, never `and`

def restock_list(items, threshold):
    low = items[items[:, 2] < threshold]                     # boolean mask selects rows (a copy)
    order = np.argsort(low[:, 2], kind="stable")             # stable: ties keep row order
    return low[order]                                        # fancy indexing reorders rows

def top_k(x, k):
    order = np.argsort(-x, kind="stable")                    # descending by value, ties by index
    return order[:k]

def relabel(labels, mapping):
    lut = np.asarray(mapping)                                # lookup table
    return lut[labels]                                       # one gather, any shape
```
