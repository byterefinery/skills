# 05 — Advanced Usage

## Embedding Extraction

Extract learned representations from any layer of the model:

```python
embeddings, idx_ranges = pipeline.embed(
    [torch.randn(100), torch.randn(200)],
    batch_size=256,
)
```

`embeddings` contains the hidden states; `idx_ranges` tracks the valid token indices per series (useful for variable-length inputs).

## Saving and Loading

Save a pipeline (base or fine-tuned) for later reuse:

```python
pipeline.save_pretrained("./my-model")
pipeline = Chronos2Pipeline.from_pretrained("./my-model", device_map="cuda")
```

S3 URIs are supported with extras: `pip install "chronos-forecasting[extras]"`.
