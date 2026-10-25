# Machine Learning with scikit-learn

scikit-learn is the standard library for classical machine learning in Python: regression, classification, clustering, dimensionality reduction, model selection and preprocessing, all behind one consistent **estimator API**. Even in the deep-learning era, it's the first tool for tabular data, sensor-based classification (terrain type from IMU features, fault detection), baselines, and all the evaluation plumbing (splits, cross-validation, metrics). This lesson covers that API, pipelines that prevent data leakage, model selection, the essential metrics, and the bias–variance trade-off behind overfitting.

## 1. The estimator API

Every model follows the same protocol:

| Method | Meaning |
|---|---|
| `est.fit(X, y)` | learn parameters from training data (returns `self`) |
| `est.predict(X)` | predict labels or values |
| `est.predict_proba(X)` | class probabilities (classifiers that support it) |
| `est.score(X, y)` | default metric (accuracy for classifiers, R² for regressors) |
| `tr.transform(X)` / `fit_transform` | transformers (scalers, PCA, encoders) |
| learned attributes end in `_` | `coef_`, `classes_`, `n_features_in_`, … |

`X` has shape `(n_samples, n_features)` and `y` has shape `(n_samples,)`.

```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

X, y = make_classification(n_samples=1000, n_features=10, n_informative=4, random_state=0)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, stratify=y, random_state=0)
clf = LogisticRegression(max_iter=1000).fit(X_tr, y_tr)
accuracy_score(y_te, clf.predict(X_te))
```

> [!KEY]
> **Never evaluate on data you trained on.** The test set estimates performance on unseen data, and you touch it only once, at the end. Tune hyperparameters with cross-validation on the training set (or a separate validation split). `stratify=y` keeps the class proportions equal across splits.

## 2. Pipelines and data leakage

Preprocessing must be **fitted on training data only**. Fitting a scaler on the whole dataset leaks test-set statistics into training and inflates your scores. Pipelines make the right thing automatic:

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier

pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
pipe.fit(X_tr, y_tr)              # the scaler learns mean/std from X_tr only
pipe.score(X_te, y_te)            # the test data is transformed with the TRAINING statistics

# mixed numeric + categorical columns (e.g. a pandas DataFrame)
pre = ColumnTransformer([
    ("num", StandardScaler(), ["speed", "current", "temp"]),
    ("cat", OneHotEncoder(handle_unknown="ignore"), ["surface"]),
])
model = make_pipeline(pre, RandomForestClassifier(n_estimators=200, random_state=0))
```

## 3. Model selection: cross-validation and grid search

```python
from sklearn.model_selection import cross_val_score, GridSearchCV, StratifiedKFold

scores = cross_val_score(pipe, X_tr, y_tr, cv=5)              # 5 fits, 5 held-out scores
scores.mean(), scores.std()

grid = GridSearchCV(
    make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
    param_grid={"logisticregression__C": [0.01, 0.1, 1, 10]},   # step name + "__" + parameter
    cv=StratifiedKFold(5, shuffle=True, random_state=0), scoring="f1",
)
grid.fit(X_tr, y_tr)
grid.best_params_, grid.best_score_
grid.score(X_te, y_te)                                           # final check on the untouched test set
```

For time-series data (sensor logs), use `TimeSeriesSplit`. Shuffling would let the model peek at the future. For data grouped by robot or by session, use `GroupKFold`, so the same robot never appears in both training and validation.

## 4. Metrics: choose what matters

| Task | Metric | Notes |
|---|---|---|
| balanced classification | accuracy | misleading when classes are imbalanced |
| imbalanced classification | precision, recall, F1, PR-AUC | e.g. rare fault detection |
| ranking/probabilities | ROC-AUC, log loss | threshold-independent |
| regression | MAE, RMSE, R² | RMSE punishes large errors |
| clustering | silhouette, adjusted Rand index | |

```python
from sklearn.metrics import confusion_matrix, classification_report, precision_recall_fscore_support

