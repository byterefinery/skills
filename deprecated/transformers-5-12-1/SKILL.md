---
name: transformers-5-12-1
description: >
  Hugging Face Transformers 5.12.1 — the Python library for state-of-the-art
  pretrained models. Use when working with LLMs, vision models, audio models,
  multimodal models, tokenization, text generation, fine-tuning, pipelines,
  or any NLP/CV/audio task using the transformers library. Covers AutoModel
  classes, from_pretrained, generate(), Trainer, TrainingArguments, pipeline(),
  quantization (bitsandbytes, GPTQ, AWQ, etc.), PEFT integration, distributed
  training (FSDP, DeepSpeed), cache systems, and the full 5.12 API.
  480+ model architectures including Llama, Gemma, Qwen, Mistral, DeepSeek,
  Phi, BERT, T5, CLIP, Whisper, and more. Trigger on: transformers, huggingface,
  AutoModel, AutoTokenizer, pipeline, from_pretrained, generate, Trainer,
  text-generation, fine-tuning, LoRA, PEFT, quantization, GGUF, bitsandbytes.
metadata:
  tags:
    - ml
    - nlp
    - deep-learning
    - python
---

# transformers 5.12.1

## Overview

Hugging Face Transformers 5.12.1 is the Python library for pretrained transformer models across text, vision, audio, and multimodal domains. It provides 480+ model architectures, a unified `from_pretrained`/`save_pretrained` API, the `pipeline()` high-level inference interface, the `Trainer` for PyTorch fine-tuning, and a comprehensive generation system with logits processors, streamers, and cache implementations.

**Key capabilities:**
- **Auto classes** — `AutoModel`, `AutoModelForCausalLM`, `AutoTokenizer`, `AutoConfig`, `AutoProcessor` resolve the correct class from a model ID or config
- **Model loading** — `from_pretrained()` with `device_map`, `dtype`, quantization (bitsandbytes, GGUF, GPTQ, AWQ, HQQ, etc.), and fusion configs
- **Text generation** — `model.generate()` with greedy, sample, beam search, assisted generation, continuous batching, and streaming
- **Pipelines** — `pipeline(task, model)` for 24+ tasks across text, vision, audio, and multimodal domains
- **Training** — `Trainer` + `TrainingArguments` with FSDP, DeepSpeed, gradient checkpointing, and PEFT integration
- **Tokenization** — fast (Rust) and slow (Python) tokenizers, sentencepiece, tiktoken, custom processors
- **Cache systems** — `DynamicCache`, `StaticCache`, `HybridCache`, quantized caches for KV optimization
- **Integrations** — PEFT, bitsandbytes, DeepSpeed, FSDP, Flash Attention, SDPA, Liger Kernels, torchao, GGUF

**Dependencies:** Python 3.10+, PyTorch 2.4+. Optional: `accelerate`, `peft`, `bitsandbytes`, `sentencepiece`, `tokenizers`, `datasets`, `scipy`, `librosa`, `Pillow`, `torchvision`, `torchaudio`.

## Usage

### Pipeline API (quick inference)

```python
from transformers import pipeline

# Text generation
gen = pipeline("text-generation", model="Qwen/Qwen2.5-1.5B")
gen("the secret to baking a good cake is ")

# Chat (conversational)
gen = pipeline("text-generation", model="Qwen/Qwen2.5-1.5B-Instruct")
chat = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum computing."},
]
gen(chat, max_new_tokens=256)

# Image classification
cls = pipeline("image-classification", model="facebook/dinov2-small-imagenet1k-1-layer")
cls("image.jpg")

# Speech recognition
asr = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3")
asr("audio.flac")
```

### Auto Classes (model-agnostic loading)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig

# Resolve architecture from Hub
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B")
config = AutoConfig.from_pretrained("meta-llama/Llama-3.1-8B")

# Inspect config
print(config.architectures)   # ["LlamaForCausalLM"]
print(config.hidden_size)     # 4096
print(config.num_hidden_layers)  # 32
```

### Model Loading with Device Placement and Dtype

```python
import torch
from transformers import AutoModelForCausalLM

# Auto device mapping (splits across GPUs)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    device_map="auto",
    dtype=torch.bfloat16,
)

# Manual device
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-1.5B",
    device_map="cuda:0",
    dtype=torch.float16,
)
```

### Quantized Loading

```python
# 4-bit quantization (bitsandbytes)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    device_map="auto",
    quantization_config={"load_in_4bit": True, "bnb_4bit_compute_dtype": "bfloat16"},
)

# GGUF (llama.cpp format)
model = AutoModelForCausalLM.from_pretrained(
    "org/model-gguf",
    variant="model-Q4_K_M.gguf",
    device_map="cpu",
)
```

### Text Generation

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-1.5B")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B")

inputs = tokenizer("Write a story about ", return_tensors="pt").to(model.device)

# Basic generation
outputs = model.generate(**inputs, max_new_tokens=128)
tokenizer.decode(outputs[0], skip_special_tokens=True)

# Sampling
outputs = model.generate(
    **inputs,
    max_new_tokens=256,
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
)

# With generation config
from transformers import GenerationConfig
config = GenerationConfig(max_new_tokens=256, do_sample=True, temperature=0.7)
outputs = model.generate(**inputs, generation_config=config)
```

