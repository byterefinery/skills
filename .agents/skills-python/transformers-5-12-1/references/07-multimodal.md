# Multimodal Reference

## Image Processing

### AutoImageProcessor

```python
from transformers import AutoImageProcessor
from PIL import Image

processor = AutoImageProcessor.from_pretrained("google/vit-base-patch16-224")

# From PIL Image
image = Image.open("photo.jpg")
inputs = processor(images=image, return_tensors="pt")

# From URL
inputs = processor(images="https://example.com/photo.jpg", return_tensors="pt")

# From numpy array
import numpy as np
array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
inputs = processor(images=array, return_tensors="pt")

# From torch tensor
import torch
tensor = torch.rand(3, 224, 224)  # CHW format
inputs = processor(images=tensor, return_tensors="pt")
```

### Key Image Processor Parameters

```python
inputs = processor(
    images=image,
    return_tensors="pt",
    do_resize=True,              # Resize to target size
    size={"height": 224, "width": 224},  # Target size
    do_normalize=True,           # Normalize with mean/std
    image_mean=[0.485, 0.456, 0.406],
    image_std=[0.229, 0.224, 0.225],
    do_center_crop=False,        # Center crop
    crop_size={"height": 224, "width": 224},
    do_flip=False,               # Random horizontal flip
    do_rotate=False,             # Random rotation
)
```

## Feature Extraction (Audio)

### AutoFeatureExtractor

```python
from transformers import AutoFeatureExtractor
import numpy as np

extractor = AutoFeatureExtractor.from_pretrained("facebook/wav2vec2-base-960h")

# From numpy array (raw audio samples)
audio = np.random.randn(16000)  # 1 second at 16kHz
inputs = extractor(
    audio,
    sampling_rate=16000,
    return_tensors="pt",
)

# From file path
inputs = extractor(
    "audio.wav",
    sampling_rate=16000,
    return_tensors="pt",
)

# From URL
inputs = extractor(
    "https://example.com/audio.flac",
    sampling_rate=16000,
    return_tensors="pt",
)
```

## AutoProcessor (Multimodal)

Combines tokenizer + image/audio processor for vision-language and other multimodal models.

```python
from transformers import AutoProcessor, AutoModelForVision2Seq
from PIL import Image

processor = AutoProcessor.from_pretrained("llava-hf/llava-1.5-7b-hf")
model = AutoModelForVision2Seq.from_pretrained("llava-hf/llava-1.5-7b-hf")

# Process text + image
image = Image.open("photo.jpg")
inputs = processor(
    text="Describe this image.",
    images=image,
    return_tensors="pt",
).to(model.device)

# Generate
outputs = model.generate(**inputs, max_new_tokens=256)
print(processor.decode(outputs[0], skip_special_tokens=True))
```

### Processor Components

```python
# Access individual components
processor.tokenizer      # The text tokenizer
processor.image_processor  # The image processor
processor.feature_extractor  # The audio feature extractor (if applicable)

# Use components independently
text_inputs = processor.tokenizer("Hello", return_tensors="pt")
image_inputs = processor.image_processor(image, return_tensors="pt")
```

## Vision-Language Models

### Common Architectures

| Model | Auto Class | Processor |
|-------|-----------|-----------|
| LLaVA | `AutoModelForVision2Seq` | `AutoProcessor` |
| Idefics / Idefics2 | `AutoModelForVision2Seq` | `AutoProcessor` |
| Qwen2-VL | `AutoModelForVision2Seq` | `AutoProcessor` |
| InternVL | `AutoModelForVision2Seq` | `AutoProcessor` |
| SmolVLM | `AutoModelForVision2Seq` | `AutoProcessor` |
| mPLUG-Owl | `AutoModelForVision2Seq` | `AutoProcessor` |
| BLIP-2 | `AutoModelForVision2Seq` | `AutoProcessor` |
| InstructBLIP | `AutoModelForVision2Seq` | `AutoProcessor` |

### Vision-Language Chat

```python
from transformers import AutoProcessor, AutoModelForVision2Seq
from PIL import Image

processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-7B-Instruct")
model = AutoModelForVision2Seq.from_pretrained("Qwen/Qwen2-VL-7B-Instruct")

messages = [
    {
        "role": "user",
        "content": [
            {"type": "image"},
            {"type": "text", "text": "What is in this image?"},
        ],
    },
]

image = Image.open("photo.jpg")

# Apply chat template with image
prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
inputs = processor(
    text=prompt,
    images=image,
    return_tensors="pt",
).to(model.device)

outputs = model.generate(**inputs, max_new_tokens=256)
print(processor.decode(outputs[0], skip_special_tokens=True))
```

