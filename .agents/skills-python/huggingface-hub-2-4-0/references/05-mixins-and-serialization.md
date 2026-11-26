# 05 — Mixins and serialization

## ModelHubMixin

Base class for integrating any ML framework with the Hub. Subclasses gain `from_pretrained`, `save_pretrained`, and `push_to_hub` plus config serialization via `CONFIG_NAME`.

```python
from huggingface_hub import ModelHubMixin

class MyConfig(ModelHubMixin):
    def __init__(self, dim: int = 768, n_layers: int = 12):
        self.dim = dim
        self.n_layers = n_layers

config = MyConfig(dim=512)
config.save_pretrained("/tmp/my-config")
config = MyConfig.from_pretrained("/tmp/my-config")
```

## PyTorchModelHubMixin

Adds PyTorch weight handling on top of `ModelHubMixin`. Weight file names are constants: `PYTORCH_WEIGHTS_NAME`, plus `FLAX_WEIGHTS_NAME`, `TF_WEIGHTS_NAME`, `TF2_WEIGHTS_NAME` for other frameworks.

```python
from huggingface_hub import PyTorchModelHubMixin
import torch.nn as nn

class MyModel(nn.Module, PyTorchModelHubMixin):
    def __init__(self, hidden_size: int = 768):
        super().__init__()
        self.linear = nn.Linear(hidden_size, hidden_size)

model = MyModel(hidden_size=256)
model.save_pretrained("/tmp/my-model")
model = MyModel.from_pretrained("/tmp/my-model")
model.push_to_hub("username/my-model")
```

Requires the `torch` extra (`pip install "huggingface_hub[torch]"` pulls `torch` + `safetensors[torch]`).

## Safetensors utilities (module-level functions)

- `get_safetensors_metadata(repo_id, ...)` — metadata for safetensors files in a repo
- `get_local_safetensors_metadata(...)` — same for local files
- `get_sharded_safetensors_metadata(...)` — combined metadata across sharded files
- `parse_safetensors_file_metadata(...)`, `parse_local_safetensors_file_metadata(...)`
- `load_state_dict_from_file(...)` — load a state dict from a local file
- `SafetensorsParsingError`, `NotASafetensorsRepoError` — related errors

## Torch storage helpers (Xet-backed)

- `save_torch_model(...)`, `save_torch_state_dict(...)`
- `split_torch_state_dict_into_shards(...)`, `StateDictSplit`
- `get_torch_storage_id(...)`, `get_torch_storage_size(...)` — Xet storage identifiers/sizes

## fastai integration

`save_pretrained_fastai`, `from_pretrained_fastai`, `push_to_hub_fastai` (requires the `fastai` extra).
