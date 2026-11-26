# Pipeline API (v5.24.1)

`pipeline()` is the high-level inference API: it loads the model and preprocessor, preprocesses input, runs inference, and postprocesses output.

## Basic usage

```python
from transformers import pipeline

# Task identifier + explicit model (default model is used when model is omitted)
pipe = pipeline(task="text-generation", model="google/gemma-2-2b")
pipe("the secret to baking a really good cake is ")
# [{'generated_text': 'the secret to baking a really good cake is 1. the right ingredients ...'}]

# Multiple inputs — pass a list
pipe(["the secret to baking a really good cake is ", "a baguette is "])
```

Task identifiers and their pipeline classes:

- **`any-to-any`** — AnyToAnyPipeline (any input modality)
- **`audio-classification`** — AudioClassificationPipeline
- **`automatic-speech-recognition`** — AutomaticSpeechRecognitionPipeline
- **`decision`** — DecisionPipeline
- **`depth-estimation`** — DepthEstimationPipeline
- **`document-question-answering`** — DocumentQuestionAnsweringPipeline
- **`feature-extraction`** — FeatureExtractionPipeline
- **`fill-mask`** — FillMaskPipeline
- **`image-classification`** — ImageClassificationPipeline
- **`image-feature-extraction`** — ImageFeatureExtractionPipeline
- **`image-segmentation`** — ImageSegmentationPipeline
- **`image-text-to-text`** — ImageTextToTextPipeline (vision-language chat models)
- **`keypoint-matching`** — KeypointMatchingPipeline
- **`mask-generation`** — MaskGenerationPipeline
- **`object-detection`** — ObjectDetectionPipeline
- **`table-question-answering`** — TableQuestionAnsweringPipeline
- **`text-classification`** (alias `sentiment-analysis`) — TextClassificationPipeline
- **`text-generation`** — TextGenerationPipeline
- **`text-to-audio`** (alias `text-to-speech`) — TextToAudioPipeline
- **`token-classification`** — TokenClassificationPipeline
- **`video-classification`** — VideoClassificationPipeline
- **`zero-shot-audio-classification`** — ZeroShotAudioClassificationPipeline
- **`zero-shot-classification`** — ZeroShotClassificationPipeline
- **`zero-shot-image-classification`** — ZeroShotImageClassificationPipeline
- **`zero-shot-object-detection`** — ZeroShotObjectDetectionPipeline

Removed in v5 (see 01-v5-migration): `question-answering`, `summarization`, `translation_*`, `text2text-generation`, `image-to-text`, `visual-question-answering`, `image-to-image`. Passing a removed task raises an error pointing at its replacement.

Programmatic access: `get_supported_tasks()` and `get_task(model)` (resolve a model's task from its config).

## Key parameters (from the `pipeline()` signature)

| Parameter | Notes |
|---|---|
| `task` | Task identifier (see list above) |
| `model` | Hub model ID or a loaded model instance |
| `config` | Hub config ID or PreTrainedConfig |
| `tokenizer` / `processor` / `image_processor` / `video_processor` / `feature_extractor` | Override the preprocessor resolution per kind |
| `revision` | Model revision to load |
| `token` | Hub token (v5 name; `use_auth_token` is deprecated) |
| `device` | First available accelerator by default (CUDA, Apple Silicon MPS, XPU, ...); CPU fallback only when none available. `device=0` for a specific CUDA id, `device="cpu"` to force CPU, `device="mps"` for Apple Silicon |
| `device_map` | e.g. `"auto"` — Accelerate big-model inference across devices (needs accelerate installed) |
| `dtype` | Defaults to `"auto"` — load weights in their stored dtype |
| `trust_remote_code` | Execute model-specific code from the Hub (security-sensitive) |
| `model_kwargs` | Extra kwargs for model loading |
| `pipeline_class` | Override pipeline class resolution |

## Batch inference

Batching is disabled by default (it is not always faster — hardware, data, and model all matter). Enable with `batch_size`:

```python
pipe = pipeline("text-generation", model="google/gemma-2-2b", batch_size=2)
pipe(["the secret to baking a really good cake is", "a baguette is", "paris is the", "hotdogs are"])
```

Streaming over a dataset (from `transformers.pipelines.pt_utils`):

```python
from transformers.pipelines.pt_utils import KeyDataset

pipe = pipeline("text-classification", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")
for out in pipe(KeyDataset(dataset, "text"), batch_size=8, truncation="only_first"):
    print(out)
```

## Task examples

```python
# Automatic speech recognition (audio URL or path)
pipe = pipeline("automatic-speech-recognition", model="openai/whisper-large-v3")
pipe("https://example.com/mlk.flac")
# {'text': ' I have a dream that one day this nation will rise up ...'}

# Image classification
pipe = pipeline("image-classification", model="google/vit-base-patch16-224")
pipe("https://example.com/cat.jpg")
# [{'label': 'lynx, catamount', 'score': 0.43}, ...]

# Vision-language chat — the image must be embedded in the message content list
pipe = pipeline("image-text-to-text", model="HuggingFaceTB/SmolVLM-256M-Instruct")
messages = [{
    "role": "user",
    "content": [
        {"type": "image", "image": "https://example.com/idefics-few-shot.jpg"},
        {"type": "text", "text": "What is in the image?"},
    ],
}]
pipe(messages, max_new_tokens=50, return_full_text=False)
```

For a text-generation pipeline on a chat model, pass a list of role/content dicts; the returned `generated_text` field holds the final assistant message.

## Device notes

- `pipeline()` auto-detects the first available accelerator; pass `device="cpu"` to force CPU.
- `device_map="auto"` (needs accelerate) loads/stores weights on the fastest device first, then offloads to CPU/disk for models larger than GPU memory.
- Half-precision weights are supported to save memory.
