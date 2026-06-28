# nn.Module Reference

## Module Basics

### `nn.Module`
Base class for all neural network modules. Manages parameters, buffers, submodules, and device placement.

```python
import torch.nn as nn

class MyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(128, 10)
        self.bn = nn.BatchNorm1d(128)

    def forward(self, x):
        return self.fc(self.bn(x))
```

**Key attributes:**
- `model.parameters()` — iterator over all parameters (for optimizers)
- `model.named_parameters()` — `(name, parameter)` pairs
- `model.state_dict()` — ordered dict of all parameters and buffers
- `model.buffers()` / `model.named_buffers()` — non-parameter tensors
- `model.modules()` — all modules including self
- `model.children()` — immediate child modules only

**Key methods:**
- `model.train()` — set to training mode (enables dropout, batch norm running stats)
- `model.eval()` — set to evaluation mode (disables dropout, uses running stats)
- `model.to(device)` — move all parameters and buffers to device
- `model.to(dtype)` — cast all parameters to dtype
- `model.to(device, dtype)` — both
- `model.cuda()` / `model.cpu()` — device-specific shortcuts
- `model.zero_grad()` — zero gradients of all parameters
- `model.apply(fn)` — call `fn` on every submodule (e.g., weight initialization)
- `model.named_modules()` — `(name, module)` pairs for all nested modules

### `nn.Sequential`

```python
# Positional (auto-named by index)
model = nn.Sequential(
    nn.Linear(784, 256),
    nn.ReLU(),
    nn.Linear(256, 10),
)

# Named (ordered dict)
model = nn.Sequential(
    nn.Sequential([
        ("fc1", nn.Linear(784, 256)),
        ("act", nn.ReLU()),
        ("fc2", nn.Linear(256, 10)),
    ])
)

# Access submodules
model[0]              # first layer
model["fc1"]          # named layer
```

### `nn.ModuleList` and `nn.ModuleDict`

```python
# ModuleList — ordered list of modules (registered, iterable)
class MultiLayer(nn.Module):
    def __init__(self, num_layers):
        super().__init__()
        self.layers = nn.ModuleList([nn.Linear(128, 128) for _ in range(num_layers)])

    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        return x

# ModuleDict — dict of modules (registered, keyed)
class Router(nn.Module):
    def __init__(self):
        super().__init__()
        self.branches = nn.ModuleDict({
            "a": nn.Linear(64, 10),
            "b": nn.Linear(64, 20),
        })

    def forward(self, x, branch):
        return self.branches[branch](x)
```

**Rule:** Do NOT use Python `list` or `dict` to store modules — parameters won't be registered. Always use `ModuleList` or `ModuleDict`.

## Linear Layers

### `nn.Linear(in_features, out_features, bias=True, device=None, dtype=None)`
Fully connected layer: `y = xA^T + b`

```python
fc = nn.Linear(256, 128)
x = torch.randn(32, 256)
y = fc(x)  # (32, 128)
```

## Convolutional Layers

### `nn.Conv1d(in_channels, out_channels, kernel_size, stride=1, padding=0, dilation=1, groups=1, bias=True)`
1D convolution (time series, audio).

```python
conv = nn.Conv1d(3, 16, kernel_size=3, padding=1)
x = torch.randn(32, 3, 100)  # (batch, channels, length)
y = conv(x)                   # (32, 16, 100)
```

### `nn.Conv2d(in_channels, out_channels, kernel_size, stride=1, padding=0, dilation=1, groups=1, bias=True)`
2D convolution (images).

```python
conv = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1)
x = torch.randn(32, 3, 224, 224)
y = conv(x)  # (32, 64, 224, 224)

# Depthwise + pointwise (groups = in_channels)
dw = nn.Conv2d(64, 64, kernel_size=3, padding=1, groups=64)
pw = nn.Conv2d(64, 128, kernel_size=1)
```

### `nn.Conv3d`
3D convolution (video, medical imaging). Same API as Conv2d with 5D input `(batch, channels, depth, height, width)`.

### Transposed Convolutions

