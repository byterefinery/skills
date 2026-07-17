# Model Loading & Saving

Loading and saving models from the Hugging Face Hub, local directories, and custom configurations.

## from_pretrained

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

# From Hub (downloads and caches)
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-1.5B")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B")

# From local directory
model = AutoModelForCausalLM.from_pretrained("./my-model")

# With dtype
import torch
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-1.5B",
    torch_dtype=torch.bfloat16,
)

# Auto dtype (matches config's torch_dtype)
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-1.5B",
    torch_dtype="auto",
)
```

### Key Parameters

| Parameter | Type | Description |
|---|---|---|
| `pretrained_model_name_or_path` | str | Model ID on Hub or local path |
| `config` | PreTrainedConfig | Pre-loaded config (overrides downloaded) |
| `torch_dtype` | torch.dtype/str | Dtype for weights (`"auto"`, `torch.float16`, etc.) |
| `device_map` | str/dict | Device placement (`"auto"`, `"cpu"`, `{layer: device}`) |
| `low_cpu_mem_usage` | bool | Use meta device for init (default True) |
| `trust_remote_code` | bool | Allow custom code from Hub |
| `revision` | str | Git revision (branch, tag, commit) |
| `local_files_only` | bool | Skip network, use cache only |
| `token` | str/bool | Auth token for gated models |
| `variant` | str | Weight variant (`"fp16"`, `"bf16"`) |
| `offload_folder` | str | CPU offload directory |
| `load_in_8bit`/`load_in_4bit` | bool | bitsandbytes quantization (deprecated) |
| `quantization_config` | dict/QuantizationConfig | Quantization config |
| `cache_dir` | str | Custom cache directory |
| `mirror` | str | Mirror URL for restricted regions |

## Device Mapping

```python
import torch
from transformers import AutoModelForCausalLM

# Single GPU
model = AutoModelForCausalLM.from_pretrained("model", device_map="cuda")
model = AutoModelForCausalLM.from_pretrained("model", device_map="cuda:0")

# Auto device mapping (multi-GPU)
model = AutoModelForCausalLM.from_pretrained("model", device_map="auto")

# Manual device mapping
model = AutoModelForCausalLM.from_pretrained(
    "model",
    device_map={
        "model.embed_tokens": 0,
        "model.layers.0": 0,
        "model.layers.1": 0,
        "model.layers.2": 1,
        "model.layers.3": 1,
        "model.norm": 1,
        "lm_head": 1,
    }
)

# CPU offloading (for models larger than GPU memory)
model = AutoModelForCausalLM.from_pretrained(
    "model",
    device_map="auto",
    offload_folder="./offload",  # Directory for offloaded layers
)

# Disk offloading
model = AutoModelForCausalLM.from_pretrained(
    "model",
    device_map="auto",
    offload_folder="./offload",
    offload_buffers=True,  # Also offload buffers
)
```

### infer_auto_device_map

```python
from transformers import AutoModelForCausalLM, AutoConfig
from accelerate import infer_auto_device_map

# Compute optimal device map
config = AutoConfig.from_pretrained("model")
device_map = infer_auto_device_map(
    model=AutoModelForCausalLM.from_config(config),
    max_memory={0: "10GiB", 1: "10GiB", "cpu": "50GiB"},
)

# Load with computed map
model = AutoModelForCausalLM.from_pretrained("model", device_map=device_map)
```

## save_pretrained

```python
# Save to directory
model.save_pretrained("./my-model")

# Save as safetensors (default)
model.save_pretrained("./my-model", safe_serialization=True)

# Save as pickle (.bin)
model.save_pretrained("./my-model", safe_serialization=False)

# Save specific layers only
model.save_pretrained("./my-model", selected_layers=["model.layers.0", "lm_head"])
```

## push_to_hub

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import login

# Authenticate
login(token="hf_...")  # Or use huggingface-cli login

# Push model
model.push_to_hub("username/my-model")

# Push with config
model.push_to_hub(
    "username/my-model",
    commit_message="Upload fine-tuned model",
    private=True,
    tags=["finetuned", "text-generation"],
)

# Push tokenizer
tokenizer.push_to_hub("username/my-model-tokenizer")

# Push both together
model.push_to_hub("username/my-model")
tokenizer.push_to_hub("username/my-model")
```

## Loading Variants

