# Multimodal

Transformers supports vision, audio, and multimodal models through image processors, feature extractors, and unified processors.

## Image Processing

```python
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image

# Load processor and model
processor = AutoImageProcessor.from_pretrained("google/vit-base-patch16-224")
model = AutoModelForImageClassification.from_pretrained("google/vit-base-patch16-224")

# Process image
image = Image.open("image.jpg").convert("RGB")
inputs = processor(images=image, return_tensors="pt")

# Inference
with torch.no_grad():
    outputs = model(**inputs)

predictions = outputs.logits.softmax(dim=-1)
top_class = predictions.argmax().item()
print(model.config.id2label[top_class])
```

### ImageProcessor Options

```python
inputs = processor(
    images=image,
    return_tensors="pt",
    do_resize=True,
    size={"height": 224, "width": 224},
    do_normalize=True,
    image_mean=[0.485, 0.456, 0.406],
    image_std=[0.229, 0.224, 0.225],
)
```

## Feature Extraction (Audio)

```python
from transformers import AutoFeatureExtractor, AutoModelForCTC
import soundfile as sf

# Load
feature_extractor = AutoFeatureExtractor.from_pretrained("facebook/wav2vec2-base-960h")
model = AutoModelForCTC.from_pretrained("facebook/wav2vec2-base-960h")
tokenizer = AutoTokenizer.from_pretrained("facebook/wav2vec2-base-960h")

# Load audio
audio, sampling_rate = sf.read("audio.wav")

# Extract features
inputs = feature_extractor(audio, sampling_rate=sampling_rate, return_tensors="pt")

# Inference
with torch.no_grad():
    outputs = model(**inputs)

logits = outputs.logits
predicted_ids = torch.argmax(logits, dim=-1)
text = tokenizer.batch_decode(predicted_ids)
print(text[0])
```

## AutoProcessor (Unified)

For multimodal models that need both text and non-text processing:

```python
from transformers import AutoProcessor, AutoModelForVision2Seq

# Vision-language model
processor = AutoProcessor.from_pretrained("llava-hf/llava-1.5-7b-hf")
model = AutoModelForVision2Seq.from_pretrained("llava-hf/llava-1.5-7b-hf")

# Process both image and text
image = Image.open("image.jpg").convert("RGB")
inputs = processor(
    images=image,
    text="Describe this image.",
    return_tensors="pt",
)

# Generate
with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=50,
    )

print(processor.decode(outputs[0], skip_special_tokens=True))
```

### Processor with Chat

```python
from transformers import AutoProcessor, AutoModelForVision2Seq

processor = AutoProcessor.from_pretrained("llava-hf/llava-1.5-7b-hf")
model = AutoModelForVision2Seq.from_pretrained("llava-hf/llava-1.5-7b-hf")

# Chat format
conversation = [
    {
        "role": "user",
        "content": [
            {"type": "image"},
            {"type": "text", "text": "What is in this image?"},
        ],
    },
]

inputs = processor(
    images=image,
    text=processor.apply_chat_template(conversation, add_generation_prompt=True),
    return_tensors="pt",
)

outputs = model.generate(**inputs, max_new_tokens=50)
print(processor.decode(outputs[0], skip_special_tokens=True))
```

## Vision Tasks

### Object Detection

```python
from transformers import pipeline

detector = pipeline(
    "object-detection",
    model="facebook/detr-resnet-50",
)

results = detector("https://example.com/image.jpg")
for result in results:
    print(f"{result['label']}: {result['score']:.3f}")
    print(f"  Box: {result['box']}")  # {"xmin": ..., "ymin": ..., "xmax": ..., "ymax": ...}
```

### Image Segmentation

```python
from transformers import pipeline

segmenter = pipeline(
    "image-segmentation",
    model="facebook/detr-resnet-50-panoptic",
)

results = segmenter("image.jpg")
for result in results:
    print(f"{result['label']}: {result['score']:.3f}")
    # result['mask'] is a PIL Image with the segmentation mask
```

### Depth Estimation

```python
from transformers import pipeline

depth_estimator = pipeline(
    "depth-estimation",
    model="Intel/dpt-large",
)

result = depth_estimator("image.jpg")
# result['predicted_depth'] — tensor with depth values
# result['depth'] — PIL Image visualization
```

