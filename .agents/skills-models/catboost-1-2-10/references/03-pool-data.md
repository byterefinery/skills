# Pool Class and Data Handling

## Pool

`Pool` is CatBoost's data container. It holds features, labels, and metadata (categorical features, weights, groups, etc.).

### Constructor

```python
Pool(
    data,                    # features: array, DataFrame, file path, or FeaturesData
    label=None,              # labels
    cat_features=None,       # categorical feature indices or names
    text_features=None,      # text feature indices or names
    embedding_features=None, # embedding feature indices or names
    embedding_features_data=None,  # embedding data (list or dict of arrays)
    weight=None,             # sample weights
    group_id=None,           # group IDs (for ranking)
    group_weight=None,       # group weights
    subgroup_id=None,        # subgroup IDs (for ranking)
    pairs=None,              # pairs for ranking
    pairs_weight=None,       # pair weights
    baseline=None,           # baseline predictions
    timestamp=None,          # timestamps (for time-ordered training)
    feature_names=None,      # feature name list
    feature_tags=None,       # feature tags dict
    thread_count=-1,
    log_cout=None,
    log_cerr=None
)
```

### Data Types

`data` accepts:
- `numpy.ndarray` — 2D array of features
- `pandas.DataFrame` / `pandas.Series` — column names become feature names
- `polars.DataFrame` / `polars.Series` — same as pandas
- `list` or `list of lists` — converted to numpy array
- `scipy.sparse.spmatrix` — sparse matrices supported
- `str` / `os.PathLike` — file path in CatBoost format
- `FeaturesData` — pre-processed feature data

### Categorical Features

```python
# By index
pool = Pool(X, y, cat_features=[0, 2, 5])

# By name (when feature_names are set)
pool = Pool(X, y, cat_features=['city', 'category', 'product_type'])

# From pandas — object dtype columns are auto-detected as categorical
df = pd.DataFrame({'num': [1, 2], 'cat': ['a', 'b']})
pool = Pool(df, y)  # 'cat' is automatically categorical
```

### Text Features

```python
pool = Pool(X, y, text_features=[3, 4])

# With text processing configuration
model = CatBoostClassifier(
    text_features=[3],
    text_processing={
        'tokenizers': [{'Type': 'Word'}],
        'dictionaries': [{'TrainFrom': 'CurrentData'}],
        'feature_calcers': [{'Type': 'RawTF', 'Dictionary': 0}]
    }
)
```

### Embedding Features

```python
import numpy as np

# Embedding data as list of arrays
embedding_data = [
    np.random.randn(100, 128),  # embedding for feature 0
    np.random.randn(100, 64),   # embedding for feature 1
]

pool = Pool(
    X, y,
    embedding_features=[0, 1],
    embedding_features_data=embedding_data
)

# Or as dict keyed by feature name
embedding_data = {
    'user_emb': np.random.randn(100, 128),
    'item_emb': np.random.randn(100, 64),
}
pool = Pool(
    X, y,
    embedding_features=['user_emb', 'item_emb'],
    embedding_features_data=embedding_data
)
```

### Feature Tags

Group features with cost weights for feature selection:

```python
feature_tags = {
    'demographics': {
        'features': [0, 1, 2],
        'cost': 1
    },
    'behavioral': {
        'features': [3, 4, 5],
        'cost': 2
    }
}
pool = Pool(X, y, feature_tags=feature_tags)
```

### Methods

```python
pool.num_row()              # number of samples
pool.num_col()              # number of features
pool.get_feature_names()    # list of feature names
pool.get_cat_feature_indices()
pool.get_text_feature_indices()
pool.get_embedding_feature_indices()

pool.save('data.pool')      # save to file
Pool('data.pool')           # load from file
```

## Data Input to fit()

`fit()` accepts data directly without explicit Pool:

```python
# numpy
model.fit(X_train, y_train, cat_features=[0, 2])

# pandas
model.fit(df_features, df_labels, cat_features=['city', 'category'])

# polars
model.fit(pl_features, pl_labels, cat_features=[0, 2])

# scipy sparse
model.fit(sparse_X, y_train)

# file path
model.fit('train.txt', column_description='train_columns.txt')
```

## Sparse Data

CatBoost supports `scipy.sparse` matrices (CSR, CSC, COO, etc.):

```python
from scipy.sparse import csr_matrix

X_sparse = csr_matrix(X_dense)
pool = Pool(X_sparse, y)
model.fit(pool)
```

Sparse matrices cannot have categorical or text features.

## Column Description File

For file-based data, use a column description:

```
# train_columns.txt
Label: 0
Categ: 1 3 5
Num: 2 4 6 7
Weight: 8
```

```python
pool = Pool('train.txt', column_description='train_columns.txt')
```

## train_eval_split()

Split a pool into train and eval:

```python
train_pool, eval_pool = pool.train_eval_split(
    has_time=False,
    is_classification=True,
    eval_fraction=0.2
)
```
