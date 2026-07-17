# Pipelines Reference

## `pipeline()` Function

High-level inference API that handles model loading, preprocessing, and postprocessing.

### Signature

```python
from transformers import pipeline

pipe = pipeline(
    task="text-generation",           # str: task name
    model="Qwen/Qwen2.5-1.5B",       # str or PreTrainedModel: model ID/path/instance
    config=None,                      # PreTrainedConfig or path
    tokenizer=None,                   # tokenizer ID/path/instance
    feature_extractor=None,           # feature extractor ID/path/instance
    image_processor=None,            # image processor ID/path/instance
    video_processor=None,            # video processor ID/path/instance
    processor=None,                  # processor ID/path/instance (multimodal)
    revision=None,                    # str: model revision
    use_fast=True,                    # bool: use fast tokenizer
    token=None,                       # str or bool: Hub auth
    device=None,                      # int, str, or torch.device
    device_map=None,                  # str or dict: device placement
    dtype="auto",                     # str or torch.dtype: model precision
    trust_remote_code=None,          # bool: allow custom code
    model_kwargs=None,               # dict: extra kwargs for from_pretrained
    pipeline_class=None,             # Pipeline subclass
    **kwargs,
)
```

### Quick Start

```python
from transformers import pipeline

# Text generation
gen = pipeline("text-generation", model="Qwen/Qwen2.5-1.5B")
gen("Once upon a time ")

# Sentiment analysis (alias for text-classification)
sent = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
sent("I love using transformers!")

# Named entity recognition (alias for token-classification)
ner = pipeline("ner", model="bert-base-cased-finetuned-conll03-english")
ner("Hugging Face is in New York.")
```

## Supported Tasks

### Text Tasks

| Task | Pipeline Class | Default Model | Input | Output |
|------|---------------|---------------|-------|--------|
| `text-generation` | `TextGenerationPipeline` | Qwen/Qwen2.5-1.5B | str or list of messages | list of dict with `generated_text` |
| `text-classification` | `TextClassificationPipeline` | distilbert-base-uncased-finetuned-sst-2 | str | list of dict with `label`, `score` |
| `token-classification` | `TokenClassificationPipeline` | bert-large-cased-finetuned-conll03 | str | list of dict with `entity`, `score`, `word` |
| `fill-mask` | `FillMaskPipeline` | distilroberta-base | str with mask token | list of dict with `token_str`, `score` |
| `zero-shot-classification` | `ZeroShotClassificationPipeline` | bart-large-mnli | str + candidate labels | dict with `labels`, `scores` |
| `feature-extraction` | `FeatureExtractionPipeline` | distilbert-base-cased | str | tensor of embeddings |
| `table-question-answering` | `TableQuestionAnsweringPipeline` | tapas-base-finetuned-wtq | table + question | dict with answer |
| `question-answering` | `QuestionAnsweringPipeline` | distilbert-base-cased-distilled-squad | context + question | dict with `answer`, `score` |

**Aliases:** `sentiment-analysis` → `text-classification`, `ner` → `token-classification`, `text2text-generation` → `text-generation`.

### Vision Tasks

| Task | Pipeline Class | Default Model | Input | Output |
|------|---------------|---------------|-------|--------|
| `image-classification` | `ImageClassificationPipeline` | dinov2-small-imagenet1k | image path/PIL/URL | list of dict with `label`, `score` |
| `zero-shot-image-classification` | `ZeroShotImageClassificationPipeline` | clip-vit-base-patch32 | image + candidate labels | list of dict with `label`, `score` |
| `image-segmentation` | `ImageSegmentationPipeline` | various | image | list of dict with `label`, `mask` |
| `image-feature-extraction` | `ImageFeatureExtractionPipeline` | various | image | tensor of embeddings |
| `object-detection` | `ObjectDetectionPipeline` | various | image | list of dict with `box`, `label`, `score` |
| `zero-shot-object-detection` | `ZeroShotObjectDetectionPipeline` | owlvit-base-patch32 | image + labels | list of dict with `box`, `label`, `score` |
| `depth-estimation` | `DepthEstimationPipeline` | various | image | dict with `predicted_depth`, `depth` |
| `mask-generation` | `MaskGenerationPipeline` | sam-vit-huge | image | list of masks |
| `keypoint-matching` | `KeypointMatchingPipeline` | various | two images | keypoints + matches |

### Audio Tasks

