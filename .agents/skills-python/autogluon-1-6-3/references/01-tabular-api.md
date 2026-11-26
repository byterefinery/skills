# TabularPredictor API (AutoGluon 1.6.3)

## Core workflow

```python
from autogluon.tabular import TabularPredictor, TabularDataset

train_data = TabularDataset("train.csv")   # or any pandas DataFrame / parquet
predictor = TabularPredictor(label="target", eval_metric="accuracy").fit(train_data, presets="good_quality")

predictions = predictor.predict(test_data)              # best model (usually weighted ensemble)
probs = predictor.predict_proba(test_data)              # class probabilities
specific = predictor.predict(test_data, model="LightGBM")  # pin a specific model
score = predictor.evaluate(test_data)                   # single score under eval_metric
lb = predictor.leaderboard(test_data, extra_metrics=["log_loss"])
```

- Data formats: pandas DataFrame, CSV, or Parquet. Multiple tables must be joined into one table where rows are independent observations.
- Problem type is inferred automatically (binary / multiclass / regression / quantile). Set `problem_type=` in the constructor to override.
- `eval_metric` defaults per problem type (accuracy for binary, RMSE shown as negative for regression since all metrics are displayed higher-is-better).

## Key fit() arguments

| Argument | Notes |
|---|---|
| `presets` | str or list of strs; composable. See preset table in SKILL.md. Default `medium_quality`. |
| `time_limit` | Seconds. Stop training after this; higher = better, too low prevents reasonable ensembling. |
| `hyperparameters` | Dict mapping model keys (`"GBM"`, `"CAT"`, `"XGB"`, `"RF"`, `"NN_TORCH"`, …) to config dict or list of dicts; or a named portfolio string used by presets (e.g. `"zeroshot"`). |
| `num_bag_folds` | k-fold bagging; ~k× training time. 0 disables, 1 is invalid, >10 may overfit. Recommend 5–10. |
| `num_bag_sets` | Repeats of the k-fold process; total models = folds × sets. Drastically increases runtime; last resort. |
| `auto_stack` | Lets AutoGluon pick bagging/stacking values automatically (used by quality presets). Do not pass `tuning_data` when stacking/bagging is active — give all data as `train_data`. |
| `num_stack_levels` | Stacking levels; ~ (levels+1)× training time. Requires `num_bag_folds >= 2` or ValueError. |
| `refit_full` | Refit each model on the full dataset (no validation split); used by `high_quality`. |
| `calibrate_decision_threshold` | Default `"auto"` — AutoGluon calibrates when beneficial for binary metrics like f1/balanced_accuracy. Set True/False or a float to control. |
| `validation_structure` | New in 1.6 — dict describing non-IID structure: `group_on`, `time_on`, `group_time_on`, `stratify_on`, `size_validation_on_groups`, `temporal_forward_only`. Splits honor groups/time instead of IID rows; mutually exclusive with the legacy `groups` init argument. |
| `validation_size_curves` | [EXPERIMENTAL] size-driven overrides for validation knobs (e.g. more bagging sets on small data). |
| `infer_limit`, `infer_limit_batch_size` | Declare a latency constraint at fit time; AutoGluon trains to satisfy it. |
| `feature_generator=None` + `feature_metadata=` | Disable built-in preprocessing entirely (advanced; removes all guardrails). |

## Foundation models (1.6)

New/updated in 1.6: **Nori** (`ag_key="NORI"`), **TabICLv2**, **TabDPT-Turbo**, **TabPFN-3**, **TabPFN-2.6**, plus existing **Mitra**. Old TabPFNv2 code was removed; TabPFNv2 supports the quantile problem type.

Fit constraints: each model declares `ag.max_rows` / `ag.max_features` / `ag.max_classes`; above the limit the model is skipped (portfolio degrades to remaining models) rather than failing. Feature caps were lifted for TabPFN-2.6/TabPFN-3 in 1.6.

Presets that use them:
- `extreme_quality` — Nori + TabICLv2 + TabDPT-Turbo + TabPrep LightGBM; all free for commercial use; GPU strongly recommended (ideally 40+ GB VRAM); adds ≥100 MB to artifact.
- `noncommercial` — same plus TabPFN-3 (Prior Labs; commercial license required).

TabPrep feature engineering is built in: group-by aggregates, random-subset compression, arithmetic/categorical interactions, out-of-fold target encoding; models can declare per-model preprocessing via `ag.model_specific_feature_generator_kwargs`.

## Inference and deployment controls

- `predictor.features()` — required input columns.
- `predictor.transform_features(df)` + `predict(preprocessed, transform_features=False)` — cache preprocessing when repeatedly predicting on the same data.
- `persist(models="all")` / `persist(models=[...])` — load models into memory for fast repeated inference.
- `refit_full()` post-fit — collapse bagged copies into single full-data models (memory/latency win, possible accuracy loss).
- `delete_models(models_to_keep=...)`, `save_space()` — shrink artifact.
- Distillation exists but may drop accuracy significantly; prefer `refit_full` / `infer_limit` / `persist` first.
- Disk: repeated fits accumulate in `AutogluonModels/ag-[TIMESTAMP]` unless `path=` is set; delete old folders.

## Interpretability

`predictor.feature_importance()` — permutation-based importance (drop in eval metric if a column were shuffled). Negative values suggest the feature may be harmful. Memory usage reduced ~25x in 1.6.
