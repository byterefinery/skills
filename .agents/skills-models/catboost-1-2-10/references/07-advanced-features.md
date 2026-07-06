# Advanced Features

## GPU Training

### Single GPU

```python
model = CatBoostClassifier(task_type='GPU', iterations=100, depth=6)
model.fit(X_train, y_train)
```

### Multi-GPU

```python
# Specific devices
model = CatBoostClassifier(devices='0:2:3', iterations=100)

# Device range
model = CatBoostClassifier(devices='0-3', iterations=100)

# As list
model = CatBoostClassifier(devices=[0, 1, 2, 3], iterations=100)
```

### GPU-Specific Parameters

- `gpu_ram_part` — fraction of GPU memory to use (default 0.95)
- `pinned_memory_size` — CPU pinned memory for GPU transfers
- `border_count` defaults to 128 on GPU (254 on CPU)
- GPU-only CTR types: `'FloatTargetMeanValue'`, `'FeatureFreq'`
- GPU-only bootstrap: `'Poisson'`, `'MVS'`

### GPU Inference

```python
predictions = model.predict(X_test, task_type='GPU')
```

## Text Features

### Basic Usage

```python
model = CatBoostClassifier(
    text_features=[0],  # column 0 is text
    text_processing={
        'tokenizers': [{'Type': 'Word'}],
        'dictionaries': [{'TrainFrom': 'CurrentData'}],
        'feature_calcers': [
            {'Type': 'RawTF', 'Dictionary': 0},
            {'Type': 'NormalizedTF', 'Dictionary': 0}
        ]
    }
)
model.fit(X_train, y_train)
```

### Tokenizers

| Tokenizer | Description |
|---|---|
| `{'Type': 'Word'}` | Split on whitespace |
| `{'Type': 'Regex', 'Regex': '[a-z]+'}` | Custom regex tokenizer |
| `{'Type': 'Whitespace'}` | Whitespace tokenizer |

### Dictionaries

| Dictionary | Description |
|---|---|
| `{'TrainFrom': 'CurrentData'}` | Build from training data |
| `{'TrainFrom': 'File', 'Path': 'dict.txt'}` | Load from file |
| `{'TrainFrom': 'CurrentData', 'MaxSize': 10000}` | Limit dictionary size |

### Feature Calculators

| Calculator | Description |
|---|---|
| `{'Type': 'RawTF', 'Dictionary': 0}` | Raw term frequency |
| `{'Type': 'NormalizedTF', 'Dictionary': 0}` | Normalized TF |
| `{'Type': 'LogTF', 'Dictionary': 0}` | Log-transformed TF |
| `{'Type': 'SqrtTF', 'Dictionary': 0}` | Sqrt-transformed TF |
| `{'Type': 'BM25', 'Dictionary': 0}` | BM25 scoring |

## Embedding Features

```python
import numpy as np

# Pre-computed embeddings (e.g., from a neural network)
user_embeddings = np.random.randn(1000, 128)
item_embeddings = np.random.randn(1000, 64)

model = CatBoostClassifier(
    embedding_features=[0, 1],
    loss_function='Logloss'
)

pool = Pool(
    X_train, y_train,
    embedding_features=[0, 1],
    embedding_features_data=[user_embeddings, item_embeddings]
)

model.fit(pool)
```

## Monotone Constraints

Enforce feature-direction relationships:

```python
# -1: decreasing, 0: no constraint, 1: increasing
constraints = {
    'age': 1,           # age → target: increasing
    'income': 1,        # income → target: increasing
    'distance': -1,     # distance → target: decreasing
    'category': 0       # no constraint
}

model = CatBoostRegressor(monotone_constraints=constraints)
model.fit(X_train, y_train)
```

As a list (by feature index):

```python
model = CatBoostRegressor(monotone_constraints=[1, -1, 0, 1])
```

## SHAP Values

### Exact SHAP

