---
name: chonkie-1-7-0
description: >
  Chonkie 1.7.0 — lightweight text chunking library for RAG pipelines.
  Provides 11 chunkers (Token, Sentence, Recursive, Semantic, Late, Code,
  Neural, Slumber, Table, Fast, TeraflopAI), fluent Pipeline API (CHOMP:
  Chef → Chunker → Refinery → Porter/Handshake), 16+ embedding providers,
  10 vector DB handshakes, 5 LLM genies, text/markdown chefs, file fetchers,
  overlap/embedding refineries, JSON/HF Datasets porters, REST API server,
  CLI, and cloud chunking. Use when splitting text for RAG, building
  ingestion pipelines, adding chunk overlap or embeddings, exporting to
  vector DBs, or running chonkie as a service. Trigger on: chonkie, text
  chunking, RAG, recursive/semantic/sentence/code/late/slumber/neural/fast/
  table/token chunker, pipeline API, overlap/embedding refinery, vector DB
  handshake, chroma/qdrant/pinecone handshake, chonkie serve, chonkie CLI.
license: Apache-2.0
compatibility: >
  Python 3.10–3.13. Base install includes tokie tokenizer and chonkie-core
  (Rust). Optional extras: `chonkie[code]` (tree-sitter), `chonkie[neural]`
  (transformers+torch), `chonkie[semantic]` (model2vec), `chonkie[st]`
  (sentence-transformers), `chonkie[openai]`, `chonkie[api]` (FastAPI server),
  `chonkie[all]` for everything. Install via `pip install chonkie`.
metadata:
  tags:
    - text-chunking
    - rag
    - nlp
    - python
    - ai
    - vector-database
---

# chonkie 1.7.0

## Overview

Chonkie is a feature-rich, lightweight text chunking library designed for RAG pipelines. It provides 11 chunking strategies, a fluent Pipeline API for end-to-end document processing, 16+ embedding providers, 10 vector database handshakes, LLM genies for agentic chunking, and a self-hosted REST API server.

**Architecture — CHOMP pipeline:** `Fetcher` → `Chef` → `Chunker` → `Refinery` → `Porter`/`Handshake`. The `Pipeline` class provides a fluent, chainable API that auto-reorders steps into this flow. Components are registered via decorators and resolved from a central `ComponentRegistry`.

**Core types:** `Chunk` (text + indices + token_count + optional embedding/metadata), `Document` (content + chunks + metadata), `RecursiveRules`/`RecursiveLevel` (hierarchical splitting rules), `Sentence` (sentence-level type).

**Key design decisions:**
- Minimum install is lightweight (~505KB wheel, ~49MB installed) — extras opt-in
- Default tokenizer is `character` (built-in); `tokie` handles `gpt2`, `cl100k_base`, etc.
- Chunkers are callable: `chunker(text)` returns `list[Chunk]`; `chunker([texts])` returns `list[list[Chunk]]`
- All chunkers support `chunk()`, `chunk_batch()`, `achunk()`, `achunk_batch()`, `chunk_document()`, `achunk_document()`
- `from_recipe()` classmethod on RecursiveChunker, SentenceChunker, SemanticChunker, LateChunker loads language-specific rules from the Chonkie Hub

## Installation

```bash
# Base install (token, sentence, recursive, table chunkers + basic tokenizers)
pip install chonkie

# With code chunking (tree-sitter)
pip install "chonkie[code]"

# With semantic chunking (model2vec)
pip install "chonkie[semantic]"

# With late chunking (sentence-transformers)
pip install "chonkie[st]"

# With neural chunking (transformers + torch)
pip install "chonkie[neural]"

# With OpenAI embeddings + genie
pip install "chonkie[openai]"

# API server
pip install "chonkie[api]"

# Everything
pip install "chonkie[all]"
```

## Usage

### Quick chunking

```python
from chonkie import RecursiveChunker

chunker = RecursiveChunker(chunk_size=512)
chunks = chunker("Your long document text here...")

for chunk in chunks:
    print(f"Tokens: {chunk.token_count}, Text: {chunk.text[:80]}...")
```

### Pipeline (fluent API)

```python
from chonkie import Pipeline

# Direct text input
doc = (
    Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("overlap", context_size=128)
    .run(texts="Your document text here...")
)

for chunk in doc.chunks:
    print(chunk.text)

# From file with export
doc = (
    Pipeline()
    .fetch_from("file", path="document.txt")
    .process_with("text")
    .chunk_with("recursive", chunk_size=512)
    .refine_with("overlap", context_size=64)
    .export_with("json", file="chunks.json")
    .run()
)

# Async
import asyncio
doc = await Pipeline().chunk_with("recursive", chunk_size=512).arun(texts="Text here")
```

### Semantic chunking

