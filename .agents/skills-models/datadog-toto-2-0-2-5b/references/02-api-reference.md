# API Reference

## Toto2Model

### Construction

```python
from toto2 import Toto2Model

model = Toto2Model.from_pretrained("Datadog/Toto-2.0-2.5B")
model = model.to(device).eval()
```

`from_pretrained()` accepts HuggingFace model IDs or local directory paths. Supports `map_location` for device placement.

### `model.forecast(inputs, horizon, **kwargs)`

Generate quantile forecasts.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `inputs` | `dict` | Yes | Input dict (see `Toto2ForecastInputs`) |
| `horizon` | `int` | Yes | Number of steps to forecast |
| `decode_block_size` | `int \| None` | No | Block decoding size (default: 0 = single pass). Must be divisible by patch_size (32). `None` for single pass; e.g., 768 for block decode |
| `has_missing_values` | `bool` | No | If `False`, enables Flash Attention (default: `True`). Only set `False` when `target_mask` is all `True` |
| `scaler_fallback_min_obs` | `int` | No | Backfill min observations for short patches (default: 0 = disabled). Set to e.g. 8 for sparse data |
| `quantile_real_cap_k` | `float` | No | Cap quantile range (default: 0.0 = disabled). Clips to `[ctx_min - K*scale, ctx_max + K*scale]` |

**Returns:** `torch.Tensor` of shape `(9, *batch, n_var, horizon)` containing quantiles at levels [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9].

**Input dict (`Toto2ForecastInputs`):**

| Key | Type | Required | Shape | Description |
|---|---|---|---|---|
| `target` | `Float[Tensor]` | Yes | `*batch n_var ctx` | Time series values |
| `target_mask` | `Bool[Tensor]` | Yes | `*batch n_var ctx` | `True` where observed, `False` where missing |
| `series_ids` | `Long[Tensor]` | Yes | `*batch n_var` | Series IDs for cross-series attention. Same ID = shared attention |
| `known_dynamic` | `Float[Tensor]` | No | `*batch n_exog ctx+horizon` | Known-future covariates (present in code path but not supported in 2.0) |
| `known_dynamic_mask` | `Bool[Tensor]` | No | `*batch n_exog ctx+horizon` | Mask for known_dynamic |
| `known_dynamic_series_ids` | `Long[Tensor]` | No | `*batch n_exog` | Series IDs for known_dynamic |

**Output:** `Toto2ModelOutputs(quantiles, loc, scale)` NamedTuple where:
- `quantiles`: `(9, *batch, n_var, horizon)` — real-space quantile predictions
- `loc`: `(*batch, n_var, seq, 1)` — causal scaler location (mean)
- `scale`: `(*batch, n_var, seq, 1)` — causal scaler scale (std)

### `model.forward(target, target_mask, cpm_mask, series_ids, num_return_steps=None)`

Raw forward pass (used internally by `forecast()`). Returns `Toto2ModelOutputs`.

### Properties

| Property | Type | Description |
|---|---|---|
| `model.config` | `Toto2ModelConfig` | Model configuration dataclass |
| `model.num_time_layers` | `int` | Number of time-axis attention layers |
| `model.output_head.knots` | `list[float]` | Quantile levels: `[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]` |
| `model.config.patch_size` | `int` | Patch size (32 for all Toto 2.0 models) |

## Toto2GluonTSModel

Wraps `Toto2Model` for GluonTS integration.

### Construction

```python
from toto2 import Toto2Model, Toto2GluonTSModel, Toto2GluonTSModelConfig

model = Toto2Model.from_pretrained("Datadog/Toto-2.0-2.5B")

gts_config = Toto2GluonTSModelConfig(
    prediction_length=96,
    context_length=512,
    target_dim=1,
)

gts_model = Toto2GluonTSModel(model, gts_config)
```

### `Toto2GluonTSModelConfig`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `prediction_length` | `int` | required | Forecast horizon |
| `context_length` | `int` | required | Context window length |
| `target_dim` | `int` | required | 1 for univariate, 2 for multivariate |
| `past_feat_dynamic_real_dim` | `int` | 0 | Past covariate dimensions |
| `feat_dynamic_real_dim` | `int` | 0 | Future covariate dimensions |
| `decode_block_size` | `int \| None` | `None` | Block decoding size |
| `has_missing_values` | `bool` | `True` | Whether data has missing values |
| `quantiles` | `list[float]` | `[0.1..0.9]` | Quantile levels |
| `imputation_internal` | `str` | `"ffill"` | Internal imputation: `"none"`, `"ffill"`, `"linear"` |
| `scaler_fallback_min_obs` | `int` | 8 | Min observations for scaler backfill |
| `quantile_real_cap_k` | `float` | 1e4 | Quantile cap factor |

### `gts_model.create_predictor(batch_size, device)`

Create a GluonTS `PyTorchPredictor`.

**Parameters:**
- `batch_size` — inference batch size
- `device` — torch device

**Returns:** `PyTorchPredictor` instance compatible with GluonTS evaluation pipelines.

### `gts_model.input_transform`

Returns the GluonTS `Transformation` pipeline for preprocessing inputs. Handles:
- `AsNumpyArray` conversion
- `ExpandDimArray` for univariate inputs
- `AddObservedValuesIndicator` for mask generation
- Imputation via configured method

### `gts_model.forecast_generator()`

Returns a `QuantileForecastGenerator` for converting model outputs to GluonTS forecasts.

## Toto2ModelConfig

Full model configuration dataclass. All values are fixed per checkpoint:

| Field | Type | 2.5B Value | Description |
|---|---|---|---|
| `patch_size` | `int` | 32 | Input patch size |
| `d_model` | `int` | 2048 | Model dimension |
| `d_ff` | `int` | 5464 | FFN hidden dimension |
| `num_heads` | `int` | 32 | Number of attention heads |
| `num_layers` | `int` | 48 | Number of transformer layers |
| `layer_group_size` | `int` | 48 | Layers per alternation group |
| `num_variate_layers_per_group` | `int` | 1 | Variate layers per group |
| `variate_layer_first` | `bool` | False | Start with variate layer |
| `num_output_patches` | `int` | 1 | Output patches per step |
| `pre_norm` | `bool` | True | Pre-norm architecture |
| `norm_eps` | `float` | 0.0005 | Layer norm epsilon |
| `attn_bias` | `bool` | True | Attention bias |
| `mlp_bias` | `bool` | False | MLP bias |
| `dropout_p` | `float` | 0.0 | Dropout (always 0) |
| `qk_norm` | `bool` | False | QK normalization |
| `use_xpos` | `bool` | True | Use x-pos encoding |
| `residual_mult` | `float` | 0.75 | Residual scaling |
| `residual_attn_ratio` | `float` | 5.1362 | Attention/MLP variance ratio |
| `per_dim_scale` | `bool` | True | Per-dimension scaling |
| `qk_dim` | `int` | 64 | QK projection dimension |
| `v_dim` | `int` | 64 | V projection dimension |
| `num_groups` | `int` | 32 | Attention groups |

## Imputation Utilities

Two imputation functions are available for handling NaN values:

```python
from toto2.model import ffill_imputation, linear_imputation

# Forward-fill (default in GluonTS integration)
imputed = ffill_imputation(values)

# Linear interpolation
imputed = linear_imputation(values)
```

Both accept 1D `(time,)` or 2D `(variate, time)` numpy arrays. Leading NaNs are left as 0 (masked by the model).
