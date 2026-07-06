---
name: xgboost-3-3-0
description: Train, tune, and deploy XGBoost 3.3.0 models for regression, classification, ranking, survival analysis, and multi-target tasks. Use when the user asks about gradient boosting, tree ensembles, XGBoost hyperparameter tuning, feature importance, or structured tabular ML. Covers scikit-learn API, native API, distributed training, custom objectives, and interpretability.
metadata:
  tags:
    - ai-ml
    - gradient-boosting
    - tabular
    - trees
    - regression
    - classification
    - ranking
---

# xgboost 3.3.0

## Overview

**XGBoost 3.3.0** is an optimized distributed gradient boosting library for structured/tabular data. It implements tree boosting (GBDT/GBM), linear boosting, and DART (dropout additive regression trees). The default `hist` tree method with GPU support delivers fast, accurate models on datasets from thousands to billions of rows.

Key capabilities:
- Regression, binary/multi-class classification, ranking (LTR), survival analysis (Cox, AFT), quantile regression, expectile regression, Poisson, Gamma, Tweedie
- Scikit-learn API (`XGBClassifier`, `XGBRegressor`, `XGBRanker`, `XGBRFClassifier`, `XGBRFRegressor`) and native API (`train`, `cv`, `Booster`, `DMatrix`)
- GPU acceleration via `device="cuda"` with `hist` and `approx` tree methods
- Native categorical feature support (`enable_categorical=True`)
- QuantileDMatrix for memory-efficient training on large datasets
- ExtMemQuantileDMatrix for out-of-core learning
- Multi-target regression and multi-class classification with vector-leaf trees
- Callback system for early stopping, checkpoints, learning rate scheduling
- Feature importance (weight, gain, cover), SHAP-like contributions (`predict contrib=True`), tree plotting

## Usage

### Installation

```bash
pip install xgboost==3.3.0
```

For GPU support, install a wheel with CUDA or build from source. The `hist` tree method (default) works on GPU.

### Scikit-Learn API (Recommended)

The scikit-learn interface is the simplest path for most tasks.

```python
import xgboost as xgb
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

X, y = make_classification(n_samples=10000, n_features=20, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Classification
clf = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="logloss",
    early_stopping_rounds=10,
    random_state=42,
    n_jobs=-1,
)
clf.fit(
    X_train, y_train,
    eval_set=[(X_val, y_val)],
    verbose=10,
)

# Predict probabilities and classes
proba = clf.predict_proba(X_val)
preds = clf.predict(X_val)

# Feature importance
importances = clf.get_booster().get_score(importance_type="gain")
```

```python
# Regression
reg = xgb.XGBRegressor(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    tree_method="hist",
    eval_metric="rmse",
    early_stopping_rounds=10,
    random_state=42,
)
reg.fit(X_train, y_train, eval_set=[(X_val, y_val)])
```

```python
# Random Forest (XGBoost's implementation)
rf = xgb.XGBRFClassifier(
    n_estimators=100,
    max_depth=6,
    subsample=0.8,
    colsample_bynode=0.8,
    random_state=42,
)
rf.fit(X_train, y_train)
```

### GPU Training

```python
clf = xgb.XGBClassifier(
    device="cuda",           # or "cuda:0", "gpu"
    tree_method="hist",      # hist or approx on GPU
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
)
clf.fit(X_train, y_train, eval_set=[(X_val, y_val)])
```

### Native API

For fine-grained control, callbacks, and custom objectives:

```python
import xgboost as xgb
import numpy as np

dtrain = xgb.DMatrix(X_train, label=y_train)
dval = xgb.DMatrix(X_val, label=y_val)

params = {
    "objective": "binary:logistic",
    "eval_metric": ["logloss", "auc"],
    "max_depth": 6,
    "learning_rate": 0.1,
    "tree_method": "hist",
    "verbosity": 1,
}

evals_result = {}
model = xgb.train(
    params,
    dtrain,
    num_boost_round=200,
    evals=[(dtrain, "train"), (dval, "val")],
    early_stopping_rounds=10,
    evals_result=evals_result,
    verbose_eval=10,
)

# Predict
preds = model.predict(dval)

# Save and load
model.save_model("model.json")
loaded = xgb.Booster()
loaded.load_model("model.json")
```

### Cross-Validation

```python
cv_results = xgb.cv(
    params,
    dtrain,
    num_boost_round=200,
    nfold=5,
    stratified=True,
    as_pandas=True,
    seed=42,
)
```

### Early Stopping with Best Model

```python
from xgboost.callback import EarlyStopping

callbacks = [
    EarlyStopping(
        stopping_rounds=10,
        save_best=True,       # returns best model, not last
        minimize=True,
    )
]

model = xgb.train(params, dtrain, num_boost_round=200,
                  evals=[(dval, "val")], callbacks=callbacks)
# model is now the best iteration
```

