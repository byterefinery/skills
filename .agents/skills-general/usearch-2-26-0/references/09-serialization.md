# Serialization

## Overview

USearch supports three serialization modes:

| Mode | Method | RAM Cost | Writable | Use Case |
|------|--------|----------|----------|----------|
| **Save** | `save()` | Full file written | — | Persist index to disk |
| **Load** | `load()` | Full index in RAM | ✅ | Working copy, modifications |
| **View** | `view()` | Near-zero (mmap) | ❌ | Serve from disk, cost optimization |

View mode uses memory-mapping (`mmap` on Unix, `CreateFileMapping` on Windows) to serve indexes from disk without loading into RAM. This can reduce cloud hosting costs by up to 20x.

## Python

```python
# Save
index.save('index.usearch')

# Load (copy into memory)
index.load('index.usearch')

# View (memory-map, read-only)
index.view('index.usearch')

# Restore without knowing original parameters
index = Index.restore('index.usearch', view=False)
index = Index.restore('index.usearch', view=True)

# Read metadata only
meta = Index.metadata('index.usearch')
print(meta.dimensions, meta.metric, meta.dtype)
```

## C++

```cpp
index.save("index.usearch");
index.load("index.usearch");
index.view("index.usearch");
```

## C

```c
// File-based
usearch_save(index, "index.usearch", &error);
usearch_load(index, "index.usearch", &error);
usearch_view(index, "index.usearch", &error);

// In-memory buffer
size_t bytes = usearch_serialized_length(index, &error);
void* buffer = malloc(bytes);
usearch_save_buffer(index, buffer, bytes, &error);
usearch_load_buffer(index, buffer, bytes, &error);
usearch_view_buffer(index, buffer, bytes, &error);

// Metadata
usearch_init_options_t opts;
usearch_metadata("index.usearch", &opts, &error);
usearch_metadata_buffer(buffer, bytes, &opts, &error);
```

## Rust

```rust
// File-based
index.save("index.usearch").unwrap();
index.load("index.usearch").unwrap();
index.view("index.usearch").unwrap();

// In-memory buffer
let mut buffer = Vec::new();
index.save_to_buffer(&mut buffer).unwrap();
index.load_from_buffer(&buffer).unwrap();
index.view_from_buffer(&buffer).unwrap();

// Restore
let meta = Index::metadata("index.usearch").unwrap();
let index = Index::restore("index.usearch").unwrap();
let index = Index::restore_view("index.usearch").unwrap();
let index = Index::restore_from_buffer(&buffer).unwrap();
```

## JavaScript

```js
index.save('index.usearch');
index.load('index.usearch');
index.view('index.usearch');
```

## File Format

### Current Version: v2

The serialized file consists of two main parts:

#### Matrix BLOB (optional, prepended)

Binary matrix of all vectors. Header: two 32-bit or 64-bit unsigned integers for `rows` and `columns` (number of vectors × bytes per vector), followed by raw vector data.

The matrix BLOB can be stored separately and is not required to open the index file.

#### Index BLOB

1. **Metadata** (64 bytes):
   - 7-byte magic string: `usearch`
   - 3-byte version: major, minor, patch
   - 1-byte enums: metric kind, scalar kind, key type, compressed slot type
   - 8-byte integers: present vectors, deleted vectors, dimensions
   - 1-byte flags: multi-vector support

2. **Levels**: Sequence of 1-byte integers (one per node), representing the HNSW level of each node.

3. **Core**:
   - Header: `size`, `connectivity`, `connectivity_base`, `max_level`, `entry_slot` (all `uint64_t`)
   - Levels block: repeats the 1-byte level integers
   - Nodes: contiguous blocks of node data (implementation-specific format)

### Upcoming Version: v3 (planned for USearch 3.0)

Designed for Apache Arrow compatibility:

1. **File Header**: Metadata
2. **Offset Array**: `N+1` entries of `uint64_t` (byte offsets for each vector)
3. **Data Chunks**: `N` chunks, each with vector + proximity graph data co-located

Advantages: variable-length vectors, better memory-mapping, Arrow array compatibility.

## Matrix File I/O (Python)

USearch provides utilities for standard k-ANN benchmark formats:

```python
from usearch.io import load_matrix, save_matrix

# Load .fbin/.f32bin/.ibin files (rows x cols header + raw data)
vectors = load_matrix('deep1B.fbin')

# Save
save_matrix(vectors, 'output.fbin')
```

Supported extensions: `.fbin`, `.f32bin`, `.f64bin`, `.hbin`, `.ibin`, `.u8bin`, `.i8bin`

## Gotchas

- **`view()` is read-only** — attempting to modify a viewed index will fail. Use `load()` for writable copies.
- **File format is cross-language** — an index saved from Python can be loaded in C++, Rust, Go, etc.
- **Matrix BLOB is optional** — if vectors are stored externally, the index file contains only the graph structure. `get()` operations will fail in this case.
- **Version compatibility** — v2 files from older USearch versions may not load in newer versions if the format changes. The 3-byte version header enables detection.
- **Large files and mmap** — on some systems, memory-mapping very large files (>2GB on 32-bit) requires special handling. Use 64-bit environments for large indexes.
- **Fragmented storage** — the matrix BLOB can be in a separate file from the index graph. This is useful when vectors are stored in a database and only the graph needs fast access.
