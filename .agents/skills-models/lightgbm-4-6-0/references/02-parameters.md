# Parameters — LightGBM 4.6.0

## Core Parameters

| Parameter | Default | Type | Description |
|---|---|---|---|
| `objective` | `regression` | enum | Loss function. See objectives reference |
| `boosting` | `gbdt` | enum | `gbdt` (traditional), `dart` (dropout), `rf` (random forest). For DART, LightGBM uses GBDT mode for first `1/learning_rate` iterations |
| `data_sample_strategy` | `bagging` | enum | `bagging` (random sampling) or `goss` (gradient-based one-side sampling). New in 4.0.0 |
| `num_iterations` | 100 | int | Number of boosting rounds. Aliases: `n_estimators`, `num_boost_round`, `num_trees`, `num_round` |
| `learning_rate` | 0.1 | float | Shrinkage rate. Lower values need more iterations. Aliases: `eta`, `shrinkage_rate` |
| `num_leaves` | 31 | int | Max leaves per tree (1–131072). Primary complexity control |
| `tree_learner` | `serial` | enum | `serial`, `feature` (feature parallel), `data` (data parallel), `voting` (voting parallel) |
| `num_threads` | 0 | int | Thread count. 0 = OpenMP default. Set to real CPU core count, not hyperthreads |
| `device_type` | `cpu` | enum | `cpu`, `gpu` (OpenCL), `cuda` (NVIDIA). GPU requires source build |
| `seed` | None | int | Master seed. Lower priority than individual seeds. Aliases: `random_seed`, `random_state` |
| `deterministic` | false | bool | Ensures stable results across different `num_threads`. Slows training |
| `verbosity` | 1 | int | `<0` fatal, `0` error/warning, `1` info, `>1` debug. Aliases: `verbose` |

## Learning Control Parameters

| Parameter | Default | Description |
|---|---|---|
| `max_depth` | -1 (no limit) | Max tree depth. Leaf-wise still applies. Use on small datasets to prevent overfitting |
| `min_data_in_leaf` | 20 | Min samples per leaf. Primary overfitting guard. Approximate (Hessian-based) |
| `min_sum_hessian_in_leaf` | 1e-3 | Min hessian sum per leaf. Alternative overfitting guard |
| `min_gain_to_split` | 0.0 | Min gain to perform a split. Speeds training and regularizes |
| `max_delta_step` | 0.0 | Max leaf output. Final cap is `learning_rate * max_delta_step`. Aliases: `max_leaf_output` |
| `lambda_l1` | 0.0 | L1 regularization on leaf weights. Aliases: `reg_alpha` |
| `lambda_l2` | 0.0 | L2 regularization on leaf weights. Aliases: `reg_lambda`, `l2_regularization` |
| `linear_lambda` | 0.0 | Linear tree regularization |
| `path_smooth` | 0 | Smooths tree nodes, prevents overfitting on small leaves. Requires `min_data_in_leaf >= 2` |
| `feature_fraction` | 1.0 | Fraction of features per tree (0–1]. Speeds training + regularizes. Aliases: `colsample_bytree` |
| `feature_fraction_bynode` | 1.0 | Fraction of features per node (0–1]. Regularizes only. Combined with `feature_fraction` multiplicatively |
| `bagging_fraction` | 1.0 | Fraction of data per round (0–1]. Requires `bagging_freq > 0`. Aliases: `subsample` |
| `bagging_freq` | 0 | Bagging interval. 0 = disabled, k = every k iterations |
| `bagging_by_query` | false | Bag by query group. New in 4.6.0 |
| `pos_bagging_fraction` | 1.0 | Positive sample fraction for imbalanced binary. Requires `bagging_freq` and `neg_bagging_fraction` |
| `neg_bagging_fraction` | 1.0 | Negative sample fraction for imbalanced binary |
| `extra_trees` | false | Extremely randomized trees. Checks only one random threshold per feature. Speeds training |
| `early_stopping_round` | 0 | Stop if no improvement in N rounds. Aliases: `n_iter_no_change` |
| `early_stopping_min_delta` | 0.0 | Min improvement delta for early stopping. New in 4.4.0 |
| `first_metric_only` | false | Use only first metric for early stopping when multiple metrics given |

### DART-Specific Parameters

| Parameter | Default | Description |
|---|---|---|
| `drop_rate` | 0.1 | Fraction of previous trees to drop (0–1) |
| `max_drop` | 50 | Max trees dropped per iteration. <=0 = no limit |
| `skip_drop` | 0.5 | Probability of skipping dropout procedure |
| `xgboost_dart_mode` | false | Use XGBoost-compatible DART mode |
| `uniform_drop` | false | Use uniform drop instead of probability-based |

### GOSS-Specific Parameters

| Parameter | Default | Description |
|---|---|---|
| `top_rate` | 0.2 | Retain ratio of large gradient data |
| `other_rate` | 0.1 | Retain ratio of small gradient data |

### Categorical Feature Parameters

| Parameter | Default | Description |
|---|---|---|
| `min_data_per_group` | 100 | Min data per categorical group |
| `max_cat_threshold` | 32 | Max split points for categorical features |
| `cat_l2` | 10.0 | L2 regularization in categorical split |
| `cat_smooth` | 10.0 | Reduces noise effect in categorical features |
| `max_cat_to_onehot` | 4 | Below this cardinality, use one-vs-other split |

### Monotone Constraints

| Parameter | Default | Description |
|---|---|---|
| `monotone_constraints` | None | Per-feature: `1` increasing, `-1` decreasing, `0` unconstrained |
| `monotone_constraints_method` | `basic` | `basic` (fast, over-constrains), `intermediate`, `advanced` (slowest, least constraining) |
| `monotone_penalty` | 0.0 | Penalizes monotone splits on first X tree levels |

