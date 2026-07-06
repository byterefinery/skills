# Advanced Features — LightGBM 4.6.0

## GPU / CUDA Acceleration

GPU support requires building LightGBM from source. Pre-built pip wheels are CPU-only.

### Building with GPU Support

```bash
# CUDA (recommended for NVIDIA GPUs)
mkdir build && cd build
cmake .. -DUSE_CUDA=ON
make -j$(nproc)
cd ../python-package && pip install .

# OpenCL (broader GPU support)
mkdir build && cd build
cmake .. -DUSE_OPENCL=ON
make -j$(nproc)
cd ../python-package && pip install .
```

### Using GPU

```python
params = {
    "device_type": "cuda",       # or "gpu" for OpenCL
    "max_bin": 63,               # smaller max_bin improves GPU speedup
    "num_gpu": 1,                # CUDA: number of GPUs
}

# OpenCL-specific
params = {
    "device_type": "gpu",
    "gpu_platform_id": 0,        # OpenCL platform
    "gpu_device_id": 0,          # GPU device
    "gpu_use_dp": False,         # double precision (slower but more accurate)
}
```

GPU considerations:
- `cuda` is faster than `gpu` (OpenCL) but requires NVIDIA GPU
- Use smaller `max_bin` (e.g., 63) for better GPU speedup
- GPU uses single precision by default (OpenCL); set `gpu_use_dp=true` for double precision
- CUDA always uses double precision

## Distributed Learning

LightGBM supports three parallel strategies via `tree_learner`:

### Feature Parallel (`tree_learner="feature"`)

- Each worker holds a different feature subset
- Every worker holds full data
- Best for many features, moderate data size
- No data split communication needed

### Data Parallel (`tree_learner="data"`)

- Each worker holds a different data partition
- Uses Reduce Scatter for histogram merging
- Best for large data, moderate features

### Voting Parallel (`tree_learner="voting"`)

- Combines data and feature parallel
- Uses two-stage voting to reduce communication to constant cost
- Controlled by `top_k` (default 20): larger = more accurate, slower

### Setup

```bash
# Machine list file (one "ip port" per line)
# machines.list:
# 192.168.1.1 12400
# 192.168.1.2 12400

# Run on each machine
lightgbm config=train.conf \
    machine_list=machines.list \
    num_machines=2 \
    local_listen_port=12400 \
    input_model=model.txt \
    output_model=output.txt
```

Python distributed training uses Dask:

```python
from lightgbm.dask import DaskLGBMClassifier, DaskLGBMRegressor

model = DaskLGBMClassifier(n_estimators=100)
model.fit(dask_X_train, dask_y_train)
predictions = model.predict(dask_X_test)
```

## Quantized Training (New in 4.0.0)

Quantizes gradients and hessians into discrete bins, replacing float arithmetic with integer operations. Speeds training with minimal accuracy loss.

```python
params = {
    "use_quantized_grad": True,
    "num_grad_quant_bins": 4,        # more bins = closer to full precision
    "quant_train_renew_leaf": False, # renew leaf values with original gradients
    "stochastic_rounding": True,     # unbiased rounding
}
```

- Works with `cpu` and `cuda` device types only
- `quant_train_renew_leaf=True` is helpful for ranking objectives
- Default 4 bins gives good speed/accuracy tradeoff

## Linear Trees

Piecewise linear gradient boosting trees. Each leaf fits a linear model (instead of constant value) using all numerical features in that leaf's branch.

```python
params = {
    "linear_tree": True,
}
```

Constraints and notes:
- CPU and GPU only (no CUDA)
- Serial tree learner only
- `regression_l1` objective not supported
- Significantly increases memory usage
- Rescale features to similar mean/std before training
- Missing values must be `np.nan`, not 0
- `monotone_constraints` enforced at split points but not in leaf linear models
- First tree uses constant leaf values; subsequent trees use linear models
- Categorical features used for splits but not in linear models

## Monotone Constraints

Enforce directional relationships between features and predictions.

```python
# Feature 0: decreasing, Feature 1: unconstrained, Feature 2: increasing
params = {
    "monotone_constraints": [-1, 0, 1],
    "monotone_constraints_method": "advanced",  # basic | intermediate | advanced
    "monotone_penalty": 0.0,                     # penalize monotone splits on shallow levels
}
```

Methods:
- `basic` — fastest, but over-constrains predictions
- `intermediate` — slight slowdown, much less constraining
- `advanced` — slowest, least constraining, best results

Cannot be applied to categorical features.

## Interaction Constraints

Restrict which features can appear together in any branch of a tree. Prevents unwanted feature interactions.

```python
# Group 1: features 0,1,2 can interact with each other
# Group 2: features 2,3 can interact with each other
# But features 0 and 3 can never appear in the same branch
params = {
    "interaction_constraints": [[0, 1, 2], [2, 3]]
}
```

## Forced Splits

Force specific splits at the top of every tree before best-first learning begins.

```python
# forced_splits.json
# [
#   {"feature": 0, "threshold": 5.0,
#    "left": {"feature": 2, "threshold": 3.0},
#    "right": null}
# ]

params = {"forcedsplits_filename": "forced_splits.json"}
```

