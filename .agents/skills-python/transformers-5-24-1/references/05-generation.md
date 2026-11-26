# Text generation (v5.24.1)

`GenerationMixin.generate()` is available on all generative models. It accepts tokenizer output, a `GenerationConfig`, logits processors, stopping criteria, and streamers.

## Basic generation

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf", device_map="auto")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

inputs = tokenizer("Hugging Face is an open-source company", return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=20)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

**Set `max_new_tokens` explicitly** — `generate()` returns up to 20 tokens by default unless the model's `GenerationConfig` specifies otherwise, and decoder-only models return the input prompt plus the generated tokens.

## Common options

| Option | Type | Notes |
|---|---|---|
| `max_new_tokens` | `int` | Maximum new tokens. Define it — the default is small |
| `do_sample` | `bool` | `True` samples, `False` is greedy (the default). Most creative use cases want `True` |
| `temperature` | `float` | Unpredictability. `>0.8` creative, `<0.4` focused. Requires `do_sample=True` |
| `num_beams` | `int` | `>1` activates beam search — good for input-grounded tasks (translation, transcription) |
| `repetition_penalty` | `float` | `>1.0` penalizes repeated tokens |
| `eos_token_id` | `list[int]` | Tokens that stop generation. Default is usually fine |
| `top_k` / `top_p` | — | Sampling constraints (e.g. `do_sample=True, top_k=50`) |

## Decoding strategies

- **Greedy search** (default) — picks the most likely token each step; max 20 new tokens unless configured; degrades into repetition on long outputs
- **Multinomial sampling** — `do_sample=True, num_beams=1`; more diverse output
- **Beam search** — `num_beams > 1`; keeps the highest-probability overall sequence; best for input-grounded tasks. Combine with `do_sample=True` to sample while still pruning beams

## GenerationConfig

All generation settings live in `GenerationConfig`, loaded from the model's `generation_config.json` on the Hub. `model.generation_config` shows only values that differ from defaults.

**v5: generation parameters are only on `model.generation_config`** — not on `model.config`. If an old model serialized generation parameters into `config.json`, they are loaded back into the generation config automatically.

```python
# Inspect
print(model.generation_config)
# GenerationConfig { "bos_token_id": 1, "eos_token_id": 2 }

# Modify in place
model.generation_config.do_sample = True
model.generation_config.eos_token_id = [tokenizer.eos_token_id]

# Or pass a fresh config
from transformers import GenerationConfig

generation_config = GenerationConfig(
    max_new_tokens=50, do_sample=True, top_k=50, eos_token_id=model.config.eos_token_id
)
model.generate(**inputs, generation_config=generation_config)
```

`generate()` kwargs override the model's generation config. Save/share configs with:

```python
generation_config.save_pretrained("my_account/my_model", push_to_hub=True)

# Multiple named configs per directory
gen_config.save_pretrained("/tmp", config_file_name="translation_generation_config.json", push_to_hub=True)
loaded = GenerationConfig.from_pretrained("/tmp", config_file_name="translation_generation_config.json")
```

## Extension points

- `logits_processor` — custom `LogitsProcessor` instances to manipulate the next-token distribution
- `stopping_criteria` — custom `StoppingCriteria` to stop generation
- `custom_generate` — load custom generation methods
- Streamers — `TextStreamer`/`BaseStreamer` still exist in `transformers.generation.streamers`; pass `streamer=TextStreamer(tokenizer)` to `generate()` for incremental output
- Assisted decoding, watermarking — see `transformers.generation` (`candidate_generator.py`, `watermarking.py`)

## Caches

- When `generate()` receives no KV-cache argument, the **default cache class is defined by the model** (v5 change — previously always `DynamicCache`).
- Cache mechanics and strategies are documented in `docs/source/en/kv_cache.md` / `cache_explanation.md`.

## Removed in v5

- Old output type aliases (e.g. `GreedySearchEncoderDecoderOutput`) — only 4 output classes remain (decoder-only vs encoder-decoder × beams vs no beams)
- Constraint classes and beam-score helpers (moved to the Hub due to low usage)

## Prompt format

Chat models expect the chat template format (role/content messages through `apply_chat_template`) — passing a raw string to an instruct model often gives suboptimal output. For batched generation, use `padding_side="left"` and set a `pad_token` (see 04-tokenizers).
