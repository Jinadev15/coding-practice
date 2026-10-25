---
id: py-vectorized-geometry
title: "Vectorised Geometry: k-NN, Occupancy Grids, Batch Transforms, Circle Fit"
difficulty: Hard
order: 1
tags: broadcasting, fancy indexing, np.add.at, linear algebra, least squares
time_limit: 3
---
## Statement
Point-cloud processing for a mobile robot, written without Python loops over points:

```python
def knn_labels(train_pts, train_labels, query_pts, k):
    """k-nearest-neighbour classification (Euclidean). Majority vote; ties -> the SMALLEST label.
    train (n, d) <= 2000, query (m, d) <= 2000; labels are small non-negative ints."""

def occupancy_grid(points, resolution, width, height):
    """points (n, 2) in metres, grid origin at (0, 0); cell = floor(p / resolution).
    Return an int array (height, width) counting points per cell; ignore points outside the grid.
    Row = y cell, column = x cell. Points may repeat cells (use np.add.at or bincount)."""

def transform_points(points, theta, tx, ty):
    """Rotate (n, 2) points by theta radians about the origin, then translate by (tx, ty)."""

def fit_circle(points):
    """Least-squares circle through (n, 2) points (algebraic/Kasa fit): solve
    [x y 1] @ [a b c] = x^2 + y^2 for a, b, c; centre = (a/2, b/2), r = sqrt(c + cx^2 + cy^2).
    Return (cx, cy, r)."""
```

## Starter
```python
import numpy as np

def knn_labels(train_pts, train_labels, query_pts, k):
    out = []
    for q in query_pts:
        d = [np.linalg.norm(q - p) for p in train_pts]
        idx = np.argsort(d)[:k]
        out.append(np.bincount(train_labels[idx]).argmax())
    return np.array(out)

def occupancy_grid(points, resolution, width, height):
    g = np.zeros((height, width), dtype=int)
    cells = np.floor(points / resolution).astype(int)
    g[cells[:, 1], cells[:, 0]] += 1
    return g

def transform_points(points, theta, tx, ty):
    return points + np.array([tx, ty])

def fit_circle(points):
    c = points.mean(axis=0)
    return (c[0], c[1], np.linalg.norm(points - c, axis=1).mean())
```

## Driver
```python
import ast
import sys
import numpy as np

for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, n, seed = line.split()
        n, rng = int(n), np.random.default_rng(int(seed))
        tr = rng.normal(size=(n, 3)); lab = (tr[:, 0] + tr[:, 1] > 0).astype(int) + 2 * (tr[:, 2] > 1)
        q = rng.normal(size=(n, 3))
        pred = knn_labels(tr, lab, q, 7)
        pts = rng.uniform(-1, 21, size=(200000, 2))
        g = occupancy_grid(pts, 0.1, 200, 200)
        cloud = rng.normal(size=(200000, 2))
        t = transform_points(cloud, 0.7, 3.0, -2.0)
        ang = rng.uniform(0, 2 * np.pi, 5000)
        circ = np.c_[4 + 2.5 * np.cos(ang), -1 + 2.5 * np.sin(ang)] + rng.normal(0, 0.01, (5000, 2))
        cx, cy, r = fit_circle(circ)
        print("gen", n, np.bincount(pred, minlength=4).tolist(), int(g.sum()), int(g.max()), (np.round(t.mean(0), 4) + 0.0).tolist(),
              round(float(cx), 2), round(float(cy), 2), round(float(r), 2))
        continue
    name, args = ast.literal_eval(line)
    if name == "knn":
        print("knn ->", knn_labels(np.array(args[0], float), np.array(args[1]), np.array(args[2], float), args[3]).tolist())
    elif name == "grid":
        print("grid ->", occupancy_grid(np.array(args[0], float), *args[1:]).tolist())
    elif name == "transform":
        print("transform ->", (np.round(transform_points(np.array(args[0], float), *args[1:]), 4) + 0.0).tolist())
    else:
        print("circle ->", [round(float(v), 4) + 0.0 for v in fit_circle(np.array(args[0], float))])
```