```python
# Upsampling convolution
conv_t = nn.ConvTranspose2d(64, 32, kernel_size=4, stride=2, padding=1)
x = torch.randn(32, 64, 7, 7)
y = conv_t(x)  # (32, 32, 14, 14)
```

## Normalization Layers

### `nn.BatchNorm1d(num_features, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)`
Batch normalization for 3D input `(batch, features, length)` or 2D `(batch, features)`.

```python
bn = nn.BatchNorm1d(128)
x = torch.randn(32, 128)
y = bn(x)
```

### `nn.BatchNorm2d(num_features)`
For 4D input `(batch, channels, height, width)`. Used in CNNs.

### `nn.LayerNorm(normalized_shape, eps=1e-05, elementwise_affine=True)`
Layer normalization — normalizes across feature dimensions, independent of batch.

```python
ln = nn.LayerNorm(768)           # normalize last dim
x = torch.randn(32, 100, 768)    # (batch, seq, features)
y = ln(x)                         # (32, 100, 768)

# Multi-dimensional shape
ln = nn.LayerNorm([10, 768])     # normalize last 2 dims
```

### `nn.GroupNorm(num_groups, num_channels, eps=1e-05, affine=True)`
Groups channels and normalizes within each group.

```python
gn = nn.GroupNorm(8, 64)  # 64 channels / 8 groups = 8 channels per group
```

### `nn.InstanceNorm2d(num_features)`
Normalizes each channel independently for each sample. Used in style transfer.

### `nn.RMSNorm(dim, eps=1e-05)`
RMS normalization (no mean subtraction). Common in modern transformer models.

```python
rms = nn.RMSNorm(768)
```

## Recurrent Layers

### `nn.LSTM(input_size, hidden_size, num_layers=1, batch_first=False, dropout=0.0, bidirectional=False)`
```python
lstm = nn.LSTM(128, 256, num_layers=2, batch_first=True, bidirectional=True)
x = torch.randn(32, 50, 128)  # (batch, seq, features)
output, (hn, cn) = lstm(x)
# output: (32, 50, 512) — 512 = 256 * 2 (bidirectional)
# hn: (4, 32, 256) — (num_layers * directions, batch, hidden)
```

### `nn.GRU(input_size, hidden_size, ...)`
Same API as LSTM but without cell state.

### `nn.RNN(input_size, hidden_size, ...)`
Basic RNN cell.

## Attention and Transformer

### `nn.MultiheadAttention(embed_dim, num_heads, dropout=0.0, batch_first=False)`
```python
mha = nn.MultiheadAttention(768, num_heads=12, batch_first=True)
query = key = value = torch.randn(32, 100, 768)
output, attn_weights = mha(query, key, value)
# output: (32, 100, 768)
# attn_weights: (32, 100, 100)
```

### `nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward=2048, dropout=0.1, batch_first=False)`
Single transformer encoder layer (self-attention + FFN).

```python
layer = nn.TransformerEncoderLayer(d_model=768, nhead=12, batch_first=True)
encoder = nn.TransformerEncoder(layer, num_layers=6)
x = torch.randn(32, 100, 768)
output = encoder(x)  # (32, 100, 768)
```

### `nn.TransformerDecoderLayer` / `nn.TransformerDecoder`
Decoder layers with self-attention + cross-attention + FFN.

### `nn.ScaledDotProductAttention`
Available via `torch.nn.functional.scaled_dot_product_attention` (SDPA).

## Embedding

### `nn.Embedding(num_embeddings, embedding_dim, padding_idx=None)`
```python
emb = nn.Embedding(10000, 300, padding_idx=0)
x = torch.tensor([[1, 2, 3], [4, 5, 0]])  # token indices
y = emb(x)  # (2, 3, 300)
```

### `nn.EmbeddingBag(num_embeddings, embedding_dim, mode="mean")`
Embedding + pooling in one operation. Efficient for variable-length sequences.

```python
eb = nn.EmbeddingBag(10000, 300, mode="mean")
offsets = torch.tensor([0, 2])  # where each bag starts
y = eb(input_ids, offsets)  # pooled embeddings
```

## Pooling

