# Mixins and Serialization

## ModelHubMixin

Generic mixin for integrating any ML framework with the Hub. Provides `save_pretrained()`, `from_pretrained()`, and `push_to_hub()`.

```python
from huggingface_hub import ModelHubMixin
from dataclasses import dataclass

@dataclass
class MyConfig(ModelHubMixin, init=False):
    dim: int = 768
    n_layers: int = 12
    dropout: float = 0.1

config = MyConfig(dim=512, n_layers=6)
config.save_pretrained("/tmp/my-config")
config = MyConfig.from_pretrained("/tmp/my-config")
```

### Class attributes

| Attribute | Type | Description |
|---|---|---|
| `repo_url` | `str` | Library repo URL (for model card) |
| `paper_url` | `str` | Paper URL (for model card) |
| `docs_url` | `str` | Documentation URL (for model card) |
| `model_card_template` | `str` | Model card template string |

### Methods

#### save_pretrained

```python
model.save_pretrained(
    save_directory="/path/to/save",
    push_to_hub=False,           # push directly to Hub
    repo_id="username/my-model", # required if push_to_hub=True
    token="hf_...",              # required if push_to_hub=True
    model_card_kwargs=None,      # dict for ModelCard generation
    safe_serialization=False,    # use safetensors (requires torch)
    conversion_fn=None,          # custom encoder for non-dataclass args
    _library_name="my-library",  # library name in model card
)
```

#### from_pretrained

```python
model = MyModel.from_pretrained(
    pretrained_model_name_or_path="username/my-model",  # local path or Hub repo ID
    force_download=False,
    cache_dir=None,
    token=None,
    revision=None,
    # Additional kwargs passed to __init__
    dim=512,
)
```

#### push_to_hub

```python
model.push_to_hub(
    repo_id="username/my-model",
    token="hf_...",
    model_card_kwargs=None,
    safe_serialization=False,
    private=False,
)
```

### Custom argument encoding

For non-dataclass/non-JSON-serializable arguments, provide `conversion_fn`:

```python
import torch

class MyModel(ModelHubMixin):
    def __init__(self, weight: torch.Tensor):
        self.weight = weight

    def _save_pretrained(self, save_directory):
        torch.save(self.weight, save_directory / "weight.pt")

    @classmethod
    def _from_pretrained(cls, model_dir, **kwargs):
        weight = torch.load(model_dir / "weight.pt")
        return cls(weight=weight)

model = MyModel(weight=torch.randn(10, 10))
model.save_pretrained("/tmp/model")
model = MyModel.from_pretrained("/tmp/model")
```

## PyTorchModelHubMixin

Specialized mixin for PyTorch models. Handles state dict serialization automatically.

```python
import torch.nn as nn
from huggingface_hub import PyTorchModelHubMixin

class MyModel(nn.Module, PyTorchModelHubMixin):
    def __init__(self, hidden_size: int = 768, output_size: int = 10):
        super().__init__()
        self.linear = nn.Linear(hidden_size, output_size)
        self.hidden_size = hidden_size
        self.output_size = output_size

    def forward(self, x):
        return self.linear(x)

# Create and save
model = MyModel(hidden_size=256, output_size=5)
model.save_pretrained("my-model")

# Load from local
model = MyModel.from_pretrained("my-model")

# Load from Hub
model = MyModel.from_pretrained("username/my-model")

# Push to Hub
model.push_to_hub("username/my-model", token="hf_...")
```

### save_pretrained with safetensors

```python
# Save using safetensors (default for PyTorchModelHubMixin)
model.save_pretrained("my-model", safe_serialization=True)

# Save using pickle (pytorch_model.bin)
model.save_pretrained("my-model", safe_serialization=False)
```

When `safe_serialization=True`, the model is saved as `model.safetensors` instead of `pytorch_model.bin`. For large models, files are sharded automatically.

### Model card generation

PyTorchModelHubMixin auto-generates a model card with library info:

```python
class MyModel(nn.Module, PyTorchModelHubMixin,
              repo_url="https://github.com/user/my-lib",
              paper_url="https://arxiv.org/abs/2301.00001",
              docs_url="https://my-lib.readthedocs.io"):
    ...
```

## Serialization utilities

### State dict splitting

