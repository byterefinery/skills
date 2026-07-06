# Advanced Topics

## Callbacks

Callbacks hook into the training loop for early stopping, checkpoints, learning rate scheduling, and custom logic.

### EarlyStopping

```python
from xgboost.callback import EarlyStopping

# Basic: returns last model
callback = EarlyStopping(stopping_rounds=10, save_best=False)

# Returns best model
callback = EarlyStopping(
    stopping_rounds=10,
    save_best=True,     # Returns best iteration's model
    minimize=True,      # Set False to maximize metric
)

model = xgb.train(params, dtrain, num_boost_round=500,
                  evals=[(dval, "val")], callbacks=[callback])
```

### TrainingCheckPoint

Save model checkpoints during training.

```python
from xgboost.callback import TrainingCheckPoint

checkpoint = TrainingCheckPoint("model_checkpoint_", 10)  # Save every 10 rounds

model = xgb.train(params, dtrain, num_boost_round=200,
                  callbacks=[checkpoint])

# Resume from checkpoint
model = xgb.train(params, dtrain, num_boost_round=200,
                  xgb_model="model_checkpoint_100")
```

### LearningRateScheduler

```python
from xgboost.callback import LearningRateScheduler

# Step decay
def step_decay(epoch):
    return 0.1 * (0.5 ** (epoch // 50))

scheduler = LearningRateScheduler(step_decay)

model = xgb.train(params, dtrain, num_boost_round=200,
                  evals=[(dval, "val")], callbacks=[scheduler])
```

### Custom Callback

```python
from xgboost.callback import TrainingCallback

class PrintMetric(TrainingCallback):
    def after_iteration(self, model, epoch, evals_log):
        if epoch % 10 == 0:
            metric = evals_log["val"]["rmse"][-1]
            print(f"Epoch {epoch}: val-rmse = {metric:.4f}")
        return False  # False = continue training

# Return True to stop training
class StopOnThreshold(TrainingCallback):
    def after_iteration(self, model, epoch, evals_log):
        if evals_log["val"]["rmse"][-1] < 0.01:
            print(f"Target reached at epoch {epoch}")
            return True
        return False
```

## Feature Importance and Interpretability

### Feature Importance Scores

```python
booster = model.get_booster()

# Weight: number of times a feature appears in trees
weight = booster.get_score(importance_type="weight")

# Gain: average gain of splits using the feature
gain = booster.get_score(importance_type="gain")

# Cover: average coverage (samples affected) of splits
cover = booster.get_score(importance_type="cover")

# Total gain/cover
total_gain = booster.get_score(importance_type="total_gain")
total_cover = booster.get_score(importance_type="total_cover")
```

### Feature Contributions (SHAP-like)

```python
# Per-sample feature contributions
contribs = model.predict(X, pred_contribs=True)
# Shape: (n_samples, n_features + 1)
# Last column is the bias (base_score)

# Sum of contributions + bias = prediction
assert np.allclose(contribs.sum(axis=1), model.predict(X))

# Bar chart of mean absolute contributions
import matplotlib.pyplot as plt
mean_contribs = np.abs(contribs[:, :-1]).mean(axis=0)
feature_names = model.get_booster().feature_names
plt.barh(feature_names, mean_contribs)
```

### Tree Dumping

```python
# Text format
trees = model.get_dump(with_stats=True, dump_format="text")

# JSON format
trees_json = model.get_dump(with_stats=True, dump_format="json")

# Single tree
tree_0 = model.get_dump(with_stats=True)[0]
```

### Plotting

```python
import xgboost as xgb
import matplotlib.pyplot as plt

# Feature importance
xgb.plot_importance(model, importance_type="gain", max_num_features=15)
plt.tight_layout()
plt.show()

# Tree visualization
xgb.plot_tree(model, num_trees=0, rankdir="LR", size=12)
plt.tight_layout()
plt.show()

# Graphviz (requires graphviz package)
graph = xgb.to_graphviz(model, num_trees=0)
graph.render("tree_0")
```

