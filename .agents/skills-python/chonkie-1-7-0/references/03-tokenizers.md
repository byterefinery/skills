# Tokenizers

Chonkie's tokenizer system abstracts tokenization behind a unified interface. `AutoTokenizer` auto-detects the backend and wraps it.

---

## Built-in Tokenizers

Available with base install, no extra dependencies:

| Name | Class | Description |
|------|-------|-------------|
| `"character"` | `CharacterTokenizer` | Each character = 1 token. Default tokenizer. |
| `"word"` | `WordTokenizer` | Splits on spaces. Each word = 1 token. |
| `"byte"` | `ByteTokenizer` | UTF-8 bytes. Each byte = 1 token. |
| `"row"` | `RowTokenizer` | Each line (newline-separated) = 1 token. Used by `TableChunker`. |

```python
from chonkie import AutoTokenizer

tok = AutoTokenizer("character")
tok.encode("hello")          # [104, 101, 108, 108, 111] (char codes, grows vocab)
tok.decode([104, 101, 108])  # "hel"
tok.count_tokens("hello")    # 5
```

## Tokie (default for named models)

`tokie` is the default backend for named model strings like `"gpt2"`, `"cl100k_base"`, etc. It loads tokenizers from HuggingFace.

```python
tok = AutoTokenizer("gpt2")           # loads via tokie
tok = AutoTokenizer("cl100k_base")    # maps to Xenova/gpt-4
tok = AutoTokenizer("o200k_base")     # maps to Xenova/gpt-4o
tok = AutoTokenizer("p50k_base")      # maps to Xenova/text-davinci-003
```

**TIKTOKEN → TOKIE mapping:**
- `cl100k_base` → `Xenova/gpt-4`
- `o200k_base` → `Xenova/gpt-4o`
- `p50k_base` → `Xenova/text-davinci-003`
- `gpt2` → `openai-community/gpt2`

Any HF tokenizer name works: `AutoTokenizer("bert-base-uncased")`.

## Tiktoken

```python
import tiktoken
tok = AutoTokenizer(tiktoken.encoding_for_model("gpt-4"))
```

Wraps a `tiktoken.Encoding` instance. Provides `encode()`, `decode()`, `count_tokens()`, batch variants.

## Transformers

```python
from transformers import AutoTokenizer as HFTokenizer
hf_tok = HFTokenizer.from_pretrained("bert-base-uncased")
tok = AutoTokenizer(hf_tok)
tok.encode("hello world", add_special_tokens=False)
```

Wraps `PreTrainedTokenizer` or `PreTrainedTokenizerFast`. `encode()` excludes special tokens by default.

## Tokenizers (HuggingFace)

```python
import tokenizers
hf_tok = tokenizers.Tokenizer.from_pretrained("bert-base-uncased")
tok = AutoTokenizer(hf_tok)
```

Wraps `tokenizers.Tokenizer`. `encode()` returns raw IDs (no special tokens).

## Custom Callable

Any callable that takes `str` and returns `int` can be used as a tokenizer (count-only):

```python
def custom_token_counter(text: str) -> int:
    return len(text) // 4  # rough estimate

chunker = RecursiveChunker(tokenizer=custom_token_counter)
```

**Note:** Callable tokenizers only support `count_tokens()`. `encode()`, `decode()`, and batch methods raise `NotImplementedError`.

## TokenizerProtocol

Custom tokenizer implementations must satisfy this protocol:

```python
from chonkie import TokenizerProtocol

class MyTokenizer(TokenizerProtocol):
    def encode(self, text: str) -> Sequence[int]: ...
    def decode(self, tokens: Sequence[int]) -> str: ...
    def tokenize(self, text: str) -> Sequence[str | int]: ...
```

## AutoTokenizer API

```python
tok = AutoTokenizer("gpt2")

# Single
tok.encode("hello")           # list[int]
tok.decode([1, 2, 3])         # str
tok.count_tokens("hello")     # int

# Batch
tok.encode_batch(["a", "b"])              # list[list[int]]
tok.decode_batch([[1], [2]])              # list[str]
tok.count_tokens_batch(["a", "b"])        # list[int]

# Backend info
tok._backend  # "tokie", "chonkie", "tiktoken", "transformers", "callable"
```

## Resolution Order

When `AutoTokenizer(string)` is called:
1. Check built-in names (`character`, `word`, `byte`, `row`)
2. Try tokie with tiktoken→tokie mapping
3. Try tokie directly with the string as HF name
4. Falls back with `InvalidTokenizerError` listing backend failures
