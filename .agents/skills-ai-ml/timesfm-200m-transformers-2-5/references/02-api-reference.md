# API Reference

## TimesFm2_5ModelForPrediction

### Construction

```python
from transformers import TimesFm2_5ModelForPrediction

model = TimesFm2_5ModelForPrediction.from_pretrained(
    "google/timesfm-2.5-200m-transformers",
)
```

### `from_pretrained()` Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `pretrained_model_name_or_path` | `str` | required | Model ID on HuggingFace Hub or local path |
| `torch_dtype` | `torch.dtype` | `None` | Model weight dtype (use `torch.float32`) |
| `device_map` | `str` | `None` | Device placement (`"cuda"`, `"cpu"`, or auto) |
| `cache_dir` | `str` | `None` | Custom cache directory for downloaded weights |

### Forward Call

```python
outputs = model(
    past_values=past_values,
    forecast_context_len=1024,
    forecast_horizon=12,
)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `past_values` | `List[torch.Tensor]` | Yes | — | List of 1-D tensors, one per series. Variable lengths supported. |
| `forecast_context_len` | `int` | No | 512 | Context window length. Series shorter than this are left-padded; longer are truncated from the start. Max: 1024. |
| `forecast_horizon` | `int` | No | 128 | Number of steps to predict. Max: 512. |

#### Return Value

A `TimesFm2_5ModelOutput` (or similar namedtuple) with:

| Attribute | Shape | Description |
|---|---|---|
| `mean_predictions` | `(batch, horizon)` | Point forecasts (mean) |
| `full_predictions` | `(batch, horizon, 11)` | Mean + 10 quantile levels (10th–90th) |

### Device Placement

```python
# GPU
model = TimesFm2_5ModelForPrediction.from_pretrained(
    "google/timesfm-2.5-200m-transformers",
).to("cuda")
model = model.to(torch.float32).eval()

# CPU
model = TimesFm2_5ModelForPrediction.from_pretrained(
    "google/timesfm-2.5-200m-transformers",
).to("cpu")
model = model.to(torch.float32).eval()
```

Always set `.eval()` for inference to disable dropout and batch norm updates.

### Saving

```python
model.save_pretrained("./my-timesfm-model")
```

### Loading from Local Path

```python
model = TimesFm2_5ModelForPrediction.from_pretrained("./my-timesfm-model")
```

## TimesFm2_5Tokenizer

The model has an associated tokenizer accessible via `AutoTokenizer`:

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("google/timesfm-2.5-200m-transformers")
```

The tokenizer handles the patch-based encoding of raw time series into model inputs. In most cases, you pass `past_values` directly to the model and the tokenizer is used internally.

## Quantile Interpretation

The `full_predictions` output has shape `(batch, horizon, 11)`:

- Column 0: mean prediction
- Column 1: 10th percentile
- Column 2: 20th percentile
- Column 3: 30th percentile
- Column 4: 40th percentile
- Column 5: 50th percentile (median)
- Column 6: 60th percentile
- Column 7: 70th percentile
- Column 8: 80th percentile
- Column 9: 90th percentile

To extract a prediction interval (e.g., 80% CI):

```python
lower = outputs.full_predictions[:, :, 1]   # 10th percentile
upper = outputs.full_predictions[:, :, 9]   # 90th percentile
median = outputs.full_predictions[:, :, 5]  # 50th percentile
```
