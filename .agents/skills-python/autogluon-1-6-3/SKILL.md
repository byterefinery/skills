---
name: autogluon-1-6-3
description: >
  AutoGluon 1.6.3 — automated machine learning for tabular data (TabularPredictor),
  time series forecasting (TimeSeriesPredictor), and multimodal data (MultiModalPredictor).
  Use when the user needs quick high-accuracy ML models with minimal code, automated
  hyperparameter tuning, ensemble stacking, or tabular foundation models (Nori, TabICLv2,
  TabDPT-Turbo, TabPFN-3/2.6, Mitra). Covers binary/multiclass classification, regression,
  quantile regression, probabilistic forecasting with Toto-2/Chronos-2, image/text/tabular
  prediction, object detection, NER, and semantic matching.
metadata:
  tags:
    - ml
    - automl
    - tabular
    - time-series
    - multimodal
    - deep-learning
---

# autogluon 1.6.3

## Overview

AutoGluon 1.6.3 automates end-to-end ML workflows across three modalities:

- **TabularPredictor** — classification, regression, and quantile regression on structured data. Supports LightGBM, XGBoost, CatBoost, random forests, neural networks, and foundation models (Nori, TabICLv2, TabDPT-Turbo, TabPFN-3, TabPFN-2.6, Mitra).
- **TimeSeriesPredictor** — probabilistic multi-step-ahead forecasting with quantile predictions. Supports Toto-2, Chronos-2, DeepAR, TFT, N-BEATS, and statistical models (ARIMA, ETS, Theta).
- **MultiModalPredictor** — image, text, and combined multimodal prediction: classification, regression, object detection, NER, semantic matching, feature extraction.

Install with `pip install autogluon` (all modules) or per module: `pip install autogluon.tabular`, `autogluon.timeseries`, `autogluon.multimodal`. Supports Python 3.10–3.13. Models trained on older AutoGluon versions cannot be loaded; re-train with 1.6.x.

## Usage

### Tabular Data

```python
from autogluon.tabular import TabularPredictor

predictor = TabularPredictor(label="target").fit(train_data, presets="extreme_quality")
predictions = predictor.predict(test_data)
score = predictor.evaluate(test_data)
leaderboard = predictor.leaderboard(test_data)
```

Pass raw data — do not pre-impute missing values or one-hot encode; AutoGluon handles both automatically.

Presets (composable as a list, e.g. `["good_quality", "optimize_for_deployment"]`):

| Preset | When to use |
|---|---|
| `medium_quality` | Default. Fast training for prototyping only; `good_quality` is much more accurate at similar inference time. |
| `good_quality` | Strong accuracy, very fast inference. ~20x faster training than this level's predecessor tiers. |
| `high_quality` | High accuracy with fast inference (~8x faster inference and lower disk usage than `best_quality`). Uses `refit_full`. |
| `best_quality` | Best CPU-oriented accuracy; auto-stacking, zero-shot portfolio, 1h time limit by default. |
| `extreme_quality` | New in 1.6 — recommended when a GPU is available (40+ GB VRAM ideal). Led by Nori, TabICLv2, TabDPT-Turbo + TabPrep LightGBM; every model free for commercial use. ~27x faster training than 1.5 `extreme`. |
| `noncommercial` | New in 1.6 (experimental) — `extreme_quality` plus TabPFN-3 (Prior Labs). SOTA on TabArena-Lite; TabPFN-3 requires a commercial license from Prior Labs for production use. |
| `optimize_for_deployment` | Combine with any quality preset to delete unused models and shrink the artifact. |

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
from autogluon.timeseries import TimeSeriesPredictor, TimeSeriesDataFrame

ts = TimeSeriesDataFrame.from_data_frame(df, id_column="item_id", timestamp_column="timestamp")
predictor = TimeSeriesPredictor(
    target="target",
    prediction_length=48,
    path="my-forecast-model",
    eval_metric="MASE",
).fit(ts, presets="medium_quality", time_limit=600)

forecasts = predictor.predict(ts)          # DataFrame of quantiles (e.g. 0.1, 0.5, 0.9)
predictor.leaderboard(test_data)           # per-model scores on held-out window
```

Presets: `best_quality`, `high_quality`, `medium_quality` (light models), `fast_training`, plus zero-shot presets `chronos2`, `chronos2_small`, and `bolt_{tiny|mini|small|base}`. New in 1.6: Toto-2 pretrained forecasting model; new metrics `MAEB`, `WAPEB`, `BIAS`, `MQL`; `TimeSeriesPredictor.export_model` for standalone checkpoints that load without AutoGluon; experimental `update()` for ensemble re-selection on fresh data.

### Multimodal Data

```python
from autogluon.multimodal import MultiModalPredictor

# Text classification/regression: pass a dict or DataFrame with text columns
predictor = MultiModalPredictor(label="label").fit(train_data, time_limit=60)
predictions = predictor.predict({"sentence": ["a sentence", "another"]})
probs = predictor.predict_proba(test_data)
score = predictor.evaluate(test_data, metrics=["acc", "f1"])

# Image classification: column with image paths (or raw bytes) named per data
predictor.fit(train_data_path_or_df)
predictions = predictor.predict({"image": ["/path/to/img.jpg"]})
```

`MultiModalPredictor.load(model_path)` restores a saved model; `predictor.extract_embedding(...)` produces features. Regression uses `label` as numeric target and metrics like `rmse`, `pearsonr`, `spearmanr`.

## Gotchas

- **1.6 presets differ from 1.5** — `extreme_quality` is now the GPU-recommended preset (new portfolio: Nori, TabICLv2, TabDPT-Turbo); the old 1.5 behavior is preserved only under aliases like `extreme_quality_v150`. Models trained on <1.6 cannot be loaded by 1.6 — re-train.
- **`noncommercial` is experimental** — may change or be removed without warning; TabPFN-3 inside it is free for research/internal use but requires a Prior Labs license for commercial use.
- **`extreme_quality`/`noncommercial` need GPU** — they use pretrained tabular foundation models (adds ≥100 MB to the artifact). Without a GPU, prefer `best_quality`/`high_quality`.
- **Do not preprocess data yourself** — no imputation, no one-hot encoding; AutoGluon's feature engineering handles these and manual preprocessing can hurt.
- **`tuning_data` is for model selection, not evaluation** — final scores should come from truly held-out data via `predictor.evaluate()`/`leaderboard()`. When using stacking/bagging (`num_bag_folds`, `auto_stack`), do not pass `tuning_data`; give all data as `train_data`.
- **Metrics are always shown higher-is-better** — RMSE, log_loss etc. have their sign flipped (negative) in leaderboards; don't read a negative score as "worse than 0".
- **Time series data must be a `TimeSeriesDataFrame`** — build with `TimeSeriesDataFrame.from_data_frame(df, id_column=..., timestamp_column=...)`; predictions cover `prediction_length` steps per series.
- **Disk usage from repeated fits** — each `fit()` writes to `path` (default `AutogluonModels/ag-[TIMESTAMP]`). Delete old artifact folders or call `predictor.save_space()` when disk runs low.
- **`TabularPredictor.load()` uses pickle** — only load artifacts you trust.

## References

- [01-tabular-api](references/01-tabular-api.md) — TabularPredictor: fit options, presets detail, foundation models, validation structure, inference controls
- [02-timeseries-api](references/02-timeseries-api.md) — TimeSeriesPredictor: data format, presets, metrics, export_model, model zoo
- [03-multimodal-api](references/03-multimodal-api.md) — MultiModalPredictor: text/image inputs, problem types, evaluation, embeddings
