---
id: py-numpy-learners
title: Learners from Scratch in NumPy
difficulty: Hard
order: 1
tags: gradient descent, logistic regression, k-means, decision stump, numpy
time_limit: 6
---
## Statement
Implement four learners using **only NumPy** (importing scikit-learn is detected and rejected). Every algorithm is specified exactly, so results are deterministic.

```python
def fit_linear(X, y, lr, epochs):
    """Batch gradient descent on MSE, starting from w = 0, b = 0.
    Each epoch: err = X@w + b - y; w -= lr * 2/n * X.T@err; b -= lr * 2/n * err.sum(). Return (w, b)."""

def fit_logistic(X, y, lr, epochs, l2):
    """Batch gradient descent on mean binary cross-entropy + (l2/2)*||w||^2 (no penalty on b), from zeros.
    Each epoch: p = sigmoid(X@w + b); w -= lr * (X.T@(p - y)/n + l2*w); b -= lr * mean(p - y).
    Use a numerically stable sigmoid. Return (w, b)."""

def kmeans(X, k, iters):
    """Lloyd's algorithm with the FIRST k points as initial centroids. Each iteration: assign each point
    to its nearest centroid (ties -> lowest index), then move each centroid to its points' mean
    (an empty cluster keeps its centroid). Stop early if no assignment changes.
    Return (centroids, labels, inertia)."""

def best_stump(X, y):
    """Best single split for binary labels y in {0,1}: over all features f and thresholds t taken as
    midpoints between consecutive DISTINCT sorted values of X[:, f], minimise the weighted Gini impurity
    of (X[:, f] <= t) vs (> t). Ties -> smaller feature index, then smaller threshold.
    Return (feature, threshold, weighted_gini)."""
```

## Starter
```python
import numpy as np

def fit_linear(X, y, lr, epochs):
    w = np.linalg.lstsq(X, y, rcond=None)[0]
    return w, 0.0

def fit_logistic(X, y, lr, epochs, l2):
    return np.zeros(X.shape[1]), 0.0

def kmeans(X, k, iters):
    return X[:k], np.zeros(len(X), dtype=int), 0.0

def best_stump(X, y):
    return 0, float(np.median(X[:, 0])), 0.5
```

## Driver
```python
import sys
import numpy as np

def r(v, d=4):
    return (np.round(np.asarray(v, dtype=float), d) + 0.0).tolist()

rng = np.random.default_rng(7)
for cmd in sys.stdin.read().split():
    if cmd == "linear":
        X = rng.normal(size=(300, 3)); y = X @ np.array([1.5, -2.0, 0.7]) + 3.0 + rng.normal(0, 0.05, 300)
        w, b = fit_linear(X, y, 0.05, 400)
        print("linear w=", r(w, 3), "b=", round(float(b), 3) + 0.0)
        w2, b2 = fit_linear(np.array([[1.0], [2.0], [3.0]]), np.array([2.0, 4.0, 6.0]), 0.01, 3)
        print("linear 3 steps:", r(w2), round(float(b2), 4) + 0.0)
    elif cmd == "logistic":
        X = np.r_[rng.normal(-1, 1, (200, 2)), rng.normal(1.5, 1, (200, 2))]
        y = np.r_[np.zeros(200), np.ones(200)]
        w, b = fit_logistic(X, y, 0.5, 500, 0.01)
        acc = ((1 / (1 + np.exp(-(X @ w + b))) >= 0.5) == y).mean()
        print("logistic w=", r(w, 3), "b=", round(float(b), 3) + 0.0, "acc=", round(float(acc), 3))
        w, b = fit_logistic(np.array([[1000.0], [-1000.0]]), np.array([1.0, 0.0]), 1.0, 5, 0.0)
        print("extreme inputs finite:", bool(np.all(np.isfinite(w))) and bool(np.isfinite(b)))
    elif cmd == "kmeans":
        X = np.array([[0.0, 0], [10, 10], [0, 1], [1, 0], [10, 11], [11, 10], [5, 5]])
        C, lab, inert = kmeans(X, 2, 50)
        print("kmeans C=", r(C), "labels=", lab.tolist(), "inertia=", round(float(inert), 4))
        big = np.r_[rng.normal(0, 1, (3000, 2)), rng.normal(6, 1, (3000, 2)), rng.normal((0, 8), 1, (3000, 2))]
        big = big[rng.permutation(len(big))]
        C, lab, inert = kmeans(big, 3, 100)
        print("kmeans big sizes=", sorted(np.bincount(lab).tolist()), "inertia=", round(float(inert), 1))
    elif cmd == "stump":
        X = np.array([[2.0, 7.0], [3.0, 1.0], [10.0, 5.0], [11.0, 6.0], [3.0, 2.0]])
        y = np.array([0, 0, 1, 1, 0])
        f, t, g = best_stump(X, y)
        print("stump:", f, round(float(t), 4), round(float(g), 4))
        X = rng.normal(size=(400, 4)); y = ((X[:, 2] > 0.3) ^ (rng.random(400) < 0.05)).astype(int)
        f, t, g = best_stump(X, y)
        print("stump big:", f, round(float(t), 3), round(float(g), 4))
print("sklearn imported:", "sklearn" in sys.modules)
```

