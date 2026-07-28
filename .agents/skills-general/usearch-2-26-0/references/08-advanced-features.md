# Advanced Features

## User-Defined Metrics (JIT Compilation)

USearch supports arbitrary distance functions compiled at runtime. This enables custom metrics for composite embeddings, domain-specific distances, or experimental similarity measures.

### Python: Numba

```python
from numba import cfunc, types, carray
from usearch.index import Index, MetricKind, MetricSignature, CompiledMetric

ndim = 256

@cfunc(types.float32(types.CPointer(types.float32), types.CPointer(types.float32)))
def custom_distance(a, b):
    a_arr = carray(a, ndim)
    b_arr = carray(b, ndim)
    # Weighted combination of cosine and L2
    dot = sum(a_arr[i] * b_arr[i] for i in range(ndim))
    norm_a = sum(a_arr[i] ** 2 for i in range(ndim)) ** 0.5
    norm_b = sum(b_arr[i] ** 2 for i in range(ndim)) ** 0.5
    cosine = dot / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0
    l2 = sum((a_arr[i] - b_arr[i]) ** 2 for i in range(ndim)) ** 0.5
    return 0.7 * (1 - cosine) + 0.3 * l2

metric = CompiledMetric(
    pointer=custom_distance.address,
    kind=MetricKind.IP,       # Nearest built-in (used for fallback)
    signature=MetricSignature.ArrayArray,
)
index = Index(ndim=ndim, metric=metric, dtype=np.float32)
```

### Python: Cppyy (Cling JIT)

```python
import cppyy
import cppyy.ll

ndim = 256
cppyy.cppdef(f"""
float custom_metric(float *a, float *b) {{
    float result = 0;
#pragma unroll
    for (size_t i = 0; i != {ndim}; ++i)
        result += a[i] * b[i];
    return 1 - result;
}}
""")

metric = CompiledMetric(
    pointer=cppyy.ll.addressof(cppyy.gbl.custom_metric),
    kind=MetricKind.IP,
    signature=MetricSignature.ArrayArraySize,
)
```

### Python: PeachPy (x86 Assembly)

For maximum performance, write AVX2/AVX-512 assembly directly:

```python
from peachpy import Argument, ptr, const_float_, float_
from peachpy.x86_64 import abi, Function, uarch, isa, GeneralPurposeRegister64, YMMRegister, VMOVUPS, VFMADD231PS, VPERM2F128, VADDPS, VHADDPS, VXORPS, VSUBPS, RETURN, LOAD

a = Argument(ptr(const_float_), name="a")
b = Argument(ptr(const_float_), name="b")

with Function("inner_product", (a, b), float_, target=uarch.default + isa.avx2) as asm_fn:
    reg_a, reg_b = GeneralPurposeRegister64(), GeneralPurposeRegister64()
    LOAD.ARGUMENT(reg_a, a)
    LOAD.ARGUMENT(reg_b, b)
    ymm_a, ymm_b = YMMRegister(), YMMRegister()
    VMOVUPS(ymm_a, [reg_a])
    VMOVUPS(ymm_b, [reg_b])
    ymm_c = YMMRegister()
    VXORPS(ymm_c, ymm_c, ymm_c)
    VFMADD231PS(ymm_c, ymm_a, ymm_b)
    # Reduce...
    ymm_c_perm = YMMRegister()
    VPERM2F128(ymm_c_perm, ymm_c, ymm_c, 1)
    VADDPS(ymm_c, ymm_c, ymm_c_perm)
    VHADDPS(ymm_c, ymm_c, ymm_c)
    VHADDPS(ymm_c, ymm_c, ymm_c)
    ymm_one = YMMRegister()
    VXORPS(ymm_one, ymm_one, ymm_one)
    VSUBPS(ymm_c, ymm_one, ymm_c)
    RETURN(ymm_c.as_xmm)

fn = asm_fn.finalize(abi.detect()).encode().load()
metric = CompiledMetric(
    pointer=fn.loader.code_address,
    kind=MetricKind.IP,
    signature=MetricSignature.ArrayArray,
)
```

### Rust: Custom Metric

```rust
use numkong::SpatialSimilarity;

let image_dim = 768;
let text_dim = 512;
let img_weight = 0.7;
let text_weight = 0.9;

let weighted_distance = Box::new(move |a: *const f32, b: *const f32| unsafe {
    let a_slice = std::slice::from_raw_parts(a, image_dim + text_dim);
    let b_slice = std::slice::from_raw_parts(b, image_dim + text_dim);

    let img_sim = f32::cosine(a_slice[0..image_dim], b_slice[0..image_dim]);
    let txt_sim = f32::cosine(a_slice[image_dim..], b_slice[image_dim..]);
    let sim = img_weight * img_sim + text_weight * txt_sim / (img_weight + text_weight);
    1.0 - sim
});
index.change_metric(weighted_distance);

// Revert
index.change_metric_kind(MetricKind::Cos);
```

