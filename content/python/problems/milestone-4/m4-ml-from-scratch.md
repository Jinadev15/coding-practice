---
id: m4-ml-from-scratch
title: A Machine-Learning Pipeline from Scratch (Checked Against scikit-learn)
difficulty: Expert
order: 2
tags: NumPy, linear algebra, SVD, PCA, logistic regression, Newton's method, cross-validation, API design
time_limit: 20
---
## Statement
Capstone: implement the core of a scikit-learn-style ML stack with **only NumPy**, using the same estimator API (`fit` / `transform` / `predict`) and the same mathematics. The judge compares your numbers with real scikit-learn.

**`StandardScaler`**: `fit(X)` stores `mean_` and `scale_` (the population std, `ddof=0`, with zeros replaced by 1). It also has `transform`, `fit_transform` and `inverse_transform`. Every `fit` returns `self`.

**`PCA(n_components)`**:
- `fit` centres the data and takes the SVD of the centred matrix.
- `components_` has shape `(k, d)`. Sign convention: **in each component, the entry with the largest absolute value is positive** (this matches `sklearn.decomposition.PCA`).
- `explained_variance_` uses `ddof=1`, and there's also `explained_variance_ratio_`.
- `transform(X) = (X − mean_) @ components_.T`.

**`LogisticRegression(C=1.0, max_iter=50, tol=1e-12)`**, for binary labels {0, 1}:
- Minimise `½‖w‖² + C·Σ log-loss`. The intercept isn't penalised. This is scikit-learn's objective.
- Use **Newton's method**: gradient plus full Hessian over `[w, b]`. Stop when the Newton step's max-abs is below `tol`.
- It exposes `coef_` with shape `(1, d)`, `intercept_` with shape `(1,)`, `predict_proba` (n×2), and `predict` (threshold 0.5).

**`Pipeline(steps)`**, where `steps` is a list of `(name, estimator)`:
- `fit(X, y)` fit-transforms through every step except the last, then fits the last.
- `predict(X)` transforms, then predicts.
- `named_steps` is a dict of the steps by name.

**`kfold_indices(n, k)`**: contiguous folds like `KFold(shuffle=False)`, where the first `n % k` folds get one extra sample. It yields `(train_idx, test_idx)` pairs of NumPy arrays.

**`cross_val_accuracy(make_estimator, X, y, k=5)`**: a list of the per-fold accuracies, refitting a **fresh** estimator from `make_estimator()` for each fold.

## Starter
```python
import numpy as np


class StandardScaler:
    def fit(self, X):
        self.mean_ = X.mean(axis=0)
        return self

    def transform(self, X):
        return X - self.mean_


class LogisticRegression:
    def __init__(self, C=1.0, max_iter=50, tol=1e-12):
        self.C = C

    def fit(self, X, y):
        self.coef_ = np.zeros((1, X.shape[1]))
        self.intercept_ = np.zeros(1)
        return self

    def predict(self, X):
        return np.zeros(len(X), dtype=int)
```

