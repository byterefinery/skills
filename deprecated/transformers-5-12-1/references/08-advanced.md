# Advanced Topics Reference

## PEFT / LoRA Integration

Parameter-Efficient Fine-Tuning with Low-Rank Adaptation.

### LoRA

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, TaskType, PeftModel

# Load base model
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    device_map="auto",
    dtype=torch.bfloat16,
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B")

# Configure LoRA
lora_config = LoraConfig(
    r=16,                              # LoRA rank
    lora_alpha=32,                     # LoRA alpha
    target_modules=["q_proj", "v_proj"],  # Modules to apply LoRA
    lora_dropout=0.05,                 # Dropout
    task_type=TaskType.CAUSAL_LM,      # Task type
    bias="none",                       # Bias treatment
)

# Wrap model with PEFT
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# trainable params: 0.18% | all params: 8,032,241,664 | trainable: 14,417,920

# Train with Trainer as usual
trainer = Trainer(model=model, args=args, train_dataset=train_dataset)
trainer.train()

# Save LoRA weights only
model.save_pretrained("./lora-adapter")

# Load and merge
base_model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B")
model = PeftModel.from_pretrained(base_model, "./lora-adapter")

# Merge LoRA into base model (for inference)
model = model.merge_and_unload()
model.save_pretrained("./merged-model")
```

### QLoRA (Quantized LoRA)

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model

# 4-bit quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    quantization_config=bnb_config,
    device_map="auto",
)

# Add LoRA
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    task_type=TaskType.CAUSAL_LM,
)
model = get_peft_model(model, lora_config)
```

### Other PEFT Methods

| Method | Class | Description |
|--------|-------|-------------|
| **LoRA** | `LoraConfig` | Low-rank adaptation |
| **QLoRA** | `LoraConfig` + 4-bit | Quantized LoRA |
| **Prefix Tuning** | `PrefixTuningConfig` | Learnable prefix tokens |
| **P-Tuning v2** | `PromptTuningConfig` | Prompt tuning on all layers |
| **IA³** | `IA3Config` | Infused adapter by injective parameters |
| **Adaption Prompt** | `AdaLoRAConfig` | Adaptive rank LoRA |

## Distributed Training

### FSDP (Fully Sharded Data Parallel)

```python
from transformers import TrainingArguments, Trainer

args = TrainingArguments(
    output_dir="./results",
    fsdp="full_shard",  # "full_shard", "shard_grad_op", "no_shard"
    fsdp_config={
        "fsdp_transformer_layer_cls_to_wrap": "LlamaDecoderLayer",
        "fsdp_cpu_ram_efficient_loading": True,
        "fsdp_offload_params": False,
        "fsdp_backward_prefetch": "BACKWARD_PRE",
        "fsdp_forward_prefetch": False,
        "fsdp_use_orig_params": True,
    },
    dtype=torch.bfloat16,
)

trainer = Trainer(model=model, args=args, train_dataset=train_dataset)
trainer.train()
```

**Launch with:**
```bash
torchrun --nproc_per_node=4 train.py
# or
accelerate launch --num_processes=4 train.py
```

### DeepSpeed

```python
from transformers import Trainer, TrainingArguments

args = TrainingArguments(
    output_dir="./results",
    deepspeed="./deepspeed_config.json",
)

trainer = Trainer(model=model, args=args, train_dataset=train_dataset)
trainer.train()
```

**DeepSpeed config (`deepspeed_config.json`):**
```json
{
    "zero_optimization": {
        "stage": 3,
        "offload_optimizer": {"device": "cpu"},
        "offload_param": {"device": "cpu"},
        "contiguous_gradients": true,
        "reduce_bucket_size": "auto",
        "stage3_max_live_parameters": "auto",
        "stage3_max_reuse_distance": "auto",
        "stage3_param_persistence_threshold": "auto",
        "sub_group_size": "auto",
        "stage3_gather_16bit_weights_on_model_save": true
    },
    "bf16": {
        "enabled": true
    },
    "train_batch_size": "auto",
    "train_micro_batch_size_per_gpu": "auto",
    "gradient_accumulation_steps": "auto",
    "zero_allow_untested_optimizer": true
}
```

### DDP (Distributed Data Parallel)

```python
from transformers import TrainingArguments

args = TrainingArguments(
    output_dir="./results",
    ddp_find_unused_parameters=False,
)
```

**Launch with:**
```bash
torchrun --nproc_per_node=4 train.py
```

## Attention Implementations

| Implementation | Flag | Notes |
|---------------|------|-------|
| **SDPA** | `"sdpa"` | PyTorch scaled dot-product attention (default in 5.x) |
| **Flash Attention 2** | `"flash_attention_2"` | Fast, memory-efficient. Requires `flash_attn` package |
| **Eager** | `"eager"` | Naive attention, most compatible |

