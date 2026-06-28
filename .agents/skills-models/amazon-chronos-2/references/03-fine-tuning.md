# 03 — Fine-Tuning

## Overview

Chronos-2 supports two fine-tuning modes:

| Mode | Description | When to use |
|---|---|---|
| `full` | Fine-tune all 120M parameters | Large domain-specific datasets, maximum accuracy |
| `lora` | Low-rank adaptation (rank 8) | Quick adaptation, limited data, memory constraints |

## Full Fine-Tuning

```python
finetuned = pipeline.fit(
    inputs=context_df,
    prediction_length=24,
    finetune_mode="full",
    learning_rate=1e-6,
    num_steps=1000,
    batch_size=256,
    output_dir="chronos-2-finetuned",
)
```

**Hyperparameter guidelines**:
- `learning_rate`: 1e-6 (start here, tune from 1e-7 to 1e-5)
- `num_steps`: proportional to dataset size. For 10k series with 500 timesteps each, 500–2000 steps is typical
- `batch_size`: 128–512 depending on GPU memory. Larger batches improve cross-learning
- Use `"bfloat16"` dtype for faster training on Ampere+ GPUs

## LoRA Fine-Tuning

Install `peft` first:

```bash
pip install peft
# or
pip install "chronos-forecasting[extras]"
```

```python
finetuned = pipeline.fit(
    inputs=context_df,
    prediction_length=24,
    finetune_mode="lora",
    learning_rate=1e-5,
    num_steps=500,
    batch_size=256,
    output_dir="chronos-2-lora",
)
```

**LoRA defaults**:
- Rank: 8
- Targets: self-attention heads + output layer
- Higher learning rate than full fine-tuning (1e-5 vs 1e-6)
- Much less memory than full fine-tuning

If `peft` is not installed, `finetune_mode="lora"` silently falls back to `"full"`.

## Fine-Tuning with Covariates

Use the preprocess helper to properly handle covariates:

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
    learning_rate=1e-6,
    num_steps=1000,
    batch_size=256,
    output_dir="chronos-2-covariates",
)
```

The `from_data_frame` helper:
- Identifies known-future covariates (columns in both `df` and `future_df`)
- Identifies past-only covariates (columns only in `df`)
- Handles both numeric and categorical covariates
- Preprocesses data into the format expected by `fit()`

## Fine-Tuning with Tensor Inputs

For advanced use cases, pass preprocessed tensors directly:

```python
import torch

# Shape: (num_series, num_timesteps) for univariate
# Shape: (num_series, num_variates, num_timesteps) for multivariate
inputs = torch.randn(100, 512)

finetuned = pipeline.fit(
    inputs=inputs,
    prediction_length=24,
    finetune_mode="full",
    learning_rate=1e-6,
    num_steps=500,
    batch_size=64,
)
```

## Saving and Loading Fine-Tuned Models

```python
# Save
finetuned.save_pretrained("./my-finetuned-model")

# Load
pipeline = Chronos2Pipeline.from_pretrained("./my-finetuned-model", device_map="cuda")

# Use for prediction
pred_df = pipeline.predict_df(context_df, prediction_length=24)
```

## Fine-Tuning on Benchmarks

Use `predict_fev()` with `finetune_kwargs` to fine-tune on the first evaluation window:

```python
import fev

task = fev.get_task("m4_hourly")
predictions, inference_time = pipeline.predict_fev(
    task,
    batch_size=256,
    finetune_kwargs={
        "finetune_mode": "full",
        "num_steps": 500,
        "learning_rate": 1e-6,
    },
)
```

## Data Preparation Patterns

### Standard Format

Data should be a DataFrame with at minimum:
- `item_id` (or custom `id_column`) — series identifier
- `timestamp` (or custom `timestamp_column`) — datetime values
- `target` (or custom `target` column) — values to predict

### Covariate Format

For covariate-aware fine-tuning, provide `future_df` containing future values of covariates:

```python
# context_df columns: item_id, timestamp, target, temperature, humidity, day_of_week
# future_df columns: item_id, timestamp, temperature, humidity, day_of_week
# (no target column in future_df)

# temperature, humidity, day_of_week → known-future covariates (in both dfs)
# Any column only in context_df → past-only covariate
```

### Multivariate Format

```python
pred_df = pipeline.predict_df(
    context_df,
    target=["price", "demand"],  # multiple targets
    prediction_length=24,
)
```

## Performance Tips

- **GPU is strongly recommended** for fine-tuning. CPU fine-tuning warns when CUDA is available
- **Use bfloat16** on Ampere+ GPUs for faster training: `dtype="bfloat16"`
- **Batch size around 100** is optimal for cross-learning during inference
- **Start with fewer steps** (100–500) and evaluate before committing to longer training
- **Monitor validation loss** on held-out data to avoid overfitting
- **LoRA is faster** and uses less memory; try it before full fine-tuning
