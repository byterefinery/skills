# CatBoostRanker

## Overview

`CatBoostRanker` implements learning-to-rank using gradient boosting. It optimizes ranking-specific loss functions (YetiRank, PairLogit, etc.) and supports group-wise evaluation metrics (NDCG, MAP, Precision).

## Constructor

```python
CatBoostRanker(
    iterations=500,
    learning_rate=0.03,
    depth=6,
    l2_leaf_reg=3.0,
    loss_function='YetiRank',
    border_count=254,
    task_type=None,
    devices=None,
    ...
)
```

### Ranking Loss Functions

| Loss Function | Description |
|---|---|
| `'YetiRank'` | Default. Pointwise approximation of listwise objective. Best general-purpose choice |
| `'YetiRankPairwise'` | Pairwise variant of YetiRank |
| `'StochasticFilter'` | Optimizes for filtering tasks |
| `'StochasticRank'` | Optimizes for ranking tasks |
| `'QueryCrossEntropy'` | Query-level cross entropy |
| `'QueryRMSE'` | Query-level RMSE |
| `'GroupQuantile'` | Group-wise quantile regression |
| `'QuerySoftMax'` | Softmax over query items |
| `'PairLogit'` | Pairwise logistic loss |
| `'PairLogitPairwise'` | Pairwise variant |

## fit()

```python
model.fit(
    X, y=None,
    cat_features=None,
    text_features=None,
    embedding_features=None,
    group_id=None,        # REQUIRED: group (query) ID for each sample
    group_weight=None,    # optional group weights
    subgroup_id=None,     # optional subgroup IDs within groups
    pairs=None,           # optional explicit pairs
    pairs_weight=None,    # optional pair weights
    sample_weight=None,
    baseline=None,
    use_best_model=None,
    eval_set=None,
    verbose=None,
    early_stopping_rounds=None,
    init_model=None,
    callbacks=None
)
```

### group_id

Required for ranking. Maps each sample to a query/group. Samples within the same group are ranked together.

```python
import numpy as np
from catboost import CatBoostRanker

# 1000 samples, 100 queries (10 samples per query)
group_id = np.repeat(np.arange(100), 10)

model = CatBoostRanker(loss_function='YetiRank', iterations=100)
model.fit(X_train, y_train, group_id=group_id,
          eval_set=(X_val, y_val, group_id_val))
```

### pairs

Optional explicit pairwise preferences. Shape `(n_pairs, 2)` where each row is `(winner_index, loser_index)` in the training set.

```python
pairs = [[0, 5], [1, 3], [2, 4]]  # sample 0 > sample 5, etc.
model.fit(X_train, y_train, group_id=group_id, pairs=pairs)
```

### subgroup_id

Optional subgroup IDs for within-group sub-ranking.

## eval_set

For ranking, eval_set tuples must include group_id:

```python
# As Pool
eval_pool = Pool(X_val, y_val, cat_features=[0], group_id=group_id_val)

# As tuple
eval_set = (X_val, y_val, group_id_val)
```

## Ranking Metrics

Use `eval_metrics()` or `custom_metric` for ranking-specific evaluation:

```python
results = model.eval_metrics(
    eval_pool,
    ['NDCG@10', 'MAP@10', 'Precision@5', 'Recall@5', 'MRR@10']
)
```

Available ranking metrics: `'NDCG'`, `'MAP'`, `'Precision'`, `'Recall'`, `'MRR'`, `'AverageHitRank'`. Append `@k` for top-k (e.g., `'NDCG@10'`).

## predict()

```python
scores = model.predict(X_test)
```

Returns raw ranking scores (higher = better rank). Apply `argsort` to get ranked order.
