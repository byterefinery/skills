# TabPFN-3 — Performance Tips

## GPU Setup

GPU is strongly recommended. Even older GPUs with ~8GB VRAM work well; 16GB needed for some large datasets.

```python
clf = TabPFNClassifier(device="cuda")
```

For Apple Silicon/MPS, install PyTorch nightly after `2.13.0.dev20260510` for flash attention support:

```bash
pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cpu
```

Set memory fraction to prevent system crashes:

```bash
export TABPFN_MPS_MEMORY_FRACTION=0.7
```

## Batch Prediction

Each `predict()` call recomputes the full training context. Batch test rows together:

```python
# Slow — 100 separate calls
for row in X_test:
    clf.predict(row)

# Fast — single batch call
predictions = clf.predict(X_test)
```

For very large test sets, split into chunks of ~1,000 samples:

```python
import numpy as np

chunk_size = 1000
predictions = []
for i in range(0, len(X_test), chunk_size):
    chunk = X_test[i:i + chunk_size]
    predictions.append(clf.predict(chunk))

all_predictions = np.concatenate(predictions)
```

## Memory Optimization

- **Subsample training data** for very large datasets to fit within GPU memory
- **Use `ignore_pretraining_limits=True`** only when necessary (performance not guaranteed)
- **Save fitted models** with `save_fitted_tabpfn_model()` to avoid re-computing context
- **Set `PYTORCH_CUDA_ALLOC_CONF`** to optimize CUDA memory fragmentation

## Feature Engineering

TabPFN benefits from domain-specific features but not standard preprocessing:

**Helpful:**
- Add domain-specific derived features (ratios, interactions, polynomial terms)
- Keep categorical columns as-is (strings, categoricals, or integers)
- Add engineered features that capture domain knowledge

**Not helpful (avoid):**
- Feature scaling or normalization (StandardScaler, MinMaxScaler)
- One-hot encoding of categorical columns
- Log transforms or other numerical transformations

The model handles encoding internally.

## Size Limits

TabPFN-3 recommended limits:

| Rows | Features |
| --- | --- |
| 1,000,000 | 200 |
| 100,000 | 2,000 |
| 1,000 | 20,000 |

Larger feature counts trade off against row capacity. For datasets exceeding limits:
1. Subsample the training data
2. Select the most important features
3. Set `ignore_pretraining_limits=True` (performance not guaranteed)

## Troubleshooting

### Pickle Error on Model Load

```
pip install tabpfn --upgrade
```

Re-download model files if the error persists.

### Out of Memory on GPU

- Reduce training set size (subsample)
- Reduce feature count
- Use a smaller checkpoint variant
- Set `PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"`

### Very Slow on CPU

- Use a GPU if available
- For small datasets (≲1,000 samples), CPU is acceptable
- For larger datasets, set `TABPFN_ALLOW_CPU_LARGE_DATASET=true` (will be very slow)
- Consider using the [TabPFN Client](https://github.com/PriorLabs/tabpfn-client) for cloud-based inference

### Authentication Issues in CI

```bash
export TABPFN_TOKEN="your_token_from_priorlabs_ai"
```

Obtain the token from [priorlabs.ai](https://ux.priorlabs.ai) → License tab.

### Apple Silicon Crashes

```bash
export TABPFN_MPS_MEMORY_FRACTION=0.5
```

Lower the fraction if crashes persist. Set before importing TabPFN.
