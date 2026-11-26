# Auto-models

Auto-model classes resolve the correct architecture from a model ID on the Hub or a local config directory. They are the standard entry point for loading models without knowing the specific architecture.

## AutoModel Classes

### Base

```python
from transformers import AutoModel, AutoConfig

# Load base model (no task head)
model = AutoModel.from_pretrained("bert-base-uncased")
config = AutoConfig.from_pretrained("bert-base-uncased")
```

### Text (NLP)

```python
from transformers import (
    AutoModelForCausalLM,           # Text generation (GPT, Llama, Mistral)
    AutoModelForMaskedLM,           # Masked language modeling (BERT, RoBERTa)
    AutoModelForSeq2SeqLM,          # Sequence-to-sequence (T5, BART)
    AutoModelForSequenceClassification,  # Text classification
    AutoModelForQuestionAnswering,        # QA (extractive)
    AutoModelForTokenClassification,      # Token classification (NER)
    AutoModelForMultipleChoice,           # Multiple choice
    AutoModelForNextSentencePrediction,   # NSP
)

# Causal LM (generation)
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-1.5B")

# Sequence classification
model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased-finetuned-sst-2-english"
)

# Question answering
model = AutoModelForQuestionAnswering.from_pretrained(
    "distilbert-base-cased-distilled-squad"
)
```

### Vision

```python
from transformers import (
    AutoModelForImageClassification,
    AutoModelForObjectDetection,
    AutoModelForImageSegmentation,
    AutoModelForDepthEstimation,
    AutoModelForZeroShotImageClassification,
    AutoModelForSemanticSegmentation,
    AutoModelForInstanceSegmentation,
    AutoModelForObjectDetection,
    AutoModelForZeroShotObjectDetection,
)

# Image classification
model = AutoModelForImageClassification.from_pretrained("google/vit-base-patch16-224")

# Object detection
model = AutoModelForObjectDetection.from_pretrained("facebook/detr-resnet-50")
```

### Audio

```python
from transformers import (
    AutoModelForAudioClassification,
    AutoModelForAudioFrameClassification,
    AutoModelForAudioXVector,
    AutoModelForCTC,               # Speech recognition (Whisper, Wav2Vec2 CTC)
)

# ASR
model = AutoModelForCTC.from_pretrained("facebook/wav2vec2-base-960h")
```

### Multimodal

```python
from transformers import (
    AutoModelForVision2Seq,              # Image-to-text (BLIP, Flamingo)
    AutoModelForVisualQuestionAnswering, # VQA
    AutoModelForDocumentQuestionAnswering, # DocVQA
    AutoModelForImageTextToText,         # Multimodal text generation
)
```

## AutoTokenizer

```python
from transformers import AutoTokenizer

# Basic
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# With padding side
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased", padding_side="left")

# For generation models, left-padding is often preferred
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B", padding_side="left")
```

## AutoProcessor

For multimodal models that need both tokenization and image/audio processing:

```python
from transformers import AutoProcessor

# Vision-language model
processor = AutoProcessor.from_pretrained("llava-hf/llava-1.5-7b-hf")

# Use for both text and image inputs
inputs = processor(images=image, text="Describe this image.", return_tensors="pt")
```

## Auto Feature Extractor

```python
from transformers import AutoFeatureExtractor

# Audio models
feature_extractor = AutoFeatureExtractor.from_pretrained("facebook/wav2vec2-base-960h")
```

## Model Resolution

The auto classes resolve models using this priority:

1. **`config.json`** — reads the `architectures` field to determine model class
2. **`model_type`** — maps to registered model classes
3. **Auto model registry** — falls back to `AutoModel` if no specific task head is found

```python
from transformers import AutoConfig

# Inspect what a model resolves to
config = AutoConfig.from_pretrained("Qwen/Qwen2.5-1.5B")
print(config.model_type)        # "qwen2"
print(config.architectures)     # ["Qwen2ForCausalLM"]
```

## Custom Model Registration

Register a custom model with the auto classes:

```python
from transformers import AutoConfig, AutoModel, AutoModelForCausalLM

# Register config
AutoConfig.register("my_model_type", MyConfig)

# Register models
AutoModel.register(MyConfig, MyModel)
AutoModelForCausalLM.register(MyConfig, MyModelForCausalLM)

# Now AutoModel.from_pretrained() works with your model
model = AutoModel.from_pretrained("my-model-dir")
```

## Model Listing

See all registered model types:

```python
from transformers import MODEL_MAPPING

for model_type, model_class in MODEL_MAPPING.items():
    print(f"{model_type}: {model_class.__name__}")
```

## Gotchas

- **`AutoModel` loads without a task head** — use task-specific classes (e.g., `AutoModelForCausalLM`) for models with classification/generation heads.
- **`trust_remote_code=True`** — required for models with custom architecture code on the Hub. Only use for trusted models.
- **`revision` parameter** — load a specific commit or branch: `from_pretrained("model", revision="main")` or `revision="abc123"`.
- **`mirror` parameter** — for regions where huggingface.co is blocked, use `mirror="hf-mirror.com"`.
- **`local_files_only=True`** — load from cache without network access.
- **`config` parameter** — pass a pre-loaded config to override settings: `from_pretrained("model", config=custom_config)`.
- **`low_cpu_mem_usage=True`** — default in 5.x. Uses meta device for initial allocation, reducing peak memory. Disable for models that don't support it.
- **`device_map`** — for multi-GPU or CPU offloading. See [06-model-loading](06-model-loading.md).
- **`torch_dtype`** — specify dtype for loading. Use `torch_dtype="auto"` to match the config's `torch_dtype` (often `bfloat16` for modern models).
- **`variant` parameter** — load specific weight variants: `from_pretrained("model", variant="fp16")` loads `model.fp16.safetensors`.
- **Model type vs architecture** — `config.model_type` is the family (e.g., "llama"), `config.architectures` is the specific class (e.g., "LlamaForCausalLM"). Auto classes use both.
