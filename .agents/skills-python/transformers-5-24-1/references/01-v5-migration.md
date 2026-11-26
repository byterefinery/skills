# v5 Migration Guide (v4 → v5.24.1)

Condensed from the repository's `MIGRATION_GUIDE_V5.md` plus the v5.24.1 source tree. Read this when porting v4 code or when a v4-era tutorial example fails.

## Library-wide

- **TensorFlow and JAX removed** — transformers is torch-only. `from_tf`/`from_flax` loading paths no longer exist (`low_cpu_mem_usage`, `mirror`, `_fast_init`, `offload_state_dict` are silently popped as deprecated).
- **Dynamic weight loading** — new `WeightConverter` core: checkpoints can be reshaped, merged, and split on load (e.g. fusing Q/K/V projections). Enables clean quantization + parallelism combinations and faster loading.
- **Safetensors only** — `safe_serialization=False` removed from all `save_pretrained`/`push_to_hub`. Save `model.state_dict()` yourself for other formats.
- **Default shard size 50GB** (was 5GB).
- **`use_auth_token` → `token`** everywhere (search-replace safe).
- **torchscript and torch.fx support dropped** — use dynamo and torch.export instead.
- **Attention features removed** — no head masking, no relative positional biases in Bert-like models, no head pruning.

## Tokenization

- **One tokenizer file per model** (`tokenization_<model>.py`), backend selected automatically:
  1. `TokenizersBackend` (Rust `tokenizers`, preferred)
  2. `SentencePieceBackend`
  3. `PythonBackend` (formerly `PreTrainedTokenizer`)
  4. `MistralCommonBackend`
- **Blank initializable tokenizers** — `LlamaTokenizer()` creates an empty, trainable tokenizer following the class definition; `LlamaTokenizer(vocab=..., merges=...)` or file paths (`vocab="<path>"`, auto-detects SentencePiece `.model`, `tekken.json`, plain files) also work.
- **`decode`/`batch_decode` unified** — both use `decode`; batched input returns a list.
- **`encode_plus` deprecated** — use `__call__`.
- **`apply_chat_template` returns `BatchEncoding`** — pass `return_tensors="pt"` for tensors; `tokenize=False` for a string.
- **Legacy files no longer saved** — `special_tokens_map.json` (now in `tokenizer_config.json`) and `added_tokens.json` (now in `tokenizer.json`). `add_bos_token`/`add_eos_token` no longer saved when `tokenizer.json` exists. Old files are still read for backward compatibility.
- **Special tokens restructured** — `SpecialTokensMixin` merged into `PreTrainedTokenizerBase`. `special_tokens_map` holds only named tokens; use `extra_special_tokens` (formerly `additional_special_tokens`; `additional_special_tokens_ids` removed → `extra_special_tokens_ids`). `special_tokens_map_extended` and `all_special_tokens_extended` removed.
- **Removed methods** — `sanitize_special_tokens()`, `create_token_type_ids_from_sequences()` (implement in subclass), `as_target_tokenizer()`, `parse_response()`, `_switch_to_input_mode()`/`_switch_to_target_mode()`. `prepare_seq2seq_batch()` deprecated → `tokenizer(src, text_target=tgt, ...)` then `labels = inputs.pop("input_ids_target")`. `BatchEncoding.words()` deprecated → `word_ids()`.
- **Model merges** — LayoutLM→BertTokenizer, LED→BartTokenizer, Longformer→RobertaTokenizer, LXMert→BertTokenizer, MT5→T5Tokenizer, MVP→BartTokenizer. T5 `_eventually_correct_t5_max_length` workaround removed.
- **Old import paths gone** — `transformers.tokenization_utils` / `tokenization_utils_fast` no longer exist; they redirect to `transformers.tokenization_utils_sentencepiece` and `transformers.tokenization_utils_tokenizers`.

## Auto classes

- `AutoModelWithLMHead` removed → `AutoModelForCausalLM` / `AutoModelForMaskedLM` / `AutoModelForSeq2SeqLM`.
- `AutoModelForVision2Seq` removed → `AutoModelForImageTextToText`.

## Configuration

- `from_xxx_config` nested-config init methods deleted — init configs from `__init__` directly.
- Loading a config class from a URL file removed — local path or Hub repo only.
- **Rotary parameters unified under `config.rope_parameters`** — `rope_theta`, `rope_type` moved there (dict, or nested dict per layer type for Gemma3/ModernBert). `config.rope_theta` may raise AttributeError.
- **Qwen-VL family configs are nested** — access `config.text_config.vocab_size` etc.
- **Non-generative models have no `generation_config`** — `model.config.generation_config` raises AttributeError for models that never call `generate()`.

## Processing (image/video/audio)

- **`use_fast` replaced by `backend`** — `AutoImageProcessor.from_pretrained("...", backend="torchvision" | "pil")`. Default is `"torchvision"` if installed, else `"pil"`; missing backends fall back with a warning.
- **Class names flipped** — `FooImageProcessor` is now the torchvision-backed class (was `FooImageProcessorFast`); `FooImageProcessorPil` is the PIL-backed class (was `FooImageProcessor`). `*Fast` imports still resolve with a deprecation warning.
- **`processor.is_fast` deprecated** — use `processor.backend == "torchvision"`.
- **`XXXFeatureExtractors` classes removed** — use `XXXImageProcessor`.
- **`AutoImageProcessor.register()` API** — `slow_image_processor_class`/`fast_image_processor_class` deprecated for `image_processor_classes={"pil": ..., "torchvision": ...}`.
- **Custom backends** — any string key works via `MyProcessor.register_backend(name="mlx", backend_class=..., availability_check=...)`.
- **Processor serialization** — attributes now serialize as a nested dict in `processor_config.json` (old formats still load).
- `image_processing_utils_fast` module removed; shared logic lives in `image_processing_utils`.

