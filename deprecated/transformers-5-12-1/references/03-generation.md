# Generation Reference

## `model.generate()`

Core generation method on all `PreTrainedModel` subclasses with a language modeling head.

### Signature

```python
outputs = model.generate(
    inputs=None,                           # torch.Tensor: input token IDs
    generation_config=None,                # GenerationConfig
    logits_processor=None,                 # LogitsProcessorList
    stopping_criteria=None,                # StoppingCriteriaList
    prefix_allowed_tokens_fn=None,         # Callable for constrained beam search
    synced_gpus=None,                      # bool: for FSDP/DeepSpeed
    assistant_model=None,                  # PreTrainedModel: for assisted generation
    streamer=None,                         # BaseStreamer: for streaming output
    negative_prompt_ids=None,              # torch.Tensor: for CFG
    negative_prompt_attention_mask=None,   # torch.Tensor: for CFG
    custom_generate=None,                  # str or Callable: custom generation fn
    **kwargs,                              # override generation_config params
)
```

### Basic Usage

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-1.5B")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B")

inputs = tokenizer("Write a story about ", return_tensors="pt").to(model.device)

# Generate
outputs = model.generate(**inputs, max_new_tokens=128)
text = tokenizer.decode(outputs[0], skip_special_tokens=True)
```

### Generation Strategies

```python
# Greedy decoding (default)
outputs = model.generate(**inputs, max_new_tokens=128)

# Sample (stochastic)
outputs = model.generate(
    **inputs,
    max_new_tokens=256,
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
    top_k=50,
)

# Beam search
outputs = model.generate(
    **inputs,
    max_new_tokens=128,
    num_beams=4,
    do_sample=False,
)

# Contrastive search (sample + beams)
outputs = model.generate(
    **inputs,
    max_new_tokens=128,
    num_beams=1,
    num_beam_groups=3,
    do_sample=True,
    diversity_penalty=0.7,
)

# Assisted generation (draft model accelerates decoding)
assistant = AutoModelForCausalLM.from_pretrained("small-draft-model")
outputs = model.generate(
    **inputs,
    assistant_model=assistant,
    max_new_tokens=256,
)
```

## GenerationConfig

Controls all generation parameters. Loaded from `generation_config.json` on the Hub or from `model.config`.

```python
from transformers import GenerationConfig

# Create custom config
config = GenerationConfig(
    max_new_tokens=256,
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
    top_k=50,
    repetition_penalty=1.1,
    no_repeat_ngram_size=3,
    eos_token_id=tokenizer.eos_token_id,
    pad_token_id=tokenizer.pad_token_id,
)

# Use with generate
outputs = model.generate(**inputs, generation_config=config)

# Or set as model default
model.generation_config = config
```

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_new_tokens` | `None` | Max tokens to generate (excludes prompt) |
| `max_length` | `20` | Max total length (prompt + generated). Deprecated in favor of `max_new_tokens` |
| `min_new_tokens` | `0` | Minimum tokens to generate |
| `do_sample` | `False` | Enable stochastic sampling |
| `temperature` | `1.0` | Sampling temperature (lower = more deterministic) |
| `top_p` | `1.0` | Nucleus sampling threshold |
| `top_k` | `50` | Top-k sampling limit |
| `typical_p` | `1.0` | Typical sampling threshold |
| `epsilon_cutoff` | `0.0` | Epsilon sampling |
| `eta_cutoff` | `0.0` | Eta sampling |
| `num_beams` | `1` | Number of beams for beam search |
| `num_beam_groups` | `1` | Diversity groups for diverse beam search |
| `diversity_penalty` | `0.0` | Penalty between beam groups |
| `repetition_penalty` | `1.0` | Penalty for repeated tokens (>1 = penalize) |
| `length_penalty` | `1.0` | Length penalty for beam search (>1 = prefer longer) |
| `no_repeat_ngram_size` | `0` | Block repeated n-grams (0 = disabled) |
| `encoder_no_repeat_ngram_size` | `0` | Block repeated n-grams in encoder |
| `forced_bos_token_id` | `None` | Force beginning-of-sequence token |
| `forced_eos_token_id` | `None` | Force end-of-sequence token |
| `early_stopping` | `False` | Stop beams when EOS is reached |
| `finetuning_behaviour` | `standard` | How to handle EOS/bos tokens |
| `suppress_tokens` | `None` | List of token IDs to suppress |
| `begin_suppress_tokens` | `None` | Tokens to suppress at beginning |
| `remove_invalid_values` | `False` | Remove NaN/Inf from logits |
| `exponential_decay_length_penalty` | `None` | Tuple (token_id, decay_factor) for length penalty |
| `guidance_scale` | `1.0` | Classifier-free guidance scale |
| `cache_implementation` | `"dynamic"` | Cache type: `"dynamic"`, `"static"`, `"hybrid"`, `"offloaded"` |
| `attn_implementation` | `"sdpa"` | Attention: `"sdpa"`, `"flash_attention_2"`, `"eager"` |

