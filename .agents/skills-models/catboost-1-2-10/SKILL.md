---
name: catboost-1-2-10
description: Train and deploy CatBoost 1.2.10 gradient boosting models for classification, regression, ranking, and multi-output tasks. Use when the user needs gradient boosting on tabular data with categorical features, GPU acceleration, text features, embedding features, monotone constraints, SHAP values, or model export to ONNX/CoreML/PMML/C++. Supports scikit-learn API and CatBoost-specific API (Pool, train, cv). Handles missing values natively. Apache 2.0 license.
metadata:
  tags:
    - ai-ml
    - gradient-boosting
    - decision-trees
    - tabular
    - classification
    - regression
    - ranking
    - gpu
    - categorical-features
    - yandex
    - scikit-learn
---

# catboost 1.2.10

## Overview

**CatBoost** (v1.2.10) by Yandex is a gradient boosting library on decision trees. It excels on tabular data with categorical features using ordered boosting to eliminate prediction shift. Supports classification, regression, ranking, and multi-output tasks with GPU acceleration, text features, and embedding features built in.

Key capabilities:
- **Categorical features** — first-class support with target statistics (CTR), no manual encoding needed
- **Ordered boosting** — eliminates prediction shift bias, improving generalization
- **GPU training** — single and multi-GPU support via `task_type='GPU'` or `devices` parameter
- **Text features** — built-in text processing with configurable tokenizers and dictionaries
- **Embedding features** — accept pre-computed embedding vectors as inputs
- **Monotone constraints** — enforce feature-direction constraints during training
- **SHAP values** — exact and approximate SHAP for interpretability
- **Model export** — ONNX, CoreML, PMML, C++, Python code export
- **Scikit-learn API** — `CatBoostClassifier`, `CatBoostRegressor`, `CatBoostRanker` with full sklearn compatibility
- **Custom objectives and metrics** — Python-callable loss functions and evaluation metrics
- **Cross-validation** — built-in `cv()` with classical, inverted, and time-series splits
- **Gaussian process sampling** — `sample_gaussian_process()` for uncertainty estimation

## Usage

### Installation

```bash
pip install catboost==1.2.10
```

Requires Python 3.7+. GPU support requires CUDA 11.0+ and cuDNN. For CPU-only, install the `catboost-cpu` package or use the standard package (includes both).

### Quick Start — Classification

```python
from catboost import CatBoostClassifier

model = CatBoostClassifier(iterations=100, depth=6, learning_rate=0.03, loss_function='Logloss')
model.fit(X_train, y_train, cat_features=[0, 2])
predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)
```

### Quick Start — Regression

```python
from catboost import CatBoostRegressor

model = CatBoostRegressor(iterations=100, depth=6, learning_rate=0.03, loss_function='RMSE')
model.fit(X_train, y_train, cat_features=[0, 2])
predictions = model.predict(X_test)
```

### With Pool (CatBoost API)

```python
from catboost import Pool, CatBoostClassifier

train_pool = Pool(X_train, y_train, cat_features=[0, 2])
test_pool = Pool(X_test, y_test, cat_features=[0, 2])

model = CatBoostClassifier(iterations=100, depth=6, learning_rate=0.03)
model.fit(train_pool, eval_set=test_pool, use_best_model=True, early_stopping_rounds=10)
```

### GPU Training

```python
model = CatBoostClassifier(task_type='GPU', iterations=100, depth=6)
model.fit(X_train, y_train)
```

Multi-GPU:

```python
model = CatBoostClassifier(devices='0:1', iterations=100, depth=6)
model.fit(X_train, y_train)
```

### Cross-Validation

```python
from catboost import cv, Pool

pool = Pool(X, y, cat_features=[0, 2])
params = {'loss_function': 'Logloss', 'iterations': 100, 'depth': 6}

cv_results = cv(pool, params, fold_count=5, plot=True)
```

### Early Stopping

```python
model = CatBoostClassifier(use_best_model=True)
model.fit(X_train, y_train, eval_set=(X_val, y_val), early_stopping_rounds=10)
```

### Save and Load

```python
model.save_model('model.cbm')  # CatBoost binary format
model.save_model('model.onnx', format='onnx')  # ONNX
model.save_model('model.json', format='json')  # JSON (for inspection)

# Load
model = CatBoostClassifier()
model.load_model('model.cbm')
```

### Feature Importance

