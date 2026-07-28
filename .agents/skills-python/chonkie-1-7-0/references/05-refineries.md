# Refineries

Refineries post-process chunks after initial chunking. They implement `refine(chunks: list[Chunk]) -> list[Chunk]` and `refine_document(document: Document) -> Document`.

---

## OverlapRefinery (`"overlap"`)

Adds context overlap between adjacent chunks. Uses LRU caching (maxsize=8192) for tokenization.

```python
from chonkie import OverlapRefinery

refinery = OverlapRefinery(
    tokenizer="character",       # default
    context_size=128,            # int (absolute) or float (0-1, relative to max chunk)
    mode="token",                # "token" or "recursive"
    method="suffix",             # "suffix", "prefix", or "justified"
    merge=True,                  # merge context into chunk.text
    inplace=True,                # modify chunks in place
)
refined_chunks = refinery.refine(chunks)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tokenizer` | str/TokenizerProtocol | `"character"` | Tokenizer for context calculation |
| `context_size` | int/float | 0.25 | Overlap size. Float = fraction of max chunk token count |
| `mode` | str | `"token"` | `"token"` = exact token count; `"recursive"` = delimiter-based |
| `method` | str | `"suffix"` | `"suffix"` = take from next chunk start; `"prefix"` = take from prev chunk end; `"justified"` = both |
| `merge` | bool | True | If True, prepend/append context to `chunk.text`. If False, store in `chunk.context` only |
| `inplace` | bool | True | If False, copies chunks before modifying |
| `rules` | RecursiveRules | default | Used when `mode="recursive"` |

### Methods

- **`suffix`** — takes first N tokens from the *next* chunk and appends to current chunk
- **`prefix`** — takes last N tokens from the *previous* chunk and prepends to current chunk
- **`justified`** — combines both: prefix from previous + suffix from next

### Important Details

- `start_index`/`end_index` are **not adjusted** when context is merged — they represent original document positions
- `token_count` is updated to include context tokens
- `chunk.context` attribute is always set (even when `merge=True`)
- Float `context_size` is computed relative to max chunk token count at refine time

### Cache Management

```python
refinery.clear_cache()   # Clear LRU caches
refinery.cache_info()    # Get cache hit/miss stats
```

---

## EmbeddingsRefinery (`"embeddings"`)

Adds embedding vectors to chunks.

```python
from chonkie import EmbeddingsRefinery

refinery = EmbeddingsRefinery(
    embedding_model="minishlab/potion-retrieval-32M",  # or BaseEmbeddings instance
)
refined_chunks = refinery.refine(chunks)
# chunks[0].embedding is now a numpy array
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `embedding_model` | str/BaseEmbeddings | `"minishlab/potion-retrieval-32M"` | Model name or pre-built instance |

### Properties

- `refinery.dimension` — embedding dimension of the model

### Important Details

- Writes `.embedding` directly on each Chunk as a numpy array
- Uses `embed_batch()` for efficiency
- For JSON serialization, use `chunk.embedding.tolist()`

---

## Pipeline Usage

```python
from chonkie import Pipeline

# Overlap
doc = (
    Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("overlap", context_size=64, method="suffix")
    .run(texts="Your text...")
)

# Embeddings
doc = (
    Pipeline()
    .chunk_with("semantic", chunk_size=512)
    .refine_with("embeddings", embedding_model="minishlab/potion-retrieval-32M")
    .run(texts="Your text...")
)

# Both
doc = (
    Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("overlap", context_size=64)
    .refine_with("embeddings", embedding_model="minishlab/potion-retrieval-32M")
    .run(texts="Your text...")
)
```
