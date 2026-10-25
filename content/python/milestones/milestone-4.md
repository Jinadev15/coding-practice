# Study guide: Special quiz 4 (capstones)

The final quiz has three capstone projects. Each section explains the theory you need; the problem statement gives the exact API.

## 1. Machine learning from scratch with NumPy

### Standardisation
Features on different scales (metres vs millimetres) break many algorithms. Standardise each column: `z = (x − mean) / std`. Learn `mean` and `std` from the **training data only**, then apply the same numbers to the test data. Using the test data's statistics is a form of cheating called **data leakage**.

### PCA with SVD
Principal Component Analysis finds the directions in which the data varies most. Centre the data matrix `X` (n × d), then compute the SVD `X = U Σ Vᵀ`:

- The rows of `Vᵀ` are the **principal directions**.
- The explained variance of component k is `σ_k² / (n − 1)`.
- To project onto k components, compute `X @ Vt[:k].T`.

```python
Xc = X - X.mean(axis=0)
U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
explained = S**2 / (len(X) - 1)
```

SVD signs are arbitrary: `v` and `−v` are equally valid. To match scikit-learn, flip each component so its largest-magnitude entry is positive. This is called sign normalisation.

### Logistic regression with Newton's method
The model is `p = σ(Xw)` with `σ(t) = 1 / (1 + e^(−t))`. Minimise the regularised negative log-likelihood. Its gradient and Hessian are:

```text
g = Xᵀ(p − y) + λw
H = Xᵀ diag(p(1−p)) X + λI
w ← w − H⁻¹ g          (repeat until ‖step‖ is tiny)
```

Newton's method converges in about 5–10 iterations because it uses curvature. Solve `H Δ = g` with `np.linalg.solve`. Don't regularise the intercept.

### Cross-validation
Split the data into k folds. Train on k−1 folds, test on the remaining one, rotate through all k, and average the scores. Fit the scaler **inside** each fold, otherwise you leak data again.

## 2. Occupancy grid mapping and frontier exploration

A robot with a range sensor builds a map of **free**, **occupied** and **unknown** cells.

**Log-odds.** Each cell stores `l = log(p / (1 − p))`, which starts at 0 (p = 0.5, unknown). Bayesian updates become simple **additions**:

- Every cell the beam passes through gets `l += l_free` (negative).
- The cell where the beam ends gets `l += l_occ` (positive).
- Clamp `l` to `[l_min, l_max]` so the map can still change later.

**Bresenham's line algorithm** lists the integer grid cells between two points using only integer arithmetic:

```python
def bresenham(x0, y0, x1, y1):
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err, cells = dx + dy, []
    while True:
        cells.append((x0, y0))
        if (x0, y0) == (x1, y1): return cells
        e2 = 2 * err
        if e2 >= dy: err += dy; x0 += sx
        if e2 <= dx: err += dx; y0 += sy
```

**Frontiers** are free cells next to unknown cells: the edge of the explored area. Group the frontier cells into connected components, then send the robot to the best cluster, for example the nearest one by BFS path length. Repeat until no frontiers remain and the map is complete.

## 3. A resumable async workflow engine

**asyncio basics:**

- `async def` defines a coroutine.
- `await` pauses it until a result is ready, and other tasks run in the meantime.
- `asyncio.gather` and `create_task` run tasks concurrently.

Concurrency here means many tasks waiting on I/O at once, on a single thread.

The tools you need:

| Need | Tool |
|---|---|
| At most k tasks at once | `sem = asyncio.Semaphore(k)`; `async with sem:` |
| Give up after t seconds | `await asyncio.wait_for(coro, t)` raises `TimeoutError` |
| Retry with backoff | loop; on failure `await asyncio.sleep(base * 2**attempt)` |
| Run a step when its deps finish | keep `remaining_deps` counts; start the step when its count hits 0 |

**Resumability.** Record each step's status (`pending/running/done/failed`) and result in **SQLite** as soon as it changes. On restart, load the table:

- Steps marked `done` are skipped.
- Steps that were `running` when the process crashed are treated as `pending`.

This only works if steps are **idempotent**: running one twice must be safe.

> [!KEY]
> Commit to SQLite **after** a step succeeds and **before** you start its dependants. Then a crash at any moment loses at most the work in progress.
