# Python SDK

## Installation

```sh
pip install usearch
```

Pre-built wheels are available for Linux, macOS, and Windows. Includes SQLite extensions.

## Index Construction

```python
from usearch.index import Index
import numpy as np

index = Index(
    ndim=768,              # Required: vector dimensions
    metric='cos',          # 'cos', 'l2sq', 'ip', 'haversine', 'tanimoto', 'sorensen', 'hamming'
    dtype='bf16',          # None (auto), 'f64', 'f32', 'bf16', 'f16', 'e5m2', 'e4m3', 'e3m2', 'e2m3', 'i8', 'u8', 'b1'
    connectivity=16,       # Neighbors per graph node (default auto)
    expansion_add=128,     # Indexing depth (default auto)
    expansion_search=64,   # Search depth (default auto)
    multi=False,           # Multiple vectors per key
)
```

## Basic Operations

```python
# Add single vector
vector = np.array([0.2, 0.6, 0.4], dtype=np.float32)
index.add(42, vector)

# Search
matches = index.search(vector, 10)  # Returns Matches
assert matches[0].key == 42
assert matches[0].distance <= 0.001

# Retrieve stored vector
retrieved = index[42]  # Returns quantized version if dtype != input type

# Remove
index.remove(42)

# Check membership
assert index.contains(42)
```

## Batch Operations

```python
n = 10000
keys = np.arange(n)
vectors = np.random.uniform(0, 0.3, (n, index.ndim)).astype(np.float32)

# Batch add (threads=0 = auto-detect all cores)
index.add(keys, vectors, threads=0, copy=True)

# Batch search
matches: BatchMatches = index.search(vectors, 10, threads=0)

# Access individual query results
first_query_matches: Matches = matches[0]
assert matches[0].key == 0  # First key is 0
assert len(matches[0]) <= 10

# Check counts for valid results
for i, count in enumerate(matches.counts):
    valid_matches = matches[i][:count]
```

> **Warning:** Unused positions in `BatchMatches` are filled with sentinel values (NaN distances). Always check `matches.counts`.

## Serialization

```python
# Save to disk
index.save('index.usearch')

# Load (copies into memory, writable)
index.load('index.usearch')

# View (memory-map, read-only, no RAM cost)
index.view('index.usearch')

# Restore without knowing original parameters
index = Index.restore('index.usearch', view=False)

# Read metadata only
meta = Index.metadata('index.usearch')
print(meta.dimensions, meta.metric, meta.dtype)
```

## Exact Search (Brute-Force)

```python
from usearch.index import search, MetricKind, Matches, BatchMatches

vectors = np.random.rand(10_000, 1024).astype(np.float32)
query = np.random.rand(1024).astype(np.float32)

# Single query against many vectors
one_in_many: Matches = search(vectors, query, 50, MetricKind.L2sq, exact=True)

# Many queries against many vectors
many_in_many: BatchMatches = search(vectors, vectors, 50, MetricKind.L2sq, exact=True)
```

Exact search bypasses HNSW indexing entirely. Uses SIMD-optimized distance functions from NumKong. Up to 20x faster than FAISS `IndexFlatL2` on Google Colab.

## User-Defined Metrics (JIT)

### Numba

```python
from numba import cfunc, types, carray
from usearch.index import Index, MetricKind, MetricSignature, CompiledMetric

ndim = 256

@cfunc(types.float32(types.CPointer(types.float32), types.CPointer(types.float32)))
def inner_product(a, b):
    a_array = carray(a, ndim)
    b_array = carray(b, ndim)
    c = 0.0
    for i in range(ndim):
        c += a_array[i] * b_array[i]
    return 1.0 - c

metric = CompiledMetric(
    pointer=inner_product.address,
    kind=MetricKind.IP,
    signature=MetricSignature.ArrayArray,
)
index = Index(ndim=ndim, metric=metric, dtype=np.float32)
```

With ndim passed at runtime:

```python
@cfunc(types.float32(types.CPointer(types.float32), types.CPointer(types.float32), types.uint64))
def inner_product(a, b, ndim):
    a_array = carray(a, ndim)
    b_array = carray(b, ndim)
    return 1.0 - sum(a_array[i] * b_array[i] for i in range(ndim))

metric = CompiledMetric(
    pointer=inner_product.address,
    kind=MetricKind.IP,
    signature=MetricSignature.ArrayArraySize,
)
```

### Cppyy (Cling JIT)

```python
import cppyy
import cppyy.ll

ndim = 256
cppyy.cppdef(f"""
float inner_product(float *a, float *b) {{
    float result = 0;
#pragma unroll
    for (size_t i = 0; i != {ndim}; ++i)
        result += a[i] * b[i];
    return 1 - result;
}}
""")

function = cppyy.gbl.inner_product
metric = CompiledMetric(
    pointer=cppyy.ll.addressof(function),
    kind=MetricKind.IP,
    signature=MetricSignature.ArrayArraySize,
)
```

### PeachPy (Assembly)

For x86_64 with AVX2, write raw assembly and load it as a metric. See the main repo's JavaScript docs for a full example. Requires `pip install peachpy`.

## Scalar Quantization & NumKong Interop

```python
import numkong as nk
import numpy as np
from usearch.index import Index

vectors_f32 = np.random.rand(1000, 256).astype(np.float32)
keys = np.arange(1000)

# Option 1: USearch quantizes internally
index = Index(ndim=256, metric='cos', dtype='e4m3')
index.add(keys, vectors_f32)

# Option 2: Pre-quantize with NumKong
vectors_e4m3 = np.asarray(nk.Tensor(vectors_f32).astype('e4m3'))
index2 = Index(ndim=256, metric='cos', dtype='e4m3')
index2.add(keys, vectors_e4m3, dtype='e4m3')
matches = index2.search(vectors_e4m3[:5], 10, dtype='e4m3')
```

## Evaluation Tools

```python
from usearch.eval import self_recall, relevance, dcg, ndcg, random_vectors
from usearch.index import Index
from usearch.io import load_matrix, save_matrix

# Load binary matrix (standard k-ANN format: rows x cols header + raw floats)
vectors = load_matrix('deep1B.fbin')

# Self-recall test
stats = self_recall(index, exact=True)   # Baseline: every vector finds itself
stats = self_recall(index, exact=False)  # Approximate recall

# Relevance / NDCG
vectors = random_vectors(index=index)
matches_approx = index.search(vectors)
matches_exact = index.search(vectors, exact=True)
relevance_scores = relevance(matches_exact, matches_approx)
print(dcg(relevance_scores), ndcg(relevance_scores))
```

## Indexes (Multi-Index)

For billion-scale workloads, split into multiple smaller indexes:

```python
from usearch.index import Indexes

multi_index = Indexes(
    indexes=[index1, index2, index3],
    # or
    paths=['index1.usearch', 'index2.usearch'],
    view=False,
    threads=0,
)
results = multi_index.search(query, 10)
```

## Clustering

```python
clustering = index.cluster(min_count=10, max_count=15, threads=0)

centroid_keys, sizes = clustering.centroids_popularity
clustering.plot_centroids_popularity()  # Matplotlib histogram

# NetworkX graph
g = clustering.network

# Members of a specific cluster
members = clustering.members_of(centroid_keys[0])

# Sub-cluster (iterative deepening)
sub_clustering = clustering.subcluster(min_count=5, max_count=10)
```

## Joins

```python
men = Index(ndim=768, metric='cos')
women = Index(ndim=768, metric='cos')

# Populate both indexes...
pairs = men.join(women, max_proposals=0, exact=False)
```

Sub-quadratic approximate fuzzy joins. Useful for deduplication and record linkage.
