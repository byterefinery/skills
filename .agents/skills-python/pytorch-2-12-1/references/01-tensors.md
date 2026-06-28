# Tensors Reference

## Creation

### From Values

```python
import torch

# From Python sequences
x = torch.tensor([1.0, 2.0, 3.0])           # copies data
x = torch.tensor([[1, 2], [3, 4]], dtype=torch.float32)

# From shapes
x = torch.zeros(3, 4)                        # zeros
x = torch.ones(3, 4)                         # ones
x = torch.full((3, 4), 7.0)                  # fill with value
x = torch.empty(3, 4)                        # uninitialized (fast)
x = torch.eye(4)                             # identity matrix
x = torch.arange(0, 10, 2)                   # [0, 2, 4, 6, 8]
x = torch.linspace(0, 1, 100)                # 100 points from 0 to 1
x = torch.logspace(0, 2, 3)                  # [1, 10, 100]

# Random
x = torch.randn(3, 4)                        # normal(0, 1)
x = torch.rand(3, 4)                         # uniform(0, 1)
x = torch.randint(0, 10, (3, 4))             # uniform integers
x = torch.randn_like(y)                      # same shape as y
```

### From NumPy

```python
import numpy as np

arr = np.array([1.0, 2.0, 3.0])
x = torch.from_numpy(arr)                    # shares memory
arr2 = x.numpy()                             # tensor → numpy (must be CPU, no grad)
```

**Rule:** `from_numpy` shares memory — modifying one modifies the other. Use `.clone().detach()` if independent copy is needed.

## Data Types

| Type | dtype | Bytes | Notes |
|------|-------|-------|-------|
| Float 32 | `torch.float32` / `torch.float` | 4 | Default for training |
| Float 16 | `torch.float16` / `torch.half` | 2 | AMP mixed precision |
| BFloat 16 | `torch.bfloat16` | 2 | Wider exponent, no GradScaler needed |
| Float 64 | `torch.float64` / `torch.double` | 8 | High precision |
| Int 64 | `torch.int64` / `torch.long` | 8 | Indexing, labels |
| Int 32 | `torch.int32` | 4 | Indexing (less memory) |
| Int 16 | `torch.int16` / `torch.short` | 2 | Quantization |
| Int 8 | `torch.int8` | 1 | Quantization |
| UInt 8 | `torch.uint8` | 1 | Images, bytes |
| Bool | `torch.bool` | 1 | Masks |

**Default dtype:** `torch.get_default_dtype()` returns `torch.float32`. Set globally: `torch.set_default_dtype(torch.bfloat16)`.

## Shape and Reshaping

```python
x = torch.randn(2, 3, 4)

# Shape inspection
x.shape          # torch.Size([2, 3, 4])
x.size()         # same as .shape
x.size(1)        # 3
x.ndim           # 3
x.numel()        # 24

# Reshape
y = x.view(6, 4)                  # requires contiguous
y = x.reshape(6, 4)               # handles non-contiguous (may copy)
y = x.flatten()                   # flatten all dims
y = x.flatten(start_dim=1)        # keep first dim
y = x.unsqueeze(0)                # add dim at start: (1, 2, 3, 4)
y = x.unsqueeze(-1)               # add dim at end: (2, 3, 4, 1)
y = x.squeeze()                   # remove all size-1 dims
y = x.squeeze(0)                  # remove only dim 0

# Transpose
y = x.T                           # 2D transpose
y = x.transpose(0, 1)            # swap dims 0 and 1
y = x.permute(2, 0, 1)           # reorder dims
```

**Rule:** `view()` is faster but requires contiguous tensor. `reshape()` is safer. After `transpose()` or `permute()`, tensor is non-contiguous — call `.contiguous()` before `view()`.

## Indexing and Slicing

