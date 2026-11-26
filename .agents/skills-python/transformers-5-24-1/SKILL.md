---
name: transformers-5-24-1
description: >
  Hugging Face Transformers 5.24.1 — model definitions for NLP, vision, audio,
  video, and multimodal models. Use when working with pretrained models,
  pipelines, tokenizers, text generation, Trainer fine-tuning, AutoModel
  classes, quantization, model export, or serving LLMs from the Hugging Face
  Hub. Covers the v5 API — torch-only (TensorFlow and JAX removed), unified
  tokenizers, backend image processors, dynamic weight loading, the
  transformers serve/chat CLI, and the v5 breaking changes (quantization_config
  loading, removed pipelines, rope_parameters, BatchEncoding chat templates,
  Trainer processing_class and hub_token arguments). Triggers on transformers,
  pipeline, AutoModel, AutoTokenizer, from_pretrained, generate, Trainer,
  TrainingArguments, quantization_config, transformers serve, chat templates,
  Hugging Face, fine-tuning, LoRA, PEFT.
license: Apache-2.0
compatibility: >
  Python 3.11–3.14, PyTorch 2.6+. Requires huggingface-hub>=1.31.0,<3.0,
  numpy, packaging, pyyaml, regex, tokenizers>=0.23.1,<0.24.0, typer,
  safetensors>=0.8.0, tqdm. Optional extras include transformers[torch]
  (torch, accelerate), transformers[vision], transformers[audio],
  transformers[video], transformers[serving], peft, bitsandbytes, deepspeed,
  accelerate.
metadata:
  tags:
    - ml
    - deep-learning
    - nlp
    - vision
    - audio
    - python
    - huggingface
---

# transformers 5.24.1

## Overview

Transformers 5.24.1 is the model-definition framework for state-of-the-art machine learning across text, vision, audio, video, and multimodal models. v5 is torch-only — the TensorFlow and JAX implementations were removed — and it ships a rewritten weight-loading core, unified tokenizers, and an integrated serving CLI.

**Core pillars:**
- **`pipeline()`** — High-level inference API; task list shrunk in v5 (see 02-pipeline-api)
- **`AutoModel*`** — 48 auto classes resolving architecture from a model ID or config
- **`AutoTokenizer` / `AutoProcessor`** — Unified tokenization, image processing, and feature extraction
- **`PreTrainedModel.from_pretrained()`** — Load models from the Hub with `dtype="auto"` (default) and dynamic weight loading
- **`model.generate()`** — Text generation with GenerationConfig, logits processors, streamers, stopping criteria
- **`Trainer` / `TrainingArguments`** — Complete training and evaluation loop (v5 renamed many arguments)
- **Quantization** — 20+ methods via `quantization_config` (bare `load_in_4bit`/`load_in_8bit` kwargs are gone)
- **Exporters** — Dynamo, ONNX, ExecuTorch, OpenVINO exporters live inside the library
- **CLI** — `transformers serve` (OpenAI-compatible server) and `transformers chat` (terminal client)

**Key modules:**
- `transformers.pipeline` — Task-agnostic inference
- `transformers.models.auto` — AutoModel*, AutoTokenizer, AutoConfig, AutoProcessor
- `transformers.generation` — GenerationConfig, logits processors, streamers, stopping criteria, caches
- `transformers.Trainer` / `TrainingArguments` — Training infrastructure
- `transformers.data` — DataCollator variants
- `transformers.exporters` — Model export (Dynamo/ONNX/ExecuTorch/OpenVINO)
- `transformers.cli` — `transformers serve`, `transformers chat`, `transformers download`

**Hard dependencies** (from `setup.py`): `huggingface-hub>=1.31.0,<3.0`, `numpy>=1.17`, `packaging>=20.0`, `pyyaml>=5.1`, `regex>=2025.10.22`, `tokenizers>=0.23.1,<0.24.0`, `typer`, `safetensors>=0.8.0`, `tqdm>=4.60`. Note the `huggingface-hub` 1.x line — it uses `httpx`, not `requests`.

## Installation

```bash
# With PyTorch (installs torch >=2.6 and accelerate)
pip install "transformers[torch]"

# Quickstart extras recommended by the docs
pip install -U transformers datasets evaluate accelerate timm

# CPU-only PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers
```

## Usage

### Pipeline API (quick inference)

```python
from transformers import pipeline

gen = pipeline("text-generation", model="google/gemma-2-2b")
gen("the secret to baking a really good cake is ")

# Chat model — pass role/content message dicts
gen = pipeline("text-generation", model="HuggingFaceTB/SmolLM3-3B")
gen([
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum computing."},
])

# Image classification
cls = pipeline("image-classification", model="google/vit-base-patch16-224")
cls("https://example.com/image.jpg")

# Vision-language model — image embedded in the chat content
vlm = pipeline("image-text-to-text", model="HuggingFaceTB/SmolVLM-256M-Instruct")
vlm([{"role": "user", "content": [
    {"type": "image", "image": "https://example.com/photo.jpg"},
    {"type": "text", "text": "What is in the image?"},
]}], max_new_tokens=50)
```

