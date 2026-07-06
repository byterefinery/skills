# Objectives and Metrics

## Objectives

The `objective` parameter defines the loss function optimized during training.

### Regression

| Objective | Description | Default Metric |
|---|---|---|
| `reg:squarederror` | Squared loss (MSE) | `rmse` |
| `reg:squaredlogerror` | Squared log loss; labels > -1 required | `rmsle` |
| `reg:pseudohubererror` | Twice-differentiable absolute loss | `mphe` |
| `reg:absoluteerror` | L1 loss (MAE) | `mae` |
| `reg:quantileerror` | Quantile (pinball) loss; set `quantile_alpha` | — |
| `reg:expectileerror` | Expectile loss (asymmetric squared); set `expectile_alpha` (3.3.0+) | `expectile` |
| `reg:gamma` | Gamma regression with log-link | `gamma-nloglik` |
| `reg:tweedie` | Tweedie regression with log-link; set `tweedie_variance_power` | `tweedie-nloglik` |
| `count:poisson` | Poisson regression for count data; `max_delta_step` defaults to 0.7 | `poisson-nloglik` |

### Binary Classification

| Objective | Description | Default Metric |
|---|---|---|
| `binary:logistic` | Logistic regression, outputs probability | `logloss` |
| `binary:logitraw` | Logistic regression, outputs raw score | `logloss` |
| `binary:hinge` | Hinge loss, outputs 0/1 predictions | `error` |

### Multi-Class Classification

| Objective | Description | Default Metric |
|---|---|---|
| `multi:softmax` | Softmax, outputs class label | `merror` |
| `multi:softprob` | Softmax, outputs probability vector (ndata × nclass) | `mlogloss` |

Requires `num_class` parameter. Use `multi:softprob` when you need probabilities or AUC.

### Ranking (Learning to Rank)

| Objective | Description | Default Metric |
|---|---|---|
| `rank:ndcg` | LambdaMART optimizing NDCG | `ndcg` |
| `rank:map` | LambdaMART optimizing MAP | `map` |
| `rank:pairwise` | LambdaRank (RankNet) pairwise | — |

Requires `group` or `qid` in DMatrix. Data must be sorted by query.

### Survival Analysis

| Objective | Description | Default Metric |
|---|---|---|
| `survival:cox` | Cox proportional hazards; predictions on hazard ratio scale | `cox-nloglik` |
| `survival:aft` | Accelerated failure time; set `aft_loss_distribution` | `aft-nloglik` |

## Evaluation Metrics

Set via `eval_metric` parameter. Multiple metrics: `eval_metric=["rmse", "mae"]`.

### Regression Metrics

| Metric | Description |
|---|---|
| `rmse` | Root mean square error |
| `rmsle` | Root mean square log error; NaN if prediction < -1 |
| `mae` | Mean absolute error |
| `mape` | Mean absolute percentage error |
| `mphe` | Mean Pseudo Huber error |
| `expectile` | Expectile regression error |
| `poisson-nloglik` | Negative log-likelihood for Poisson |
| `gamma-nloglik` | Negative log-likelihood for Gamma |
| `gamma-deviance` | Residual deviance for Gamma |
| `tweedie-nloglik` | Negative log-likelihood for Tweedie |

### Classification Metrics

| Metric | Description |
|---|---|
| `logloss` | Negative log-likelihood (binary) |
| `mlogloss` | Multiclass log loss |
| `error` | Binary error rate (threshold 0.5) |
| `error@t` | Binary error rate at custom threshold `t` |
| `merror` | Multiclass error rate |
| `auc` | Area under ROC curve |
| `aucpr` | Area under Precision-Recall curve |

**AUC notes:**
- Binary: use with `binary:logistic` or probability-outputting objectives
- Multi-class: use with `multi:softprob` (not `multi:softmax`)
- Computed as 1-vs-rest weighted by class prevalence
- Returns NaN if only one class present
- Distributed AUC is approximate; use another metric in distributed settings

### Ranking Metrics

| Metric | Description |
|---|---|
| `ndcg` | Normalized Discounted Cumulative Gain |
| `ndcg@n` | NDCG truncated at position `n` |
| `ndcg@n-` | NDCG@n treating all-negative lists as 0 |
| `map` | Mean Average Precision |
| `map@n` | MAP truncated at position `n` |
| `map@n-` | MAP@n treating all-negative lists as 0 |
| `pre@n` | Precision at `k` |
| `auc` | Pairwise AUC for ranking |
| `aucpr` | PR-AUC (binary relevance only) |

### Survival Metrics

| Metric | Description |
|---|---|
| `cox-nloglik` | Negative partial log-likelihood for Cox PH |
| `aft-nloglik` | Negative log-likelihood for AFT model |
| `interval-regression-accuracy` | Fraction of predictions within interval-censored labels |

## Choosing Objective + Metric

### Regression
```python
# Standard regression
objective="reg:squarederror", eval_metric="rmse"

# Robust to outliers
objective="reg:pseudohubererror", eval_metric="mae"

# Percentage-based error
objective="reg:squarederror", eval_metric="mape"

# Quantile predictions
objective="reg:quantileerror", quantile_alpha=[0.1, 0.5, 0.9]

# Count data
objective="count:poisson"

# Positive continuous (insurance claims)
objective="reg:gamma"
```

### Binary Classification
```python
# Probability output
objective="binary:logistic", eval_metric=["logloss", "auc"]

# Raw score output
objective="binary:logitraw", eval_metric="auc"

# Hard classification
objective="binary:hinge", eval_metric="error"
```

### Multi-Class Classification
```python
# Class labels
objective="multi:softmax", num_class=10, eval_metric="merror"

# Probabilities + AUC
objective="multi:softprob", num_class=10, eval_metric=["mlogloss", "auc"]
```

### Ranking
```python
# NDCG optimization
objective="rank:ndcg", eval_metric=["ndcg@3", "ndcg@10", "map"]

# MAP optimization
objective="rank:map", eval_metric=["map@5", "ndcg@5"]
```

## Custom Objectives

```python
import numpy as np

def custom_objective(y_pred, dtrain):
    y_true = dtrain.get_label()
    grad = y_pred - y_true
    hess = np.ones_like(y_true)
    return grad, hess

# With sample weight support
def custom_objective_sw(y_true, y_pred, sample_weight=None):
    grad = (y_pred - y_true)
    hess = np.ones_like(y_true)
    if sample_weight is not None and len(sample_weight) > 0:
        grad = grad * sample_weight
        hess = hess * sample_weight
    return grad, hess

model = xgb.train(params, dtrain, num_boost_round=100, obj=custom_objective)
```

## Custom Metrics

```python
def custom_metric(y_pred, dtrain):
    y_true = dtrain.get_label()
    mae = float(np.mean(np.abs(y_true - y_pred)))
    return "custom_mae", mae

# Lower is better (minimize)
model = xgb.train(
    params, dtrain, num_boost_round=100,
    custom_metric=custom_metric,
    maximize=False,
)
```