## Tests
=== sample
linear
kmeans
---
linear w= [1.501, -2.008, 0.7] b= 2.999
linear 3 steps: [0.5004] 0.2138
kmeans C= [[1.5, 1.5], [10.3333, 10.3333]] labels= [0, 1, 0, 0, 1, 1, 0] inertia= 35.3333
kmeans big sizes= [2998, 2999, 3003] inertia= 17819.4
sklearn imported: False
=== hidden
logistic
stump
---
logistic w= [1.992, 1.626] b= -0.621 acc= 0.97
extreme inputs finite: True
stump: 0 6.5 0.0
stump big: 2 0.301 0.0859
sklearn imported: False

## Hints
- Write the updates exactly as specified. The judge compares numbers rounded to 3–4 decimals, so a different update order (for example updating b with the new w) gives different results.
- Stable sigmoid: `np.where(z >= 0, 1/(1+np.exp(-z)), np.exp(z)/(1+np.exp(z)))`, computing `np.exp` on clipped values (or using `np.exp(-np.abs(z))`) to avoid overflow warnings.
- k-means assignment: `((X[:, None] - C[None]) ** 2).sum(-1).argmin(1)`. `argmin` returns the lowest index on ties.
- Stump: sort each feature once. For each distinct-value boundary, compute the left/right class counts with cumulative sums. Weighted Gini = (nL·GL + nR·GR)/n.

## Solution
```python
import numpy as np

def fit_linear(X, y, lr, epochs):
    n, d = X.shape
    w, b = np.zeros(d), 0.0
    for _ in range(epochs):
        err = X @ w + b - y
        w = w - lr * 2 / n * (X.T @ err)
        b = b - lr * 2 / n * err.sum()
    return w, b

def _sigmoid(z):
    e = np.exp(-np.abs(z))                       # never overflows
    return np.where(z >= 0, 1 / (1 + e), e / (1 + e))

def fit_logistic(X, y, lr, epochs, l2):
    n, d = X.shape
    w, b = np.zeros(d), 0.0
    for _ in range(epochs):
        p = _sigmoid(X @ w + b)
        w = w - lr * (X.T @ (p - y) / n + l2 * w)
        b = b - lr * (p - y).mean()
    return w, b

def kmeans(X, k, iters):
    C = X[:k].astype(float).copy()
    labels = None
    for _ in range(iters):
        new = ((X[:, None, :] - C[None, :, :]) ** 2).sum(-1).argmin(1)
        if labels is not None and np.array_equal(new, labels):
            break
        labels = new
        for j in range(k):
            members = X[labels == j]
            if len(members):
                C[j] = members.mean(0)
    inertia = float(((X - C[labels]) ** 2).sum())
    return C, labels, inertia

def best_stump(X, y):
    n, d = X.shape
    best = (None, None, np.inf)
    total1 = y.sum()
    for f in range(d):
        order = np.argsort(X[:, f], kind="stable")
        xs, ys = X[order, f], y[order]
        left1 = np.cumsum(ys)[:-1]                    # class-1 count among the first i+1 samples
        nl = np.arange(1, n)
        nr = n - nl
        right1 = total1 - left1
        gl = 1 - (left1 / nl) ** 2 - ((nl - left1) / nl) ** 2
        gr = 1 - (right1 / nr) ** 2 - ((nr - right1) / nr) ** 2
        g = (nl * gl + nr * gr) / n
        valid = xs[1:] != xs[:-1]                     # only between distinct values
        for i in np.flatnonzero(valid):
            t = (xs[i] + xs[i + 1]) / 2
            if g[i] < best[2] - 1e-12:
                best = (f, t, g[i])
    return best[0], float(best[1]), float(best[2])
```

- **Gradient descent**, written exactly as the maths says, recovers the generating coefficients. The sigmoid evaluates `exp(-|z|)`, so inputs like ±1000 can't overflow. That's the standard trick behind every library's logistic function.
- **k-means** alternates assignment (an argmin over broadcast distances) with mean updates, and stops as soon as the assignments stabilise. Deterministic initialisation makes the result reproducible. Real code uses k-means++ plus restarts.
- **The stump** evaluates every split of a feature in one vectorised pass: cumulative class counts give both children's Gini at every boundary at once, so each feature costs O(n log n) (the sort). Repeated recursively, this is exactly how CART decision trees, and the trees inside random forests and gradient boosting, choose their splits.