| Task | Pipeline Class | Default Model | Input | Output |
|------|---------------|---------------|-------|--------|
| `automatic-speech-recognition` | `AutomaticSpeechRecognitionPipeline` | whisper-large-v3 | audio path/URL/array | dict with `text` |
| `audio-classification` | `AudioClassificationPipeline` | superb/wav2vec2-base-superb-ks | audio path/URL/array | list of dict with `label`, `score` |
| `zero-shot-audio-classification` | `ZeroShotAudioClassificationPipeline` | clap-htsat-fused | audio + candidate labels | list of dict with `label`, `score` |
| `text-to-audio` | `TextToAudioPipeline` | suno/bark-small | str | audio array |
| `audio-frame-classification` | `AudioFrameClassificationPipeline` | various | audio | frames with labels |

**Alias:** `text-to-speech` → `text-to-audio`.

### Multimodal Tasks

| Task | Pipeline Class | Default Model | Input | Output |
|------|---------------|---------------|-------|--------|
| `document-question-answering` | `DocumentQuestionAnsweringPipeline` | layoutlm-document-qa | image + question | dict with answer |
| `image-text-to-text` | `ImageTextToTextPipeline` | various | image + text | generated text |
| `any-to-any` | `AnyToAnyPipeline` | various | mixed modalities | mixed outputs |

### Video Tasks

| Task | Pipeline Class | Default Model | Input | Output |
|------|---------------|---------------|-------|--------|
| `video-classification` | `VideoClassificationPipeline` | various | video path/array | list of dict with `label`, `score` |

## Chat / Conversational Usage

```python
from transformers import pipeline

gen = pipeline("text-generation", model="Qwen/Qwen2.5-1.5B-Instruct")

# Chat format (list of message dicts)
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"},
]
result = gen(messages, max_new_tokens=128)
print(result[0]["generated_text"])  # Full conversation including response
```

## Batch Processing

```python
from transformers import pipeline

classifier = pipeline("sentiment-analysis")

# Batch of texts
results = classifier([
    "I love this product!",
    "This is terrible.",
    "It's okay, nothing special.",
])
# List of lists (one per input)
```

## Custom Pipeline

```python
from transformers import Pipeline

class CustomPipeline(Pipeline):
    def _sanitize_parameters(self, **kwargs):
        # Extract and validate parameters
        return {}, {}, {"custom_param": kwargs.get("custom_param", None)}

    def preprocess(self, inputs, custom_param=None):
        # Preprocess inputs
        return {"input_ids": inputs["input_ids"]}

    def _forward(self, input_tensors, custom_param=None):
        # Forward pass
        outputs = self.model(**input_tensors)
        return outputs.logits

    def postprocess(self, model_outputs, custom_param=None):
        # Postprocess outputs
        return [{"label": "custom", "score": 0.9}]

# Register the pipeline
from transformers import PIPELINE_REGISTRY
PIPELINE_REGISTRY.register_pipeline(
    "custom-task",
    pipeline_class=CustomPipeline,
    pt_model=("AutoModelForCustomTask",),
)
```

## Pipeline with Custom Model Instance

```python
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

# Load model separately
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-1.5B")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B")

# Pass to pipeline
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=0,
)
```

## Pipeline Return Types

```python
# Text generation returns list of dicts
gen = pipeline("text-generation")
result = gen("Hello")
# [{'generated_text': 'Hello, how can I help you?'}]

# Text classification returns list of dicts
cls = pipeline("text-classification")
result = cls("I love this!")
# [{'label': 'POSITIVE', 'score': 0.9998}]

# Token classification returns list of dicts
ner = pipeline("ner", aggregation_strategy="simple")
result = ner("Hugging Face is in New York.")
# [{'entity_group': 'ORG', 'score': 0.99, 'word': 'Hugging Face', ...}]

# Feature extraction returns tensor
feat = pipeline("feature-extraction")
result = feat("Hello world")
# tensor of shape (batch, sequence, hidden_dim)
```

## Pipeline Device Management

```python
# Specific GPU
pipe = pipeline("text-generation", model="Qwen/Qwen2.5-1.5B", device=0)

# Auto device map
pipe = pipeline("text-generation", model="Qwen/Qwen2.5-1.5B", device_map="auto")

# CPU
pipe = pipeline("text-generation", model="Qwen/Qwen2.5.1-1.5B", device=-1)
```

## Getting Supported Tasks

```python
from transformers import get_supported_tasks

tasks = get_supported_tasks()
print(tasks)
# ['text-generation', 'text-classification', 'ner', ...]
```
