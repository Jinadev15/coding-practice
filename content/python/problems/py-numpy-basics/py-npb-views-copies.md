---
id: py-npb-views-copies
title: Views vs Copies
difficulty: Medium
order: 5
tags: numpy, views, copies, in-place, shares_memory, slicing
time_limit: 3
---
## Statement
Some functions must change the caller's array **in place**, some must return a **view** (sharing memory), and some must leave the input **untouched**. The driver checks all three with `np.shares_memory` and by comparing the caller's array before and after.

```python
def zero_border(a):
    """In place: set the outermost rows and columns of the 2-D array a to 0. Return None."""

def even_rows(a):
    """Return a VIEW of rows 0, 2, 4, ... of the 2-D array a (writing to it must change a)."""

def centered(a):
    """Return a NEW array a - column means (2-D float). The input must not change."""

def rotate_left(a, k):
    """In place: rotate the 1-D array a left by k positions (0 <= k, k may exceed len(a)).
    [1, 2, 3, 4, 5] with k = 2 becomes [3, 4, 5, 1, 2]. Return None."""
```

**Input:** one call per line as a Python tuple `("name", args)`. A line `gen N SEED` runs a large check.

**Output:** for each call the driver prints the relevant array(s) (`shape v1 v2 ...`, values to 2 decimals) and a memory/mutation check.

## Starter
```python
import numpy as np

def zero_border(a):
    a = a.copy()
    a[0, :] = a[-1, :] = 0
    a[:, 0] = a[:, -1] = 0

def even_rows(a):
    return a[np.arange(0, a.shape[0], 2)]

def centered(a):
    a -= a.mean(axis=0)
    return a

def rotate_left(a, k):
    a = np.roll(a, -k)
```

## Driver
```python
import ast
import sys
import numpy as np

def show(a):
    a = np.asarray(a, dtype=float)
    shape = "x".join(map(str, a.shape)) or "scalar"
    return (shape + " " + " ".join(f"{v:.2f}" for v in a.ravel().tolist())).rstrip()

def check_all(a, fresh):
    out = []
    b = a.copy(); r = zero_border(b); out.append(("zero_border", show(b), "returned_none:", r is None))
    b = a.copy(); v = even_rows(b); sm = bool(np.shares_memory(v, b))
    if v.size:
        v[...] = -1
    out.append(("even_rows", "view:", sm, "after_write:", show(b)))
    b = a.copy(); orig = b.copy(); c = centered(b)
    out.append(("centered", show(c), "input_unchanged:", bool(np.array_equal(b, orig)), "new:", not np.shares_memory(c, b)))
    return out

for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, n, seed = line.split()
        n, rng = int(n), np.random.default_rng(int(seed))
        a = rng.integers(0, 10, size=(n, n)).astype(float)
        b = a.copy(); zero_border(b)
        v = even_rows(b)
        c = centered(a)
        x = np.arange(n * n, dtype=float)
        rotate_left(x, n * n + 12345)
        print("gen", f"{b.sum():.1f}", bool(np.shares_memory(v, b)), v.shape, f"{np.abs(c.mean(axis=0)).max():.6f}",
              x[:3].tolist(), x[-3:].tolist())
        continue
    name, args = ast.literal_eval(line)
    if name == "rotate_left":
        x = np.array(args[0], dtype=float)
        r = rotate_left(x, args[1])
        print("rotate_left", show(x), "returned_none:", r is None)
        continue
    a = np.array(args[0], dtype=float)
    for row in check_all(a, args):
        if row[0] == name:
            print(*row)
```

