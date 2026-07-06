# Data Inputs

## Supported Input Types

XGBoost accepts a wide range of data structures through both the sklearn and native APIs.

### NumPy Arrays

```python
import numpy as np
import xgboost as xgb

X = np.random.randn(1000, 20).astype(np.float32)
y = np.random.randint(0, 2, 1000)

# Sklearn
clf = xgb.XGBClassifier()
clf.fit(X, y)

# Native
dtrain = xgb.DMatrix(X, label=y)
```

Recommended dtype: `float32`. XGBoost converts internally but passing `float32` avoids a copy.

### Pandas DataFrames

```python
import pandas as pd

df = pd.read_csv("data.csv")

# Automatic type handling
clf = xgb.XGBClassifier(enable_categorical=True)
clf.fit(df.drop("target", axis=1), df["target"])

# Categorical columns (must be category dtype)
df["region"] = df["region"].astype("category")
df["size"] = pd.Categorical(df["size"], categories=["S", "M", "L", "XL"])

# String columns are auto-converted to categorical when enable_categorical=True
df["color"] = df["color"].astype(str)
```

**Supported dtypes:**
- `float32`, `float64` — quantitative features
- `int8`–`int64`, `uint8`–`uint64` — quantitative (auto-converted)
- `category` — categorical features (with `enable_categorical=True`)
- `string` — auto-converted to categorical
- `boolean` — treated as quantitative (0/1)
- Nullable integer types (`Int8`, `Int16`, etc.) — supported

### PyArrow Tables

```python
import pyarrow as pa

table = pa.table({
    "feature1": pa.array([1.0, 2.0, 3.0]),
    "feature2": pa.array(["a", "b", "c"]),
    "target": pa.array([0, 1, 0]),
})

clf = xgb.XGBClassifier(enable_categorical=True)
clf.fit(table.drop(["target"]), table["target"].to_pandas())
```

### cuDF (GPU DataFrames)

```python
import cudf

gdf = cudf.read_csv("data.csv")
gdf["category"] = gdf["category"].astype("category")

clf = xgb.XGBClassifier(device="cuda", enable_categorical=True)
clf.fit(gdf.drop("target", axis=1), gdf["target"])
```

Zero-copy when data stays on GPU.

### CuPy Arrays (GPU NumPy)

```python
import cupy as cp

X_gpu = cp.random.randn(10000, 20, dtype=cp.float32)
y_gpu = cp.random.randint(0, 2, 10000)

clf = xgb.XGBClassifier(device="cuda")
clf.fit(X_gpu, y_gpu)
```

### Sparse Matrices

```python
from scipy.sparse import csr_matrix, csc_matrix

sparse_X = csr_matrix(X_dense)

# Sklearn
clf.fit(sparse_X, y)

# Native
dtrain = xgb.DMatrix(sparse_X, label=y)
```

Both CSR and CSC formats are supported. CSC uses the array interface directly.

### Polars DataFrames

```python
import polars as pl

df = pl.read_csv("data.csv")

# Convert to pandas or use array interface
clf.fit(df.drop("target").to_pandas(), df["target"].to_pandas())
```

LazyFrames are supported but materialized internally.

### File Inputs

```python
# LIBSVM format (native API only)
dtrain = xgb.DMatrix("train.svm.txt")
dtrain = xgb.DMatrix("train.libsvm")

# NDJSON (line-delimited JSON)
dtrain = xgb.DMatrix("train.json", format="json")

# CSV
dtrain = xgb.DMatrix("train.csv", format="csv")
```

### DMatrix Construction Options

```python
dtrain = xgb.DMatrix(
    data,
    label=y,
    weight=None,              # Sample weights
    base_margin=None,         # Base margin per instance
    missing=np.nan,           # Value treated as missing
    feature_names=None,       # List of feature names
    feature_types=None,       # List of types: "q" (quantitative), "c" (categorical)
    nthread=-1,               # Threads for construction
    enable_categorical=False, # Enable native categorical handling
    group=None,               # Group sizes for ranking
    qid=None,                 # Query IDs for ranking
)
```

## QuantileDMatrix

Memory-efficient data structure using quantization. Best for large datasets with `hist` tree method.

```python
# Training set
qdm_train = xgb.QuantileDMatrix(
    X_train,
    label=y_train,
    max_bin=256,
    missing=np.nan,
    nthread=-1,
)

# Validation set (must reference training QuantileDMatrix)
qdm_val = xgb.QuantileDMatrix(
    X_val,
    label=y_val,
    ref=qdm_train,   # Align quantile bins
    max_bin=256,
)

# Use with train()
model = xgb.train(params, qdm_train, num_boost_round=200,
                  evals=[(qdm_val, "val")])
```

**Benefits:**
- Lower memory footprint (quantized features)
- Cached transformed data for repeated use
- Automatically used by sklearn interface with `hist` tree method

**Limitations:**
- Requires `hist` or `approx` tree method
- `ref` required for validation/test sets
- One-time preprocessing cost
- Not supported with `gblinear`

## ExtMemQuantileDMatrix

For datasets larger than available RAM.

```python
# From file
ext_dm = xgb.ExtMemQuantileDMatrix(
    "train_file",
    label=y_train,
    max_bin=256,
    silent=True,
)
```

## DataIter

Custom streaming iterator for out-of-core or generated data.

```python
import xgboost as xgb
import numpy as np

class ChunkedDataIter(xgb.DataIter):
    def __init__(self, file_path, label_path, batch_size=4096):
        super().__init__()
        self.X_data = np.memmap(file_path, dtype=np.float32, mode="r", shape=(1000000, 20))
        self.y_data = np.memmap(label_path, dtype=np.float32, mode="r", shape=(1000000,))
        self.batch_size = batch_size
        self.offset = 0

    def data(self):
        batch = self.X_data[self.offset:self.offset + self.batch_size]
        self.offset += self.batch_size
        return batch

    def label(self):
        return self.y_data[self.offset - self.batch_size:self.offset]

    def has_next(self):
        return self.offset < len(self.y_data)

    def reset(self):
        self.offset = 0

iterator = ChunkedDataIter("X.dat", "y.dat")
model = xgb.train(params, iterator, num_boost_round=100)
```

## Data Preprocessing Notes

### Missing Values

XGBoost handles missing values natively. During training, it learns the default direction for missing values at each split.

```python
# NaN is treated as missing (default)
dtrain = xgb.DMatrix(X, label=y, missing=np.nan)

# Custom missing value indicator
dtrain = xgb.DMatrix(X, label=y, missing=-999)
```

### Infinite Values

`inf` and `-inf` are not accepted. Replace before training:

```python
X = np.nan_to_num(X, nan=0.0, posinf=np.max(X, axis=0), neginf=np.min(X, axis=0))
```

### Feature Scaling

XGBoost (tree-based) is invariant to monotonic feature scaling. StandardScaler is not needed. However, it can help with:
- Gradient-based sampling stability
- Interpretability of feature contributions
- Consistency with pipelines that include other estimators

### Categorical Encoding

With `enable_categorical=True`, XGBoost handles categoricals natively using a specialized split finding algorithm (efficient partitioning, not one-hot). Do not one-hot encode when using native categorical support.

```python
# Native categorical (recommended)
df["cat"] = df["cat"].astype("category")
clf = xgb.XGBClassifier(enable_categorical=True)
clf.fit(df, y)

# Without native categorical
# One-hot encode externally, then use enable_categorical=False
```

For low-cardinality categoricals (< `max_cat_to_onehot`, default 10), XGBoost uses one-hot encoding. For high-cardinality, it uses partition-based splits.
