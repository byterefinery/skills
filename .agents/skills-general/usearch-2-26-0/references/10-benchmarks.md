# Benchmarks

## Hyper-parameters

All HNSW implementations share these tuning parameters:

| Parameter | USearch Default | hnswlib | FAISS |
|-----------|----------------|---------|-------|
| Connectivity (M) | 16 | 16 | 32 |
| EF @ Add (efConstruction) | 128 | 200 | 40 |
| EF @ Search (ef) | 64 | 10 | 16 |

## Performance Numbers

AWS c7g.metal (Graviton 3, 64 cores), 256-dim `f32` vectors:

### Connectivity Variations

| Connectivity | EF@A | EF@S | Add QPS | Search QPS | Recall@1 |
|-------------|------|------|---------|------------|----------|
| 16 | 128 | 64 | 75,640 | 131,654 | 99.3% |
| 12 | 128 | 64 | 81,747 | 149,728 | 99.0% |
| 32 | 128 | 64 | 64,368 | 104,050 | 99.4% |

### Expansion Factor Variations

| EF@A | EF@S | Add QPS | Search QPS | Recall@1 |
|------|------|---------|------------|----------|
| 128 | 64 | 75,640 | 131,654 | 99.3% |
| 64 | 32 | 128,644 | 228,422 | 97.2% |
| 256 | 128 | 39,981 | 69,065 | 99.2% |

### Quantization Variations

| Type | Add QPS | Search QPS | Recall@1 |
|------|---------|------------|----------|
| `f32` | 87,995 | 171,856 | 99.1% |
| `f16` | 87,270 | 153,788 | 98.4% |
| `i8` | 115,923 | 274,653 | 98.9% |

## Benchmarking Tools

### RetriEval (Recommended)