```python
importances = model.get_feature_importance()
# or with SHAP values
shap_values = model.get_feature_importance(data=test_pool, type='ShapValues')
```

## Gotchas

- **Categorical features must be declared** — pass `cat_features` as a list of column indices (or names). CatBoost does not auto-detect categoricals. Integer columns that represent categories (e.g., zip codes) must be explicitly listed.
- **Categorical values should be integers or strings** — CatBoost converts object-dtype pandas columns automatically, but float columns with NaNs cannot be categorical.
- **`nan_mode` defaults to `'Min'`** — missing numeric values are treated as the minimum value, not as a separate category. Set `nan_mode='Max'` or `nan_mode='Forbidden'` as needed.
- **`use_best_model` requires `eval_set`** — cannot use best model selection without a validation set.
- **GPU training uses different defaults** — `border_count` defaults to 128 on GPU (254 on CPU). Some CTR types are GPU-only (`FloatTargetMeanValue`, `FeatureFreq`).
- **`iterations` is the number of trees** — not epochs. Each iteration adds one tree. Default is 500.
- **`depth` limits tree depth** — range is [1, 16]. Default is 6. Higher depth risks overfitting.
- **`l2_leaf_reg` is always applied** — default is 3.0. Set to 0 to disable L2 regularization.
- **`learning_rate` default varies** — for binary classification with default params, it's auto-selected. For other tasks, default is 0.03.
- **`boosting_type` defaults to `'Ordered'`** — ordered boosting gives better quality but is slower. Use `'Plain'` for speed when quality difference is acceptable.
- **`random_seed` must be set for reproducibility** — without it, results vary between runs.
- **`fit()` returns `self`** — supports sklearn-style chaining.
- **`predict()` default differs by class** — `CatBoostClassifier.predict()` returns class labels (not probabilities). Use `predict_proba()` for probabilities.
- **`predict()` on `CatBoost` base class** — returns `RawFormulaVal` by default, not class labels. Use `prediction_type='Class'` or `prediction_type='Probability'`.
- **`eval_set` copies categorical feature info** — when `eval_set` is a tuple `(X, y)`, CatBoost infers categorical features from the training pool.
- **Sparse matrices are supported** — `scipy.sparse` matrices work directly with Pool and `fit()`.
- **Pandas and Polars DataFrames are supported** — column names become feature names automatically.
- **`cv()` requires `loss_function` in params** — unlike `fit()`, cross-validation always needs an explicit loss function.
- **Model files can be large** — CBM format is compact but still stores all trees. Use `ctr_leaf_count_limit` and `model_size_reg` to control size.
- **`get_feature_importance()` without data** — returns global importance from leaf weights (models trained with v1.2+). For older models, pass data.
- **`sample_gaussian_process()`** — returns a list of models for uncertainty estimation. Use `sum_models()` to combine.
- **`onnx` export requires `pool`** — when saving to ONNX, pass the training pool for proper feature type inference.
- **Text features need `text_processing` config** — specify tokenizers, dictionaries, and feature calculators for text columns.
- **`monotone_constraints` values** — use -1 (decreasing), 0 (no constraint), 1 (increasing). Can be a list, dict, or JSON string.
- **`class_weights` vs `auto_class_weights`** — `auto_class_weights='Balanced'` or `'SqrtBalanced'` auto-computes weights from training data distribution.
- **`eval_fraction`** — splits training data into train/eval internally. Cannot use with explicit `eval_set`.

## References

- [01-classifiers-regressors](references/01-classifiers-regressors.md) — `CatBoostClassifier` and `CatBoostRegressor` API, parameters, and methods
- [02-ranker](references/02-ranker.md) — `CatBoostRanker` for learning-to-rank tasks
- [03-pool-data](references/03-pool-data.md) — `Pool` class, data handling, categorical/text/embedding features
- [04-training-params](references/04-training-params.md) — Complete training parameters reference
- [05-loss-functions-metrics](references/05-loss-functions-metrics.md) — Loss functions, evaluation metrics, and custom objectives
- [06-export-deploy](references/06-export-deploy.md) — Model export formats (ONNX, CoreML, PMML, C++, Python) and deployment
- [07-advanced-features](references/07-advanced-features.md) — GPU training, text features, embeddings, monotone constraints, SHAP, uncertainty
- [08-utility-functions](references/08-utility-functions.md) — `cv()`, `train()`, `sample_gaussian_process()`, `sum_models()`, and other utilities
