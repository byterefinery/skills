# API Reference — LightGBM 4.6.0

## Native API

### `lightgbm.Dataset`

Core data container. Pre-processes data into histogram bins for efficient training.

```python
lgb.Dataset(
    data,                      # np.ndarray, pd.DataFrame, scipy.sparse, pa.Table, str/Path, Sequence
    label=None,                # labels (np.ndarray, pd.Series, list)
    weight=None,               # sample weights (non-negative)
    group=None,                # group sizes for ranking (list of ints, sum = n_samples)
    init_score=None,           # initial scores for continued training
    feature_name=None,         # list of feature names or 'auto'
    categorical_feature=None,  # list of feature names/indices or 'auto'
    params=None,               # additional params dict
    free_raw_data=True,        # free raw data after construction (saves memory)
    reference=None,            # reference Dataset for shared binning (use for valid sets)
)
```

Key methods:
- `save_binary(file_name)` — save to binary format for faster reloading
- `construct()` — explicitly construct (called automatically by train)
- `get_label()` / `get_weight()` / `get_group()` — retrieve metadata
- `set_field(name, data)` — set label, weight, group, init_score
- `get_field(name)` — get label, weight, group, init_score
- `set_reference(ref_dataset)` — set reference for bin alignment
- `set_categorical_feature(cat_feature)` — mark categorical features
- `sub_sample(seed, n_iterations, is_train)` — subsample data
- `slice(start_idx, end_idx)` — create a slice view

```python
# Create validation set sharing binning with training set
train_data = lgb.Dataset(X_train, label=y_train)
valid_data = lgb.Dataset(X_valid, label=y_valid, reference=train_data)

# For ranking: group sizes, data must be sorted by query
train_data = lgb.Dataset(X_train, label=y_train, group=[10, 20, 15])
```

### `lightgbm.Booster`

Trained model object.

```python
lgb.Booster(
    params=None,           # params dict
    train_set=None,        # training Dataset
    model_file=None,       # load from file (str/Path)
    model_str=None,        # load from string
)
```

Key methods:
- `update(fobj=None)` — train one iteration
- `predict(data, start_iteration=0, num_iteration=None, raw_score=False, pred_leaf=False, pred_contrib=False)` — predict
- `eval(data_set, feval=None)` — evaluate on dataset
- `eval_train(feval=None)` / `eval_valid(feval=None)` — evaluate on train/valid
- `save_model(file_name, num_iteration=None, importance_type='split')` — save model
- `model_to_string(num_iteration=None, importance_type='split')` — serialize to string
- `model_from_string(model_str)` — load from string
- `feature_importance(importance_type='split', iteration=-1)` — get importance
  - `importance_type='split'`: number of splits
  - `importance_type='gain'`: total gain of splits
- `dump_model(num_iteration=None, importances_type='split')` — JSON model dump
- `free_dataset()` — free referenced datasets
- `refit(data, data_label, decay_rate=0.9)` — refit leaf values on new data

Properties:
- `best_iteration` — best iteration from early stopping
- `best_score` — best scores dict: `{dataset_name: {metric_name: score}}`
- `current_iteration` — current iteration count
- `num_total_iteration` — total iterations trained
- `upper_bound_value` / `lower_bound_value` — prediction bounds

### `lightgbm.train()`

```python
lgb.train(
    params,                          # params dict
    train_set,                       # Dataset
    num_boost_round=100,             # max boosting iterations
    valid_sets=None,                 # list of validation Datasets
    valid_names=None,                # names for valid_sets
    feval=None,                      # custom evaluation function(s)
    init_model=None,                 # continue from existing model (str/Path/Booster)
    keep_training_booster=False,     # if False, converts to _InnerPredictor (frees datasets)
    callbacks=None,                  # list of callback functions
) -> Booster
```

### `lightgbm.cv()`

Cross-validation.

```python
lgb.cv(
    params,
    train_set,
    num_boost_round=100,
    folds=None,                      # sklearn KFold or list of (train_idx, val_idx) tuples
    nfold=-1,                        # number of folds (-1 = use max possible)
    stratified=True,                 # stratified splitting (classification)
    shuffle=True,                    # shuffle before splitting
    callbacks=None,
    eval_train_metric=False,         # also evaluate on training data
    feval=None,
    init_model=None,
    return_cvbooster=False,          # return CVBooster object
) -> dict
```

Returns dict with metric names as keys, lists of per-fold scores as values.

### `lightgbm.CVBooster`

Container for multiple boosters from CV. Has same predict/eval interface as Booster, operations applied to all underlying boosters.

```python
cvbooster = lgb.cv(params, train_set, return_cvbooster=True)
mean_pred = np.mean([b.predict(X) for b in cvbooster.boosters], axis=0)
```

## Callbacks

### `lightgbm.early_stopping(stopping_rounds, verbose=True, first_metric_only=False, min_delta=0.0)`

Stop training if a metric doesn't improve in `stopping_rounds` rounds. Sets `best_iteration` on returned Booster.

### `lightgbm.log_evaluation(period=1, show_stdv=True)`

Log evaluation results every `period` iterations.

### `lightgbm.record_evaluation(eval_result)`

Record evaluation history into pre-allocated dict.

