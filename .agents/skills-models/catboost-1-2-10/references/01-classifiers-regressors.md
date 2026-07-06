# CatBoostClassifier and CatBoostRegressor API

## CatBoostClassifier

Scikit-learn-compatible classifier for binary and multiclass classification.

### Constructor

```python
CatBoostClassifier(
    iterations=500,
    learning_rate=None,        # auto-selected for binary, 0.03 otherwise
    depth=6,
    l2_leaf_reg=3.0,
    loss_function='Logloss',   # or 'MultiClass', 'CrossEntropy', 'AMR', 'RMSE'
    border_count=254,          # 128 on GPU
    classes_count=None,        # number of classes for multiclass
    class_weights=None,        # list or dict of class weights
    auto_class_weights=None,   # 'Balanced' or 'SqrtBalanced'
    class_names=None,          # list of class name strings
    task_type=None,            # 'CPU' or 'GPU'
    devices=None,              # GPU devices: '0:1' or [0, 1]
    ...
)
```

### Key Classification-Specific Parameters

| Parameter | Default | Description |
|---|---|---|
| `loss_function` | `'Logloss'` | `'Logloss'` (binary), `'MultiClass'` (multiclass), `'CrossEntropy'`, `'AMR'` |
| `classes_count` | `None` | Upper limit for numeric class labels. Auto-detected from data if None |
| `class_weights` | `None` | List of weights (ordered by class) or dict `{class_name: weight}` |
| `auto_class_weights` | `None` | `'Balanced'` or `'SqrtBalanced'` — auto-compute from training distribution |
| `class_names` | `None` | List of class name strings, overrides default integer labels |
| `target_border` | `None` | Threshold for binary classification target binarization |

### Methods

#### `fit()`

```python
model.fit(
    X, y=None,
    cat_features=None,
    text_features=None,
    embedding_features=None,
    sample_weight=None,
    baseline=None,
    use_best_model=None,
    eval_set=None,
    verbose=None,
    logging_level=None,
    plot=False,
    early_stopping_rounds=None,
    save_snapshot=None,
    snapshot_file=None,
    snapshot_interval=None,
    init_model=None,
    callbacks=None
)
```

- `X`: Pool, numpy array, pandas DataFrame, polars DataFrame, or file path
- `y`: labels (numeric for binary/multiclass, or class names)
- `eval_set`: Pool, `(X, y)` tuple, or list thereof
- `init_model`: existing CatBoost model or file path for continued training
- Returns `self`

#### `predict()`

```python
predictions = model.predict(X)
```

Returns class labels (not probabilities). Default `prediction_type='Class'`.

#### `predict_proba()`

```python
probabilities = model.predict_proba(X)
```

Returns class probabilities. Shape `(n_samples, n_classes)`. For binary classification, returns both classes.

#### `predict_log_proba()`

```python
log_probs = model.predict_log_proba(X)
```

Returns log probabilities.

#### `staged_predict()` / `staged_predict_proba()`

```python
for iteration_predictions in model.staged_predict(X):
    # iteration_predictions is predictions using trees [0..iteration]
    pass
```

Generator yielding predictions after each tree. Useful for finding optimal tree count.

#### `get_feature_importance()`

```python
importances = model.get_feature_importance()
importances = model.get_feature_importance(data=test_pool, type='ShapValues')
```

Types: `'PredictionValuesChange'`, `'LossFunctionChange'`, `'ShapValues'`, `'ShapInteractionValues'`, `'SageValues'`, `'Interaction'`, `'PredictionDiff'`.

#### `eval_metrics()`

```python
results = model.eval_metrics(test_pool, ['Accuracy', 'Logloss', 'AUC'])
```

Returns dict mapping metric name to array of values (one per eval interval).

#### `save_model()` / `load_model()`

```python
model.save_model('model.cbm')
model.save_model('model.onnx', format='onnx')

model.load_model('model.cbm')
model.load_model('model.cbm', format='cbm')
```

Supported formats: `'cbm'`, `'json'`, `'onnx'`, `'coreml'`, `'pmml'`, `'cpp'`, `'python'`.

## CatBoostRegressor

Scikit-learn-compatible regressor.

### Constructor

```python
CatBoostRegressor(
    iterations=500,
    learning_rate=0.03,
    depth=6,
    l2_leaf_reg=3.0,
    loss_function='RMSE',
    border_count=254,
    task_type=None,
    devices=None,
    ...
)
```

### Key Regression-Specific Parameters

| Parameter | Default | Description |
|---|---|---|
| `loss_function` | `'RMSE'` | `'RMSE'`, `'MAE'`, `'MSE'`, `'Quantile:alpha=0.5'`, `'LogLinQuantile'`, `'Poisson'`, `'MAPE'`, `'Lq:q=2'`, `'SurvivalAft'` |

### Methods

Same as `CatBoostClassifier` except `predict_proba()`, `predict_log_proba()`, `staged_predict_proba()`, `staged_predict_log_proba()`.

#### `predict()`

Returns raw formula values (continuous predictions). Default `prediction_type='RawFormulaVal'`.

### Multi-Regression

For multi-output regression, use a 2D label array and set `loss_function='MultiRMSE'` (or `'MultiMAE'`, `'MultiMSE'`).

```python
model = CatBoostRegressor(loss_function='MultiRMSE')
model.fit(X, Y_multi)  # Y_multi is (n_samples, n_outputs)
```

## Sklearn Compatibility

Both classes implement the full sklearn estimator interface:

- `get_params()` / `set_params()`
- `score()` — returns accuracy for classifier, R² for regressor
- `feature_importances_` property
- Compatible with `GridSearchCV`, `RandomizedSearchCV`, `Pipeline`

### Aliases for Other Libraries

Parameters accept aliases from XGBoost, LightGBM, and others:

| CatBoost | XGBoost alias | LightGBM alias |
|---|---|---|
| `iterations` | `n_estimators` | `num_boost_round`, `num_iterations` |
| `depth` | `max_depth` | `max_depth` |
| `learning_rate` | `eta` | `learning_rate` |
| `l2_leaf_reg` | `reg_lambda` | `lambda_l2` |
| `border_count` | `max_bin` | `max_bin` |
| `rsm` | `colsample_bylevel` | `colsample_bytree` |
| `random_seed` | `random_state` | `random_state` |
| `cat_features` | — | `categorical_feature` |