```python
from transformers import AutoModelForCausalLM

# Set at load time
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    attn_implementation="flash_attention_2",
)

# Or set on config
from transformers import AutoConfig
config = AutoConfig.from_pretrained("meta-llama/Llama-3.1-8B")
config.attn_implementation = "flash_attention_2"
model = AutoModelForCausalLM.from_config(config)
```

## Cache Systems

### DynamicCache (default)

```python
from transformers import DynamicCache

cache = DynamicCache()
# Used automatically during generate()
# Grows dynamically as tokens are generated
```

### StaticCache

For compilation and serving:

```python
from transformers import StaticCache, GenerationConfig

# Pre-allocate cache
batch_size = 4
max_cache_len = 4096
cache = StaticCache(
    config=model.config,
    max_batch_size=batch_size,
    max_cache_len=max_cache_len,
    device=model.device,
    dtype=model.dtype,
)

config = GenerationConfig(
    cache_implementation="static",
    cache_config={"max_cache_len": max_cache_len},
)
outputs = model.generate(**inputs, past_key_values=cache, generation_config=config)
```

### HybridCache

Combines static pre-allocation with dynamic growth:

```python
from transformers import GenerationConfig

config = GenerationConfig(cache_implementation="hybrid")
outputs = model.generate(**inputs, generation_config=config)
```

### OffloadedCache

Offloads KV cache to CPU when GPU memory is constrained:

```python
from transformers import GenerationConfig

config = GenerationConfig(cache_implementation="offloaded")
outputs = model.generate(**inputs, generation_config=config)
```

## Integrations

### Accelerate

```python
from accelerate import Accelerator

accelerator = Accelerator()
model, optimizer, train_dataloader = accelerator.prepare(model, optimizer, train_dataloader)

for batch in train_dataloader:
    with accelerator.accumulate(model):
        outputs = model(**batch)
        loss = outputs.loss
        accelerator.backward(loss)
        optimizer.step()
        optimizer.zero_grad()
```

### Liger Kernels

Memory-efficient attention and layer norm kernels:

```python
from transformers import AutoModelForCausalLM

# Liger kernels are applied automatically when available
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B")
```

### NEFTune

Noise Embedding for fine-tuning:

```python
from transformers import TrainingArguments

args = TrainingArguments(
    output_dir="./results",
    optim="adamw_torch",
)
# Enable NEFTune
args.neftune_noise_alpha = 5.0
```

### TorchAO

PyTorch native optimization:

```python
from torchao import int8_weight_only

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B")
model = int8_weight_only(model)
```

## CLI Tools

### `transformers-cli`

```bash
# Download model
transformers-cli download meta-llama/Llama-3.1-8B --model-cache ./models

# System info
transformers-cli env

# Serve model
transformers-cli serve --model Qwen/Qwen2.5-1.5B

# Chat with model
transformers chat Qwen/Qwen2.5-1.5B-Instruct
```

### Model Serving

```bash
# Start serving endpoint
transformers serve --model Qwen/Qwen2.5-1.5B --port 8080

# Chat interface
transformers chat Qwen/Qwen2.5-1.5B-Instruct
```

## Model Debugging

```python
from transformers import DebugUnderflowOverflow

# Debug NaN/Inf during training
debugger = DebugUnderflowOverflow(model)
trainer = Trainer(model=model, args=args, train_dataset=train_dataset)
trainer.add_callback(debugger)
```

## Gradient Checkpointing

```python
from transformers import TrainingArguments

args = TrainingArguments(
    output_dir="./results",
    gradient_checkpointing=True,
    gradient_checkpointing_kwargs={"use_reentrant": False},
)
```

## Custom Model Registration

```python
from transformers import AutoConfig, AutoModel, AutoModelForCausalLM

# Register custom model
AutoConfig.register("my_model_config", MyModelConfig)
AutoModel.register(MyModelConfig, MyModel)
AutoModelForCausalLM.register(MyModelConfig, MyModelForCausalLM)
```

## Compilation

```python
import torch

# Compile model for faster inference
model = torch.compile(model)

# Or during loading
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    torch_compile_compat=True,  # Compilation-compatible mode
)
model = torch.compile(model)
```

## Memory Optimization

```python
# Mixed precision
from transformers import TrainingArguments
args = TrainingArguments(bf16=True)  # or fp16=True

# Gradient accumulation (effective larger batch)
args = TrainingArguments(
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,  # effective batch = 32
)

# Activate offloading
from transformers import AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-70B",
    device_map="auto",
    offload_folder="./offload",
    max_memory={"0": "20GB", "1": "20GB", "cpu": "20GB"},
)
```
