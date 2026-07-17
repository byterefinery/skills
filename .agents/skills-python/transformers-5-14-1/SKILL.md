---
name: transformers-5-14-1
description: >
  Hugging Face Transformers 5.14.1 — state-of-the-art model definitions for
  NLP, vision, audio, video, and multimodal models. Use when working with
  pretrained models, pipelines, tokenizers, generation, Trainer API, AutoModel
  classes, model fine-tuning, quantization, ONNX export, or any task involving
  transformer-based models from the Hugging Face Hub. Covers pipeline inference,
  model loading via from_pretrained, text generation with GenerationConfig,
  training with Trainer/TrainingArguments, tokenization, image processing,
  feature extraction, and integration with PEFT, DeepSpeed, FSDP, vLLM, and
  other frameworks. Trigger on: transformers, pipeline, AutoModel, AutoTokenizer,
  from_pretrained, generate, Trainer, tokenization, Hugging Face, pretrained
  model, fine-tuning, text-generation, image-classification, speech-recognition,
  quantization, ONNX export.
license: Apache-2.0
compatibility: >
  Python 3.10–3.14, PyTorch 2.4+. Requires huggingface-hub>=1.5.0,<2.0,
  numpy, Pillow, jinja2, accelerate>=1.1.0. Optional: torch, torchvision,
  torchaudio, datasets, peft, deepspeed, trl, optimum.
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

# transformers 5.14.1

## Overview

Transformers 5.14.1 is the model-definition framework for state-of-the-art machine learning across text, vision, audio, video, and multimodal modalities. It acts as the pivot across the ML ecosystem — model definitions here are compatible with training frameworks (Axolotl, Unsloth, DeepSpeed, FSDP, PyTorch-Lightning), inference engines (vLLM, SGLang, TGI), and adjacent libraries (llama.cpp, mlx).

**Core pillars:**
- **`pipeline()`** — High-level inference API for 30+ tasks (text generation, classification, image classification, ASR, etc.)
- **`AutoModel*`** — Auto-model classes that resolve the correct architecture from a model ID or config
- **`AutoTokenizer` / `AutoProcessor`** — Unified tokenization, image processing, and feature extraction
- **`PreTrainedModel.from_pretrained()`** — Load models from the Hub with automatic config resolution
- **`model.generate()`** — Text generation with configurable decoding strategies, logits processors, and streamers
- **`Trainer`** — Feature-complete training loop with evaluation, callbacks, mixed precision, and distributed support
- **`GenerationConfig`** — Control decoding parameters (temperature, top-p, top-k, repetition penalty, etc.)
- **Quantization** — Support for bitsandbytes (4/8-bit), GPTQ, AWQ, AQLM, HQQ, EETQ, FP8, and more
- **Exporters** — ONNX, TorchScript, ExecuTorch export pipelines

**Key modules:**
- `transformers.pipeline` — Task-agnostic inference
- `transformers.models.auto` — AutoModel, AutoTokenizer, AutoConfig, AutoProcessor
- `transformers.generation` — GenerationConfig, logits processors, streamers, stopping criteria
- `transformers.Trainer` / `TrainingArguments` — Training infrastructure
- `transformers.data` — DataCollator variants for different tasks
- `transformers.quantizers` — Quantization backends
- `transformers.exporters` — Model export (ONNX, TorchScript, ExecuTorch)
- `transformers.cli` — CLI tools (`transformers serve`, `transformers chat`)

**Dependencies:** `huggingface-hub>=1.5.0,<2.0`, `numpy>=1.17`, `Pillow>=10.0.1,<=15.0`, `jinja2>=3.1.0`, `accelerate>=1.1.0`, `packaging>=20.0`, `pyyaml>=5.1`, `regex`, `requests`, `safetensors>=0.1.2`, `tokenizers>=0.21`. Optional: `torch>=2.4`, `torchvision`, `torchaudio`, `datasets`, `scipy`, `sentencepiece`, `protobuf`, `phonemizer`, `librosa`, `opencv-python`.

## Installation

```bash
# Core + PyTorch
pip install "transformers[torch]"

# With training dependencies
pip install "transformers[torch,training]"

# From source
git clone --branch v5.14.1 https://github.com/huggingface/transformers.git
cd transformers
pip install '.[torch]'
```

**Rule:** Always pin or constrain the version when reproducibility matters. Transformers 5.x has significant API changes from 4.x.

## Usage

### Pipeline API (quick inference)

```python
from transformers import pipeline

# Text generation
gen = pipeline("text-generation", model="Qwen/Qwen2.5-1.5B")
gen("the secret to baking a good cake is ")

# Chat
gen = pipeline("text-generation", model="meta-llama/Meta-Llama-3-8B-Instruct")
gen([
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Explain quantum computing."},
])

# Image classification
cls = pipeline("image-classification", model="facebook/dinov2-small-imagenet1k-1-layer")
cls("https://example.com/image.jpg")

# Speech recognition
asr = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3")
asr("audio.flac")
```

