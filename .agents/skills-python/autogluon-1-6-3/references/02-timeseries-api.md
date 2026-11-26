# TimeSeriesPredictor API (AutoGluon 1.6.3)

## Data format

Data must be a `TimeSeriesDataFrame` — a pandas DataFrame with a multi-index of `(item_id, timestamp)` plus a target column:

```python
from autogluon.timeseries import TimeSeriesPredictor, TimeSeriesDataFrame

ts = TimeSeriesDataFrame.from_data_frame(
    df, id_column="item_id", timestamp_column="timestamp"
)
```

## Core workflow

```python
predictor = TimeSeriesPredictor(
    target="target",
    prediction_length=48,        # forecast horizon in timesteps
    path="my-forecast-model",
    eval_metric="MASE",
).fit(ts, presets="medium_quality", time_limit=600)

forecasts = predictor.predict(ts)      # quantile columns (e.g. 0.1 / 0.5 / 0.9) per horizon step
predictor.leaderboard(test_data)       # score computed on the last prediction_length timesteps of each series
```

## Presets

From `predictor_presets.py`:

- `best_quality` — default hyperparameters, `num_val_windows="auto"`, `refit_every_n_windows="auto"`.
- `high_quality` — default hyperparameters.
- `medium_quality` — light model set.
- `fast_training` — experimental fast path with auto validation windows.
- Zero-shot presets (skip model selection): `chronos2` (`autogluon/chronos-2`), `chronos2_small`, and Chronos-Bolt tiers `bolt_tiny` / `bolt_mini` / `bolt_small` / `bolt_base`.

## Models

Toto-2 (new in 1.6, pretrained forecasting), Toto, Chronos-2, Chronos-Bolt, DeepAR, TFT, N-BEATS, and statistical models (ARIMA, ETS, Theta). See the model zoo docs for full list and hyperparameter keys.

## New in 1.6

- **Toto-2** pretrained forecasting model added.
- **New metrics**: `MAEB` and `WAPEB` (bias-penalized), `BIAS` (forecast bias check), `MQL` (mean quantile loss).
- **`TimeSeriesPredictor.export_model`** — export a trained model to a standalone checkpoint that loads without AutoGluon installed.
- **Experimental `update()`** — re-select the ensemble on fresh data without full refit.
- Prediction caching is disabled by default and deprecated (removed in a future release).

## Gotchas

- `prediction_length` must be set at construction; it defines both training context usage and forecast horizon.
- `leaderboard(test_data)` scores each model using the last `prediction_length` timesteps of each series in `test_data`.
- Known covariates (if used) must cover the full forecast horizon at prediction time.
