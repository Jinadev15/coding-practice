# NumPy: Broadcasting, Vectorization, Linear Algebra

With NumPy basics in hand, the next level is to **eliminate Python loops entirely**. Broadcasting lets arrays of different shapes combine without copying. Fancy indexing gathers and scatters arbitrary elements. `np.linalg` solves the linear algebra at the heart of robotics, vision and machine learning. This lesson shows how to think in whole arrays: pairwise distance matrices, batched transforms, histogram and scatter operations, least-squares fits and eigen-decompositions, all as a few lines of vectorised code.

## 1. Broadcasting rules

When operating on two arrays, NumPy compares their shapes **from the right**. Two dimensions are compatible if they're **equal** or one of them is **1**. A dimension of 1 is (virtually) stretched to match, and missing leading dimensions count as 1.

| A | B | Result |
|---|---|---|
| (3, 4) | (4,) | (3, 4): B is applied to every row |
| (3, 4) | (3, 1) | (3, 4): B is applied to every column |
| (5, 1, 3) | (4, 3) | (5, 4, 3) |
| (3, 4) | (3,) | ❌ error: 4 vs 3 |

```python
pts = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])   # (3, 2)
centroid = pts.mean(axis=0)                             # (2,)
centered = pts - centroid                               # (3, 2) - (2,) broadcasts per row

scale = np.array([[1.0], [10.0], [100.0]])              # (3, 1)
pts * scale                                             # scales each row differently
```

> [!KEY]
> Broadcasting never copies data. The stretched axis has stride 0. But the **result** is materialised at the full broadcast shape, so `a[:, None] - b[None, :]` with 10⁵ points each allocates a 10¹⁰-element array. Check result sizes before broadcasting big arrays.

## 2. The outer-difference trick: pairwise distances

```python
def pairwise_dist(A, B):
    """A: (n, d), B: (m, d) → (n, m) Euclidean distances, no loops."""
    diff = A[:, None, :] - B[None, :, :]        # (n, 1, d) - (1, m, d) → (n, m, d)
    return np.sqrt((diff ** 2).sum(axis=-1))

def pairwise_dist_fast(A, B):                   # memory-light: ||a||² + ||b||² - 2 a·b
    sq = (A ** 2).sum(1)[:, None] + (B ** 2).sum(1)[None, :] - 2 * A @ B.T
    return np.sqrt(np.maximum(sq, 0))           # clamp tiny negatives from rounding
```

This is the core of k-nearest neighbours, k-means assignment, and data association in robot tracking.

## 3. Vectorising loops: patterns

| Loop | Vectorised |
|---|---|
| `for i: y[i] = f(x[i])` with arithmetic | `y = expression(x)` |
| `for i: if x[i] > t: y[i] = a else b` | `np.where(x > t, a, b)` |
| running total | `np.cumsum` |
| counting categories | `np.bincount(labels, minlength=k)` |
| per-group sums | `np.bincount(groups, weights=values)` or `np.add.at` |
| sliding window | `np.lib.stride_tricks.sliding_window_view(x, w)` |
| differences | `np.diff` |
| sorted search | `np.searchsorted` |

```python
labels = np.array([0, 2, 1, 2, 2])
np.bincount(labels, minlength=4)                  # [1 1 3 0]

grid = np.zeros(5)
idx = np.array([0, 1, 1, 3])
np.add.at(grid, idx, 1.0)                         # [1. 2. 0. 1. 0.]: handles repeated indices
# grid[idx] += 1 would add only ONCE per repeated index (buffered fancy assignment)

x = np.arange(10.0)
np.lib.stride_tricks.sliding_window_view(x, 3).mean(axis=1)   # moving average, no copy of the windows
```

> [!WARNING]
> `a[idx] += 1` with **repeated** indices in `idx` increments each position only once, because fancy assignment is buffered. Use `np.add.at` (or `np.bincount`) for scatter-accumulate. This is a classic bug when building occupancy grids from lidar points.

## 4. Fancy indexing

```python
m = np.arange(12).reshape(3, 4)
m[[0, 2]]                         # rows 0 and 2
m[[0, 1, 2], [3, 2, 1]]           # elements (0,3), (1,2), (2,1) → paired indices
m[np.ix_([0, 2], [1, 3])]         # the sub-grid of rows {0,2} × cols {1,3}
order = np.argsort(m[:, 0])[::-1]
m[order]                          # rows sorted by column 0, descending
```

## 5. Linear algebra