```python
from chonkie import SemanticChunker

chunker = SemanticChunker(
    embedding_model="minishlab/potion-base-32M",
    chunk_size=2048,
    threshold=0.8,
)
chunks = chunker("Long document with topic shifts...")
```

### Late chunking (embeddings included)

```python
from chonkie import LateChunker

chunker = LateChunker(
    embedding_model="nomic-ai/modernbert-embed-base",
    chunk_size=2048,
)
chunks = chunker("Document text...")
# Each chunk already has .embedding populated
```

### Code chunking

```python
from chonkie import CodeChunker

chunker = CodeChunker(chunk_size=1024, language="python")
chunks = chunker("def hello():\n    print('world')\n...")
```

### Adding overlap

```python
from chonkie import RecursiveChunker, OverlapRefinery

chunks = RecursiveChunker(chunk_size=512)("Document text...")
refinery = OverlapRefinery(context_size=128, method="suffix")
refined = refinery.refine(chunks)
```

### Adding embeddings

```python
from chonkie import RecursiveChunker, EmbeddingsRefinery

chunks = RecursiveChunker(chunk_size=512)("Document text...")
refinery = EmbeddingsRefinery(embedding_model="minishlab/potion-retrieval-32M")
refined = refinery.refine(chunks)
# Each chunk now has .embedding
```

### Writing to vector DB

```python
from chonkie import RecursiveChunker, ChromaHandshake

chunks = RecursiveChunker(chunk_size=512)("Document text...")
handshake = ChromaHandshake(collection_name="my_docs")
handshake.write(chunks)
```

### API server

```bash
pip install "chonkie[api,semantic,code,catsu]"
chonkie serve --port 8000

# Or with uvicorn
uvicorn chonkie.api.main:app --host 0.0.0.0 --port 8000
```

See reference files for complete API coverage:

- **Chunkers** — all 11 chunkers with parameters and patterns: [01-chunkers](references/01-chunkers.md)
- **Pipeline API** — fluent API, CHOMP flow, recipes, config: [02-pipeline](references/02-pipeline.md)
- **Tokenizers** — built-in, tokie, tiktoken, transformers, custom: [03-tokenizers](references/03-tokenizers.md)
- **Embeddings** — 16+ providers, AutoEmbeddings, provider aliases: [04-embeddings](references/04-embeddings.md)
- **Refineries** — OverlapRefinery, EmbeddingsRefinery: [05-refineries](references/05-refineries.md)
- **Handshakes** — 10 vector DB integrations: [06-handshakes](references/06-handshakes.md)
- **Chefs & Fetchers** — text preprocessing and data loading: [07-chefs-fetchers](references/07-chefs-fetchers.md)
- **Types** — Chunk, Document, RecursiveRules, Sentence: [08-types](references/08-types.md)
- **Genies** — LLM providers for SlumberChunker: [09-genies](references/09-genies.md)
- **Porters** — JSON and HuggingFace Datasets export: [10-porters](references/10-porters.md)
- **Cloud** — chonkie.cloud remote chunking API: [11-cloud](references/11-cloud.md)
- **API Server** — REST API, pipelines, Docker: [12-api-server](references/12-api-server.md)
- **CLI** — command-line interface: [13-cli](references/13-cli.md)

## Gotchas

