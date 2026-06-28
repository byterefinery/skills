# TabularPredictor API Reference

## Constructor

```python
TabularPredictor(
    label: str,
    problem_type: str = None,          # 'binary', 'multiclass', 'regression', 'quantile'
    eval_metric: str = None,           # auto-selected based on problem_type
    path: str = None,                  # save directory (default: timestamped)
    verbosity: int = 2,                # 0-4, higher = more output
    log_to_file: bool = False,
    sample_weight: str = None,         # column name or 'auto_weight' / 'balance_weight'
    weight_evaluation: bool = False,
    groups: str = None,                # column for group-aware validation
    positive_class: str | int = None,  # positive class in binary classification
    quantile_levels: list[float] = None,  # for quantile regression
)
```

Default eval metrics: `accuracy` (binary/multiclass), `root_mean_squared_error` (regression), `pinball_loss` (quantile).

### Eval Metrics by Problem Type

**Classification:** `accuracy`, `balanced_accuracy`, `roc_auc`, `roc_auc_ovo`, `roc_auc_ovo_macro`, `roc_auc_ovo_weighted`, `average_precision`, `average_precision_ovo`, `f1`, `f1_macro`, `f1_micro`, `f1_weighted`, `log_loss`, `mcc`, `pac_score`.

**Regression:** `root_mean_squared_error`, `mean_absolute_error`, `mean_absolute_percentage_error`, `r2`, `median_absolute_error`, `spearman_correlation`, `pearson_correlation`, `mean_squared_log_error`.

**Quantile:** `pinball_loss`.

## fit()

```python
predictor.fit(
    train_data: pd.DataFrame | str,
    tuning_data: pd.DataFrame | str = None,
    time_limit: float = None,
    presets: str | list[str] = None,
    hyperparameters: str | dict = None,
    feature_metadata: str | FeatureMetadata = "infer",
    infer_limit: float = None,
    fit_weighted_ensemble: bool = True,
    dynamic_stacking: bool | str = False,
    num_cpus: int | str = "auto",
    num_gpus: int | str = "auto",
    memory_limit: float | str = "auto",
    fit_strategy: Literal["sequential", "parallel"] = "sequential",
)
```

### Presets (full list)

- `extreme_quality` — TabPFNv2, TabICL, TabDPT, Mitra. GPU required. `pip install autogluon.tabular[tabarena]`.
- `best_quality_v150` — v1.5 improved best quality, 5x+ faster than `best_quality`.
- `best_quality` — zero-shot portfolio (~100 models) + stacking. Max accuracy.
- `high_quality_v150` — v1.5 improved high quality.
- `high_quality` — zero-shot + refit_full. ~8x faster inference than best.
- `good_quality` — light hyperparameters + refit_full. Fast inference.
- `medium_quality` — default. No stacking. Fast training.
- `experimental_quality` — cutting-edge features for testing.
- `optimize_for_deployment` — delete unused models, save space.
- `interpretable` — only interpretable rule-based models (requires `imodels`).
- `ignore_text` — disable text feature generation.

### Hyperparameter Presets

- `default` — strong accuracy, reasonable size
- `zeroshot` — ~100-model portfolio from TabRepo (used by `best_quality`)
- `zeroshot_2025_tabfm` — TabArena portfolio with foundation models (used by `extreme_quality`)
- `light` — smaller models, faster inference
- `very_light` — much smaller, lower accuracy
- `toy` — extremely small, prototyping only
- `multimodal` — transformer + tabular models (requires GPU)
- `interpretable` — rule-based models from imodels

### Model Type Keys

**Stable:** `GBM` (LightGBM), `CAT` (CatBoost), `XGB` (XGBoost), `EBM` (Explainable Boosting), `REALMLP`, `TABM`, `MITRA`, `TABICL`, `TABPFNV2`, `RF`, `XT`, `KNN`, `LR`, `NN_TORCH`, `FASTAI`, `AG_AUTOMM`.

**Experimental:** `TABPFNV2`, `TABICL`, `TABDPT`, `TABM`.

### Hyperparameter Tuning

```python
from autogluon.common import space

hyperparameters = {
    "NN_TORCH": {"num_epochs": 10, "dropout_prob": space.Real(0.0, 0.5)},
    "GBM": {"learning_rate": space.Real(0.01, 0.1, log=True)},
}

predictor.fit(
    train_data,
    hyperparameters=hyperparameters,
    hyperparameter_tune_kwargs="auto",
    time_limit=300,
)
```

## Prediction Methods

```python
predictor.predict(data)                      # class labels or regression values
predictor.predict_proba(data)                 # probability estimates
predictor.predict_proba(data, as_multiclass=True)  # multiclass probability matrix
```

## Evaluation

```python
predictor.evaluate(test_data)                          # shorthand: predict + evaluate
predictor.evaluate_predictions(y_true, y_pred, auxiliary_metrics=True)
predictor.leaderboard(data=None, extra_info=False)     # model comparison table
```

## Feature Importance

```python
predictor.feature_importance(data, features=None, model=None,
                              explanation_mode="feature_contribution")
```

Modes: `feature_contribution` (default, SHAP-like), `permutation`, `mean_decrease_impurity`.

## Model Management

```python
predictor.leaderboard()                              # compare all trained models
predictor.delete_models(models_to_keep="best")       # remove inferior models
predictor.save_space()                               # remove training artifacts
predictor.refit_full(models=None)                    # retrain on all data
predictor.persist(models="best", max_memory=0.4)     # keep models in memory for fast inference
predictor.compile(models="best")                     # compile to ONNX (requires skl2onnx)
```

## Save / Load

```python
predictor.save()                                      # auto-saved to path on fit()
loaded = TabularPredictor.load(path)
```

## fit_summary()

```python
predictor.fit_summary(verbosity=3, show_plot=False)
```

Returns dict with training times, model performances, and stack configuration.

## Quantile Regression

```python
predictor = TabularPredictor(
    label="target",
    problem_type="quantile",
    quantile_levels=[0.1, 0.5, 0.9],
)
predictor.fit(train_data)
predictions = predictor.predict(test_data)  # returns DataFrame with quantile columns
```

## Augmented Fit

```python
# Add more training data to an existing predictor
predictor.fit(train_data=additional_data)

# Pseudolabeling: use trained models to label unlabeled data, then retrain
predictor.fit_pseudolabel(pseudolabel_data, num_classes=None, subsample_size=100000)

# Fit extra models on top of existing ones
predictor.fit_extra(hyperparameters={"CAT": {}}, set_best_to_fit_extra=True)
```

## Out-of-Fold Predictions

```python
predictor.predict_oof(model=None)  # predictions on training data via cross-validation
predictor.predict_proba_oof(model=None)
```
