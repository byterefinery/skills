# Model loading & saving (v5.24.1)

## from_pretrained

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    dtype="auto",        # default — load weights in stored dtype (avoids double float32 load)
    device_map="auto",   # Accelerate big-model inference (needs accelerate installed)
)
```

Key parameters (verified from the v5.24.1 source):

- `pretrained_model_name_or_path` — Hub ID or local path
- `revision` — resolved once; config, weights, generation config, and adapters all load from that exact revision
- `token` — Hub auth (v5 name; `use_auth_token` deprecated)
- `cache_dir` — defaults under `HF_HOME` (legacy `TRANSFORMERS_CACHE` env vars removed)
- `use_safetensors` — safetensors is the default and only serialization format
- `weights_only` — weights-only safe loading
- `local_files_only`, `force_download`
- `ignore_mismatched_sizes` — load even when a head size differs (e.g. fine-tuning for a different `num_labels`)
- `fusion_config` — weight fusion on load (dynamic weight loading)
- `disable_mmap`
- `*model_args` — `dtype`, `device_map`, `quantization_config`, `gguf_file`, `trust_remote_code`, and other model-specific kwargs

Backward-compat aliases still popped: `torch_dtype` (→ `dtype`); deprecated names silently ignored: `low_cpu_mem_usage`, `mirror`, `_fast_init`, `from_tf`, `from_flax`, `offload_state_dict`.

## Dynamic weight loading (WeightConverter)

v5's new weight-loading core applies transformations to checkpoints as they load — reshaping, merging, and splitting layers according to a `WeightConverter` (list of `ConversionOps` mapping source keys to target keys). Example from the migration guide:

```python
conversion = WeightConverter(
    ["self_attn.q_proj", "self_attn.k_proj", "self_attn.v_proj"],  # input layers
    "self_attn.qkv_proj",  # single fused output
    operations=[Concatenate(dim=0)],
)
```

Benefits: reversible transformations (load/save round-trips), faster loading via scheduling of tensor materialization, and combinations that were previously impossible (quantization + MoE, tensor parallelism + MoE). See `docs/source/en/weightconverter.md`.

## GGUF checkpoints

A GGUF file holds weights, config, and tokenizer in one file (no `config.json`). Name the file with `gguf_file`:

```python
model = AutoModelForCausalLM.from_pretrained(
    "unsloth/Qwen3.5-4B-GGUF",
    gguf_file="Qwen3.5-4B-Q4_K_M.gguf",
)
```

## save_pretrained

- Safetensors only — `safe_serialization=False` was removed in v5. For another format, save `model.state_dict()` yourself.
- Default shard size is **50GB** (was 5GB), so large models produce far fewer weight files.
- Tokenizer saves consolidate: no more `special_tokens_map.json` / `added_tokens.json` (special tokens in `tokenizer_config.json`, added tokens in `tokenizer.json`).

```python
model.save_pretrained("./my-model")
tokenizer.save_pretrained("./my-model")
```

## push_to_hub (v5 API)

v5 tightened `PushToHubMixin.push_to_hub`:

- Arguments are **keyword-only**; only `repo_id` is positional
- `**kwargs` are no longer accepted — every accepted parameter is explicit
- `repo_id` is required (removed: `organization`, `repo_url`)
- Removed: `use_temp_dir` (tmp dir always used), `ignore_metadata_errors` (fail early instead)

```python
# From a model directly
model.push_to_hub("my_account/my-model")

# Via Trainer — uploads weights, generation config, tokenizer, and model config
trainer.push_to_hub()
```

Authentication: `hf auth login` or pass `token="hf_..."`.

## Loading tips

- `device_map="auto"` dispatches weights across devices (fastest first, then CPU/disk) — requires `accelerate` (included in `transformers[torch]`).
- `ignore_mismatched_sizes=True` when swapping task heads of a different size.
- Non-generative models have no generation config — don't read `model.config.generation_config` for them.
- `trust_remote_code=True` executes model-specific code from the Hub — security-sensitive; note v5 removed many old import paths remote code relied on (`transformers.tokenization_utils*` no longer exists).
