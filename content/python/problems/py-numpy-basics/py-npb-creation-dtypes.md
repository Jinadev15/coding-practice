---
id: py-npb-creation-dtypes
title: Array Creation and Dtypes
difficulty: Easy
order: 2
tags: numpy, array creation, dtypes, overflow, iinfo
time_limit: 3
---
## Statement
Four small array factories. Each one trains a different creation or dtype habit. Use NumPy only, with **no Python loops over elements**: the hidden tests build 3000 × 3000 arrays.

```python
def checkerboard(h, w):
    """int8 array of shape (h, w): 1 where (row + col) is even, else 0."""

def ramp(a, b, n):
    """n evenly spaced float64 values from a to b, BOTH ends included (n >= 2)."""

def blend(img1, img2):
    """Two uint8 arrays of the same shape -> uint8 array floor((p + q) / 2), computed without overflow."""

def smallest_uint(max_value):
    """Name (a str) of the smallest dtype among uint8, uint16, uint32, uint64 that can store
    max_value, where 0 <= max_value < 2**64."""
```

**Input:** one call per line, written as a Python tuple `("name", args)`. A line `gen N SEED` runs a large check on N × N arrays.

**Output:** arrays are printed as `dtype shape v1 v2 ...`, with the shape joined by `x` (for example `int8 2x3 1 0 1 0 1 0`), floats to 4 decimals, and the values in row-major order. `smallest_uint` prints the name.

Example: `ramp(0, 1, 5)` → `float64 5 0.0000 0.2500 0.5000 0.7500 1.0000`.

## Starter
```python
import numpy as np

def checkerboard(h, w):
    out = np.zeros((h, w), dtype=np.int8)
    for r in range(h):
        for c in range(w):
            if (r + c) % 2 == 0:
                out[r, c] = 1
    return out

def ramp(a, b, n):
    return np.arange(a, b, (b - a) / n)

def blend(img1, img2):
    return (img1 + img2) // 2

def smallest_uint(max_value):
    return "uint64"
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
        vals = " ".join(f"{v:.4f}" for v in a.ravel().tolist())
    else:
        vals = " ".join(str(int(v)) for v in a.ravel().tolist())
    return f"{a.dtype} {shape} {vals}".rstrip()

for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, n, seed = line.split()
        n, rng = int(n), np.random.default_rng(int(seed))
        cb = checkerboard(n, n + 1)
        p = rng.integers(0, 256, size=(n, n), dtype=np.uint8)
        q = rng.integers(0, 256, size=(n, n), dtype=np.uint8)
        bl = blend(p, q)
        r = ramp(-1.0, 1.0, n * n)
        print("gen", cb.dtype, cb.shape, int(cb.sum()), bl.dtype, int(bl.astype(np.int64).sum()),
              r.dtype, r.size, f"{float(r[0]):.4f}", f"{float(r[-1]):.4f}", f"{float(r.sum()):.4f}")
        continue
    name, args = ast.literal_eval(line)
    if name == "checkerboard":
        print(show(checkerboard(*args)))
    elif name == "ramp":
        print(show(ramp(*args)))
    elif name == "blend":
        print(show(blend(np.array(args[0], dtype=np.uint8), np.array(args[1], dtype=np.uint8))))
    else:
        print(smallest_uint(args[0]))
```

## Tests
=== sample
("checkerboard", (2, 3))
("ramp", (0, 1, 5))
("blend", ([[200, 10], [255, 0]], [[100, 20], [255, 1]]))
("smallest_uint", (255,))
("smallest_uint", (256,))
---
int8 2x3 1 0 1 0 1 0
float64 5 0.0000 0.2500 0.5000 0.7500 1.0000
uint8 2x2 150 15 255 0
uint8
uint16
=== hidden
("checkerboard", (1, 1))
("checkerboard", (3, 1))
("ramp", (5, -5, 3))
("ramp", (0, 0.3, 4))
("ramp", (1, 2, 2))
("blend", ([255, 255, 254], [255, 254, 254]))
("blend", ([0], [0]))
("smallest_uint", (0,))
("smallest_uint", (65535,))
("smallest_uint", (65536,))
("smallest_uint", (4294967295,))
("smallest_uint", (4294967296,))
("smallest_uint", (18446744073709551615,))
---
int8 1x1 1
int8 3x1 1 0 1
float64 3 5.0000 0.0000 -5.0000
float64 4 0.0000 0.1000 0.2000 0.3000
float64 2 1.0000 2.0000
uint8 3 255 254 254
uint8 1 0
uint8
uint16
uint32
uint32
uint64
uint64
=== hidden
gen 3000 7
---
gen int8 (3000, 3001) 4501500 uint8 1145282885 float64 9000000 -1.0000 1.0000 0.0000

## Hints
- Make a column vector `np.arange(h)[:, None]` and a row vector `np.arange(w)[None, :]`. What shape does their sum have?
- `np.arange` excludes the stop value. Which function lets you fix the number of points and include both ends?
- What is `np.uint8(200) + np.uint8(100)`? Convert to a wider type before adding, and use `np.iinfo` to look up type ranges.

## Solution
- **`checkerboard`**: a column of row numbers plus a row of column numbers broadcasts to the full `(h, w)` grid of `r + c`. Comparing gives a boolean array, and `.astype(np.int8)` gives the requested dtype. That's one vectorised pass instead of `h·w` interpreter steps (`np.indices((h, w)).sum(0)` works too).
- **`ramp`**: `np.arange(a, b, step)` is half-open and, with float steps, can produce one element too many or too few because of rounding. `np.linspace(a, b, n)` fixes the *count* and includes both ends, which is what you want whenever you know how many points you need.
- **`blend`**: `uint8 + uint8` stays `uint8` and wraps modulo 256 (`200 + 100 → 44`). Widen first (`uint16` holds up to 65535), add, halve, then narrow back. The result always fits because the average of two bytes is a byte. A neat alternative is `(p >> 1) + (q >> 1) + (p & q & 1)`.
- **`smallest_uint`**: `np.iinfo(dtype).max` gives the range of each integer type (255, 65535, 4294967295, 18446744073709551615). Note that `max_value` may be a big Python int, which compares exactly with these limits.

Complexity: O(h·w) for the arrays, O(1) for `smallest_uint`.

```python
import numpy as np

def checkerboard(h, w):
    r = np.arange(h)[:, None]                 # column vector of row numbers
    c = np.arange(w)[None, :]                 # row vector of column numbers
    return ((r + c) % 2 == 0).astype(np.int8)  # broadcasting builds the (h, w) grid

def ramp(a, b, n):
    return np.linspace(a, b, n, dtype=np.float64)   # inclusive of both ends

def blend(img1, img2):
    s = img1.astype(np.uint16) + img2.astype(np.uint16)   # 255 + 255 = 510 fits in uint16
    return (s // 2).astype(np.uint8)

def smallest_uint(max_value):
    for name in ("uint8", "uint16", "uint32", "uint64"):
        if max_value <= np.iinfo(name).max:
            return name
```
