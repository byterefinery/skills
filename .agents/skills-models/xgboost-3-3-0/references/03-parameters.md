# Parameter Reference

## Global Configuration

Set once, applies to all subsequent calls:

```python
import xgboost as xgb

xgb.set_config(verbosity=1)

# Context manager
with xgb.config_context(verbosity=2, use_rmm=False):
    model = xgb.train(params, dtrain, num_boost_round=100)

# Current config
print(xgb.get_config())
```

| Parameter | Default | Description |
|---|---|---|
| `verbosity` | 1 | 0=silent, 1=warning, 2=info, 3=debug |
| `use_rmm` | false | Use RAPIDS Memory Manager for GPU |
| `use_cuda_async_pool` | false | Use CUDA driver memory pool (3.2.0+) |
| `nthread` | auto | Global OpenMP thread count |

## General Parameters

| Parameter | Default | Description |
|---|---|---|
| `booster` | `gbtree` | `gbtree`, `dart`, `gblinear` (deprecated 3.3.0) |
| `device` | `cpu` | `cpu`, `cuda`, `cuda:<n>`, `gpu`, `gpu:<n>` |
| `verbosity` | 1 | 0=silent, 1=warning, 2=info, 3=debug |
| `nthread` | auto | Parallel threads |
| `validate_parameters` | false | Warn on unknown parameters |
| `disable_default_eval_metric` | false | Disable auto eval metric |

## Tree Booster Parameters

### Learning Control

| Parameter | Default | Range | Description |
|---|---|---|---|
| `learning_rate` (eta) | 0.3 | [0, 1] | Step shrinkage; lower = more conservative |
| `n_estimators` | 100 | [1, ∞) | Number of boosting rounds (sklearn only) |
| `gamma` (min_split_loss) | 0 | [0, ∞) | Min loss reduction to split |
| `max_delta_step` | 0 | [0, ∞) | Max leaf output change; useful for imbalanced logistic |
| `scale_pos_weight` | 1 | [0, ∞) | Balance pos/neg weights; use `sum(neg)/sum(pos)` |

### Tree Structure

| Parameter | Default | Range | Description |
|---|---|---|---|
| `max_depth` | 6 | [0, ∞) | Max tree depth; 0 = unlimited |
| `max_leaves` | 0 | [0, ∞) | Max leaves; used with `lossguide` grow policy |
| `min_child_weight` | 1 | [0, ∞) | Min hessian sum in child node |
| `grow_policy` | `depthwise` | — | `depthwise` or `lossguide` (hist/approx only) |

### Subsampling

| Parameter | Default | Range | Description |
|---|---|---|---|
| `subsample` | 1.0 | (0, 1] | Row subsample ratio per iteration |
| `sampling_method` | `uniform` | — | `uniform` or `gradient_based` (hist only) |
| `colsample_bytree` | 1.0 | (0, 1] | Column subsample per tree |
| `colsample_bylevel` | 1.0 | (0, 1] | Column subsample per depth level |
| `colsample_bynode` | 1.0 | (0, 1] | Column subsample per split |

Column sampling is cumulative: `colsample_bytree=0.5, colsample_bylevel=0.5, colsample_bynode=0.5` with 64 features leaves ~8 features at each split.

### Regularization

| Parameter | Default | Range | Description |
|---|---|---|---|
| `reg_lambda` (lambda) | 1 | [0, ∞) | L2 regularization on weights |
| `reg_alpha` (alpha) | 0 | [0, ∞) | L1 regularization on weights |

### Tree Method

| Parameter | Default | Description |
|---|---|---|
| `tree_method` | `hist` | `auto` (=hist), `exact`, `approx`, `hist` |
| `max_bin` | 256 | Max bins for hist/approx |
| `max_cached_hist_node` | 65536 | Max cached histogram nodes |

- `auto` — same as `hist` since 2.0
- `exact` — exhaustive search; slow on large data; no categorical support
- `approx` — quantile sketch + histogram
- `hist` — optimized histogram (default); fastest, supports categoricals

### DART-specific

| Parameter | Default | Description |
|---|---|---|
| `rate_drop` | 0.001 | Dropout rate per iteration |
| `skip_drop` | 0.5 | Probability of skipping dropout |
| `refresh_leaf` | 1 | Refresh leaf values during update |