## Tests
=== sample
("knn", ([[0, 0], [1, 0], [5, 5], [6, 5]], [0, 0, 1, 1], [[0.2, 0.1], [5.5, 5.2]], 1))
("grid", ([[0.05, 0.05], [0.07, 0.01], [0.15, 0.25], [9.0, 9.0]], 0.1, 3, 3))
("transform", ([[1, 0], [0, 1]], 1.5707963267948966, 10, 0))
("circle", ([[1, 0], [0, 1], [-1, 0], [0, -1]],))
---
knn -> [0, 1]
grid -> [[2, 0, 0], [0, 0, 0], [0, 1, 0]]
transform -> [[10.0, 1.0], [9.0, 0.0]]
circle -> [0.0, 0.0, 1.0]
=== hidden
("knn", ([[0], [1], [2], [3]], [3, 3, 1, 1], [[1.5]], 4))
("knn", ([[0], [10]], [5, 2], [[5]], 2))
("knn", ([[0, 0], [0, 1], [1, 0]], [1, 0, 0], [[0, 0]], 3))
("grid", ([[-0.1, 0.5], [0.5, -0.1], [0.3, 0.3], [0.3, 0.3], [0.3, 0.3]], 0.2, 2, 2))
("grid", ([[0.39, 0.39]], 0.2, 2, 2))
("transform", ([[2, 3]], 0.0, -1, -1))
("transform", ([[1, 1], [-1, 2]], 3.141592653589793, 0, 0))
("circle", ([[3, 0], [-1, 0], [1, 2], [1, -2]],))
---
knn -> [1]
knn -> [2]
knn -> [0]
grid -> [[0, 0], [0, 3]]
grid -> [[0, 0], [0, 1]]
transform -> [[1.0, 2.0]]
transform -> [[-1.0, -1.0], [1.0, -2.0]]
circle -> [1.0, 0.0, 2.0]
=== hidden
gen 2000 3
---
gen 2000 [879, 821, 160, 140] 165353 16 [3.0001, -2.0008] 4.0 -1.0 2.5

## Hints
- **k-NN**: the distance matrix `((Q[:, None, :] - T[None, :, :]) ** 2).sum(-1)` (m, n), then `np.argpartition(D, k - 1, axis=1)[:, :k]` for the neighbour indices. For the votes, `counts = np.zeros((m, L)); np.add.at(counts, (rows, labels[idx]), 1)`, then `counts.argmax(1)`, which returns the smallest label on ties.
- **Grid**: drop out-of-range cells with a mask *before* indexing (negative indices would wrap!), then `np.add.at(g, (cy, cx), 1)`. Plain `g[cy, cx] += 1` counts repeated cells only once.
- **Transform**: `R = [[c, -s], [s, c]]`, then `points @ R.T + [tx, ty]`.
- **Circle**: `A = np.c_[x, y, ones]`, `rhs = x² + y²`, `np.linalg.lstsq(A, rhs, rcond=None)`.

## Solution
```python
import numpy as np

def knn_labels(train_pts, train_labels, query_pts, k):
    d2 = ((query_pts[:, None, :] - train_pts[None, :, :]) ** 2).sum(axis=-1)   # (m, n)
    nn = np.argpartition(d2, k - 1, axis=1)[:, :k]                             # k smallest, unordered
    labels = train_labels[nn]                                                  # (m, k)
    L = int(train_labels.max()) + 1
    counts = np.zeros((len(query_pts), L), dtype=np.int64)
    rows = np.repeat(np.arange(len(query_pts)), k)
    np.add.at(counts, (rows, labels.ravel()), 1)
    return counts.argmax(axis=1)                                               # first max = smallest label

def occupancy_grid(points, resolution, width, height):
    cells = np.floor(points / resolution).astype(np.int64)
    cx, cy = cells[:, 0], cells[:, 1]
    keep = (cx >= 0) & (cx < width) & (cy >= 0) & (cy < height)
    g = np.zeros((height, width), dtype=np.int64)
    np.add.at(g, (cy[keep], cx[keep]), 1)
    return g

def transform_points(points, theta, tx, ty):
    c, s = np.cos(theta), np.sin(theta)
    R = np.array([[c, -s], [s, c]])
    return points @ R.T + np.array([tx, ty])

def fit_circle(points):
    x, y = points[:, 0], points[:, 1]
    A = np.c_[x, y, np.ones_like(x)]
    (a, b, c), *_ = np.linalg.lstsq(A, x * x + y * y, rcond=None)
    cx, cy = a / 2, b / 2
    return cx, cy, float(np.sqrt(c + cx * cx + cy * cy))
```

- **Broadcasting** builds the whole query × train distance matrix in one expression. `argpartition` finds the k nearest neighbours in O(n) per row without a full sort.
- **Scatter-accumulate** (`np.add.at`) is the correct way to count points per cell or votes per label when indices repeat. Fancy `+=` silently counts each repeated index once. Masking *before* indexing also matters, because a negative cell index would wrap around to the far side of the grid.
- **Batch transforms** are a single matrix product, `points @ R.T`, for hundreds of thousands of points.
- **The Kasa fit** linearises the circle equation x² + y² = a·x + b·y + c, turning a nonlinear fit into one least-squares solve. It's exact for noise-free points and an excellent initialiser for a geometric fit.
