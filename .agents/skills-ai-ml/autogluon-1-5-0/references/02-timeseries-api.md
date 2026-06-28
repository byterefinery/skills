# TimeSeriesPredictor API Reference

## Constructor

```python
TimeSeriesPredictor(
    target: str = "target",
    prediction_length: int = 1,
    freq: str = None,
    eval_metric: str | TimeSeriesScorer = "WQL",
    eval_metric_seasonal_period: int = None,
    horizon_weight: list[float] = None,
    known_covariates_names: list[str] = None,
    quantile_levels: list[float] = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
    path: str = None,
    verbosity: int = 2,
    log_to_file: bool = True,
    cache_predictions: bool = True,
)
```

### Eval Metrics

**Probabilistic (quantile):** `SQL` (scaled quantile loss), `WQL` (weighted quantile loss).

**Point forecast:** `MAE`, `MAPE`, `MASE`, `MSE`, `RMSE`, `RMSLE`, `RMSSE`, `SMAPE`, `WAPE`.

## Data Format: TimeSeriesDataFrame

Time series data requires a multi-index DataFrame with `(item_id, timestamp)` index:

```python
from autogluon.timeseries import TimeSeriesDataFrame

# Convert from regular DataFrame
ts_data = TimeSeriesDataFrame.from_dataframe(
    df,
    id_column="item_id",
    timestamp_column="timestamp",
)

# Direct construction
ts_data = TimeSeriesDataFrame(
    df,
    freq="D",  # 'D'=daily, 'H'=hourly, 'W'=weekly, 'M'=monthly
)
```

The `target` column holds the values to forecast. Additional columns are treated as `past_covariates` (known only historically). Columns listed in `known_covariates_names` are treated as future-known covariates.

## fit()

```python
predictor.fit(
    train_data: TimeSeriesDataFrame,
    tuning_data: TimeSeriesDataFrame = None,
    time_limit: int = None,
    presets: str = None,
    hyperparameters: str | dict = None,
    hyperparameter_tune_kwargs: str | dict = None,
    excluded_model_types: list[str] = None,
    num_val_windows: int | tuple | "auto" = 1,
    val_step_size: int = None,
    refit_full: bool = False,
    enable_ensemble: bool = True,
    random_seed: int = 123,
)
```

### Presets

- `fast_training` — statistical + tree models only. Fast, lower accuracy.
- `medium_quality` — adds TFT + Chronos-2 small. Good accuracy/time trade-off.
- `high_quality` — full model mix (DL, ML, statistical). Best accuracy.
- `best_quality` — same as `high_quality` with multi-window backtesting.
- `chronos2` — Chronos-2 base model for zero-shot forecasting.
- `chronos2_small` — smaller Chronos-2, faster, lower memory.
- `chronos2_ensemble` — zero-shot + fine-tuned Chronos-2 ensemble.
- `bolt_{tiny|mini|small|base}` — Chronos-Bolt pretrained models for zero-shot.

### Model Zoo

**Deep Learning:** `TemporalFusionTransformer` (TFT), `DeepAR`, `NBEATS`, `NHITS`, `DLinear`, `PatchTST`, `AutoTimes`, `PyraForecast`, `TiDE`, `SFM`, `PRONET`, `SCINet`, `TimesNet`, `FEDformer`, `Autoformer`, `Informer`, `D2ST`, `iPatchTST`, `Chronos`, `Chronos2`, `ChronosBolt`.

**Statistical:** `ARIMA`, `AutoARIMA`, `ETS`, `Theta`, `Naive`, `SeasonalNaive`, `ADCore`, `Croston`, `AutoCroston`.

**Machine Learning:** `DLinear`, `THOR`, `MultiHorizonDocument`, `GPT4MTS`, `MOMENT`, `PatchTST`.

**Ensemble:** `SimpleEnsemble`, `BacktestEnsemble`, `WeightedEnsemble`, `MultiWindowMultiModelBacktestEnsemble`.

## Prediction

```python
forecasts = predictor.predict(
    data: TimeSeriesDataFrame,
    known_covariates: TimeSeriesDataFrame = None,
    model: str = None,
    use_cache: bool = True,
)
```

Returns a `TimeSeriesDataFrame` with `mean` and quantile columns (`0.10`, `0.20`, …, `0.90`).

### Known Covariates

When `known_covariates_names` was specified during construction, `predict()` requires future covariate values:

```python
# Generate template for future covariates
future_covariates_template = predictor.make_future_data_frame(
    data=past_data,
    known_covariates_template=future_covariates,
)

# Fill in actual future values and predict
forecasts = predictor.predict(data, known_covariates=future_covariates)
```

## Evaluation

```python
predictor.evaluate(data, metrics=None)
```

Returns dict of metric scores. Uses the last `prediction_length` steps of each series.

## Backtesting

```python
# Multi-window backtest predictions
backtest_preds = predictor.backtest_predictions(
    data=None,                          # None = use training data
    model=None,                         # specific model or list of models
    num_val_windows=3,
    val_step_size=None,
)

# Get corresponding actual targets
backtest_targets = predictor.backtest_targets(
    data=None,
    num_val_windows=3,
    val_step_size=None,
)
```

## Leaderboard

```python
predictor.leaderboard(data=None, extra_info=False)
```

Shows all trained models ranked by validation score.

## fit_summary()

```python
predictor.fit_summary(verbosity=1)
```

Returns dict with training times, model performances, and data statistics.

## Save / Load

```python
predictor.save()
loaded = TimeSeriesPredictor.load(path)
```

## Hyperparameter Tuning

```python
from autogluon.common import space

predictor.fit(
    train_data,
    hyperparameters={
        "DeepAR": {"hidden_size": space.Int(20, 100)},
        "TFT": {"hidden_dim": space.Int(16, 128)},
    },
    hyperparameter_tune_kwargs={
        "searcher": "auto",
        "scheduler": "auto",
        "num_trials": 10,
    },
    time_limit=600,
)
```

## Gotchas

- Time series shorter than `(num_val_windows + 1) * prediction_length` are silently ignored during training.
- `tuning_data` disables multi-window backtesting entirely. If you provide tuning data, `num_val_windows` is set to 0.
- GPU non-determinism means `random_seed` does not guarantee identical results for GPU models.
- `refit_full` is disabled when `tuning_data` is provided.