### Interaction Constraints

```python
# Restrict which features can appear together in a branch
params = {
    "interaction_constraints": [[0, 1, 2], [2, 3]]
}
# Features 0,1,2 can interact; features 2,3 can interact; but 0 and 3 cannot
```

### Cost-Effective Gradient Boosting (CEGB)

| Parameter | Default | Description |
|---|---|---|
| `cegb_tradeoff` | 1.0 | Multiplier for all CEGB penalties |
| `cegb_penalty_split` | 0.0 | Penalty for splitting a node |
| `cegb_penalty_feature_lazy` | 0 per feature | Per-data-point penalty for using a feature |
| `cegb_penalty_feature_coupled` | 0 per feature | Per-forest penalty for using a feature |

### Feature Contribution Control

```python
# Control split gain per feature: gain[i] = max(0, feature_contri[i]) * gain[i]
params = {"feature_contri": [1.0, 0.5, 0.0, 2.0]}  # suppress feature 2, boost feature 3
```

### Forced Splits

```python
# Force specific splits at top of every tree (JSON file path)
params = {"forcedsplits_filename": "splits.json"}
```

## Dataset Parameters

| Parameter | Default | Description |
|---|---|---|
| `max_bin` | 255 | Max histogram bins per feature. Smaller = less accuracy, more generalization |
| `max_bin_by_feature` | None | Per-feature max bins |
| `min_data_in_bin` | 3 | Min data per bin. Avoids one-data-one-bin |
| `bin_construct_sample_cnt` | 200000 | Samples used to construct bins. Aliases: `subsample_for_bin` |
| `linear_tree` | false | Piecewise linear trees. Linear model at each leaf. CPU/GPU only, serial only |
| `is_enable_sparse` | true | Enable sparse optimization |
| `enable_bundle` | true | Enable Exclusive Feature Bundling (EFB) |
| `use_missing` | true | Special handling of missing values |
| `zero_as_missing` | false | Treat zeros as missing |
| `feature_pre_filter` | true | Pre-filter unsplittable features based on `min_data_in_leaf` |
| `force_col_wise` | false | Force column-wise histogram building. Recommended for many columns or many threads |
| `force_row_wise` | false | Force row-wise histogram building. Recommended for many data points, few threads. Doubles memory |
| `histogram_pool_size` | -1 (no limit) | Max cache size in MB for historical histograms |

## Objective-Specific Parameters

| Parameter | Default | Used With |
|---|---|---|
| `num_class` | 1 | `multiclass`, `multiclassova` |
| `is_unbalance` | false | `binary`, `multiclassova` |
| `scale_pos_weight` | 1.0 | `binary`, `multiclassova` |
| `sigmoid` | 1.0 | `binary`, `multiclassova`, `lambdarank` |
| `boost_from_average` | true | `regression`, `binary`, `multiclassova`, `cross-entropy` |
| `reg_sqrt` | false | `regression` — fits sqrt(label), outputs prediction^2 |
| `alpha` | 0.9 | `huber`, `quantile` |
| `fair_c` | 1.0 | `fair` |
| `poisson_max_delta_step` | 0.7 | `poisson` |
| `tweedie_variance_power` | 1.5 | `tweedie` (1.0–2.0) |
| `lambdarank_truncation_level` | 30 | `lambdarank` |
| `lambdarank_norm` | true | `lambdarank` |
| `label_gain` | 0,1,3,7,... | `lambdarank`, `rank_xendcg` |
| `objective_seed` | 5 | `rank_xendcg` |

## Prediction Parameters

| Parameter | Default | Description |
|---|---|---|
| `predict_raw_score` | false | Return raw scores instead of transformed |
| `predict_leaf_index` | false | Return leaf index for all trees |
| `predict_contrib` | false | Return SHAP-style feature contributions |
| `predict_disable_shape_check` | false | Allow prediction with different feature count (dangerous) |
| `pred_early_stop` | false | Early-stop prediction for speed (classification/ranking only) |
| `pred_early_stop_freq` | 10 | Check frequency for prediction early stopping |
| `pred_early_stop_margin` | 10.0 | Margin threshold for prediction early stopping |

## Quantized Training Parameters (New in 4.0.0)

| Parameter | Default | Description |
|---|---|---|
| `use_quantized_grad` | false | Quantize gradients/hessians into bins. CPU and CUDA only |
| `num_grad_quant_bins` | 4 | Number of quantization bins. More = closer to full precision |
| `quant_train_renew_leaf` | false | Renew leaf values with original gradients. Helpful for ranking |
| `stochastic_rounding` | true | Use stochastic rounding in quantization |

## GPU Parameters

| Parameter | Default | Description |
|---|---|---|
| `gpu_platform_id` | -1 | OpenCL platform ID. -1 = system default |
| `gpu_device_id` | -1 | GPU device ID. -1 = default device |
| `gpu_use_dp` | false | Use double precision on GPU (OpenCL only; CUDA always double) |
| `num_gpu` | 1 | Number of GPUs (CUDA only) |

## Network Parameters (Distributed)

| Parameter | Default | Description |
|---|---|---|
| `num_machines` | 1 | Number of machines |
| `local_listen_port` | 12400 | TCP listen port |
| `time_out` | 120 | Socket timeout in minutes |
| `machines` | "" | Machine list: `ip1:port1,ip2:port2` |

## Refit Parameter

| Parameter | Default | Description |
|---|---|---|
| `refit_decay_rate` | 0.9 | Decay for refit: `leaf = decay * old + (1-decay) * new` |
