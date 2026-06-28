# nn.functional Reference

`torch.nn.functional` (imported as `F`) provides functional (stateless) versions of layers and losses. Use `F` when you need to pass extra parameters at call time or compose operations without `nn.Module` overhead.

## Activations

```python
import torch.nn.functional as F

F.relu(x)
F.relu(x, inplace=True)
F.sigmoid(x)
F.tanh(x)
F.gelu(x, approximate="tanh")     # "tanh" (default) or "none"
F.silu(x)                         # Swish
F.elu(x, alpha=1.0)
F.leaky_relu(x, negative_slope=0.01)
F.hardswish(x)
F.hardshrink(x, lambd=0.5)
F.softplus(x, beta=1, threshold=20)
F.softmax(x, dim=-1, dtype=None)
F.log_softmax(x, dim=-1, dtype=None)
F.softsign(x)
F.mish(x)
```

## Normalization

```python
F.batch_norm(x, running_mean, running_var, weight, bias, training, momentum, eps)
F.layer_norm(x, normalized_shape, weight, bias, eps=1e-05)
F.group_norm(x, num_groups, weight, bias, eps=1e-05)
F.instance_norm(x, running_mean, running_var, weight, bias, momentum, eps, track_running_stats)
F.normalize(x, p=2, dim=1, eps=1e-12)  # Lp normalization
```

## Convolutions

```python
# 1D
F.conv1d(input, weight, bias=None, stride=1, padding=0, dilation=1, groups=1)

# 2D
F.conv2d(input, weight, bias=None, stride=1, padding=0, dilation=1, groups=1)

# 3D
F.conv3d(input, weight, bias=None, stride=1, padding=0, dilation=1, groups=1)

# Transposed
F.conv_transpose1d(input, weight, bias=None, stride=1, padding=0, output_padding=0, groups=1, dilation=1)
F.conv_transpose2d(input, weight, bias=None, stride=1, padding=0, output_padding=0, groups=1, dilation=1)

# Unfold (im2col)
patches = F.unfold(input, kernel_size=3, padding=1, stride=1)
```

## Pooling

```python
F.avg_pool1d(input, kernel_size, stride=None, padding=0, ceil_mode=False, count_include_pad=True)
F.avg_pool2d(input, kernel_size, stride=None, padding=0, ceil_mode=False, count_include_pad=True, divisor_override=None)
F.avg_pool3d(input, kernel_size, stride=None, padding=0, ceil_mode=False, count_include_pad=True)

F.max_pool1d(input, kernel_size, stride=None, padding=0, dilation=1, ceil_mode=False, return_indices=False)
F.max_pool2d(input, kernel_size, stride=None, padding=0, dilation=1, ceil_mode=False, return_indices=False)
F.max_pool3d(input, kernel_size, stride=None, padding=0, dilation=1, ceil_mode=False, return_indices=False)

# Unpooling (with indices from max_pool)
output = F.max_unpool2d(pooled, indices, kernel_size=2, stride=2, padding=0, output_size=None)

# Adaptive pooling
F.adaptive_avg_pool1d(input, output_size)
F.adaptive_avg_pool2d(input, output_size)     # output_size can be int or tuple
F.adaptive_avg_pool3d(input, output_size)
F.adaptive_max_pool2d(input, output_size)
```

## Padding

```python
F.pad(x, pad, mode="constant", value=0)
# pad: (pad_left, pad_right, pad_top, pad_bottom, ...) — reverse order, pairs per dim
F.pad(x, (1, 1, 1, 1), mode="reflect")   # reflect padding
F.pad(x, (1, 1, 1, 1), mode="replicate") # edge replication
F.pad(x, (1, 1, 1, 1), mode="circular")  # circular padding
```

**Rule:** `pad` argument is specified in reverse dimension order. For 4D `(N, C, H, W)`, `(1, 1, 1, 1)` pads left/right then top/bottom.

## Upsampling and Interpolation

```python
F.interpolate(input, size=None, scale_factor=None, mode="nearest", align_corners=None)

# Resize to specific shape
F.interpolate(x, size=(224, 224), mode="bilinear", align_corners=False)

# Scale by factor
F.interpolate(x, scale_factor=2, mode="bilinear", align_corners=False)

# Modes: "nearest", "linear" (1D), "bilinear" (2D), "trilinear" (3D),
#        "area", "bicubic" (2D), "nearest-exact"
```

**Rule:** `align_corners=True` maps corners exactly; `False` uses uniform sampling. For most vision tasks, use `align_corners=False`.

