# API Reference

## BaseChronosPipeline

Base class for all Chronos pipelines. Provides shared loading and DataFrame interfaces.

### `from_pretrained(model_name_or_path, **kwargs)`

Load a model from HuggingFace Hub, local path, or S3 (`s3://` requires `boto3`). Default model: `amazon/chronos-2`.

- `amazon/chronos-2` — **(default)** flagship Chronos-2 (120M, Apache-2.0)
- `amazon/chronos-bolt-small` — fast Bolt variant (48M, latency-sensitive only)
- `amazon/chronos-t5-small` — original Chronos (46M, legacy)

For SageMaker JumpStart deployment, the model ID is `pytorch-forecasting-chronos-2` (not `amazon/chronos-2`).

**Parameters:**
- `pretrained_model_name_or_path` — HF model ID, local path, or S3 URI
- `device_map` — `"cuda"`, `"cpu"`, or dict for layer placement
- `torch_dtype` / `dtype` — `"bfloat16"`, `"float32"`, or `"auto"` (string resolved automatically)
- Additional kwargs forwarded to `AutoConfig` and `AutoModel`

Auto-detects the correct pipeline class from the model config (`chronos_pipeline_class` field). Falls back to `ChronosPipeline` for legacy configs.

### `predict(inputs, prediction_length=None)`

Generate forecasts. Returns type depends on `ForecastType`:
- `QUANTILES` (Chronos-2, Chronos-Bolt): list of `(n_variates, n_quantiles, prediction_length)` tensors
- `SAMPLES` (original Chronos): list of `(n_samples, prediction_length)` tensors

**Input formats:**
- 1D tensor `(history_length,)`
- 2D tensor `(batch, history_length)` — left-pad with `torch.nan`
- List of 1D/2D tensors (auto left-padded)

### `predict_quantiles(inputs, prediction_length=None, quantile_levels=[0.1..0.9])`

Return `(quantiles, mean)` tuple. Quantiles shape: `(batch, prediction_length, num_quantiles)`. Mean shape: `(batch, prediction_length)`. Interpolates if requested quantiles differ from training quantiles.

### `predict_df(df, ...)`

DataFrame API. Parameters vary by pipeline subclass. See individual pipeline docs below.

### `predict_fev(task, batch_size=32, **kwargs)`

Run on an `fev.Task` benchmark. Returns `(predictions_per_window, inference_time_s)`. Base implementation splits multivariate targets and drops covariates (univariate-only).

---

## Chronos2Pipeline

### `predict(inputs, prediction_length=None, batch_size=256, context_length=None, cross_learning=False, limit_prediction_length=False)`

**Additional parameters:**
- `batch_size` — number of time series per forward pass (including variates and covariates)
- `context_length` — max context length (default: model's 8192)
- `cross_learning` — share information across all inputs in batch
- `limit_prediction_length` — error if prediction_length exceeds model default

**Input formats (extended):**
- 3D tensor `(batch, n_variates, history_length)` — multivariate
- List of dicts with `target`, `past_covariates`, `future_covariates` keys:
  ```python
  [{
      "target": np.array([...]),
      "past_covariates": {"temp": np.array([...]), "day": np.array(["Mon", ...])},
      "future_covariates": {"temp": np.array([...]), "day": np.array(["Tue", ...])},
  }]
  ```

### `predict_df(df, future_df=None, target="target", prediction_length=None, quantile_levels=[0.1..0.9], batch_size=256, context_length=None, cross_learning=False, validate_inputs=True, freq=None)`

**Parameters:**
- `df` — long-format DataFrame with id, timestamp, target(s), and optional covariates
- `future_df` — future covariates DataFrame (same id/timestamp schema, no target columns)
- `target` — column name or list of names for multivariate forecasting
- `future_df` columns become known-future covariates; columns only in `df` become past-only covariates
- `freq` — pandas frequency string (e.g., `"h"`, `"D"`) to skip frequency inference

### `fit(inputs, prediction_length, validation_inputs=None, finetune_mode="full", lora_config=None, context_length=None, learning_rate=1e-6, num_steps=1000, batch_size=256, output_dir=None, min_past=None, finetuned_ckpt_name="finetuned-ckpt", callbacks=None, remove_printer_callback=False, disable_data_parallel=True, **extra_trainer_kwargs)`

Fine-tune and return a new `Chronos2Pipeline`.

**Parameters:**
- `inputs` — same formats as `predict()`, or `list[PreparedInput]` from `from_data_frame()`
- `finetune_mode` — `"full"` or `"lora"`
- `lora_config` — `LoraConfig` or dict. Default: rank 8, alpha 16, targets self-attention q/v/k/o + output layer
- `learning_rate` — 1e-6 for full, 1e-5 recommended for LoRA
- `num_steps` — training steps
- `batch_size` — number of time series per batch
- `output_dir` — checkpoint directory (default: `chronos-2-finetuned/{timestamp}`)
- `min_past` — minimum context length (series shorter than `min_past + prediction_length` are filtered)
- `disable_data_parallel` — force single-GPU training (default: True)
- `extra_trainer_kwargs` — forwarded to `TrainingArguments`

### `embed(inputs, batch_size=256, context_length=None)`

Get encoder embeddings. Returns `(embeddings, idx_ranges)` where each embedding is a tensor and `idx_ranges` maps back to input positions.

---

## ChronosBoltPipeline

Same interface as `Chronos2Pipeline` for `predict()`, `predict_quantiles()`, and `predict_df()`. Does not support covariates, multivariate forecasting, cross-learning, or fine-tuning.

**Properties:**
- `model_context_length` — 2048
- `model_prediction_length` — model-specific (e.g., 512 for bolt-small)
- `forecast_type` — `ForecastType.QUANTILES`

---

## ChronosPipeline (Original Chronos)

### `predict(inputs, prediction_length=None, limit_prediction_length=False)`

Returns sampled trajectories. Shape: list of `(n_samples, prediction_length)` tensors.

**Config parameters:**
- `num_samples` — number of sample trajectories (default: model-specific)
- `temperature` — sampling temperature
- `top_k` — top-k filtering
- `top_p` — nucleus sampling threshold

### `predict_quantiles(inputs, prediction_length=None, quantile_levels=[0.1..0.9])`

Converts samples to quantile estimates. Quality depends on number of samples.

---

## Preprocessing Helpers

### `from_data_frame(df, target_columns, prediction_length, future_df=None, known_covariates_names=None, id_column="item_id", timestamp_column="timestamp", validate_inputs=True)`

Convert DataFrames to `list[PreparedInput]` for fine-tuning or direct prediction. Handles:
- Numeric covariate standardization
- Categorical covariate encoding
- Past vs future covariate separation
- NaN padding

### `from_tensor(data, prediction_length)`

Convert 3D tensor `(n_series, n_variates, context_length)` to `list[PreparedInput]`.

### `from_list_of_tensors(data, prediction_length)`

Convert list of 1D/2D tensors to `list[PreparedInput]`.

### `PreparedInput` TypedDict

```python
class PreparedInput(TypedDict):
    context: torch.Tensor           # (n_variates, context_length), float32
    future_covariates: torch.Tensor # (n_variates, prediction_length), float32
    n_targets: int
    n_covariates: int
    n_future_covariates: int
```
