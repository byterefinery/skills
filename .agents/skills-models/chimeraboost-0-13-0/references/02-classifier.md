# ChimeraBoostClassifier

## Constructor Parameters

| Parameter | Default | Type | Description |
|---|---|---|---|
| `n_estimators` | `2000` | int | Maximum boosting rounds. Upper bound with early stopping. |
| `learning_rate` | `None` | float | Per-tree shrinkage. `None` resolves to 0.1 with early stopping. |
| `depth` | `6` | int | Tree depth. |
| `l2_leaf_reg` | `1.0` | float | L2 penalty on leaf values. |
| `max_bins` | `128` | int | Histogram bins per numeric feature. |
| `subsample` | `1.0` | float | Row fraction per tree (Minimum Variance Sampling below 1.0). |
| `colsample` | `1.0` | float | Feature fraction eligible per tree. |
| `cat_smoothing` | `1.0` | float | Prior strength for ordered target statistics. Must be > 0. |
| `cat_n_permutations` | `4` | int | Random orderings averaged by ordered target encoder. |
| `early_stopping_rounds` | `None` | int | Patience when early stopping active. `None` becomes 50. |
| `min_child_weight` | `None` | float | Minimum hessian mass. `None` is size-adaptive: full veto below ~500 rows, off above ~2000. |
| `thread_count` | `None` | int | numba threads. `None`/`-1` uses all cores. |
| `random_state` | `None` | int | Seed for reproducibility. |
| `verbose` | `False` | bool | Print per-round metrics. |
| `ordered_boosting` | `False` | bool | Leave-one-out leaf training step. |
| `cat_combinations` | `None` | bool | Pairwise categorical features. Auto for all-categorical data. |
| `leaf_estimation_iterations` | `3` | int | Newton refinement steps per leaf. |
| `linear_leaves` | `None` | bool | Ridge linear model per leaf. `None` = on for binary, off for multiclass. |
| `linear_lambda` | `1.0` | float | Ridge penalty on per-leaf slopes. |
| `early_stopping` | `True` | bool | Hold out stratified validation split. |
| `validation_fraction` | `0.2` | float | Held-out fraction. Ignored with explicit `eval_set`. |
| `n_ensembles` | `None` | int | Bagged members. `None`/1 = single model; >= 2 soft-votes probabilities. |
| `ensemble_n_jobs` | `1` | int | Processes for fitting members. |
| `cat_features` | `None` | list | Default categorical columns. For GridSearchCV/Pipeline. |

## fit() Method

```python
model.fit(X, y, cat_features=None, eval_set=None, groups=None,
          sample_weight=None, callbacks=None)
```

Same signature as the regressor. For classification:
- Auto-holdout uses `StratifiedShuffleSplit` (or `StratifiedGroupKFold` with `groups`)
- Binary classification uses `Logloss` internally
- Multiclass (3+ classes) uses `MultiSoftmax` internally
- `eval_set` should contain original class labels

## predict() Method

```python
labels = model.predict(X)
```

Returns class labels (original values, including strings). Based on `argmax` of `predict_proba()`.

## predict_proba() Method

```python
proba = model.predict_proba(X)
```

Returns calibrated probability matrix. Shape `(n_samples, n_classes)`. Columns follow `classes_` order. Temperature-scaled on validation split.

For bagged models, soft-votes: averages members' calibrated probabilities, aligning each member's class columns to the global class set.

## shap_values() Method

```python
phi = model.shap_values(X, X_background=None)
base = model.expected_value_
```

Binary classification only. Returns SHAP in log-odds (margin) space. Rows sum to `raw_log_odds - expected_value_`. Multiclass raises `NotImplementedError`.

## Fitted Attributes

| Attribute | Description |
|---|---|
| `classes_` | Class labels in `predict_proba` column order. Preserves original values. |
| `n_classes_` | Number of classes. |
| `feature_importances_` | Split-gain importance, normalized to sum to 1. |
| `best_iteration_` | Trees retained after early stopping. |
| `temperature_` | Calibration temperature. > 1 means raw scores were over-confident. |
| `expected_value_` | SHAP baseline (binary only). Set after `shap_values()`. |
| `estimators_` | Fitted members when `n_ensembles > 1`, else `None`. |
| `validation_history_` | Per-round validation log loss. |
| `n_features_in_` | Number of input features. |
| `feature_names_in_` | Feature names from DataFrame input. |

## Binary vs Multiclass Behavior

### Binary Classification (2 classes)
- Uses `Logloss` loss internally
- `linear_leaves` enabled by default (`None` resolves to `True`)
- `shap_values` supported (in log-odds space)
- `min_child_weight` auto-adaptive (`None` default)
- Temperature scaling on `predict_proba`

### Multiclass Classification (3+ classes)
- Uses `MultiSoftmax` loss internally
- `linear_leaves` disabled (`None` resolves to `False`; explicit `True` raises `NotImplementedError`)
- `shap_values` not supported (raises `NotImplementedError`)
- `min_child_weight` auto-adaptive (`None` default)
- Temperature scaling on `predict_proba`
- Original label values preserved (including strings)

## Temperature Scaling

`predict_proba` divides raw scores by `temperature_` before applying sigmoid/softmax. The temperature is fitted on the validation split to minimize log loss. The transform is monotonic, so `predict()`, AUC, and accuracy are unchanged — only the probability calibration improves.

```python
clf = ChimeraBoostClassifier(random_state=0).fit(Xtr, ytr)
print(clf.temperature_)  # > 1 means raw scores were over-confident
```

## Bagging (n_ensembles > 1)

Classifier bagging soft-votes: each member's calibrated probabilities are averaged, with class columns aligned to the global `classes_` set. A member whose bootstrap missed a class contributes 0 to that column.

`shap_values` averages SHAP across members (additive surrogate for the soft-voted probability).
