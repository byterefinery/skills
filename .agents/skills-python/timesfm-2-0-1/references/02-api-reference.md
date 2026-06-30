# TimesFM 2.0.1 API Reference

## Model Classes

### `timesfm.TimesFM_2p5_200M_torch`

PyTorch implementation of TimesFM 2.5 (200M parameters). Inherits from `PyTorchModelHubMixin` for HuggingFace integration.

#### `from_pretrained()`

```python
model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
    "google/timesfm-2.5-200m-pytorch",
    cache_dir=None,
    revision=None,
    force_download=False,
    local_files_only=False,
    token=None,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model_id` | str | `"google/timesfm-2.5-200m-pytorch"` | HuggingFace repo ID or local directory path |
| `revision` | str \| None | None | Specific model revision/tag |
| `cache_dir` | str \| Path \| None | None | Custom cache directory (default: `~/.cache/huggingface/`) |
| `force_download` | bool | False | Re-download even if cached |
| `local_files_only` | bool | False | Use only cached files, no network |
| `token` | str \| bool \| None | None | HuggingFace auth token for private repos |

**Returns**: Initialized model instance (not yet compiled).

**Notes**:
- Weights are downloaded from HuggingFace on first call
- Model is moved to CUDA if available, otherwise CPU
- `torch.compile` is applied by default (set `torch_compile=False` to disable)

#### `compile()`

```python
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
```

Compiles the model with the given forecast configuration. Must be called before `forecast()`.

**Raises**:
- `ValueError` if `max_context + max_horizon > context_limit` (16,384)
- `ValueError` if `use_continuous_quantile_head` and `max_horizon > 1,024`

#### `forecast()`

