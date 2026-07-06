---
name: lightgbm-4-6-0
description: Train, tune, and deploy LightGBM 4.6.0 gradient boosting models for regression, binary/multiclass classification, ranking, and custom objectives. Use when the user asks about LightGBM, gradient boosting on tabular data, tree-based ensemble models, or needs fast accurate predictions on structured data. Covers native API (Dataset/Booster/train/cv), scikit-learn API (LGBMClassifier/LGBMRegressor/LGBMRanker), callbacks, custom objectives/metrics, SHAP-style contributions, GPU/CUDA acceleration, and distributed training.
metadata:
  tags:
    - ai-ml
    - gradient-boosting
    - tabular
    - classification
    - regression
    - ranking
    - lightgbm
    - microsoft
---

# lightgbm 4.6.0

## Overview

LightGBM 4.6.0 is a highly efficient gradient boosting framework using leaf-wise (best-first) tree growth with histogram-based split finding. It supports regression, binary and multiclass classification, learning-to-rank, and custom objectives. Key advantages over other boosting libraries: faster training via histogram binning and exclusive feature bundling, lower memory usage, leaf-wise growth for better accuracy per tree, and native GPU/CUDA support.

Two API styles are available:
- **Native API** (`lightgbm.Dataset`, `lightgbm.Booster`, `lightgbm.train`, `lightgbm.cv`) — full control, callbacks, custom objectives/metrics
- **Scikit-learn API** (`LGBMClassifier`, `LGBMRegressor`, `LGBMRanker`) — drop-in replacement for sklearn estimators

### Core Algorithm Concepts