### Multi-Image Input

```python
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image"},
            {"type": "image"},
            {"type": "text", "text": "Compare these two images."},
        ],
    },
]

images = [Image.open("photo1.jpg"), Image.open("photo2.jpg")]
prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
inputs = processor(text=prompt, images=images, return_tensors="pt")
```

## Audio Models

### Speech Recognition (Whisper)

```python
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
import torch

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    "openai/whisper-large-v3",
    torch_dtype=torch.float16,
    device_map="cuda",
)
processor = AutoProcessor.from_pretrained("openai/whisper-large-v3")

# Process audio
inputs = processor(
    "audio.flac",
    return_tensors="pt",
    sampling_rate=16000,
)
inputs = inputs.to(model.device)

# Generate transcription
outputs = model.generate(**inputs)
print(processor.batch_decode(outputs, skip_special_tokens=True))
```

### wav2vec2 (CTC-based ASR)

```python
from transformers import AutoFeatureExtractor, AutoModelForCTC, AutoTokenizer

model = AutoModelForCTC.from_pretrained("facebook/wav2vec2-base-960h")
feature_extractor = AutoFeatureExtractor.from_pretrained("facebook/wav2vec2-base-960h")
tokenizer = AutoTokenizer.from_pretrained("facebook/wav2vec2-base-960h")

inputs = feature_extractor("audio.wav", return_tensors="pt", sampling_rate=16000)
with torch.no_grad():
    logits = model(inputs.input_values).logits

predicted = torch.argmax(logits, dim=-1)
text = tokenizer.batch_decode(predicted)
```

## Video Processing

### AutoVideoProcessor

```python
from transformers import AutoVideoProcessor, AutoModelForVideoClassification

processor = AutoVideoProcessor.from_pretrained("facebook/xclip-base-patch32")
model = AutoModelForVideoClassification.from_pretrained("facebook/xclip-base-patch32")

# Process video (list of frames)
from PIL import Image
frames = [Image.open(f"frame_{i}.jpg") for i in range(16)]
inputs = processor(videos=frames, return_tensors="pt")

outputs = model(**inputs)
predictions = outputs.logits.softmax(dim=-1)
```

## Any-to-Any Models

Models that accept mixed modalities and produce mixed outputs:

```python
from transformers import pipeline

any_to_any = pipeline("any-to-any", model="Qwen/Qwen2-Audio-7B-Instruct")

# Text + audio input
result = any_to_any(
    [
        {"type": "text", "content": "Transcribe this audio."},
        {"type": "audio", "content": "audio.wav"},
    ]
)
```

## Image-to-Image

```python
from transformers import pipeline

# Image-to-image translation
pipe = pipeline("image-to-image", model="stabilityai/stable-diffusion-xl-refiner-1.0")
result = pipe("a photo of a cat", image=prompt_image)
```

## Depth Estimation

```python
from transformers import pipeline
from PIL import Image

pipe = pipeline("depth-estimation", model="Intel/dpt-large")
image = Image.open("photo.jpg")
result = pipe(image)
# result['predicted_depth'] — depth tensor
# result['depth'] — depth as PIL Image
```

## Zero-Shot Image Classification (CLIP)

```python
from transformers import pipeline

classifier = pipeline("zero-shot-image-classification", model="openai/clip-vit-base-patch32")

result = classifier(
    "photo.jpg",
    candidate_labels=["cat", "dog", "bird", "fish"],
)
# [{'label': 'cat', 'score': 0.95}, ...]
```

## Object Detection

```python
from transformers import pipeline

detector = pipeline("object-detection", model="facebook/detr-resnet-50")

result = detector("photo.jpg")
# [{'box': {'xmin': 10, 'ymin': 20, 'xmax': 100, 'ymax': 200},
#    'label': 'cat', 'score': 0.95}]
```

## Mask Generation (SAM)

```python
from transformers import pipeline

segmenter = pipeline("mask-generation", model="facebook/sam-vit-huge")

result = segmenter("photo.jpg")
# List of masks with bounding boxes and scores
```

## Multimodal Pipeline

```python
from transformers import pipeline

# Image-to-text
pipe = pipeline("image-text-to-text", model="-salesforce/blip-image-captioning-base")
result = pipe("photo.jpg")
# [{'generated_text': 'a photo of ...'}]

# Document QA
pipe = pipeline("document-question-answering", model="impira/layoutlm-document-qa")
result = pipe(image="document.jpg", question="What is the total amount?")
```