```python
point_forecast, quantile_forecast = model.forecast(
    horizon=24,
    inputs=[np.array([...]), np.array([...])],
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `horizon` | int | Number of future steps to forecast (must be ≤ `max_horizon`) |
| `inputs` | list[np.ndarray] | List of 1-D numpy arrays, each a time series |

**Returns**: `tuple[np.ndarray, np.ndarray]`

| Output | Shape | Description |
|--------|-------|-------------|
| `point_forecast` | `(B, H)` | Median (q50) forecast for B series, H steps |
| `quantile_forecast` | `(B, H, 10)` | Full quantile distribution |

**Quantile channels** (index → quantile):

| Index | Value | Description |
|-------|-------|-------------|
| 0 | mean | Average prediction |
| 1 | 0.1 | 10th percentile |
| 2 | 0.2 | 20th percentile |
| 3 | 0.3 | 30th percentile |
| 4 | 0.4 | 40th percentile |
| 5 | 0.5 | 50th percentile (= `point_forecast`) |
| 6 | 0.6 | 60th percentile |
| 7 | 0.7 | 70th percentile |
| 8 | 0.8 | 80th percentile |
| 9 | 0.9 | 90th percentile |

**Raises**: `RuntimeError` if model is not compiled.

**Automatic preprocessing**:
- Leading NaN values are stripped
- Internal NaN values are linearly interpolated
- Series longer than `max_context` are truncated to last `max_context` points
- Series shorter than `max_context` are zero-padded at the front

#### `forecast_with_covariates()`

```python
point, quantiles = model.forecast_with_covariates(
    inputs=[series1, series2],
    dynamic_numerical_covariates={"price": [price1, price2]},
    dynamic_categorical_covariates={"dow": [dow1, dow2]},
    static_numerical_covariates={"capacity": [100.0, 200.0]},
    static_categorical_covariates={"region": ["east", "west"]},
    xreg_mode="xreg + timesfm",
    normalize_xreg_target_per_input=True,
    ridge=0.0,
    max_rows_per_col=0,
    force_on_cpu=False,
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `inputs` | list[Sequence[float]] | Target time series |
| `dynamic_numerical_covariates` | dict[str, list[Sequence[float]]] | Time-varying numeric features (context + horizon) |
| `dynamic_categorical_covariates` | dict[str, list[Sequence[Category]]] | Time-varying categorical features (context + horizon) |
| `static_numerical_covariates` | dict[str, Sequence[float]] | Fixed numeric features (one per series) |
| `static_categorical_covariates` | dict[str, Sequence[Category]] | Fixed categorical features (one per series) |
| `xreg_mode` | str | `"xreg + timesfm"` or `"timesfm + xreg"` |
| `normalize_xreg_target_per_input` | bool | Normalize XReg target per series |
| `ridge` | float | Ridge penalty for linear model (0 = OLS) |
| `max_rows_per_col` | int | Subsample rows for speed (0 = no subsampling) |
| `force_on_cpu` | bool | Force CPU for linear model fitting |

**Requires**: `timesfm[xreg]` extras (JAX + scikit-learn) and `return_backcast=True` in `ForecastConfig`.

#### `load_checkpoint()`

```python
model.load_checkpoint("/path/to/model.safetensors")
```

Load weights from a local safetensors file or directory.

#### `save_pretrained()`

```python
model.save_pretrained("./my-timesfm-model")
```

Save model weights to a directory (safetensors format).

---

### `timesfm.TimesFM_2p5_200M_flax`

JAX/Flax implementation of TimesFM 2.5. Same API as the PyTorch version but optimized for TPU/GPU via JAX.

---

## `timesfm.ForecastConfig`

Immutable dataclass controlling all forecast behavior.

```python
@dataclasses.dataclass(frozen=True)
class ForecastConfig:
    max_context: int = 0
    max_horizon: int = 0
    normalize_inputs: bool = False
    window_size: int = 0
    per_core_batch_size: int = 1
    use_continuous_quantile_head: bool = False
    force_flip_invariance: bool = True
    infer_is_positive: bool = True
    fix_quantile_crossing: bool = False
    return_backcast: bool = False
```

### Parameter Details

#### `max_context` (int, default=0)

Maximum number of historical time points as context.

- **0**: Use model maximum (16,384 for v2.5)
- **N**: Truncate to last N points; rounded up to nearest multiple of 32
- **Constraint**: `max_context + max_horizon ≤ 16,384`

#### `max_horizon` (int, default=0)

Maximum forecast horizon.

- **0**: Use model maximum
- **N**: Forecasts up to N steps; rounded up to nearest multiple of 128
- **Constraint**: `max_context + max_horizon ≤ 16,384`
- **With continuous quantile head**: `max_horizon ≤ 1,024`

#### `normalize_inputs` (bool, default=False)

Z-normalize each series: `(x - mean) / std`.

- **True**: Recommended for most use cases; prevents numerical issues with extreme scales
- **False**: Only if series are already normalized or near unit scale

#### `per_core_batch_size` (int, default=1)

Number of series per device per batch.

- Global batch size = `per_core_batch_size × num_devices`
- Increase for throughput, decrease for memory

#### `use_continuous_quantile_head` (bool, default=False)

Use the 30M-parameter continuous quantile head.

- **True**: Better interval calibration, especially for horizons > 128
- **False**: Fixed quantile buckets (faster, less accurate intervals)

#### `force_flip_invariance` (bool, default=True)

Ensures `f(-x) = -f(x)` by averaging forward passes on `x` and `-x`.

- **True**: Mathematical consistency; doubles compute but ensures no sign bias
- **False**: Slightly faster but may produce asymmetric forecasts

#### `infer_is_positive` (bool, default=True)

Detect if all inputs are non-negative and clamp forecasts ≥ 0.

- **True**: Safe for demand, sales, counts, prices
- **False**: Required for temperature, returns, anomalies

#### `fix_quantile_crossing` (bool, default=False)

Post-process to enforce `q10 ≤ q20 ≤ ... ≤ q90`.

- **True**: Guarantees well-ordered quantiles
- **False**: Slightly faster but quantiles may cross

#### `return_backcast` (bool, default=False)

Include the model's reconstruction of the input series.

- **True**: Required for XReg covariate workflows; adds backcast to output
- **False**: Only return forecast

---

## Internal Config Classes

### `ResidualBlockConfig`

```python
@dataclasses.dataclass(frozen=True)
class ResidualBlockConfig:
    input_dims: int
    hidden_dims: int
    output_dims: int
    use_bias: bool
    activation: Literal["relu", "swish", "none"]
```

### `TransformerConfig`

```python
@dataclasses.dataclass(frozen=True)
class TransformerConfig:
    model_dims: int
    hidden_dims: int
    num_heads: int
    attention_norm: Literal["rms"]
    feedforward_norm: Literal["rms"]
    qk_norm: Literal["rms", "none"]
    use_bias: bool
    use_rotary_position_embeddings: bool
    ff_activation: Literal["relu", "swish", "none"]
    fuse_qkv: bool
```

### `StackedTransformersConfig`

```python
@dataclasses.dataclass(frozen=True)
class StackedTransformersConfig:
    num_layers: int
    transformer: TransformerConfig
```

---

## Helper Functions

### `strip_leading_nans(arr)`

Removes contiguous NaN values from the beginning of a NumPy array.

### `linear_interpolation(arr)`

Fills NaN values in a 1D array using linear interpolation. Falls back to mean imputation if all values are NaN.

---

## Error Reference

| Error | Cause | Fix |
|-------|-------|-----|
| `RuntimeError: Model is not compiled` | Called `forecast()` before `compile()` | Call `model.compile(ForecastConfig(...))` first |
| `ValueError: Context + horizon > context_limit` | `max_context + max_horizon > 16,384` | Reduce one or both values |
| `ValueError: Continuous quantile head horizon > 1024` | `use_continuous_quantile_head=True` with large horizon | Disable quantile head or reduce horizon |
| `torch.cuda.OutOfMemoryError` | Batch too large for GPU | Reduce `per_core_batch_size` |
| `HfHubHTTPError` | Download failed | Check internet, set `HF_HOME` to writable directory |
| `ImportError: XReg module` | Missing `timesfm[xreg]` | Install with `pip install timesfm[xreg]` |
