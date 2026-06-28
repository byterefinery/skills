# Tokenization Reference

## Tokenizer Types

| Type | Backing | Speed | Notes |
|------|---------|-------|-------|
| **Fast** (Rust) | `tokenizers` library | Fast | Supports batched encoding, alignment |
| **Slow** (Python) | Pure Python | Slower | Fallback when fast unavailable |
| **SentencePiece** | `sentencepiece` | Medium | Used by T5, LLaMA, many multilingual models |
| **tiktoken** | `tiktoken` (OpenAI) | Fast | Used by GPT-4, some Llama variants |

## Basic Usage

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B")

# Single text
encoded = tokenizer("Hello, world!")
print(encoded)
# {'input_ids': [1, 1539, 374, 38766, 128007, 198], 'attention_mask': [1, 1, 1, 1, 1, 1]}

# With PyTorch tensors
encoded = tokenizer("Hello, world!", return_tensors="pt")
# {'input_ids': tensor([[...]]), 'attention_mask': tensor([[...]})

# Decode
text = tokenizer.decode(encoded["input_ids"][0])
text_no_special = tokenizer.decode(encoded["input_ids"][0], skip_special_tokens=True)
```

## Key Parameters

```python
encoded = tokenizer(
    "Hello, world!",
    return_tensors="pt",          # "pt" (PyTorch), "tf" (TensorFlow), "np" (NumPy), or None
    padding=False,                # False, "longest", "max_length"
    truncation=False,             # False, True, "longest_first", "only_first", "only_second"
    max_length=512,               # Max tokens (used with padding/truncation)
    padding_side="right",         # "right" or "left"
    add_special_tokens=True,      # Add BOS/EOS tokens
    return_attention_mask=True,   # Include attention mask
    return_token_type_ids=True,   # Include token type IDs (for BERT-style models)
    return_overflowing_tokens=False,  # Return overflow tokens as separate sequences
    return_length=False,          # Return sequence length
    return_offsets_mapping=False, # Return character offset mapping
    return_special_tokens_mask=False,  # Return special tokens mask
)
```

## Padding

```python
texts = ["Short text", "This is a much longer text that needs padding"]

# Pad to longest in batch
encoded = tokenizer(texts, padding="longest", return_tensors="pt")

# Pad to max_length
encoded = tokenizer(texts, padding="max_length", max_length=128, return_tensors="pt")

# Pad to specific length
encoded = tokenizer(texts, padding="max_length", max_length=256, return_tensors="pt")
```

## Truncation

```python
long_text = " ".join(["word"] * 10000)

# Truncate to max_length
encoded = tokenizer(long_text, truncation=True, max_length=512, return_tensors="pt")

# Truncate+pad together
encoded = tokenizer(
    long_text,
    padding="max_length",
    truncation=True,
    max_length=512,
    return_tensors="pt",
)
```

## Text Pair (for encoder-decoder / BERT)

```python
encoded = tokenizer(
    "Question: What is the capital of France?",
    "France is a country in Western Europe. Its capital is Paris.",
    return_tensors="pt",
    padding=True,
    truncation=True,
    max_length=512,
)
# For BERT: token_type_ids distinguishes sentence A (0) from sentence B (1)
# For encoder-decoder: use model.encode_plus() or separate encoding
```

## Chat Templates

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"},
    {"role": "assistant", "content": "The capital of France is Paris."},
    {"role": "user", "content": "What about Germany?"},
]

# Apply chat template (returns formatted string)
text = tokenizer.apply_chat_template(messages, tokenize=False)

# Apply and tokenize in one step
encoded = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt")

# For generation, add_generation_prompt=True adds the assistant turn marker
encoded = tokenizer.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=True,
    return_tensors="pt",
).to(model.device)

outputs = model.generate(**encoded, max_new_tokens=128)
```

### Custom Chat Templates

```python
# Set custom template
tokenizer.chat_template = """{{ bos_token }}
{% for message in messages %}
  {{ '<|im_start|>' + message['role'] + '\\n' + message['content'] + '<|im_end|>' + '\\n' }}
{% endfor %}
{% if add_generation_prompt %}
  {{ '<|im_start|>assistant\\n' }}
{% endif %}"""

# Use built-in default
tokenizer.chat_template = tokenizer.default_chat_template
```