### Model loading and generation

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf", dtype="auto", device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

inputs = tokenizer("The secret to baking a good cake is ", return_tensors="pt").to(model.device)
generated_ids = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(generated_ids, skip_special_tokens=True))
```

### Fine-tuning with Trainer

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments, DataCollatorWithPadding
from datasets import load_dataset

model = AutoModelForSequenceClassification.from_pretrained("distilbert/distilbert-base-uncased")
tokenizer = AutoTokenizer.from_pretrained("distilbert/distilbert-base-uncased")
dataset = load_dataset("cornell-movie-review-data/rotten_tomatoes").map(
    lambda batch: tokenizer(batch["text"]), batched=True
)

args = TrainingArguments(
    output_dir="distilbert-rotten-tomatoes",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    num_train_epochs=2,
    push_to_hub=True,
)
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    processing_class=tokenizer,   # v5 name; `tokenizer=` is gone
    data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
)
trainer.train()
trainer.push_to_hub()
```

See the reference files for complete detail:

- **v5 migration** — every breaking change from v4 to v5, with old→new: [01-v5-migration](references/01-v5-migration.md)
- **Pipeline API** — full v5 task list, parameters, batching: [02-pipeline-api](references/02-pipeline-api.md)
- **Auto-models** — the 48 AutoModel* classes, from_pretrained parameters: [03-auto-models](references/03-auto-models.md)
- **Tokenizers** — v5 backend architecture, unified decode, chat templates: [04-tokenizers](references/04-tokenizers.md)
- **Text generation** — GenerationConfig, decoding strategies, caches, streamers: [05-generation](references/05-generation.md)
- **Training** — Trainer, v5 TrainingArguments names, PEFT integration: [06-training](references/06-training.md)
- **Model loading & saving** — from_pretrained, save_pretrained, push_to_hub, WeightConverter: [07-model-loading](references/07-model-loading.md)
- **Quantization** — 20+ backends via quantization_config, GGUF loading: [08-quantization](references/08-quantization.md)
- **Multimodal** — backend image processors, video, AutoProcessor, VLM access: [09-multimodal](references/09-multimodal.md)
- **Exporters & CLI** — export to ONNX/Dynamo/ExecuTorch/OpenVINO, transformers serve/chat: [10-exporters-cli](references/10-exporters-cli.md)

## Gotchas

