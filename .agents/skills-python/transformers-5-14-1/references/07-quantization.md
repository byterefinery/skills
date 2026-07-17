# Quantization

Transformers 5.14.1 supports multiple quantization backends for reduced memory usage and faster inference. Quantization reduces model precision from FP16/FP32 to lower-bit representations.

## bitsandbytes (4-bit and 8-bit)

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch

# 4-bit quantization (NF4)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",           # Normalized Float4
    bnb_4bit_compute_dtype=torch.bfloat16,  # Compute dtype
    bnb_4bit_use_double_quant=True,      # Double quantization for scales
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B",
    quantization_config=bnb_config,
    device_map="auto",
)

# 8-bit quantization
bnb_config = BitsAndBytesConfig(
    load_in_8bit=True,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B",
    quantization_config=bnb_config,
    device_map="auto",
)
```

### bitsandbytes Config Options

| Parameter | Type | Default | Description |
|---|---|---|---|
| `load_in_4bit` | bool | False | Enable 4-bit quantization |
| `load_in_8bit` | bool | False | Enable 8-bit quantization |
| `bnb_4bit_quant_type` | str | "nf4" | "nf4" or "fp4" |
| `bnb_4bit_compute_dtype` | torch.dtype | torch.float32 | Dtype for computations |
| `bnb_4bit_use_double_quant` | bool | False | Quantize quantization constants |
| `bnb_4bit_quant_storage` | torch.dtype | torch.uint8 | Storage dtype for quantized weights |

## GPTQ

```python
from transformers import AutoModelForCausalLM, GPTQConfig

quantization_config = GPTQConfig(
    bits=4,                          # 4-bit or 8-bit
    group_size=128,                  # Group size for quantization
    damp_percent=0.01,              # Damping percentage
    desc_act=False,                  # Descending activation (slower, more accurate)
    sym=True,                        # Symmetric quantization
)

model = AutoModelForCausalLM.from_pretrained(
    "model-gptq",
    quantization_config=quantization_config,
    device_map="auto",
)

# Or load pre-quantized GPTQ model
model = AutoModelForCausalLM.from_pretrained(
    "TheBloke/Llama-2-7B-GPTQ",
    device_map="auto",
)
```

## AWQ

```python
from transformers import AutoModelForCausalLM, AwqConfig

quantization_config = AwqConfig(
    bits=4,
    group_size=128,
)

model = AutoModelForCausalLM.from_pretrained(
    "model-awq",
    quantization_config=quantization_config,
    device_map="auto",
)

# Or load pre-quantized AWQ model
model = AutoModelForCausalLM.from_pretrained(
    "TheBloke/Llama-2-7B-AWQ",
    device_map="auto",
)
```

## FP8

```python
from transformers import AutoModelForCausalLM

# Load with FP8 (requires compatible hardware)
model = AutoModelForCausalLM.from_pretrained(
    "model",
    torch_dtype=torch.float8_e4m3fn,  # FP8 dtype
    device_map="auto",
)
```

## Available Quantization Backends

| Backend | Bits | Hardware | Speed | Quality |
|---|---|---|---|---|
| bitsandbytes (NF4) | 4 | GPU (CUDA) | Fast | Good |
| bitsandbytes (LLM.int8) | 8 | GPU (CUDA) | Fast | Very good |
| GPTQ | 4, 8 | GPU | Very fast | Good |
| AWQ | 4 | GPU | Very fast | Good |
| AQLM | 2, 4, 8 | GPU | Fast | Varies |
| HQQ | 4, 8 | GPU/CPU | Fast | Good |
| EETQ | 1-8 | GPU | Fast | Varies |
| Quanto | 4, 8 | GPU/CPU | Fast | Good |
| TorchAO | 4, 8 | GPU | Fast | Good |
| Compressed Tensors | 4, 8 | GPU | Fast | Good |
| SparQ | 4, 8 | GPU | Fast | Good |
| SqueezeLLM (SINQ) | 4, 8 | GPU | Fast | Good |

## QLoRA (Quantized LoRA)

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig, Trainer, TrainingArguments
from peft import LoraConfig, get_peft_model

# 4-bit base model
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

# Add LoRA adapters
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "v_proj"],
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# Train with Trainer
training_args = TrainingArguments(
    output_dir="./qlora-results",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    optim="adamw_torch",
    logging_steps=10,
    save_strategy="steps",
    save_steps=500,
    fp16=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

trainer.train()

# Save LoRA weights only
model.save_pretrained("./qlora-adapter")
```

## Checking Quantization

```python
# Check if model is quantized
print(model.config.quantization_config)

# Check quantization type
if hasattr(model, "is_quantized"):
    print(f"Quantized: {model.is_quantized}")

# Check bit depth
if hasattr(model.config, "quantization_method"):
    print(f"Method: {model.config.quantization_method}")

# Check compute dtype
if hasattr(model.config, "quantization_config"):
    config = model.config.quantization_config
    if hasattr(config, "bnb_4bit_compute_dtype"):
        print(f"Compute dtype: {config.bnb_4bit_compute_dtype}")
```

## Quantization-Aware Training (QAT)

```python
# Note: Transformers focuses on post-training quantization (PTQ).
# For QAT, use torch.ao.quantization or framework-specific tools.

# Export quantized model for deployment
model.save_pretrained("./quantized-model")
```

## Gotchas

- **`bitsandbytes` requires CUDA** — 4-bit and 8-bit quantization via bitsandbytes only works on NVIDIA GPUs. No CPU support.
- **`bnb_4bit_compute_dtype` should match training dtype** — use `torch.bfloat16` for Ampere+ GPUs, `torch.float16` for older GPUs. Mismatch causes precision loss.
- **`bnb_4bit_use_double_quant` saves memory** — quantizes the quantization constants themselves. Use for maximum memory savings, slight quality trade-off.
- **`GPTQ` and `AWQ` are post-training** — the model is quantized once, then the quantized weights are loaded. You don't quantize at load time (unless using auto-round).
- **`quantization_config` as keyword arg** — pass as `quantization_config=bnb_config`, not inside `model_kwargs`.
- **`load_in_4bit`/`load_in_8bit` deprecated** — use `BitsAndBytesConfig` instead of direct kwargs.
- **Quantized models can't be fine-tuned natively** — use QLoRA (PEFT + 4-bit) for efficient fine-tuning of quantized models.
- **`device_map="auto"` with quantization** — required for bitsandbytes. The quantizer handles device placement.
- **Generation speed varies by backend** — GPTQ and AWQ are typically fastest for inference. bitsandbytes is slower but more flexible.
- **Quantized models use less VRAM** — 4-bit reduces memory by ~4x vs FP16. An 8B model goes from ~16GB to ~4-5GB.
- **Quality degradation** — 4-bit can cause quality loss on complex reasoning tasks. 8-bit is nearly lossless for most tasks.
- **`torch.float8_e4m3fn` requires Hopper+** — native FP8 support requires H100+ GPUs. Use quantization backends for older hardware.
- **Mixed precision with quantization** — the compute dtype (`bnb_4bit_compute_dtype`) determines the precision of activations. Weights stay quantized.
- **`peft` with quantization** — LoRA adapters are stored in full precision. Only the base model is quantized.
- **Saving quantized models** — `save_pretrained()` saves the quantized weights. To save de-quantized weights, use `model.config.quantization_config = None` before saving (requires enough memory).
- **`AutoRound` for automatic quantization** — use `AutoRoundConfig` for automated GPTQ-style quantization without a calibration dataset.
- **Quantization and `torch.compile`** — compatibility varies. Test with `torch._dynamo.explain()` to check for fallbacks.