```python
A = np.array([[3.0, 1.0], [1.0, 2.0]])
b = np.array([9.0, 8.0])

x = np.linalg.solve(A, b)          # solve Ax = b: [2. 3.]. NEVER compute inv(A) @ b (slower, less stable)
A @ x                              # matrix multiply (the @ operator)
np.linalg.det(A), np.linalg.inv(A), np.linalg.norm(b)
w, V = np.linalg.eigh(A)           # symmetric/Hermitian: real eigenvalues, ascending
U, S, Vt = np.linalg.svd(A)        # singular value decomposition
np.linalg.matrix_rank(A), np.linalg.cond(A)

# least squares: fit y ≈ a·t + c to noisy data
t = np.linspace(0, 1, 50)
y = 2.0 * t + 1.0 + np.random.default_rng(1).normal(0, 0.05, 50)
X = np.column_stack([t, np.ones_like(t)])
(a, c), *_ = np.linalg.lstsq(X, y, rcond=None)     # a ≈ 2, c ≈ 1
```

| Task | Function |
|---|---|
| square system | `solve` |
| over/under-determined | `lstsq` (QR/SVD based) |
| symmetric eigenproblem (covariance, inertia) | `eigh` |
| general eigenproblem | `eig` |
| low-rank approximation, PCA, pseudo-inverse | `svd`, `pinv` |
| batched operations | most linalg functions accept stacks: shape (k, n, n) |

### Batched transforms (robotics)

```python
theta = np.radians([0, 90, 180])
c, s = np.cos(theta), np.sin(theta)
R = np.stack([np.stack([c, -s], -1), np.stack([s, c], -1)], -2)   # (3, 2, 2) rotation matrices
p = np.array([1.0, 0.0])
R @ p                                                              # (3, 2): p rotated by each angle
cloud = np.random.default_rng(2).random((1000, 2))
rotated = cloud @ R[1].T                                          # rotate 1000 points at once
```

`np.einsum` expresses arbitrary tensor contractions readably: `np.einsum("kij,kj->ki", R, pts)` applies one rotation per point.

## 6. Random number generation done right

```python
rng = np.random.default_rng(seed=7)      # a Generator (PCG64): independent, reproducible streams
rng.integers(0, 10, size=5)
rng.normal(size=(2, 3)); rng.uniform(-1, 1, 4); rng.choice(10, 3, replace=False)
rng.permutation(10)
child = np.random.default_rng(np.random.SeedSequence(7).spawn(1)[0])   # independent streams for parallel workers
```

Avoid the legacy global `np.random.seed`/`np.random.rand` in new code: global state makes experiments hard to reproduce.

## 7. Memory and performance

- Prefer in-place operations for big arrays: `a *= 2`, `np.add(a, b, out=a)`.
- Use `float32` when the precision suffices (half the memory and bandwidth).
- Know your layout: C order (row-major, the default) versus Fortran order. Iterate along the last axis for locality.
- If you can't vectorise, use **Numba** (`@njit`), Cython, or move the hot loop to C++ (pybind11).

## 8. Exam-ready answers

> [!EXAM]
> **Broadcasting.** Broadcasting is NumPy's rule for applying elementwise operations to arrays of different shapes. Shapes are aligned from the trailing dimension; two dimensions are compatible if they're equal or one is 1, and missing leading dimensions are treated as 1. Size-1 dimensions are virtually expanded with zero strides, so no data is copied for the inputs, although the result has the full broadcast shape. Broadcasting enables loop-free formulations such as centering data by subtracting a mean vector or computing pairwise distance matrices with `A[:, None, :] − B[None, :, :]`.

## 9. Cheat sheet

| Need | Code |
|---|---|
| per-row operation | `M - v` (v has shape (cols,)) |
| per-column operation | `M - v[:, None]` |
| pairwise | `A[:, None] - B[None, :]` |
| scatter-add | `np.add.at(arr, idx, vals)` |
| histogram of labels | `np.bincount` |
| moving window | `sliding_window_view` |
| solve | `np.linalg.solve(A, b)` |
| least squares | `np.linalg.lstsq(X, y, rcond=None)` |
| symmetric eig | `np.linalg.eigh` |
| tensor contraction | `np.einsum` |

> [!INTERVIEW]
> **"Why `np.linalg.solve(A, b)` instead of `np.linalg.inv(A) @ b`?"** `solve` uses an LU factorisation and forward/back substitution, which is about 2–3× fewer operations and numerically more stable (the error is bounded by the condition number, without the extra rounding of forming the inverse). Explicit inverses are rarely needed. For repeated solves with the same A, factor once (`scipy.linalg.lu_factor` / `cho_factor`) and reuse the factorisation.
