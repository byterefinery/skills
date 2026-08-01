# Toto2Model API Reference

## Toto2Model

### `Toto2Model.from_pretrained(model_name: str) -> Toto2Model`

Load a pre-trained Toto 2.0 model from Hugging Face.

**Parameters:**
- `model_name` — Hugging Face model ID, e.g. `"Datadog/Toto-2.0-22m"`

**Returns:** `Toto2Model` instance on CPU. Call `.to(device)` and `.eval()` before inference.

```python
from toto2 import Toto2Model

model = Toto2Model.from_pretrained("Datadog/Toto-2.0-22m")
model = model.to("cuda").eval()
```

### `model.forecast(inputs: dict, horizon: int, **kwargs) -> torch.Tensor`

Generate quantile forecasts for the input time series.

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `inputs` | `dict` | — | Input dict with keys: `target`, `target_mask`, `series_ids` |
| `horizon` | `int` | — | Number of future timesteps to predict |
| `decode_block_size` | `int \| None` | `768` | `None` = single forward pass; int = block decode chunk size |
| `has_missing_values` | `bool` | `True` | `False` enables Flash Attention (only if no gaps in data) |

**Input dict keys:**

| Key | Shape | Dtype | Description |
|---|---|---|---|
| `target` | `(batch, n_variates, context_len)` | `float32` | Input time series values |
| `target_mask` | `(batch, n_variates, context_len)` | `bool` | `True` = observed, `False` = missing |
| `series_ids` | `(batch, n_variates)` | `long` | Integer ID per series (0 for single series) |

**Returns:** `torch.Tensor` of shape `(9, batch, n_variates, horizon)` with quantile levels `[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]`.

### Extracting predictions from quantiles

```python
quantiles = model.forecast(inputs, horizon=96)

# Shape: (9, batch, n_variates, horizon)
# Index 0 → 0.1 quantile, ..., 4 → 0.5 (median), ..., 8 → 0.9 quantile

median = quantiles[4]                    # (batch, n_variates, horizon)
p10 = quantiles[0]                       # lower bound
p90 = quantiles[8]                       # upper bound
p25 = quantiles[1]                       # 25th percentile
p75 = quantiles[7]                       # 75th percentile
```

## Toto2GluonTSModel

Wraps `Toto2Model` for compatibility with GluonTS evaluation pipelines.

### `Toto2GluonTSModel.from_pretrained(model_name: str) -> Toto2GluonTSModel`

```python
from toto2 import Toto2GluonTSModel

model = Toto2GluonTSModel.from_pretrained("Datadog/Toto-2.0-22m")

# Use with GluonTS evaluators
from gluonts.ev import Evaluator
evaluator = Evaluator(quantiles=[0.1, 0.5, 0.9])

# Evaluate on a test dataset
metrics, _ = evaluator(iter(test_data), iter(model.predict(test_data)))
```

See the [GluonTS integration notebook](https://github.com/DataDog/toto/tree/v2.0.0/toto2/notebooks/gluonts_integration.ipynb) for full examples with built-in GluonTS datasets.

## Available Models

| Model ID | Parameters | Recommended use |
|---|---|---|
| `Datadog/Toto-2.0-4m` | 4 million | Edge devices, constrained environments |
| `Datadog/Toto-2.0-22m` | 22 million | Default — balanced speed and accuracy |
| `Datadog/Toto-2.0-313m` | 313 million | Higher accuracy, moderate GPU |
| `Datadog/Toto-2.0-1B` | 1 billion | High-accuracy forecasting |
| `Datadog/Toto-2.0-2.5B` | 2.5 billion | Maximum accuracy, large GPU cluster |

## Architecture

Toto 2.0 uses a **decoder-only transformer** with:
- **Alternating time/variate attention** — separate attention layers for temporal and cross-variate dependencies
- **u-μP scaling** — unit scaling that works correctly with `torch.compile` and FSDP2
- **Quantile head** — directly outputs 9 quantile levels instead of sampling-based approaches
- **Positional encoding** — supports variable context lengths and prediction horizons
