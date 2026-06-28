# Auto Classes Reference

Auto classes resolve the correct model/tokenizer/config class from a model ID on the Hub or a local config file. They inspect `config.json` to determine the architecture.

## Configuration Auto

### `AutoConfig`
Base class for all configuration objects. Resolves config from model ID or path.

```python
from transformers import AutoConfig

config = AutoConfig.from_pretrained("meta-llama/Llama-3.1-8B")
print(config.model_type)          # "llama"
print(config.architectures)       # ["LlamaForCausalLM"]
print(config.hidden_size)         # 4096
print(config.num_attention_heads) # 32
```

**Key config attributes:**
- `model_type` — string identifier (e.g., `"llama"`, `"gemma2"`)
- `architectures` — list of model class names
- `hidden_size` — model dimension
- `num_hidden_layers` — depth
- `num_attention_heads` / `num_key_value_heads` — attention heads (GQA if different)
- `vocab_size` — vocabulary size
- `max_position_embeddings` — max sequence length
- `rms_norm_eps` / `layer_norm_eps` — normalization epsilon
- `rope_theta` — RoPE base frequency (if applicable)

### `PretrainedConfig` / `PreTrainedConfig`
Alias for `PretrainedConfig`. Both names are exported. All model configs inherit from this.

```python
from transformers import PreTrainedConfig

# Save/load config
config.save_pretrained("./my-config")
config = PreTrainedConfig.from_pretrained("./my-config")
```

## Model Auto Classes

### Base
| Class | Task |
|-------|------|
| `AutoModel` | Base model (no head), feature extraction |
| `AutoModelForPreTraining` | Original pretraining objective (MLM, next sentence, etc.) |

### Text (Language Models)
| Class | Task |
|-------|------|
| `AutoModelForCausalLM` | Text generation (decoder-only: Llama, GPT, Gemma) |
| `AutoModelForMaskedLM` | Fill-mask (encoder: BERT, RoBERTa) |
| `AutoModelForSeq2SeqLM` | Sequence-to-sequence (T5, BART, PEGASUS) |
| `AutoModelForMultimodalLM` | Multimodal language models (vision + text) |

### Text Classification & Understanding
| Class | Task |
|-------|------|
| `AutoModelForSequenceClassification` | Text classification, sentiment analysis |
| `AutoModelForQuestionAnswering` | Extractive QA (SQuAD-style) |
| `AutoModelForTokenClassification` | NER, POS tagging, chunking |
| `AutoModelForMultipleChoice` | Multiple choice (SWAG, HellaSwag) |
| `AutoModelForNextSentencePrediction` | Next sentence prediction |
| `AutoModelForTableQuestionAnswering` | Table QA (TAPAS) |

### Vision
| Class | Task |
|-------|------|
| `AutoModelForImageClassification` | Image classification |
| `AutoModelForZeroShotImageClassification` | Zero-shot image classification (CLIP) |
| `AutoModelForImageSegmentation` | Image segmentation |
| `AutoModelForSemanticSegmentation` | Semantic segmentation |
| `AutoModelForUniversalSegmentation` | Universal segmentation |
| `AutoModelForInstanceSegmentation` | Instance segmentation |
| `AutoModelForObjectDetection` | Object detection (DETR, YOLO) |
| `AutoModelForZeroShotObjectDetection` | Zero-shot object detection (OWL-ViT) |
| `AutoModelForDepthEstimation` | Depth estimation |
| `AutoModelForMaskGeneration` | Mask generation (SAM) |
| `AutoModelForKeypointMatching` | Keypoint matching |
| `AutoModelForImageToImage` | Image-to-image translation |

### Vision-Language
| Class | Task |
|-------|------|
| `AutoModelForVisualQuestionAnswering` | Visual QA |
| `AutoModelForDocumentQuestionAnswering` | Document QA (LayoutLM) |
| `AutoModelForImageTextToText` | Image-to-text (BLIP, Flamingo) |
| `AutoModelForTextRecognition` | Text recognition (OCR) |
| `AutoModelForTableRecognition` | Table recognition |

### Audio
| Class | Task |
|-------|------|
| `AutoModelForAudioClassification` | Audio classification |
| `AutoModelForCTC` | CTC-based ASR (wav2vec2, HuBERT) |
| `AutoModelForSpeechSeq2Seq` | Seq2Seq ASR (Whisper) |
| `AutoModelForTDT` | Transducer-based ASR |
| `AutoModelForAudioFrameClassification` | Audio frame classification |
| `AutoModelForAudioXVector` | Speaker verification |

