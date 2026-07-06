# Native API Reference

## DMatrix

The core data structure. Wraps features, labels, and metadata for training.

```python
import xgboost as xgb
import numpy as np

# Basic creation
dtrain = xgb.DMatrix(X_train, label=y_train)

# With weights and missing value
dtrain = xgb.DMatrix(
    X_train,
    label=y_train,
    weight=sample_weights,
    missing=np.nan,
    nthread=4,
)

# Feature names and types
dtrain = xgb.DMatrix(
    X_train,
    label=y_train,
    feature_names=["age", "income", "zip"],
    feature_types=["q", "q", "c"],  # q=quantitative, c=categorical
)

# Categorical data (Pandas with category dtype)
import pandas as pd
df = pd.DataFrame({"cat": pd.Categorical(["a", "b", "c"])})
dtrain = xgb.DMatrix(df, label=y, enable_categorical=True)

# Sparse matrices
from scipy.sparse import csr_matrix
sparse_X = csr_matrix(X_train)
dtrain = xgb.DMatrix(sparse_X, label=y_train)

# From file
dtrain = xgb.DMatrix("train.svm.txt")
dtrain = xgb.DMatrix("train.libsvm")

# Save/Load
dtrain.save_binary("train.buffer", silent=False)
dtrain = xgb.DMatrix("train.buffer")
```

### DMatrix Methods

```python
# Get label, weight, base margin
labels = dtrain.get_label()
weights = dtrain.get_weight()
base_margin = dtrain.get_base_margin()

# Set metadata
dtrain.set_group([10, 20, 15])     # For ranking
dtrain.set_weight(weights)
dtrain.set_base_margin(margins)

# Info
num_row = dtrain.num_row()
num_col = dtrain.num_col()
```

## QuantileDMatrix

Memory-efficient variant using quantization. Automatically used by sklearn interface with `hist` tree method.

```python
qdm = xgb.QuantileDMatrix(
    X_train,
    label=y_train,
    max_bin=256,          # Max bins per feature
    missing=np.nan,
    nthread=4,
)

# For validation, reference the training QuantileDMatrix
qval = xgb.QuantileDMatrix(
    X_val,
    label=y_val,
    ref=qdm,              # Align bins with training data
    max_bin=256,
)
```

**When to use:**
- Large datasets where memory is a concern
- `hist` or `approx` tree method
- Not supported with `exact` tree method or `gblinear`

**Caveats:**
- One-time preprocessing cost (quantile computation)
- `ref` parameter is required for validation/test sets
- Device mismatch (CPU data + GPU training) incurs transfer overhead

## ExtMemQuantileDMatrix

Out-of-core learning for datasets larger than RAM.

```python
ext_dm = xgb.ExtMemQuantileDMatrix(
    "train_file",          # File path or iterable of chunks
    label=y_train,
    max_bin=256,
    silent=True,
)
```

## DataIter

Custom data iterator for streaming/large datasets.

```python
import numpy as np
import xgboost as xgb

class MyDataIter(xgb.DataIter):
    def __init__(self, data, label, batch_size=1024):
        super().__init__()
        self.data = data
        self.label = label
        self.batch_size = batch_size
        self.idx = 0

    def data(self):
        # Return current batch of features
        batch = self.data[self.idx:self.idx + self.batch_size]
        self.idx += self.batch_size
        return batch

    def label(self):
        # Return current batch of labels
        batch = self.label[self.idx - self.batch_size:self.idx]
        return batch

    def has_next(self):
        return self.idx < len(self.data)

    def reset(self):
        self.idx = 0

# Use with train()
iterator = MyDataIter(X_train, y_train, batch_size=1024)
model = xgb.train(params, iterator, num_boost_round=100)
```

## train()

Train a Booster model.

