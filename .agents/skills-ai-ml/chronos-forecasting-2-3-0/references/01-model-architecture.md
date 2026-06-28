# Chronos-2 Model Architecture

## Overview

Chronos-2 is an encoder-only transformer (120M parameters) designed for universal time series forecasting. It extends Chronos-Bolt's patch-based approach with two key innovations: **cross-learning** (information sharing across time series) and **native covariate support**.

## Architecture Components

### Input Processing

1. **Patch Embedding** — Input series are chunked into patches via `Patch(patch_size, patch_stride)`. Patches are unfolded along the time dimension, padding with NaN if needed to align to patch boundaries.
2. **Instance Normalization** — Each series is standardized (mean=0, std=1) using `InstanceNorm`. Optionally applies arcsinh transform for heavy-tailed data.
3. **Residual Embedding** — A `ResidualBlock` maps patches to the model's hidden dimension (`d_model=512`) with layer norm option.

### Encoder Blocks

Each `Chronos2EncoderBlock` applies three sub-layers in sequence:

1. **TimeSelfAttention** — Standard self-attention along the time dimension with RoPE position embeddings. Uses either eager attention or SDPA (`torch.nn.functional.scaled_dot_product_attention`). No scaling factor (matches original Chronos-2 design).
2. **GroupSelfAttention** — Self-attention along the **batch dimension** (time and batch axes are swapped). No RoPE since there is no natural ordering across series. The group attention mask controls which series can attend to each other, enabling cross-learning.
3. **FeedForward** — Position-wise MLP with ReLU activation, layer norm before MLP, and residual connection.

### Output Head

The `Chronos2Decoder` (a thin wrapper) applies:
1. Time cross-attention from output tokens to encoder states
2. Residual block to produce quantile predictions directly

### Key Hyperparameters

| Parameter | Value | Description |
|---|---|---|
| `d_model` | 512 | Hidden dimension |
| `d_kv` | 64 | Key/value dimension per head |
| `d_ff` | 2048 | FFN intermediate dimension |
| `num_layers` | 6 | Encoder blocks |
| `num_heads` | 8 | Attention heads |
| `context_length` | 8192 | Max input context |
| `output_patch_size` | model-specific | Tokens per output patch |
| `input_patch_size` | model-specific | Input patch size |
| `input_patch_stride` | model-specific | Patch stride |
| `quantiles` | [0.1–0.9] | Trained quantile levels |
| `rope_theta` | 10000.0 | RoPE base frequency |
| `dropout_rate` | 0.1 | Dropout across all layers |

## Cross-Learning Mechanism

Cross-learning is implemented via `GroupSelfAttention`. During pretraining, time series are grouped, and the group attention mask allows attention within groups but blocks cross-group attention. At inference:

- **Default (`cross_learning=False`)** — Each series gets a unique `group_id`, so group attention is effectively disabled (each series attends only to itself).
- **Enabled (`cross_learning=True`)** — All series share `group_id=0`, allowing full cross-series attention. This lets the model leverage patterns from related series in the batch.

The group attention mask has shape `(batch, num_heads, seq_len, batch)` and is constructed so that series in the same group can attend to each other.

## Patch-Based Forecasting

Chronos-2 uses a patch-based approach inherited from Chronos-Bolt:

- **Input**: Series → patches of `input_patch_size` with stride `input_patch_stride` → embedded to `(n_patches, d_model)`
- **Output**: Encoder produces `(n_patches, d_model)` → decoder generates `max_output_patches` output patches, each of size `output_patch_size`, directly predicting quantile values
- **Long horizons**: When `prediction_length > max_output_patches * output_patch_size`, autoregressive unrolling is used. Selected quantiles from the first prediction are appended to context and fed back through the model.

## Attention Implementation

Two backends are supported via `attn_implementation` config:

- **`"sdpa"`** (default) — Uses `torch.nn.functional.scaled_dot_product_attention`. Faster, lower memory. Does not return attention weights.
- **`"eager"`** — Manual matmul + softmax. Returns attention weights. Used when `output_attentions=True`.

Both implementations use `scale=1.0` (no scaling), matching the original Chronos-2 design.

## Layer Normalization

Chronos-2 uses T5-style layer normalization (`Chronos2LayerNorm`): no bias, no mean subtraction, only variance-based scaling. Applied before each attention and FFN sub-layer (pre-norm).

## RoPE Position Embeddings

`Chronos2RotaryEmbedding` applies standard RoPE with `theta=10000`. Used only in `TimeSelfAttention` (not `GroupSelfAttention`, since there is no temporal ordering across series). Computed in float32 regardless of model dtype to preserve precision on long contexts.

## Training Data

The default model `amazon/chronos-2` was trained on:

- **Chronos Datasets** — subset of [autogluon/chronos_datasets](https://huggingface.co/datasets/autogluon/chronos_datasets), excluding test portions that overlap with GIFT-Eval benchmarks
- **GIFT-Eval Pretrain** — subset of [Salesforce/GiftEvalPretrain](https://huggingface.co/datasets/Salesforce/GiftEvalPretrain)
- **Synthetic data** — large-scale synthetic univariate and multivariate time series

Full details in the [Chronos-2 technical report](https://arxiv.org/abs/2510.15821).

## Model Derivatives

The HuggingFace Hub hosts derivatives of `amazon/chronos-2`:

- **2 LoRA adapters** — domain-specific adapters that can be loaded on top of the base model
- **4 community fine-tunes** — full fine-tuned variants for specific domains
- **4 quantized versions** — INT8/INT4 quantizations for reduced memory footprint

See the [Chronos Models & Datasets collection](https://huggingface.co/collections/amazon/chronos-models-and-datasets).