### Model loading and inference

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-1.5B")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B")

inputs = tokenizer("Hello, how are you?", return_tensors="pt")
outputs = model(**inputs)
logits = outputs.logits  # (batch, seq_len, vocab_size)

# Generation
generated = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(generated[0], skip_special_tokens=True))
```

See the reference files for complete code examples:

- **Pipeline API** — all supported tasks, batch inference, device placement: [01-pipeline-api](references/01-pipeline-api.md)
- **Auto-models** — AutoModel classes, AutoConfig, model resolution: [02-auto-models](references/02-auto-models.md)
- **Tokenizers** — encoding, batching, chat templates, special tokens: [03-tokenizers](references/03-tokenizers.md)
- **Text generation** — GenerationConfig, logits processors, streamers, stopping criteria: [04-generation](references/04-generation.md)
- **Training** — Trainer, TrainingArguments, DataCollators, callbacks: [05-training](references/05-training.md)
- **Model loading & saving** — from_pretrained, save_pretrained, push_to_hub, device mapping: [06-model-loading](references/06-model-loading.md)
- **Quantization** — bitsandbytes, GPTQ, AWQ, FP8, and other backends: [07-quantization](references/07-quantization.md)
- **Exporters** — ONNX, TorchScript, ExecuTorch: [08-exporters](references/08-exporters.md)
- **Configuration** — PreTrainedConfig, model configs, custom architectures: [09-configuration](references/09-configuration.md)
- **Multimodal** — image processing, feature extraction, processors: [10-multimodal](references/10-multimodal.md)
- **Integrations** — PEFT, DeepSpeed, FSDP, vLLM, TRL: [11-integrations](references/11-integrations.md)

## Gotchas

- **`pipeline()` caches models** — calling `pipeline()` with the same model ID reuses the cached instance. Use `pipeline(model=None)` or reload with a different variable to get a fresh instance.
- **`from_pretrained()` downloads on first call** — models are cached in `~/.cache/huggingface/hub`. Set `HF_HOME` to change the cache location. Use `low_cpu_mem_usage=True` (default) to reduce peak memory during loading.
- **`model.generate()` expects `input_ids`** — always pass tokenizer output with `return_tensors="pt"` (or `"tf"`/`"np"`). Passing raw strings or lists of integers directly causes silent failures.
- **`max_new_tokens` vs `max_length`** — `max_new_tokens` controls how many tokens to generate beyond the input. `max_length` controls total sequence length (input + output). Prefer `max_new_tokens` for predictable output length.
- **`do_sample=True` requires `temperature`** — when sampling is enabled, temperature defaults to 1.0. Set explicitly to control randomness. Combine with `top_p` (nucleus sampling) or `top_k` for better quality.
- **`pad_token` must be set for batching** — many models lack a default pad token. Set `tokenizer.pad_token = tokenizer.eos_token` or `tokenizer.add_special_tokens({"pad_token": "[PAD]"})` before batching. After adding, resize model embeddings: `model.resize_token_embeddings(len(tokenizer))`.
- **`device_map="auto"` needs `accelerate`** — automatic device placement requires `accelerate` installed. Without it, use `.to("cuda")` manually.
- **`Trainer` wraps the model** — after `Trainer` initialization, `trainer.model` may be wrapped (DDP, DeepSpeed, etc.). Access unwrapped model via `trainer.model.module` (DDP) or `trainer.model_wrapped`.
- **`TrainingArguments.output_dir` is mandatory** — always set explicitly. Default creates `tmp_trainer` in cwd which is lost on exit.
- **`per_device_train_batch_size` vs global batch size** — the actual global batch size is `per_device_train_batch_size * num_gpus * gradient_accumulation_steps`. Tune `gradient_accumulation_steps` to simulate larger batches.
- **`remove_unused_columns=True` by default** — Trainer drops columns not in model's `forward()` signature. Set to `False` if your custom forward needs extra columns.
- **`tokenizer.apply_chat_template()` needs `tokenize=True`** — for generation, pass `tokenize=True, add_generation_prompt=True`. For display, use `tokenize=False`.
- **`chat_template` varies by model** — not all models have a chat template. Check with `tokenizer.chat_template`. For models without one, define manually or use the `<|user|>`/`<|assistant|>` pattern.
- **`safetensors` is default format** — models saved with `save_pretrained()` use safetensors by default. Use `safe_serialization=False` to save as `.bin` (pickle) if needed for compatibility with older tools.
- **`generation_config` vs `generate()` kwargs** — kwargs passed to `generate()` override the model's `generation_config`. The model's config is loaded from `generation_config.json` on the Hub.
- **`repetition_penalty` applies to all tokens** — including input tokens. Values > 1.0 penalize repetition; values < 1.0 encourage it. Default is 1.0 (no effect).
- **`eos_token_id` stops generation** — if the model generates the EOS token, generation stops. Multiple EOS tokens can be set: `model.generation_config.eos_token_id = [eos1, eos2]`.
- **`Trainer.compute_metrics` receives numpy arrays** — not tensors. Convert back to tensors if needed: `torch.tensor(predictions.predictions)`.
- **`DataCollatorWithPadding` needs `pad_token`** — will fail silently or crash if the tokenizer has no pad token. Always set pad token before creating the collator.
- **`push_to_hub` requires authentication** — call `huggingface-cli login` or pass `token="hf_..."` directly. Token must have write access to the target repo.
- **`bitsandbytes` 4-bit requires NF4** — use `bnb_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4")`. LLM.int8() uses 8-bit.
- **`quantization_config` in `from_pretrained()`** — pass quantization config as `quantization_config=bnb_config` keyword argument, not inside `model_kwargs`.
- **`TextStreamer` works with `generate()`** — pass `streamer=TextStreamer(tokenizer)` to `generate()` for real-time output. Incompatible with `return_dict_in_generate=True` in some versions.
- **`model.eval()` is needed for inference** — even after loading, call `model.eval()` to disable dropout and set batch norm to evaluation mode. `pipeline()` does this automatically.
- **Flash Attention requires compatible hardware** — Flash Attention 2 requires Ampere+ GPUs (RTX 30xx+). Flash Attention 3 requires Hopper (H100+). Check with `is_flash_attn_2_available()`.
- **`trust_remote_code=True` is a security risk** — only use for models you trust. It executes arbitrary code from the Hub. Prefer models with native support.
- **`AutoProcessor` for multimodal** — use `AutoProcessor` instead of separate tokenizer + image processor for models like LLaVA, Qwen2-VL, IDEFICS. It handles both text and image inputs.
- **`pipeline` batch inference** — pass a list of inputs for batch processing. Set `batch_size` parameter for controlled batching. Not all pipelines support batching.
- **`torch.compile` compatibility** — some transformer models compile cleanly, others have fallbacks. Use `torch._dynamo.explain(model.forward)` to check.
- **`gradient_checkpointing` trades speed for memory** — enables activation recomputation to save memory at ~20% speed cost. Enable via `model.config.use_cache = False` and `model.gradient_checkpointing_enable()`.
- **`num_labels` mismatch** — when fine-tuning for classification, `num_labels` in config must match your task. Mismatch causes embedding size errors. Override on load: `AutoModelForSequenceClassification.from_pretrained(name, num_labels=3)`.
- **`return_dict=True` is default** — `model()` returns a dataclass (e.g., `CausalLMOutputWithPast`). Access via `.logits`, `.past_key_values`. Set `return_dict=False` for tuple output (slightly faster).
- **`past_key_values` for incremental generation** — `generate()` uses past key values internally. For manual incremental decoding, capture `outputs.past_key_values` and pass to next forward pass.
- **`tokenizer.model_max_length`** — some tokenizers have hardcoded max lengths. Override with `tokenizer.model_max_length = int(1e30)` if needed, but respect the model's actual context window.

