# NumPy Fundamentals

NumPy is the foundation of scientific Python. Pandas, SciPy, scikit-learn, OpenCV, PyTorch interop, and ROS point-cloud and image messages all speak `ndarray`. An `ndarray` is a block of **contiguous, homogeneously typed memory** plus metadata (shape, strides, dtype), and its operations run as compiled C loops over that memory. That's why NumPy code is typically **10–100× faster** than equivalent Python loops: the loop runs once in C instead of n times in the interpreter. This lesson covers arrays, dtypes, shapes, indexing and slicing (and the crucial **view vs copy** distinction), universal functions and reductions.

## 1. Creating arrays

```python
import numpy as np

a = np.array([1, 2, 3])                  # from a list: dtype inferred (int64)
b = np.array([[1.0, 2.0], [3.0, 4.0]])   # 2-D, float64
np.zeros((3, 4))                         # 3x4 of 0.0
np.ones(5, dtype=np.int32)
np.full((2, 2), 7.5)
np.arange(0, 10, 2)                      # [0 2 4 6 8]  (half-open, like range)
np.linspace(0, 1, 5)                     # [0. 0.25 0.5 0.75 1.]  (inclusive, n points)
np.eye(3)                                # identity matrix
np.empty((1000, 1000))                   # uninitialised (fast; garbage values!)
rng = np.random.default_rng(42)          # the modern random API (seeded, reproducible)
rng.normal(0.0, 1.0, size=(3, 3))
```

## 2. The array's anatomy

```python
x = np.arange(12, dtype=np.float32).reshape(3, 4)
x.shape      # (3, 4)
x.ndim       # 2
x.size       # 12 elements
x.dtype      # float32
x.itemsize   # 4 bytes per element
x.nbytes     # 48
x.strides    # (16, 4): bytes to step to the next row / next column
```

**Strides** explain everything about views. A transpose, a slice, or a reshape of contiguous data just creates new metadata over the **same memory**.

## 3. dtypes

| dtype | Use | Pitfall |
|---|---|---|
| `float64` (default) | science, statistics | 8 bytes per value |
| `float32` | GPUs, deep learning, big images | ~7 significant digits |
| `int64` / `int32` | counts, indices | **silent overflow** wraps around (no exception!) |
| `uint8` | images (0–255) | `200 + 100` wraps to 44 |
| `bool` | masks | |
| `complex128` | FFTs, signals | |

```python
img = np.array([200, 250], dtype=np.uint8)
img + 100                         # array([ 44,  94], dtype=uint8): wrapped!
img.astype(np.int16) + 100        # [300, 350]: convert before arithmetic
np.clip(img.astype(np.int16) + 100, 0, 255).astype(np.uint8)   # saturating brightness: [255, 255]
```

> [!WARNING]
> NumPy integer arrays **overflow silently**, unlike Python ints. `np.int64` maxes out at about 9.2·10¹⁸, and `uint8` image maths wraps at 256. Convert to a wider type before summing or scaling.

## 4. Indexing and slicing

```python
m = np.arange(20).reshape(4, 5)
m[1, 3]          # one element (row 1, col 3): use m[r, c], not m[r][c]
m[1]             # row 1 → shape (5,)
m[:, 2]          # column 2 → shape (4,)
m[1:3, ::2]      # rows 1–2, every other column
m[-1]            # last row
m[..., 0]        # Ellipsis: "all leading axes", then index 0 on the last axis
```

### Views vs copies: the most important rule

> [!KEY]
> **Basic slicing returns a view** (the same memory). **Fancy indexing (integer arrays) and boolean masks return copies.**

```python
a = np.arange(10)
s = a[2:5]       # VIEW
s[0] = 99
a                # [ 0  1 99  3 ...]: the original changed!

t = a[[2, 3, 4]] # COPY (fancy indexing)
t[0] = -1        # a unchanged

safe = a[2:5].copy()          # explicit copy when you need independence
np.shares_memory(a, s)        # True: check when unsure
```

