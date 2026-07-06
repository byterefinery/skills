# ChimeraBoostRegressor

## Constructor Parameters

| Parameter | Default | Type | Description |
|---|---|---|---|
| `n_estimators` | `2000` | int | Maximum boosting rounds. Upper bound when early stopping is active. |
| `learning_rate` | `None` | float | Per-tree shrinkage. `None` resolves to 0.1 with early stopping. |
| `depth` | `None` | int | Tree depth. Auto: 6 for RMSE/MAE, 4 for Quantile. Raise to 8–10 for interaction-heavy data. |
| `l2_leaf_reg` | `1.0` | float | L2 penalty on leaf values. Higher is smoother. |
| `max_bins` | `128` | int | Histogram bins per numeric feature. |
| `subsample` | `1.0` | float | Row fraction per tree. Below 1.0 uses Minimum Variance Sampling (gradient-weighted). |
| `colsample` | `1.0` | float | Feature fraction eligible per tree. |
| `cat_smoothing` | `1.0` | float | Prior strength for ordered target statistics. Must be > 0. |
| `cat_n_permutations` | `4` | int | Random orderings averaged by ordered target encoder. |
| `early_stopping_rounds` | `None` | int | Patience when early stopping active. `None` becomes 50. |
| `loss` | `"RMSE"` | str | `"RMSE"`, `"MAE"`, or `"Quantile"`. |
| `alpha` | `0.5` | float | Quantile level for `loss="Quantile"`. |
| `min_child_weight` | `1.0` | float | Minimum hessian mass on each side of a split. |
| `thread_count` | `None` | int | numba threads. `None`/`-1` uses all cores. |
| `random_state` | `None` | int | Seed for reproducibility (deterministic for fixed `thread_count`). |
| `verbose` | `False` | bool | Print per-round train and validation metrics. |
| `ordered_boosting` | `False` | bool | Leave-one-out leaf training step instead of plain Newton updates. |
| `cat_combinations` | `None` | bool | Pairwise categorical features. `None` enables auto for all-categorical data. |
| `leaf_estimation_iterations` | `1` | int | Newton refinement steps per leaf. |
| `linear_leaves` | `False` | bool | Ridge linear model per leaf over numeric split features. Not available with MAE/Quantile. |
| `linear_lambda` | `1.0` | float | Ridge penalty on per-leaf slopes. Larger is closer to constant. |
| `early_stopping` | `True` | bool | Hold out validation split and stop on plateau. |
| `validation_fraction` | `0.2` | float | Held-out fraction. Ignored when `eval_set` is passed to `fit`. |
| `n_ensembles` | `None` | int | Bagged members. `None`/1 = single model; >= 2 averages bootstrap members. |
| `ensemble_n_jobs` | `1` | int | Processes for fitting members; `-1` uses all cores. |
| `cat_features` | `None` | list | Default categorical columns (int positions and/or names). For GridSearchCV/Pipeline. |

## fit() Method

```python
model.fit(X, y, cat_features=None, eval_set=None, groups=None,
          sample_weight=None, callbacks=None)
```

| Argument | Description |
|---|---|
| `X` | Training features. NumPy array, pandas DataFrame, or PyArrow table. |
| `y` | Training targets. 1D array of shape `(n_samples,)`. |
| `cat_features` | Categorical columns by integer position and/or name. Overrides constructor value. |
| `eval_set` | `(X_val, y_val)` tuple. Overrides internal validation split. |
| `groups` | Group labels for grouped auto-split. Ignored when `eval_set` is passed. |
| `sample_weight` | Per-sample weights. Normalized to mean 1. Training only; eval metric stays unweighted. |
| `callbacks` | Per-round hooks `cb(iteration, train_loss, val_loss, model)`. Return `True` to stop early. Not supported with `n_ensembles > 1`. |

## predict() Method

```python
y_pred = model.predict(X)
```

Returns predicted target values. For bagged models, averages across members.

## staged_predict() Method

```python
for stage_pred in model.staged_predict(X):
    pass
```

Yields prediction after each successive tree. Not available with `n_ensembles > 1`.

## shap_values() Method

```python
phi = model.shap_values(X, X_background=None)
base = model.expected_value_
```

Returns exact interventional TreeSHAP contributions. Shape `(n_samples, n_features)`. Rows sum to `predict(X) - expected_value_`. `X_background` overrides the reference distribution.

## Fitted Attributes

| Attribute | Description |
|---|---|
| `feature_importances_` | Split-gain importance per feature, normalized to sum to 1. |
| `best_iteration_` | Trees retained after early stopping. |
| `expected_value_` | SHAP baseline (mean prediction over background). Set after `shap_values()`. |
| `estimators_` | Fitted members when `n_ensembles > 1`, else `None`. |
| `validation_history_` | Per-round validation loss list. Empty without eval_set. For bagged models, list of members' histories. |
| `n_features_in_` | Number of input features seen during fit. |
| `feature_names_in_` | Feature names from DataFrame input, if available. |

## Loss Functions

### RMSE (default)
- Squared-error regression
- Newton leaf estimation
- `grad = pred - y`, `hess = 1`
- Supports `linear_leaves`

### MAE
- Mean absolute error (median regression)
- Leaf values set to weighted median of residuals
- `grad = sign(pred - y)`, `hess = 1`
- Does not support `linear_leaves`

### Quantile
- Pinball loss at level `alpha`
- Leaf values set to weighted quantile of residuals
- `grad = -alpha` where `y >= pred`, `1-alpha` otherwise
- Default `depth=4` (shallower to avoid overfitting tails)
- Does not support `linear_leaves`

## Input Validation

- `X` must be 2D, at least 1 sample and 1 feature
- `y` must be 1D, finite values (no NaN/inf in targets)
- `X` can contain NaN (routed to missing bin) but not inf
- Complex data not supported
- Sparse matrices not supported
- Masked arrays rejected (convert via `X.filled(np.nan)`)
- `sample_weight` must be 1D, non-negative, non-zero sum, finite
