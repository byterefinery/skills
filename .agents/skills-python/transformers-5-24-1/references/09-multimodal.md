# Multimodal (v5.24.1)

## AutoProcessor

For models that take more than one input kind (text + image, audio + text, ...), use `AutoProcessor` — it wraps the tokenizer and image/video processors and handles both input types in one call.

```python
from transformers import AutoProcessor, AutoModelForImageTextToText

processor = AutoProcessor.from_pretrained("HuggingFaceTB/SmolVLM-256M-Instruct")
model = AutoModelForImageTextToText.from_pretrained("HuggingFaceTB/SmolVLM-256M-Instruct")
```

Processor attributes serialize as a nested dict in `processor_config.json` in v5 (old per-attribute config files still load).

## Image processors — backend architecture

The old slow/fast dual-file design was replaced by named backends:

- `image_processing_<model>.py` → **torchvision** backend (default; was `FooImageProcessorFast`)
- `image_processing_pil_<model>.py` → **PIL** backend (was `FooImageProcessor`)

```python
# v5 — use `backend`, not the deprecated `use_fast`
processor = AutoImageProcessor.from_pretrained("google/vit-base-patch16-224", backend="torchvision")
processor = AutoImageProcessor.from_pretrained("google/vit-base-patch16-224", backend="pil")
```

- Default backend: `"torchvision"` if installed, else `"pil"`; a missing backend falls back to another available one with a warning
- `FooImageProcessor` now means the torchvision-backed class; `FooImageProcessorPil` is the PIL-backed class; importing `*Fast` names still works but emits a deprecation warning
- `processor.is_fast` is deprecated — check `processor.backend == "torchvision"`
- `AutoImageProcessor.register()` uses `image_processor_classes={"pil": MyPilProcessor, "torchvision": MyTorchvisionProcessor}` (the old `slow_image_processor_class`/`fast_image_processor_class` kwargs are deprecated)
- **Custom backends** — any string key: `MyProcessor.register_backend(name="mlx", backend_class=MyMlxProcessor, availability_check=lambda: is_mlx_available())`, then `from_pretrained(..., backend="mlx")`
- `XXXFeatureExtractors` classes were **removed** — use the `XXXImageProcessor` for all vision models
- The `image_processing_utils_fast` module is gone; shared logic lives in `image_processing_utils`

Video processors are first-class (`BaseVideoProcessor`, `video_processors.md`) and `pipeline()` accepts a `video_processor` argument.

## Multimodal chat templates

Messages carry a `content` list of typed parts for VLMs:

```python
messages = [{
    "role": "user",
    "content": [
        {"type": "image", "image": "https://example.com/photo.jpg"},
        {"type": "text", "text": "What is in the image?"},
    ],
}]
inputs = processor.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")
```

`image-text-to-text` pipelines no longer accept images as a separate argument — embed the image in the chat `content` field.

## Accessing VLM components

The `model.language_model` shortcut was removed on vision-language generative models:

```python
# v5 — the model.language_model shortcut is gone
decoder = model.get_decoder()            # recommended
language_model = model.model.language_model
```

## Feature-extraction helpers

`get_text_features`, `get_image_features`, `get_audio_features`, `get_video_features` now return a `BaseModelOutputWithPooling` (v4 returned a plain tensor):

```python
# v4
text_embeddings = model.get_text_features(**inputs)

# v5 — take the pooled output for the old behavior
outputs = model.get_text_features(**inputs, return_dict=True)
text_embeddings = outputs.pooler_output
```

There is no universal shape for `last_hidden_state` or `pooler_output` — inspect a small forward pass before assuming shapes. `output_hidden_states=True` / `output_attentions=True` populate `hidden_states` / `attentions`.

## Vision encoder hidden states

For many vision encoders (ViT, DeiT, DINOv2/DINOv3, ...), `hidden_states[-1]` is the output of the last block **before** the final layernorm, while `last_hidden_state` is normalized. Use `last_hidden_state` for final features. `ViTConfig(tie_last_hidden_states=True)` (available from v5.18.0) restores the pre-v4.57.2 behavior where the two were identical.