### Zero-Shot Image Classification

```python
from transformers import pipeline

classifier = pipeline(
    "zero-shot-image-classification",
    model="openai/clip-vit-base-patch32",
)

result = classifier(
    "image.jpg",
    candidate_labels=["cat", "dog", "bird", "fish"],
)
for label, score in zip(result["labels"], result["scores"]):
    print(f"{label}: {score:.3f}")
```

## Audio Tasks

### Speech Recognition

```python
from transformers import pipeline

recognizer = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-large-v3",
)

result = recognizer("audio.flac")
print(result["text"])

# With word timestamps
result = recognizer("audio.flac", return_timestamps="word")
for chunk in result.get("chunks", []):
    print(f"{chunk['timestamp']}: {chunk['text']}")
```

### Audio Classification

```python
from transformers import pipeline

classifier = pipeline(
    "audio-classification",
    model="superb/hubert-large-superb-er",
)

result = classifier("audio.wav")
for item in result:
    print(f"{item['label']}: {item['score']:.3f}")
```

## Video Processing

```python
from transformers import pipeline

# Video classification
classifier = pipeline(
    "video-classification",
    model="MCG-NJU/videomae-base",
)

result = classifier("video.mp4")
```

## Batch Processing

```python
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image

processor = AutoImageProcessor.from_pretrained("google/vit-base-patch16-224")
model = AutoModelForImageClassification.from_pretrained("google/vit-base-patch16-224")
model.eval()

# Batch of images
images = [Image.open(f"image_{i}.jpg").convert("RGB") for i in range(4)]

inputs = processor(images=images, return_tensors="pt", padding=True)

with torch.no_grad():
    outputs = model(**inputs)

predictions = outputs.logits.softmax(dim=-1)
for i, pred in enumerate(predictions):
    top_class = pred.argmax().item()
    print(f"Image {i}: {model.config.id2label[top_class]} ({pred[top_class]:.3f})")
```

## Gotchas

- **`AutoProcessor` for multimodal** — use `AutoProcessor` instead of separate tokenizer + image processor for vision-language models. It handles both modalities.
- **`images` parameter accepts multiple types** — PIL Image, numpy array, tensor, URL string, or list of any. The processor handles conversion.
- **`return_tensors="pt"` is essential** — always specify tensor format for model input.
- **`do_resize` and `size`** — processors resize images to model-specific dimensions. Check `processor.size` for expected dimensions.
- **`do_normalize`** — applies ImageNet-style normalization by default. Set `do_normalize=False` for custom normalization.
- **`padding` for batch images** — use `padding=True` when batching images of different sizes.
- **`feature_extractor` sampling rate** — audio models expect specific sampling rates (e.g., 16000 Hz for wav2vec2). Resample if needed.
- **`whisper` language detection** — pass `generate_kwargs={"language": "en"}` to force a language. Omit for auto-detection.
- **`return_timestamps` for whisper** — `"word"` for word-level, `"chunk"` for chunk-level, or `True` for segment-level.
- **`image_mean` and `image_std`** — normalization values vary by model. Use the processor's defaults (loaded from config).
- **`processor.apply_chat_template`** — not all processors support chat templates. Check `processor.tokenizer.chat_template`.
- **`crop` for object detection** — some detectors expect uncropped images. Check model card for preprocessing requirements.
- **`target_size` for segmentation** — output mask resolution may differ from input. Use `processor.post_process_segmentation()` for proper resizing.
- **`batch_size` in pipelines** — set `batch_size` parameter for controlled batching in pipeline inference.
- **`device` placement for multimodal** — ensure images/audio are on the same device as the model. Processors return CPU tensors by default.
- **`Pillow` required for image processing** — install with `pip install Pillow`.
- **`librosa`/`soundfile` for audio** — install audio libraries for loading audio files.
- **`video` requires `av`** — install with `pip install av` for video processing support.
- **`image_seq_length` for vision transformers** — number of patches = (H/P) × (W/P) where P is patch size. Affects sequence length.
- **`num_images` for batch multimodal** — some models support multiple images per prompt. Check model documentation.
