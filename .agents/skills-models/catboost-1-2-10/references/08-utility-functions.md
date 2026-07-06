# Utility Functions

## cv() — Cross-Validation

```python
from catboost import cv, Pool

pool = Pool(X, y, cat_features=[0, 2])
params = {
    'loss_function': 'Logloss',
    'iterations': 100,
    'depth': 6,
    'learning_rate': 0.03
}

cv_results = cv(
    pool, params,
    fold_count=5,
    partition_random_seed=42,
    shuffle=True,
    stratified=None,
    type='Classical',
    as_pandas=True,
    verbose=True,
    plot=False,
    early_stopping_rounds=10,
    return_models=False
)
```

### Parameters

| Parameter | Default | Description |
|---|---|---|
| `pool` | required | Training pool |
| `params` | required | Training params dict. Must include `loss_function` |
| `fold_count` | 3 | Number of folds |
| `type` | `'Classical'` | `'Classical'`, `'Inverted'`, `'TimeSeries'` |
| `inverted` | False | Train on test fold, evaluate on train folds |
| `partition_random_seed` | 0 | Random seed for data permutation |
| `shuffle` | True | Shuffle before splitting |
| `stratified` | auto | True for classification, False otherwise |
| `as_pandas` | True | Return DataFrame (if pandas available) |
| `return_models` | False | Return list of trained models per fold |
| `folds` | None | Custom fold indices or sklearn splitter |

### Returns

- DataFrame with columns: `test-*-mean`, `test-*-std`, `train-*-mean`, `train-*-std`
- If `return_models=True`: tuple of (results, models)

### Time Series CV

```python
cv_results = cv(
    pool, params,
    type='TimeSeries',
    fold_count=5
)
# Respects data order, no shuffling
```

### Custom Folds (sklearn)

```python
from sklearn.model_selection import StratifiedKFold

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

cv_results = cv(
    pool, params,
    folds=skf
)
```

## train() — Functional API

```python
from catboost import train, Pool

params = {
    'loss_function': 'Logloss',
    'iterations': 100,
    'depth': 6,
    'learning_rate': 0.03
}

pool = Pool(X_train, y_train, cat_features=[0, 2])
eval_pool = Pool(X_val, y_val, cat_features=[0, 2])

model = train(
    pool, params,
    eval_set=eval_pool,
    verbose=100,
    early_stopping_rounds=10
)
```

This is equivalent to:

```python
model = CatBoost(params)
model.fit(pool, eval_set=eval_pool, verbose=100, early_stopping_rounds=10)
```

## sample_gaussian_process()

Uncertainty estimation via kernel gradient boosting (from "Gradient Boosting Performs Gaussian Process Inference"):

```python
from catboost import sample_gaussian_process

models = sample_gaussian_process(
    X, y,
    cat_features=[0, 2],
    text_features=None,
    embedding_features=None,
    eval_set=None,
    random_seed=42,
    samples=10,
    posterior_iterations=900,
    prior_iterations=100,
    learning_rate=0.1,
    depth=6,
    sigma=0.1,
    delta=0,
    random_strength=0.1,
    random_score_type='Gumbel',
    eps=1e-4,
    verbose=False
)
```

### Parameters

| Parameter | Default | Description |
|---|---|---|
| `X` | required | Feature matrix |
| `y` | required | Labels (numeric) |
| `samples` | 10 | Number of GP posterior samples (models returned) |
| `posterior_iterations` | 900 | Trees for posterior step |
| `prior_iterations` | 100 | Trees for prior step |
| `sigma` | 0.1 | GP kernel scale (lower = lower posterior variance) |
| `delta` | 0 | Homogeneous noise scale (adjust for noisy targets) |
| `random_strength` | 0.1 | Convergence speed to GP posterior |
| `random_score_type` | `'Gumbel'` | `'Gumbel'` or `'NormalWithModelSizeDecrease'` |
| `eps` | 1e-4 | Prior estimation precision |

### Returns

List of `CatBoostRegressor` models. Use ensemble predictions for uncertainty:

```python
predictions = [m.predict(X_test) for m in models]
mean = np.mean(predictions, axis=0)
std = np.std(predictions, axis=0)
```

## sum_models()

Combine multiple CatBoost models:

```python
from catboost import sum_models

combined = sum_models([model1, model2, model3])
combined = sum_models([model1, model2], weights=[0.7, 0.3])
combined = sum_models(
    [model1, model2],
    ctr_merge_policy='IntersectingCountersAverage'
)
```

### CTR Merge Policies

| Policy | Description |
|---|---|
| `'IntersectingCountersAverage'` | Average counters for intersecting categories |
| `'AllCountersAverage'` | Average all counters |
| `'FirstCounters'` | Use counters from first model |

## to_classifier() / to_regressor() / to_ranker()

Convert between model types:

```python
from catboost import to_classifier, to_regressor, to_ranker

classifier = to_classifier(regressor_model)
regressor = to_regressor(classifier_model)
ranker = to_ranker(regressor_model)
```

## Metrics Utilities

```python
from catboost import (
    is_classification_objective,
    is_regression_objective,
    is_ranking_objective,
    is_multiregression_objective,
    is_multitarget_objective,
    is_multilabel_objective,
    is_survivalregression_objective,
    is_multiclass_compatible_objective,
    is_groupwise_metric,
    is_ranking_metric,
    is_maximizable_metric,
    is_minimizable_metric
)

is_classification_objective('Logloss')  # True
is_maximizable_metric('AUC')            # True
is_minimizable_metric('RMSE')           # True
```

## log_fixup()

Redirect CatBoost logging:

```python
from catboost import log_fixup
import io

output = io.StringIO()
with log_fixup(log_cout=output):
    model.fit(X_train, y_train, verbose=True)

logged_text = output.getvalue()
```

## _configure_malloc()

Configure memory allocation:

```python
from catboost import _configure_malloc
_configure_malloc()  # Called automatically on import
```

## MetricVisualizer / MetricsPlotter

```python
from catboost import MetricVisualizer

visualizer = MetricVisualizer()
# Automatically shows in Jupyter notebooks when plot=True in fit()
```