```python
eval_result = {}
callbacks = [lgb.record_evaluation(eval_result)]
model = lgb.train(params, train_data, valid_sets=[valid_data], callbacks=callbacks)
# eval_result: {'valid_0': {'binary_logloss': [...], 'auc': [...]}}
```

### `lightgbm.reset_parameter(callback)`

Dynamically change parameters during training.

```python
# Learning rate warmup then decay
callbacks = [
    lgb.reset_parameter(
        callback={
            'learning_rate': (lambda iter: max(0.01, 0.3 - 0.003 * iter))
        }
    )
]
```

### Custom Callback

```python
def my_callback(env):
    # env: CallbackEnv with model, params, iteration, begin_iteration, end_iteration, evaluation_result_list
    if env.iteration % 100 == 0:
        print(f"Iteration {env.iteration}, score: {env.evaluation_result_list}")

callbacks = [my_callback]
```

## Scikit-learn API

### `LGBMClassifier` / `LGBMRegressor` / `LGBMRanker`

Full sklearn compatibility: `fit()`, `predict()`, `predict_proba()`, `score()`, `get_params()`, `set_params()`. Compatible with `GridSearchCV`, `Pipeline`, `cross_validate`.

```python
from lightgbm import LGBMClassifier

clf = LGBMClassifier(
    n_estimators=200,
    learning_rate=0.05,
    num_leaves=31,
    max_depth=-1,
    subsample_for_bin=200000,
    objective=None,         # auto-inferred
    class_weight=None,      # 'balanced' or dict
    min_split_gain=0.0,
    min_child_weight=0.0,
    min_child_samples=20,
    subsample=1.0,
    subsample_freq=0,
    colsample_bytree=1.0,
    reg_alpha=0.0,
    reg_lambda=0.0,
    random_state=None,
    n_jobs=-1,
    importance_type='split',
    verbose=-1,
)

# Fit with validation
clf.fit(
    X_train, y_train,
    sample_weight=None,
    init_score=None,
    group=None,             # for LGBMRanker
    eval_set=[(X_valid, y_valid)],
    eval_names=['valid'],
    eval_metric=None,
    callbacks=None,
    init_model=None,
)

# Predict
y_pred = clf.predict(X_test)
y_proba = clf.predict_proba(X_test)
y_raw = clf.predict(X_test, raw_score=True)
y_leaf = clf.predict(X_test, pred_leaf=True)
y_shap = clf.predict(X_test, pred_contrib=True)
```

### `fit()` Parameters

| Parameter | Description |
|---|---|
| `eval_set` | List of `(X, y)` tuples for validation |
| `eval_sample_weight` | Weights for eval sets |
| `eval_class_weight` | Class weights for eval sets |
| `eval_init_score` | Init scores for eval sets |
| `eval_group` | Group data for eval sets (ranking) |
| `eval_metric` | Override metric: str, callable, or list |
| `feature_name` | Feature names or `'auto'` |
| `categorical_feature` | Categorical features or `'auto'` |
| `callbacks` | LightGBM callbacks |
| `init_model` | Continue training from existing model |

### `predict()` Parameters

| Parameter | Description |
|---|---|
| `raw_score` | Return raw scores (default False) |
| `start_iteration` | Start index of iteration to predict |
| `num_iteration` | Number of iterations. None = use best_iteration |
| `pred_leaf` | Return leaf indices |
| `pred_contrib` | Return SHAP-style contributions |
| `validate_features` | Check feature match (DataFrame only) |

### Attributes After Fit

| Attribute | Description |
|---|---|
| `booster_` | Underlying `Booster` object |
| `n_features_in_` | Number of features |
| `classes_` | Class labels (classifier) |
| `n_classes_` | Number of classes (classifier) |
| `n_estimators_` | Actual number of boosting iterations |
| `best_iteration_` | Best iteration from early stopping |
| `best_score_` | Best scores dict |
| `eval_results_` | Recorded evaluation results |
| `feature_names_in_` | Feature names |
| `feature_importances_` | Feature importance array |

## Plotting (requires graphviz and matplotlib)

```python
from lightgbm import plot_importance, plot_metric, plot_tree, plot_split_value_histogram, create_tree_digraph

# Feature importance
plot_importance(model, importance_type='gain')

# Training metric history
plot_metric(eval_result)

# Tree visualization
plot_tree(model, tree_index=0)
create_tree_digraph(model, tree_index=0)  # returns Digraph

# Split value histogram
plot_split_value_histogram(model, feature_name='x1', data=X_train)
```

## Data Input Formats

| Format | Description |
|---|---|
| `np.ndarray` | 2D float array |
| `pd.DataFrame` | Auto-detects categorical columns when `categorical_feature='auto'` |
| `scipy.sparse` | CSR, CSC, COO, BSR, DIA, DOK, LIL sparse matrices |
| `pa.Table` / `pa.Array` | PyArrow tables and arrays |
| `str` / `Path` | LibSVM, CSV, TSV text files |
| `Sequence` | Iterable yielding batches of data |
| `List[np.ndarray]` | List of arrays, concatenated |

## Sequence (Batch Data Loading)

```python
from lightgbm import Sequence

def data_generator():
    for batch in load_batches():
        yield batch  # np.ndarray or pd.DataFrame

train_data = lgb.Dataset(Sequence(data_generator), label=y_train)
```
