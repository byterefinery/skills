# Autograd Reference

## Core Concepts

PyTorch's autograd engine records operations on tensors with `requires_grad=True` and builds a dynamic computation graph. `backward()` traverses the graph in reverse to compute gradients.

```python
import torch

x = torch.tensor(2.0, requires_grad=True)
y = x ** 2
z = y * 3
z.backward()  # computes dz/dx

print(x.grad)  # tensor(12.0) — d(3x²)/dx = 6x = 12
```

## Gradient Tracking Control

```python
# Enable/disable gradient tracking
x = torch.tensor([1.0, 2.0], requires_grad=True)

# Detach from graph (returns new tensor, shares storage)
y = x.detach()
y.requires_grad  # False

# No grad context
with torch.no_grad():
    y = x ** 2  # y.requires_grad is False

# Inference mode (skips graph construction entirely, less memory)
with torch.inference_mode():
    y = x ** 2  # no graph built at all

# Save memory during inference
torch.set_grad_enabled(False)
```

**Rule:** Use `torch.inference_mode()` for pure inference (no gradients needed). It is faster than `torch.no_grad()` because it skips graph construction. Use `torch.no_grad()` when you might still need the graph for other tensors.

## `requires_grad`

```python
# Creation
x = torch.randn(3, 4, requires_grad=True)

# Toggle
x.requires_grad_(True)   # inplace toggle

# Automatic propagation
x = torch.randn(3, requires_grad=True)
y = torch.randn(4, requires_grad=False)
z = x @ y.t()            # z.requires_grad is True (any input has requires_grad)

# Leaf tensors
x = torch.randn(3, requires_grad=True)
y = x ** 2               # y.is_leaf is False (result of operation)
x.is_leaf                 # True (created by user)
```

## `backward()`

```python
# Scalar output — no arguments needed
loss = criterion(output, target)
loss.backward()

# Non-scalar output — pass gradient tensor
output = model(x)  # shape (32, 10)
grad_tensors = torch.ones_like(output)
output.backward(grad_tensors)  # equivalent to (output * grad_tensors).sum().backward()

# retain_graph=True — keep graph for second backward call
output.backward(retain_graph=True)

# create_graph=True — create graph of gradients (for higher-order derivatives)
output.backward(create_graph=True)
```

**Rule:** Call `loss.backward()` on a scalar. For non-scalar, pass `torch.ones_like()` or appropriate gradient tensor. Call `optimizer.zero_grad()` before each backward pass.

## Gradient Accumulation

```python
# Manual accumulation
for i, (x, y) in enumerate(loader):
    loss = model(x, y)
    loss.backward()  # gradients accumulate in .grad
    if (i + 1) % accum_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

## Hooks

### Gradient Hooks

```python
# Register gradient hook on a parameter
def grad_hook(grad):
    print(f"Gradient norm: {grad.norm().item()}")

hook = model.fc.weight.register_hook(grad_hook)

# Gradient clipping via hook
def clip_hook(grad):
    return grad.clamp(-1.0, 1.0)

model.fc.weight.register_hook(clip_hook)

# Remove hook
hook.remove()
```

### Function Hooks (for debugging)

```python
# Hook on autograd function
def pre_hook(ctx, input):
    print(f"Pre: input shape {input[0].shape}")

def post_hook(ctx, grad_output):
    print(f"Post: grad shape {grad_output[0].shape}")

# Register on a specific operation
handle = torch.autograd.Function.register_hook(...)
```

## Custom Autograd Functions

```python
from torch.autograd import Function

class MyFunction(Function):
    @staticmethod
    def forward(ctx, x):
        ctx.save_for_backward(x)
        return x ** 2

    @staticmethod
    def backward(ctx, grad_output):
        x, = ctx.saved_tensors
        return grad_output * 2 * x

# Usage
y = MyFunction.apply(x)
y.backward()
```

**Rule:** Save tensors needed for backward in `ctx.save_for_backward()`. Access via `ctx.saved_tensors`. Do NOT save Python objects that are not tensors unless wrapped properly.

## `torch.autograd.functional`

```python
import torch.autograd.functional as AF

# Jacobian
J = AF.jacobian(model, x)  # Jacobian matrix

# Jacobian-vector product
jvp = AF.jvp(model, x, v)

# Vector-Jacobian product
vjp = AF.vjp(model, x, v)

# Hessian
H = AF.hessian(loss_fn, x)

# Hessian-vector product
hvp = AF.hessian_vector_product(loss_fn, x, v)

# Numerical gradient (finite differences)
grad = AF.gradcheck(func, x, eps=1e-6)  # verifies analytic gradients
```

## Checkpointing (Memory Optimization)

```python
from torch.utils.checkpoint import checkpoint

# Save memory by recomputing activations during backward
def forward_block(x):
    return checkpoint(expensive_block, x)

# With multiple inputs
def forward_block(x, mask):
    return checkpoint(expensive_block, x, mask, use_reentrant=False)
```

**Rule:** Use `checkpoint` for large intermediate activations (e.g., deep transformers). It trades ~20-30% compute for significant memory savings. Use `use_reentrant=False` for compatibility with `torch.compile`.

## `torch.vmap` (Vectorized Map)

```python
# Batch an operation over a new dimension
def single_forward(x):
    return model(x)

batched_forward = torch.vmap(single_forward)
outputs = batched_forward(batch_x)  # vmapped over dim 0

# With specific dimension
batched = torch.vmap(single_forward, in_dims=1, out_dims=1)

# Higher-order: vmap over parameters
def loss_for_params(params, x, y):
    output = apply_params(model, params, x)
    return criterion(output, y)

vmapped_loss = torch.vmap(loss_for_params, in_dims=(0, None, None))
```

## Computational Graph Inspection

```python
# Inspect graph
x = torch.tensor(1.0, requires_grad=True)
y = x ** 2 + 3
print(y.grad_fn)  # <AddBackward0>
print(y.grad_fn.next_functions)  # upstream functions

# Graph visualization (with graphviz)
from torch.utils.tensorboard import SummaryWriter
writer = SummaryWriter()
writer.add_graph(model, input_to_model)
writer.close()
```

## Common Patterns

### Detach for Running Statistics

```python
# EMA (exponential moving average)
running_mean = 0.9 * running_mean + 0.1 * batch_mean.detach()
```

### Stop Gradient

```python
# Prevent gradient flow through a specific tensor
y = x.detach()  # or x.detach().requires_grad_(False)
```

### Accumulate Gradients from Multiple Losses

```python
loss1 = criterion1(output1, target1)
loss2 = criterion2(output2, target2)
loss = loss1 + loss2
loss.backward()  # gradients from both losses accumulate
```
