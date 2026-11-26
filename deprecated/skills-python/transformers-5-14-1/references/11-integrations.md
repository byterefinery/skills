# Integrations

Transformers integrates with PEFT, DeepSpeed, FSDP, vLLM, TRL, and other frameworks for efficient training and inference.

## PEFT (Parameter-Efficient Fine-Tuning)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, TaskType

model = AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-3-8B")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")

# LoRA config
lora_config = LoraConfig(
    r=16,                          # Rank
    lora_alpha=32,                 # Scaling factor
    lora_dropout=0.05,             # Dropout
    target_modules=["q_proj", "v_proj"],  # Layers to apply LoRA
    task_type=TaskType.CAUSAL_LM,
)

# Apply LoRA
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# trainable params: ~0.04% of total

# Train with Trainer
from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
    output_dir="./lora-results",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    logging_steps=10,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

trainer.train()

# Save LoRA weights
model.save_pretrained("./lora-adapter")
tokenizer.save_pretrained("./lora-adapter")
```

### Loading LoRA Weights

```python
from peft import PeftModel, PeftConfig

# Load base model
base_model = AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-3-8B")

# Load LoRA adapter
model = PeftModel.from_pretrained(base_model, "./lora-adapter")

# Merge weights into base model (optional)
model = model.merge_and_unload()
model.save_pretrained("./merged-model")
```

### QLoRA (Quantized LoRA)

```python
from transformers import BitsAndBytesConfig, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model

# 4-bit quantization
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B",
    quantization_config=bnb_config,
    device_map="auto",
)

# Add LoRA
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    task_type=TaskType.CAUSAL_LM,
)

model = get_peft_model(model, lora_config)
```

### PEFT Methods

| Method | Description | Memory Savings |
|---|---|---|
| LoRA | Low-rank adaptation of attention weights | ~99% |
| QLoRA | LoRA + 4-bit quantization | ~99.5% |
| Prefix Tuning | Learnable prefix tokens | ~95% |
| P-Tuning v2 | Embedded prefix tokens | ~95% |
| AdaLoRA | Adaptive rank allocation | ~99% |
| IA³ | Input/output attention activation | ~99% |

## DeepSpeed

```python
from transformers import Trainer, TrainingArguments, DeepSpeedSchedulerWrapper

training_args = TrainingArguments(
    output_dir="./results",
    deepspeed="./deepspeed_config.json",  # DeepSpeed config file
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    learning_rate=2e-5,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

trainer.train()
```

### DeepSpeed Config (ZeRO-3)

```json
{
    "zero_optimization": {
        "stage": 3,
        "offload_optimizer": {
            "device": "cpu",
            "pin_memory": true
        },
        "offload_param": {
            "device": "cpu",
            "pin_memory": true
        },
        "overlap_comm": true,
        "contiguous_gradients": true,
        "reduce_bucket_size": 5e8,
        "stage3_max_live_parameters": 1e9,
        "stage3_prefetch_bucket_size": 5e8,
        "stage3_param_persistence_threshold": 1e6,
        "sub_group_size": 1e12,
        "stage3_gather_16bit_weights_on_model_save": true
    },
    "bf16": {
        "enabled": true
    },
    "train_micro_batch_size_per_gpu": "auto",
    "gradient_accumulation_steps": "auto",
    "scheduler": {
        "type": "WarmupLR",
        "params": {
            "warmup_min_lr": 0,
            "warmup_max_lr": 2e-5,
            "warmup_num_steps": 0
        }
    }
}
```

## FSDP (Fully Sharded Data Parallel)

```python
from transformers import Trainer, TrainingArguments
from torch.distributed.fsdp import ShardingStrategy, FullStateDictConfig, StateDictType

training_args = TrainingArguments(
    output_dir="./results",
    fsdp=["FULL_SHARD", "AUTO_WRAP", "OFFLOAD"],  # FSDP options
    fsdp_config={
        "backward_prefetch": "BACKWARD_PRE",
        "forward_prefetch": "true",
        "limit_all_gathers": "true",
        "use_orig_params": "false",
    },
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    learning_rate=2e-5,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

trainer.train()
```

### FSDP Sharding Strategies

| Strategy | Description |
|---|---|
| `FULL_SHARD` | Shard parameters, gradients, and optimizer states |
| `SHARD_GRAD_OP` | Shard gradients and optimizer states only |
| `NO_SHARD` | No sharding (equivalent to DDP) |
| `HYBRID_SHARD` | Hybrid sharding within a node |

## vLLM

vLLM is a high-throughput inference engine. Transformers models are compatible via the Hub.

```python
from vllm import LLM, SamplingParams

# Load model
llm = LLM(model="meta-llama/Meta-Llama-3-8B", tensor_parallel_size=1)

# Sampling params
sampling_params = SamplingParams(
    temperature=0.8,
    top_p=0.95,
    max_tokens=512,
)

# Generate
outputs = llm.generate(
    prompts=["Hello, how are you?", "What is Python?"],
    sampling_params=sampling_params,
)

for output in outputs:
    print(output.outputs[0].text)
```

### vLLM Engine

```python
from vllm import AsyncLLMEngine, EngineArgs

engine_args = EngineArgs(
    model="meta-llama/Meta-Llama-3-8B",
    tensor_parallel_size=4,
    gpu_memory_utilization=0.9,
    max_model_len=4096,
)

engine = AsyncLLMEngine.from_engine_args(engine_args)

# Streaming
async def generate(prompt):
    sampling_params = SamplingParams(temperature=0.8, max_tokens=512)
    results_generator = engine.generate(prompt, sampling_params, "req-1")
    async for output in results_generator:
        yield output.outputs[0].text
```

## TRL (Transformer Reinforcement Learning)

```python
from trl import SFTTrainer, SFTConfig
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-3-8B")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")

# Supervised Fine-Tuning
training_args = SFTConfig(
    output_dir="./sft-results",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    learning_rate=2e-5,
    logging_steps=10,
    packing=True,  # Pack multiple samples
    max_seq_length=2048,
)

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    tokenizer=tokenizer,
)

