---
name: chimeraboost-0-13-0
description: Train and deploy ChimeraBoost 0.13.0 gradient boosting models for regression, quantile regression, binary and multiclass classification. Use when the user needs a fast, pure-Python GBDT with CatBoost-style ordered target statistics for categorical features, oblivious trees, bagging (n_ensembles), exact TreeSHAP, linear-leaf trees, temperature-scaled probabilities, and automatic early stopping. Pure Python with numba backend — no C/C++ compilation. Apache 2.0 license.
metadata:
  tags:
    - ai-ml
    - gradient-boosting
    - decision-trees
    - tabular
    - classification
    - regression
    - quantile-regression
    - categorical-features
    - shap
    - pure-python
    - numba
    - scikit-learn
---

# chimeraboost 0.13.0

## Overview

**ChimeraBoost** (v0.13.0) is a CatBoost-inspired gradient boosting library implemented entirely in Python with a numba-accelerated backend. It combines ordered target statistics for categoricals, oblivious (symmetric) trees, and histogram-based splitting into a single scikit-learn-compatible library with zero compiled extensions.

Key capabilities:
- **Regression** — RMSE (squared error), MAE (median), Quantile (pinball loss at any alpha)
- **Classification** — binary (logloss) and multiclass (softmax), auto-detected from number of classes
- **Categorical features** — CatBoost-style ordered target statistics with configurable smoothing and permutations; no manual encoding
- **Oblivious trees** — symmetric tree structure (same split at each level), strongly regularized and fast
- **Bagging** — `n_ensembles` trains independent bootstrap members, averaged at predict time
- **Exact SHAP** — interventional TreeSHAP computed exactly (not sampled) via oblivious tree structure; includes linear-leaf slopes
- **Linear-leaf trees** — ridge linear model per leaf over numeric split features for local slope
- **Temperature-scaled probabilities** — `predict_proba` calibrated on validation split via temperature scaling
- **Automatic early stopping** — on by default with internal holdout; grouped splits via `groups` argument
- **Sample weights** — per-sample training weights, normalized to mean 1
- **NaN handling** — NaN routed to dedicated histogram bin, no imputation needed
- **Pure Python** — depends only on numpy, numba, scikit-learn, scipy, pandas; no compilation step

## Usage

### Installation

```bash
pip install chimeraboost==0.13.0
```

Requires Python 3.9+. Dependencies: numpy, numba, scikit-learn, scipy, pandas.

### Quick Start — Classification

```python
from chimeraboost import ChimeraBoostClassifier
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

X, y = load_breast_cancer(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)

clf = ChimeraBoostClassifier(n_estimators=1000, random_state=0)
clf.fit(Xtr, ytr, eval_set=(Xte, yte))

proba = clf.predict_proba(Xte)
preds = clf.predict(Xte)
auc = roc_auc_score(yte, proba[:, 1])
print(f"AUC={auc:.4f}  trees={clf.best_iteration_}")
```

### Quick Start — Regression

```python
from chimeraboost import ChimeraBoostRegressor

reg = ChimeraBoostRegressor(n_estimators=2000, random_state=0)
reg.fit(X_train, y_train)
y_pred = reg.predict(X_test)
```

### Categorical Features

Pass categorical columns by integer position or by name (for DataFrames):

```python
# By position
clf.fit(X, y, cat_features=[0, 3])

# By name (DataFrame)
clf.fit(df, y, cat_features=["city", "device_type"])

# Via constructor (for GridSearchCV / Pipeline compatibility)
clf = ChimeraBoostClassifier(cat_features=["city", "brand"])
```

Categorical columns can be strings or objects; the rest of the matrix stays numeric. NaN in categorical columns is handled naturally.

### Quantile Regression

```python
lo = ChimeraBoostRegressor(loss="Quantile", alpha=0.05, random_state=0).fit(Xtr, ytr)
md = ChimeraBoostRegressor(loss="Quantile", alpha=0.50, random_state=0).fit(Xtr, ytr)
hi = ChimeraBoostRegressor(loss="Quantile", alpha=0.95, random_state=0).fit(Xtr, ytr)

lower, median, upper = lo.predict(Xte), md.predict(Xte), hi.predict(Xte)
```

