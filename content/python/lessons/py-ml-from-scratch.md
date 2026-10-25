# ML Algorithms from Scratch

Libraries hide the mathematics, and interviews, research and debugging all require it. Implementing the core algorithms yourself in NumPy builds real understanding: what a gradient is, why features must be scaled, how a decision tree chooses splits, why k-means can get stuck. This lesson derives and implements linear regression (closed form and gradient descent), logistic regression, k-nearest neighbours, k-means and decision trees, each in a few vectorised lines, and connects them to the scikit-learn estimators you'd use in production.

## 1. Linear regression

Model: ŷ = Xw + b. Loss: mean squared error L = (1/n)‖Xw + b − y‖².

**Closed form** (the normal equations): with a bias column appended, w = (XᵀX)⁻¹Xᵀy. Compute it with `lstsq` for numerical stability, never with an explicit inverse.

**Gradient descent**: ∂L/∂w = (2/n)·Xᵀ(ŷ − y) and ∂L/∂b = (2/n)·Σ(ŷ − y).

```python
import numpy as np

def linreg_gd(X, y, lr=0.1, epochs=500):
    n, d = X.shape
    w, b = np.zeros(d), 0.0
    for _ in range(epochs):
        err = X @ w + b - y                 # (n,)
        w -= lr * (2 / n) * (X.T @ err)     # vectorised gradient
        b -= lr * (2 / n) * err.sum()
    return w, b

rng = np.random.default_rng(0)
X = rng.normal(size=(200, 3))
y = X @ np.array([2.0, -1.0, 0.5]) + 4.0 + rng.normal(0, 0.1, 200)
w, b = linreg_gd(X, y)                      # ≈ [2, -1, 0.5], 4
```

> [!KEY]
> **Feature scaling matters for gradient descent.** If one feature ranges over [0, 1000] and another over [0, 1], the loss surface is a long narrow valley: a learning rate small enough for the steep direction crawls along the shallow one. Standardise features (zero mean, unit variance) first, using statistics from the **training** set only.

**Ridge** (L2) regularisation adds λ‖w‖² to the loss, so the gradient gains `2λw` and the closed form becomes (XᵀX + λI)⁻¹Xᵀy. That shrinks weights, reduces variance, and fixes ill-conditioned XᵀX.

## 2. Logistic regression

The probability of class 1 is σ(z) = 1/(1 + e^(−z)) with z = Xw + b. Minimise the **binary cross-entropy** L = −(1/n)Σ[y log p + (1−y) log(1−p)]. Its gradient has the same simple form as linear regression's: ∂L/∂w = (1/n)·Xᵀ(p − y).

```python
def sigmoid(z):
    return np.where(z >= 0, 1 / (1 + np.exp(-z)), np.exp(z) / (1 + np.exp(z)))   # overflow-safe

def logreg_fit(X, y, lr=0.5, epochs=1000, l2=0.0):
    n, d = X.shape
    w, b = np.zeros(d), 0.0
    for _ in range(epochs):
        p = sigmoid(X @ w + b)
        w -= lr * (X.T @ (p - y) / n + l2 * w)
        b -= lr * (p - y).mean()
    return w, b

def logreg_predict(X, w, b, threshold=0.5):
    return (sigmoid(X @ w + b) >= threshold).astype(int)
```

Cross-entropy (not MSE) is used because it's convex for logistic regression and its gradient doesn't vanish when the prediction is confidently wrong. The **softmax** generalisation handles k classes: pₖ = e^{zₖ}/Σe^{zⱼ}, computed with the max subtracted for stability.

## 3. k-nearest neighbours

There's no training: store the data, and at query time vote among the k closest points.

```python
def knn_predict(X_train, y_train, X_query, k=5):
    d2 = ((X_query[:, None, :] - X_train[None, :, :]) ** 2).sum(-1)    # (m, n) squared distances
    nn = np.argpartition(d2, k - 1, axis=1)[:, :k]
    votes = y_train[nn]                                                 # (m, k)
    return np.array([np.bincount(v).argmax() for v in votes])
```

The trade-offs: training costs O(1), but each query costs O(n·d) unless a KD-tree or ball tree is used (which works well in low dimensions). Small k means high variance, large k high bias. Scaling matters, because distances mix units. And performance collapses in high dimensions (the curse of dimensionality: all distances become similar).

## 4. k-means clustering

Lloyd's algorithm alternates two steps:
1. Assign each point to its nearest centroid.
2. Move each centroid to the mean of its points.

Each step lowers the within-cluster sum of squares, so it converges, but only to a **local** optimum.