### Training with Trainer

```python
from transformers import Trainer, TrainingArguments, AutoModelForSequenceClassification, AutoTokenizer
from datasets import load_dataset

model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

def tokenize(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128)

dataset = load_dataset("imdb").map(tokenize, batched=True)

training_args = TrainingArguments(
    output_dir="./results",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    num_train_epochs=3,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_steps=50,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    tokenizer=tokenizer,
)
trainer.train()
```

## Gotchas

- **`torch_dtype` is deprecated** — use `dtype` instead in `from_pretrained()`. The old `torch_dtype` parameter still works but emits a warning.
- **`device_map="auto"` requires `accelerate`** — install it with `pip install accelerate`. Without it, you must specify explicit device placement.
- **`generate()` returns token IDs, not text** — always decode with `tokenizer.decode()` or use `tokenizer.batch_decode()` for batches. Use `skip_special_tokens=True` to hide BOS/EOS/pad tokens.
- **`padding_side` matters for chat** — decoder-only models used for chat need `tokenizer.padding_side = "left"` so padding is on the left (past the generated tokens). The default is `"right"`.
- **`return_tensors="pt"` required for generation** — `tokenizer()` returns Python lists by default. Pass `return_tensors="pt"` to get PyTorch tensors for `model.generate()`.
- **KV cache is enabled by default in 5.x** — `DynamicCache` is used automatically during `generate()`. Set `use_cache=False` in GenerationConfig to disable (needed for gradient computation during generation).
- **`model.generate()` ignores `model.config` generation params when `generation_config` is passed** — the explicit `generation_config` takes full precedence. kwargs override both.
- **Beam search requires `num_beams > 1` AND `do_sample=False`** — if `do_sample=True` with `num_beams > 1`, you get contrastive search, not standard beam search.
- **`max_new_tokens` vs `max_length`** — `max_new_tokens` counts only generated tokens; `max_length` counts the full sequence (prompt + generated). Prefer `max_new_tokens` to avoid unexpected truncation with long prompts.
- **`trust_remote_code=True` is a security risk** — it executes arbitrary code from the Hub. Only use with models from trusted sources. Prefer models with native support.
- **Tokenizer `chat_template` is model-specific** — not all models ship with a Jinja chat template. Check `tokenizer.chat_template` is not `None` before using `apply_chat_template()`.
- **`AutoProcessor` needed for multimodal** — vision-language models (LLaVA, Idefics, etc.) need `AutoProcessor` which combines tokenizer + image processor. Don't use `AutoTokenizer` alone.
- **`pipeline()` caches models by default** — repeated calls with the same model reuse the cached instance. Use `pipeline(..., model=new_model_instance)` to force a fresh load.
- **`Trainer.compute_loss` override for custom objectives** — the default computes cross-entropy on `model_outputs.loss`. Override `compute_loss()` in a Trainer subclass for custom loss functions.
- **Gradient checkpointing trades speed for memory** — `TrainingArguments(gradient_checkpointing=True)` saves memory but slows training ~20%. Enable only when OOM.
- **`save_pretrained()` saves weights + config** — it does not save the tokenizer. Call `tokenizer.save_pretrained()` separately in the same directory.
- **`push_to_hub()` needs `huggingface_hub` login** — run `huggingface-cli login` first or pass `token="hf_..."` explicitly.
- **FSDP requires `accelerate` and `torch.distributed`** — launch with `torchrun` or `accelerate launch`. Not compatible with single-GPU training.
- **`DynamicCache` shapes differ from `use_cache=True` tuples** — in 5.x the default cache returns `past_key_values` as a `DynamicCache` object, not a tuple of tuples. Code expecting tuple shapes will break.
- **`tokenizer.apply_chat_template()` returns a string** — for generation, you still need to tokenize: `tokenizer(tokenizer.apply_chat_template(messages, tokenize=False), return_tensors="pt")`. Or pass `tokenize=True` directly.

## References

- [01-auto-classes](references/01-auto-classes.md) — AutoModel, AutoTokenizer, AutoConfig, AutoProcessor, and all Auto* variants
- [02-model-loading](references/02-model-loading.md) — from_pretrained, save_pretrained, device_map, dtype, quantization (bitsandbytes, GGUF, GPTQ, AWQ, HQQ, torchao, etc.)
- [03-generation](references/03-generation.md) — generate(), GenerationConfig, logits processors, stopping criteria, streamers, candidate generators
- [04-pipelines](references/04-pipelines.md) — pipeline() API, all 24+ supported tasks, custom pipelines
- [05-training](references/05-training.md) — Trainer, TrainingArguments, Seq2SeqTrainer, data collators, callbacks, evaluation
- [06-tokenization](references/06-tokenization.md) — tokenizers, chat templates, preprocessing, sentencepiece, tiktoken
- [07-multimodal](references/07-multimodal.md) — vision, audio, video processing, image processors, feature extractors
- [08-advanced](references/08-advanced.md) — PEFT/LoRA, distributed training (FSDP, DeepSpeed), cache systems, integrations, CLI tools