```python
x = torch.randn(4, 3, 2)

# Basic slicing
x[0]              # shape (3, 2) — first element of dim 0
x[0, 1]           # shape (2,) — first of dim 0, second of dim 1
x[:, 1, :]        # shape (4, 2) — all of dim 0, second of dim 1
x[..., 0]         # shape (4, 3) — last dim index 0

# Fancy indexing
idx = torch.tensor([0, 2, 3])
x[idx]            # shape (3, 3, 2) — select rows 0, 2, 3

# Boolean masking
mask = x > 0.5
x[mask]           # 1D tensor of all values > 0.5

# index_select / gather
y = x.index_select(0, torch.tensor([0, 2]))  # select rows
y = x.gather(0, torch.tensor([[0], [2]]))    # gather along dim 0

# Advanced
y = torch.masked_select(x, x > 0)            # returns 1D tensor
y = torch.nonzero(x > 0)                      # indices of True values
```

## Broadcasting

PyTorch broadcasting follows NumPy rules: dimensions are aligned from the right, and size-1 dimensions are expanded.

```python
a = torch.randn(3, 1, 4)
b = torch.randn(1, 5, 4)
c = a + b  # shape (3, 5, 4) — both broadcast

# Common patterns
x = torch.randn(32, 10)
bias = torch.randn(10)
y = x + bias  # bias broadcasts across batch dim

# Manual broadcast
expanded = bias.unsqueeze(0).expand(32, 10)
```

## Memory Layout

```python
x = torch.randn(3, 4)
x.is_contiguous()   # True

x_t = x.transpose(0, 1)
x_t.is_contiguous()  # False — strides swapped
x_c = x_t.contiguous()  # True — copies data

# Strides
x.stride()  # (4, 1) — how many elements to skip per dimension

# Storage
x.storage()  # underlying 1D data buffer
x.storage_offset()  # offset into storage
```

**Rule:** `contiguous()` allocates new memory. Only call when needed (e.g., before `view()` on non-contiguous tensors).

## Device

```python
x = torch.randn(3, 4, device="cuda")
x = torch.randn(3, 4, device="cuda:1")
x = torch.randn(3, 4).to("cuda")
x = torch.randn(3, 4).cuda()
x = torch.randn(3, 4).cpu()

# Device-agnostic
device = "cuda" if torch.cuda.is_available() else "cpu"
x = torch.randn(3, 4, device=device)
```

## Pin Memory

```python
x = torch.randn(3, 4, pin_memory=True)  # page-locked memory
# Faster transfer to GPU via DataLoader with pin_memory=True
```

**Rule:** Pin memory only when transferring to GPU. It cannot be paged out, so use sparingly.

## Tensor Flags

```python
x.requires_grad    # bool — tracks gradients
x.is_leaf          # bool — leaf tensor (input or parameter)
x.grad             # gradient tensor (set by backward())
x.grad_fn          # function that created this tensor
```

## Clone and Detach

```python
y = x.clone()              # deep copy, same requires_grad
y = x.clone().detach()     # copy without grad tracking
y = x.detach()             # view without grad tracking (shares storage)
```

**Rule:** Use `.detach()` to break from computation graph. Use `.clone().detach()` when you need an independent copy.

## Practical Patterns

```python
import torch

# Creation shortcuts
x = torch.randn(3, 4)                    # random float32
x = torch.zeros(3, 4, dtype=torch.int64) # explicit dtype
x = torch.arange(10, device="cuda")       # on GPU
x = torch.tensor([1.0, 2.0, 3.0])         # from Python list

# Operations
y = x @ x.T                              # matrix multiply
y = torch.matmul(x, x.T)                 # explicit matmul
y = x.sin()                              # elementwise
y = x.sum(dim=1, keepdim=True)           # reduction
y = x.view(2, 6)                         # reshape (same storage)
y = x.reshape(2, 6)                      # reshape (may copy)

# Indexing
y = x[0, :]                              # row slice
y = x[x > 0.5]                           # boolean mask
y = x.index_select(0, torch.tensor([0, 2]))  # select rows
```