- JSON file can be arbitrarily nested
- Categorical splits forced in one-hot fashion
- Forced splits are ignored if they make gain worse

## Forced Bins

Pre-specify bin upper bounds for features.

```python
# forced_bins.json
# [
#   {"feature": 0, "bin_upper_bound": [1.0, 5.0, 10.0, 100.0]},
#   {"feature": 1, "bin_upper_bound": [0.5, 2.0, 8.0]}
# ]

train_data = lgb.Dataset(X_train, label=y_train, params={"forcedbins_filename": "forced_bins.json"})
```

## Continued Training

### From Saved Model

```python
# Continue from file
model = lgb.train(params, train_data, init_model="model.txt")

# Continue from Booster object
model = lgb.train(params, train_data, init_model=previous_booster)
```

### With Initial Scores

```python
# Provide init_score file alongside data
# train.txt.init:
# 0.5
# -0.1
# 0.9
# ...

# Or via Dataset
train_data = lgb.Dataset(X_train, label=y_train, init_score=init_scores)
```

### Refit

Update leaf values on new data without retraining tree structure.

```python
# Via Booster method
model.refit(new_X, new_y, decay_rate=0.9)

# decay_rate: 0.9 = 90% old + 10% new
# leaf_output = decay_rate * old + (1 - decay_rate) * new
```

## Custom Objective Functions

```python
# Binary classification: log loss
def binary_logloss_objective(preds, train_data):
    labels = train_data.get_label()
    preds = 1.0 / (1.0 + np.exp(-preds))  # sigmoid
    grad = preds - labels
    hess = preds * (1.0 - preds)
    return grad, hess

# Multiclass: softmax cross-entropy
def multiclass_objective(preds, train_data):
    labels = train_data.get_label()
    num_class = 3
    preds = preds.reshape(num_class, -1).T
    # softmax
    preds = np.exp(preds - np.max(preds, axis=1, keepdims=True))
    preds /= np.sum(preds, axis=1, keepdims=True)
    one_hot = np.zeros_like(preds)
    one_hot[np.arange(len(labels)), labels.astype(int)] = 1
    grad = preds - one_hot
    hess = preds * (1.0 - preds)
    return grad.ravel(), hess.ravel()
```

## Custom Evaluation Metrics

```python
def rmsle(preds, train_data):
    labels = train_data.get_label()
    preds = np.expm1(preds)  # inverse log transform
    labels = np.expm1(labels)
    preds = np.clip(preds, a_min=0, a_max=None)
    return "RMSLE", np.sqrt(np.mean(np.log1p(preds) - np.log1p(labels)) ** 2), False
```

## Model Export and Deployment

### Text Format

```python
model.save_model("model.txt", num_iteration=None, importance_type="split")
```

### JSON Format

```python
model_dict = model.dump_model()
# Contains: max_feature_idx, num_leaves, num_cat, tree_info,
#           feature_names, objective, average_output, etc.
```

### Convert to C++ (CLI)

```bash
lightgbm config=convert.conf task=convert_model \
    input_model=model.txt \
    convert_model_language=cpp \
    convert_model=model.cpp
```

### External Tools

- **Treelite** — compile model for fast inference
- **ONNXMLTools** — convert to ONNX format
- **SHAP** — detailed model explanation
- **m2cgen** — convert to multiple languages
- **Hummingbird** — convert to tensor computations
- **Treelite** — model compiler for deployment

## Hyperparameter Tuning Tips

### Tuning Order

1. `num_leaves` and `max_depth` — set complexity bounds first
2. `learning_rate` and `num_iterations` — lower rate + more iterations = better accuracy
3. `min_data_in_leaf` — primary overfitting control (start at 20–50)
4. `feature_fraction` and `bagging_fraction` — regularization (0.6–0.9)
5. `lambda_l1` and `lambda_l2` — leaf weight regularization
6. `min_gain_to_split` — additional split regularization

### Common Patterns

```python
# Fast prototype
params = {
    "objective": "binary",
    "learning_rate": 0.1,
    "num_leaves": 31,
    "verbose": -1,
}

# Production-quality
params = {
    "objective": "binary",
    "learning_rate": 0.01,
    "num_leaves": 63,
    "max_depth": 6,
    "min_data_in_leaf": 50,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 5,
    "lambda_l1": 0.1,
    "lambda_l2": 0.1,
    "min_gain_to_split": 0.01,
    "verbose": -1,
}

# Imbalanced binary
params = {
    "objective": "binary",
    "is_unbalance": True,
    # or: "scale_pos_weight": neg_count / pos_count,
    "pos_bagging_fraction": 0.5,
    "neg_bagging_fraction": 1.0,
    "bagging_freq": 5,
}
```

## Performance Tuning

```python
# For large datasets
params = {
    "force_col_wise": True,           # many columns / many threads
    "num_threads": 16,                # real CPU cores
    "bin_construct_sample_cnt": 500000,  # more samples for bin construction
    "histogram_pool_size": 128,       # MB cache for histograms
}

# For small datasets
params = {
    "force_row_wise": True,           # many rows, few threads
    "extra_trees": True,              # randomized splits for speed
    "max_bin": 63,                    # fewer bins
}

# Deterministic results
params = {
    "deterministic": True,
    "force_col_wise": True,
    "seed": 42,
}
```
