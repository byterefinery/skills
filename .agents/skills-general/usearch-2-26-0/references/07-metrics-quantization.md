# Metrics and Quantization

## Distance Metrics

### Vector Metrics

| Metric | Symbol | Formula | Use Case |
|--------|--------|---------|----------|
| Cosine | `cos` | `1 - Σ(aᵢ·bᵢ) / (‖a‖·‖b‖)` | Text embeddings, semantic search |
| Inner Product | `ip` | `1 - Σ(aᵢ·bᵢ)` | Normalized vectors, dot product |
| Squared Euclidean | `l2sq` | `Σ(aᵢ - bᵢ)²` | Raw feature vectors, image features |
| Pearson | `pearson` | Correlation distance | Probability distributions |
| Haversine | `haversine` | Great circle distance | GIS, lat/lon coordinates |
| Divergence | `divergence` | Jensen-Shannon divergence | Probability distributions |

### Binary Metrics

| Metric | Symbol | Formula | Use Case |
|--------|--------|---------|----------|
| Hamming | `hamming` | Number of differing bits | Hash comparison, fingerprints |
| Tanimoto | `tanimoto` | `1 - |A∩B| / |A∪B|` | Molecular fingerprints (RDKit) |
| Sorensen | `sorensen` | Dice coefficient | Binary feature comparison |

### Metric Selection Guide

- **Text/semantic embeddings** → `cos` (cosine) or `ip` (inner product, if vectors are pre-normalized)
- **Image features (SIFT, etc.)** → `l2sq` (squared Euclidean)
- **Geospatial** → `haversine` (lat/lon as 2D vectors)
- **Molecular/chemistry** → `tanimoto` (binary fingerprints)
- **Probability distributions** → `divergence` (Jensen-Shannon) or `pearson`

## Scalar Types (Quantization)

| Type | Bits | Range | Best For |
|------|------|-------|----------|
| `f64` | 64 | ~1.7×10³⁰⁸ | Maximum precision |
| `f32` | 32 | ~3.4×10³⁸ | Default NumPy type |
| `bf16` | 16 | ~3.4×10³⁸ | **Recommended default on modern CPUs** |
| `f16` | 16 | ~6.5×10⁴ | Widely supported half-precision |
| `e5m2` | 8 | ±57344 | Float8, wider range |
| `e4m3` | 8 | ±448 | Float8, higher precision |
| `e3m2` | 6 (padded to 8) | ±28 | Float6, MX-compatible |
| `e2m3` | 6 (padded to 8) | ±7.5 | Float6, MX-compatible |
| `i8` | 8 | [-127, 127] | Cosine-like metrics only |
| `u8` | 8 | [0, 255] | Cosine-like metrics only |
| `b1` | 1 | {0, 1} | Binary metrics only |

### Quantization Trade-offs

| Type | Memory vs f32 | Speed vs f32 | Precision Loss |
|------|---------------|--------------|----------------|
| `bf16` | 50% | ~1.2x | Minimal on modern CPUs |
| `f16` | 50% | ~1.1x | Small (depends on data) |
| `i8` | 75% | ~2x | Small for cosine metrics |
| `b1` | 97% | ~10x+ | Only for binary use cases |

> On AWS Graviton 3 (64 cores), 256-dim vectors: `i8` achieves 274K QPS search vs 172K for `f32` with 98.9% vs 99.1% recall@1.

## Quantization Rules

### `i8` / `u8` (Integer Quantization)

- **Only valid with cosine-like metrics** (`cos`, `ip`)
- Vectors are normalized to unit length, then scaled to [-127, 127] or [0, 255]
- Using with `l2sq` produces meaningless results
- `get()` returns quantized values, not originals

### `b1` (Binary Quantization)

- **Only valid with binary metrics** (`hamming`, `tanimoto`, `sorensen`)
- Positive values → `1`, zero/negative → `0`
- Common in chemistry (molecular fingerprints) and information retrieval

### `bf16` (BFloat16)

- **Recommended default** for modern CPUs (Intel Sapphire Rapids, AMD Zen 4+)
- Same exponent range as `f32`, truncated mantissa
- Hardware acceleration via AVX-512 / ARM SVE
- Check with: `index.hardware_acceleration` (prints CPU codename like "sapphire" or "ice")

## Hardware Acceleration

USearch uses [NumKong](https://github.com/ashvardanian/numkong) for SIMD-accelerated distance kernels. Over 100 kernel variants for x86 (SSE, AVX2, AVX-512 with masked loads) and ARM (NEON, SVE).

```python
from usearch.index import Index

# Check hardware acceleration level
index = Index(ndim=768, metric="cos", dtype="f16")
print(index.hardware_acceleration)  # e.g., "sapphire" (AVX-512) or "ice" (AVX2)
```

Acceleration levels (best to worst):
1. **Sapphire** — AVX-512 with BF16/VNNI (Intel Sapphire Rapids)
2. **Gold** — AVX-512 F+D (Intel Ice Lake)
3. **Ice** — AVX2 (broad x86 coverage)
4. **Silver** — SSE4.2 (older x86)
5. **ARM SVE** — Scalable Vector Extension (ARM)
6. **ARM NEON** — Standard ARM SIMD
7. **Fallback** — Scalar software implementation

## Checking Hardware Support

```python
# Python
from usearch.index import Index
print(Index(ndim=768, metric="cos", dtype="f16").hardware_acceleration)

# C++
std::cout << index.hardware_acceleration() << std::endl;

# Rust
println!("{}", index.hardware_acceleration());

# C
printf("%s\n", usearch_hardware_acceleration(index, &error));
```

## Memory Usage

```python
# Python
print(index.memory_usage())  # bytes

# C
printf("%zu bytes\n", usearch_memory_usage(index, &error));
```

Approximate memory per vector:
- `f32`: `4 × ndim` bytes + graph overhead (~20-40 bytes per vector for neighbors)
- `bf16`/`f16`: `2 × ndim` bytes + graph overhead
- `i8`/`u8`: `1 × ndim` bytes + graph overhead
- `b1`: `ndim / 8` bytes + graph overhead

For 1M vectors of 768 dimensions:
- `f32`: ~3 GB + overhead
- `bf16`: ~1.5 GB + overhead
- `i8`: ~768 MB + overhead
