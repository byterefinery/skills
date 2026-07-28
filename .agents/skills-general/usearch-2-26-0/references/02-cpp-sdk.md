# C++ SDK

## Installation

### Header-Only (Manual)

Copy `include/usearch/*.hpp` into your project:

```cpp
#include <usearch/index.hpp>
#include <usearch/index_dense.hpp>
```

### CMake FetchContent (Recommended)

```cmake
FetchContent_Declare(usearch GIT_REPOSITORY https://github.com/unum-cloud/USearch.git)
FetchContent_MakeAvailable(usearch)
```

With NumKong SIMD acceleration:

```cmake
cmake -DUSEARCH_USE_NUMKONG=1 -DUSEARCH_USE_OPENMP=1 -DCMAKE_BUILD_TYPE=RelWithDebInfo -B build
```

## Quickstart

```cpp
#include <usearch/index.hpp>
#include <usearch/index_dense.hpp>

using namespace unum::usearch;

int main() {
    metric_punned_t metric(3, metric_kind_t::l2sq_k, scalar_kind_t::f32_k);
    index_dense_t index = index_dense_t::make(metric);

    index.reserve(10);  // Pre-allocate
    float vec[3] = {0.1, 0.3, 0.2};
    index.add(42, &vec[0]);

    auto results = index.search(&vec[0], 5);
    for (std::size_t i = 0; i != results.size(); ++i)
        std::printf("Key: %zu, Dist: %f\n",
            results[i].member.key, results[i].distance);
    return 0;
}
```

## Type System

### Index Types

| Type | Key Size | Use Case |
|------|----------|----------|
| `index_dense_t` | `uint32_t` | Up to 4B entries (default) |
| `index_dense_big_t` | `uint40_t` | 4B to 1T entries, 37.5% smaller than `uint64_t` |
| `index_dense_gt<K, S>` | Custom | Full control over key/slot types |

### Metric Kinds

```cpp
metric_kind_t::cos_k          // Cosine similarity
metric_kind_t::ip_k           // Inner product (normalized)
metric_kind_t::l2sq_k         // Squared Euclidean
metric_kind_t::haversine_k    // Great circle distance (GIS)
metric_kind_t::divergence_k   // Jensen-Shannon divergence
metric_kind_t::pearson_k      // Pearson correlation
metric_kind_t::hamming_k      // Bit-level hamming distance
metric_kind_t::tanimoto_k     // Bit-level Jaccard (Tanimoto)
metric_kind_t::sorensen_k     // Bit-level Dice-Sorensen
```

### Scalar Kinds

```cpp
scalar_kind_t::f64_k    // 64-bit double
scalar_kind_t::f32_k    // 32-bit float
scalar_kind_t::bf16_k   // BFloat16 (recommended for modern CPUs)
scalar_kind_t::f16_k    // IEEE half-precision
scalar_kind_t::e5m2_k   // Float8 (wider range ±57344)
scalar_kind_t::e4m3_k   // Float8 (higher precision ±448)
scalar_kind_t::e3m2_k   // Float6 (MX-compatible ±28)
scalar_kind_t::e2m3_k   // Float6 (MX-compatible ±7.5)
scalar_kind_t::i8_k     // 8-bit signed integer (cosine metrics only)
scalar_kind_t::u8_k     // 8-bit unsigned integer (cosine metrics only)
scalar_kind_t::b1_k     // Single-bit (binary metrics only)
```

## Multi-Type Operations

The `add` function accepts different vector types and casts automatically:

```cpp
double vec_double[3] = {0.1, 0.3, 0.2};
_Float16 vec_half[3] = {0.1, 0.3, 0.2};
index.add(43, span_t{&vec_double[0], 3});
index.add(44, span_t{&vec_half[0], 3});
```

## Serialization

```cpp
index.save("index.usearch");           // Save to disk
index.load("index.usearch");           // Load (copy into memory, writable)
index.view("index.usearch");           // Memory-map (read-only)
```

## Error Handling

USearch does not use exceptions. All operations return result objects:

```cpp
bool success = (bool)index.try_reserve(10);
success = (bool)index.add(42, &vec[0]);
success = (bool)index.search(&vec[0], 5);
```

Use `try_reserve()` over `reserve()` for explicit error checking.

## Multi-Threading

### OpenMP (Parallel Index Construction)

```cpp
#pragma omp parallel for
for (std::size_t i = 0; i < n; ++i)
    index.add(keys[i], vectors[i]);
```

The `add()` function is thread-safe by design.

### Executors

```cpp
std::size_t executor_threads = std::thread::hardware_concurrency() * 4;
executor_default_t executor(executor_threads);

index.reserve(index_limits_t {vectors.size(), executor.size()});
executor.fixed(vectors.size(), [&](std::size_t thread, std::size_t task) {
    index.add(task, vectors[task].data(), index_update_config_t { .thread = thread });
});
```

Available executors:
- `executor_default_t` — internal thread pool
- `executor_openmp_t` — OpenMP runtime
- `executor_stl_t` — `std::thread` instances
- `dummy_executor_t` — sequential execution

## Clustering

### Single-Vector Clustering

```cpp
some_scalar_t vector[3] = {0.1, 0.3, 0.2};
cluster_result_t result = index.cluster(&vector, index.max_level() / 2);

match_t cluster = result.cluster;
member_cref_t member = cluster.member;
distance_t distance = cluster.distance;
```

The level parameter (0 = all levels except bottom, N = level N only) controls the granularity.

### Full Index Clustering

```cpp
index_dense_clustering_config_t config;
config.min_clusters = 1000;
config.max_clusters = 2000;
config.mode = index_dense_clustering_config_t::merge_smallest_k;

vector_key_t cluster_centroids_keys[queries_count];
distance_t distances_to_centroids[queries_count];

clustering_result_t result = cluster(
    queries_begin, queries_end,
    config,
    &cluster_centroids_keys, &distances_to_centroids,
    thread_pool, progress_bar);
```

## User-Defined Metrics

Wrap a custom distance function into `metric_punned_t` (a trivial type, unlike `std::function`):

```cpp
auto custom_metric = [](const void* a, const void* b, void*) -> distance_t {
    // Custom distance computation
    return distance;
};
metric_punned_t metric(768, custom_metric, metric_kind_t::unknown_k, scalar_kind_t::f32_k);
```

## Advanced Template Interface

```cpp
template <
    typename distance_at = default_distance_t,              // float
    typename key_at = default_key_t,                        // int64_t, uuid_t
    typename compressed_slot_at = default_slot_t,           // uint32_t, uint40_t
    typename dynamic_allocator_at = std::allocator<byte_t>,
    typename tape_allocator_at = dynamic_allocator_at
>
class index_gt;
```

This low-level interface gives full control over memory layout, allocation strategy, and key types. Required for custom allocators, embedded systems, or database integrations.

## Variable-Length Vectors

C++ supports variable-length vectors (vectors of different dimensions in the same index). Other language bindings do not expose this feature.

```cpp
index_gt<...> index;
index.add(1, span_t{short_vector, 3});
index.add(2, span_t{long_vector, 128});
```

The custom metric must handle variable lengths.
