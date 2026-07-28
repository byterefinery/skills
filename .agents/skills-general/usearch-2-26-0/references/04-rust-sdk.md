# Rust SDK

## Installation

```sh
cargo add usearch
```

Or in `Cargo.toml`:

```toml
[dependencies]
usearch = "2.26.0"
```

### Features

```toml
[dependencies]
usearch = { version = "2.26.0", default-features = false }

# Enable specific features
usearch = { version = "2.26.0", features = ["numkong", "openmp", "fp16lib"] }
```

- `numkong` (default) — dynamic SIMD dispatch for x86/ARM
- `openmp` — OpenMP runtime for parallelism (Linux only, better multi-core performance)
- `fp16lib` — C-layer `fp16` emulation for CPUs without native half-precision support

## Quickstart

```rust
use usearch::{Index, IndexOptions, MetricKind, ScalarKind, new_index};

let options = IndexOptions {
    dimensions: 3,
    metric: MetricKind::IP,           // or ::L2sq, ::Cos, ...
    quantization: ScalarKind::BF16,   // or ::F32, ::F16, ::E5M2, ::E4M3, ::E3M2, ::E2M3, ::U8, ::I8, ::B1x8
    connectivity: 0,                  // 0 = auto
    expansion_add: 0,                 // 0 = auto
    expansion_search: 0,              // 0 = auto
};

let index: Index = new_index(&options).unwrap();

assert!(index.reserve(10).is_ok());
assert!(index.capacity() >= 10);
assert_eq!(index.dimensions(), 3);
assert_eq!(index.size(), 0);

let first: [f32; 3] = [0.2, 0.1, 0.2];
let second: [f32; 3] = [0.2, 0.1, 0.2];

assert!(index.add(42, &first).is_ok());
assert!(index.add(43, &second).is_ok());
assert_eq!(index.size(), 2);

let results = index.search(&first, 10).unwrap();
assert_eq!(results.keys.len(), 2);
```

## Serialization

```rust
// File-based
assert!(index.save("index.usearch").is_ok());
assert!(index.load("index.usearch").is_ok());
assert!(index.view("index.usearch").is_ok());

// In-memory buffer
let mut buffer = Vec::new();
assert!(index.save_to_buffer(&mut buffer).is_ok());
assert!(index.load_from_buffer(&buffer).is_ok());
assert!(index.view_from_buffer(&buffer).is_ok());

// Restore without knowing original parameters
let meta = Index::metadata("index.usearch").unwrap();
println!("dim={}, metric={:?}, dtype={:?}", meta.dimensions, meta.metric, meta.quantization);

let index = Index::restore("index.usearch").unwrap();

// Memory-mapped restore
let index = Index::restore_view("index.usearch").unwrap();
let index = Index::restore_from_buffer(&buffer).unwrap();
```

## Metrics

| Constant | Description |
|----------|-------------|
| `MetricKind::IP` | Inner product |
| `MetricKind::L2sq` | Squared Euclidean |
| `MetricKind::Cos` | Cosine similarity |
| `MetricKind::Pearson` | Pearson correlation |
| `MetricKind::Haversine` | Great circle distance |
| `MetricKind::Divergence` | Jensen-Shannon divergence |
| `MetricKind::Hamming` | Bit-level hamming |
| `MetricKind::Tanimoto` | Bit-level Tanimoto (Jaccard) |
| `MetricKind::Sorensen` | Bit-level Sorensen (Dice) |

### User-Defined Metrics

```rust
use numkong::SpatialSimilarity;

let image_dimensions: usize = 768;
let text_dimensions: usize = 512;
let image_weights: f32 = 0.7;
let text_weights: f32 = 0.9;

let weighted_distance = Box::new(move |a: *const f32, b: *const f32| unsafe {
    let a_slice = std::slice::from_raw_parts(a, image_dimensions + text_dimensions);
    let b_slice = std::slice::from_raw_parts(b, image_dimensions + text_dimensions);

    let image_sim = f32::cosine(a_slice[0..image_dimensions], b_slice[0..image_dimensions]);
    let text_sim = f32::cosine(a_slice[image_dimensions..], b_slice[image_dimensions..]);
    let sim = image_weights * image_sim + text_weights * text_sim / (image_weights + text_weights);

    1.0 - sim
});
index.change_metric(weighted_distance);

// Revert to built-in
index.change_metric_kind(MetricKind::Cos);
```

## Filtering with Predicates

```rust
let is_odd = |key: Key| key % 2 == 1;
let query = vec![0.2, 0.1, 0.2, 0.1, 0.3];
let results = index.filtered_search(&query, 10, is_odd).unwrap();

assert!(
    results.keys.iter().all(|&key| key % 2 == 1),
    "All keys must be odd"
);
```

## Half-Precision (f16)

Rust has no native `f16`, but USearch provides `usearch::f16`:

```rust
use usearch::f16 as USearchF16;
use half::f16 as HalfF16;

let vector_a: Vec<HalfF16> = /* ... */;
let buffer_a: &[USearchF16] = unsafe {
    std::slice::from_raw_parts(
        vector_a.as_ptr() as *const USearchF16,
        vector_a.len()
    )
};

index.add(42, buffer_a);
```

## Binary Vectors

```rust
let index = Index::new(&IndexOptions {
    dimensions: 8,
    metric: MetricKind::Hamming,
    quantization: ScalarKind::B1x8,
    ..Default::default()
}).unwrap();

let vector42: Vec<b1x8> = vec![b1x8(0b00001111)];
let vector43: Vec<b1x8> = vec![b1x8(0b11110000)];
let query: Vec<b1x8> = vec![b1x8(0b01111000)];

index.reserve(10).unwrap();
index.add(42, &vector42).unwrap();
index.add(43, &vector43).unwrap();

let results = index.search(&query, 5).unwrap();
assert_eq!(results.keys[0], 43);  // 2 bits differ
assert_eq!(results.distances[0], 2.0);
assert_eq!(results.keys[1], 42);  // 6 bits differ
assert_eq!(results.distances[1], 6.0);
```

## Performance Tuning

```rust
// Read current settings
println!("Add expansion: {}", index.expansion_add());
println!("Search expansion: {}", index.expansion_search());

// Change dynamically
index.change_expansion_add(32);
index.change_expansion_search(32);

// Hardware info
println!("SIMD: {}", index.hardware_acceleration());
println!("Memory: {} bytes", index.memory_usage());
```

## API Reference

Full documentation: [docs.rs/usearch](https://docs.rs/usearch/latest/usearch/struct.Index.html)
