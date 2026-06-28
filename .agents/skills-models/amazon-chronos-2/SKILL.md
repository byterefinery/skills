---
name: amazon-chronos-2
description: >
  Amazon Chronos-2 — 120M-parameter encoder-only time series foundation model for
  zero-shot probabilistic forecasting. Supports univariate, multivariate, and
  covariate-informed tasks with cross-learning across related series. Trained on
  real-world and synthetic data, achieves state-of-the-art zero-shot accuracy on
  fev-bench, GIFT-Eval, and Chronos Benchmark II. Delivers 300+ forecasts/sec on
  a single A10G GPU with CPU inference support. Use when the user needs high-accuracy
  zero-shot time series forecasting, multivariate forecasting, covariate-aware
  predictions, or fine-tuning (full or LoRA) on custom data.
metadata:
  tags:
    - ml
    - deep-learning
    - time-series
    - forecasting
    - foundation-model
    - probabilistic
---

# amazon-chronos-2

## Overview

Chronos-2 is a 120M-parameter, encoder-only transformer for zero-shot time series forecasting. It produces multi-step-ahead quantile forecasts and uses a group attention mechanism for efficient in-context learning across related series and covariates.

Key capabilities:
- **Univariate** — single series forecasting, zero-shot on any data
- **Multivariate** — multiple target columns with cross-series learning
- **Covariate-informed** — past-only and known-future covariates (numeric and categorical)
- **Cross-learning** — information sharing across series within a batch
- **Fine-tuning** — full fine-tuning and LoRA (rank 8, targets self-attention + output)
- **Efficient** — 300+ forecasts/sec on A10G, supports CPU inference
- **Long context** — 8192 context tokens, 1024 prediction horizon

Install with `pip install "chronos-forecasting>=2.0"`. Load with `Chronos2Pipeline.from_pretrained("amazon/chronos-2", device_map="cuda")`.

### Model Details