| Layer | Description |
|-------|-------------|
| `nn.AdaptiveAvgPool2d(output_size)` | Adaptive average pooling to target size |
| `nn.AdaptiveMaxPool2d(output_size)` | Adaptive max pooling to target size |
| `nn.AvgPool2d(kernel_size, stride, padding)` | Fixed-size average pooling |
| `nn.MaxPool2d(kernel_size, stride, padding)` | Fixed-size max pooling |
| `nn.LPPool2d(norm_type, kernel_size)` | Lp norm pooling |

## Activation Functions (as modules)

| Module | Function |
|--------|----------|
| `nn.ReLU()` | `max(0, x)` |
| `nn.ReLU6()` | `min(max(0, x), 6)` |
| `nn.Sigmoid()` | `1 / (1 + exp(-x))` |
| `nn.Tanh()` | hyperbolic tangent |
| `nn.GELU()` | Gaussian error linear unit |
| `nn.SiLU()` / `nn.SiLU()` | `x * sigmoid(x)` (Swish) |
| `nn.ELU(alpha=1.0)` | exponential linear unit |
| `nn.LeakyReLU(negative_slope=0.01)` | leaky ReLU |
| `nn.Hardswish()` | `x * hard_sigmoid(x)` |
| `nn.Softmax(dim)` | softmax along dim |
| `nn.LogSoftmax(dim)` | log softmax along dim |
| `nn.Softplus()` | `log(1 + exp(x))` |

## Hooks

```python
# Forward hook — called after forward()
def forward_hook(module, input, output):
    print(f"{module.__class__.__name__} output shape: {output.shape}")

hook = model.fc.register_forward_hook(forward_hook)

# Forward pre-hook — called before forward()
def pre_hook(module, input):
    print(f"Input shape: {input[0].shape}")

model.fc.register_forward_pre_hook(pre_hook)

# Full forward hook (2.0+) — receives kwargs too
def full_hook(module, args, kwargs, output):
    pass

model.fc.register_full_forward_hook(full_hook)

# Gradient hook — called when grad is computed
def grad_hook(module, grad_input, grad_output):
    print(f"Grad norm: {grad_output[0].norm().item()}")

model.fc.register_full_backward_hook(grad_hook)

# Remove hook
hook.remove()
```

## Parameter Initialization

```python
import torch.nn.init as init

# Common initializers
init.xavier_uniform_(model.fc.weight)   # for tanh/sigmoid
init.kaiming_uniform_(model.fc.weight)  # for ReLU (default)
init.kaiming_normal_(model.conv.weight) # for ReLU
init.normal_(model.fc.weight, mean=0, std=0.01)
init.constant_(model.fc.bias, 0)

# Apply to all modules
def init_weights(m):
    if isinstance(m, nn.Linear):
        init.xavier_uniform_(m.weight)
        init.constant_(m.bias, 0)
    elif isinstance(m, nn.Conv2d):
        init.kaiming_normal_(m.weight)

model.apply(init_weights)
```

## Loss Functions (as modules)

| Module | Use Case |
|--------|----------|
| `nn.CrossEntropyLoss()` | Classification (logits → labels) |
| `nn.BCELoss()` | Binary classification (probabilities → labels) |
| `nn.BCEWithLogitsLoss()` | Binary classification (logits → labels, numerically stable) |
| `nn.MSELoss()` | Regression (mean squared error) |
| `nn.L1Loss()` | Regression (mean absolute error) |
| `nn.SmoothL1Loss(beta=1.0)` | Huber loss |
| `nn.NLLLoss()` | Negative log likelihood (log-probs → labels) |
| `nn.KLDivLoss(reduction="batchmean")` | KL divergence |
| `nn.CosineEmbeddingLoss()` | Cosine similarity loss |
| `nn.TripletMarginLoss(margin=1.0)` | Triplet loss for embeddings |
| `nn.CTCLoss(blank=0, zero_infinity=False)` | CTC loss for sequence models |

**Rule:** `CrossEntropyLoss` expects raw logits (no softmax). `NLLLoss` expects log-probabilities (apply `LogSoftmax` first). `BCEWithLogitsLoss` is preferred over `BCELoss` + `Sigmoid` for numerical stability.
