# Training Workflow Reference

## Model Definition

```python
import torch.nn as nn
import torch.nn.functional as F

class MyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 256)
        self.fc2 = nn.Linear(256, 10)
        self.bn = nn.BatchNorm1d(256)

    def forward(self, x):
        x = x.view(x.size(0), -1)
        x = F.relu(self.bn(self.fc1(x)))
        x = F.dropout(x, p=0.3, training=self.training)
        return self.fc2(x)

model = MyModel()
print(model)  # architecture summary
```

## Training Loop

```python
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

device = "cuda" if torch.cuda.is_available() else "cpu"

# Data
dataset = TensorDataset(X, y)
loader = DataLoader(dataset, batch_size=64, shuffle=True, num_workers=4)

# Setup
model = MyModel().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-2)
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=10)

# Train
model.train()
for epoch in range(10):
    for batch_x, batch_y in loader:
        batch_x, batch_y = batch_x.to(device), batch_y.to(device)
        optimizer.zero_grad()
        logits = model(batch_x)
        loss = criterion(logits, batch_y)
        loss.backward()
        optimizer.step()
    scheduler.step()
```

## Gradient Accumulation

```python
accum_steps = 8
optimizer.zero_grad()

for i, (x, y) in enumerate(loader):
    logits = model(x)
    loss = criterion(logits, y) / accum_steps  # scale loss
    loss.backward()

    if (i + 1) % accum_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

**Rule:** Always divide loss by accumulation steps before `backward()`, otherwise the effective learning rate is multiplied by the accumulation factor.

## Mixed Precision (AMP)

```python
from torch.amp import autocast

scaler = torch.amp.GradScaler("cuda")

for x, y in loader:
    optimizer.zero_grad()
    with autocast("cuda"):
        logits = model(x)
        loss = criterion(logits, y)
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

**Rule:** `GradScaler` is needed for `float16` to prevent underflow. Not needed for `bfloat16` (same exponent range as float32). `autocast` defaults to `float16` on CUDA, `bfloat16` on CPU.

## Saving and Loading Models

```python
# Save weights only (recommended)
torch.save(model.state_dict(), "model.pth")

# Load weights
model = MyModel()
model.load_state_dict(torch.load("model.pth", weights_only=True))

# Save full checkpoint (state dict + hyperparams)
torch.save({
    "epoch": epoch,
    "state_dict": model.state_dict(),
    "optimizer": optimizer.state_dict(),
    "loss": loss.item(),
}, "checkpoint.pth")

# Load full checkpoint
checkpoint = torch.load("checkpoint.pth")
model.load_state_dict(checkpoint["state_dict"])
optimizer.load_state_dict(checkpoint["optimizer"])
start_epoch = checkpoint["epoch"]

# Partial loading (e.g., transfer learning)
model.load_state_dict(checkpoint["state_dict"], strict=False)
```

**Rule:** Use `weights_only=True` when loading state dicts to avoid arbitrary code execution via `pickle`. Only omit when loading full checkpoints with custom objects. Use `strict=True` (default) and check return values when doing partial loading: `missing, unexpected = model.load_state_dict(sd, strict=False)`.

## Evaluation Loop

```python
model.eval()
correct, total = 0, 0

with torch.inference_mode():
    for batch_x, batch_y in val_loader:
        batch_x, batch_y = batch_x.to(device), batch_y.to(device)
        logits = model(batch_x)
        preds = logits.argmax(dim=1)
        correct += (preds == batch_y).sum().item()
        total += batch_y.size(0)

accuracy = correct / total
```

**Rule:** Use `torch.inference_mode()` for pure inference — it skips graph construction entirely (less memory, faster than `torch.no_grad()`). Always call `model.eval()` before inference to disable dropout and use running statistics in batch norm.