For reproducible recall-vs-throughput sweeps across the full quantization matrix: [RetriEval](https://github.com/ashvardanian/RetriEval)

### C++ Benchmark Binary

```sh
git submodule update --init --recursive
cmake -DUSEARCH_BUILD_BENCH_CPP=1 -DUSEARCH_BUILD_TEST_C=1 \
    -DUSEARCH_USE_NUMKONG=1 -DUSEARCH_USE_OPENMP=1 \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo -B build_profile
cmake --build build_profile --config RelWithDebInfo --parallel
build_profile/bench_cpp --help
```

Usage:

```sh
build_profile/bench_cpp \
    --vectors datasets/wiki_1M/base.1M.fbin \
    --queries datasets/wiki_1M/query.public.100K.fbin \
    --neighbors datasets/wiki_1M/groundtruth.public.100K.ibin \
    --dtype bf16 --metric ip
```

Options:
- `--vectors` — base dataset (`.fbin`, `.f32bin`, `.i8bin`, `.u8bin`)
- `--queries` — query vectors
- `--neighbors` — ground truth (`.ibin`)
- `-o` — output index path
- `-b` — enable `uint40_t` for 4B+ entries
- `-j` — thread count (0 = auto)
- `-c` — connectivity
- `--expansion-add` / `--expansion-search`
- `--rows-skip` / `--rows-take` — subset of vectors
- `--dtype` — quantization type
- `--metric` — distance metric

### Python Benchmarks

```sh
python python/scripts/bench.py --help       # Approximate search
python python/scripts/bench_exact.py --help # Exact search
python python/scripts/bench_cluster.py --help # Clustering
```

These are smoke tests and ad-hoc profiling helpers. Use RetriEval for published numbers.

## Datasets

### ~1M Scale (Development & Testing)

| Dataset | Type | Dimensions | Metric | Size | Ground Truth |
|---------|------|-----------|--------|------|-------------|
| [Unum Wiki][wiki] | `f32` | 256 | IP | 1 GB | 100K queries |
| [Unum CC-3M][cc] | `f32` | 256 | IP | 3 GB | cross-modal |
| [Arxiv E5][arxiv] | `f32` | 768 | IP | 6 GB | cross-modal |

### ~10M Scale

| Dataset | Type | Dimensions | Metric | Size | Ground Truth |
|---------|------|-----------|--------|------|-------------|
| [BIGANN SIFT][bigann] | `u8` | 128 | L2 | 1.2 GB | 10K queries |
| [Turing-ANNS][turing] | `f32` | 100 | L2 | 3.7 GB | 100K queries |
| [Yandex Deep][deep] | `f32` | 96 | L2 | 3.6 GB | no subset GT |

### ~100M Scale

| Dataset | Type | Dimensions | Metric | Size | Ground Truth |
|---------|------|-----------|--------|------|-------------|
| [BIGANN SIFT][bigann] | `u8` | 128 | L2 | 12 GB | 10K queries |
| [Turing-ANNS][turing] | `f32` | 100 | L2 | 37 GB | 100K queries |
| [SpaceV][spacev] | `i8` | 100 | L2 | 9.3 GB | 30K queries |

### ~1B Scale

| Dataset | Type | Dimensions | Metric | Size | Ground Truth |
|---------|------|-----------|--------|------|-------------|
| [BIGANN SIFT][bigann] | `u8` | 128 | L2 | 119 GB | 10K queries |
| [Turing-ANNS][turing] | `f32` | 100 | L2 | 373 GB | 100K queries |
| [SpaceV][spacev] | `i8` | 100 | L2 | 93 GB | 30K queries |
| [Yandex T2I][t2i] | `f32` | 200 | Cos | 750 GB | 100K queries |
| [Yandex Deep][deep] | `f32` | 96 | L2 | 358 GB | 10K queries |

## Downloading Datasets

### Unum Wiki 1M

```sh
mkdir -p datasets/wiki_1M/
wget -nc https://huggingface.co/datasets/unum-cloud/ann-wiki-1m/resolve/main/base.1M.fbin -P datasets/wiki_1M/
wget -nc https://huggingface.co/datasets/unum-cloud/ann-wiki-1m/resolve/main/query.public.100K.fbin -P datasets/wiki_1M/
wget -nc https://huggingface.co/datasets/unum-cloud/ann-wiki-1m/resolve/main/groundtruth.public.100K.ibin -P datasets/wiki_1M/
```

### Yandex T2I 1B

```sh
mkdir -p datasets/t2i_1B/
wget -nc https://storage.yandexcloud.net/yandex-research/ann-datasets/T2I/base.1B.fbin -P datasets/t2i_1B/
wget -nc https://storage.yandexcloud.net/yandex-research/ann-datasets/T2I/query.public.100K.fbin -P datasets/t2i_1B/
wget -nc https://storage.yandexcloud.net/yandex-research/ann-datasets/T2I/groundtruth.public.100K.ibin -P datasets/t2i_1B/
```

### BIGANN SIFT 10M (subset via range request)

```sh
mkdir -p datasets/sift_10M/
wget -nc https://dl.fbaipublicfiles.com/billion-scale-ann-benchmarks/bigann/query.public.10K.u8bin -P datasets/sift_10M/
wget -nc https://dl.fbaipublicfiles.com/billion-scale-ann-benchmarks/GT_10M/bigann-10M -O datasets/sift_10M/groundtruth.public.10K.ibin
wget --header="Range: bytes=0-1280000007" \
    https://dl.fbaipublicfiles.com/billion-scale-ann-benchmarks/bigann/base.1B.u8bin \
    -O datasets/sift_10M/base.10M.u8bin
python3 -c "
import struct
with open('datasets/sift_10M/base.10M.u8bin', 'r+b') as f:
    f.write(struct.pack('I', 10_000_000))
"
```

> **Warning:** Yandex Deep and T2I only publish ground truth for the full 1B dataset. Using 1B ground truth with smaller subsets produces misleadingly low recall. Use subsets only for throughput/latency testing.

## Profiling

### perf

```sh
# Statistics
sudo -E perf stat -d build_profile/bench_cpp ...

# Memory access patterns
sudo -E perf mem -d build_profile/bench_cpp ...

# Sampling
sudo -E perf record -F 1000 build_profile/bench_cpp ...
perf record -d -e arm_spe// -- build_profile/bench_cpp ..
```

### Cache Metrics

```sh
sudo perf stat -e 'faults,dTLB-loads,dTLB-load-misses,cache-misses,cache-references' \
    build_profile/bench_cpp ...
```

### Huge Pages

If cache miss rates are high (>90%), enable Huge Pages:

```sh
sudo cat /proc/sys/vm/nr_hugepages
sudo sysctl -w vm.nr_hugepages=2048
sudo reboot
```

[wiki]: https://huggingface.co/datasets/unum-cloud/ann-wiki-1m
[cc]: https://huggingface.co/datasets/unum-cloud/ann-cc-3m
[arxiv]: https://huggingface.co/datasets/unum-cloud/ann-arxiv-2m
[bigann]: https://dl.fbaipublicfiles.com/billion-scale-ann-benchmarks/bigann/
[turing]: https://learning2hash.github.io/publications/microsoftturinganns1B/
[deep]: https://research.yandex.com/blog/benchmarks-for-billion-scale-similarity-search
[t2i]: https://research.yandex.com/blog/benchmarks-for-billion-scale-similarity-search
[spacev]: https://github.com/ashvardanian/SpaceV
