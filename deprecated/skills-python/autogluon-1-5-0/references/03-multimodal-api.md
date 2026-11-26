# MultiModalPredictor API Reference

## Constructor

```python
MultiModalPredictor(
    label: str = None,
    problem_type: str = None,
    query: str | list[str] = None,
    response: str | list[str] = None,
    match_label: int | str = None,
    presets: str = None,
    eval_metric: str | Scorer = None,
    hyperparameters: dict = None,
    path: str = None,
    verbosity: int = 2,
    num_classes: int = None,
    classes: list = None,
    pretrained: bool = True,
    use_ensemble: bool = False,
    ensemble_size: int = 2,
    ensemble_mode: str = "one_shot",
    sample_data_path: str = None,
)
```

## Problem Types

### Standard

- `binary` — binary classification
- `multiclass` — multi-class classification
- `regression` — regression
- `classification` — auto-detected binary or multiclass

### Advanced (some support zero-shot inference without fit)

- `object_detection` — bounding box detection (requires mmdet)
- `ner` / `named_entity_recognition` — named entity extraction
- `text_similarity` — text-text semantic matching (zero-shot available)
- `image_similarity` — image-image semantic matching (zero-shot available)
- `image_text_similarity` — text-image semantic matching (zero-shot available)
- `feature_extraction` — extract embeddings (inference only)
- `zero_shot_image_classification` — zero-shot classification (inference only)
- `few_shot_classification` — few-shot image/text classification
- `semantic_segmentation` — segmentation with SAM

## fit()

```python
predictor.fit(
    train_data: pd.DataFrame,
    presets: str = None,               # 'best_quality', 'high_quality', 'medium_quality'
    tuning_data: pd.DataFrame = None,
    time_limit: int = None,
    hyperparameters: str | list[str] | dict = None,
    column_types: dict = None,         # {'col': 'text', 'image': 'image_path', ...}
    holdout_frac: float = None,
    teacher_predictor: str | MultiModalPredictor = None,
    seed: int = 0,
    standalone: bool = True,
    hyperparameter_tune_kwargs: dict = None,
)
```

### Presets

- `best_quality` — highest accuracy, longest training
- `best_quality_hpo` — best quality with hyperparameter optimization
- `high_quality` — default. Good accuracy/speed balance.
- `high_quality_hpo` — high quality with HPO
- `medium_quality` — faster training, lower accuracy
- `medium_quality_hpo` — medium quality with HPO

### Column Types

Auto-inferred from data. Override with `column_types`:

```python
column_types = {
    "item_name": "text",
    "image": "image_path",
    "description": "text",
    "price": "numerical",
    "category": "categorical",
}
```

### Hyperparameters

Override defaults via string, list, or dict:

```python
# String format
hyperparameters = "model.hf_text.checkpoint_name=google/electra-small-discriminator model.timm_image.checkpoint_name=swin_small_patch4_window7_224"

# Dict format
hyperparameters = {
    "model.hf_text.checkpoint_name": "google/electra-small-discriminator",
    "model.timm_image.checkpoint_name": "swin_small_patch4_window7_224",
    "env.batch_size": 128,
    "env.num_gpus": 1,
    "optim.max_epochs": 50,
}
```

Key config namespaces: `model.*`, `env.*`, `optim.*`, `data.*`.

## Prediction

```python
predictor.predict(data: pd.DataFrame)          # class labels or regression values
predictor.predict_proba(data: pd.DataFrame)    # probability estimates
```

## Evaluation

```python
predictor.evaluate(
    data: pd.DataFrame,
    metrics: list[str] = None,
    return_pred: bool = False,
)
```

## Semantic Matching

```python
# Setup
predictor = MultiModalPredictor(
    query="query_text",
    response="response_text",
    match_label="duplicate",
    problem_type="text_similarity",
)

# Train (or use zero-shot)
predictor.fit(train_data)

# Predict
scores = predictor.predict(test_data)
```

## Object Detection

```python
predictor = MultiModalPredictor(
    problem_type="object_detection",
    presets="high_quality",
)

# Requires: pip install mmdet pycocotools
# Train
predictor.fit(train_data)

# Predict
predictions = predictor.predict(test_data)
```

## Knowledge Distillation

```python
# Train a teacher model
teacher = MultiModalPredictor(label="label").fit(train_data, presets="best_quality")

# Distill to a smaller student
student = MultiModalPredictor(label="label").fit(
    train_data,
    teacher_predictor=teacher,
    hyperparameters={"model.names": ["text_mlp"]},
)
```

## Ensemble

```python
predictor = MultiModalPredictor(
    label="label",
    use_ensemble=True,
    ensemble_size=3,
    ensemble_mode="one_shot",  # or 'iterative'
)
predictor.fit(train_data)
```

## fit_summary()

```python
predictor.fit_summary(verbosity=0, show_plot=False)
```

## Save / Load

```python
predictor.save()
loaded = MultiModalPredictor.load(path)
```

## Hyperparameter Tuning

```python
from ray import tune

predictor.fit(
    train_data,
    hyperparameters={
        "optim.lr": tune.uniform(1e-5, 1e-3),
        "model.ft_transformer.ffn_dropout": tune.uniform(0.0, 0.5),
    },
    hyperparameter_tune_kwargs={
        "searcher": "random",
        "scheduler": "FIFO",
        "num_trials": 20,
    },
    time_limit=600,
)
```

## Gotchas

- **GPU required for image models** — most image backbones and multimodal models need CUDA. CPU-only fallback is slow and limited.
- **Object detection requires extra packages** — `mim install "mmcv==2.1.0"`, `pip install "mmdet==3.2.0" pycocotools`.
- **Image paths must be absolute or relative to working directory** — relative paths in DataFrames are resolved from the current working directory at fit time.
- **`feature_extraction` is inference-only** — cannot call `fit()`. Load a pretrained model and call `predict()` directly.
- **`zero_shot_image_classification` is inference-only** — no `fit()` needed. Pass class names via `classes` parameter.
