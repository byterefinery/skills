# Loss Functions and Metrics

## Classification Loss Functions

| Loss Function | Task | Description |
|---|---|---|
| `'Logloss'` | Binary | Binary cross-entropy. Default for `CatBoostClassifier` |
| `'MultiClass'` | Multiclass | Multiclass cross-entropy |
| `'CrossEntropy'` | Binary | Cross-entropy with label smoothing |
| `'AMR'` | Binary | Asymmetric mean ratio. For imbalanced binary classification |
| `'RMSE'` | Binary | RMSE on binary labels (less common) |

### AMR Parameters

```python
loss_function='AMR:alpha=0.1'
# alpha controls asymmetry, default 0.1
```

## Regression Loss Functions

| Loss Function | Description |
|---|---|
| `'RMSE'` | Root mean squared error. Default for `CatBoostRegressor` |
| `'MSE'` | Mean squared error |
| `'MAE'` | Mean absolute error |
| `'MAPE'` | Mean absolute percentage error |
| `'Poisson'` | Poisson regression loss |
| `'Lq:q=2'` | Lq loss with configurable q |
| `'Quantile:alpha=0.5'` | Quantile regression |
| `'LogLinQuantile:alpha=0.5'` | Log-linear quantile regression |
| `'SurvivalAft:dist=LogLogistic;scale=1.0'` | Survival regression (accelerated failure time) |

### Quantile Parameters

```python
loss_function='Quantile:alpha=0.9'  # 90th percentile
loss_function='Quantile:alpha=0.1'  # 10th percentile
```

### Survival Parameters

```python
loss_function='SurvivalAft:dist=LogLogistic;scale=1.0'
# dist: LogLogistic, Logistic, Exponential, Weibull
# scale: distribution scale parameter
```

## Ranking Loss Functions

| Loss Function | Description |
|---|---|
| `'YetiRank'` | Default. Pointwise approximation of listwise objective |
| `'YetiRankPairwise'` | Pairwise variant |
| `'StochasticFilter'` | Optimizes for filtering |
| `'StochasticRank'` | Optimizes for ranking |
| `'QueryCrossEntropy'` | Query-level cross entropy |
| `'QueryRMSE'` | Query-level RMSE |
| `'GroupQuantile'` | Group-wise quantile |
| `'QuerySoftMax'` | Softmax over query items |
| `'PairLogit'` | Pairwise logistic loss |
| `'PairLogitPairwise'` | Pairwise variant |

## Multi-Output Loss Functions

| Loss Function | Task |
|---|---|
| `'MultiRMSE'` | Multi-output regression |
| `'MultiMAE'` | Multi-output regression |
| `'MultiMSE'` | Multi-output regression |

## Evaluation Metrics

### Classification Metrics

| Metric | Description | Higher is Better |
|---|---|---|
| `'Accuracy'` | Classification accuracy | Yes |
| `'Logloss'` | Binary cross-entropy | No |
| `'MultiClass'` | Multiclass cross-entropy | No |
| `'CrossEntropy'` | Cross-entropy | No |
| `'AUC'` | Area under ROC curve | Yes |
| `'AUCPR'` | Area under precision-recall curve | Yes |
| `'F1'` | F1 score | Yes |
| `'Precision'` | Precision | Yes |
| `'Recall'` | Recall | Yes |
| `'RMSError'` | RMSE on predictions | No |
| `'TotalRelevance'` | Total relevance | Yes |
| `'Underoverratio'` | Under/over ratio | — |
| `'MaxOverordering'` | Max overordering | No |
| `'ElementsLossLength'` | Elements loss length | No |
| `'ElementsHitRatio'` | Elements hit ratio | Yes |
| `'PermutationImportance'` | Permutation importance | — |

### Regression Metrics

| Metric | Description | Higher is Better |
|---|---|---|
| `'RMSE'` | Root mean squared error | No |
| `'MSE'` | Mean squared error | No |
| `'MAE'` | Mean absolute error | No |
| `'MAPE'` | Mean absolute percentage error | No |
| `'R2'` | R-squared | Yes |
| `'ExplainedVariance'` | Explained variance ratio | Yes |
| `'Poisson'` | Poisson loss | No |

### Ranking Metrics

| Metric | Description | Higher is Better |
|---|---|---|
| `'NDCG@k'` | Normalized discounted cumulative gain | Yes |
| `'MAP@k'` | Mean average precision | Yes |
| `'Precision@k'` | Precision at k | Yes |
| `'Recall@k'` | Recall at k | Yes |
| `'MRR@k'` | Mean reciprocal rank | Yes |
| `'AverageHitRank'` | Average hit rank | No |

Append `@k` for top-k evaluation (e.g., `'NDCG@10'`, `'MAP@5'`).

## Custom Metrics

### Python Callable

```python
def custom_metric(output, labels, weight):
    # output: raw model predictions
    # labels: true labels
    # weight: sample weights (may be None)
    predictions = 1 / (1 + np.exp(-output))  # sigmoid for classification
    return np.mean((predictions - labels) ** 2), False  # (value, is_less_better)

model = CatBoostClassifier(custom_metric=[custom_metric])
model.fit(X_train, y_train, eval_set=(X_val, y_val))
```

Return `(metric_value, is_less_better)` where `is_less_better` indicates if lower values are better.

### Multiple Custom Metrics

```python
model = CatBoostClassifier(
    custom_metric=['Accuracy', custom_metric1, custom_metric2]
)
```

### Optimizing Custom Metric

Use `eval_metric` to optimize a custom metric during training:

```python
model = CatBoostClassifier(
    loss_function='Logloss',
    custom_metric=[custom_metric],
    eval_metric=custom_metric  # optimize this metric
)
```

## Metric Classes

CatBoost provides `BuiltinMetric` classes for programmatic metric construction:

```python
from catboost.metrics import *

# Parameterized metrics
metric = Quantile(alpha=0.9)
metric = SurvivalAft(dist='LogLogistic', scale=1.0)

# Evaluate metric manually
result = metric.eval(labels, predictions)
```

## Metric Direction

```python
from catboost import is_maximizable_metric, is_minimizable_metric

is_maximizable_metric('AUC')    # True
is_minimizable_metric('Logloss')  # True
```
