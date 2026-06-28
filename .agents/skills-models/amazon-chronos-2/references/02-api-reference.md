# 02 — API Reference

## Chronos2Pipeline

### `from_pretrained(model_id, device_map, **kwargs)`

Load a pre-trained Chronos-2 model.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `model_id` | str | `"amazon/chronos-2"` | HuggingFace model ID or local path |
| `device_map` | str | `"cpu"` | `"cuda"`, `"cpu"`, or dict mapping layers to devices |
| `dtype` / `torch_dtype` | str | `"float32"` | `"bfloat16"` or `"float32"` |

```python
from chronos import Chronos2Pipeline

pipeline = Chronos2Pipeline.from_pretrained("amazon/chronos-2", device_map="cuda")
```

### `predict(inputs, prediction_length, **kwargs)`

Tensor-based prediction. Returns a list of tensors, one per input series.

| Parameter | Type | Description |
|---|---|---|
| `inputs` | Tensor, list[Tensor] | Series data. Variable-length lists are auto left-padded with NaN. |
| `prediction_length` | int | Number of steps to forecast |
| `limit_prediction_length` | bool | If True, error when prediction_length > 1024. Default: warn. |

**Return shape**: `List[torch.Tensor]` — each tensor is `(n_variates, n_quantiles, prediction_length)`.

```python
import torch

# Single univariate
forecast = pipeline.predict(torch.randn(512), prediction_length=24)
# forecast.shape == (1, 9, 24)

# Batch
forecasts = pipeline.predict(torch.randn(32, 512), prediction_length=24)
# forecasts[i].shape == (1, 9, 24) for each i

# Multivariate input
forecasts = pipeline.predict(torch.randn(4, 3, 512), prediction_length=24)
# forecasts[i].shape == (3, 9, 24) — 3 variates, 9 quantiles, 24 steps
```

### `predict_quantiles(inputs, prediction_length, quantile_levels, **kwargs)`

Quantile prediction with explicit quantile levels. Consistent interface across Chronos-2 and Chronos-Bolt.

| Parameter | Type | Description |
|---|---|---|
| `inputs` | Tensor, list[Tensor] | Series data |
| `prediction_length` | int | Forecast horizon |
| `quantile_levels` | list[float] | Quantiles to return (e.g., `[0.1, 0.5, 0.9]`) |

### `predict_df(context_df, **kwargs)`

DataFrame-based prediction. Handles grouping, batching, and timestamp generation.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `context_df` | DataFrame | — | Historical data with timestamps |
| `prediction_length` | int | — | Forecast horizon |
| `quantile_levels` | list[float] | `[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]` | Quantiles to return |
| `id_column` | str | `"item_id"` | Column identifying series |
| `timestamp_column` | str | `"timestamp"` | Column with datetime values |
| `target` | str or list[str] | `"target"` | Target column(s). List enables multivariate. |
| `future_df` | DataFrame | None | Future covariates (without target columns) |
| `cross_learning` | bool | False | Enable cross-series learning |
| `batch_size` | int | 256 | Batch size for prediction |
| `validate_inputs` | bool | True | Validate timestamp regularity |
| `limit_prediction_length` | bool | False | Error on horizon > 1024 |

**Returned DataFrame columns**: `item_id`, `timestamp`, `target_name`, `predictions`, plus one column per quantile level (string names).

```python
pred_df = pipeline.predict_df(
    context_df,
    prediction_length=24,
    quantile_levels=[0.1, 0.5, 0.9],
    id_column="item_id",
    timestamp_column="timestamp",
    target="target",
)

# Access quantiles
median = pred_df["0.5"]
lower = pred_df["0.1"]
upper = pred_df["0.9"]
```

### `embed(inputs, batch_size)`

Extract encoder embeddings for downstream use.

| Parameter | Type | Description |
|---|---|---|
| `inputs` | list[Tensor] | Series data |
| `batch_size` | int | Batch size for embedding extraction |

**Returns**: `(embeddings, idx_ranges)` — tensor embeddings and index ranges per series.

### `predict_fev(task, batch_size, finetune_kwargs)`

Benchmark prediction using `fev` tasks.

| Parameter | Type | Description |
|---|---|---|
| `task` | fev.Task | Task from `fev.get_task()` |
| `batch_size` | int | Batch size |
| `finetune_kwargs` | dict | Optional fine-tuning config for first window |

```python
import fev

task = fev.get_task("m4_hourly")
predictions, inference_time = pipeline.predict_fev(task, batch_size=256)
```

### `save_pretrained(save_directory)`

Save model to disk.

```python
pipeline.save_pretrained("./my-model")
```

## Data Preparation

### `from_data_frame(df, **kwargs)`

Preprocess DataFrame inputs for fine-tuning with covariates.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `df` | DataFrame | — | Historical data |
| `future_df` | DataFrame | None | Future covariates |
| `target_columns` | list[str] | — | Target column names |
| `prediction_length` | int | — | Forecast horizon |
| `id_column` | str | `"item_id"` | Series identifier column |
| `timestamp_column` | str | `"timestamp"` | Timestamp column |

Columns in `df` that also appear in `future_df` are treated as known-future covariates. Columns only in `df` are past-only covariates.

```python
from chronos.chronos2.preprocess import from_data_frame

prepared = from_data_frame(
    df=context_df,
    future_df=future_df,
    target_columns=["target"],
    prediction_length=24,
    id_column="item_id",
    timestamp_column="timestamp",
)
```

## BaseChronosPipeline

Generic loader that auto-detects the correct pipeline class:

```python
from chronos import BaseChronosPipeline

# Works for Chronos-2, Chronos-Bolt, and original Chronos
pipeline = BaseChronosPipeline.from_pretrained("amazon/chronos-2", device_map="cuda")
```