Views make NumPy fast (slicing a 1 GB array is free) and dangerous (functions that modify a slice modify the caller's data).

## 5. Boolean masks

```python
temps = np.array([21.5, 35.2, 18.9, 40.1, 25.0])
hot = temps > 30                 # array([False,  True, False,  True, False])
temps[hot]                       # [35.2, 40.1]
temps[(temps > 20) & (temps < 30)]   # use & | ~ with parentheses, not 'and'/'or'
temps[temps > 38] = 38           # clamp in place via a mask
np.count_nonzero(hot), hot.mean()    # 2, 0.4 (the fraction True)
np.where(temps > 30, "hot", "ok")    # vectorised if/else
```

## 6. Universal functions (ufuncs) and reductions

Ufuncs apply elementwise in C: `np.sqrt`, `np.exp`, `np.sin`, `np.abs`, `+ - * / ** %`, comparisons, `np.maximum`, …

```python
x = np.linspace(0, 2 * np.pi, 5)
np.sin(x)
np.maximum(x, 1.0)                    # elementwise max (np.max reduces!)

data = np.arange(12).reshape(3, 4)
data.sum()                            # 66: everything
data.sum(axis=0)                      # [12 15 18 21]: collapse rows → one value per column
data.sum(axis=1)                      # [ 6 22 38]:    collapse columns → one value per row
data.mean(axis=1, keepdims=True)      # shape (3, 1): stays broadcastable against data
data.argmax(), data.cumsum(), data.std(), np.median(data)
```

> [!TIP]
> `axis=k` means "the axis that disappears". `axis=0` aggregates *down* the rows (giving per-column results). For NaN-tolerant statistics, use `np.nanmean`, `np.nansum`, and so on.

## 7. Reshaping and combining

```python
v = np.arange(6)
v.reshape(2, 3)           # a view when possible
v.reshape(-1, 2)          # -1: infer that dimension → (3, 2)
v[:, np.newaxis]          # (6, 1): add an axis (column vector)
m.T                       # transpose (a view)
m.ravel()                 # flatten (a view if contiguous), m.flatten() always copies
np.concatenate([a, b], axis=0)
np.stack([a, b])          # a new axis
np.vstack, np.hstack, np.split
```

## 8. Why vectorised code is fast

```python
import time
x = np.random.default_rng(0).random(1_000_000)

t = time.perf_counter(); s = sum(v * v for v in x); t_loop = time.perf_counter() - t
t = time.perf_counter(); s2 = np.dot(x, x);          t_vec = time.perf_counter() - t
# t_loop ≈ 0.1–0.3 s, t_vec ≈ 0.0005 s: hundreds of times faster
```

There's no per-element interpreter overhead and no boxing into Python objects, and the CPU gets cache-friendly contiguous memory plus SIMD instructions.

## 9. Exam-ready answers

> [!EXAM]
> **The NumPy ndarray.** A NumPy ndarray is an n-dimensional array of fixed-size elements of a single dtype, stored in a contiguous (or strided) memory buffer described by its shape and strides. Operations are vectorised: universal functions and reductions execute compiled loops over the buffer, avoiding per-element interpreter overhead and enabling SIMD, which makes them orders of magnitude faster than Python loops. Basic slicing creates views that share memory with the original array, whereas integer (fancy) indexing and boolean masking produce copies; integer dtypes have fixed width and overflow silently.

## 10. Cheat sheet

| Need | Code |
|---|---|
| range of floats | `np.linspace(a, b, n)` |
| reproducible random | `rng = np.random.default_rng(seed)` |
| element / row / column | `m[r, c]`, `m[r]`, `m[:, c]` |
| independent slice | `.copy()` |
| filter | `a[a > 0]` |
| vectorised if | `np.where(cond, x, y)` |
| per-column mean | `m.mean(axis=0)` |
| keep dims for broadcasting | `keepdims=True` |
| safe image maths | `astype(np.int16)`, then `np.clip`, then back to `uint8` |

> [!INTERVIEW]
> **"Why did modifying my function's argument change the caller's array?"** The function received a *view* (for example `arr[10:20]`), or the array itself (Python passes references), and modified it in place. Views share memory. Use `.copy()` at the boundary if the function must not mutate its input, or document the in-place behaviour, as NumPy's own `out=` parameters do. Check with `np.shares_memory`.