```python
def kmeans(X, k, iters=100, seed=0):
    rng = np.random.default_rng(seed)
    C = X[rng.choice(len(X), k, replace=False)]                 # random init (k-means++ is better)
    for _ in range(iters):
        labels = ((X[:, None, :] - C[None]) ** 2).sum(-1).argmin(1)
        newC = np.array([X[labels == j].mean(0) if np.any(labels == j) else C[j] for j in range(k)])
        if np.allclose(newC, C):
            break
        C = newC
    inertia = ((X - C[labels]) ** 2).sum()
    return C, labels, inertia
```

- **k-means++** initialisation picks each new centre with probability proportional to its squared distance from the existing centres, which gives provably better starts. scikit-learn uses it by default, with multiple restarts (`n_init`).
- k-means assumes roughly spherical, similar-sized clusters. Use DBSCAN or Gaussian mixtures otherwise.

## 5. Decision trees

A tree recursively splits the data on the feature and threshold that most reduce **impurity**:
- **Gini**: G = 1 − Σ pₖ²
- **Entropy**: H = −Σ pₖ log₂ pₖ
- **MSE** for regression

```python
def gini(y):
    _, counts = np.unique(y, return_counts=True)
    p = counts / counts.sum()
    return 1.0 - (p ** 2).sum()

def best_split(X, y):
    best = (None, None, gini(y))                         # (feature, threshold, weighted impurity)
    n = len(y)
    for f in range(X.shape[1]):
        order = np.argsort(X[:, f])
        xs, ys = X[order, f], y[order]
        for i in range(1, n):
            if xs[i] == xs[i - 1]:
                continue                                 # can't split between equal values
            g = (i * gini(ys[:i]) + (n - i) * gini(ys[i:])) / n
            if g < best[2]:
                best = (f, (xs[i] + xs[i - 1]) / 2, g)
    return best
```

(Production implementations update class counts incrementally while sweeping the sorted values, making each feature O(n log n) instead of O(n²).)

Trees need no scaling and capture interactions and non-linearity, but a single deep tree overfits badly. **Random forests** average many trees grown on bootstrap samples with random feature subsets, which reduces variance. **Gradient boosting** fits each new shallow tree to the residuals (the negative gradient) of the current ensemble, which reduces bias. These ensembles dominate tabular ML.

## 6. Evaluation from scratch

```python
def confusion(y_true, y_pred, k):
    m = np.zeros((k, k), dtype=int)
    np.add.at(m, (y_true, y_pred), 1)
    return m

def precision_recall_f1(y_true, y_pred):
    tp = np.sum((y_pred == 1) & (y_true == 1))
    fp = np.sum((y_pred == 1) & (y_true == 0))
    fn = np.sum((y_pred == 0) & (y_true == 1))
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return p, r, (2 * p * r / (p + r) if p + r else 0.0)
```

## 7. Exam-ready answers

> [!EXAM]
> **Gradient descent for logistic regression.** Logistic regression models the probability of the positive class as σ(wᵀx + b), where σ is the logistic sigmoid, and is trained by minimising the average binary cross-entropy between predicted probabilities and labels. This loss is convex, and its gradient with respect to the weights is (1/n)Xᵀ(p − y), the same form as least-squares regression with the residual replaced by the probability error. Batch gradient descent repeatedly updates w ← w − η∇L until convergence; stochastic and mini-batch variants use subsets of the data per step. Feature standardisation improves conditioning and convergence speed, and L2 regularisation adds λw to the gradient to reduce overfitting.

## 8. Cheat sheet

| Algorithm | Core equation | Complexity |
|---|---|---|
| linear regression | w = lstsq([X 1], y) / grad (2/n)Xᵀ(ŷ−y) | O(nd²) closed form |
| logistic regression | grad (1/n)Xᵀ(σ(Xw)−y) | O(nd) per epoch |
| k-NN | vote among argpartition of distances | O(nd) per query |
| k-means | assign → mean, repeat | O(nkd) per iteration |
| decision tree split | minimise weighted Gini | O(d·n log n) per node |

> [!INTERVIEW]
> **"Why might k-means give different results on each run, and how do you fix it?"** Lloyd's algorithm converges only to a local minimum that depends on the initial centroids. Use k-means++ initialisation, run several restarts (`n_init`) keeping the lowest inertia, standardise the features, and choose k with the elbow method or silhouette scores. If the clusters aren't spherical, or have very different sizes or densities, k-means is the wrong model: consider DBSCAN or Gaussian mixtures.