### Process Control

| Parameter | Default | Description |
|---|---|---|
| `process_type` | `default` | `default` (new trees) or `update` (modify existing) |
| `num_parallel_tree` | 1 | Parallel trees per iteration (random forest) |
| `multi_strategy` | `one_output_per_tree` | `one_output_per_tree` or `multi_output_tree` |

## Categorical Feature Parameters

| Parameter | Default | Description |
|---|---|---|
| `max_cat_to_onehot` | 10 | Threshold for one-hot vs. partition split |
| `max_cat_threshold` | 10 | Max categories for one-hot encoding |
| `enable_categorical` | True | Enable native categorical (sklearn interface) |

## Task-Specific Parameters

### Intercept

| Parameter | Default | Description |
|---|---|---|
| `base_score` | auto-estimated | Initial prediction for all instances |

Since 3.1.0, `base_score` is automatically estimated from labels. To disable, pass an explicit float.

### Random Seed

| Parameter | Default | Description |
|---|---|---|
| `seed` | 0 | Random seed (native API) |
| `seed_per_iteration` | false | Deterministic seeding per iteration |

### Constraints

| Parameter | Default | Description |
|---|---|---|
| `monotone_constraints` | None | e.g., `{"age": 1, "income": -1}` or `"(1,0,-1,1)"` |
| `interaction_constraints` | None | e.g., `[[0, 1], [2, 3, 4]]` — feature groups that can interact |

## Learning-to-Rank Parameters

| Parameter | Default | Description |
|---|---|---|
| `lambdarank_pair_method` | `topk` | `mean` or `topk` |
| `lambdarank_num_pair_per_sample` | — | Pairs per sample / truncation level |
| `lambdarank_normalization` | true | Normalize leaf value by lambda gradient |
| `lambdarank_score_normalization` | true | Normalize by score difference (3.0.0+) |
| `lambdarank_unbiased` | false | Position-bias debiasing |
| `lambdarank_sigmoid` | 0.3 | Sigmoid parameter for pairwise loss |

## Tweedie Regression (`objective=reg:tweedie`)

| Parameter | Default | Range | Description |
|---|---|---|---|
| `tweedie_variance_power` | 1.5 | (1, 2) | Closer to 2 = gamma-like; closer to 1 = poisson-like |

## Quantile Regression (`objective=reg:quantileerror`)

| Parameter | Default | Description |
|---|---|---|
| `quantile_alpha` | 0.5 | Scalar or list of quantiles, e.g., `[0.1, 0.5, 0.9]` |

## Expectile Regression (`objective=reg:expectileerror`)

| Parameter | Required | Description |
|---|---|---|
| `expectile_alpha` | Yes | Scalar or sorted list of expectiles in [0, 1] |

New in 3.3.0. Unlike quantile, expectile does not suffer from curve crossing.

## AFT Survival (`objective=survival:aft`)

| Parameter | Default | Description |
|---|---|---|
| `aft_loss_distribution` | `normal` | `normal`, `logistic`, or `extreme` |
| `aft_loss_distribution_scale` | 1.0 | Scale factor for the AFT distribution |

## Pseudo-Huber (`objective=reg:pseudohubererror`)

| Parameter | Default | Description |
|---|---|---|
| `huber_slope` | 1.0 | Delta term controlling smoothness |

## Parameter Tuning Strategy

**High-impact parameters to tune first:**
1. `learning_rate` + `n_estimators` — trade-off between speed and accuracy
2. `max_depth` — model complexity
3. `subsample` / `colsample_bytree` — regularization via subsampling
4. `min_child_weight` — prevents overfitting on small groups
5. `reg_alpha` / `reg_lambda` — L1/L2 regularization

**Typical ranges:**
- `learning_rate`: 0.01–0.3 (lower with more trees)
- `max_depth`: 3–12 (3–6 for high regularization, 8–12 for complex patterns)
- `subsample`: 0.6–1.0
- `colsample_bytree`: 0.6–1.0
- `min_child_weight`: 1–10
- `reg_lambda`: 0.1–10
- `reg_alpha`: 0–1
