# TimesFM 2.5 Architecture

## Overview

TimesFM 2.5 is a decoder-only transformer with 200M parameters designed for zero-shot time series forecasting. It processes time series through patch-based tokenization, autoregressive decoding, and outputs both point forecasts and quantile predictions.

## Model Definition

The model is defined by `TimesFM_2p5_200M_Definition`:

```python
@dataclasses.dataclass(frozen=True)
class TimesFM_2p5_200M_Definition:
    context_limit: int = 16384          # Max total context (input + output)
    input_patch_len: int = 32           # Input patch size (tokenization window)
    output_patch_len: int = 128         # Output patch size (per decode step)
    output_quantile_len: int = 1024     # Max quantile horizon
    quantiles: list[float] = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    decode_index: int = 5               # Index used for autoregressive feedback
```

## Tokenization Pipeline

Raw time series are converted to tokens through patching:

1. **Front-padding**: If series length is not a multiple of `input_patch_len` (32), zeros are prepended
2. **Patching**: Series is reshaped from `(context,)` to `(num_patches, 32)`
3. **Masking**: A boolean mask tracks which patches are real data vs. padding
4. **Tokenization**: Each patch + mask is fed through a `ResidualBlock` (tokenizer) to produce embeddings

```
Input: [x₁, x₂, ..., xₙ]
         ↓ front-pad to multiple of 32
Padded: [0, 0, ..., x₁, x₂, ..., xₙ]
         ↓ reshape to patches
Patches: [[0,...,0], [0,...,xₖ], [xₖ,...,xₙ], ...]
         ↓ tokenizer (ResidualBlock)
Tokens:  [e₁, e₂, ..., eₘ]  →  (num_patches, 1280)
```

## Transformer Stack

20 transformer layers process the token sequence:

- **Model dimension**: 1,280
- **Hidden dimension**: 1,280
- **Attention heads**: 16 (head dimension = 80)
- **Normalization**: RMSNorm for attention and feedforward
- **QK normalization**: RMSNorm on queries and keys
- **Position embeddings**: Rotary (RoPE) for relative position awareness
- **Feedforward activation**: Swish
- **QKV fusion**: Fused QKV projection for efficiency

Each layer outputs both the transformed embeddings and a `DecodeCache` for autoregressive decoding.

## Output Projections

Two separate `ResidualBlock` projections produce the outputs:

1. **Point projection** (`output_projection_point`): 1280 → 1280 → `(output_patch_len × 10)` = 1,280
   - Produces per-step predictions for all 10 quantile channels

2. **Quantile spread projection** (`output_projection_quantiles`): 1280 → 1280 → `(output_quantile_len × 10)` = 10,240
   - Produces continuous quantile spreads for the quantile head

## ReVIN Normalization

Reversible Instance Normalization (ReVIN) normalizes each series independently:

```python
def revin(inputs, mu, sigma, reverse=False):
    if not reverse:
        return (inputs - mu) / sigma  # normalize
    else:
        return inputs * sigma + mu    # denormalize
```

Running statistics are maintained patch-by-patch during decoding:

```python
def update_running_stats(n, mu, sigma, new_patch, mask):
    # Online update of mean and variance
    # Handles masked (padded) patches correctly
    return (n, mu, sigma), updated_patch
```

This ensures the model is invariant to the scale of input data — a series of values in [0, 1] or [0, 1,000,000] produces equivalent forecasts (rescaled appropriately).

## Autoregressive Decoding

For horizons beyond the initial output patch, the model decodes autoregressively:

1. **Prefill phase**: Process all input patches through the transformer stack
2. **Initial output**: Get first `output_patch_len` (128) predictions
3. **Feedback loop**: Take the `decode_index` (5, i.e., median) from the last output patch
4. **Reshape**: Split the 128-point output into 4 patches of 32 points each (`m = output_patch_len / input_patch_len = 4`)
5. **Decode step**: Feed these 4 patches through the transformer, get 4 new output patches
6. **Repeat**: Continue until desired horizon is reached

```
Prefill → [output₁, output₂, ..., outputₖ]
              ↓ take last patch, index 5 (median)
Feedback: [p₁, p₂, p₃, p₄]  (4 patches of 32 points)
              ↓ transformer decode
New output: [outputₖ₊₁, ..., outputₖ₊₄]
              ↓ repeat
```

Number of decode steps: `(horizon - 1) // output_patch_len`

## Decode Cache

Each transformer layer maintains a `DecodeCache` for efficient autoregressive decoding:

```python
@dataclasses.dataclass
class DecodeCache:
    next_index: torch.Tensor    # (batch_size,) — next position to write
    num_masked: torch.Tensor    # (batch_size,) — count of masked positions
    key: torch.Tensor           # (batch_size, cache_size, heads, head_dim)
    value: torch.Tensor         # (batch_size, cache_size, heads, head_dim)
```

Cache size: `num_input_patches + num_decode_steps × m` where `m = 4`.

## Quantile Head

The optional continuous quantile head (30M parameters) improves prediction interval calibration:

- **When enabled**: `use_continuous_quantile_head=True` in `ForecastConfig`
- **Max horizon**: 1,024 time steps (`output_quantile_len`)
- **Mechanism**: Uses the quantile spread output to adjust quantile estimates relative to the median
- **Quantile adjustment**: For indices 1-4 and 6-9, replaces the fixed quantile with a continuous estimate derived from the spread

## Flip Invariance

TimesFM guarantees `f(aX + b) = a × f(X) + b` for `a ≥ 0` by default. With `force_flip_invariance=True`, this extends to `a < 0`:

1. Run forward pass on `inputs`
2. Run forward pass on `-inputs`
3. Average: `output = (f(inputs) - f(-inputs)) / 2`

This ensures mathematical consistency and prevents sign-dependent bias.

## Framework Implementations

The architecture is implemented in two backends:

| Component | PyTorch (`torch/`) | JAX/Flax (`flax/`) |
|-----------|-------------------|-------------------|
| Dense layers | `dense.ResidualBlock` | `dense.ResidualBlock` |
| Transformer | `transformer.Transformer` | `transformer.Transformer` |
| Normalization | `normalization.RMSNorm` | `normalization.RMSNorm` |
| Utilities | `util.revin`, `util.DecodeCache` | `util.revin`, `util.DecodeCache` |

Both implementations share the same config definitions from `configs.py`.
