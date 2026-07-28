# Cloud

Chonkie Cloud provides remote chunking via the chonkie.ai API. All local chunkers have cloud equivalents in `chonkie.cloud.chunker`.

---

## Authentication

Set `CHONKIE_CLOUD_API_KEY` environment variable or pass `api_key` parameter.

---

## Cloud Chunkers

All cloud chunkers mirror the local API:

```python
from chonkie.cloud.chunker import (
    RecursiveChunker,
    SemanticChunker,
    SentenceChunker,
    TokenChunker,
    LateChunker,
    CodeChunker,
    NeuralChunker,
    SlumberChunker,
)

# Same API as local chunkers
chunker = RecursiveChunker(chunk_size=512, api_key="your_key")
chunks = chunker("Text to chunk...")
```

**Available cloud chunkers:**
- `TokenChunker` — fixed token size
- `SentenceChunker` — sentence boundary aware
- `RecursiveChunker` — hierarchical rules
- `SemanticChunker` — embedding-based topic detection
- `LateChunker` — recursive with late interaction embeddings
- `CodeChunker` — tree-sitter AST-based
- `NeuralChunker` — neural token classification
- `SlumberChunker` — LLM-driven split detection

All share the same parameters and return types as their local counterparts.

---

## Cloud Refineries

```python
from chonkie.cloud.refineries import OverlapRefinery, EmbeddingsRefinery

refinery = OverlapRefinery(context_size=64, api_key="your_key")
refined = refinery.refine(chunks)
```

---

## Cloud Pipeline

```python
from chonkie.cloud.pipeline import Pipeline, PipelineStep

pipeline = Pipeline(api_key="your_key")
pipeline.add_step(PipelineStep("chunk", "recursive", {"chunk_size": 512}))
pipeline.add_step(PipelineStep("refine", "overlap", {"context_size": 64}))

result = pipeline.run(texts="Your text...")
```

---

## FileManager

Upload and manage files for cloud processing:

```python
from chonkie.cloud import FileManager

fm = FileManager(api_key="your_key")

# Upload
file_id = fm.upload("path/to/document.pdf")

# List
files = fm.list()

# Delete
fm.delete(file_id)
```
