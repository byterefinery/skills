---
name: autogluon-1-5-0
description: >
  AutoGluon 1.5.0 — automated machine learning for tabular data (TabularPredictor),
  time series forecasting (TimeSeriesPredictor), and multimodal data (MultiModalPredictor).
  Use when the user needs quick high-accuracy ML models with minimal code, automated
  hyperparameter tuning, ensemble stacking, or zero-shot tabular foundation models
  (TabPFNv2, TabICL, TabDPT, Mitra). Covers binary/multiclass classification, regression,
  quantile regression, probabilistic forecasting, image/text/tabular prediction, object
  detection, and semantic matching.
metadata:
  tags:
    - ml
    - automl
    - tabular
    - time-series
    - multimodal
    - deep-learning
---

# autogluon 1.5.0

## Overview

AutoGluon 1.5.0 automates end-to-end ML workflows across three modalities:

- **TabularPredictor** — classification, regression, and quantile regression on structured/tabular data. Supports LightGBM, XGBoost, CatBoost, random forests, neural networks, and foundation models (TabPFNv2, TabICL, Mitra).
- **TimeSeriesPredictor** — probabilistic multi-step-ahead forecasting with quantile predictions. Supports DeepAR, TFT, N-BEATS, THOR, Chronos-2, Chronos-Bolt, and statistical models (ARIMA, ETS, Theta).
- **MultiModalPredictor** — image, text, and combined multimodal prediction. Supports classification, regression, object detection, NER, semantic matching, and feature extraction.

Install with `pip install autogluon` (all modules) or `pip install autogluon.tabular`, `autogluon.timeseries`, `autogluon.multimodal` individually. Requires Python 3.10–3.13.

## Usage

### Tabular Data

```python
from autogluon.tabular import TabularPredictor

predictor = TabularPredictor(label="target").fit(train_data, presets="best_quality")
predictions = predictor.predict(test_data)
```

Presets control the accuracy/effort trade-off:

| Preset | When to use |
|---|---|
| `medium_quality` | Default. Fast training, reasonable accuracy. Good for prototyping. |
| `good_quality` | Strong accuracy with fast inference. Uses `refit_full` for compact models. |
| `high_quality` | High accuracy, ~8x faster inference than `best_quality`. |
| `best_quality` | Maximum accuracy. Uses zero-shot portfolio (~100 models) + stacking. |
| `extreme_quality` | State-of-the-art. Requires GPU + `autogluon.tabular[tabarena]` for TabPFNv2, TabICL, TabDPT. |
| `optimize_for_deployment` | Combine with any quality preset to delete unused models and save disk space. |

Customize models explicitly:

```python
predictor.fit(
    train_data,
    hyperparameters={
        "GBM": {},
        "CAT": {},
        "XGB": {},
        "RF": {},
        "NN_TORCH": {},
    },
    time_limit=300,
)
```

### Time Series Forecasting

```python
from autogluon.timeseries import TimeSeriesPredictor

predictor = TimeSeriesPredictor(
    target="target",
    prediction_length=7,
    known_covariates_names=["promotion", "price"],
).fit(train_data, presets="high_quality")

forecasts = predictor.predict(test_data, known_covariates=future_covariates)
```

Presets: `fast_training`, `medium_quality`, `high_quality`, `best_quality`, `chronos2`, `chronos2_small`, `bolt_{tiny|mini|small|base}`.

### Multimodal Data

```python
from autogluon.multimodal import MultiModalPredictor

predictor = MultiModalPredictor(label="label").fit(
    train_data,
    presets="high_quality",
    hyperparameters={"model.hf_text.checkpoint_name": "google/electra-small-discriminator"},
)
predictions = predictor.predict(test_data)
```

## Gotchas

- **`tuning_data` is not test data** — it is used for model selection and ensemble weights. Providing test data as `tuning_data` biases model selection. Evaluate on truly held-out data with `predictor.leaderboard(test_data)`.
- **`extreme_quality` requires GPU and extra install** — run `pip install autogluon.tabular[tabarena]` to enable TabPFNv2, TabICL, and TabDPT models. Without GPU, these models will fail or fall back.
- **`best_quality` trains ~100 models** — it uses the zero-shot portfolio from TabRepo. Expect high disk usage and long training. Use `optimize_for_deployment` or `predictor.delete_models(models_to_keep="best")` after training to reduce size.
- **Time series requires `TimeSeriesDataFrame`** — data must have a multi-index of `(item_id, timestamp)` and a `target` column. Use `TimeSeriesDataFrame.from_dataframe()` to convert regular DataFrames.
- **Time series `known_covariates` must cover the forecast horizon** — when predicting, future covariate values must be provided for the full `prediction_length`. Use `predictor.make_future_data_frame()` to generate the required template.
- **`refit_full` retrain on all data** — when `refit_full=True`, models are retrained on `train_data` + `tuning_data` combined. This means `tuning_data` labels leak into the final model. Always validate on separate data.
- **`presets` are composable** — pass a list like `["good_quality", "optimize_for_deployment"]` to combine quality settings with deployment optimization. Later presets override earlier ones for conflicting keys.
- **Tabular `hyperparameters` dict keys are model type strings** — use `"GBM"`, `"CAT"`, `"XGB"`, `"RF"`, `"XT"`, `"KNN"`, `"LR"`, `"NN_TORCH"`, `"FASTAI"`, `"EBM"`, `"MITRA"`, `"TABICL"`, `"TABPFNV2"`, `"AG_AUTOMM"`. Values can be dicts (single model) or lists of dicts (multiple variants).
- **Multimodal column types are inferred** — pass `column_types={"col": "text"}` to override automatic inference. Supported types: `image_path`, `text`, `numerical`, `categorical`.
- **Mac GPU is not supported for multimodal** — Apple Silicon uses CPU-only for `MultiModalPredictor`. Install via conda for best compatibility on Mac.

## References

- [01-tabular-api](references/01-tabular-api.md) — TabularPredictor: constructors, fit, predict, evaluation, feature importance, compilation
- [02-timeseries-api](references/02-timeseries-api.md) — TimeSeriesPredictor: constructors, fit, predict, backtesting, model zoo
- [03-multimodal-api](references/03-multimodal-api.md) — MultiModalPredictor: constructors, fit, predict, problem types, hyperparameters
- [04-installation](references/04-installation.md) — Installation guides: pip, uv, conda, GPU, platform-specific
