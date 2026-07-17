# Text Generation

The `model.generate()` method produces text by iteratively sampling or selecting tokens. It supports multiple decoding strategies, logits processors, and streaming.

## Basic Generation

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-1.5B")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B")

inputs = tokenizer("Hello, how are you?", return_tensors="pt")

# Basic generation
outputs = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

## GenerationConfig

```python
from transformers import GenerationConfig

# Create custom config
config = GenerationConfig(
    max_new_tokens=256,
    temperature=0.8,
    top_p=0.95,
    top_k=50,
    repetition_penalty=1.1,
    do_sample=True,
    num_beams=1,
    eos_token_id=tokenizer.eos_token_id,
    pad_token_id=tokenizer.pad_token_id,
)

# Use with generate
outputs = model.generate(**inputs, generation_config=config)

# Or set as model default
model.generation_config = config
```

### Key Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `max_new_tokens` | int | None | Tokens to generate beyond input |
| `max_length` | int | 20 | Total sequence length (deprecated, use `max_new_tokens`) |
| `temperature` | float | 1.0 | Sampling temperature (lower = more deterministic) |
| `top_p` | float | 1.0 | Nucleus sampling threshold |
| `top_k` | int | 50 | Top-k sampling |
| `repetition_penalty` | float | 1.0 | Penalty for repeated tokens (>1 discourages) |
| `do_sample` | bool | False | Enable sampling (False = greedy) |
| `num_beams` | int | 1 | Beam search beam count |
| `num_return_sequences` | int | 1 | Sequences per prompt (with beam/search) |
| `eos_token_id` | int/list | None | End-of-sequence token(s) |
| `pad_token_id` | int | None | Padding token ID |
| `early_stopping` | bool | False | Stop beams when all reach EOS |
| `length_penalty` | float | 1.0 | Beam search length penalty |
| `no_repeat_ngram_size` | int | 0 | Block repeating n-grams |
| `min_new_tokens` | int | 0 | Minimum tokens to generate |
| `typical_p` | float | 1.0 | Typical sampling threshold |
| `watermarking` | bool | False | Apply watermark to generated text |

## Decoding Strategies

### Greedy Decoding

```python
# Default — selects highest-probability token at each step
outputs = model.generate(**inputs, do_sample=False, max_new_tokens=50)
```

### Sampled Decoding

```python
# Temperature sampling
outputs = model.generate(**inputs, do_sample=True, temperature=0.7, max_new_tokens=50)

# Nucleus (top-p) sampling
outputs = model.generate(**inputs, do_sample=True, top_p=0.9, max_new_tokens=50)

# Top-k sampling
outputs = model.generate(**inputs, do_sample=True, top_k=50, max_new_tokens=50)

# Combined
outputs = model.generate(
    **inputs, do_sample=True, temperature=0.8, top_p=0.95, top_k=50, max_new_tokens=50
)
```

### Beam Search

```python
# Beam search — explores multiple paths
outputs = model.generate(
    **inputs,
    num_beams=4,
    max_new_tokens=50,
    early_stopping=True,
    length_penalty=2.0,  # Encourages longer sequences
)

# Constrained beam search (grammar/regex)
# Use `fall_back_to_token_id` for tokens that don't match constraints
```

### Contrastive Search

```python
# Penalizes tokens similar to previous choices
outputs = model.generate(
    **inputs,
    penalty_alpha=0.6,
    top_k=30,
    max_new_tokens=50,
)
```

## Logits Processors and Warpers

Processors modify logits before token selection. Warpers are a subclass that reshape the distribution.

### Built-in Processors

```python
from transformers import (
    RepetitionPenaltyLogitsProcessor,
    NoRepeatNGramLogitsProcessor,
    MinLengthLogitsProcessor,
    NoBadWordsLogitsProcessor,
)

# Custom processors
processors = [
    RepetitionPenaltyLogitsProcessor(penalty=1.2),
    MinLengthLogitsProcessor(min_length=10, eos_token_id=tokenizer.eos_token_id),
]

outputs = model.generate(**inputs, max_new_tokens=50, logits_processor=processors)
```

### Built-in Warpers

```python
from transformers import (
    TemperatureLogitsWarper,
    TopPLogitsWarper,
    TopKLogitsWarper,
    MinPLogitsWarper,
    TypicalLogitsWarper,
)

# These are applied automatically when you set the corresponding parameters:
outputs = model.generate(
    **inputs,
    temperature=0.7,      # TemperatureLogitsWarper
    top_p=0.9,            # TopPLogitsWarper
    top_k=50,             # TopKLogitsWarper
    max_new_tokens=50,
)
```

## Stopping Criteria

