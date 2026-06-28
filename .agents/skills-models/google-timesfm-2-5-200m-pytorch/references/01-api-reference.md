# TimesFM 2.5 API Reference

## Model Class: `timesfm.TimesFM_2p5_200M_torch`

### `from_pretrained()`

Load the model from Hugging Face Hub.

```python
model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
    "google/timesfm-2.5-200m-pytorch",
    cache_dir=None,         # Optional: custom cache directory
    force_download=True,    # Re-download even if cached
)
```

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `model_id` | str | `"google/timesfm-2.5-200m-pytorch"` | Hugging Face model ID |
| `revision` | str \| None | None | Specific model revision |
| `cache_dir` | str \| Path \| None | None | Custom cache directory |
| `force_download` | bool | True | Force re-download of weights |

**Returns**: Initialized model instance (not yet compiled).

### `compile()`

Compile the model with a forecast configuration. **Must be called before `forecast()`.**

```python
model.compile(timesfm.ForecastConfig(
    max_context=1024,
    max_horizon=256,
    normalize_inputs=True,
    per_core_batch_size=32,
    use_continuous_quantile_head=True,
    force_flip_invariance=True,
    infer_is_positive=True,
    fix_quantile_crossing=True,
))
```

### `forecast()`

Run zero-shot inference on one or more time series.

```python
point_forecast, quantile_forecast = model.forecast(
    horizon=24,
    inputs=[array1, array2, ...],
)
```

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `horizon` | int | Number of future steps to forecast |
| `inputs` | list[np.ndarray] | List of 1-D numpy arrays (one per series) |

**Returns**: `tuple[np.ndarray, np.ndarray]`

- `point_forecast`: shape `(batch_size, horizon)` — median (0.5 quantile)
- `quantile_forecast`: shape `(batch_size, horizon, 10)` — `[mean, q10, q20, q30, q40, q50, q60, q70, q80, q90]`

**Behavior**:
- Leading NaN values are stripped automatically
- Internal NaN values are linearly interpolated
- Series longer than `max_context` are truncated (last `max_context` points used)
- Series shorter than `max_context` are padded
- Variable-length series in the same batch are supported

**Raises**: `RuntimeError` if model is not compiled.

### `forecast_with_covariates()`

Run inference with exogenous variables. Requires `pip install timesfm[xreg]`.

```python
point, quantiles = model.forecast_with_covariates(
    inputs=inputs,
    dynamic_numerical_covariates={"price": [price_arr1, price_arr2]},
    dynamic_categorical_covariates={"holiday": [hol_arr1, hol_arr2]},
    static_categorical_covariates={"region": ["east", "west"]},
    xreg_mode="xreg + timesfm",
)
```

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| `inputs` | list[np.ndarray] | Target time series |
| `dynamic_numerical_covariates` | dict[str, list[np.ndarray]] | Time-varying numeric features |
| `dynamic_categorical_covariates` | dict[str, list[np.ndarray]] | Time-varying categorical features |
| `static_categorical_covariates` | dict[str, list[str]] | Per-series static features |
| `xreg_mode` | str | `"xreg + timesfm"` (default) or `"timesfm + xreg"` |

**Important**: Dynamic covariates must span both the context window and the forecast horizon. Their length must be `len(context) + horizon`.

## `ForecastConfig` Parameters

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `max_context` | int | 0 | Maximum context window. 0 = auto. Supports up to 16,384. |
| `max_horizon` | int | 0 | Maximum forecast horizon. 0 = auto. |
| `normalize_inputs` | bool | False | **Set True** — normalizes inputs to prevent scale instability |
| `per_core_batch_size` | int | 32 | Batch size per core. Tune for memory vs speed. |
| `use_continuous_quantile_head` | bool | False | **Set True** — better quantile accuracy for long horizons |
| `force_flip_invariance` | bool | False | Ensures f(-x) = -f(x). Improves symmetry. |
| `infer_is_positive` | bool | True | Clamp forecasts ≥ 0 when all inputs > 0. Set False for negative data. |
| `fix_quantile_crossing` | bool | False | **Set True** — ensures q10 ≤ q20 ≤ ... ≤ q90 |
| `return_backcast` | bool | False | Return backcast alongside forecast (for covariate workflows) |

## Quantile Output Details

The quantile forecast tensor has shape `(batch, horizon, 10)`. The last dimension maps to:

| Index | Quantile Level | Common Use |
| ----- | -------------- | ---------- |
| 0 | Mean | Average prediction |
| 1 | 0.10 (q10) | Lower bound of 80% prediction interval |
| 2 | 0.20 (q20) | Lower bound of 60% PI |
| 3 | 0.30 (q30) | — |
| 4 | 0.40 (q40) | Lower bound of 20% PI |
| 5 | 0.50 (q50) | Median (equals `point_forecast`) |
| 6 | 0.60 (q60) | Upper bound of 20% PI |
| 7 | 0.70 (q70) | — |
| 8 | 0.80 (q80) | Upper bound of 60% PI |
| 9 | 0.90 (q90) | Upper bound of 80% PI |

```python
point, q = model.forecast(horizon=H, inputs=data)

# 80% prediction interval
lower_80 = q[:, :, 1]  # q10
upper_80 = q[:, :, 9]  # q90

# 60% prediction interval
lower_60 = q[:, :, 2]  # q20
upper_60 = q[:, :, 8]  # q80

# 90% prediction interval (approximate — q05/q95 not available)
```

## Model Versions

| Version | Params | Max Context | Checkpoint |
| ------- | ------ | ----------- | ---------- |
| **2.5** | 200M | 16,384 | `google/timesfm-2.5-200m-pytorch` |
| 2.0 | 500M | 2,048 | `google/timesfm-2.0-500m-pytorch` |
| 1.0 | 200M | 2,048 | `google/timesfm-1.0-200m-pytorch` |

TimesFM 1.0/2.0 require `freq=[0]` for monthly data. TimesFM 2.5 removed the frequency parameter entirely.
