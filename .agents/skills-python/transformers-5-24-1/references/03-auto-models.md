# Auto-models (v5.24.1)

Auto classes resolve the correct architecture from a Hub model ID, local path, or config — no need to know the exact architecture class.

## The 48 Auto classes

From `docs/source/en/model_doc/auto.md` (v5.24.1):

**Text**
- `AutoModel` — base model (raw hidden states)
- `AutoModelForPreTraining`
- `AutoModelForCausalLM` — causal LMs (replaces removed `AutoModelWithLMHead`)
- `AutoModelForMaskedLM`
- `AutoModelForMaskGeneration`
- `AutoModelForSeq2SeqLM` — encoder-decoder
- `AutoModelForSequenceClassification`
- `AutoModelForMultipleChoice`
- `AutoModelForNextSentencePrediction`
- `AutoModelForTokenClassification`
- `AutoModelForQuestionAnswering`
- `AutoModelForTextEncoding` — text embeddings

**Vision**
- `AutoModelForDepthEstimation`
- `AutoModelForNormalEstimation`
- `AutoModelForPointmapEstimation`
- `AutoModelForImageMatting`
- `AutoModelForTextRecognition`
- `AutoModelForTableRecognition`
- `AutoModelForImageClassification`
- `AutoModelForVideoClassification`
- `AutoModelForPoseEstimation`
- `AutoModelForKeypointDetection`
- `AutoModelForKeypointMatching`
- `AutoModelForMaskedImageModeling`
- `AutoModelForObjectDetection`
- `AutoModelForImageSegmentation`
- `AutoModelForImageToImage`
- `AutoModelForSemanticSegmentation`
- `AutoModelForInstanceSegmentation`
- `AutoModelForUniversalSegmentation`
- `AutoModelForZeroShotImageClassification`
- `AutoModelForZeroShotObjectDetection`

**Audio**
- `AutoModelForAudioClassification`
- `AutoModelForAudioFrameClassification`
- `AutoModelForCTC`
- `AutoModelForTDT`
- `AutoModelForRNNT`
- `AutoModelForSpeechSeq2Seq`
- `AutoModelForAudioXVector`
- `AutoModelForTextToSpectrogram`
- `AutoModelForTextToWaveform`
- `AutoModelForAudioTokenization`

**Multimodal / other**
- `AutoModelForMultimodalLM`
- `AutoModelForTableQuestionAnswering`
- `AutoModelForDocumentQuestionAnswering`
- `AutoModelForVisualQuestionAnswering`
- `AutoModelForImageTextToText` — replaces removed `AutoModelForVision2Seq`
- `AutoModelForDecision`
- `AutoModelForTimeSeriesPrediction`

Also: `AutoTokenizer`, `AutoProcessor`, `AutoImageProcessor`, `AutoConfig`.

Removed in v5: `AutoModelWithLMHead`, `AutoModelForVision2Seq`.

## Choosing the right class

The base model returns raw hidden states; task heads convert them into results (e.g. `LlamaModel` vs `LlamaForCausalLM`). Pick the head matching the task:

```python
from transformers import AutoModelForCausalLM, AutoModelForSequenceClassification

# Generation
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
# Classification (head sized for the default 2 labels; override num_labels as needed)
model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert/distilbert-base-uncased", num_labels=3
)
```

## from_pretrained parameters (v5.24.1)

Verified signature pieces from `src/transformers/modeling_utils.py`:

| Parameter | Notes |
|---|---|
| `pretrained_model_name_or_path` | Hub ID or local directory |
| `config` | PreTrainedConfig or config kwargs dict |
| `cache_dir` | Download cache (defaults under `HF_HOME`) |
| `ignore_mismatched_sizes` | Load even when head sizes differ (e.g. changing `num_labels`) |
| `force_download` | Re-download even if cached |
| `local_files_only` | Don't touch the network |
| `token` | Hub auth token (v5 name) |
| `revision` | Branch/tag/commit — resolved once, and config, weights, generation config, and adapters all load from that exact revision |
| `use_safetensors` | Prefer safetensors (the default format) |
| `weights_only` | Safe weights-only loading |
| `fusion_config` | Weight fusion on load (dynamic weight loading) |
| `disable_mmap` | Disable mmap'd weight loading |
| `*model_args` | Everything else — `dtype`, `device_map`, `quantization_config`, `gguf_file`, `trust_remote_code`, etc. |

`dtype` defaults to `"auto"` (initialize weights in the dtype they are stored in — avoids a double float32 load). `torch_dtype` still works as a backward-compat alias. `low_cpu_mem_usage`, `mirror`, `_fast_init`, `from_tf`, `from_flax`, `offload_state_dict` are silently popped as deprecated.

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf", dtype="auto", device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
```

## AutoConfig

```python
from transformers import AutoConfig

config = AutoConfig.from_pretrained("HuggingFaceTB/SmolLM3-3B")
# Inspect attributes before loading weights
config.hidden_size
```

v5 config gotchas:
- Rotary embedding parameters live in `config.rope_parameters` (dict, possibly nested per layer type for Gemma3/ModernBert) — `config.rope_theta` may raise AttributeError.
- Qwen-VL family configs are nested — read `config.text_config.vocab_size`, not `config.vocab_size`.
- Non-generative models have no `generation_config`; `model.config.generation_config` raises AttributeError.
- `from_xxx_config` init helpers are gone; `AutoConfig` loads from local paths or Hub repos only (no URLs).

## Custom model classes

Custom architectures can be registered with Auto classes and used with `trust_remote_code=True` (executes code from the Hub — security-sensitive). When subclassing `PreTrainedModel`, weights are auto-initialized with the common scheme (`_init_weights`); override `_init_weights` with a no-op to opt out of auto-init for custom submodules.
