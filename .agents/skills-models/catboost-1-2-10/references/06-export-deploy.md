# Model Export and Deployment

## save_model()

```python
model.save_model(fname, format='cbm', export_parameters=None, pool=None)
```

### Export Formats

| Format | Description | Use Case |
|---|---|---|
| `'cbm'` | CatBoost binary | Default. Compact, fast loading |
| `'json'` | JSON text | Inspection, debugging |
| `'onnx'` | ONNX-ML | Cross-framework deployment |
| `'coreml'` | Apple CoreML | iOS/macOS deployment |
| `'pmml'` | PMML | Enterprise ML platforms |
| `'cpp'` | C++ code | Standalone C++ inference |
| `'python'` | Python code | Standalone Python inference |

### CBM (Default)

```python
model.save_model('model.cbm')

# Load
model = CatBoostClassifier()
model.load_model('model.cbm')
```

### ONNX

```python
# Requires training pool for feature type inference
model.save_model('model.onnx', format='onnx', pool=train_pool)
```

ONNX export preserves categorical feature handling and works with ONNX Runtime.

### CoreML

```python
model.save_model(
    'model.mlmodel',
    format='coreml',
    export_parameters={
        'prediction_type': 'probability',  # or 'raw'
        'coreml_description': 'My CatBoost Model',
        'coreml_model_version': '1.0',
        'coreml_model_author': 'Author',
        'coreml_model_license': 'MIT'
    },
    pool=train_pool
)
```

### PMML

```python
model.save_model(
    'model.pmml',
    format='pmml',
    export_parameters={
        'pmml_copyright': 'Copyright 2024',
        'pmml_description': 'CatBoost PMML Model',
        'pmml_model_version': '1.0'
    },
    pool=train_pool
)
```

### C++ Export

```python
model.save_model('model.cpp', format='cpp', pool=train_pool)
```

Generates standalone C++ code with a prediction function. No CatBoost library needed at inference time.

### Python Export

```python
model.save_model('model.py', format='python', pool=train_pool)
```

Generates standalone Python code with a prediction function.

### JSON (for Inspection)

```python
model.save_model('model.json', format='json', pool=train_pool)

import json
with open('model.json') as f:
    model_data = json.load(f)
# Inspect oblivious_trees, leaf_values, etc.
```

## load_model()

```python
# From file
model.load_model('model.cbm')

# From stream
with open('model.cbm', 'rb') as f:
    model.load_model(stream=f)

# From blob (string)
model.load_model(blob=model_string)
```

## Continued Training

```python
# Save checkpoint
model.save_model('checkpoint.cbm')

# Continue training
new_model = CatBoostClassifier()
new_model.load_model('checkpoint.cbm')
new_model.fit(X_train, y_train, init_model=new_model)
```

Or directly:

```python
model.fit(X_train, y_train, init_model='checkpoint.cbm')
```

## Model Inspection

```python
model.tree_count_          # number of trees
model.get_feature_importance()
model.get_cat_feature_indices()
model.get_text_feature_indices()
model.get_embedding_feature_indices()
model.get_scale_and_bias()
model.is_fitted()
model.get_param('learning_rate')
```

## Model Combination

```python
from catboost import sum_models

# Combine models with equal weights
combined = sum_models([model1, model2, model3])

# With custom weights
combined = sum_models([model1, model2], weights=[0.7, 0.3])

# CTR merge policy
combined = sum_models(
    [model1, model2],
    ctr_merge_policy='IntersectingCountersAverage'
    # or 'AllCountersAverage', 'FirstCounters'
)
```

## Model Conversion

```python
from catboost import to_classifier, to_regressor, to_ranker

# Convert between types
classifier = to_classifier(regressor_model)
regressor = to_regressor(classifier_model)
ranker = to_ranker(regressor_model)
```

## Inference Optimization

```python
# Use GPU for inference
predictions = model.predict(X_test, task_type='GPU')

# Use specific threads
predictions = model.predict(X_test, thread_count=4)

# Use subset of trees
predictions = model.predict(X_test, ntree_start=0, ntree_end=100)
```

## Production Considerations

- **CBM format** is the most compact and fastest to load
- **ONNX** provides the best cross-platform compatibility
- **C++ export** eliminates runtime dependencies but generates large files
- **Model size** can be controlled with `model_size_reg`, `ctr_leaf_count_limit`, and `max_ctr_complexity`
- **Snapshot support** — enable `save_snapshot=True` to recover from crashes during training