```python
from transformers import (
    MaxLengthCriteria,
    MaxTimeCriteria,
    StopStringCriteria,
    StoppingCriteriaList,
)

# Stop after generating a specific string
stop = StopStringCriteria("\n\n", tokenizer)

# Stop after a time limit
time_limit = MaxTimeCriteria(max_time=30.0)  # 30 seconds

# Combine criteria
stopping_criteria = StoppingCriteriaList([stop, time_limit])

outputs = model.generate(**inputs, max_new_tokens=500, stopping_criteria=stopping_criteria)
```

## Streaming

```python
from transformers import TextStreamer, TextIteratorStreamer

# TextStreamer — prints tokens as they're generated
streamer = TextStreamer(tokenizer, skip_prompt=True)
outputs = model.generate(**inputs, max_new_tokens=50, streamer=streamer)

# TextIteratorStreamer — yields tokens for async processing
streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

import threading

def stream_print():
    for token in streamer:
        print(token, end="", flush=True)

thread = threading.Thread(target=stream_print)
thread.start()

outputs = model.generate(**inputs, max_new_tokens=50, streamer=streamer)
thread.join()
```

## Return Values

```python
# Default — returns generated token IDs
outputs = model.generate(**inputs, max_new_tokens=50)
# outputs.shape -> (batch_size, total_length)

# Return full output with scores, etc.
outputs = model.generate(
    **inputs,
    max_new_tokens=50,
    return_dict_in_generate=True,
    output_scores=True,
)
# outputs.sequences — token IDs
# outputs.scores — logits at each step
# outputs.past_key_values — cache for continued generation

# Return only new tokens
outputs = model.generate(
    **inputs,
    max_new_tokens=50,
    return_dict_in_generate=True,
)
new_tokens = outputs.sequences[:, inputs.input_ids.shape[1]:]
```

## Continued Generation (with cache)

```python
# First generation
outputs1 = model.generate(
    **inputs,
    max_new_tokens=20,
    return_dict_in_generate=True,
    output_scores=True,
)

# Continue from where we left off
cached_ids = outputs1.sequences
cached_past = outputs1.past_key_values

# Feed the generated text back as input
inputs2 = {"input_ids": cached_ids, "attention_mask": torch.ones_like(cached_ids)}
outputs2 = model.generate(
    **inputs2,
    past_key_values=cached_past,
    max_new_tokens=20,
)
```

## Gotchas

- **`max_new_tokens` vs `max_length`** — `max_new_tokens` is tokens beyond input. `max_length` is total length. Use `max_new_tokens` for predictable output.
- **`do_sample=False` is greedy** — always picks the highest-probability token. Deterministic but can be repetitive.
- **`temperature=0` with `do_sample=True`** — behaves like greedy decoding. Temperature only matters with sampling.
- **`top_p` and `top_k` together** — both are applied. `top_k` first (hard cutoff), then `top_p` on the remaining.
- **`num_beams > 1` with `do_sample=True`** — beam search and sampling are mutually exclusive. Set `do_sample=False` for beam search.
- **`pad_token_id` required for beam search** — beam search needs a pad token to align sequences of different lengths.
- **`repetition_penalty` applies to all tokens** — including input tokens. This can penalize words in the prompt itself.
- **`eos_token_id` stops generation** — when the model generates EOS, that beam/prompt stops. Multiple EOS tokens: pass a list.
- **`streamer` is incompatible with `num_beams > 1`** — streaming only works with single-sequence generation (greedy or sampled).
- **`return_dict_in_generate=True` has overhead** — stores intermediate scores and states. Only use when you need them.
- **`generation_config` is loaded from Hub** — models can ship with `generation_config.json`. Kwargs to `generate()` override these defaults.
- **`suppress_tokens` removed** — use `SequenceBiasLogitsProcessor` or `NoBadWordsLogitsProcessor` instead.
- **`guidance_scale` for contrastive search** — higher values increase diversity but may reduce coherence.
- **`typical_p` sampling** — different from `top_p`. Typical sampling controls the "perplexity per token" rather than cumulative probability.
- **`watermarking`** — applies a statistical watermark to generated text for attribution. Use `WatermarkLogitsProcessor` with a secret key.
- **`generate()` modifies `attention_mask` internally** — the attention mask is extended for generated tokens. Don't reuse the original mask after generation.
- **`use_cache=True` is default** — enables KV caching for faster generation. Disable with `use_cache=False` if you need all hidden states.
- **`model.generate()` on CPU is slow** — generation is inherently sequential. Use GPU for reasonable speeds.
- **`batch generation with variable lengths`** — shorter sequences stop at EOS but computation continues for longer ones. Use `pad_token_id` and consider continuous batching for production.