- **v5 renamed or removed many Trainer and TrainingArguments names** — `Trainer(tokenizer=...)` is gone; pass `processing_class=`. `TrainingArguments`: `push_to_hub_token`→`hub_token`, `push_to_hub_model_id`/`push_to_hub_organization`→`hub_model_id`, `warmup_ratio`→`warmup_step` (accepts float), `per_gpu_train_batch_size`→`per_device_train_batch_size`, `no_cuda`→`use_cpu`, `jit_mode_eval`→`use_torch_compile`, `fsdp_min_num_params`→`fsdp_config`, `tpu_metrics_debug`→`debug`, `include_inputs_for_metrics`→`include_for_metrics`.
- **`use_auth_token` is deprecated everywhere** — search-replace with `token`.
- **`safe_serialization=False` no longer exists** — v5 saves safetensors only; the parameter was removed from all `save_pretrained`/`push_to_hub`. To export another format, save `model.state_dict()` yourself. Default shard size is now 50GB, not 5GB.
- **Bare `load_in_4bit`/`load_in_8bit` kwargs are removed** — pass a config object: `from_pretrained(..., quantization_config=BitsAndBytesConfig(load_in_4bit=True))`.
- **Removed auto classes** — `AutoModelWithLMHead` → `AutoModelForCausalLM` (or MaskedLM/Seq2SeqLM); `AutoModelForVision2Seq` → `AutoModelForImageTextToText`.
- **Removed pipelines** — `question-answering`, `summarization`, `translation_*`, `text2text-generation`, `image-to-text`, `visual-question-answering`, and `image-to-image` are gone. Use `text-generation` with a chat model, `image-text-to-text` for VLMs, or Diffusers for image generation.
- **`apply_chat_template` returns a `BatchEncoding`** — not bare `input_ids`. Pass `return_tensors="pt"` and index `outputs["input_ids"]`, or `tokenize=False` for a string.
- **`decode` handles batches now** — `batch_decode` still exists, but `decode` unifies both (`tokenizer.decode(tokenizer.encode(batch))` returns a list).
- **`config.rope_theta` raises AttributeError on many models** — rotary parameters moved to `config.rope_parameters` (a dict, possibly nested per layer type for Gemma3/ModernBert).
- **Multimodal configs are nested** — e.g. Qwen-VL family: read `config.text_config.vocab_size`, not `config.vocab_size`. Non-generative models have no `generation_config` at all — `model.config.generation_config` raises AttributeError.
- **Trainer sets `config.use_cache=False` by default** — new v5 default; override via `TrainingArguments(use_cache=True)` if you need KV-cache behavior.
- **`dtype` is the new dtype argument** — defaults to `"auto"` (loads weights in their stored dtype, avoiding a double float32 load). `torch_dtype` still works as a backward-compat alias; `low_cpu_mem_usage` is silently ignored (popped as deprecated).
- **`use_fast` is deprecated for image processors** — use `backend="torchvision"` or `backend="pil"`. `FooImageProcessor` now means the torchvision-backed class; `*Fast` names emit deprecation warnings; `processor.is_fast` → `processor.backend == "torchvision"`.
- **`XXXFeatureExtractors` classes are removed** — use the `XXXImageProcessor` for all vision models.
- **`get_text_features`/`get_image_features`/`get_audio_features`/`get_video_features` return a `BaseModelOutputWithPooling`** — where v4 returned a tensor. Use `outputs.pooler_output` for the old behavior.
- **VLM component access changed** — `model.language_model` shortcut is gone on vision-language models; use `model.model.language_model` or `model.get_decoder()`.
- **Generation parameters live only in `model.generation_config`** — not on `model.config` anymore (old values in `config.json` are loaded back into the generation config automatically).
- **Default cache class is model-defined** — when `generate()` gets no KV-cache argument, the model's default cache is used, not always `DynamicCache`.
- **PushToHubMixin API is stricter** — `push_to_hub` arguments are keyword-only (only `repo_id` is positional), `**kwargs` are no longer accepted, and `use_temp_dir` was removed. `repo_id` is required (no more `organization`/`repo_url`).
- **CLI split** — `transformers-cli` is deprecated in favor of `transformers`. `transformers run` was removed. `transformers chat` is now only a terminal UI client; the server is `transformers serve` (OpenAI-compatible, default http://localhost:8000, needs `pip install transformers[serving]`).
- **Legacy env vars removed** — `TRANSFORMERS_CACHE` and friends are gone; use `HF_HOME`.
- **huggingface-hub 1.x uses httpx** — catch `httpx.HTTPError`, not `requests.HTTPError`; `hf_transfer`/`HF_HUB_ENABLE_HF_TRANSFER` replaced by `hf_xet`.
- **`generate()` is short by default** — it produces up to 20 new tokens by default unless the model's GenerationConfig says otherwise; always set `max_new_tokens` explicitly.
- **Set `padding_side="left"` for batched LLM generation** — LLMs are not trained to continue from pad tokens; set `tokenizer.pad_token` (e.g. to `eos_token`) before padding.
- **Chat models need the chat template** — pass role/content dicts through `apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt")`. `tokenize=True` is safer because it avoids double-adding special tokens.
- **`encode_plus` is deprecated** — use `tokenizer(...)` (`__call__`). For encoder-decoder labels use `tokenizer(src, text_target=tgt)` instead of the removed `as_target_tokenizer` / `prepare_seq2seq_batch`.
- **Special tokens were restructured** — `special_tokens_map` now holds only named tokens; use `extra_special_tokens` (not `additional_special_tokens`). `special_tokens_map.json` and `added_tokens.json` are no longer written.
- **The repo no longer ships task fine-tuning example scripts** — `examples/` in v5 contains only generate (continuous batching), quantization, and scheduler; follow the docs training tutorials (Trainer) instead of old `examples/pytorch/...` scripts.
- **`trust_remote_code=True` executes arbitrary code from the Hub** — the pipeline and from_pretrained accept it; only enable it for models you trust, and note v5 removed many old remote-code paths (`transformers.tokenization_utils*` no longer exist).
- **`device_map="auto"` requires accelerate** — included in `transformers[torch]`, but if you installed bare transformers, install accelerate first.

## References

- [01-v5-migration](references/01-v5-migration.md) — v4→v5 breaking changes: tokenization, config, processing, modeling, generation, Trainer, pipelines, CLI, env vars
- [02-pipeline-api](references/02-pipeline-api.md) — Full v5 pipeline task list, parameters, batch inference, streaming, removed tasks
- [03-auto-models](references/03-auto-models.md) — The 48 AutoModel* classes, AutoConfig, from_pretrained parameters, removed auto classes
- [04-tokenizers](references/04-tokenizers.md) — v5 tokenizer backends, unified decode, chat templates, special tokens, text_target
- [05-generation](references/05-generation.md) — generate(), GenerationConfig, decoding strategies, caches, streamers, logits processors
- [06-training](references/06-training.md) — Trainer, v5 TrainingArguments, data collators, callbacks, PEFT via add_adapter
- [07-model-loading](references/07-model-loading.md) — from_pretrained, save_pretrained, push_to_hub, dynamic weight loading (WeightConverter), GGUF
- [08-quantization](references/08-quantization.md) — Quantize-on-load vs pre-quantized checkpoints, all backends, GGUF, memory rules
- [09-multimodal](references/09-multimodal.md) — backend image/video processors, AutoProcessor, multimodal chat templates, VLM module access
- [10-exporters-cli](references/10-exporters-cli.md) — Dynamo/ONNX/ExecuTorch/OpenVINO exporters, transformers serve/chat CLI, OpenAI-compatible endpoints
