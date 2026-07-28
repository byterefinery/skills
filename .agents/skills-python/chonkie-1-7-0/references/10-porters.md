# Porters

Porters export chunks to external formats. They implement `export(chunks: list[Chunk], **kwargs)` and `aexport()` for async.

---

## JSONPorter (`"json"`)

Exports chunks to a JSON file.

```python
from chonkie import JSONPorter

porter = JSONPorter()
porter.export(chunks, file="chunks.json")
```

**Output format:**
```json
[
  {
    "id": "chnk_abc123",
    "text": "Chunk text content...",
    "start_index": 0,
    "end_index": 50,
    "token_count": 10,
    "context": null,
    "embedding": [0.1, 0.2, ...],
    "metadata": {}
  }
]
```

**Pipeline usage:**
```python
from chonkie import Pipeline

doc = (
    Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .export_with("json", file="chunks.json")
    .run(texts="Your text...")
)
```

---

## DatasetsPorter (`"datasets"`)

Exports chunks to HuggingFace Datasets format. Requires `chonkie[datasets]`.

```python
from chonkie import DatasetsPorter

porter = DatasetsPorter()
porter.export(chunks, file="chunks_dataset")
```

Creates a HuggingFace `Dataset` object that can be saved and loaded:

```python
from datasets import load_dataset

dataset = load_dataset("chunks_dataset")
```

**Pipeline usage:**
```python
doc = (
    Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .export_with("datasets", file="chunks_dataset")
    .run(texts="Your text...")
)
```

---

## BasePorter

Abstract base class. Custom porters should implement:
- `export(chunks: list[Chunk], **kwargs)` — export chunks
- `aexport(chunks: list[Chunk], **kwargs)` — async variant (inherited default uses `asyncio.to_thread`)
