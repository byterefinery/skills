# Model Loading Reference

## `from_pretrained()`

Universal loading method on all `PreTrainedModel`, `PreTrainedTokenizer`, `PreTrainedConfig`, and processor classes.

### Signature

```python
model = AutoModelForCausalLM.from_pretrained(
    pretrained_model_name_or_path,  # str: Hub ID or local path
    *,
    config=None,                     # PreTrainedConfig or path
    cache_dir=None,                  # str: custom cache directory
    ignore_mismatched_sizes=False,   # bool: allow partial weight mismatches
    force_download=False,            # bool: re-download even if cached
    local_files_only=False,          # bool: don't download, use cache only
    token=None,                      # str or bool: Hub auth token
    revision="main",                 # str: git revision/branch/tag
    use_safetensors=None,           # bool: prefer safetensors format
    weights_only=True,               # bool: use torch.load weights_only
    dtype=None,                      # torch.dtype or str: model precision
    device_map=None,                 # str or dict: device placement
    quantization_config=None,        # dict or QuantizationConfig
    torch.compile_compat=False,      # bool: compile compatibility mode
    **kwargs,
)
```

### Model ID vs Local Path

```python
# From Hub
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B")

# From local directory
model = AutoModelForCausalLM.from_pretrained("./my-model-dir")

# From specific revision
model = AutoModelForCausalLM.from_pretrained("bert-base-uncased", revision="main")

# With auth token (gated models)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    token="hf_...",
)
```

### Dtype (Precision)

```python
import torch
from transformers import AutoModelForCausalLM

# Full precision (default)
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-1.5B")

# Half precision
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-1.5B",
    dtype=torch.float16,
)

# BFloat16 (recommended for Ampere+ GPUs)
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-1.5B",
    dtype=torch.bfloat16,
)

# String shorthand
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-1.5B",
    dtype="auto",  # infers from saved weights or GPU capability
)
```

> **Note:** `torch_dtype` is deprecated. Use `dtype` instead.

### Device Map

```python
# Auto-split across available GPUs
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-70B",
    device_map="auto",
)

# Specific GPU
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-1.5B",
    device_map="cuda:0",
)

# CPU offloading (for models larger than GPU memory)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-70B",
    device_map="auto",
    offload_folder="./offload",  # CPU offload directory
)

# Disk offloading
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-70B",
    device_map="auto",
    offload_folder="./offload",
    offload_buffers=True,
)

# Manual device map
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-70B",
    device_map={
        "model.embed_tokens": 0,
        "model.layers.0": 0,
        "model.layers.1": 0,
        "model.layers.2": 1,
        "model.layers.3": 1,
        "model.norm": 1,
        "lm_head": 1,
    },
)
```

> **Requires:** `accelerate` package (`pip install accelerate`).

## Quantization

### bitsandbytes (4-bit / 8-bit)

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

# 4-bit quantization
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",           # "nf4" or "fp4"
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,      # quantize quantization constants
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    quantization_config=bnb_config,
    device_map="auto",
)

# 8-bit quantization
bnb_config = BitsAndBytesConfig(load_in_8bit=True)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    quantization_config=bnb_config,
    device_map="auto",
)
```

### GGUF (llama.cpp format)

```python
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "org/model-gguf",
    variant="model-Q4_K_M.gguf",  # GGUF file name
    device_map="cpu",              # GGUF runs on CPU by default
)
```

### GPTQ

```python
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "TheBloke/Llama-2-7B-Chat-GPTQ",
    device_map="auto",
)
# GPTQ config is read from model's config.json automatically
```

### AWQ

```python
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "TheBloke/Llama-2-13B-AWQ",
    device_map="auto",
)
```

### Other Quantization Backends

| Backend | Config/Method | Notes |
|---------|--------------|-------|
| **HQQ** | `quantization_config={"load_in_4bit": True}` + HQQ config | High-precision quantization |
| **EETQ** | Auto-detected from model | Efficient equalized transformation |
| **Quanto** | `optimum-quanto` integration | CPU/GPU quantization |
| **torchao** | `torchao` integration | PyTorch native quantization |
| **FP8** | `quantization_config` with FP8 settings | Fine-grained FP8 |
| **AQLM** | Auto-detected | 2-bit quantization |
| **Compressed Tensors** | `compression` config | Model-specific compression |
| **SPQR** | Auto-detected | Sparse + quantized |
| **VPTQ** | Auto-detected | Per-tensor quantization |
| **MXFP4** | Auto-detected | Microsoft MXFP4 format |
| **SMoE** | Auto-detected | Sparse mixture-of-experts |

### Quantization via kwargs (shorthand)

```python
# Shorthand for bitsandbytes 4-bit
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    device_map="auto",
    quantization_config={"load_in_4bit": True},
)
```

## Model Saving

### `save_pretrained()`

```python
model.save_pretrained("./my-model-dir")

# With safe tensors (default in 5.x)
model.save_pretrained("./my-model-dir", safe_serialization=True)

# Push directly to Hub
model.push_to_hub("my-username/my-model", token="hf_...")
```

### Save Tokenizer Separately

```python
tokenizer.save_pretrained("./my-model-dir")
```

### Save Config

```python
config.save_pretrained("./my-model-dir")
```

## Model Inspection

```python
from transformers import AutoConfig, AutoModelForCausalLM

# Config inspection
config = AutoConfig.from_pretrained("meta-llama/Llama-3.1-8B")
print(config.to_dict())

# Model inspection
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-1.5B")
print(model.config)           # Full config
print(model.device)           # Current device
print(model.dtype)            # Current dtype
print(model.num_parameters()) # Total parameter count

# Module tree
for name, param in model.named_parameters():
    print(f"{name}: {param.shape} ({param.dtype})")
```

## Fusion Config

Enable kernel fusion for specific backends:

```python
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    fusion_config={
        "fuse_mlp": True,
        "fuse_attention": True,
    },
)
```

## Cache Control

```python
# Disable model caching (re-download every time)
import os
os.environ["HF_HUB_DISABLE_CACHE"] = "1"

# Custom cache directory
os.environ["HF_HOME"] = "./my-cache"

# Or pass cache_dir directly
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-1.5B",
    cache_dir="./my-cache",
)
```

## Low Memory Loading

```python
# Load weights directly to target device (skip CPU staging)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    device_map="cuda",
    dtype=torch.bfloat16,
)

# Load with mmap (memory-mapped file access)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    device_map="auto",
    disable_mmap=False,  # enable mmap for faster loading
)
```

## Variant Loading

Load specific weight files from a repo:

```python
# Load a specific GGUF variant
model = AutoModelForCausalLM.from_pretrained(
    "org/model-gguf",
    variant="model-Q4_K_M.gguf",
)

# Load a specific Safetensors shard
model = AutoModelForCausalLM.from_pretrained(
    "org/model",
    variant="model.fp16.safetensors",
)
```
