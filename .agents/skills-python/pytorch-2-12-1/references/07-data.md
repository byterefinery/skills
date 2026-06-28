# Data Reference

## Dataset

### `torch.utils.data.Dataset`
Abstract base class. Implement `__len__` and `__getitem__`.

```python
from torch.utils.data import Dataset

class MyDataset(Dataset):
    def __init__(self, data, labels, transform=None):
        self.data = data
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sample = self.data[idx]
        label = self.labels[idx]
        if self.transform:
            sample = self.transform(sample)
        return sample, label
```

### `TensorDataset`
Wrap tensors directly. Splits along first dimension.

```python
from torch.utils.data import TensorDataset

dataset = TensorDataset(X, y)  # X: (N, ...), y: (N, ...) or (N,)
sample = dataset[0]  # returns (x_0, y_0)
```

### `ConcatDataset`
Concatenate multiple datasets.

```python
from torch.utils.data import ConcatDataset

combined = ConcatDataset([train_set, val_set])
```

### `Subset`
Select a subset of indices.

```python
from torch.utils.data import Subset

subset = Subset(dataset, indices=[0, 1, 2, 3])
```

### `random_split`
Split dataset randomly.

```python
from torch.utils.data import random_split

train, val = random_split(dataset, [0.8, 0.2], generator=torch.Generator().manual_seed(42))
```

## DataLoader

### `torch.utils.data.DataLoader(dataset, batch_size=1, shuffle=False, sampler=None, batch_sampler=None, num_workers=0, collate_fn=None, pin_memory=False, drop_last=False, timeout=0, worker_init_fn=None, prefetch_factor=2, persistent_workers=False, ...)`

```python
from torch.utils.data import DataLoader

loader = DataLoader(
    dataset,
    batch_size=32,
    shuffle=True,
    num_workers=4,
    pin_memory=True,
    drop_last=False,
    prefetch_factor=2,
    persistent_workers=True,
)

# Iterate
for batch_x, batch_y in loader:
    ...

# With enumeration
for i, (batch_x, batch_y) in enumerate(loader):
    ...
```

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `batch_size` | 1 | Samples per batch |
| `shuffle` | False | Shuffle each epoch (incompatible with custom sampler) |
| `sampler` | None | Custom sampler (incompatible with shuffle) |
| `num_workers` | 0 | Number of worker processes |
| `pin_memory` | False | Pin CPU memory for faster GPU transfer |
| `drop_last` | False | Drop incomplete last batch |
| `prefetch_factor` | 2 | Batches prefetched per worker |
| `persistent_workers` | False | Keep workers alive across epochs |
| `collate_fn` | `default_collate` | Merge samples into batch |
| `timeout` | 0 | Seconds to wait for worker data |

**Rule:** Set `persistent_workers=True` with `num_workers > 0` for faster epoch restarts. Set `pin_memory=True` when transferring to GPU.

## Samplers

### `torch.utils.data.SequentialSampler(dataset)`
Draw samples sequentially.

### `torch.utils.data.RandomSampler(dataset, replacement=False, num_samples=None, generator=None)`
Draw samples randomly.

```python
sampler = RandomSampler(dataset, generator=torch.Generator().manual_seed(42))
loader = DataLoader(dataset, sampler=sampler)  # shuffle must be False
```

### `torch.utils.data.WeightedRandomSampler(weights, num_samples, replacement=True, generator=None)`
Sample with probability proportional to weights.

```python
import torch

weights = torch.tensor([1.0, 2.0, 0.5, 3.0])  # higher = more likely
sampler = WeightedRandomSampler(weights, num_samples=len(weights), replacement=False)
```

### `torch.utils.data.BatchSampler(sampler, batch_size, drop_last)`
Wrap a sampler to yield batches.

```python
sampler = BatchSampler(RandomSampler(dataset), batch_size=32, drop_last=True)
```