### C: Custom Metric

```c
usearch_distance_t custom_callback(void const* a, void const* b, void* state) {
    // Custom distance computation
    return distance;
}

usearch_change_metric(index, custom_callback, NULL, usearch_metric_unknown_k, &error);

// Revert
usearch_change_metric_kind(index, usearch_metric_cos_k, &error);
```

## Filtering with Predicates

Filter results during graph traversal, not post-hoc. This avoids scanning the entire index.

### Rust

```rust
let is_odd = |key: Key| key % 2 == 1;
let results = index.filtered_search(&query, 10, is_odd).unwrap();
```

### C

```c
int is_even(usearch_key_t key, void* state) {
    return (key % 2 == 0);  // non-zero = accept
}

usearch_filtered_search(
    index, &query[0], usearch_scalar_f32_k, 10,
    &is_even, NULL,
    &found_keys[0], &found_distances[0], &error);
```

### Go

```go
handler := &usearch.FilteredSearchHandler{
    Callback: func(key usearch.Key, h *usearch.FilteredSearchHandler) int {
        return int(key % 2 == 0)  // 1 = accept, 0 = reject
    },
}
keys, distances, err := index.FilteredSearch(query, 10, handler)
```

> Python bindings do not currently expose filtered search. Use post-hoc filtering or switch to Rust/C/C++.

## Clustering

The HNSW graph structure itself provides implicit clustering. USearch exposes this for fast KNN-style clustering without separate algorithms.

### Python

```python
clustering = index.cluster(min_count=10, max_count=15, threads=0)

# Centroid keys and their cluster sizes
centroid_keys, sizes = clustering.centroids_popularity

# Plot histogram (requires matplotlib)
clustering.plot_centroids_popularity()

# NetworkX graph of clusters
g = clustering.network

# Members of a specific cluster
members = clustering.members_of(centroid_keys[0])

# Iterative deepening (sub-cluster)
sub_clustering = clustering.subcluster(min_count=5, max_count=10)
```

### C++

```cpp
// Single vector clustering
cluster_result_t result = index.cluster(&vector, index.max_level() / 2);
match_t cluster = result.cluster;

// Full index clustering
index_dense_clustering_config_t config;
config.min_clusters = 1000;
config.max_clusters = 2000;
config.mode = index_dense_clustering_config_t::merge_smallest_k;

clustering_result_t result = cluster(
    queries_begin, queries_end, config,
    &cluster_centroids_keys, &distances_to_centroids,
    thread_pool, progress_bar);
```

Performance: 50K clusters on 1M points is ~100x faster than Scikit-Learn K-Means.

## Joins

Sub-quadratic approximate fuzzy joins between two indexes.

### Python

```python
men = Index(ndim=768, metric='cos')
women = Index(ndim=768, metric='cos')

# Populate both indexes...
pairs = men.join(women, max_proposals=0, exact=False)
# Returns dict mapping keys from `men` to matched keys from `women`
```

Use cases:
- Record linkage / deduplication
- Cross-modal matching (image ↔ text)
- Fuzzy database joins

### C++

```cpp
auto pairs = index_a.join(index_b, max_proposals, exact);
```

## Multi-Index (Indexes)

For billion-scale workloads, split data across multiple smaller indexes.

### Python

```python
from usearch.index import Indexes

# From existing index objects
multi = Indexes(indexes=[index1, index2, index3], threads=0)

# From disk paths
multi = Indexes(paths=['index1.usearch', 'index2.usearch'], view=False, threads=0)

results = multi.search(query, 10)
```

## Variable-Length Vectors (C++ Only)

HNSW does not require fixed-length vectors. C++ exposes this; other bindings do not.

```cpp
index_gt<...> index;
index.add(1, span_t{short_vector, 3});
index.add(2, span_t{long_vector, 128});
```

The custom metric must handle variable lengths (use `MetricSignature.ArrayArraySize` or pass ndim as third argument).

## uint40_t Keys (4B+ Capacity)

For indexes exceeding 4 billion entries:

### C++

```cpp
index_dense_big_t index = index_dense_big_t::make(metric);
// Uses uint40_t internally: 37.5% smaller than uint64_t, addresses up to 1 trillion entries
```

### CMake

```cmake
# Build with big index support
build_profile/bench_cpp --vectors data.fbin -b  # -b flag enables uint40_t
```

Python, Rust, and other bindings do not yet expose this feature.
