# Tokenizers (v5.24.1)

## v5 backend architecture

The slow/fast tokenizer split is gone. One tokenizer file per model (`tokenization_<model>.py`) picks the best available backend:

1. **`TokenizersBackend`** (preferred) — Rust `tokenizers` library; parallelized, full Python API, training support
2. **`SentencePieceBackend`** — for tokenizers requiring the `sentencepiece` library (inherits `PythonBackend`)
3. **`PythonBackend`** — pure-Python implementation of the tokenizers feature set (formerly `PreTrainedTokenizer`)
4. **`MistralCommonBackend`** — Mistral's tokenization library (formerly `MistralCommonTokenizer`)

`AutoTokenizer.from_pretrained()` selects the backend transparently, exactly as before.

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
inputs = tokenizer("Hello, how are you?", return_tensors="pt")
```

## Encoding and decoding

```python
# __call__ encodes (encode_plus is deprecated — use __call__)
inputs = tokenizer("Translate to French: hello world", return_tensors="pt", padding=True, truncation=True)

# decode handles both single and batch (batch_decode still exists as an alias)
tokenizer.decode(tokenizer.encode(["hey how are you?", "fine"]))
# ['hey how are you?</s>', 'fine</s>']

tokenizer.decode(generated_ids, skip_special_tokens=True)
```

Encoder-decoder labels without `as_target_tokenizer` (removed in v5) or `prepare_seq2seq_batch` (deprecated):

```python
model_inputs = tokenizer(src_texts, text_target=tgt_texts, max_length=128, return_tensors="pt")
model_inputs["labels"] = model_inputs.pop("input_ids_target")
```

Other v5 renames: `BatchEncoding.words()` → `word_ids()`; `additional_special_tokens` → `extra_special_tokens` (`additional_special_tokens_ids` → `extra_special_tokens_ids`). `special_tokens_map` now holds only named special tokens; `all_special_tokens` includes named plus extra.

## Blank and custom tokenizers

v5 lets you initialize a blank, trainable tokenizer that follows the class definition:

```python
from transformers import LlamaTokenizer

tokenizer = LlamaTokenizer()  # empty, trainable — train it on a corpus via the tokenizers library

# Or initialize from vocab and merges (file paths auto-detect format)
tokenizer = LlamaTokenizer(vocab=vocab_dict, merges=merges_list)
tokenizer = LlamaTokenizer(vocab="/path/to/vocab.json")  # quick testing; format auto-detected
```

## Chat templates

Chat models expect their conversation formatted with control tokens that differ per model. `apply_chat_template` handles this.

**v5 behavior: it returns a `BatchEncoding`** (not naked `input_ids`):

```python
messages = [
    {"role": "system", "content": "You are a friendly chatbot."},
    {"role": "user", "content": "How many cats does it take to change a light bulb?"},
]

# For generation — tokenize in one step (safer: avoids double special tokens)
model_inputs = tokenizer.apply_chat_template(
    messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
).to(model.device)

# For inspection — plain string
prompt_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
```

Key arguments:
- `add_generation_prompt=True` — append the assistant turn so the model starts generating the reply
- `continue_final_message=True` — continue an in-progress assistant message instead of starting a new one
- `tokenize=False` — returns a string; if you tokenize it later, pass `add_special_tokens=False` to avoid duplicating special tokens (the template already includes them)

Message content can be multimodal — a list of parts for VLMs:

```python
messages = [{
    "role": "user",
    "content": [
        {"type": "image", "image": "https://example.com/photo.jpg"},
        {"type": "text", "text": "Describe this image."},
    ],
}]
```

## Batched LLM generation setup

LLMs are not trained to continue from padding tokens, so pad on the left when batching prompts:

```python
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1", padding_side="left")
tokenizer.pad_token = tokenizer.eos_token  # many models lack a pad token
model_inputs = tokenizer(["1, 2, 3", "A, B, C, D, E"], padding=True, return_tensors="pt").to(model.device)
```

Right padding corrupts generation for state-space and hybrid models too — their recurrent state keeps updating over trailing pad tokens, so the cache no longer matches the end of the prompt.

## Special tokens and saved files

- `special_tokens_map.json` and `added_tokens.json` are no longer written — special tokens live in `tokenizer_config.json`, added tokens in `tokenizer.json` (or `added_tokens_decoder` when there is no `tokenizer.json`).
- `add_bos_token`/`add_eos_token` are no longer saved in `tokenizer_config.json` when a `tokenizer.json` exists — the tokenizer class or `tokenizer.json` defines them.
- Old files are still read on load for backward compatibility; new saves use the consolidated format.
- Added-token behavior is fixed at initialization (the old post-init backend synchronization of `add_prefix_space`, `do_lower_case`, `strip_accents`, `tokenize_chinese_chars` was removed).

## Tokenization algorithms

- **BPE** (Byte Pair Encoding) — Llama, Gemma, Qwen; deterministic merge rules; byte-level BPE (GPT-2) uses the 256 byte values as base vocabulary so no `<unk>` is needed
- **Unigram** — T5, BigBird, Pegasus; probabilistic; keeps the highest-likelihood tokenization
- **SentencePiece** — BPE/Unigram on raw text with `▁` space tokens (CJK support)
- **WordPiece** — BERT family; merges the pair that maximizes training-data likelihood
