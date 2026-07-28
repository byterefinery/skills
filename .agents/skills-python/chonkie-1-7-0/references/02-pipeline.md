# Pipeline API

The `Pipeline` class provides a fluent, chainable API for building end-to-end document processing workflows. Steps are defined in any order but always execute in CHOMP flow: **F**etcher → **V**ision → **C**hef → **C**hunker → **R**efinery → **P**orter/**H**andshake.

---

## Basic Usage

```python
from chonkie import Pipeline

# Direct text input — returns Document
doc = (
    Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("overlap", context_size=64)
    .run(texts="Your document text here...")
)

for chunk in doc.chunks:
    print(f"Chunk {chunk.start_index}-{chunk.end_index}: {chunk.text[:50]}...")
```

## CHOMP Flow

Steps are auto-reordered into this execution order:

| Order | Step | Method | Description |
|-------|------|--------|-------------|
| 1 | Fetch | `.fetch_from(alias, **kwargs)` | Load data from sources |
| 2 | Vision | `.see_with(alias, **kwargs)` | OCR / image text extraction |
| 3 | Process (Chef) | `.process_with(alias, **kwargs)` | Parse/clean text into Document |
| 4 | Chunk | `.chunk_with(alias, **kwargs)` | Split into chunks |
| 5 | Refine | `.refine_with(alias, **kwargs)` | Post-process (overlap, embeddings) |
| 6 | Export | `.export_with(alias, **kwargs)` | Save chunks (JSON, Datasets) |
| 7 | Write | `.store_in(alias, **kwargs)` | Write to vector DB |

**Rules:**
- Only one chef (process) step allowed — if multiple defined, last one wins
- Only one vision step allowed
- Multiple chunkers, refineries, and exporters are allowed (executed in definition order)
- Default `TextChef` is auto-inserted if no `.process_with()` step is defined
- Fetcher step is skipped when `run(texts=...)` provides direct text input

## From File

```python
# Single file
doc = (
    Pipeline()
    .fetch_from("file", path="document.txt")
    .process_with("text")
    .chunk_with("recursive", chunk_size=512)
    .run()
)

# Directory with extension filter
docs = (
    Pipeline()
    .fetch_from("file", dir="./docs", ext=[".txt", ".md"])
    .process_with("text")
    .chunk_with("recursive", chunk_size=512)
    .run()
)
# docs is list[Document]
for doc in docs:
    print(f"{len(doc.chunks)} chunks")
```

## With Refinement and Export

```python
doc = (
    Pipeline()
    .fetch_from("file", path="document.txt")
    .process_with("text")
    .chunk_with("recursive", chunk_size=512)
    .refine_with("overlap", context_size=64)
    .refine_with("embeddings", embedding_model="minishlab/potion-retrieval-32M")
    .export_with("json", file="chunks.json")
    .run()
)
```

## With Vector DB

```python
doc = (
    Pipeline()
    .fetch_from("file", path="document.txt")
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embeddings", embedding_model="minishlab/potion-retrieval-32M")
    .store_in("chroma", collection_name="documents")
    .run()
)
```

## Async

```python
import asyncio

async def main():
    doc = await (
        Pipeline()
        .chunk_with("recursive", chunk_size=512)
        .arun(texts="Text to chunk...")
    )
    print(len(doc.chunks))

asyncio.run(main())
```

## Multiple Chunkers

```python
# Chain multiple chunkers — second refines chunks from first
doc = (
    Pipeline()
    .chunk_with("recursive", chunk_size=2048)
    .chunk_with("semantic", chunk_size=512)
    .run(texts="Your text...")
)
```

## Recipes

Load pre-defined pipeline configurations from the Chonkie Hub:

```python
# From hub
pipeline = Pipeline.from_recipe("markdown")
doc = pipeline.run(texts="Your markdown here...")

# From local file
pipeline = Pipeline.from_recipe("custom", path="my_recipe.json")
```

## Config

```python
# From list of tuples: (step_type, component_alias, kwargs)
pipeline = Pipeline.from_config([
    ("chunk", "recursive", {"chunk_size": 512}),
    ("refine", "overlap", {"context_size": 64}),
])

# From dict format
pipeline = Pipeline.from_config([
    {"type": "chunk", "component": "recursive", "chunk_size": 512},
    {"type": "refine", "component": "overlap", "context_size": 64},
])

# From JSON file
pipeline = Pipeline.from_config("pipeline.json")
```

## Export Config

```python
pipeline = (
    Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("overlap", context_size=64)
)

# As list
config = pipeline.to_config()

# To file
pipeline.to_config("my_pipeline.json")
```

## Introspection

```python
pipeline = (
    Pipeline()
    .fetch_from("file", path="doc.txt")
    .chunk_with("recursive", chunk_size=512)
    .refine_with("overlap", context_size=64)
)

print(pipeline.describe())
# "fetch(file) -> process(text) -> chunk(recursive) -> refine(overlap)"

print(repr(pipeline))
# "Pipeline(fetch(file) -> process(text) -> chunk(recursive) -> refine(overlap))"
```

## Reset

```python
pipeline.reset()  # Clear all steps and cached component instances
```

## Parameter Splitting

The pipeline automatically splits kwargs between `__init__` and method parameters by inspecting signatures. Init params are used when creating the component instance; call params are passed to the execute method. Unknown params raise `ValueError`.

## Component Caching

Component instances are cached by `(name, json_kwargs)` key. Reusing the same component with identical params within a pipeline reuses the instance.

## Return Types

- `Pipeline.run()` returns `Document` for single text/file input
- Returns `list[Document]` for multiple texts or directory fetch
- Access chunks via `doc.chunks` (list of `Chunk` objects)
- `export_with()` and `store_in()` return the Document(s) for chaining

## Validation

Pipeline validates at `run()` time:
- Must have at least one chunker
- Must have fetcher OR direct text input
- Only one chef allowed (raises if user defines multiple)
- Empty list input (`run(texts=[])`) returns `[]` gracefully
