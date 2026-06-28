# Optimization Reference

## Optimizers

### `optim.SGD(params, lr, momentum=0, dampening=0, weight_decay=0, nesterov=False)`
Stochastic gradient descent with optional momentum.

```python
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9, weight_decay=1e-4)
```

### `optim.Adam(params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8, weight_decay=0)`
Adam optimizer. Adaptive learning rates per parameter.

```python
optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=0)
```

### `optim.AdamW(params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8, weight_decay=0.01)`
Adam with decoupled weight decay. Preferred for deep learning.

```python
optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-2)
```

### Other Optimizers

| Optimizer | Key Parameters | Notes |
|-----------|----------------|-------|
| `optim.Adamax` | `lr, betas, eps, weight_decay` | Adam with L∞ norm |
| `optim.RMSprop` | `lr, alpha, eps, weight_decay, momentum` | RMSProp |
| `optim.Rprop` | `lr, etas, min_lr, max_lr` | Resilient backprop (no momentum) |
| `optim.Lion` | `lr, betas, weight_decay` | Sign-based optimizer, memory efficient |
| `optim.Adadelta` | `lr, rho, eps, weight_decay` | Adaptive learning rate |
| `optim.Adagrad` | `lr, lr_decay, eps, weight_decay` | Accumulates squared gradients |

## Parameter Groups

```python
# Different learning rates for different parameters
optimizer = optim.AdamW([
    {"params": model.backbone.parameters(), "lr": 1e-4},
    {"params": model.head.parameters(), "lr": 1e-3},
    {"params": model.backbone.parameters(), "weight_decay": 1e-4},
    {"params": model.norm.parameters(), "weight_decay": 0.0},  # no WD on norms
])
```

**Rule:** Exclude batch norm / layer norm bias and weight from weight decay. Use `weight_decay=0.0` for normalization layers.

## Learning Rate Schedulers

### Step-Based

```python
# StepLR — reduce LR by factor every step_size epochs
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=30, gamma=0.1)

# MultiStepLR — reduce at specific milestones
scheduler = optim.lr_scheduler.MultiStepLR(optimizer, milestones=[30, 60], gamma=0.1)

# ExponentialLR — multiply by gamma each epoch
scheduler = optim.lr_scheduler.ExponentialLR(optimizer, gamma=0.95)
```

### Performance-Based

```python
# ReduceLROnPlateau — reduce when metric stops improving
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode="min", factor=0.1, patience=5, verbose=True
)
# Call with metric value
scheduler.step(val_loss)  # not scheduler.step()!
```

### Cosine and Warmup

```python
# CosineAnnealingLR — cosine decay
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=50, eta_min=1e-6)

# CosineAnnealingWarmRestarts — cosine with periodic restarts
scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
    optimizer, T_0=10, T_mult=2, eta_min=1e-6
)
```

### OneCycleLR

```python
# One cycle policy — warmup then cosine decay
scheduler = optim.lr_scheduler.OneCycleLR(
    optimizer,
    max_lr=1e-2,
    total_steps=len(train_loader) * num_epochs,
    pct_start=0.3,          # 30% of training for warmup
    anneal_strategy="cos",  # "cos" or "linear"
    div_factor=25,          # min_lr = max_lr / div_factor
)
# Call every step (not every epoch)
for batch in loader:
    ...
    scheduler.step()
```

### Sequential and Chained

```python
# SequentialLR — chain multiple schedulers
scheduler = optim.lr_scheduler.SequentialLR(
    optimizer,
    schedulers=[
        optim.lr_scheduler.LinearLR(optimizer, start_factor=0.1, total_iters=5),
        optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=45),
    ],
    milestones=[5],
)
```

### Constant and Linear Warmup

```python
# Linear warmup
warmup = optim.lr_scheduler.LinearLR(optimizer, start_factor=0.01, total_iters=100)

# Constant LR
constant = optim.lr_scheduler.ConstantLR(optimizer, factor=1.0, total_iters=10)
```

### LambdaLR (Custom)

```python
# Custom schedule via lambda function
scheduler = optim.lr_scheduler.LambdaLR(
    optimizer,
    lr_lambda=lambda epoch: 0.95 ** epoch
)

# Multiple lambdas for multiple parameter groups
scheduler = optim.lr_scheduler.LambdaLR(
    optimizer,
    lr_lambda=[
        lambda epoch: 0.95 ** epoch,   # for group 0
        lambda epoch: 0.99 ** epoch,   # for group 1
    ]
)
```

## Gradient Clipping

```python
# Clip by value
torch.nn.utils.clip_grad_clip_(model.parameters(), clip_value=1.0)

# Clip by norm (recommended)
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

# Clip by value (elementwise)
torch.nn.utils.clip_grad_value_(model.parameters(), clip_value=1.0)

# Get current grad norm
total_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), float("inf"))
```

**Rule:** Use `clip_grad_norm_` for RNNs and transformers. Typical values: 1.0 for LLMs, 0.5 for unstable training. Call after `loss.backward()` and before `optimizer.step()`.

## Mixed Precision (AMP)

### Automatic Mixed Precision

```python
from torch.amp import autocast, GradScaler

scaler = GradScaler("cuda")

for x, y in loader:
    optimizer.zero_grad()
    with autocast("cuda"):
        output = model(x)
        loss = criterion(output, y)
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

### Device-Specific Defaults

| Device | Default dtype | GradScaler needed? |
|--------|--------------|-------------------|
| CUDA | `float16` | Yes |
| CPU | `bfloat16` | No |
| XPU | `bfloat16` | No |

```python
# Override default dtype
with autocast("cuda", dtype=torch.bfloat16):
    output = model(x)
```

### torch.compile with AMP

```python
model = torch.compile(model)

for x, y in loader:
    with autocast("cuda"):
        output = model(x)
        loss = criterion(output, y)
    loss.backward()
    optimizer.step()
```

**Rule:** `torch.compile` works with AMP. No `GradScaler` needed when using `bfloat16`. Prefer `bfloat16` on CUDA for compatibility with `torch.compile`.

## Optimizer State Management

```python
# Save optimizer state
torch.save(optimizer.state_dict(), "optimizer.pth")

# Load
optimizer.load_state_dict(torch.load("optimizer.pth"))

# After loading model state dict, call to re-register parameter refs
optimizer.load_state_dict(torch.load("optimizer.pth"))
# If model params changed, may need:
for param_group in optimizer.param_groups:
    param_group["params"] = [p for p in model.parameters()]
```

## Common Training Patterns

### Freeze / Unfreeze Parameters

```python
# Freeze backbone
for param in model.backbone.parameters():
    param.requires_grad = False

# Only train head
optimizer = optim.AdamW(model.head.parameters(), lr=1e-3)

# Unfreeze all
for param in model.parameters():
    param.requires_grad = True
```

### Gradient Accumulation

```python
accum_steps = 8
for i, (x, y) in enumerate(loader):
    with autocast("cuda"):
        output = model(x)
        loss = criterion(output, y) / accum_steps
    scaler.scale(loss).backward()

    if (i + 1) % accum_steps == 0:
        scaler.unscale_(optimizer)  # unscale before clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad()
```

### Warmup + Cosine (Manual)

```python
def get_lr(current_step, warmup_steps, max_lr, min_lr):
    if current_step < warmup_steps:
        return min_lr + (max_lr - min_lr) * current_step / warmup_steps
    progress = (current_step - warmup_steps) / (total_steps - warmup_steps)
    return min_lr + 0.5 * (max_lr - min_lr) * (1 + math.cos(math.pi * progress))

# Use with LambdaLR or manual lr setting
```