| Property | Value |
|---|---|
| Parameters | 120M |
| Architecture | Encoder-only transformer (T5-inspired), 6 layers, 8 heads, d_model=512 |
| Max context | 8192 |
| Max prediction length | 1024 (autoregressive beyond) |
| Trained quantiles | [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9] |
| License | Apache-2.0 |
| Papers | [Chronos](https://arxiv.org/abs/2403.07815), [Chronos-2](https://arxiv.org/abs/2510.15821) |

Derivative models on HuggingFace: 2 LoRA adapters, 4 fine-tunes, 4 quantizations (INT8/INT4).

## Usage

### Loading

```python
from chronos import Chronos2Pipeline

# GPU (recommended)
pipeline = Chronos2Pipeline.from_pretrained("amazon/chronos-2", device_map="cuda")

# CPU (no GPU required)
pipeline = Chronos2Pipeline.from_pretrained("amazon/chronos-2", device_map="cpu")

# Auto-detect pipeline class (works for any Chronos family)
from chronos import BaseChronosPipeline
pipeline = BaseChronosPipeline.from_pretrained("amazon/chronos-2", device_map="cuda")
```

### Univariate Forecasting

```python
import pandas as pd

context_df = pd.read_parquet("data/train.parquet")

pred_df = pipeline.predict_df(
    context_df,
    prediction_length=24,
    quantile_levels=[0.1, 0.5, 0.9],
    id_column="item_id",
    timestamp_column="timestamp",
    target="target",
)
```

The returned DataFrame contains `item_id`, `timestamp`, `target_name`, `predictions`, and one column per quantile level (string names: `"0.1"`, `"0.5"`, `"0.9"`).

### Multivariate Forecasting

Pass multiple target columns:

```python
pred_df = pipeline.predict_df(
    context_df,
    target=["price", "demand"],
    prediction_length=24,
)
```

### Covariate-Aware Forecasting

Pass future covariates via `future_df`. Columns appearing in both `context_df` and `future_df` are treated as known-future covariates. Columns only in `context_df` are past-only covariates. Both numeric and categorical covariates are supported.

```python
future_df = pd.read_parquet("data/future.parquet").drop(columns="target")

pred_df = pipeline.predict_df(
    context_df,
    future_df=future_df,
    prediction_length=24,
)
```

### Cross-Learning

Enable information sharing across series in a batch. Most helpful when individual series have limited history.

```python
pred_df = pipeline.predict_df(
    context_df,
    prediction_length=24,
    cross_learning=True,
    batch_size=100,  # optimal per technical report
)
```

### Tensor-Based Prediction

```python
import torch

# Single series
forecast = pipeline.predict(torch.randn(512), prediction_length=24)

# Batch (left-pad with NaN for variable lengths)
forecasts = pipeline.predict(torch.randn(32, 512), prediction_length=24)

# Variable-length list (auto left-padded)
series = [torch.randn(100), torch.randn(200), torch.randn(150)]
forecasts = pipeline.predict(series, prediction_length=24)
```

`predict()` returns a list of tensors shaped `(n_variates, n_quantiles, prediction_length)`.

### Fine-Tuning

```python
finetuned = pipeline.fit(
    inputs=context_df,
    prediction_length=24,
    finetune_mode="lora",       # or "full"
    learning_rate=1e-5,
    num_steps=1000,
    batch_size=256,
    output_dir="chronos-2-finetuned",
)

pred_df = finetuned.predict_df(context_df, prediction_length=24)
```

For LoRA, install `peft` with `pip install peft`. Use higher LR for LoRA (1e-5) vs full fine-tuning (1e-6).

With covariates, use the preprocess helper:

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

finetuned = pipeline.fit(inputs=prepared, prediction_length=24, finetune_mode="full")
```

### Embedding Extraction

```python
embeddings, idx_ranges = pipeline.embed(
    [torch.randn(100), torch.randn(200)],
    batch_size=256,
)
```

### Saving and Loading

```python
pipeline.save_pretrained("./my-model")
pipeline = Chronos2Pipeline.from_pretrained("./my-model", device_map="cuda")
```

### Benchmarking with fev

```python
import fev

pipeline = Chronos2Pipeline.from_pretrained("amazon/chronos-2", device_map="cuda")
task = fev.get_task("m4_hourly")

predictions, inference_time = pipeline.predict_fev(task, batch_size=256)

# With fine-tuning on first window
predictions, inference_time = pipeline.predict_fev(
    task,
    batch_size=256,
    finetune_kwargs={"finetune_mode": "full", "num_steps": 500},
)
```

### Deployment

Two production options:

**AutoGluon-Cloud** (recommended) — minimal setup, pandas DataFrames in/out:

```bash
pip install "autogluon.cloud>=0.5.0"
```

```python
from autogluon.cloud import TimeSeriesFoundationModel

model = TimeSeriesFoundationModel(model_name="chronos-2")
forecast_df = model.predict(df, prediction_length=24)

# Real-time endpoint
endpoint = model.deploy(instance_type="ml.g5.xlarge")
forecast_df = endpoint.predict(df, prediction_length=24)
```

**SageMaker JumpStart** — fine-grained control, JSON payloads:

```bash
pip install -U 'sagemaker<3'
```

```python
from sagemaker.jumpstart.model import JumpStartModel

model = JumpStartModel(model_id="pytorch-forecasting-chronos-2", instance_type="ml.g5.2xlarge")
predictor = model.deploy()

payload = {
    "inputs": [{"target": [1.0, 2.5, 12.3]}],
    "parameters": {"prediction_length": 24},
}
forecast = predictor.predict(payload)["predictions"]
```

## Gotchas

- **`predict()` return shape** — returns list of tensors `(n_variates, n_quantiles, prediction_length)`. For single univariate series, shape is `(1, n_quantiles, prediction_length)`.
- **`predict_df()` quantile columns are strings** — access with `pred_df["0.5"]`, not `pred_df[0.5]`.
- **Horizons beyond 1024 use autoregressive unrolling** — a warning is emitted. Set `limit_prediction_length=True` to error instead.
- **Cross-learning is batch-size-dependent** — the model was pretrained with a fixed group size. Use batch sizes around 100 for best results.
- **Categorical covariates must be numpy arrays** — torch does not support string dtype. Use `np.array` with string values, not `torch.tensor`.
- **`predict_df()` validates timestamps by default** — all series must have regular timestamps at the same frequency with no gaps. Set `validate_inputs=False` to skip (faster but risky).
- **LoRA silently falls back to full fine-tuning** — if `peft` is not installed, `finetune_mode="lora"` becomes `"full"`. Install with `pip install peft` (or `chronos-forecasting[extras]`).
- **GPU recommended for fine-tuning** — CPU fine-tuning warns when CUDA is available. Chronos-2 supports CPU inference for environments without GPUs.
- **`device_map` vs `torch_dtype`** — `from_pretrained()` handles both old `torch_dtype` and new `dtype` kwargs. String values `"bfloat16"` and `"float32"` are resolved automatically.
- **S3 loading requires extras** — `s3://` URIs need `pip install "chronos-forecasting[extras]"` for `boto3`.
- **Quantile interpolation** — trained quantiles are [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]. Other levels are interpolated at inference time.

## References

- [01-architecture](references/01-architecture.md) — Model architecture, group attention, cross-learning mechanism, training data
- [02-api-reference](references/02-api-reference.md) — Full API: Chronos2Pipeline, predict_df, predict, fit, embed, parameter details
- [03-fine-tuning](references/03-fine-tuning.md) — Fine-tuning strategies, LoRA config, data preparation with covariates, hyperparameter tuning
- [04-deployment](references/04-deployment.md) — AutoGluon-Cloud, SageMaker JumpStart, batch inference, endpoint configuration