## Model Slicing

Use a subset of trees for prediction:

```python
# Slice booster: use first 50 trees
sliced = model[0:50]
preds = sliced.predict(dtest)

# Via iteration_range in predict
preds = model.predict(dtest, iteration_range=(0, 50))

# Best iteration from early stopping
best_iter = model.best_iteration  # Set by EarlyStopping callback
preds = model.predict(dtest, iteration_range=(0, best_iter + 1))
```

## Hyperparameter Tuning

### With Optuna

```python
import optuna
import xgboost as xgb
from sklearn.model_selection import cross_val_score

def objective(trial):
    params = {
        "max_depth": trial.suggest_int("max_depth", 3, 12),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
        "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
        "gamma": trial.suggest_float("gamma", 0, 5),
        "tree_method": "hist",
        "eval_metric": "rmse",
        "random_state": 42,
    }

    model = xgb.XGBRegressor(
        n_estimators=500,
        early_stopping_rounds=20,
        verbosity=0,
        **params,
    )

    scores = cross_val_score(
        model, X, y, cv=5, scoring="neg_root_mean_squared_error",
        fit_kwargs={"verbose": False},
    )
    return scores.mean()

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=100)
print(study.best_params)
```

### With scikit-learn GridSearchCV

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    "max_depth": [3, 6, 9],
    "learning_rate": [0.01, 0.1, 0.2],
    "n_estimators": [100, 200, 500],
    "subsample": [0.8, 1.0],
    "colsample_bytree": [0.8, 1.0],
}

grid = GridSearchCV(
    xgb.XGBRegressor(tree_method="hist", random_state=42),
    param_grid, cv=5, scoring="neg_root_mean_squared_error",
    n_jobs=-1, verbose=1,
)
grid.fit(X, y)
print(grid.best_params_, grid.best_score_)
```

## Monotone Constraints

Force features to have monotonic relationships with the target:

```python
# Dictionary form (feature name → constraint)
constraints = {
    "age": 1,           # Monotonically increasing
    "debt_ratio": -1,   # Monotonically decreasing
    "income": 0,        # No constraint
}

model = xgb.XGBRegressor(monotone_constraints=constraints)

# String form (positional)
model = xgb.XGBRegressor(monotone_constraints="(1,0,-1,1)")
```

Values: `1` = increasing, `-1` = decreasing, `0` = no constraint.

## Interaction Constraints

Restrict which features can interact within a tree:

```python
# Features in same group can interact; features in different groups cannot
constraints = [[0, 1, 2], [3, 4, 5]]

model = xgb.XGBRegressor(interaction_constraints=constraints)
```

## Multi-Target Regression

```python
# Multiple targets
reg = xgb.XGBRegressor(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    multi_strategy="one_output_per_tree",  # or "multi_output_tree"
)

# y shape: (n_samples, n_targets)
reg.fit(X_train, Y_train)  # Y_train.shape = (1000, 3)
preds = reg.predict(X_val)  # Shape: (n_val, 3)
```

## Distributed Training

XGBoost supports distributed training via Dask, Spark, and Rabit.

### Dask

```python
import dask.dataframe as dd
from xgboost.dask import DaskXGBRegressor

ddf = dd.read_csv("s3://bucket/data/*.csv")

model = DaskXGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1)
model.fit(ddf.drop("target", axis=1), ddf["target"])
preds = model.predict(ddf.drop("target", axis=1))
```

### PySpark

```python
from xgboost.spark import SparkXGBRegressor

spark_df = spark.read.parquet("hdfs://data/")

model = SparkXGBRegressor(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    features_col="features",
    label_col="label",
)
model.fit(spark_df)
```

## Global Config Context

```python
import xgboost as xgb

# Set globally
xgb.set_config(verbosity=2)

# Temporary context
with xgb.config_context(verbosity=0, use_rmm=False):
    model = xgb.train(params, dtrain, num_boost_round=100)

# Inspect
print(xgb.get_config())
```