## References

- [01-pipeline-api](references/01-pipeline-api.md) — Pipeline class, all supported tasks, batch inference, device placement
- [02-auto-models](references/02-auto-models.md) — AutoModel classes, AutoConfig, model resolution, task mapping
- [03-tokenizers](references/03-tokenizers.md) — Tokenizer API, encoding, batching, chat templates, special tokens
- [04-generation](references/04-generation.md) — GenerationConfig, logits processors/warpers, streamers, stopping criteria
- [05-training](references/05-training.md) — Trainer, TrainingArguments, DataCollators, callbacks, evaluation
- [06-model-loading](references/06-model-loading.md) — from_pretrained, save_pretrained, push_to_hub, device mapping, offloading
- [07-quantization](references/07-quantization.md) — bitsandbytes (4/8-bit), GPTQ, AWQ, FP8, and other quantization backends
- [08-exporters](references/08-exporters.md) — ONNX export, TorchScript, ExecuTorch
- [09-configuration](references/09-configuration.md) — PreTrainedConfig, model configs, custom architectures, config inheritance
- [10-multimodal](references/10-multimodal.md) — Image processors, feature extractors, AutoProcessor, multimodal pipelines
- [11-integrations](references/11-integrations.md) — PEFT (LoRA, QLoRA), DeepSpeed, FSDP, vLLM, TRL, Axolotl