## Logits Processors

Modify logits before sampling. Applied in order via `LogitsProcessorList`.

### Built-in Processors

| Processor | Purpose |
|-----------|---------|
| `TemperatureLogitsWarper` | Apply temperature scaling |
| `TopKLogitsWarper` | Top-k filtering |
| `TopPLogitsWarper` | Nucleus (top-p) sampling |
| `MinPLogitsWarper` | Min-p sampling |
| `TypicalLogitsWarper` | Typical sampling |
| `EpsilonLogitsWarper` | Epsilon sampling |
| `EtaLogitsWarper` | Eta sampling |
| `RepetitionPenaltyLogitsProcessor` | Penalize repeated tokens |
| `NoRepeatNGramLogitsProcessor` | Block n-gram repetition |
| `NoBadWordsLogitsProcessor` | Block specific token sequences |
| `ForceBOSTokenLogitsProcessor` | Force BOS token at start |
| `ForceEOSTokenLogitsProcessor` | Force EOS at max length |
| `MinLengthLogitsProcessor` | Force minimum generation length |
| `MinNewTokensLengthLogitsProcessor` | Force min new tokens before EOS |
| `PrefixConstrainedLogitsProcessor` | Constrained decoding (grammar) |
| `SuppressTokensLogitsProcessor` | Suppress specific tokens |
| `SuppressTokensAtBeginLogitsProcessor` | Suppress tokens at start |
| `InfNanRemoveLogitsProcessor` | Remove inf/nan values |
| `SequenceBiasLogitsProcessor` | Apply bias to specific sequences |
| `ClassifierFreeGuidanceLogitsProcessor` | CFG for conditional generation |
| `UnbatchedClassifierFreeGuidanceLogitsProcessor` | Unbatched CFG |
| `WatermarkLogitsProcessor` | Text watermarking |
| `SynthIDTextWatermarkLogitsProcessor` | SynthID watermarking |
| `WhisperTimeStampLogitsProcessor` | Whisper timestamp tokens |
| `ExponentialDecayLengthPenalty` | Exponential length penalty |

### Custom Logits Processor

```python
from transformers import LogitsProcessor, LogitsProcessorList
import torch

class CustomLogitsProcessor(LogitsProcessor):
    def __init__(self, banned_tokens: list[int]):
        self.banned_tokens = set(banned_tokens)

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor):
        for token_id in self.banned_tokens:
            scores[:, token_id] = float("-inf")
        return scores

processor = LogitsProcessorList([CustomLogitsProcessor([1, 2, 3])])
outputs = model.generate(**inputs, logits_processor=processor)
```

## Stopping Criteria

Control when generation stops.

### Built-in Criteria

| Criteria | Description |
|----------|-------------|
| `MaxLengthCriteria` | Stop at max length (default) |
| `MaxTimeCriteria` | Stop after max time in seconds |
| `EosTokenCriteria` | Stop at EOS token (default) |
| `StopStringCriteria` | Stop when specific string is generated |
| `ConfidenceCriteria` | Stop when confidence drops below threshold |