```python
# Load specific weight variant
model = AutoModelForCausalLM.from_pretrained("model", variant="fp16")
# Loads model.fp16.safetensors instead of model.safetensors

# Load from specific revision
model = AutoModelForCausalLM.from_pretrained("model", revision="main")
model = AutoModelForCausalLM.from_pretrained("model", revision="v1.0")
model = AutoModelForCausalLM.from_pretrained("model", revision="abc1234")

# Load from Hub URL directly
model = AutoModelForCausalLM.from_pretrained(
    "https://huggingface.co/user/model/resolve/main/model.safetensors"
)

# Load from S3/other storage (requires fsspec)
model = AutoModelForCausalLM.from_pretrained("s3://bucket/model/")
```

## Custom Config

```python
from transformers import AutoConfig, AutoModelForSequenceClassification

# Override config parameters
config = AutoConfig.from_pretrained("bert-base-uncased")
config.num_labels = 3
config.hidden_dropout_prob = 0.3

model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    config=config,
)

# Or inline
model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=3,
    attn_dropout=0.3,
)
```

## Loading State Dicts

```python
import torch

# Load state dict from file
state_dict = torch.load("model.pth", map_location="cpu", weights_only=True)
model.load_state_dict(state_dict)

# Partial load (ignore missing keys)
missing, unexpected = model.load_state_dict(state_dict, strict=False)
print(f"Missing: {missing}")
print(f"Unexpected: {unexpected}")

# Load from safetensors
from safetensors.torch import load_file

state_dict = load_file("model.safetensors")
model.load_state_dict(state_dict)
```

## Loading Custom Models

```python
# Model with custom architecture on Hub
model = AutoModelForCausalLM.from_pretrained(
    "custom-model",
    trust_remote_code=True,  # Executes custom code from Hub
)

# Model from local custom code
from my_module import MyModel

model = MyModel.from_pretrained("./my-model-dir")
```

## Memory Optimization

```python
# Low CPU memory usage (default in 5.x)
model = AutoModelForCausalLM.from_pretrained(
    "model",
    low_cpu_mem_usage=True,  # Uses meta device
)

# Load in specific dtype to save memory
model = AutoModelForCausalLM.from_pretrained(
    "model",
    torch_dtype=torch.float16,  # Half precision
    low_cpu_mem_usage=True,
)

# Gradient checkpointing (saves memory during training)
model.config.use_cache = False
model.gradient_checkpointing_enable()
```

## Gotchas

- **`torch_dtype="auto"` reads from config** — the config may specify `torch_dtype: "bfloat16"`. Use explicit dtype if you need a specific one.
- **`device_map="auto"` requires `accelerate`** — install with `pip install accelerate`. Without it, use `.to("cuda")`.
- **`low_cpu_mem_usage=True` is default** — uses meta device for initialization. Disable for models that don't support meta tensors.
- **`trust_remote_code=True` is a security risk** — only use for models you trust. It executes arbitrary Python code from the Hub.
- **`safetensors` is the default format** — models saved with `save_pretrained()` use safetensors. Older models may use `.bin` (pickle).
- **`push_to_hub` requires write access** — the token must have write permissions to the repo. Create the repo on the Hub first if it doesn't exist.
- **`variant` loads specific files** — `variant="fp16"` loads `model.fp16.safetensors`. The variant must exist in the repo.
- **`offload_folder` must exist** — create the directory before loading, or the loader creates it automatically.
- **`device_map` with `generate()`** — when using device maps, ensure `generate()` inputs are on the correct device (usually the first device in the map).
- **`load_state_dict` with `strict=False`** — silently ignores missing/unexpected keys. Always check the return values.
- **`torch.load` with `weights_only=True`** — safe loading that only deserializes tensors. Use for state dicts. Omit only for full model saves with custom objects.
- **`cache_dir` vs `HF_HOME`** — `cache_dir` parameter overrides `HF_HOME` env var for this specific load.
- **`local_files_only=True` for air-gapped** — useful in production where network access is restricted. Pre-download models during deployment.
- **`revision` for reproducibility** — always pin to a specific commit hash for reproducible loads, not a branch name.
- **`token=True` uses stored token** — passes the token from `huggingface-cli login`. Use `token="hf_..."` for explicit tokens.
- **`resume_from_checkpoint`** — Trainer can resume from a saved checkpoint directory. Pass the path or `True` for auto-detection.
- **`is_loaded_in_4bit`/`is_loaded_in_8bit`** — check if model was loaded with quantization: `model.config.quantization_config`.
- **`model.hf_device_map`** — after loading with `device_map`, check device placement: `model.hf_device_map`.
- **`dispatch_model` for manual placement** — use `accelerate.dispatch_model(model, device_map)` for fine-grained control.
- **`.to()` after `device_map`** — avoid calling `.to()` on models loaded with `device_map`. It overrides the device placement.