## Driver
```python
import sys
import warnings
import numpy as np
warnings.simplefilter("ignore")
from sklearn.datasets import load_breast_cancer, make_classification
from sklearn.preprocessing import StandardScaler as SkScaler
from sklearn.decomposition import PCA as SkPCA
from sklearn.linear_model import LogisticRegression as SkLR
from sklearn.model_selection import KFold

for cmd in sys.stdin.read().split():
    if cmd == "scaler_pca":
        X = load_breast_cancer().data
        s = StandardScaler().fit(X); sk = SkScaler().fit(X)
        print("scaler match", np.allclose(s.mean_, sk.mean_) and np.allclose(s.scale_, sk.scale_), "roundtrip", np.allclose(s.inverse_transform(s.transform(X)), X))
        Z = s.transform(X)
        p = PCA(5).fit(Z); q = SkPCA(5, svd_solver="full").fit(Z)
        print("components match", np.allclose(p.components_, q.components_, atol=1e-8), "variance match", np.allclose(p.explained_variance_, q.explained_variance_))
        print("ratio", " ".join(f"{v:.4f}" for v in p.explained_variance_ratio_), "transform match", np.allclose(p.transform(Z), q.transform(Z), atol=1e-8))
        const = np.column_stack([np.ones(10), np.arange(10.0)])
        print("constant column scale", " ".join(f"{v:.6f}" for v in StandardScaler().fit(const).scale_))
    elif cmd == "logreg":
        X, y = make_classification(n_samples=400, n_features=6, n_informative=4, random_state=3)
        for C in (0.1, 1.0, 10.0):
            mine = LogisticRegression(C=C).fit(X, y)
            ref = SkLR(C=C, tol=1e-12, max_iter=10000).fit(X, y)
            print(f"C={C}", "coef match", np.allclose(mine.coef_, ref.coef_, atol=1e-5), "intercept match", np.allclose(mine.intercept_, ref.intercept_, atol=1e-5),
                  "proba match", np.allclose(mine.predict_proba(X), ref.predict_proba(X), atol=1e-6), "acc", f"{(mine.predict(X) == y).mean():.4f}")
        print("shapes", mine.coef_.shape, mine.intercept_.shape, mine.predict_proba(X[:3]).shape)
    elif cmd == "pipeline":
        data = load_breast_cancer(); X, y = data.data, data.target
        make = lambda: Pipeline([("scale", StandardScaler()), ("pca", PCA(8)), ("clf", LogisticRegression(C=0.5))])
        folds = list(kfold_indices(len(X), 5))
        ref_folds = list(KFold(5).split(X))
        print("folds match", all(np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1]) for a, b in zip(folds, ref_folds)), [len(t) for _, t in folds])
        scores = cross_val_accuracy(make, X, y, k=5)
        print("cv", " ".join(f"{s:.4f}" for s in scores), "mean", f"{np.mean(scores):.4f}")
        pipe = make().fit(X, y)
        print("steps", list(pipe.named_steps), "train acc", f"{(pipe.predict(X) == y).mean():.4f}")
        from sklearn.pipeline import Pipeline as SkPipe
        from sklearn.model_selection import cross_val_score
        sk = cross_val_score(SkPipe([("s", SkScaler()), ("p", SkPCA(8, svd_solver="full")), ("c", SkLR(C=0.5, tol=1e-12, max_iter=10000))]), X, y, cv=KFold(5))
        print("matches sklearn cv", np.allclose(scores, sk))
```

## Tests
=== sample
scaler_pca
---
scaler match True roundtrip True
components match True variance match True
ratio 0.4427 0.1897 0.0939 0.0660 0.0550 transform match True
constant column scale 1.000000 2.872281
=== hidden
logreg
---
C=0.1 coef match True intercept match True proba match True acc 0.8550
C=1.0 coef match True intercept match True proba match True acc 0.8550
C=10.0 coef match True intercept match True proba match True acc 0.8550
shapes (1, 6) (1,) (3, 2)
=== hidden
pipeline
---
folds match True [114, 114, 114, 114, 113]
cv 0.9649 0.9649 0.9825 0.9825 0.9735 mean 0.9736
steps ['scale', 'pca', 'clf'] train acc 0.9824
matches sklearn cv True

## Hints
- PCA: `U, S, Vt = np.linalg.svd(Xc, full_matrices=False)`. The variances are `S² / (n − 1)`. Flip each row of `Vt` so that `Vt[i, argmax(|Vt[i]|)] > 0`.
- Logistic regression: augment `X` with a column of ones. For `p = σ(Xa·θ)`, the gradient is `[w, 0] + C·Xaᵀ(p − y)` and the Hessian is `diag([1,…,1, 0]) + C·Xaᵀ diag(p(1−p)) Xa`. Step with `θ −= solve(H, g)`.
- Use a numerically stable sigmoid: `np.where(z >= 0, 1/(1+e^{−z}), e^{z}/(1+e^{z}))`, or `scipy.special.expit`.
- `kfold_indices`: `sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]`, then slice contiguous ranges.