### `torch.utils.data.DistributedSampler(dataset, num_replicas=None, rank=None, shuffle=True, seed=0)`
For distributed training — each process gets a disjoint subset.

```python
from torch.utils.data import DistributedSampler

sampler = DistributedSampler(dataset, shuffle=True)
loader = DataLoader(dataset, sampler=sampler, batch_size=32)

# Must call set_epoch before each epoch for different shuffles
for epoch in range(num_epochs):
    sampler.set_epoch(epoch)
    for batch in loader:
        ...
```

## Collate Functions

### Default Collate
`default_collate` stacks tensors, pads sequences, and handles dicts/lists.

### Custom Collate

```python
def custom_collate(batch):
    # batch is a list of samples from __getitem__
    images = [item[0] for item in batch]
    labels = torch.tensor([item[1] for item in batch])
    # Stack images (must be same size)
    images = torch.stack(images)
    return images, labels

loader = DataLoader(dataset, collate_fn=custom_collate)
```

### Padding Sequences

```python
import torch.nn.utils.rnn as rnn_utils

def pad_collate(batch):
    texts, labels = zip(*batch)
    # Pad to longest sequence in batch
    texts_padded = rnn_utils.pad_sequence(texts, batch_first=True, padding_value=0)
    labels = torch.tensor(labels)
    return texts_padded, labels
```

## Transforms

### Compose

```python
from torchvision.transforms import Compose, ToTensor, Normalize, RandomCrop, Resize

transform = Compose([
    Resize((224, 224)),
    RandomCrop(224),
    ToTensor(),
    Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])
```

### Functional Transforms

```python
import torchvision.transforms.functional as TF

# Apply transforms individually (for conditional logic)
image = TF.resize(image, (224, 224))
image = TF.to_tensor(image)
image = TF.normalize(image, mean=[...], std=[...])
```

## Utilities

### `torch.utils.data.SubsetRandomSampler(indices)`
Sample randomly from a subset of indices.

```python
indices = [i for i, (_, y) in enumerate(dataset) if y == 1]
sampler = SubsetRandomSampler(indices)
```

### `makeIterableLoader` (for iterable datasets)

```python
from torch.utils.data import IterableDataset

class StreamDataset(IterableDataset):
    def __init__(self, source):
        self.source = source

    def __iter__(self):
        return iter(self.source)

loader = DataLoader(stream_dataset, batch_size=32, num_workers=4)
```

### Worker Initialization

```python
def worker_init_fn(worker_id):
    # Set seed per worker for reproducibility
    import random
    seed = torch.initial_seed() % (2**32)
    random.seed(seed + worker_id)

loader = DataLoader(dataset, worker_init_fn=worker_init_fn)
```

## Memory Mapping

```python
# For large datasets that don't fit in RAM
import numpy as np
from torch.utils.data import Dataset

class MmapDataset(Dataset):
    def __init__(self, path):
        self.data = np.memmap(path, dtype=np.float32, mode="r", shape=(100000, 784))
        self.labels = np.memmap(path + ".labels", dtype=np.int64, mode="r", shape=(100000,))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return torch.from_numpy(self.data[idx]), self.labels[idx]
```

## Common Patterns

### Train/Val Split

```python
from torch.utils.data import random_split, DataLoader

total = len(dataset)
train_size = int(0.8 * total)
val_size = total - train_size

train_set, val_set = random_split(dataset, [train_size, val_size],
                                   generator=torch.Generator().manual_seed(42))

train_loader = DataLoader(train_set, batch_size=32, shuffle=True, num_workers=4)
val_loader = DataLoader(val_set, batch_size=64, shuffle=False, num_workers=4)
```

### Data Augmentation with Albumentations

```python
import albumentations as A
from torchvision.transforms import ToTensor

transform = A.Compose([
    A.RandomRotate90(),
    A.Flip(),
    A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.1, rot_limit=15),
    A.ToFloat(max_value=255.0),
    A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ToTensor(),
])
```
