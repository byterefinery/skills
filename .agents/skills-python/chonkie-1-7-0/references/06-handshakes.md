# Handshakes

Handshakes provide a unified interface to ingest chunks into vector databases. All implement `write(chunks: Union[Chunk, list[Chunk]]) -> Any` and `awrite()` for async.

---

## BaseHandshake

Shared behavior:
- `_merge_chunk_metadata()` — merges `chunk.metadata` into stored record fields (handshake fields override on conflict)
- `_coerce_flat_metadata()` — converts non-primitive metadata values to JSON strings (for stores that only accept primitives)
- `_generate_id()` — deterministic UUID from text content
- `__call__(chunks)` — shorthand for `write(chunks)`

---

## ChromaHandshake (`"chroma"`)

```python
from chonkie import ChromaHandshake

handshake = ChromaHandshake(
    collection_name="my_docs",
    host=None,              # chroma server host (None = in-memory)
    port=None,              # chroma server port
    persist_directory=None, # persistence path
)
handshake.write(chunks)
```

Uses `chromadb`. Metadata is coerced to primitives (str/int/float/bool).

---

## QdrantHandshake (`"qdrant"`)

```python
from chonkie import QdrantHandshake

handshake = QdrantHandshake(
    collection_name="my_docs",
    host="localhost",
    port=6333,
)
handshake.write(chunks)
```

Uses `qdrant-client`. Supports payloads from chunk metadata.

---

## PineconeHandshake (`"pinecone"`)

```python
from chonkie import PineconeHandshake

handshake = PineconeHandshake(
    index_name="my-index",
    api_key="your_key",
    environment="us-east1-gcp",
)
handshake.write(chunks)
```

Uses `pinecone`. Metadata coerced to primitives.

---

## PgvectorHandshake (`"pgvector"`)

```python
from chonkie import PgvectorHandshake

handshake = PgvectorHandshake(
    connection_string="postgresql://user:pass@localhost:5432/db",
    table_name="chunks",
    dimension=384,
)
handshake.write(chunks)
```

Uses `vecs`. Requires chunks to have `.embedding` set (use `EmbeddingsRefinery` or `LateChunker`).

---

## WeaviateHandshake (`"weaviate"`)

```python
from chonkie import WeaviateHandshake

handshake = WeaviateHandshake(
    url="http://localhost:8080",
    class_name="Document",
)
handshake.write(chunks)
```

Uses `weaviate-client`.

---

## MongoDBHandshake (`"mongodb"`)

```python
from chonkie import MongoDBHandshake

handshake = MongoDBHandshake(
    connection_string="mongodb://localhost:27017",
    database="rag",
    collection="chunks",
)
handshake.write(chunks)
```

Uses `pymongo`.

---

## ElasticHandshake (`"elastic"`)

```python
from chonkie import ElasticHandshake

handshake = ElasticHandshake(
    hosts=["http://localhost:9200"],
    index_name="chunks",
)
handshake.write(chunks)
```

Uses `elasticsearch`.

---

## MilvusHandshake (`"milvus"`)

```python
from chonkie import MilvusHandshake

handshake = MilvusHandshake(
    collection_name="my_docs",
    host="localhost",
    port=19530,
    dimension=384,
)
handshake.write(chunks)
```

Uses `pymilvus`. Requires `.embedding` on chunks.

---

## LanceDBHandshake (`"lancedb"`)

```python
from chonkie import LanceDBHandshake

handshake = LanceDBHandshake(
    uri="./lancedb",
    table_name="chunks",
)
handshake.write(chunks)
```

Uses `lancedb`. Local file-based or remote.

---

## TurbopufferHandshake (`"turbopuffer"`)

```python
from chonkie import TurbopufferHandshake

handshake = TurbopufferHandshake(
    namespace="my_docs",
    api_token="your_token",
    region="us-east-1",
)
handshake.write(chunks)
```

Uses `turbopuffer`.

---

## Pipeline Usage

```python
from chonkie import Pipeline

doc = (
    Pipeline()
    .chunk_with("recursive", chunk_size=512)
    .refine_with("embeddings", embedding_model="minishlab/potion-retrieval-32M")
    .store_in("chroma", collection_name="documents")
    .run(texts="Your text...")
)
```

## Important Notes

- Chunks must have `.embedding` set before writing to most vector DBs (except Chroma which can embed internally)
- Use `EmbeddingsRefinery` or `LateChunker` to populate embeddings
- Metadata from `chunk.metadata` is merged into stored records
- Non-primitive metadata values are JSON-stringified via `_coerce_flat_metadata()`
- `chunk.id` (auto-generated UUID with `"chnk_"` prefix) is used as the record ID