### Available Template Variables

- `bos_token` — beginning of sequence token
- `eos_token` — end of sequence token
- `messages` — list of message dicts with `role` and `content`
- `add_generation_prompt` — boolean, True when preparing for generation
- `tokenizer` — the tokenizer instance itself

## Special Tokens

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Check special tokens
print(tokenizer.pad_token)     # [PAD]
print(tokenizer.eos_token)     # [SEP] or </s>
print(tokenizer.bos_token)     # [CLS] or <s>
print(tokenizer.unk_token)     # [UNK]
print(tokenizer.mask_token)    # [MASK]

# Set padding token (if not set)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# Add new special tokens
num_added = tokenizer.add_special_tokens({
    "additional_special_tokens": ["<custom1>", "<custom2>"],
})

# Add tokens to model vocabulary
model.resize_token_embeddings(len(tokenizer))
```

## Padding Side

```python
# Default: right padding
tokenizer.padding_side = "right"
# Good for training, feature extraction

# Left padding (for generation with decoder-only models)
tokenizer.padding_side = "left"
# Required for batched generation so padding is before content,
# and the model generates from the rightmost (non-padded) tokens
```

## Batch Encoding

```python
texts = ["First sentence.", "Second sentence that is longer.", "Third."]

# Batch encode
encoded = tokenizer(
    texts,
    padding=True,
    truncation=True,
    max_length=128,
    return_tensors="pt",
)
# encoded.input_ids.shape -> (3, 128)

# Batch decode
texts = tokenizer.batch_decode(encoded["input_ids"], skip_special_tokens=True)
```

## Word-Level Alignment (Fast Tokenizers)

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")

encoded = tokenizer("Hello world!", return_offsets_mapping=True)
# encoded.offset_mapping -> list of (start_char, end_char) tuples

# Convert token indices to word indices
words = tokenizer.convert_tokens_to_string(
    tokenizer.convert_ids_to_tokens(encoded["input_ids"])
)

# Get token for a character span
token_ids_in_span = tokenizer.encode("world", add_special_tokens=False)
```

## Tokenizer Save/Load

```python
# Save
tokenizer.save_pretrained("./my-tokenizer")

# Load
tokenizer = AutoTokenizer.from_pretrained("./my-tokenizer")

# Push to Hub
tokenizer.push_to_hub("my-username/my-tokenizer", token="hf_...")
```

## Tokenizer Inspection

```python
print(tokenizer.vocab_size)           # Vocabulary size
print(tokenizer.model_max_length)     # Max sequence length
print(tokenizer.pad_token_id)         # Pad token ID
print(tokenizer.eos_token_id)         # EOS token ID
print(tokenizer.bos_token_id)         # BOS token ID
print(tokenizer.unk_token_id)         # Unknown token ID
print(tokenizer.mask_token_id)        # Mask token ID
print(tokenizer.chat_template)        # Chat template (may be None)
print(tokenizer.is_fast)              # Whether fast tokenizer is available

# Token ID to text
print(tokenizer.decode([1]))          # Single token
print(tokenizer.decode([1, 2, 3]))    # Multiple tokens

# Text to token ID
print(tokenizer.encode("hello"))      # List of token IDs
print(tokenizer.vocab["hello"])       # Direct vocab lookup (if available)
```

## SentencePiece Tokenizers

```python
from transformers import AutoTokenizer

# Models using SentencePiece (T5, LLaMA, etc.)
tokenizer = AutoTokenizer.from_pretrained("google/t5-v1_1-base")

# SentencePiece tokenizers handle subword tokenization natively
# They don't need the tokenizers library for fast mode
encoded = tokenizer("Hello world!", return_tensors="pt")
```

## tiktoken Tokenizers

```python
from transformers import AutoTokenizer

# Some models use tiktoken (OpenAI's tokenizer)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B")

# tiktoken-based tokenizers are fast and compatible with OpenAI's encoding
encoded = tokenizer("Hello world!", return_tensors="pt")
```