```python
shap_values = model.get_feature_importance(
    data=test_pool,
    type='ShapValues',
    shap_calc_type='Exact'
)
# Shape: (n_samples, n_features + 1)
# Last column is the base value
```

### Approximate SHAP

```python
shap_values = model.get_feature_importance(
    data=test_pool,
    type='ShapValues',
    shap_calc_type='Approximate'
)
```

### SHAP with Pre-computation

```python
shap_values = model.get_feature_importance(
    data=test_pool,
    type='ShapValues',
    shap_mode='UsePreCalc'  # faster for large datasets
)
```

### SHAP Interaction Values

```python
# All pairs
interactions = model.get_feature_importance(
    data=test_pool,
    type='ShapInteractionValues'
)

# Specific pair
interactions = model.get_feature_importance(
    data=test_pool,
    type='ShapInteractionValues',
    interaction_indices=[0, 2]  # features 0 and 2
)
```

### SAGE Values

```python
sage_values = model.get_feature_importance(
    data=test_pool,
    type='SageValues',
    sage_n_samples=128,
    sage_batch_size=512,
    sage_detect_convergence=True
)
```

## Feature Importance Types

```python
# Prediction value change (default for non-ranking)
importance = model.get_feature_importance(type='PredictionValuesChange')

# Loss function change (default for ranking)
importance = model.get_feature_importance(type='LossFunctionChange')

# Interaction importance
interaction = model.get_feature_importance(type='Interaction')

# Prediction difference between two samples
diff = model.get_feature_importance(
    data=[sample1_features, sample2_features],
    type='PredictionDiff'
)
```

## Gaussian Process Sampling

Uncertainty estimation via kernel gradient boosting:

```python
from catboost import sample_gaussian_process, sum_models

models = sample_gaussian_process(
    X, y,
    cat_features=[0, 2],
    samples=10,
    posterior_iterations=900,
    prior_iterations=100,
    learning_rate=0.1,
    depth=6,
    sigma=0.1,       # GP kernel scale
    delta=0,         # noise scale
    random_strength=0.1,
    random_seed=42
)

# Ensemble prediction
mean_pred = np.mean([m.predict(X_test) for m in models], axis=0)
std_pred = np.std([m.predict(X_test) for m in models], axis=0)

# Or combine into single model
combined = sum_models(models)
```

## Bayesian Inference (Langevin)

```python
model = CatBoostRegressor(
    langevin=True,
    diffusion_temperature=1.0,
    posterior_sampling=True
)
model.fit(X_train, y_train)
```

## Feature Selection

```python
# Recursive feature elimination
model.select_features(
    X_train, y_train,
    cat_features=[0, 2],
    eval_set=(X_val, y_val),
    algorithm='RecursiveByPredictionValuesChange',
    num_features=10
)
```

Algorithms: `'RecursiveByPredictionValuesChange'`, `'RecursiveByLossFunctionChange'`, `'RecursiveByShapValues'`.

## Staged Prediction

```python
# Find optimal number of trees
best_score = float('inf')
best_n = 0
for i, preds in enumerate(model.staged_predict(X_val)):
    score = mean_squared_error(y_val, preds)
    if score < best_score:
        best_score = score
        best_n = i
```

## Callbacks

```python
from catboost.widget.callbacks import TrainingNotification

class MyCallback(TrainingNotification):
    def on_iteration_end(self, iteration, metrics):
        if metrics['TestLogloss'] < 0.1:
            self.stop_training()
        return super().on_iteration_end(iteration, metrics)

model.fit(X_train, y_train, callbacks=[MyCallback()])
```

## Snapshot Recovery

```python
model = CatBoostClassifier(
    save_snapshot=True,
    snapshot_file='snapshots/model.snap',
    snapshot_interval=60  # save every 60 seconds
)
model.fit(X_train, y_train)
# If interrupted, resume with init_model='snapshots/model.snap'
```
