# Pipeline API

The `pipeline()` function is the high-level inference API. It handles model loading, preprocessing, inference, and postprocessing in one call.

## Basic Usage

```python
from transformers import pipeline

# By task name (auto-resolves default model)
pipe = pipeline("text-classification")

# By task + model
pipe = pipeline("text-generation", model="Qwen/Qwen2.5-1.5B")

# Run inference
result = pipe("Hello, how are you?")
```

## Supported Tasks

### Text

| Task | Pipeline Name | Input | Output |
|---|---|---|---|
| Text generation | `text-generation` | string or chat list | list of dicts with `generated_text` |
| Text classification | `text-classification` | string or list | list of dicts with `label`, `score` |
| Token classification (NER) | `token-classification` | string or list | list of dicts with `word`, `entity`, `score` |
| Question answering | `question-answering` | `{"question": ..., "context": ...}` | dict with `answer`, `score`, `start`, `end` |
| Fill mask | `fill-mask` | string with `[MASK]` | list of dicts with `token_str`, `score` |
| Summarization | `summarization` | string | list of dicts with `summary_text` |
| Translation | `translation` | string | list of dicts with `translation_text` |
| Zero-shot classification | `zero-shot-classification` | string + candidate labels | dict with `sequence`, `labels`, `scores` |

### Vision

| Task | Pipeline Name | Input | Output |
|---|---|---|---|
| Image classification | `image-classification` | PIL Image or URL | list of dicts with `label`, `score` |
| Object detection | `object-detection` | PIL Image or URL | list of dicts with `label`, `score`, `box` |
| Image segmentation | `image-segmentation` | PIL Image or URL | list of dicts with `label`, `score`, `mask` |
| Depth estimation | `depth-estimation` | PIL Image or URL | dict with `predicted_depth`, `depth` |
| Zero-shot image classification | `zero-shot-image-classification` | PIL Image + labels | list of dicts with `label`, `score` |
| Image-to-image | `image-to-image` | PIL Image or URL | PIL Image |

### Audio

| Task | Pipeline Name | Input | Output |
|---|---|---|---|
| Speech recognition | `automatic-speech-recognition` | audio file path or numpy array | dict with `text`, `chunks` |
| Audio classification | `audio-classification` | audio file path or numpy array | list of dicts with `label`, `score` |

### Multimodal

| Task | Pipeline Name | Input | Output |
|---|---|---|---|
| Visual question answering | `visual-question-answering` | image + question | list of dicts with `answer`, `score` |
| Document question answering | `document-question-answering` | image + question | list of dicts with `answer`, `score`, `box` |
| Image text-to-text | `image-text-to-text` | image + prompt | list of dicts with `generated_text` |

## Batch Inference

```python
from transformers import pipeline

pipe = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

# Batch — pass a list
results = pipe([
    "This movie was amazing!",
    "Terrible experience, would not recommend.",
    "It was okay, nothing special.",
], batch_size=4)
```

## Device Placement

```python
import torch
from transformers import pipeline

# CPU
pipe = pipeline("text-generation", model="...", device="cpu")

# Specific GPU
pipe = pipeline("text-generation", model="...", device=0)

# Auto (first available GPU, falls back to CPU)
pipe = pipeline("text-generation", model="...", device="auto")

# Multiple GPUs (model parallelism via device_map)
pipe = pipeline(
    "text-generation",
    model="...",
    model_kwargs={"device_map": "auto"},
)
```

## dtype Control

```python
from transformers import pipeline
import torch

# Load in bfloat16
pipe = pipeline(
    "text-generation",
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Load in float16
pipe = pipeline(
    "text-generation",
    model="...",
    torch_dtype=torch.float16,
    device_map="auto",
)
```

## Generation Parameters

Pass generation kwargs directly to the pipeline call:

```python
pipe = pipeline("text-generation", model="Qwen/Qwen2.5-1.5B")

result = pipe(
    "Write a haiku about ",
    max_new_tokens=20,
    temperature=0.7,
    top_p=0.9,
    do_sample=True,
    repetition_penalty=1.1,
)
```

## Chat Pipelines

```python
from transformers import pipeline

pipe = pipeline("text-generation", model="meta-llama/Meta-Llama-3-8B-Instruct")

# Chat format — list of role/content dicts
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is transformers?"},
]

result = pipe(messages, max_new_tokens=128)
# result[0]["generated_text"] is the full chat history
```

## Custom Pipelines

For tasks not covered by built-in pipelines, use `CustomPipeline`:

```python
from transformers import pipeline, PreTrainedModel, PreTrainedTokenizer

class MyPipeline:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.model.eval()

    def __call__(self, inputs):
        encoded = self.tokenizer(inputs, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**encoded)
        return outputs.logits

pipe = pipeline(
    model=my_model,
    tokenizer=my_tokenizer,
    task="custom-task",
)
```

## Pipeline Internals

- `pipeline()` caches instances keyed by (task, model, device). Calling with same args returns the cached instance.
- Use `torch_dtype` parameter (not `model_kwargs={"torch_dtype": ...}`) for clean dtype specification.
- `truncation=True` is applied automatically when input exceeds model's max length.
- `padding=True` is applied automatically for batched inputs.
- For zero-shot tasks, the pipeline handles prompt templating internally.

## Gotchas

- **`pipeline()` is for inference only** — it calls `model.eval()` and wraps forward in `torch.no_grad()`. Do not use for training.
- **`return_tensors` is not a pipeline parameter** — pipelines return Python dicts/lists, not tensors. Use the model directly if you need tensor outputs.
- **`top_k` results** — for classification pipelines, use `top_k=5` to get top-5 predictions instead of just the best one.
- **`aggregation_strategy` for NER** — use `aggregation_strategy="simple"` or `"first"` to aggregate token-level predictions into entity spans.
- **`return_time=True`** — for speech recognition, set `return_time=True` to get word-level timestamps in the output.
- **`clean_up_tokenization_spaces`** — set to `False` if you need exact token boundaries. Default is `True` which merges spaces.
- **`pipeline` vs direct model** — `pipeline()` adds overhead for preprocessing/postprocessing. For tight loops, call the model directly with pre-tokenized inputs.