## Attention

### `F.scaled_dot_product_attention(query, key, value, attn_mask=None, dropout_p=0.0, is_causal=False, scale=None)`
PyTorch's optimized SDPA — auto-selects backend (Flash Attention, memory-efficient, or eager).

```python
Q = K = V = torch.randn(32, 100, 8, 64)  # (batch, heads, seq, dim)

# Standard attention
attn = F.scaled_dot_product_attention(Q, K, V, scale=1/64**0.5)

# Causal (masked) attention
attn = F.scaled_dot_product_attention(Q, K, V, is_causal=True)

# With explicit mask
mask = torch.randn(32, 100, 100)
attn = F.scaled_dot_product_attention(Q, K, V, attn_mask=mask)
```

**Rule:** `is_causal=True` is equivalent to applying a lower-triangular mask. Prefer `is_causal` over explicit mask for auto-regressive models — it enables Flash Attention.

## Losses

```python
# Classification
F.cross_entropy(logits, targets, weight=None, ignore_index=-100, reduction="mean", label_smoothing=0.0)
F.binary_cross_entropy(input, target, weight=None, reduction="mean")
F.binary_cross_entropy_with_logits(logits, target, weight=None, reduction="mean")

# Regression
F.mse_loss(input, target, reduction="mean")
F.l1_loss(input, target, reduction="mean")
F.smooth_l1_loss(input, target, reduction="mean", beta=1.0)

# Probability
F.nll_loss(input, target, weight=None, ignore_index=-100, reduction="mean")
F.kl_div(input, target, reduction="batchmean", log_target=False)

# Embedding
F.cosine_embedding_loss(input1, input2, target, margin=0.0)
F.triplet_margin_loss(anchor, positive, negative, margin=1.0)
F.hinge_embedding_loss(input, target, margin=1.0)

# Sequence
F.ctc_loss(log_probs, targets, input_lengths, target_lengths, blank=0, zero_infinity=False)
```

**Rule:** `reduction` options: `"mean"` (default, average loss), `"sum"` (total), `"none"` (per-element tensor). Use `"none"` for custom weighting.

## Embedding

```python
F.embedding(input, weight, padding_idx=None, max_norm=None, norm_type=2.0, scale_grad_by_freq=False, sparse=False)
F.embedding_bag(input, weight, offsets=None, max_norm=None, norm_type=2.0, scale_grad_by_freq=False, mode="mean", sparse=False, per_sample_weights=None)
F.one_hot(tensor, num_classes)  # one-hot encoding
```

## Dropout

```python
F.dropout(x, p=0.5, training=True, inplace=False)
F.dropout2d(x, p=0.5, training=True)  # drops entire channels
F.dropout3d(x, p=0.5, training=True)  # drops entire channel-depth slices
F.alpha_dropout(x, p=0.5, training=True)  # for SELU
F.feature_alpha_dropout(x, p=0.5, training=True)
F.bernoulli(x, p=0.5)
```

**Rule:** `F.dropout` uses `training` parameter (defaults to `True`). When used in `forward()`, pass `training=self.training` so it respects `model.train()` / `model.eval()`. `nn.Dropout` layer handles this automatically.

## Distance and Similarity

```python
F.pairwise_distance(x1, x2, p=2.0, eps=1e-06, keepdim=False)
F.cosine_similarity(x1, x2, dim=1, eps=1e-08)
```

## Padding for Sequences

```python
F.pad(sequence, pad=(1, 1), mode="constant", value=0)
# For padding sequences to same length, use torch.nn.utils.rnn.pad_sequence
```

## Vision

```python
F.adjust_brightness(image, brightness_factor)
F.adjust_contrast(image, contrast_factor)
F.adjust_saturation(image, saturation_factor)
F.adjust_hue(image, hue_factor)
F.gaussian_blur(input, kernel_size, sigma)
F.normalize(tensor, mean, std, inplace=False)
F.grid_sample(input, grid, mode="bilinear", padding_mode="zeros", align_corners=True)
F.perspective_transform(input, matrix, align_corners=True)
F.affine_grid(eye_affine, output_size, align_corners=True)
F.feature_alpha_dropout(x, p=0.5, training=True)
```

## Tokenizer Helpers

```python
F.pad_sequence(sequences, batch_first=False, padding_value=0.0)
# sequences: list of 1D tensors of varying lengths
# Returns padded tensor of shape (max_len, batch) or (batch, max_len) with batch_first=True
```