### Categorical Features

XGBoost handles categoricals natively — no one-hot encoding needed:

```python
import pandas as pd

df = pd.read_csv("data.csv")
df["category_col"] = df["category_col"].astype("category")

clf = xgb.XGBClassifier(enable_categorical=True)
clf.fit(df.drop("target", axis=1), df["target"])
```

### Quantile Regression

```python
reg = xgb.XGBRegressor(
    objective="reg:quantileerror",
    quantile_alpha=[0.1, 0.5, 0.9],
    n_estimators=200,
    learning_rate=0.1,
)
reg.fit(X_train, y_train)
```

### Ranking (Learning to Rank)

```python
from xgboost import XGBRanker

ranker = XGBRanker(
    objective="rank:ndcg",
    eval_metric=["ndcg@3", "map@5"],
    n_estimators=200,
    learning_rate=0.1,
)

# group = array of group sizes (data must be sorted by query)
ranker.fit(X_train, y_train, group=[10, 20, 15, ...])
```

## Gotchas

- **`hist` is the default tree method** — since 2.0, `tree_method="hist"` is default. It is fast and memory-efficient. Use `auto` only if you need backward compatibility with pre-2.0 code.
- **`booster=gblinear` is deprecated** in 3.3.0 and will be removed. Use `gbtree` (default) or `dart`.
- **`predictor` parameter is removed** — use `device` for GPU selection.
- **`ntree_limit` is removed** — use `iteration_range` in `predict()` or `Booster.__getitem__()` for slicing.
- **`gblinear` deprecation** — if you need linear models, use scikit-learn's `LinearRegression`/`LogisticRegression` or switch to `gbtree` with `max_depth=1`.
- **Categorical features need `enable_categorical=True`** — XGBoost will not auto-detect categoricals; set this explicitly or pass `feature_types=["c", ...]`.
- **`exact` tree method does not support categoricals** — use `hist` (default) or `approx`.
- **`enable_categorical` defaults to `True`** in the sklearn interface since 2.1. If you one-hot encode manually, set `enable_categorical=False` to avoid double-encoding.
- **`base_score` is auto-estimated** by default (since 3.1.0). To disable, pass an explicit float (e.g., `base_score=0.5`).
- **Early stopping returns last model, not best** — unless you use the `EarlyStopping(save_best=True)` callback. The `early_stopping_rounds` parameter on `fit()` uses the default callback behavior.
- **`eval_metric` defaults depend on objective** — `rmse` for regression, `logloss` for binary classification, `mlogloss` for multi-class. Explicitly set `eval_metric` for clarity.
- **`n_jobs=-1` uses all cores** — but can oversubscribe on shared machines. Pin to a specific count in production.
- **`QuantileDMatrix` is used internally** by the sklearn interface when `tree_method` is `hist` or `auto`. It saves memory but has a one-time preprocessing cost.
- **`inf` values cause errors** — XGBoost does not accept `inf` or `-inf`. Replace with `NaN` (which XGBoost handles) or clip.
- **`seed` vs `random_state`** — in sklearn API, use `random_state`. In native API, use `seed` in params.
- **Model format** — `.json` is the default and recommended. `.ubj` (ProtocolBuffer) is legacy. `.raw` is binary.
- **`scale_pos_weight` vs class weights** — `scale_pos_weight` is the native XGBoost way; sklearn's `class_weight="balanced"` is also supported via the sklearn interface.
- **`device` in distributed environments** — do not use `cuda:<ordinal>` in distributed training; use `cuda` or `gpu` and let the framework manage GPUs.
- **`max_depth=0` means unlimited** — this is valid but dangerous with `hist`; memory grows exponentially with depth.

## References

- [01-sklearn-api](references/01-sklearn-api.md) — Full scikit-learn API: XGBClassifier, XGBRegressor, XGBRanker, XGBRFClassifier, XGBRFRegressor, fit/predict/save methods
- [02-native-api](references/02-native-api.md) — Native API: train(), cv(), Booster, DMatrix, QuantileDMatrix, ExtMemQuantileDMatrix, DataIter
- [03-parameters](references/03-parameters.md) — Complete parameter reference: general, tree, task-specific, LTR, Tweedie, quantile, expectile, AFT survival
- [04-objectives-metrics](references/04-objectives-metrics.md) — All objectives and evaluation metrics with usage guidance
- [05-data-inputs](references/05-data-inputs.md) — Supported data formats: NumPy, Pandas, PyArrow, cuDF, CuPy, sparse, external memory
- [06-advanced-topics](references/06-advanced-topics.md) — Callbacks, custom objectives/metrics, SHAP/contributions, model slicing, interpretability, distributed training, hyperparameter tuning
- [07-gpu-and-performance](references/07-gpu-and-performance.md) — GPU setup, tree methods, memory optimization, QuantileDMatrix, performance tuning