- **Histogram-based splits**: continuous values bucketed into `max_bin` (default 255) discrete bins, reducing split evaluation from O(#data) to O(#bins)
- **Leaf-wise growth**: splits the leaf with maximum loss delta, not level-wise. Achieves lower loss per tree but can overfit on small data — constrain with `max_depth` or `min_data_in_leaf`
- **GOSS** (Gradient-based One-Side Sampling) and **bagging**: subsampling strategies for speed and regularization
- **EFB** (Exclusive Feature Bundling): bundles mutually exclusive sparse features to reduce dimensionality

## Usage

### Installation

```bash
pip install lightgbm==4.6.0
```

For GPU support, build from source (see references). Pre-built wheels do not include GPU/CUDA.

### Native API — Training Pipeline

```python
import lightgbm as lgb
import numpy as np

# 1. Create Dataset objects
train_data = lgb.Dataset(X_train, label=y_train)
valid_data = lgb.Dataset(X_valid, label=y_valid, reference=train_data)

# 2. Define parameters
params = {
    "objective": "binary",
    "metric": ["binary_logloss", "auc"],
    "learning_rate": 0.05,
    "num_leaves": 31,
    "verbose": -1,
}

# 3. Train with callbacks
callbacks = [
    lgb.early_stopping(stopping_rounds=50, verbose=True),
    lgb.log_evaluation(period=100),
    lgb.record_evaluation(eval_result={}),
]

model = lgb.train(
    params=params,
    train_set=train_data,
    num_boost_round=1000,
    valid_sets=[valid_data],
    valid_names=["valid"],
    callbacks=callbacks,
)

# 4. Predict
y_pred = model.predict(X_test)
y_proba = model.predict(X_test, raw_score=False)  # probabilities for classification
```

### Scikit-learn API

```python
from lightgbm import LGBMClassifier, LGBMRegressor, LGBMRanker

# Classification
clf = LGBMClassifier(n_estimators=200, learning_rate=0.05, num_leaves=31, verbose=-1)
clf.fit(X_train, y_train, eval_set=[(X_valid, y_valid)])
y_pred = clf.predict(X_test)
y_proba = clf.predict_proba(X_test)

# Regression
reg = LGBMRegressor(n_estimators=200, learning_rate=0.05, verbose=-1)
reg.fit(X_train, y_train)

# Ranking
ranker = LGBMRanker(n_estimators=200, verbose=-1)
ranker.fit(X_train, y_train, group=train_groups)
```

### Cross-Validation

```python
results = lgb.cv(
    params=params,
    train_set=train_data,
    num_boost_round=1000,
    nfold=5,
    stratified=True,
    callbacks=[lgb.early_stopping(50)],
)
```

### Key Parameters

| Parameter | Default | Purpose |
|---|---|---|
| `objective` | `regression` | Loss function (binary, multiclass, lambdarank, etc.) |
| `metric` | auto | Evaluation metric(s) on validation sets |
| `learning_rate` | 0.1 | Shrinkage rate; lower = more trees needed |
| `num_leaves` | 31 | Max leaves per tree; controls complexity |
| `num_iterations` | 100 | Number of boosting rounds |
| `max_depth` | -1 (no limit) | Max tree depth; use to prevent overfitting |
| `min_data_in_leaf` | 20 | Min samples per leaf; primary overfitting guard |
| `feature_fraction` | 1.0 | Fraction of features sampled per tree |
| `bagging_fraction` | 1.0 | Fraction of data sampled per round |
| `bagging_freq` | 0 | Bagging interval (0 = disabled) |
| `lambda_l1` / `lambda_l2` | 0.0 | L1/L2 regularization on leaf weights |
| `min_gain_to_split` | 0.0 | Min gain required to make a split |
| `max_bin` | 255 | Max histogram bins per feature |
| `verbose` | 1 | Verbosity: <0 fatal, 0 error, 1 info, >1 debug |

### Categorical Features

Pass categorical features natively — no one-hot encoding needed. LightGBM uses a specialized O(k log k) split-finding algorithm for categoricals.

```python
# Python: mark columns as categorical
train_data = lgb.Dataset(X_train, label=y_train, categorical_feature=["col_a", "col_b"])

# Or via params
params = {"categorical_feature": [0, 2]}  # by index

# sklearn API
clf = LGBMClassifier(categorical_feature=["col_a", "col_b"])
```

### Missing Values

LightGBM handles missing values natively — it learns the best default direction for each split. Use `np.nan` (Python), `NA` (CLI/R). Do not encode missing as 0 unless you want zeros treated as missing via `zero_as_missing=true`.

### Feature Importance and SHAP Values

```python
# Feature importance
importance = model.feature_importance(importance_type="split")  # or "gain"

# SHAP-style contributions (built-in, no shap package needed)
shap_values = model.predict(X, pred_contrib=True)
# shape: (n_samples, n_features + 1), last column = expected value
```

### Model Persistence

```python
# Save / load
model.save_model("model.txt")
model = lgb.Booster(model_file="model.txt")

# Continue training from saved model
model = lgb.train(params, train_data, init_model=previous_model)
```

## Gotchas

- **`num_leaves` vs `max_depth`**: Leaf-wise growth means `num_leaves` (default 31) can produce trees much deeper than depth-5. Rule of thumb: `num_leaves < 2^max_depth`. Set `max_depth` explicitly on small datasets to prevent overfitting.
- **`min_data_in_leaf` is approximate**: It is based on Hessian approximation, so occasional leaves may have fewer samples than specified.
- **`bagging_freq` must be > 0 for bagging to work**: Setting `bagging_fraction < 1.0` alone does nothing — you must also set `bagging_freq >= 1`.
- **`is_unbalance` and `scale_pos_weight` are mutually exclusive**: Pick one. `is_unbalance` auto-derives weights; `scale_pos_weight` gives manual control.
- **`categorical_feature` negative values are treated as missing**: If your categories include negative integers, they will be dropped. Re-encode to non-negative integers.
- **`num_threads` should match real CPU cores, not hyperthreads**: Setting it too high for small data degrades performance. Do not change `num_threads` mid-training.
- **Custom objective functions receive raw margins**: For classification, `preds` passed to your function are raw scores (log-odds), not probabilities. Return `(grad, hess)` arrays.
- **`early_stopping` needs at least one validation set**: Without `valid_sets`, early stopping is silently ignored.
- **`keep_training_booster=False` (default) converts the booster to an inner predictor**: This frees datasets but prevents calling `eval()`, `eval_train()`, or `eval_valid()` on the returned model. Set `True` if you need those methods.
- **GPU/CUDA requires building from source**: Pre-built pip wheels are CPU-only. Use `device_type="cuda"` (faster, NVIDIA only) or `device_type="gpu"` (OpenCL, broader GPU support). For GPU, use smaller `max_bin` (e.g., 63) for better speedup.
- **`deterministic=true` slows training**: Use only when reproducible results across `num_threads` settings are needed. Pair with `force_col_wise=true` or `force_row_wise=true` to avoid numerical instability.
- **Parameter aliases**: When both primary name and alias are given, primary name wins. When only aliases are given, the first in LightGBM's internal list wins (arbitrary order). Always use primary names.
- **`metric="None"` (string) disables all metrics**: Do not confuse with Python `None`. Use the string `"None"` to suppress metric output.
- **`multiclass` objective requires `num_class`**: Set `num_class` to the number of classes, or let sklearn API infer it.
- **Ranking tasks need grouped data**: Provide `group` array to Dataset (list of group sizes, data must be pre-sorted by query ID).

## References

- [01-objectives-and-metrics](references/01-objectives-and-metrics.md) — All objective functions and evaluation metrics
- [02-parameters](references/02-parameters.md) — Complete parameter reference (learning control, dataset, predict, GPU, network)
- [03-api-reference](references/03-api-reference.md) — Native API (Dataset, Booster, train, cv) and sklearn API details
- [04-advanced-features](references/04-advanced-features.md) — Distributed learning, GPU/CUDA, quantized training, linear trees, monotone constraints, custom objectives
