# Fine-Tuning Guide

## Overview

Fine-tune `amazon/chronos-2` (the default model) on your domain data. Chronos-2 supports two fine-tuning modes: **full fine-tuning** (all 120M parameters) and **LoRA** (Low-Rank Adaptation). The `fit()` method returns a new `Chronos2Pipeline` with the fine-tuned model, leaving the original unchanged.

## Quick Start

```python
from chronos import Chronos2Pipeline

pipeline = Chronos2Pipeline.from_pretrained("amazon/chronos-2", device_map="cuda")

finetuned = pipeline.fit(
    inputs=context_df,
    prediction_length=24,
    finetune_mode="full",
    learning_rate=1e-6,
    num_steps=1000,
    batch_size=256,
)
```

## Fine-Tuning Modes

### Full Fine-Tuning

Updates all 120M parameters. Use when you have substantial domain-specific data and want maximum adaptation.

```python
finetuned = pipeline.fit(
    inputs=train_data,
    prediction_length=24,
    finetune_mode="full",
    learning_rate=1e-6,
    num_steps=1000,
)
```

### LoRA Fine-Tuning

Freezes the base model and trains low-rank adapter matrices. Requires `peft` (`pip install peft`).

```python
from peft import LoraConfig

finetuned = pipeline.fit(
    inputs=train_data,
    prediction_length=24,
    finetune_mode="lora",
    learning_rate=1e-5,
    num_steps=1000,
    lora_config=LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=[
            "self_attention.q", "self_attention.v",
            "self_attention.k", "self_attention.o",
            "output_patch_embedding.output_layer",
        ],
    ),
)
```

Default LoRA config (when `lora_config=None`): rank 8, alpha 16, targeting all attention heads and the output layer. LoRA trains far fewer parameters (~0.1% of total) and is faster with less GPU memory.

## Data Preparation

### Simple: DataFrame Direct

Pass a DataFrame directly — targets only, no covariates:

```python
finetuned = pipeline.fit(
    inputs=context_df,
    prediction_length=24,
    finetune_mode="full",
)
```

### With Covariates: Preprocess Helpers

For covariate-aware fine-tuning, use `from_data_frame()` to build properly structured inputs:

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

### With List of Dicts

Manual control over past/future covariates:

```python
inputs = [
    {
        "target": np.array([...]),
        "past_covariates": {
            "temperature": np.array([...]),
            "day_of_week": np.array(["Mon", "Tue", ...]),
        },
        "future_covariates": {
            "temperature": np.array([...]),
            "day_of_week": np.array(["Wed", "Thu", ...]),
        },
    }
    for _ in range(n_series)
]

finetuned = pipeline.fit(inputs=inputs, prediction_length=24, finetune_mode="full")
```

## Validation

Pass `validation_inputs` to enable validation during training. The best model (lowest eval loss) is saved automatically:

```python
finetuned = pipeline.fit(
    inputs=train_data,
    validation_inputs=val_data,
    prediction_length=24,
    finetune_mode="full",
    num_steps=2000,
)
```

Validation triggers periodic evaluation (every 100 steps) and saves checkpoints. Adds overhead — skip for small datasets.

## Hyperparameter Tuning

| Parameter | Default | Typical Range | Notes |
|---|---|---|---|
| `learning_rate` | 1e-6 | 1e-7–1e-5 | Use 1e-5 for LoRA |
| `num_steps` | 1000 | 100–5000 | Scale with dataset size |
| `batch_size` | 256 | 64–512 | Larger = more stable gradients |
| `context_length` | 8192 | 256–8192 | Shorter = faster, less history |
| `min_past` | prediction_length | prediction_length–context_length | Filters short series |

## Context Length During Fine-Tuning

You can increase `context_length` beyond the pretrained value during fine-tuning. The model's RoPE embeddings support longer sequences via the pretrained `inv_freq` buffer. The fine-tuned model updates `chronos_config.context_length` to reflect the new value.

```python
finetuned = pipeline.fit(
    inputs=train_data,
    prediction_length=24,
    context_length=4096,  # shorter than default 8192 for faster training
)
```

## Saving and Loading

Fine-tuned models are saved automatically to `output_dir/finetuned_ckpt/`. Load them like any pretrained model:

```python
# Save location: output_dir / finetuned_ckpt_name
finetuned_path = Path("chronos-2-finetuned/2025-01-01_12-00-00/finetuned-ckpt")

loaded = Chronos2Pipeline.from_pretrained(str(finetuned_path), device_map="cuda")
```

## Training Infrastructure

### GPU Requirements

- **Full fine-tuning**: ~16GB+ VRAM for batch_size=256 with bf16
- **LoRA**: ~8GB+ VRAM for the same batch size
- Training uses bf16 on SM80+ GPUs (Ampere+) with tf32 enabled
- DataParallel is disabled by default (`disable_data_parallel=True`); use multi-GPU strategies externally if needed

### Performance Tips

- Use `batch_size` that fits in GPU memory — the effective batch includes all variates and covariates
- For LoRA, higher learning rates (1e-4–1e-5) often work well
- Set `remove_printer_callback=True` to suppress training progress output
- Use `output_dir` on fast storage (NVMe) for checkpoint saving
- Set `dataloader_num_workers=0` (default) to avoid multiprocessing overhead on small datasets

## Common Patterns

### Domain Adaptation

Fine-tune on a small dataset from your domain to adapt the pretrained model:

```python
finetuned = pipeline.fit(
    inputs=domain_data,
    prediction_length=24,
    finetune_mode="lora",
    learning_rate=1e-5,
    num_steps=500,
)
```

### Horizon-Specific Tuning

Fine-tune for a specific prediction horizon:

```python
finetuned = pipeline.fit(
    inputs=train_data,
    prediction_length=168,  # 1-week ahead (hourly)
    finetune_mode="full",
    num_steps=1000,
)
```

The model updates `max_output_patches` to cover the new horizon.

### Multi-Target Fine-Tuning

Fine-tune with multiple target columns for multivariate adaptation:

```python
prepared = from_data_frame(
    df=context_df,
    target_columns=["price", "demand", "inventory"],
    prediction_length=24,
)

finetuned = pipeline.fit(
    inputs=prepared,
    prediction_length=24,
    finetune_mode="full",
)
```