## Tests
=== sample
("zero_border", ([[1, 2, 3], [4, 5, 6], [7, 8, 9]],))
("even_rows", ([[1, 2], [3, 4], [5, 6]],))
("centered", ([[1, 10], [3, 30]],))
("rotate_left", ([1, 2, 3, 4, 5], 2))
---
zero_border 3x3 0.00 0.00 0.00 0.00 5.00 0.00 0.00 0.00 0.00 returned_none: True
even_rows view: True after_write: 3x2 -1.00 -1.00 3.00 4.00 -1.00 -1.00
centered 2x2 -1.00 -10.00 1.00 10.00 input_unchanged: True new: True
rotate_left 5 3.00 4.00 5.00 1.00 2.00 returned_none: True
=== hidden
("zero_border", ([[5]],))
("zero_border", ([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]],))
("even_rows", ([[1, 2, 3]],))
("even_rows", ([[1], [2], [3], [4], [5]],))
("centered", ([[2.5]],))
("centered", ([[1, 2], [2, 4], [3, 9]],))
("rotate_left", ([1, 2, 3], 0))
("rotate_left", ([1, 2, 3], 3))
("rotate_left", ([1, 2, 3], 7))
("rotate_left", ([9], 4))
("rotate_left", ([1, 2, 3, 4, 5, 6], 4))
---
zero_border 1x1 0.00 returned_none: True
zero_border 4x4 0.00 0.00 0.00 0.00 0.00 6.00 7.00 0.00 0.00 10.00 11.00 0.00 0.00 0.00 0.00 0.00 returned_none: True
even_rows view: True after_write: 1x3 -1.00 -1.00 -1.00
even_rows view: True after_write: 5x1 -1.00 2.00 -1.00 4.00 -1.00
centered 1x1 0.00 input_unchanged: True new: True
centered 3x2 -1.00 -3.00 0.00 -1.00 1.00 4.00 input_unchanged: True new: True
rotate_left 3 1.00 2.00 3.00 returned_none: True
rotate_left 3 1.00 2.00 3.00 returned_none: True
rotate_left 3 2.00 3.00 1.00 returned_none: True
rotate_left 1 9.00 returned_none: True
rotate_left 6 5.00 6.00 1.00 2.00 3.00 4.00 returned_none: True
=== hidden
gen 2000 5
---
gen 17967181.0 True (1000, 2000) 0.000000 [12345.0, 12346.0, 12347.0] [12342.0, 12343.0, 12344.0]

## Hints
- Inside a function, `a = something` rebinds the local name only. `a[...] = something` or `a[:] = something` writes into the caller's array.
- A slice with a step (`a[::2]`) is still a view. An index *array* (`a[[0, 2, 4]]`) is always a copy.
- For the rotation, build the rotated values first (for example with `np.concatenate`), then assign them with `a[:] = ...`. Don't forget `k % n`.

## Solution
**Where memory is shared.**

| expression | result |
|---|---|
| `a[0, :]`, `a[::2]`, `a.T`, `a.reshape(...)` | **view** (new shape/strides over the same buffer) |
| `a[[0, 2]]`, `a[mask]` | **copy** |
| `a - m` | new array |
| `a -= m` | modifies `a` in place |

- **`zero_border`**: slice assignment (`a[0, :] = 0`) writes through the view into the caller's buffer. The starter's `a = a.copy()` rebinds the *local name* to a new array, so the caller never sees the change.
- **`even_rows`**: `a[::2]` changes only the row stride (every other row), so it is a view. `a[np.arange(0, n, 2)]` selects the same rows, but fancy indexing always copies, so writes to it are lost.
- **`centered`**: `a -= ...` is an in-place ufunc and would corrupt the caller's data. `a - ...` allocates a fresh result.
- **`rotate_left`**: `np.roll` returns a new array, and assigning it to `a` only rebinds the local name. Writing `a[:] = ...` copies the values into the existing buffer. The right-hand side is fully built *before* the write, which matters: something like `a[:n-k], a[n-k:] = a[k:], a[:k]` reads from views of `a` while it overwrites `a`, which corrupts the data. Reduce `k` modulo `n` first.

Complexity: O(size) for each function. `even_rows` is O(1), because a view copies no data.

```python
import numpy as np

def zero_border(a):
    a[0, :] = 0          # basic slices are views: assignment writes into the caller's memory
    a[-1, :] = 0
    a[:, 0] = 0
    a[:, -1] = 0

def even_rows(a):
    return a[::2]        # a step slice is still a view (it only changes the strides)

def centered(a):
    return a - a.mean(axis=0)   # the binary operator allocates a new array

def rotate_left(a, k):
    n = a.size
    if n == 0:
        return
    k %= n
    a[:] = np.concatenate((a[k:], a[:k]))   # build the new order, then write it into the SAME buffer
```