- **Default tokenizer is `character`** — not `gpt2` or `tiktoken`. Pass `tokenizer="gpt2"` explicitly when token accuracy matters. The `character` tokenizer counts chars as tokens (1:1 mapping), which is fast but inaccurate for LLM token budgets.
- **`chunker(text)` vs `chunker([text])`** — single string returns `list[Chunk]`; list of strings returns `list[list[Chunk]]`. The `__call__` dispatches based on input type.
- **`chunk_overlap` on TokenChunker accepts float** — pass `0.1` for 10% overlap (computed as fraction of `chunk_size`). Integer is absolute token count.
- **`SemanticChunker` requires `chonkie[semantic]`** — default embedding model is `minishlab/potion-base-32M` (model2vec). Without the extra, import fails.
- **`LateChunker` requires `chonkie[st]`** — uses sentence-transformers for token-level embeddings. Returns chunks with `.embedding` already populated.
- **`CodeChunker` requires `chonkie[code]`** — depends on `tree-sitter-language-pack`. First use downloads all language grammars.
- **`NeuralChunker` requires `chonkie[neural]`** — depends on `transformers` + `torch`. Uses token-classification models from mirth/chonky.
- **`SlumberChunker` requires a Genie** — uses an LLM to find semantic split points. Pass `genie=OpenAIGenie(api_key=...)` or use default GeminiGenie.
- **`FastChunker` uses bytes, not tokens** — `chunk_size` is in bytes, not tokens. `token_count` on resulting chunks is always 0. Use when raw speed matters (~100+ GB/s).
- **`OverlapRefinery` modifies chunks in-place by default** — pass `inplace=False` to keep originals. `context_size` as float is relative to max chunk token count.
- **`EmbeddingsRefinery` writes `.embedding` directly on Chunk** — the embedding is a numpy array, not a list. Use `chunk.embedding.tolist()` for JSON serialization.
- **Pipeline auto-adds `TextChef`** — if no `.process_with()` step, the pipeline inserts a default `TextChef`. Only one chef per pipeline.
- **Pipeline reorders steps** — definition order doesn't matter. Steps are always executed: Fetch → Vision → Process → Chunk → Refine → Export/Write.
- **`chunk_document()` propagates metadata** — `Document.metadata` is shallow-merged into each chunk's `.metadata` (chunk keys override on conflict).
- **`from_recipe()` needs `chonkie[hub]`** — loads language-specific rules from HuggingFace Hub. Requires `huggingface-hub` and `jsonschema`.
- **Handshakes coerce metadata to primitives** — `BaseHandshake._coerce_flat_metadata()` converts non-primitive values to JSON strings. Complex metadata structures are stringified.
- **`AutoEmbeddings` uses `://` prefix for providers** — `"openai://text-embedding-3-small"` routes to `OpenAIEmbeddings`. Without prefix, registry auto-matches.
- **`AutoTokenizer` tries backends in order** — built-in (character/word/byte/row) → tokie → tiktoken → transformers. String `"gpt2"` resolves via tokie's HF mapping.
- **`RecursiveRules` default is 5 levels** — paragraphs → sentences → punctuation → whitespace → token. Customize with `RecursiveLevel(delimiters=...)` or `RecursiveLevel(whitespace=True)`.
- **`FastChunker` doesn't call `super().__init__()`** — it has no tokenizer. `self._tokenizer` is `None`. Don't pass `tokenizer=` to FastChunker.
- **`chonkie serve` needs `chonkie[api]`** — installs FastAPI, uvicorn, SQLAlchemy, alembic, aiosqlite.
- **`Pipeline.run(texts=...)` skips fetcher** — when direct text input is provided, any `.fetch_from()` step is ignored.
- **`Pipeline.run()` returns `Document` or `list[Document]`** — single text/file returns one Document; multiple texts/files returns list. Access chunks via `doc.chunks`.
- **Cloud chunkers require `CHONKIE_CLOUD_API_KEY`** — `chonkie.cloud.chunker.RecursiveChunker` etc. call the chonkie.ai cloud API. Set env var or pass `api_key` parameter.
- **`TableChunker` default tokenizer is `row`** — counts table rows as tokens. Default `chunk_size=3` means 3 rows per chunk. Use `tokenizer="character"` for char-based chunking.
- **`TeraflopAIChunker` requires API key** — calls the TeraflopAI Segmentation API. Pass `api_key` or set `TERAFLOPAI_API_KEY` env var.

## References

- [01-chunkers](references/01-chunkers.md) — Token, Sentence, Recursive, Semantic, Late, Code, Neural, Slumber, Table, Fast, TeraflopAI chunkers
- [02-pipeline](references/02-pipeline.md) — Pipeline fluent API, CHOMP flow, recipes, config, async, validation
- [03-tokenizers](references/03-tokenizers.md) — AutoTokenizer, built-in tokenizers, tokie, tiktoken, transformers, custom callables
- [04-embeddings](references/04-embeddings.md) — AutoEmbeddings, 16+ providers, provider aliases, registry, batch embedding
- [05-refineries](references/05-refineries.md) — OverlapRefinery (token/recursive, prefix/suffix/justified), EmbeddingsRefinery
- [06-handshakes](references/06-handshakes.md) — Chroma, Qdrant, Pinecone, pgvector, Weaviate, MongoDB, Elastic, Milvus, LanceDB, Turbopuffer
- [07-chefs-fetchers](references/07-chefs-fetchers.md) — TextChef, MarkdownChef, TableChef, MistralOCR, LiteParse, FileFetcher
- [08-types](references/08-types.md) — Chunk, Document, RecursiveLevel, RecursiveRules, Sentence, MarkdownDocument
- [09-genies](references/09-genies.md) — OpenAIGenie, GeminiGenie, AzureOpenAIGenie, GroqGenie, CerebrasGenie
- [10-porters](references/10-porters.md) — JSONPorter, DatasetsPorter
- [11-cloud](references/11-cloud.md) — Cloud chunkers, FileManager, Cloud Pipeline
- [12-api-server](references/12-api-server.md) — REST API, pipeline CRUD, Docker, endpoints
- [13-cli](references/13-cli.md) — `chonkie` CLI commands, `chonkie serve`