## Solution
```python
import numpy as np


class StandardScaler:
    def fit(self, X):
        X = np.asarray(X, dtype=float)
        self.mean_ = X.mean(axis=0)
        std = X.std(axis=0)
        self.scale_ = np.where(std == 0, 1.0, std)
        return self

    def transform(self, X):
        return (np.asarray(X, dtype=float) - self.mean_) / self.scale_

    def fit_transform(self, X, y=None):
        return self.fit(X).transform(X)

    def inverse_transform(self, Z):
        return np.asarray(Z) * self.scale_ + self.mean_


class PCA:
    def __init__(self, n_components):
        self.n_components = n_components

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        self.mean_ = X.mean(axis=0)
        Xc = X - self.mean_
        _, S, Vt = np.linalg.svd(Xc, full_matrices=False)
        signs = np.sign(Vt[np.arange(len(Vt)), np.argmax(np.abs(Vt), axis=1)])
        Vt = Vt * signs[:, None]                                  # deterministic sign convention
        var = S ** 2 / (len(X) - 1)
        k = self.n_components
        self.components_ = Vt[:k]
        self.explained_variance_ = var[:k]
        self.explained_variance_ratio_ = var[:k] / var.sum()
        return self

    def transform(self, X):
        return (np.asarray(X, dtype=float) - self.mean_) @ self.components_.T

    def fit_transform(self, X, y=None):
        return self.fit(X).transform(X)


def _sigmoid(z):
    out = np.empty_like(z)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out


class LogisticRegression:
    def __init__(self, C=1.0, max_iter=50, tol=1e-12):
        self.C, self.max_iter, self.tol = C, max_iter, tol

    def fit(self, X, y):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        Xa = np.hstack([X, np.ones((len(X), 1))])
        d = X.shape[1]
        theta = np.zeros(d + 1)
        reg = np.ones(d + 1)
        reg[-1] = 0.0                                             # intercept not penalised
        for _ in range(self.max_iter):
            p = _sigmoid(Xa @ theta)
            grad = reg * theta + self.C * Xa.T @ (p - y)
            W = p * (1 - p)
            H = np.diag(reg) + self.C * (Xa.T * W) @ Xa
            step = np.linalg.solve(H, grad)
            theta -= step
            if np.max(np.abs(step)) < self.tol:
                break
        self.coef_ = theta[:d][None, :]
        self.intercept_ = theta[d:].copy()
        return self

    def predict_proba(self, X):
        p = _sigmoid(np.asarray(X, dtype=float) @ self.coef_[0] + self.intercept_[0])
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)


class Pipeline:
    def __init__(self, steps):
        self.steps = steps
        self.named_steps = dict(steps)

    def fit(self, X, y):
        Z = X
        for _, est in self.steps[:-1]:
            Z = est.fit_transform(Z) if hasattr(est, "fit_transform") else est.fit(Z).transform(Z)
        self.steps[-1][1].fit(Z, y)
        return self

    def _transform(self, X):
        for _, est in self.steps[:-1]:
            X = est.transform(X)
        return X

    def predict(self, X):
        return self.steps[-1][1].predict(self._transform(X))


def kfold_indices(n, k):
    sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
    idx = np.arange(n)
    start = 0
    for s in sizes:
        test = idx[start:start + s]
        train = np.concatenate([idx[:start], idx[start + s:]])
        yield train, test
        start += s


def cross_val_accuracy(make_estimator, X, y, k=5):
    X, y = np.asarray(X), np.asarray(y)
    scores = []
    for train, test in kfold_indices(len(X), k):
        model = make_estimator().fit(X[train], y[train])          # fresh model per fold: no leakage
        scores.append(float((model.predict(X[test]) == y[test]).mean()))
    return scores
```

- **The estimator API is the design**: every component has `fit`/`transform`/`predict`, so a `Pipeline` composes them without knowing what they are. That's the Composite plus Strategy patterns behind scikit-learn's whole ecosystem.
- **PCA by SVD** of the centred data is numerically better than an eigendecomposition of the covariance. Fixing the sign of each component makes results reproducible across platforms, which is exactly why scikit-learn does it too.
- **Newton's method** for L2-regularised logistic regression converges quadratically. The objective is strictly convex, so the optimum is unique and matches scikit-learn's L-BFGS solution to 1e-5, as the judge verifies.
- **Cross-validation without leakage**: the scaler and PCA are refitted *inside* each training fold through the pipeline. Fitting them on all the data first is a classic, subtle way to inflate accuracy.