y_pred = pipe.predict(X_te)
confusion_matrix(y_te, y_pred)               # rows = true class, columns = predicted
print(classification_report(y_te, y_pred, digits=3))
```

- **Precision** = TP / (TP + FP): of the alarms raised, how many were real.
- **Recall** = TP / (TP + FN): of the real faults, how many were caught.

A collision detector needs high recall, while a spam filter wants high precision. Adjust the decision threshold on `predict_proba` to trade one for the other.

## 5. The model zoo (what to reach for)

| Need | Estimators |
|---|---|
| linear baseline | `LinearRegression`, `Ridge`, `Lasso`, `LogisticRegression` |
| strong tabular default | `HistGradientBoostingClassifier/Regressor`, `RandomForest*` |
| small data, smooth boundaries | `SVC` (RBF kernel, needs scaling), `KNeighbors*` |
| interpretability | `DecisionTree*` (shallow), linear models with coefficients |
| clustering | `KMeans`, `DBSCAN` (arbitrary shapes, noise), `AgglomerativeClustering` |
| dimensionality reduction | `PCA`, `TruncatedSVD`; t-SNE/UMAP for visualisation |
| anomaly detection | `IsolationForest`, `OneClassSVM` |

## 6. Overfitting, regularisation and the bias–variance trade-off

- **Underfitting** (high bias): the model is too simple, so training and validation errors are both high.
- **Overfitting** (high variance): the training error is low but the validation error is high. The model memorised noise.

Remedies for overfitting:
- more data
- regularisation (`C` small in logistic regression or SVMs, `alpha` large in Ridge/Lasso)
- shallower trees (`max_depth`, `min_samples_leaf`)
- feature selection
- ensembling (random forests average decorrelated trees)
- early stopping (gradient boosting)

**Learning curves** (score versus training-set size) and **validation curves** (score versus a hyperparameter) diagnose which regime you're in.

```python
from sklearn.model_selection import validation_curve
from sklearn.tree import DecisionTreeClassifier
depths = [1, 2, 4, 8, 16]
train_s, val_s = validation_curve(DecisionTreeClassifier(random_state=0), X_tr, y_tr,
                                  param_name="max_depth", param_range=depths, cv=5)
# training accuracy keeps rising with depth; validation accuracy peaks, then falls: overfitting
```

## 7. Persistence and reproducibility

- Set `random_state` everywhere randomness enters (splits, models).
- Save fitted pipelines with `joblib.dump(model, "model.joblib")` and load them with `joblib.load`. This uses pickle, so only load files you trust.
- Record the library versions alongside the model.
- `sklearn.set_config(transform_output="pandas")` keeps column names through transformers.

## 8. Exam-ready answers

> [!EXAM]
> **Cross-validation and data leakage.** k-fold cross-validation partitions the training data into k folds, trains the model k times on k − 1 folds, and evaluates it on the remaining fold each time; the mean and spread of the k scores estimate generalisation performance more reliably than a single split, and are used to select hyperparameters. Data leakage occurs when information from the evaluation data influences training, for example by fitting a scaler or feature selector on the full dataset, shuffling time-ordered data, or splitting correlated samples (such as recordings of the same subject) across folds; it produces optimistic estimates. Wrapping preprocessing and model in a single pipeline, so that every fold refits the preprocessing on its training part only, together with group-aware or time-ordered splitters, prevents it.

## 9. Cheat sheet

| Need | Code |
|---|---|
| split | `train_test_split(X, y, test_size=.2, stratify=y, random_state=0)` |
| preprocessing + model | `make_pipeline(StandardScaler(), Model())` |
| mixed columns | `ColumnTransformer` |
| CV score | `cross_val_score(pipe, X, y, cv=5)` |
| tune | `GridSearchCV(pipe, {"step__param": [...]}, cv=5)` |
| report | `classification_report`, `confusion_matrix` |
| time series CV | `TimeSeriesSplit` |
| grouped CV | `GroupKFold` |
| save | `joblib.dump` / `joblib.load` |

> [!INTERVIEW]
> **"Your model scores 99% in validation but fails in production. What happened?"** The likely causes are leakage (the scaler fitted on all data, a target-derived feature, duplicate or near-duplicate samples across splits, or future information in time-series features), a distribution shift between training and deployment data, or an imbalanced test set where accuracy hides poor recall. Diagnose with a pipeline-based CV, group/time-aware splits, per-class metrics, and by checking the feature pipeline that runs in production against the one used in training.
