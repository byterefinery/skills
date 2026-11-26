# Chunking

Docling provides native chunkers that operate directly on `DoclingDocument`, producing chunks with metadata for RAG pipelines. In 2.153.0, `docling.chunking` exports `HybridChunker` and `HierarchicalChunker` (plus the base types). The older `LineBasedTokenChunker` is no longer exported.

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
```

**Two-pass approach:** (1) split oversized chunks (exceed `max_tokens`), (2) merge undersized successive chunks with same headings/captions.

### HierarchicalChunker

Uses document structure to create one chunk per document element. Minimal processing.

```python
from docling.chunking import HierarchicalChunker

chunker = HierarchicalChunker(merge_list_items=True)  # merge consecutive list items (default)
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
# pip install 'docling-core[chunking]'         # HuggingFace tokenizers
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

When tables span multiple chunks: `repeat_table_header=True` (default) repeats headers at the start of each chunk; `omit_header_on_overflow=True` omits the header for a row that fits without it but not with it. This maximizes token efficiency while preserving table context.

## Known warning

`HybridChunker` may trigger a transformers "sequence length exceeds model max" warning. This is a **false alarm** — the chunker tokenizes to count tokens, then splits if oversized; the warning is emitted before the split. Actual chunk sizes stay within limits.

## Alternative: Markdown export + external chunking

Export to Markdown and chunk externally (langchain text splitter, LlamaIndex, etc.) for full control over strategy, at the cost of DoclingDocument structural metadata.