### Video
| Class | Task |
|-------|------|
| `AutoModelForVideoClassification` | Video classification |
| `AutoModelForTextToVideo` | Text-to-video generation |

### Specialized
| Class | Task |
|-------|------|
| `AutoModelForTextToWaveform` | Direct text-to-waveform synthesis |
| `AutoModelForTextToSpectrogram` | Text-to-spectrogram synthesis |
| `AutoModelForTextEncoding` | Text encoding (embeddings) |
| `AutoModelForTimeSeriesPrediction` | Time series forecasting |

## Tokenizer Auto

### `AutoTokenizer`
Resolves the correct tokenizer class from config.

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B")
encoded = tokenizer("Hello, world!", return_tensors="pt")
print(encoded.keys())  # dict_keys(['input_ids', 'attention_mask'])
```

**Key tokenizer attributes:**
- `tokenizer.model_max_length` — maximum sequence length
- `tokenizer.pad_token` / `tokenizer.eos_token` / `tokenizer.bos_token` — special tokens
- `tokenizer.padding_side` — `"right"` (default) or `"left"`
- `tokenizer.chat_template` — Jinja template for chat formatting (may be `None`)

### `AutoTokenizer` from config
```python
# From a local directory
tokenizer = AutoTokenizer.from_pretrained("./my-model-dir")

# With specific revision
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased", revision="main")
```

## Processor Auto

### `AutoProcessor`
Combines tokenizer + image/audio processor for multimodal models.

```python
from transformers import AutoProcessor

# Vision-language model
processor = AutoProcessor.from_pretrained("llava-hf/llava-1.5-7b-hf")

# Process text + image
from PIL import Image
image = Image.open("photo.jpg")
inputs = processor(text="Describe this image.", images=image, return_tensors="pt")
```

### `AutoFeatureExtractor`
Audio feature extraction (mel spectrograms, etc.).

```python
from transformers import AutoFeatureExtractor

extractor = AutoFeatureExtractor.from_pretrained("facebook/wav2vec2-base-960h")
inputs = extractor(audio, sampling_rate=16000, return_tensors="pt")
```

### `AutoImageProcessor`
Standalone image processing (normalization, resizing).

```python
from transformers import AutoImageProcessor

processor = AutoImageProcessor.from_pretrained("google/vit-base-patch16-224")
inputs = processor(image, return_tensors="pt")
```

### `AutoVideoProcessor`
Video frame processing.

```python
from transformers import AutoVideoProcessor

processor = AutoVideoProcessor.from_pretrained("facebook/xclip-base-patch32")
```

## Model Mapping

The auto classes use internal mapping dictionaries:
- `MODEL_FOR_CAUSAL_LM_MAPPING` — maps config types to causal LM classes
- `TOKENIZER_MAPPING` — maps config types to tokenizer classes
- `PROCESSOR_MAPPING` — maps config types to processor classes
- `FEATURE_EXTRACTOR_MAPPING` — maps config types to feature extractor classes
- `IMAGE_PROCESSOR_MAPPING` — maps config types to image processor classes

You can inspect these mappings:
```python
from transformers.models.auto import modeling_auto, tokenization_auto

# Check if a model type is supported
from transformers import AutoConfig
config = AutoConfig.from_pretrained("some-model")
print(config.model_type in modeling_auto.MODEL_FOR_CAUSAL_LM_MAPPING)
```

## Custom Model Registration

Register a new model type with the auto classes:

```python
from transformers import AutoConfig, AutoModel, AutoModelForCausalLM

# Register with AutoConfig
AutoConfig.register("my_custom_config_class", MyCustomModel)

# Register with AutoModel
AutoModel.register(MyCustomConfig, MyCustomModel)

# Register with AutoModelForCausalLM
AutoModelForCausalLM.register(MyCustomConfig, MyCustomModelForCausalLM)
```

## Resolution Order

Auto classes resolve in this order:
1. If `pretrained_model_name_or_path` is a string, download/fetch `config.json` from Hub or local path
2. Parse `model_type` from config
3. Look up the appropriate class in the mapping dictionary
4. Instantiate the resolved class

If resolution fails, check:
- The model ID exists and is accessible
- `model_type` is registered in the auto mappings
- For custom models, use `trust_remote_code=True` or register manually
