---
name: usearch-2-26-0
description: >
  USearch 2.26.0 — single-file HNSW-based vector similarity search and clustering engine.
  Supports cosine, L2, inner product, haversine, hamming, tanimoto, sorensen, pearson,
  and Jensen-Shannon divergence metrics. Quantization from f64 down to b1 (single-bit).
  Bindings for Python, C++11 (header-only), C99, Rust, JavaScript/Node.js, Java, Go,
  C#, Swift, Objective-C, and SQLite extensions. Use when the user needs approximate
  nearest neighbor (ANN) search, vector indexing, semantic search, molecular/GIS search,
  clustering, or exact brute-force SIMD-accelerated distance computation.
license: MIT
compatibility: >
  Linux, macOS, Windows, iOS, Android, WebAssembly. C++11 or newer for header-only usage.
  Python 3.8+ for pip install. CMake for C/C++ builds. Cargo for Rust.
  NumKong SIMD kernels require x86 (AVX2/AVX-512) or ARM (NEON/SVE) hardware.
allowed-tools: Bash(pip:*,cargo:*,npm:*,dotnet:*,git:*) Read
metadata:
  tags:
    - vector-search
    - ann
    - hnsw
    - similarity
    - embeddings
    - ml
---

# usearch 2.26.0

## Overview

USearch is a compact, high-performance vector search engine built on the HNSW (Hierarchical Navigable Small World) algorithm. It is a single-header C++11 library with native bindings for 10+ languages. Key differentiators vs. FAISS:

- **Single-file header** (~3 K SLOC vs. FAISS's 84 K SLOC)
- **10x faster indexing** on large datasets (100M+ vectors)
- **User-defined metrics** via JIT compilation (Numba, Cppyy, PeachPy, or plain C/C++/Rust callbacks)
- **Hardware-agnostic quantization** — `f64`, `f32`, `bf16`, `f16`, `e5m2`, `e4m3`, `e3m2`, `e2m3`, `i8`, `u8`, `b1`
- **Disk-backed views** — memory-map indexes without loading into RAM (up to 20x cost reduction on cloud)
- **`uint40_t` keys** — address 1 trillion entries at 37.5% less memory than `uint64_t`
- **No required dependencies** — no BLAS, no OpenMP (optional), no external libraries

Integrated into ClickHouse, DuckDB, ScyllaDB, TiDB, YugaByte, MemGraph, LangChain, Microsoft Semantic Kernel, Google UniSim, and others.

## Usage

### Python (most common)

```python
pip install usearch

from usearch.index import Index
import numpy as np

index = Index(ndim=768, metric='cos', dtype='bf16')
index.add(42, np.random.rand(768).astype(np.float32))
matches = index.search(np.random.rand(768).astype(np.float32), 10)
```

### C++ (header-only)

```cpp
#include <usearch/index.hpp>
using namespace unum::usearch;

metric_punned_t metric(768, metric_kind_t::cos_k, scalar_kind_t::f32_k);
index_dense_t index = index_dense_t::make(metric);
index.reserve(1000);
index.add(42, vector);
auto results = index.search(vector, 10);
```

### Rust

```rust
use usearch::{Index, IndexOptions, MetricKind, ScalarKind, new_index};

let index = new_index(&IndexOptions {
    dimensions: 768,
    metric: MetricKind::Cos,
    quantization: ScalarKind::BF16,
    ..Default::default()
}).unwrap();
index.add(42, &vector).unwrap();
let results = index.search(&vector, 10).unwrap();
```

### C

```c
#include <usearch/usearch.h>

usearch_error_t error = NULL;
usearch_init_options_t opts = {
    .metric_kind = usearch_metric_cos_k,
    .scalar_kind = usearch_scalar_f32_k,
    .dimensions = 768,
};
usearch_index_t index = usearch_init(&opts, &error);
usearch_add(index, 42, vector, usearch_scalar_f32_k, &error);
```

### JavaScript (Node.js)

```js
const usearch = require('usearch');
const index = new usearch.Index({ metric: 'cos', dimensions: 768 });
index.add(42n, new Float32Array(vector));
const results = index.search(new Float32Array(query), 10);
```

See references for full language-specific details.

## Gotchas

- **Always call `reserve()` before bulk inserts** — without pre-allocation, the index grows incrementally and degrades performance significantly.
- **`dtype` (quantization) is irreversible** — once vectors are stored as `i8` or `bf16`, `get()` returns quantized data, not originals. Keep a separate store if you need the raw vectors.
- **`i8` quantization only works with cosine-like metrics** — vectors are normalized to unit length then scaled to [-127, 127]. Using `i8` with L2 or IP produces meaningless results.
- **`b1` quantization only works with binary metrics** — positive values become `1`, zero/negative become `0`. Only use with `hamming`, `tanimoto`, or `sorensen` metrics.
- **HNSW is not designed for frequent deletions** — removals leave tombstones. If you delete more than ~10% of entries, rebuild the index.
- **`view()` is read-only** — memory-mapped indexes cannot be modified. Use `load()` for writable copies.
- **`BatchMatches` has sentinel values** — unused result slots contain `NaN` distances. Always check `matches.counts` to know how many valid results each query returned.
- **JavaScript keys are `BigInt`** — use `42n` not `42`. This is a common source of runtime errors.
- **C++ does not use exceptions** — all operations return result objects. Check with `(bool)result` or `.is_ok()` rather than try/catch.
- **`expansion_add` vs `expansion_search`** — higher `expansion_add` improves index quality (slower build), higher `expansion_search` improves recall (slower search). Defaults are `128` and `64` respectively.
- **`connectivity` cannot be changed after creation** — it is fixed at index construction time. `expansion_add` and `expansion_search` can be tuned dynamically.
- **Python `copy=True` (default)** copies vectors into the index. `copy=False` avoids the copy but requires the input array to outlive the index.
- **`Index.restore()` reconstructs from file** — use when you don't know the original `ndim`/`metric`/`dtype`. It reads the file header automatically.
- **Exact search bypasses HNSW** — `search(vector, k, exact=True)` or `usearch.index.search()` does brute-force SIMD scan. Use for small datasets (<10K vectors) or ground truth generation.
- **CMake FetchContent is the recommended C++ install** — copying headers manually works but FetchContent handles versioning and submodules (NumKong).
- **Java requires manual JAR download** — Maven Central is not supported. Use the Gradle download task pattern from references.
- **Go requires native library pre-install** — download the `.deb` (Linux), `.zip` (macOS), or run `winlibinstaller.bat` (Windows) before `go get`.

## References

- [01-python-sdk](references/01-python-sdk.md) — Python bindings: Index, batch ops, JIT metrics, evaluation
- [02-cpp-sdk](references/02-cpp-sdk.md) — C++11 header-only: templates, executors, low-level API
- [03-c-sdk](references/03-c-sdk.md) — C99 API: error handling, predicates, exact search, concurrency
- [04-rust-sdk](references/04-rust-sdk.md) — Rust bindings: Cargo features, custom metrics, binary vectors
- [05-javascript-sdk](references/05-javascript-sdk.md) — Node.js and WASM: BigInt keys, batch ops
- [06-other-languages](references/06-other-languages.md) — Java, Go, C#, Swift, Objective-C
- [07-metrics-quantization](references/07-metrics-quantization.md) — All metrics, scalar types, quantization guide
- [08-advanced-features](references/08-advanced-features.md) — Custom metrics, filtering, clustering, joins
- [09-serialization](references/09-serialization.md) — Save, load, view, buffer ops, file format v2/v3
- [10-benchmarks](references/10-benchmarks.md) — Benchmarking utilities, datasets, profiling
- [11-sqlite](references/11-sqlite.md) — SQLite extensions: vector, string, binary distance functions
