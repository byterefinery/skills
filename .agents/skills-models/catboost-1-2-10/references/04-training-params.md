# Training Parameters Reference

## Core Parameters

| Parameter | Default | Range | Description |
|---|---|---|---|
| `iterations` | 500 | [1, ∞) | Maximum number of trees |
| `learning_rate` | auto / 0.03 | (0, 1] | Step size shrinkage |
| `depth` | 6 | [1, 16] | Tree depth |
| `l2_leaf_reg` | 3.0 | [0, ∞) | L2 regularization on leaf values |
| `model_size_reg` | None | [0, ∞) | Model size regularization |
| `rsm` | None | (0, 1] | Column subsample ratio per tree |
| `border_count` | 254 (CPU) / 128 (GPU) | [1, 65535] (CPU), [1, 255] (GPU) | Numeric feature partition count |
| `random_seed` | None (0) | [0, ∞) | Random seed for reproducibility |

## Boosting Parameters

| Parameter | Default | Description |
|---|---|---|
| `boosting_type` | auto | `'Ordered'` (better quality, slower) or `'Plain'` (classic GB, faster) |
| `bootstrap_type` | `'Bayesian'` (GPU) / `'MVS'` (CPU) | `'Bayesian'`, `'Bernoulli'`, `'Poisson'`, `'MVS'`, `'No'` |
| `subsample` | None | Fraction of samples used (for Bernoulli/Poisson/MVS) |
| `bagging_temperature` | None | Bayesian bagging intensity. [0, 1], 0 = no bagging, 1 = default |
| `fold_len_multiplier` | None | Fold length multiplier (>1) |
| `fold_permutation_block` | 1 | Block size for permutation. [1, 256]. Set to 1 for small datasets |
| `approx_on_full_history` | False | Use full history for approximations (slower, more accurate) |
| `eval_fraction` | 0.0 | Fraction of training data for internal eval. Cannot use with `eval_set` |

## Overfitting Control

| Parameter | Default | Description |
|---|---|---|
| `od_type` | None | `'IncToDec'` (uses `od_pval`) or `'Iter'` (uses `od_wait`). None = `'IncToDec'` |
| `od_pval` | None | p-value threshold for overfitting detection. [0, 1]. Only with `'IncToDec'` |
| `od_wait` | None | Iterations to wait after new best error. Used with `'Iter'` type |
| `use_best_model` | None | Use best model from eval_set in `predict()`. Requires `eval_set` |
| `best_model_min_trees` | None | Minimum trees the best model should have |

## Categorical Feature Parameters

| Parameter | Default | Description |
|---|---|---|
| `max_ctr_complexity` | 4 | Maximum number of categorical features combined. [0, ∞) |
| `ctr_leaf_count_limit` | None | Max leaves with categorical features. Reduces model size |
| `store_all_simple_ctr` | None | Keep all simple CTRs even if not in combinations |
| `simple_ctr` | None | CTR settings: `['Borders:CtrBorderCount=5', ...]` |
| `combinations_ctr` | None | Combination CTR settings |
| `per_feature_ctr` | None | Per-feature CTR settings |
| `ctr_target_border_count` | None | Max borders in target binarization. [1, 255] |
| `ctr_history_unit` | None | History unit for CTR computation |
| `one_hot_max_size` | None | Convert to one-hot if unique values exceed this |
| `nan_mode` | `'Min'` | `'Forbidden'`, `'Min'`, `'Max'` — how to handle NaN in numeric features |

## Leaf Estimation Parameters

| Parameter | Default | Description |
|---|---|---|
| `leaf_estimation_iterations` | None (1) | Gradient steps for leaf values. [1, ∞) |
| `leaf_estimation_method` | None | `'Newton'` or `'Gradient'` |
| `leaf_estimation_backtracking` | `'AnyImprovement'` | `'AnyImprovement'`, `'ArmijoBacktracking'`, `'No'` |
| `score_function` | `'Cosine'` | `'Cosine'` or `'L2'` |

## Feature Border Parameters

| Parameter | Default | Description |
|---|---|---|
| `feature_border_type` | `'GreedyLogSum'` | `'Median'`, `'Uniform'`, `'UniformAndQuantiles'`, `'GreedyLogSum'`, `'MaxLogSum'`, `'MinEntropy'` |
| `per_float_feature_quantization` | None | Per-feature quantization: `['0:1024', '1:border_count=32']` |
| `input_borders` | None | File with pre-computed borders |
| `output_borders` | None | File to write used borders |

## GPU Parameters

| Parameter | Default | Description |
|---|---|---|
| `task_type` | None | `'CPU'` or `'GPU'` |
| `devices` | None | GPU devices: `'0:1:3'`, `'0-3'`, or `[0, 1, 3]` |
| `device_config` | None | Deprecated, use `devices` |
| `gpu_ram_part` | 0.95 | Fraction of GPU RAM for training. (0, 1] |
| `pinned_memory_size` | None | CPU pinned memory for GPU training |
| `gpu_cat_features_storage` | None | GPU storage mode for categorical features |

## Regularization Parameters

| Parameter | Default | Description |
|---|---|---|
| `random_strength` | 1 | Score noise multiplier |
| `random_score_type` | `'NormalWithModelSizeDecrease'` | `'Gumbel'` or `'NormalWithModelSizeDecrease'` |
| `model_shrink_rate` | None | Model shrinkage rate |
| `model_shrink_mode` | None | Model shrinkage mode |
| `mvs_reg` | None | MVS regularization |
| `sampling_frequency` | None | `'PerTree'` or `'PerTreeAndInteraction'` |
| `sampling_unit` | None | Sampling unit for MVS |

## Constraint Parameters

| Parameter | Default | Description |
|---|---|---|
| `monotone_constraints` | None | Dict or list of -1/0/1 constraints per feature |
| `feature_weights` | None | Feature weights (path penalty multiplier) |
| `penalties_coefficient` | None | Penalty coefficient |
| `first_feature_use_penalties` | None | First feature penalty settings |
| `per_object_feature_penalties` | None | Per-object penalty settings |

## Miscellaneous Parameters

| Parameter | Default | Description |
|---|---|---|
| `thread_count` | -1 | Number of threads. -1 = all CPU cores |
| `used_ram_limit` | None | Memory limit: `'1.2gb'` or `1.2e9` |
| `train_dir` | None | Directory for training output files |
| `allow_writing_files` | True | Set False to prevent file creation |
| `name` | `'experiment'` | Name shown in visualization |
| `verbose` | None | bool or int (log frequency) |
| `silent` | None | Synonym for `verbose=False` |
| `logging_level` | `'Verbose'` | `'Silent'`, `'Verbose'`, `'Info'`, `'Debug'` |
| `metric_period` | 1 | Metric output frequency |
| `has_time` | False | Preserve input order (no shuffling) |
| `allow_const_label` | False | Allow constant label values |
| `boost_from_average` | True | Start from average target value |
| `final_ctr_computation_mode` | `'Default'` | `'Default'` or `'Skip'` |
| `data_partition` | None | Data partitioning mode |
| `grow_policy` | `'SymmetricTree'` | `'SymmetricTree'`, `'Lossguide'`, `'Depthwise'`, `'SymmetricHist'`, `'DepthwiseHist'` |
| `min_data_in_leaf` | None | Min samples in leaf |
| `max_leaves` | None | Max leaves per tree |
| `fixed_binary_splits` | None | Fixed binary split configuration |
| `dev_efb_max_buckets` | None | Max EFB buckets |
| `sparse_features_conflict_fraction` | None | Sparse feature conflict threshold |
| `dev_score_calc_obj_block_size` | None | Score calculation block size |
