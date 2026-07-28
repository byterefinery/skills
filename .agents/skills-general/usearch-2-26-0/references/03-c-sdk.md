# C SDK

## Installation

### CMake

```cmake
FetchContent_Declare(usearch GIT_REPOSITORY https://github.com/unum-cloud/USearch.git)
FetchContent_MakeAvailable(usearch)
```

### Precompiled Binaries

Download from [GitHub Releases](https://github.com/unum-cloud/USearch/releases): shared libraries and `usearch.h` header for Linux, macOS, Windows.

## Quickstart

```c
#include <stdio.h>
#include <assert.h>
#include <usearch/usearch.h>

int main() {
    size_t dimensions = 128;
    usearch_error_t error = NULL;
    usearch_init_options_t opts = {
        .metric_kind = usearch_metric_cos_k,
        .scalar_kind = usearch_scalar_f16_k,
        .dimensions = dimensions,
        .expansion_add = 0,    // 0 = defaults
        .expansion_search = 0  // 0 = defaults
    };
    usearch_index_t index = usearch_init(&opts, &error);

    usearch_reserve(index, 1000, &error);
    if (error) goto cleanup;

    float vector[dimensions];  // Fill with data
    usearch_add(index, 42, &vector[0], usearch_scalar_f32_k, &error);
    if (error) goto cleanup;

    assert(usearch_size(index, &error) == 1);
    assert(usearch_contains(index, 42, &error));

    // Search
    usearch_key_t found_keys[10];
    usearch_distance_t found_distances[10];
    size_t found_count = usearch_search(
        index, &vector[0], usearch_scalar_f32_k, 10,
        &found_keys[0], &found_distances[0], &error);

cleanup:
    if (error) fprintf(stderr, "Error: %s\n", error);
    if (index) usearch_free(index, &error);
    return error ? 1 : 0;
}
```

## Error Handling Pattern

Every function takes a `usearch_error_t*` (output). The idiomatic C pattern:

```c
usearch_error_t error = NULL;
// ... operations ...
if (error) goto cleanup;
// ... more operations ...
if (error) goto cleanup;

cleanup:
    if (error) fprintf(stderr, "Error: %s\n", error);
    usearch_free(index, &error);
```

## Serialization

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

// Metadata from file or buffer
usearch_init_options_t opts;
usearch_metadata("index.usearch", &opts, &error);
usearch_metadata_buffer(buffer, bytes, &opts, &error);
```

## Metrics

Built-in metrics:

| Constant | Description |
|----------|-------------|
| `usearch_metric_cos_k` | Cosine similarity |
| `usearch_metric_ip_k` | Inner product |
| `usearch_metric_l2sq_k` | Squared Euclidean |
| `usearch_metric_haversine_k` | Great circle distance |
| `usearch_metric_divergence_k` | Jensen-Shannon divergence |
| `usearch_metric_pearson_k` | Pearson correlation |
| `usearch_metric_hamming_k` | Bit-level hamming |
| `usearch_metric_tanimoto_k` | Bit-level Tanimoto (Jaccard) |
| `usearch_metric_sorensen_k` | Bit-level Sorensen (Dice) |

### User-Defined Metrics

```c
usearch_distance_t callback(void const* a, void const* b, void* state) {
    // Custom distance
    return distance;
}

usearch_change_metric(index, callback, NULL, usearch_metric_unknown_k, &error);

// Revert to built-in
usearch_change_metric_kind(index, usearch_metric_cos_k, &error);
```

## Filtering with Predicates

```c
int is_odd(usearch_key_t key, void* state) {
    return key % 2;  // non-zero = accept, zero = reject
}

usearch_key_t found_keys[10];
usearch_distance_t found_distances[10];
usearch_filtered_search(
    index, &query[0], usearch_scalar_f32_k, 10,
    &is_odd, NULL,  // callback, state
    &found_keys[0], &found_distances[0], &error);
```

## Extracting, Updating, Removing

```c
// Retrieve vector
float recovered_vector[dimensions];
size_t count = usearch_get(index, 42, 1,
    &recovered_vector[0], usearch_scalar_f32_k, &error);

// Rename key
size_t renamed = usearch_rename(index, 42, 43, &error);

// Remove key
size_t removed = usearch_remove(index, 43, &error);

// Multi-vector get (up to 10 vectors for key 42)
float many_vectors[10][dimensions];
size_t count = usearch_get(index, 42, 10,
    &many_vectors[0][0], usearch_scalar_f32_k, &error);
```

## Exact Search

### Pairwise Distance

```c
float vector_a[dimensions], vector_b[dimensions];
usearch_distance_t distance = usearch_distance(
    &vector_a[0], &vector_b[0],
    usearch_scalar_f32_k, dimensions,
    usearch_metric_cos_k, &error);
```

### Batch Exact Search

```c
size_t threads = 0;  // 0 = auto
size_t top_k = 10;

usearch_key_t resulting_keys[queries_count][top_k];
usearch_distance_t resulting_distances[queries_count][top_k];

usearch_exact_search(
    &dataset[0][0], dataset_count, dimensions * sizeof(nk_f16_t),
    &queries[0][0], queries_count, dimensions * sizeof(nk_f16_t),
    usearch_scalar_f16_k, top_k, threads,
    &resulting_keys[0][0], sizeof(usearch_key_t) * top_k,
    &resulting_distances[0][0], sizeof(usearch_distance_t) * top_k,
    &error);
```

## Concurrency

```c
// Configure thread pools
usearch_change_threads_add(index, omp_get_max_threads(), &error);
usearch_change_threads_search(index, omp_get_max_threads(), &error);

#pragma omp parallel for
for (size_t i = 0; i < 1000; i++) {
    usearch_add(index, i, &vector[0], usearch_scalar_f32_k, &error);
}

#pragma omp parallel for
for (size_t i = 0; i < 1000; i++) {
    usearch_key_t found_keys[10];
    usearch_distance_t found_distances[10];
    size_t found = usearch_search(
        index, &vector[0], usearch_scalar_f32_k, 10,
        &found_keys[0], &found_distances[0], &error);
}
```

## Performance Tuning

```c
// Read current settings
printf("Connectivity: %zu\n", usearch_connectivity(index, &error));
printf("Add expansion: %zu\n", usearch_expansion_add(index, &error));
printf("Search expansion: %zu\n", usearch_expansion_search(index, &error));

// Change expansion (connectivity is fixed after creation)
usearch_change_expansion_add(index, 32, &error);
usearch_change_expansion_search(index, 32, &error);

// Hardware info
printf("SIMD: %s\n", usearch_hardware_acceleration(index, &error));
printf("Memory: %zu bytes\n", usearch_memory_usage(index, &error));
```