```python
import xgboost as xgb

params = {
    "objective": "reg:squarederror",
    "max_depth": 6,
    "learning_rate": 0.1,
    "eval_metric": "rmse",
    "tree_method": "hist",
    "verbosity": 1,
}

dtrain = xgb.DMatrix(X_train, label=y_train)
dval = xgb.DMatrix(X_val, label=y_val)

# Basic training
model = xgb.train(params, dtrain, num_boost_round=200)

# With evaluation and early stopping
evals_result = {}
model = xgb.train(
    params,
    dtrain,
    num_boost_round=200,
    evals=[(dtrain, "train"), (dval, "val")],
    early_stopping_rounds=10,
    evals_result=evals_result,
    verbose_eval=10,
)

# With callbacks
from xgboost.callback import EarlyStopping, LearningRateScheduler, TrainingCheckPoint

callbacks = [
    EarlyStopping(stopping_rounds=10, save_best=True, minimize=True),
    TrainingCheckPoint("checkpoint_", 10),  # Save every 10 rounds
]

model = xgb.train(
    params,
    dtrain,
    num_boost_round=200,
    evals=[(dval, "val")],
    callbacks=callbacks,
)

# Continue training from existing model
model = xgb.train(
    params,
    dtrain,
    num_boost_round=100,
    xgb_model="model.json",  # or Booster object
)

# Custom objective
def custom_objective(y_true, y_pred):
    grad = y_pred - y_true
    hess = np.ones_like(y_true)
    return grad, hess

model = xgb.train(params, dtrain, num_boost_round=200, obj=custom_objective)

# Custom metric
def custom_metric(y_true, y_pred):
    return "mae", float(np.mean(np.abs(y_true - y_pred)))

model = xgb.train(
    params, dtrain, num_boost_round=200,
    custom_metric=custom_metric,
)
```

### evals_result

```python
# After training
print(evals_result)
# {
#   "train": {"rmse": [0.5, 0.45, ...]},
#   "val": {"rmse": [0.6, 0.55, ...]},
# }
```

## cv()

Cross-validation.

```python
cv_results = xgb.cv(
    params,
    dtrain,
    num_boost_round=200,
    nfold=5,
    stratified=True,        # Stratified splits for classification
    shuffle=True,           # Shuffle before splitting
    as_pandas=True,         # Return DataFrame
    metrics=["rmse", "mae"],
    seed=42,
    early_stopping_rounds=10,
    verbose_eval=50,
)

# cv_results columns: train-rmse-mean, train-rmse-std, test-rmse-mean, test-rmse-std
best_round = cv_results["test-rmse-mean"].idxmin()
best_score = cv_results["test-rmse-mean"].min()
```

## Booster

The trained model object.

```python
# After training
model = xgb.train(params, dtrain, num_boost_round=200)

# Prediction
preds = model.predict(dtest)
preds = model.predict(dtest, output_margin=True)     # Raw margins
preds = model.predict(dtest, iteration_range=(0, 50)) # First 50 trees
contribs = model.predict(dtest, pred_contribs=True)   # Feature contributions

# Model inspection
num_trees = model.best_ntree_limit if hasattr(model, 'best_ntree_limit') else 200
dump = model.get_dump(with_stats=True, dump_format="text")
dump_json = model.get_dump(with_stats=True, dump_format="json")

# Feature importance
score = model.get_fscore()                    # Weight (frequency)
score = model.get_score(importance_type="gain")
score = model.get_score(importance_type="cover")
score = model.get_score(importance_type="total_gain")
score = model.get_score(importance_type="total_cover")

# Parameters
config = model.save_config()                  # JSON string
model.load_config(config)                     # Load from JSON string

# Save/Load
model.save_model("model.json")
model.save_model("model.raw")                 # Binary format

loaded = xgb.Booster()
loaded.load_model("model.json")

# Model slicing
sliced = model[0:50]                          # First 50 trees
preds = sliced.predict(dtest)

# Attributes
model.set_attr(my_attr="value")
attrs = model.attr()                          # Get all attributes
model.save_model("model.json")                # Attrs saved with model
```

## Plotting

```python
import xgboost as xgb

# Feature importance plot
xgb.plot_importance(model, importance_type="gain", max_num_features=20)

# Tree plot
xgb.plot_tree(model, num_trees=0, rankdir="LR")

# Graphviz (requires graphviz)
graph = xgb.to_graphviz(model, num_trees=0)
```
