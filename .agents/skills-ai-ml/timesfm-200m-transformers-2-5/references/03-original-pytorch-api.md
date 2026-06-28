# Original PyTorch API Comparison

The original TimesFM PyTorch checkpoint (`google/timesfm-2.5-200m-pytorch`) uses the `timesfm` package with a different API surface. This reference documents the differences for migration.

## Installation

```bash
# Transformers port (this skill)
pip install torch transformers

# Original PyTorch checkpoint
git clone https://github.com/google-research/timesfm.git
cd timesfm
pip install -e .
```

## API Differences

### Loading

```python
# Transformers port
from transformers import TimesFm2_5ModelForPrediction
model = TimesFm2_5ModelForPrediction.from_pretrained(
    "google/timesfm-2.5-200m-transformers",
)
model = model.to(torch.float32).eval()

# Original PyTorch
import timesfm
model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
    "google/timesfm-2.5-200m-pytorch",
    torch_compile=True,
)
```

### Forecasting

```python
# Transformers port — pass list of tensors directly
import torch
past_values = [torch.randn(100), torch.sin(torch.linspace(0, 20, 67))]
outputs = model(past_values=past_values, forecast_context_len=1024, forecast_horizon=12)
mean_pred = outputs.mean_predictions
quantile_pred = outputs.full_predictions

# Original PyTorch — requires compile step with ForecastConfig
import numpy as np
model.compile(
    timesfm.ForecastConfig(
        max_context=1024,
        max_horizon=256,
        normalize_inputs=True,
        use_continuous_quantile_head=True,
        force_flip_invariance=True,
        infer_is_positive=True,
        fix_quantile_crossing=True,
    )
)
point_forecast, quantile_forecast = model.forecast(
    horizon=12,
    inputs=[np.linspace(0, 1, 100), np.sin(np.linspace(0, 20, 67))],
)
```

### Feature Comparison

| Feature | Transformers Port | Original PyTorch |
|---|---|---|
| `torch.compile` optimization | ❌ | ✅ via `model.compile()` |
| Auto-normalization | ❌ (manual) | ✅ via `normalize_inputs=True` |
| Flip invariance | ❌ | ✅ via `force_flip_invariance=True` |
| Positive inference | ❌ | ✅ via `infer_is_positive=True` |
| Quantile crossing fix | ❌ | ✅ via `fix_quantile_crossing=True` |
| HuggingFace ecosystem | ✅ | ❌ |
| Separate package install | ❌ (just transformers) | ✅ (git clone + pip install) |

### When to Use the Original PyTorch Version

Use `google/timesfm-2.5-200m-pytorch` with the `timesfm` package when you need:

1. **`torch.compile`** — the original supports JIT compilation for faster inference
2. **Auto-normalization** — `normalize_inputs=True` handles scaling automatically
3. **Flip invariance** — `force_flip_invariance=True` improves robustness to reversed series
4. **Positive inference** — `infer_is_positive=True` constrains predictions to positive values
5. **Quantile crossing fix** — `fix_quantile_crossing=True` ensures monotonic quantiles

### Normalization (Manual, for Transformers Port)

Since the transformers port does not auto-normalize, apply standardization manually:

```python
import torch

def normalize_series(series: torch.Tensor) -> tuple:
    """Z-score normalize a series."""
    mean = series.mean()
    std = series.std()
    if std < 1e-8:
        std = 1.0
    return (series - mean) / std, mean, std

def denormalize(pred: torch.Tensor, mean: torch.Tensor, std: torch.Tensor) -> torch.Tensor:
    """Reverse z-score normalization."""
    return pred * std + mean

# Usage
series = torch.tensor([...], dtype=torch.float32)
normalized, mean, std = normalize_series(series)

with torch.no_grad():
    outputs = model(past_values=[normalized], forecast_context_len=1024, forecast_horizon=12)

# Denormalize predictions
mean_forecast = denormalize(outputs.mean_predictions[0], mean, std)
```
