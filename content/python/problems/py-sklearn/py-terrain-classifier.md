---
id: py-terrain-classifier
title: Terrain Classifier with scikit-learn Pipelines
difficulty: Hard
order: 1
tags: scikit-learn, Pipeline, ColumnTransformer, cross-validation, metrics, leakage
time_limit: 10
---
## Statement
A wheeled robot classifies the terrain under it (`grass`, `gravel`, `tile`) from wheel-vibration features. The data is a pandas DataFrame with numeric columns `vib_rms`, `current`, `speed`, a categorical column `wheel` (`front`/`rear`) and the label `terrain`. Implement, **with scikit-learn**:

```python
def build_pipeline(C=1.0):
    """Unfitted Pipeline: ColumnTransformer(StandardScaler on vib_rms/current/speed,
    OneHotEncoder(handle_unknown="ignore") on wheel) followed by LogisticRegression(C=C, max_iter=2000)."""

def best_C(df, Cs):
    """Choose C from Cs by 5-fold StratifiedKFold(shuffle=True, random_state=0) cross-validation of
    build_pipeline(C) with scoring="f1_macro" (GridSearchCV). Return the best C (ties -> first in Cs)."""

def evaluate(model, df):
    """Return dict(accuracy=..., macro_f1=..., confusion=[[...]]) on df, with labels ordered
    ["grass", "gravel", "tile"]; floats rounded to 3 decimals."""
```

The driver generates training and test sets with a fixed seed, fits on training only, and reports test metrics. Preprocessing **must** live inside the pipeline: the driver refits on shifted data to detect leakage.

## Starter
```python
from sklearn.linear_model import LogisticRegression

FEATURES = ["vib_rms", "current", "speed"]

def build_pipeline(C=1.0):
    return LogisticRegression(C=C)

def best_C(df, Cs):
    return Cs[0]

def evaluate(model, df):
    acc = (model.predict(df[FEATURES]) == df["terrain"]).mean()
    return {"accuracy": round(float(acc), 3), "macro_f1": 0.0, "confusion": []}
```

## Driver
```python
import sys
import numpy as np
import pandas as pd

def make(n, seed, shift=0.0):
    rng = np.random.default_rng(seed)
    terrain = rng.choice(["grass", "gravel", "tile"], n, p=[0.5, 0.3, 0.2])
    base = {"grass": 0.8, "gravel": 2.5, "tile": 1.4}
    vib = np.array([base[t] for t in terrain]) * 100 + rng.normal(0, 25, n) + shift
    current = np.array([{"grass": 3.0, "gravel": 4.2, "tile": 2.2}[t] for t in terrain]) + rng.normal(0, 0.5, n)
    speed = rng.uniform(0.2, 1.5, n)
    wheel = rng.choice(["front", "rear"], n)
    vib = vib * np.where(wheel == "rear", 1.15, 1.0)
    return pd.DataFrame({"vib_rms": vib, "current": current * 1000, "speed": speed, "wheel": wheel, "terrain": terrain})

train, test = make(1500, 1), make(600, 2)
for cmd in sys.stdin.read().split():
    if cmd == "structure":
        p = build_pipeline(0.5)
        steps = [type(s).__name__ for _, s in p.steps] if hasattr(p, "steps") else [type(p).__name__]
        print("steps:", steps)
        if hasattr(p, "steps"):
            ct = p.steps[0][1]
            print("transformers:", sorted((type(t).__name__, tuple(cols)) for _, t, cols in ct.transformers))
            print("C:", p.steps[-1][1].C, "max_iter:", p.steps[-1][1].max_iter)
    elif cmd == "cv":
        print("best C:", best_C(train, [0.001, 0.01, 0.1, 1.0, 10.0]))
    elif cmd == "eval":
        m = build_pipeline(1.0).fit(train.drop(columns="terrain"), train["terrain"])
        print("test:", evaluate(m, test))
        unseen = test.copy(); unseen.loc[:5, "wheel"] = "middle"
        print("unseen category ok:", len(m.predict(unseen.drop(columns="terrain"))) == len(unseen))
    elif cmd == "leak":
        shifted = make(1500, 3, shift=500.0)
        m = build_pipeline(1.0).fit(shifted.drop(columns="terrain"), shifted["terrain"])
        print("shifted:", evaluate(m, make(600, 4, shift=500.0))["accuracy"] > 0.8)
```

## Tests
=== sample
structure
eval
---
steps: ['ColumnTransformer', 'LogisticRegression']
transformers: [('OneHotEncoder', ('wheel',)), ('StandardScaler', ('vib_rms', 'current', 'speed'))]
C: 0.5 max_iter: 2000
test: {'accuracy': 0.94, 'macro_f1': 0.93, 'confusion': [[287, 2, 13], [0, 176, 0], [21, 0, 101]]}
unseen category ok: True
=== hidden
cv
leak
eval
---
best C: 10.0
shifted: True
test: {'accuracy': 0.94, 'macro_f1': 0.93, 'confusion': [[287, 2, 13], [0, 176, 0], [21, 0, 101]]}
unseen category ok: True

## Hints
- `make_pipeline(ColumnTransformer([("num", StandardScaler(), NUM), ("cat", OneHotEncoder(handle_unknown="ignore"), ["wheel"])]), LogisticRegression(C=C, max_iter=2000))`.
- Fit with `df.drop(columns="terrain")` (the ColumnTransformer selects the columns by name) and `df["terrain"]`.
- `GridSearchCV(build_pipeline(), {"logisticregression__C": Cs}, cv=StratifiedKFold(5, shuffle=True, random_state=0), scoring="f1_macro")`. Its `best_params_` returns the first best on ties.
- Metrics: `accuracy_score`, `f1_score(average="macro")`, `confusion_matrix(labels=[...]).tolist()`.

## Solution
```python
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUM = ["vib_rms", "current", "speed"]
LABELS = ["grass", "gravel", "tile"]

def build_pipeline(C=1.0):
    pre = ColumnTransformer([
        ("num", StandardScaler(), NUM),
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["wheel"]),
    ])
    return make_pipeline(pre, LogisticRegression(C=C, max_iter=2000))

def best_C(df, Cs):
    search = GridSearchCV(build_pipeline(), {"logisticregression__C": list(Cs)},
                          cv=StratifiedKFold(5, shuffle=True, random_state=0), scoring="f1_macro")
    search.fit(df.drop(columns="terrain"), df["terrain"])
    return search.best_params_["logisticregression__C"]

def evaluate(model, df):
    y = df["terrain"]
    pred = model.predict(df.drop(columns="terrain"))
    return {
        "accuracy": round(float(accuracy_score(y, pred)), 3),
        "macro_f1": round(float(f1_score(y, pred, average="macro")), 3),
        "confusion": confusion_matrix(y, pred, labels=LABELS).tolist(),
    }
```

- **The pipeline is the model.** Scaling and encoding statistics are learned in `fit` on the training data only, and replayed in `predict`. That's what makes cross-validation honest: each fold refits the scaler on its own training part. It's also why the shifted-data test works, since the scaler adapts to whatever data the pipeline is trained on.
- **Feature scales** differ by about 1000× here (current in mA versus speed in m/s). Without the `StandardScaler`, regularised logistic regression penalises the features unevenly and converges poorly.
- `handle_unknown="ignore"` makes the encoder output all zeros for a category never seen in training (a new wheel position) instead of crashing in production.
- **Macro F1** weights every class equally, so the rare `tile` class counts as much as `grass`. Accuracy alone would hide poor performance on it.