```python
from huggingface_hub import split_torch_state_dict_into_shards

state_dict = {"layer1.weight": ..., "layer2.weight": ...}

shards, index = split_torch_state_dict_into_shards(
    state_dict,
    max_shard_size="5GB",           # max size per shard
    weights_name="model.safetensors",
)
# shards: dict of shard_name -> state_dict_subset
# index: dict with metadata for loading
```

### save_torch_model / load_torch_model

```python
from huggingface_hub import save_torch_model, load_torch_model

# Save model with automatic sharding
save_torch_model(
    model,
    save_directory="/path/to/model",
    max_shard_size="5GB",
    safe_serialization=True,
)

# Load model from sharded files
model = load_torch_model(
    model,
    checkpoint_file="/path/to/model/model.safetensors.index.json",
    strict=False,
)
```

### save_torch_state_dict / load_state_dict_from_file

```python
from huggingface_hub import save_torch_state_dict, load_state_dict_from_file

# Save state dict
save_torch_state_dict(
    state_dict,
    save_directory="/path/to/model",
    max_shard_size="5GB",
    safe_serialization=True,
)

# Load state dict
state_dict = load_state_dict_from_file(
    checkpoint_file="/path/to/model/model.safetensors",
    weights_map=None,  # optional: mapping of expected param names
)
```

### split_state_dict_into_shards_factory

```python
from huggingface_hub import split_state_dict_into_shards_factory

splitter = split_state_dict_into_shards_factory(
    state_dict,
    max_shard_size="5GB",
    weights_name="model.safetensors",
    storage_id=get_torch_storage_id,
    storage_size=get_torch_storage_size,
)
shards, index = splitter()
```

### get_torch_storage_id / get_torch_storage_size

```python
from huggingface_hub import get_torch_storage_id, get_torch_storage_size

storage_id = get_torch_storage_id(tensor.storage())
storage_size = get_torch_storage_size(tensor.storage())
```

## Safetensors utilities

### get_safetensors_metadata

```python
from huggingface_hub import get_safetensors_metadata

metadata = get_safetensors_metadata(
    repo_id="username/my-model",
    filename="model.safetensors",
    token=None,
)
```

### parse_safetensors_file_metadata

```python
from huggingface_hub import parse_safetensors_file_metadata

info = parse_safetensors_file_metadata(metadata)
print(info.metadata)  # custom metadata dict
print(info.weights_metadata)  # tensor info
```

### get_local_safetensors_metadata

```python
from huggingface_hub import get_local_safetensors_metadata

info = get_local_safetensors_metadata("/path/to/model.safetensors")
```

### parse_local_safetensors_file_metadata

```python
from huggingface_hub import parse_local_safetensors_file_metadata

info = parse_local_safetensors_file_metadata("/path/to/model.safetensors")
```

## DDUF (Deep Learning Unified Format)

DDUF is a format for packaging model weights with metadata.

```python
from huggingface_hub import (
    export_folder_as_dduf,
    export_entries_as_dduf,
    read_dduf_file,
)

# Export a folder as DDUF
dduf_path = export_folder_as_dduf(
    folder_path="/path/to/model",
    output_path="/path/to/output.dduf",
)

# Export entries as DDUF
entries = [DDUFEntry(...)]
dduf_path = export_entries_as_dduf(entries, output_path="/path/to/output.dduf")

# Read DDUF file
dduf = read_dduf_file("/path/to/output.dduf")
```

## Constants

| Constant | Value | Description |
|---|---|---|
| `PYTORCH_WEIGHTS_NAME` | `"pytorch_model.bin"` | Default PyTorch weights filename |
| `TF_WEIGHTS_NAME` | `"model.ckpt"` | Default TensorFlow weights filename |
| `TF2_WEIGHTS_NAME` | `"model.ckpt"` | Default TF2 weights filename |
| `FLAX_WEIGHTS_NAME` | `"flax_model.msgpack"` | Default Flax weights filename |
| `CONFIG_NAME` | `"config.json"` | Default config filename |
| `SAFETENSORS_SINGLE_FILE` | `"model.safetensors"` | Single safetensors file |
| `SAFETENSORS_INDEX_FILE` | `"model.safetensors.index.json"` | Sharded index file |
