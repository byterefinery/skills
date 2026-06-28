---
name: chronos-forecasting-2-3-0
description: >
  Chronos 2.3.0 — pretrained foundation models for probabilistic time series forecasting
  from Amazon Science. Supports three model families: Chronos-2 (120M, multivariate,
  covariate-aware, cross-learning, fine-tuning), Chronos-Bolt (patch-based, 250x faster),
  and original Chronos (T5-based tokenization). Zero-shot univariate and multivariate
  forecasting with quantile predictions, pandas DataFrame API, fev benchmark integration,
  and SageMaker deployment. Use when the user needs pretrained time series forecasting
  without training from scratch, covariate-aware forecasting, or fast probabilistic
  predictions on arbitrary time series.
metadata:
  tags:
    - ml
    - deep-learning
    - time-series
    - forecasting
    - foundation-model
    - probabilistic
---

# chronos-forecasting 2.3.0

## Overview

Chronos provides pretrained time series forecasting models that work zero-shot on arbitrary data. Install with `pip install chronos-forecasting` (requires Python 3.10+). Three model families are available:

- **Chronos-2** (`Chronos2Pipeline`) — 120M parameters, context length 8192, max prediction length 1024. Supports univariate, multivariate, and covariate-informed forecasting with cross-learning. Best zero-shot accuracy on fev-bench, GIFT-Eval, and Chronos Benchmark II. Supports fine-tuning (full and LoRA). Delivers 300+ forecasts/sec on a single A10G GPU; supports both GPU and CPU inference.
- **Chronos-Bolt** (`ChronosBoltPipeline`) — patch-based direct multi-step forecasting. Up to 250x faster and 20x more memory-efficient than original Chronos at the same size. Sizes: tiny (9M), mini (21M), small (48M), base (205M).
- **Chronos** (`ChronosPipeline`) — original T5-based model using tokenization via scaling and quantization. Probabilistic forecasts via sampling. Sizes: tiny (8M), mini (20M), small (46M), base (200M), large (710M).

All pipelines share the `BaseChronosPipeline` interface: `predict()`, `predict_quantiles()`, `predict_df()`, `predict_fev()`, and `from_pretrained()`.

### Available Models

| Model ID | Parameters | Family | Max Context | Max Horizon |
|---|---|---|---|---|
| `amazon/chronos-2` | 120M | Chronos-2 | 8192 | 1024 |
| `autogluon/chronos-2-synth` | 120M | Chronos-2 | 8192 | 1024 |
| `autogluon/chronos-2-small` | 28M | Chronos-2 | 8192 | 1024 |
| `amazon/chronos-bolt-tiny` | 9M | Chronos-Bolt | 2048 | 64 |
| `amazon/chronos-bolt-mini` | 21M | Chronos-Bolt | 2048 | 64 |
| `amazon/chronos-bolt-small` | 48M | Chronos-Bolt | 2048 | 64 |
| `amazon/chronos-bolt-base` | 205M | Chronos-Bolt | 2048 | 64 |
| `amazon/chronos-t5-tiny` | 8M | Chronos | 512 | 64 |
| `amazon/chronos-t5-mini` | 20M | Chronos | 512 | 64 |
| `amazon/chronos-t5-small` | 46M | Chronos | 512 | 64 |
| `amazon/chronos-t5-base` | 200M | Chronos | 512 | 64 |
| `amazon/chronos-t5-large` | 710M | Chronos | 512 | 64 |

### Capability Comparison

| Capability | Chronos-2 | Chronos-Bolt | Chronos |
|---|---|---|---|
| Univariate Forecasting | ✅ | ✅ | ✅ |
| Cross-learning across items | ✅ | ❌ | ❌ |
| Multivariate Forecasting | ✅ | ❌ | ❌ |
| Past-only covariates (real/categorical) | ✅ | ❌ | ❌ |
| Known-future covariates (real/categorical) | ✅ | ❌ | ❌ |
| Fine-tuning | ✅ | ✅ | ✅ |

Chronos and Chronos-Bolt do not natively support future covariates, but can be combined with external covariate regressors (e.g., via AutoGluon). Chronos-2 supports all covariate types natively, modeling effects across time.

## Usage

### Loading a Model

Use `amazon/chronos-2` as the default model — it is the flagship release with the best accuracy and full feature support (multivariate, covariates, cross-learning, fine-tuning).

```python
from chronos import Chronos2Pipeline

# Default: load amazon/chronos-2
pipeline = Chronos2Pipeline.from_pretrained("amazon/chronos-2", device_map="cuda")

# CPU inference (no GPU required)
pipeline = Chronos2Pipeline.from_pretrained("amazon/chronos-2", device_map="cpu")

# Generic loader (auto-detects pipeline class; works for any Chronos family)
from chronos import BaseChronosPipeline
pipeline = BaseChronosPipeline.from_pretrained("amazon/chronos-2", device_map="cuda")
```

