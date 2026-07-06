# Objectives and Metrics — LightGBM 4.6.0

## Objective Functions

Set via `objective` parameter. Determines the loss function LightGBM optimizes.

### Regression

| Objective | Aliases | Description |
|---|---|---|
| `regression` | `regression_l2`, `l2`, `mean_squared_error`, `mse`, `l2_root`, `rmse` | L2 loss (default). Use `rmse` alias for root mean squared error output |
| `regression_l1` | `l1`, `mean_absolute_error`, `mae` | L1 loss, robust to outliers |
| `huber` | — | Huber loss, controlled by `alpha` (default 0.9). Combines L2 for small residuals, L1 for large |
| `fair` | — | Fair loss, controlled by `fair_c` (default 1.0). Less sensitive to outliers |
| `poisson` | — | Poisson regression for count data. Use `poisson_max_delta_step` (default 0.7) to safeguard optimization |
| `quantile` | — | Quantile regression, controlled by `alpha` (default 0.9). Predicts specified quantile |
| `mape` | `mean_absolute_percentage_error` | Mean absolute percentage error |
| `gamma` | — | Gamma regression with log-link. Useful for insurance claim severity modeling |
| `tweedie` | — | Tweedie regression with log-link. Controlled by `tweedie_variance_power` (1.0–2.0). Closer to 2 = Gamma-like, closer to 1 = Poisson-like |
| `custom` | — | Custom objective. Pass a callable returning `(grad, hess)`. Cannot be used in CLI |

### Binary Classification

| Objective | Aliases | Description |
|---|---|---|
| `binary` | — | Binary log loss (logistic regression). Labels must be {0, 1}. Outputs probability via sigmoid |

Additional binary parameters:
- `is_unbalance` — auto-adjust weights for imbalanced data (mutually exclusive with `scale_pos_weight`)
- `scale_pos_weight` — manual positive class weight (mutually exclusive with `is_unbalance`)
- `sigmoid` — sigmoid function parameter (default 1.0)
- `boost_from_average` — adjusts initial score to mean of labels (default true)

### Multiclass Classification

| Objective | Aliases | Description |
|---|---|---|
| `multiclass` | `softmax` | Softmax objective. Requires `num_class` parameter |
| `multiclassova` | `multiclass_ova`, `ova`, `ovr` | One-vs-All binary objective. Requires `num_class` |

For multiclass, LightGBM internally builds `num_class * num_iterations` trees.

### Cross-Entropy

| Objective | Aliases | Description |
|---|---|---|
| `cross_entropy` | `xentropy` | Cross-entropy with optional linear weights. Labels in [0, 1] |
| `cross_entropy_lambda` | `xentlambda` | Alternative parameterization of cross-entropy. Labels in [0, 1] |

### Ranking

| Objective | Aliases | Description |
|---|---|---|
| `lambdarank` | — | LambdaRank with NDCG. Integer labels (higher = more relevant). Configure with `label_gain`, `lambdarank_truncation_level` |
| `rank_xendcg` | `xendcg`, `xe_ndcg`, `xe_ndcg_mart`, `xendcg_mart` | XE_NDCG MART ranking. Faster than lambdarank with similar performance |

Ranking parameters:
- `label_gain` — gain weights per label rank (default: 0,1,3,7,15,31,63,...,2^30-1)
- `lambdarank_truncation_level` — top results to focus on (default 30). Set slightly above target NDCG@k cutoff
- `lambdarank_norm` — normalize lambdas for unbalanced data (default true)
- Data must be pre-sorted by query ID; provide `group` array with group sizes

### Custom Objective

```python
def custom_objective(preds, train_data):
    labels = train_data.get_label()
    # preds are raw margins (not transformed)
    grad = preds - labels  # example: L2 gradient
    hess = np.ones_like(preds)  # example: L2 hessian
    return grad, hess

params = {"objective": custom_objective}
```

For multiclass, `preds` shape is `(n_samples, n_classes)` and `grad`/`hess` must match.

## Evaluation Metrics

Set via `metric` parameter. Multiple metrics separated by commas. Empty string (default) uses metric matching the objective. String `"None"` disables all metrics.

### Regression Metrics

| Metric | Aliases | Description |
|---|---|---|
| `l1` | `mean_absolute_error`, `mae`, `regression_l1` | Absolute loss |
| `l2` | `mean_squared_error`, `mse`, `regression_l2`, `regression` | Square loss |
| `rmse` | `root_mean_squared_error`, `l2_root` | Root square loss |
| `quantile` | — | Quantile regression metric |
| `mape` | `mean_absolute_percentage_error` | Mean absolute percentage error |
| `huber` | — | Huber loss |
| `fair` | — | Fair loss |
| `poisson` | — | Negative log-likelihood for Poisson |
| `gamma` | — | Negative log-likelihood for Gamma |
| `gamma_deviance` | — | Residual deviance for Gamma |
| `tweedie` | — | Negative log-likelihood for Tweedie |
| `kullback_leibler` | `kldiv` | Kullback-Leibler divergence |

### Classification Metrics

| Metric | Aliases | Description |
|---|---|---|
| `auc` | — | Area under ROC curve |
| `average_precision` | — | Average precision score |
| `binary_logloss` | `binary` | Log loss for binary classification |
| `binary_error` | — | 0 for correct, 1 for error per sample |
| `auc_mu` | — | AUC-mu with weighted classification errors. Requires `auc_mu_weights` |
| `multi_logloss` | `multiclass`, `softmax`, `multiclassova`, `ova`, `ovr` | Log loss for multiclass |
| `multi_error` | — | Error rate for multiclass. Controlled by `multi_error_top_k` |
| `cross_entropy` | `xentropy` | Cross-entropy |
| `cross_entropy_lambda` | `xentlambda` | Intensity-weighted cross-entropy |

### Ranking Metrics

| Metric | Aliases | Description |
|---|---|---|
| `ndcg` | `lambdarank`, `rank_xendcg`, `xendcg`, `xe_ndcg`, `xe_ndcg_mart`, `xendcg_mart` | Normalized Discounted Cumulative Gain. Positions controlled by `eval_at` |
| `map` | `mean_average_precision` | Mean Average Precision. Positions controlled by `eval_at` |

### Metric Parameters

- `eval_at` — positions for NDCG and MAP evaluation (default: 1,2,3,4,5). Pass as list in Python: `eval_at=[1, 3, 5, 10]`
- `multi_error_top_k` — threshold for top-k multi-error (default 1)
- `auc_mu_weights` — flattened n×n weight matrix for AUC-mu (row-major order)

### Custom Metrics

```python
def custom_metric(preds, train_data):
    labels = train_data.get_label()
    # Return (name, value, is_higher_better)
    return "my_metric", float(np.mean((preds - labels) ** 2)), False

# Or return multiple metrics:
def multi_metric(preds, train_data):
    labels = train_data.get_label()
    return [
        ("mae", float(np.mean(np.abs(preds - labels))), False),
        ("mse", float(np.mean((preds - labels) ** 2)), False),
    ]

callbacks = [lgb.record_evaluation(eval_result={})]
model = lgb.train(params, train_data, feval=custom_metric, callbacks=callbacks)
```