## Modeling

- Some `RotaryEmbeddings` layers return a dict of (cos, sin) tuples when a model uses several RoPE configurations (Gemma2, ModernBert).
- **VLM shortcut removed** — `model.language_model` no longer available on vision-language generative models; use `model.model.language_model` or `model.get_decoder()`.
- **`get_text_features`/`get_image_features`/`get_audio_features`/`get_video_features` return `BaseModelOutputWithPooling`** — use `.pooler_output` for the old pooled tensor. No universal shape for `last_hidden_state`/`pooler_output`; inspect a small forward pass first.
- **Vision `hidden_states[-1]` is pre-norm** — `last_hidden_state` is the normalized output (differ since v4.57.2). Use `last_hidden_state` for final features; `ViTConfig(tie_last_hidden_states=True)` restores old behavior (available from v5.18.0).

## Generation

- Old output type aliases removed (e.g. `GreedySearchEncoderDecoderOutput`) — only 4 output classes remain (decoder-only vs encoder-decoder × beams vs no beams).
- **Constraints and beam-score classes removed** (moved to the Hub, low usage).
- **Default cache class is model-defined** — `generate()` with no KV-cache argument uses the model's default, not always `DynamicCache`.
- **Generation parameters are only in `model.generation_config`** — serialized values left in `config.json` load back into the generation config; modify via `model.generation_config.do_sample = True`, not the model config.

## Trainer

Removed without deprecation cycle: `mp_parameters`, `_n_gpu`, `overwrite_output_dir`, `logging_dir` (set `TENSORBOARD_LOGGING_DIR`), `jit_mode_eval` (use `use_torch_compile`), `tpu_num_cores` (set `TPU_NUM_CORES`), `past_index`, `ray_scope` (set `RAY_SCOPE`), `warmup_ratio` (use `warmup_step`, which accepts floats).

Renamed: `fsdp_min_num_params` + `fsdp_transformer_layer_cls_to_wrap` → `fsdp_config`; `tpu_metrics_debug` → `debug`; `push_to_hub_token` → `hub_token`; `push_to_hub_model_id`/`push_to_hub_organization` → `hub_model_id`; `include_inputs_for_metrics` → `include_for_metrics`; `per_gpu_train_batch_size` → `per_device_train_batch_size`; `per_gpu_eval_batch_size` → `per_device_eval_batch_size`; `use_mps_device` removed (MPS auto-detected); `fp16_backend`/`half_precision_backend` removed (torch.amp only); `no_cuda` → `use_cpu`; `include_tokens_per_second` → `include_num_input_tokens_seen`; `use_legacy_prediction_loop` removed.

`Trainer` changes: `tokenizer=` argument → `processing_class=`; `model_path` in `train()` → `resume_from_checkpoint`. Removed: sigopt hyperparameter search integration, sagemaker API <1.10. Minimum accelerate is 1.1.0.

**New default:** Trainer sets `use_cache=False` in the model config; override with `TrainingArguments(use_cache=...)`.

## Pipelines

Removed (use the replacements):

| Removed | Replacement |
|---|---|
| `question-answering`, `Text2TextGenerationPipeline` (incl. `SummarizationPipeline`, `TranslationPipeline`) | `text-generation` pipeline with a chat model and a task prompt |
| `image-to-text`, `visual-question-answering` | `image-text-to-text` pipeline with a VLM |
| `image-to-image` | 🤗 Diffusers |

`image-text-to-text` no longer accepts images as a separate argument — embed them in the chat `content` list as `{"type": "image", "image": ...}`.

## PushToHubMixin

- `organization` and `repo_url` removed — pass `repo_id`.
- `push_to_hub` accepts no `**kwargs` (all parameters explicitly documented) and arguments are keyword-only; only `repo_id` is positional.
- `use_temp_dir` removed (tmp dir always used); `ignore_metadata_errors` removed.

## CLI

- `transformers-cli` deprecated — `transformers` (Typer-based) is the only entry point.
- `transformers run` removed (never documented or tested).
- `transformers chat` is now a terminal UI client only (server functionality moved to `transformers serve`).
- Example: `transformers chat HuggingFaceTB/SmolLM3-3B` (works against any OpenAI-compatible endpoint, e.g. `transformers chat <model_id> https://router.huggingface.co/v1`).

## Environment variables

- Removed: `TRANSFORMERS_CACHE`, `PYTORCH_TRANSFORMERS_CACHE`, `PYTORCH_PRETRAINED_BERT_CACHE` — use `HF_HOME`.
- Removed: `HUGGINGFACE_CO_EXAMPLES_TELEMETRY`, `HUGGINGFACE_CO_PREFIX`, `HUGGINGFACE_CO_RESOLVE_ENDPOINT` — use `huggingface_hub.constants.ENDPOINT`.

## Requirements

- Python 3.11–3.14; `torch>=2.6` in the torch extra.
- `huggingface-hub>=1.31.0,<3.0` — hub 1.x switched its HTTP backend from `requests` to `httpx` (catch `httpx.HTTPError`; proxies via `HTTP_PROXY`/`HTTPS_PROXY` env vars only) and replaced `hf_transfer`/`HF_HUB_ENABLE_HF_TRANSFER` with `hf_xet`.
- `tokenizers>=0.23.1,<0.24.0`, `safetensors>=0.8.0`.
- `typer-slim` added as a hard dependency (shared by `hf` and `transformers` CLIs).