The `device_map` argument accepts `"cuda"`, `"cpu"`, or a dict mapping layers to devices. Use `"cuda"` for GPU inference. Chronos-2 supports both GPU and CPU inference.

Use alternative models only when you have a specific reason:
- **Chronos-Bolt** — latency-sensitive workloads where speed matters more than accuracy
- **Chronos (T5)** — compatibility with existing pipelines trained on the original family
- **`autogluon/chronos-2-small`** — constrained memory environments (28M vs 120M)

### `amazon/chronos-2` Model Details

The flagship Chronos-2 model (`amazon/chronos-2`) is the primary release from Amazon Science.

- **Architecture**: Encoder-only transformer inspired by T5, 120M parameters, 6 layers, 8 attention heads, d_model=512
- **Training data**: Subset of [Chronos Datasets](https://huggingface.co/datasets/autogluon/chronos_datasets) (excluding test portions overlapping with GIFT-Eval), subset of [GIFT-Eval Pretrain](https://huggingface.co/datasets/Salesforce/GiftEvalPretrain), plus synthetic univariate and multivariate data
- **Performance**: 300+ time series forecasts per second on a single A10G GPU; supports CPU inference
- **Quantiles**: Trained on [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]; other levels are interpolated at inference time
- **License**: Apache-2.0
- **Papers**: [Chronos](https://arxiv.org/abs/2403.07815), [Chronos-2](https://arxiv.org/abs/2510.15821)

Derivative models on the HuggingFace Hub:
- **Adapters**: 2 LoRA adapter models built on top of `amazon/chronos-2`
- **Finetunes**: 4 community fine-tuned variants
- **Quantizations**: 4 quantized versions (INT8/INT4) for reduced memory footprint

See [Chronos Models & Datasets collection](https://huggingface.co/collections/amazon/chronos-models-and-datasets) on HuggingFace.

### Tensor-Based Prediction

```python
import torch

# Single univariate series
forecast = pipeline.predict(
    torch.randn(512),
    prediction_length=24,
)

# Batch of series (left-pad with NaN for variable lengths)
batch = torch.randn(32, 512)
forecasts = pipeline.predict(batch, prediction_length=24)

# List of variable-length series (auto left-padded)
series = [torch.randn(100), torch.randn(200), torch.randn(150)]
forecasts = pipeline.predict(series, prediction_length=24)
```

For `Chronos2Pipeline`, `predict()` returns a list of tensors shaped `(n_variates, n_quantiles, prediction_length)`. For `ChronosPipeline`, it returns sampled trajectories shaped `(n_samples, prediction_length)`.

### DataFrame API (Recommended)

The `predict_df()` method handles grouping, batching, and timestamp generation:

```python
import pandas as pd

context_df = pd.read_parquet("data/train.parquet")

pred_df = pipeline.predict_df(
    context_df,
    prediction_length=24,
    quantile_levels=[0.1, 0.5, 0.9],
    id_column="item_id",       # default: "item_id"
    timestamp_column="timestamp",  # default: "timestamp"
    target="target",           # default: "target"
)
```

The returned DataFrame contains: `item_id`, `timestamp`, `target_name`, `predictions`, and one column per quantile level.

### Chronos-2 Specific Features

#### Multivariate Forecasting

Pass multiple target columns:

```python
pred_df = pipeline.predict_df(
    context_df,
    target=["price", "demand"],
    prediction_length=24,
)
```

#### Covariate-Aware Forecasting

Pass future covariates via `future_df`:

```python
future_df = pd.read_parquet("data/test.parquet").drop(columns="target")

pred_df = pipeline.predict_df(
    context_df,
    future_df=future_df,
    prediction_length=24,
)
```

Columns in `context_df` that also appear in `future_df` are treated as known-future covariates. Columns only in `context_df` are past-only covariates. Both numeric and categorical covariates are supported.

#### Cross-Learning

Enable information sharing across time series in a batch:

```python
pred_df = pipeline.predict_df(
    context_df,
    prediction_length=24,
    cross_learning=True,
    batch_size=100,  # optimal ~100 per the technical report
)
```

Cross-learning helps most when individual series have limited history. It does not always improve accuracy — test on your data. Large batch sizes may not help as they deviate from pretraining group sizes.

#### Fine-Tuning

Full fine-tuning and LoRA are supported:

```python
finetuned_pipeline = pipeline.fit(
    inputs=context_df,
    prediction_length=24,
    finetune_mode="lora",       # or "full"
    learning_rate=1e-5,
    num_steps=1000,
    batch_size=256,
    output_dir="chronos-2-finetuned",
)

# Use the fine-tuned model
pred_df = finetuned_pipeline.predict_df(context_df, prediction_length=24)
```

For LoRA, install `peft` with `pip install peft`. Default LoRA config targets self-attention heads and output layer with rank 8. Use higher learning rate (1e-5) for LoRA vs full fine-tuning (1e-6).

#### Preparing Inputs with Covariates for Fine-Tuning

Use the preprocess helpers for proper covariate handling:

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

finetuned = pipeline.fit(
    inputs=prepared,
    prediction_length=24,
    finetune_mode="full",
)
```

### Chronos-Bolt (Alternative)

Use Chronos-Bolt only when latency is critical and you don't need covariates or multivariate support. Chronos-2 (`amazon/chronos-2`) is the default recommendation.

```python
from chronos import ChronosBoltPipeline

pipeline = ChronosBoltPipeline.from_pretrained("amazon/chronos-bolt-small", device_map="cuda")
forecasts = pipeline.predict(torch.randn(512), prediction_length=24)
```

Chronos-Bolt uses `ForecastType.QUANTILES` like Chronos-2. It does not support covariates or multivariate forecasting.

### Benchmarking with fev

```python
import fev
from chronos import Chronos2Pipeline

pipeline = Chronos2Pipeline.from_pretrained("amazon/chronos-2", device_map="cuda")
task = fev.get_task("m4_hourly")
predictions, inference_time = pipeline.predict_fev(task, batch_size=256)
```

For Chronos-2, pass `finetune_kwargs` to fine-tune on the first window before evaluation:

```python
predictions, inference_time = pipeline.predict_fev(
    task,
    batch_size=256,
    finetune_kwargs={"finetune_mode": "full", "num_steps": 500},
)
```

### Saving and Loading Fine-Tuned Models

```python
# Save
pipeline.save_pretrained("./my-chronos-model")

# Load
pipeline = Chronos2Pipeline.from_pretrained("./my-chronos-model", device_map="cuda")
```

### Embedding Extraction (Chronos-2)

Get encoder embeddings for downstream use:

```python
embeddings, idx_ranges = pipeline.embed(
    [torch.randn(100), torch.randn(200)],
    batch_size=256,
)
```

## Gotchas

- **`predict()` return shapes differ by family** — Chronos-2 and Chronos-Bolt return `(n_variates, n_quantiles, prediction_length)` per series. Original Chronos returns `(n_samples, prediction_length)` per series. Use `predict_quantiles()` for a consistent quantile interface across Bolt and Chronos-2.
- **`predict_df()` column naming** — the returned DataFrame uses string quantile levels as column names (e.g., `"0.1"`, `"0.5"`, `"0.9"`), not numeric types. Access with `pred_df["0.5"]`.
- **Long horizons warn by default** — Chronos-2's native max prediction length is 1024. Horizons beyond that use autoregressive unrolling with a warning. Chronos-Bolt and original Chronos are limited to 64 steps. Set `limit_prediction_length=True` to error instead of warn.
- **Cross-learning is batch-size-dependent** — results depend on batch size because the model was pretrained with a maximum group size. Use batch sizes around 100 for best cross-learning results.
- **`device_map` vs `torch_dtype`** — the `from_pretrained()` method handles both the old `torch_dtype` and new `dtype` kwargs from transformers. String values `"bfloat16"` and `"float32"` are resolved automatically.
- **Categorical covariates must be numpy arrays** — torch does not support string dtype. When passing categorical covariates as tensors/dicts, use `np.array` with string values, not `torch.tensor`.
- **`predict_df()` validates timestamps by default** — all series must have regular timestamps at the same frequency with no gaps. Set `validate_inputs=False` to skip validation (faster but risky).
- **Original Chronos uses sampling** — `ChronosPipeline.predict()` returns sample-based forecasts. Use `predict_quantiles()` to get quantile estimates from samples. The number of samples controls forecast quality; more samples give better quantile estimates but are slower.
- **S3 loading requires extras** — loading models from `s3://` URIs requires `pip install 'chronos-forecasting[extras]'` for the `boto3` dependency.
- **LoRA requires peft** — `finetune_mode="lora"` silently falls back to `"full"` if `peft` is not installed. Install with `pip install peft` (or `chronos-forecasting[extras]`).
- **GPU recommended for fine-tuning** — CPU fine-tuning produces a warning when CUDA is available. Use GPU for reasonable fine-tuning speed. Chronos-2 supports CPU inference (not just fine-tuning) for environments without GPUs.

## References

- [01-model-architecture](references/01-model-architecture.md) — Chronos-2 architecture, patch-based forecasting, cross-learning mechanism
- [02-api-reference](references/02-api-reference.md) — Full API reference for all pipeline classes and methods
- [03-fine-tuning-guide](references/03-fine-tuning-guide.md) — Fine-tuning strategies, LoRA config, data preparation patterns
- [04-deployment](references/04-deployment.md) — SageMaker JumpStart, AutoGluon-Cloud deployment patterns
