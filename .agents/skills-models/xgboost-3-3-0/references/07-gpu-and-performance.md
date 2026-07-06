# GPU and Performance

## GPU Setup

### Device Parameter

```python
# CPU (default)
clf = xgb.XGBClassifier()

# Any available GPU
clf = xgb.XGBClassifier(device="gpu")       # or "cuda"

# Specific GPU
clf = xgb.XGBClassifier(device="cuda:0")     # GPU 0
clf = xgb.XGBClassifier(device="cuda:1")     # GPU 1
```

### Tree Methods on GPU

| Tree Method | GPU Support | Notes |
|---|---|---|
| `hist` | ✅ Full | Default; fastest on GPU |
| `approx` | ✅ Full | Good for very wide datasets |
| `exact` | ❌ | CPU only |

```python
# GPU + hist (recommended)
clf = xgb.XGBClassifier(device="cuda", tree_method="hist")

# GPU + approx
clf = xgb.XGBClassifier(device="cuda", tree_method="approx")
```

### GPU Data

For zero-copy GPU training, keep data on GPU:

```python
import cupy as cp
import cudf

# CuPy arrays
X_gpu = cp.asarray(X_cpu)
y_gpu = cp.asarray(y_cpu)
clf = xgb.XGBClassifier(device="cuda")
clf.fit(X_gpu, y_gpu)

# cuDF DataFrame
gdf = cudf.read_csv("data.csv")
clf.fit(gdf.drop("target", axis=1), gdf["target"])
```

When data is on CPU but `device="cuda"`, XGBoost transfers data internally. For repeated training, keep data on GPU.

### RAPIDS Memory Manager

```python
import xgboost as xgb

# Enable RMM for GPU memory pooling
xgb.set_config(use_rmm=True)

# Or via context
with xgb.config_context(use_rmm=True):
    model = xgb.train(params, dtrain, num_boost_round=100)
```

### CUDA Async Pool (3.2.0+)

```python
xgb.set_config(use_cuda_async_pool=True)
```

Experimental. Not compatible with RMM.

## Performance Tuning

### Tree Method Selection

| Scenario | Recommended Method |
|---|---|
| Most cases | `hist` (default) |
| Very small datasets (< 1000 rows) | `exact` |
| Very wide datasets (100K+ features) | `approx` or `hist` |
| GPU training | `hist` or `approx` |
| Categorical features | `hist` (required) |

### Memory Optimization

#### QuantileDMatrix

```python
# Automatic (sklearn + hist)
clf = xgb.XGBClassifier(tree_method="hist")  # Uses QuantileDMatrix internally

# Manual (native API)
qdm = xgb.QuantileDMatrix(X, label=y, max_bin=256)
model = xgb.train(params, qdm, num_boost_round=200)
```

**Memory savings:** QuantileDMatrix quantizes features to bins, reducing memory from `O(n × d × 4 bytes)` to `O(n × d × 2 bytes)` plus a small histogram cache.

#### max_bin

```python
# Fewer bins = less memory, slightly less accuracy
qdm = xgb.QuantileDMatrix(X, label=y, max_bin=128)  # Default: 256
```

#### max_cached_hist_node

```python
# Limit histogram cache for deep trees
params = {"max_cached_hist_node": 32768}  # Default: 65536
```

Critical for deep trees (`max_depth > 10`) where cache grows exponentially.

### Thread Control

```python
# Sklearn
clf = xgb.XGBClassifier(n_jobs=8)

# Native
params = {"nthread": 8}
dtrain = xgb.DMatrix(X, label=y, nthread=8)

# Global
xgb.set_config(nthread=8)
```

**Guidelines:**
- `n_jobs=-1` uses all cores; fine for single-model training
- Pin to specific count in production/shared environments
- Match `nthread` in DMatrix construction to `nthread` in training
- Oversubscription (XGBoost threads + other processes) degrades performance

### Batch Size for DataIter

```python
# Larger batches = better throughput, more memory
iterator = MyDataIter(data, label, batch_size=8192)
```

Tune based on available memory and data characteristics.

### Gradient-Based Sampling

```python
clf = xgb.XGBClassifier(
    sampling_method="gradient_based",
    subsample=0.1,  # Can go much lower than uniform sampling
    tree_method="hist",  # Required for gradient_based
)
```

Gradient-based sampling selects instances proportional to gradient magnitude. Allows `subsample` as low as 0.1 without accuracy loss. Not supported with `exact` tree method.

## Performance Profiling

### Verbosity

```python
# More verbose output for debugging
params = {"verbosity": 3}  # 0=silent, 1=warning, 2=info, 3=debug

# Or globally
xgb.set_config(verbosity=2)
```

### Build Info

```python
import xgboost as xgb

print(xgb.build_info())
# Shows: USE_CUDA, USE_OPENMP, USE_HYPRE, etc.
```

### Training Time Breakdown

With `verbosity=2`, XGBoost prints per-iteration timing:

```
[0]	train-rmse:0.5000	val-rmse:0.5500
Training time: 0.123s
```

## Common Performance Issues

### CPU → GPU Transfer Bottleneck

If data lives on CPU but training is on GPU, each iteration incurs transfer overhead. For repeated training (hyperparameter search), move data to GPU once:

```python
X_gpu = cp.asarray(X_cpu)  # Transfer once
for params in param_grid:
    clf = xgb.XGBClassifier(device="cuda", **params)
    clf.fit(X_gpu, y_gpu)  # No transfer overhead
```

### Deep Trees on hist

Memory grows exponentially with tree depth. For `max_depth > 10`:
- Reduce `max_cached_hist_node`
- Consider `max_leaves` with `grow_policy="lossguide"` instead
- Use `approx` if GPU is not available

### Too Many Features

For datasets with 100K+ features:
- Use `colsample_bytree < 1.0` to reduce split search space
- `approx` tree method may be faster than `hist` for extremely wide data
- Consider feature selection before training

### Small Datasets

For < 10,000 rows:
- `exact` tree method can be competitive (or faster)
- GPU overhead may exceed benefit; stick with CPU
- `max_depth` can be lower (3–6)

## GPU Memory Estimation

Approximate GPU memory usage:

```
GPU RAM ≈ model_size + data_size + histogram_cache

model_size ≈ n_trees × avg_nodes_per_tree × 16 bytes
data_size ≈ n_samples × n_features × 4 bytes (float32)
histogram_cache ≈ max_cached_hist_node × max_bin × 8 bytes
```

For a typical model:
- 200 trees, 64 nodes/tree: ~1 MB model
- 1M rows × 100 features: ~400 MB data
- 65536 cached nodes × 256 bins: ~128 MB cache

Total: ~530 MB for this configuration.