Quantile models default to `depth=4` (shallower than RMSE's `depth=6`) to avoid overfitting tail quantiles.

### Bagging

```python
reg = ChimeraBoostRegressor(n_ensembles=10, ensemble_n_jobs=-1, random_state=0)
reg.fit(X_train, y_train)
```

Averages predictions (regressor) or soft-votes calibrated probabilities (classifier). `feature_importances_` and `shap_values` average across the bag automatically.

### Early Stopping

On by default. Holds out `validation_fraction=0.2` (stratified for classifiers):

```python
# Default: automatic internal holdout
m = ChimeraBoostRegressor(random_state=0).fit(X_train, y_train)

# Explicit validation set (overrides internal split)
m.fit(X_train, y_train, eval_set=(X_val, y_val))

# Grouped split (keeps groups intact)
m.fit(X_train, y_train, groups=subject_ids)

# Disable early stopping (fixed tree count)
m = ChimeraBoostRegressor(early_stopping=False, n_estimators=500, random_state=0)
```

### SHAP Explanations

```python
phi = reg.shap_values(X_test)           # (n_samples, n_features)
base = reg.expected_value_              # baseline, set by the call above

# Efficiency: contributions + baseline = prediction (to ~1e-14)
assert abs(phi.sum(axis=1) + base - reg.predict(X_test)).max() < 1e-6
```

Exact interventional TreeSHAP — not sampled. Works for regression and binary classification; multiclass raises `NotImplementedError`.

### Cross-Validation and Hyperparameter Search

Standard scikit-learn compatibility:

```python
from sklearn.model_selection import cross_val_score, GridSearchCV

scores = cross_val_score(
    ChimeraBoostRegressor(random_state=0), X, y, cv=5,
    scoring="neg_root_mean_squared_error",
)

search = GridSearchCV(
    ChimeraBoostRegressor(cat_features=[0, 3], random_state=0),
    {"depth": [6, 8, 10], "l2_leaf_reg": [1.0, 3.0]},
    cv=5,
)
search.fit(X, y)
```

Set `cat_features` on the constructor so `GridSearchCV`/`Pipeline` carry it.

### Save and Load

```python
import joblib

joblib.dump(reg, "model.joblib")
reg = joblib.load("model.joblib")
```

### Interaction-Heavy Regression

Raise `depth` to 8–10 for large, interaction-heavy problems:

```python
reg = ChimeraBoostRegressor(depth=10, linear_leaves=True, random_state=0).fit(Xtr, ytr)
```

### Reproducibility

```python
m = ChimeraBoostRegressor(random_state=0, thread_count=4).fit(Xtr, ytr)
```

Deterministic for a fixed `thread_count`. `thread_count=None` or `-1` uses all cores.

## Gotchas

- **`cat_features` must be passed explicitly** — ChimeraBoost does not auto-detect categorical columns. Pass via `fit(cat_features=[...])` or constructor `cat_features=[...]` for GridSearchCV compatibility. Names are resolved against the DataFrame at fit time.
- **NaN is accepted, inf is not** — NaN routes to a dedicated histogram bin. `inf`/`-inf` raises `ValueError`; clip or replace first.
- **Sparse matrices are not supported** — pass dense arrays. NumPy, pandas DataFrames, and PyArrow tables all work.
- **Masked arrays silently drop the mask** — `np.ma.MaskedArray` is rejected with guidance. Convert via `X.filled(np.nan)`.
- **`linear_leaves` is auto-on for binary classification** — `None` (default) enables it for binary, disables for multiclass. Explicit `True` on multiclass raises `NotImplementedError`. Not available with MAE or Quantile loss (silently ignored with a warning).
- **`linear_leaves` falls back to constant below ~1000 rows** — not enough data per leaf to fit a ridge model.
- **`shap_values` is binary/regression only** — multiclass raises `NotImplementedError`.
- **Classifier SHAP is in log-odds (margin) space** — not probability space. Contributions sum to `raw_log_odds - expected_value_`.
- **`early_stopping=True` is the default** — model holds out 20% internally. Pass `eval_set` to use your own validation split instead.
- **`early_stopping_rounds` defaults to 50** — not 10. The 50-round patience beats 10 on 25/34 benchmark datasets.
- **`min_child_weight` is auto-adaptive for the classifier** — `None` resolves to a size-adaptive value: full veto below ~500 rows, off above ~2000. For the regressor, default is `1.0`.
- **`learning_rate` defaults to `None`** — resolves to `0.1` when early stopping is active.
- **`depth` is loss-adaptive** — defaults to 6 for RMSE/MAE, 4 for Quantile. Deep trees overfit tail quantiles.
- **`cat_combinations` auto-enables for all-categorical data only** — pairwise categorical features help on purely categorical data but crowd out numerics on mixed data. Set `True`/`False` to force.
- **`n_ensembles > 1` does not support callbacks** — members fit in parallel worker processes, so per-round hooks are incompatible.
- **`staged_predict` not available with bagging** — raises `NotImplementedError` when `n_ensembles > 1`.
- **`validation_history_` is empty without eval_set** — when no validation split is available (too small data or `early_stopping=False` without `eval_set`), the history is empty.
- **`temperature_` > 1 means over-confident raw scores** — the classifier applies temperature scaling on the validation split. `predict()` and AUC are unchanged (monotonic transform); only `predict_proba()` is calibrated.
- **`ordered_boosting` defaults to `False`** — uses plain Newton updates. Enable for leave-one-out leaf training step (CatBoost-style). Mutually exclusive with `leaf_estimation_iterations` in the booster.
- **`leaf_estimation_iterations` differs by estimator** — default 1 for regressor, 3 for classifier.
- **`subsample` uses Minimum Variance Sampling** — below 1.0, rows are drawn gradient-weighted (unbiased), not uniformly.
- **`feature_importances_` ignores linear-leaf slopes** — gain importance measures split structure only. Use `shap_values` for a faithful decomposition that includes linear-leaf contributions.
- **`cat_smoothing` must be > 0** — it is the Bayesian pseudocount in the encoder denominator; 0 is undefined.
- **`random_state` + fixed `thread_count` gives determinism** — floating-point reductions across threads can vary; pin `thread_count` for exact reproducibility.
- **`best_iteration_` for bagged models is the mean** — rounded mean of members' best iterations.
- **`groups` only affects auto-split** — when `eval_set` is passed explicitly, `groups` is ignored.
- **`sample_weight` applies to training only** — the validation eval metric is always unweighted. Weights are normalized to mean 1 internally.
- **`cat_features` at `fit()` overrides constructor** — the constructor form exists for `GridSearchCV`/`Pipeline`; passing at `fit()` takes priority.
- **`validation_fraction` is ignored with explicit `eval_set`** — the internal split is skipped entirely.
- **`max_bins` default is 128** — raising can improve fit on some datasets but increases memory.
- **`ensemble_n_jobs=-1` uses all cores** — can oversubscribe on shared machines. Pin to a specific count in production.
- **`pyarrow.Table.columns` is not column names** — ChimeraBoost uses `.column_names` for pyarrow to avoid extracting column data as names.
- **`cat_features` can mix indices and names** — `cat_features=[0, "city", 3]` is valid; names resolved against the DataFrame at fit.
- **`multiclass` uses softmax automatically** — no configuration needed. The classifier detects 3+ classes and switches internally.
- **`predict_proba` columns follow `classes_` order** — `classes_` preserves original label values (including strings).
- **`shap_values` with bagging averages across members** — exact for regression (linear), additive surrogate for classification.
- **`X_background` in `shap_values` overrides reference** — defaults to a training data sample captured at fit. Cost scales linearly with background size.

## References

- [01-regressor](references/01-regressor.md) — ChimeraBoostRegressor: full parameter reference, fit/predict methods, attributes, loss options
- [02-classifier](references/02-classifier.md) — ChimeraBoostClassifier: full parameter reference, binary/multiclass behavior, temperature scaling, attributes
- [03-losses](references/03-losses.md) — Loss functions: RMSE, MAE, Quantile, Logloss, MultiSoftmax with gradient/hessian details
- [04-shap](references/04-shap.md) — Exact TreeSHAP: interventional formulation, efficiency property, background distribution, per-leaf linear inclusion
- [05-advanced](references/05-advanced.md) — Callbacks, staged_predict, validation_history_, hyperparameter tuning, reproducibility, performance tips
