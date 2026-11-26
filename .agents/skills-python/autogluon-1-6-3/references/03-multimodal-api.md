# MultiModalPredictor API (AutoGluon 1.6.3)

Install: `pip install autogluon.multimodal`.

## Text prediction

Classification or regression on text columns. Input is a DataFrame or dict of lists; the label column name is set via `label=`.

```python
from autogluon.multimodal import MultiModalPredictor

predictor = MultiModalPredictor(label="label").fit(train_data, time_limit=60)
predictions = predictor.predict({"sentence": ["text one", "text two"]})
probs = predictor.predict_proba(test_data)
score = predictor.evaluate(test_data, metrics=["acc", "f1"])
```

Regression: numeric label; evaluate with `metrics=['rmse', 'pearsonr', 'spearmanr']`. Semantic-matching style tasks use two text columns (e.g. `sentence1`, `sentence2`) and a numeric score label.

## Image prediction

Input column contains image file paths or raw bytes (one image per row).

```python
predictor = MultiModalPredictor(label="label").fit(train_data)   # DataFrame with 'image' + label columns
predictions = predictor.predict({"image": ["/path/to/img.jpg"]})
proba = predictor.predict_proba({"image": [img_bytes]})
scores = predictor.evaluate(test_data_path, metrics=["accuracy"])
```

## Common operations

- `MultiModalPredictor.load(model_path)` — reload a saved model.
- `predictor.save(new_path)` — save to a new location.
- `predictor.extract_embedding(data)` — feature vectors for text or images.
- Column types are inferred automatically; override with `column_types={"col": "text"}` (supported: `image_path`, `text`, `numerical`, `categorical`).

## Tasks supported

Classification, regression, object detection, named entity recognition, semantic matching, image segmentation. Foundation model zoos: HuggingFace, TIMM, MMDetection.

## Gotchas

- Mac/Apple Silicon: CPU-only for multimodal; no GPU acceleration.
- Multimodal training is compute-heavy — prototype on a sample first, then scale up data and `time_limit`.
- 1.6 updates: missing image backbones added to the HF model list; semantic segmentation module updated.
