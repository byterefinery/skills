# Tokenizers

Tokenizers convert raw text into token IDs for model input. Transformers provides both "slow" (Python) and "fast" (Rust-based `tokenizers` library) implementations.

## Basic Usage

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Single string
encoding = tokenizer("Hello, world!")
# {'input_ids': [101, 7592, 1010, 2978, 102], 'attention_mask': [1, 1, 1, 1, 1]}

# Return PyTorch tensors
encoding = tokenizer("Hello, world!", return_tensors="pt")
# input_ids: tensor([[101, 7592, 1010, 2978, 102]])

# Decode
tokenizer.decode([101, 7592, 1010, 2978, 102])
# "[CLS] hello, world! [SEP]"

tokenizer.decode([101, 7592, 1010, 2978, 102], skip_special_tokens=True)
# "hello, world!"
```

## Encoding Options

```python
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Truncation
tokenizer("A long text...", max_length=128, truncation=True)

# Padding
tokenizer(["Short", "A much longer sentence here"], padding=True)
# Pads to longest in batch

tokenizer(["Short", "Longer text..."], padding="max_length", max_length=512)
# Pads to exact max_length

# Both
tokenizer("Text", max_length=128, padding="max_length", truncation=True)
```

## Batching

```python
# Batch encoding
batch = tokenizer(
    ["First sentence", "Second sentence", "Third"],
    padding=True,
    truncation=True,
    max_length=512,
    return_tensors="pt",
)
# batch.input_ids.shape -> (3, 512)
```

## Chat Templates

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")

# Apply chat template
messages = [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "What is Python?"},
]

# For generation (returns token IDs)
input_ids = tokenizer.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=True,  # Adds assistant turn marker
    return_tensors="pt",
)

# For display (returns string)
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
)
```

### Custom Chat Templates

```python
# Set a custom template
tokenizer.chat_template = "{% for msg in messages %}{{msg['role']}}: {{msg['content']}}\n{% endfor %}"

# Use a template from the Hub
tokenizer = AutoTokenizer.from_pretrained("model", chat_template="default")

# Check if model has a chat template
print(tokenizer.chat_template)  # None if not set
```

## Special Tokens

```python
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# Check special tokens
print(tokenizer.special_tokens_map)
# {'bos_token': '<|endoftext|>', 'eos_token': '<|endoftext|>', ...}

# Add pad token (many models lack one)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# Add custom special tokens
tokenizer.add_special_tokens({
    "pad_token": "<PAD>",
    "additional_special_tokens": ["<SPECIAL1>", "<SPECIAL2>"],
})

# After adding tokens, resize model embeddings
model.resize_token_embeddings(len(tokenizer))
```

## Padding Side

```python
# Left padding — preferred for generation (pad before, not after)
tokenizer.padding_side = "left"

# Right padding — preferred for training (pad after)
tokenizer.padding_side = "right"
```

## Token-Type IDs

For models like BERT that distinguish sentence pairs:

```python
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

encoding = tokenizer(
    "First sentence",
    "Second sentence",
    return_tensors="pt",
)
# encoding.token_type_ids -> [0, 0, ..., 1, 1, ...]
# 0 = first sentence, 1 = second sentence
```

## Word IDs and Offset Mapping

```python
encoding = tokenizer("Hello world!", return_offsets_mapping=True)

# Get word-level spans
for word, (start, end) in zip(
    ["Hello", "world", "!"],
    encoding.offset_mapping[0][1:-1],  # Skip [CLS] and [SEP]
):
    print(f"{word}: chars {start}-{end}")
```

## Fast vs Slow Tokenizers

```python
# Check which is available
print(tokenizer.is_fast)  # True if fast (Rust) tokenizer is available

# Force slow tokenizer
tokenizer = AutoTokenizer.from_pretrained("model", use_fast=False)

# Fast tokenizers support additional features:
encoding = tokenizer("Text", return_words=True)
encoding.word_ids(0)  # Token index -> word index mapping

encoding = tokenizer("Text", return_special_tokens_mask=True)
encoding.special_tokens_mask[0]  # Boolean mask for special tokens
```

## Saving and Loading

```python
# Save
tokenizer.save_pretrained("./my-tokenizer")

# Load
tokenizer = AutoTokenizer.from_pretrained("./my-tokenizer")
```

## Common Parameters

| Parameter | Type | Description |
|---|---|---|
| `padding` | bool/str | `"longest"`, `"max_length"`, or bool |
| `truncation` | bool/str | `"longest_first"`, `"only_first"`, `"only_second"` |
| `max_length` | int | Max tokens (truncation/padding target) |
| `return_tensors` | str | `"pt"`, `"tf"`, `"np"` |
| `return_token_type_ids` | bool | Include token type IDs |
| `return_attention_mask` | bool | Include attention mask |
| `return_overflow` | bool | Return truncated overflow chunks |
| `stride` | int | Overlap between overflow chunks |
| `add_special_tokens` | bool | Add BOS/EOS/padding tokens |

## Gotchas

- **`pad_token` must be set for batching** — without it, `padding=True` fails. Set `tokenizer.pad_token = tokenizer.eos_token` if missing.
- **`padding_side` matters for generation** — use `"left"` so the generated tokens are at the end of the sequence. Right padding shifts the generation position.
- **`model_max_length` is a soft limit** — it's informational. The tokenizer won't enforce it automatically; pass `max_length` + `truncation=True` explicitly.
- **`add_special_tokens=False`** — use when you manage special tokens manually (e.g., adding BOS/EOS yourself).
- **`apply_chat_template` with `add_generation_prompt=True`** — this adds the assistant role marker, signaling the model to generate. Omit it when encoding completed conversations.
- **`tokenize=False` in `apply_chat_template`** — returns the raw formatted string. Use for debugging or logging.
- **`return_overflow` for long documents** — combined with `stride`, this splits long texts into overlapping chunks for processing.
- **`clean_up_tokenization_spaces`** — default `True`. Merges spaces introduced by tokenization. Set `False` for exact character alignment.
- **`strip_accents`** — some tokenizers have this option. Removes diacritical marks, reducing vocabulary size for non-English text.
- **Fast tokenizer `word_ids()`** — maps token indices back to word indices. Useful for aligning token-level predictions (NER) with original words.
- **`tokenizer.encode()` vs `tokenizer()`** — `encode()` returns a list of IDs directly. `tokenizer()` returns a dict with `input_ids`, `attention_mask`, etc. Prefer `tokenizer()` for clarity.
- **`tokenizer.decode()` with `skip_special_tokens`** — always set `True` for readable output. Special tokens like `[PAD]`, `[CLS]`, `[SEP]` clutter the output.
- **`add_bos_token`/`add_eos_token`** — control whether BOS/EOS tokens are added. Some models expect them, others don't. Check the model card.
- **`tokenizer.model_max_length` override** — some tokenizers have hardcoded limits (e.g., 512 for BERT). Override with `tokenizer.model_max_length = int(1e30)` if needed, but respect the model's actual context window.
- **`padding="max_length"` without `max_length`** — uses `model_max_length` from config. Explicit `max_length` is clearer.
- **`truncation="only_second"`** — for BERT-style models with sentence pairs, truncates only the second sentence, preserving the first (often the query).
- **`tokenizer.save_pretrained()` saves all files** — includes `tokenizer.json` (fast), `tokenizer_config.json`, `special_tokens_map.json`, `vocab.txt` (slow), and `added_tokens.json`.