trainer.train()
```

### DPO (Direct Preference Optimization)

```python
from trl import DPOTrainer, DPOConfig

dpo_args = DPOConfig(
    output_dir="./dpo-results",
    per_device_train_batch_size=4,
    learning_rate=5e-7,
    beta=0.1,  # Preference strength
    max_prompt_length=512,
    max_completion_length=256,
)

dpo_trainer = DPOTrainer(
    model=model,
    ref_model=ref_model,  # Reference model (original)
    args=dpo_args,
    train_dataset=preference_dataset,
    tokenizer=tokenizer,
)

dpo_trainer.train()
```

## Axolotl

Axolotl is a training orchestrator that uses Transformers internally.

```yaml
# axolotl_config.yaml
base_model: meta-llama/Meta-Llama-3-8B
model_type: AutoModelForCausalLM
tokenizer_type: AutoTokenizer

load_in_4bit: true
lora_model_dir: null
lora_r: 16
lora_alpha: 16
lora_dropout: 0.05
lora_target_modules:
  - q_proj
  - v_proj

gradient_accumulation_steps: 4
micro_batch_size: 2
num_epochs: 3
learning_rate: 2.0e-4
lr_scheduler: cosine

cutoff_len: 2048
sample_packing: true
```

```bash
axolotl train axolotl_config.yaml
```

## Gotchas

- **`PEFT` requires `peft` package** — install with `pip install peft`.
- **`DeepSpeed` requires `deepspeed` package** — install with `pip install deepspeed`. May need compilation.
- **`FSDP` requires PyTorch >= 2.0** — use `torch.distributed.run` to launch.
- **`vLLM` is inference-only** — not for training. Use for high-throughput serving.
- **`TRL` requires `trl` package** — install with `pip install trl`.
- **LoRA `target_modules` must match model** — check model architecture for layer names. Common: `["q_proj", "v_proj"]` or `["q_proj", "k_proj", "v_proj", "o_proj"]`.
- **`merge_and_unload` for deployment** — merge LoRA weights into base model before deployment for single-model serving.
- **`bnb_config` with PEFT** — quantization config goes to `from_pretrained()`, not to PEFT.
- **`DeepSpeed ZeRO-3` vs FSDP** — both shard model states. ZeRO-3 is DeepSpeed-specific; FSDP is native PyTorch.
- **`gradient_accumulation_steps` with PEFT** — effective batch size = `per_device × num_gpus × accumulation_steps`.
- **`SFTTrainer` packing** — `packing=True` concatenates short samples into one sequence. More efficient but changes training dynamics.
- **`DPO beta` parameter** — controls preference strength. Higher beta = stronger preference alignment. Typical: 0.1.
- **`vLLM tensor_parallel_size`** — number of GPUs for model parallelism. Must divide the model evenly.
- **`Axolotl` uses YAML configs** — all training parameters in a single YAML file. Supports LoRA, QLoRA, GaLore, BnB.
- **`PEFT` with multiple adapters** — use `model.add_adapter()` and `model.set_adapter()` to switch between adapters.
- **`offload` in DeepSpeed/FSDP** — CPU offloading saves GPU memory but adds CPU-GPU transfer overhead.
- **`trl` dataset format** — SFT expects `{"text": "..."}` or `{"messages": [...]}`. DPO expects `{"prompt", "chosen", "rejected"}`.
- **`vLLM` quantization** — supports AWQ, GPTQ, SqueezeLLM natively. Pass `quantization="awq"` to `LLM()`.
- **`PEFT` saving** — only saves adapter weights (~MBs), not the full model. Base model is referenced by ID.
- **`DeepSpeed` checkpoint format** — uses DeepSpeed-specific format. Convert with `deepspeed.utils.save_fsdp_model()` if needed.