### Custom Stopping Criteria

```python
from transformers import StoppingCriteria, StoppingCriteriaList
import torch

class StopOnToken(StoppingCriteria):
    def __init__(self, stop_token_id: int):
        self.stop_token_id = stop_token_id

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor):
        return self.stop_token_id in input_ids[0]

criteria = StoppingCriteriaList([StopOnToken(tokenizer.eos_token_id)])
outputs = model.generate(**inputs, stopping_criteria=criteria)
```

## Streamers

Stream generated tokens as they are produced.

### TextStreamer

```python
from transformers import TextStreamer

streamer = TextStreamer(tokenizer, skip_prompt=True)
outputs = model.generate(**inputs, streamer=streamer, max_new_tokens=256)
# Tokens print to stdout as they are generated
```

### TextIteratorStreamer

```python
from transformers import TextIteratorStreamer
import threading

streamer = TextIteratorStreamer(tokenizer, skip_prompt=True)

# Run generation in background thread
thread = threading.Thread(target=model.generate, kwargs={**inputs, "streamer": streamer, "max_new_tokens": 256})
thread.start()

# Stream tokens as they arrive
for token_text in streamer:
    print(token_text, end="", flush=True)

thread.join()
```

### AsyncTextIteratorStreamer

```python
from transformers import AsyncTextIteratorStreamer

streamer = AsyncTextIteratorStreamer(tokenizer, skip_prompt=True)

async def generate_and_stream():
    thread = threading.Thread(
        target=model.generate,
        kwargs={**inputs, "streamer": streamer, "max_new_tokens": 256}
    )
    thread.start()
    async for token_text in streamer:
        print(token_text, end="", flush=True)
    thread.join()
```

## Cache Implementations

| Cache | Description | Use Case |
|-------|-------------|----------|
| `DynamicCache` | Grows dynamically during generation | Default, most flexible |
| `StaticCache` | Pre-allocated fixed-size cache | Compilation, serving |
| `HybridCache` | Combines static + dynamic | Mixed workloads |
| `OffloadedCache` | Offloads to CPU when GPU memory is low | Large context windows |
| `QuantizedCache` | Quantized KV cache | Memory-constrained serving |

```python
from transformers import GenerationConfig, DynamicCache, StaticCache

# Use static cache (for compilation)
config = GenerationConfig(cache_implementation="static")
outputs = model.generate(**inputs, generation_config=config)

# Use dynamic cache explicitly
past_key_values = DynamicCache()
outputs = model.generate(**inputs, past_key_values=past_key_values)
```

## Continuous Batching

For serving scenarios with multiple concurrent requests:

```python
from transformers.generation import ContinuousBatchingManager, FIFOScheduler

manager = ContinuousBatchingManager(
    model=model,
    tokenizer=tokenizer,
    scheduler=FIFOScheduler(),
)
```

## Output Types

`generate()` returns different output types based on settings:

```python
# Default: just token IDs
outputs = model.generate(**inputs)  # torch.LongTensor

# With return_dict_in_generate=True: full output object
outputs = model.generate(
    **inputs,
    return_dict_in_generate=True,
    output_scores=True,
)
# outputs.sequences — generated token IDs
# outputs.scores — logits at each step
# outputs.past_key_values — KV cache
```

Output types:
- `GenerateDecoderOnlyOutput` — decoder-only models
- `GenerateEncoderDecoderOutput` — encoder-decoder models
- `GenerateBeamDecoderOnlyOutput` — beam search, decoder-only
- `GenerateBeamEncoderDecoderOutput` — beam search, encoder-decoder

## Watermarking

```python
from transformers import WatermarkingConfig, WatermarkDetector

# Enable watermarking during generation
config = GenerationConfig(
    watermarking=WatermarkingConfig(
        gamma=0.5,
        delta=3.0,
    ),
)
outputs = model.generate(**inputs, generation_config=config)

# Detect watermark
detector = WatermarkDetector(...)
result = detector.detect(text)
```
