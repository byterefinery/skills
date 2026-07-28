# Chunking

Docling provides native chunkers that operate directly on `DoclingDocument`, producing chunks with metadata for RAG pipelines.

## Chunker types

### HybridChunker

Tokenization-aware chunking on top of hierarchical structure. Best for RAG with embedding models.

```python
from docling.chunking import HybridChunker
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

chunker = HybridChunker(
    tokenizer=tokenizer,
    max_tokens=512,
    merge_peers=True,           # merge undersized chunks with same headings (default)
    repeat_table_header=True,   # repeat table headers across chunks (default)
    omit_header_on_overflow=False,  # omit header if row overflows with it
)

chunks = list(chunker.chunk(doc))

for chunk in chunks:
    text = chunker.contextualize(chunk)  # metadata-enriched text for embedding
    print(f"[{len(tokenizer.tokenize(text))} tokens] {text[:100]}...")
```

**Two-pass approach:**
1. Split oversized chunks (exceed `max_tokens`)
2. Merge undersized successive chunks with same headings/captions

### LineBasedTokenChunker

Preserves line boundaries. Best for structured content (tables, code, logs, lists).

```python
from docling.chunking import LineBasedTokenChunker

chunker = LineBasedTokenChunker(
    tokenizer=tokenizer,
    max_tokens=512,
    prefix=None,                      # optional repeated prefix (e.g. table header)
    omit_prefix_on_overflow=False,    # drop prefix if line overflows with it
)

chunks = list(chunker.chunk(doc))
```

### HierarchicalChunker

Uses document structure to create one chunk per document element. Minimal processing.

```python
from docling_core.transforms.chunker.hierarchical_chunker import HierarchicalChunker

chunker = HierarchicalChunker(
    merge_list_items=True,  # merge consecutive list items (default)
)

chunks = list(chunker.chunk(doc))
```

## Chunk structure

Each `BaseChunk` contains:

- `text` — the chunk text
- `meta` — `BaseMeta` with document metadata, headings, captions
- `orig` — reference to original document items

```python
chunk = chunks[0]
print(chunk.text)
print(chunk.meta.headings)       # applicable headings
print(chunk.meta.captions)       # applicable captions
print(chunker.contextualize(chunk))  # enriched text for embedding
```

## Installation

```python
# Via docling package (includes chunking)
from docling.chunking import HybridChunker

# Via docling-core with extra
# pip install 'docling-core[chunking]'     # HuggingFace tokenizers
# pip install 'docling-core[chunking-openai]'  # tiktoken
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
```

## Tokenizers

Choose a tokenizer aligned with your embedding model:

```python
# HuggingFace tokenizer
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# OpenAI tiktoken
import tiktoken
tokenizer = tiktoken.encoding_for_model("text-embedding-3-small")
```

## Table chunking

When tables span multiple chunks:

- `repeat_table_header=True` (default): headers repeated at start of each chunk
- `omit_header_on_overflow=True`: if a row fits without header but not with it, omit the header for that row

This maximizes token efficiency while preserving table context.

## Known warning

`HybridChunker` may trigger a transformers warning:

> Token indices sequence length is longer than the specified maximum sequence length

This is a **false alarm** — the chunker tokenizes to count tokens, then splits if oversized. The warning is emitted before the split happens. Actual chunk sizes stay within limits.

To verify:

```python
chunk_max_len = 0
for chunk in chunks:
    ser_txt = chunker.contextualize(chunk)
    ser_tokens = len(tokenizer.tokenize(ser_txt))
    chunk_max_len = max(chunk_max_len, ser_tokens)
print(f"Longest chunk: {chunk_max_len} tokens")
```

## Alternative: Markdown export + external chunking

Instead of native chunkers, export to Markdown and chunk externally:

```python
md = doc.export_to_markdown()
# Then use langchain.text_splitter, llama-index, etc.
```

This gives full control over chunking strategy but loses DoclingDocument structural metadata.
