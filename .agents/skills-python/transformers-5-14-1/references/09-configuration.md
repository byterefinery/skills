# Configuration

Model configurations define architecture hyperparameters. `PreTrainedConfig` is the base class for all model configs.

## Basic Usage

```python
from transformers import AutoConfig

# Load from Hub
config = AutoConfig.from_pretrained("bert-base-uncased")

# Inspect
print(config.model_type)        # "bert"
print(config.hidden_size)       # 768
print(config.num_hidden_layers) # 12
print(config.num_attention_heads) # 12

# Load with overrides
config = AutoConfig.from_pretrained(
    "bert-base-uncased",
    num_labels=3,
    hidden_dropout_prob=0.3,
)

# Create from scratch
from transformers import BertConfig

config = BertConfig(
    vocab_size=30522,
    hidden_size=768,
    num_hidden_layers=12,
    num_attention_heads=12,
    intermediate_size=3072,
)
```

## Config Properties

```python
config = AutoConfig.from_pretrained("Qwen/Qwen2.5-1.5B")

# Architecture
print(config.architectures)     # ["Qwen2ForCausalLM"]
print(config.model_type)        # "qwen2"
print(config.hidden_size)       # 1536
print(config.num_hidden_layers) # 28
print(config.num_attention_heads) # 12
print(config.intermediate_size) # 8960

# Tokenizer settings
print(config.vocab_size)        # 152064
print(config.bos_token_id)      # 151643
print(config.eos_token_id)      # 151645

# Training settings
print(config.hidden_dropout_prob)  # 0.0
print(config.layer_norm_eps)       # 1e-06

# Generation settings
print(config.max_position_embeddings)  # 32768
print(config.rope_theta)              # 1000000.0

# Dtype
print(config.torch_dtype)             # "bfloat16"
```

## Using Config with Models

```python
from transformers import AutoConfig, AutoModelForSequenceClassification

# Modify config before creating model
config = AutoConfig.from_pretrained("bert-base-uncased")
config.num_labels = 5
config.hidden_dropout_prob = 0.2

model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    config=config,
)

# Or inline overrides
model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=5,
    hidden_dropout_prob=0.2,
)
```

## Saving and Loading Configs

```python
# Save
config.save_pretrained("./my-config")

# Load
config = AutoConfig.from_pretrained("./my-config")

# From dict
config_dict = {
    "model_type": "bert",
    "hidden_size": 768,
    "num_hidden_layers": 12,
    "num_attention_heads": 12,
    "intermediate_size": 3072,
}
config = AutoConfig_for_model_type(**config_dict)
```

## Custom Config

```python
from transformers import PreTrainedConfig

class MyConfig(PreTrainedConfig):
    model_type = "my_model"

    def __init__(
        self,
        hidden_size=512,
        num_layers=6,
        num_heads=8,
        intermediate_size=2048,
        max_position_embeddings=512,
        vocab_size=30000,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.intermediate_size = intermediate_size
        self.max_position_embeddings = max_position_embeddings
        self.vocab_size = vocab_size

# Register with auto classes
from transformers import AutoConfig
AutoConfig.register("my_model", MyConfig)

# Use
config = MyConfig(hidden_size=768, num_layers=12)
config.save_pretrained("./my-model-config")
```

## Config Inheritance

```python
# Child configs inherit from parent
from transformers import BertConfig

# Base config
base_config = BertConfig()

# Derive with changes
child_config = BertConfig(
    **base_config.to_dict(),
    num_labels=3,
    hidden_dropout_prob=0.3,
)
```

## Inspecting Config

```python
# All attributes
print(config.to_dict())

# JSON
print(config.to_json_string())

# Diff between configs
config1 = AutoConfig.from_pretrained("bert-base-uncased")
config2 = AutoConfig.from_pretrained("bert-large-uncased")

diff = {k: (getattr(config1, k), getattr(config2, k))
        for k in set(config1.to_dict()) & set(config2.to_dict())
        if getattr(config1, k) != getattr(config2, k)}
```

## Common Config Attributes

| Attribute | Description |
|---|---|
| `hidden_size` | Dimension of hidden layers |
| `num_hidden_layers` | Number of transformer layers |
| `num_attention_heads` | Number of attention heads |
| `intermediate_size` | FFN hidden dimension |
| `hidden_act` | Activation function ("gelu", "relu", "silu") |
| `hidden_dropout_prob` | Dropout probability |
| `attention_probs_dropout_prob` | Attention dropout |
| `max_position_embeddings` | Max sequence length |
| `vocab_size` | Vocabulary size |
| `type_vocab_size` | Token type vocab size (for BERT) |
| `layer_norm_eps` | Layer norm epsilon |
| `initializer_range` | Truncated normal init std |
| `torch_dtype` | Recommended dtype ("float32", "bfloat16", "float16") |
| `tie_word_embeddings` | Share input/output embeddings |
| `use_cache` | Enable KV caching for generation |
| `pad_token_id` | Padding token ID |
| `bos_token_id` | Beginning-of-sequence token ID |
| `eos_token_id` | End-of-sequence token ID |

## Gotchas

- **`num_labels` must match task** — for classification, `num_labels` determines the output head size. Mismatch causes shape errors.
- **`torch_dtype` in config is informational** — it recommends a dtype but doesn't enforce it. Pass `torch_dtype` to `from_pretrained()` explicitly.
- **`is_encoder_decoder`** — set to `True` for seq2seq models (T5, BART). Affects how the model is constructed.
- **`tie_word_embeddings`** — when `True`, input and output embeddings share weights. Common in decoder-only models.
- **`use_cache` must be `False` for gradient checkpointing** — the cache prevents activation recomputation.
- **`config.to_dict()` vs `vars(config)`** — `to_dict()` returns a clean serializable dict. `vars()` includes internal attributes.
- **`AutoConfig` resolves model type** — it reads `config.json` from the Hub to determine the correct config class.
- **`revision` parameter** — load config from a specific revision: `from_pretrained("model", revision="v1.0")`.
- **`trust_remote_code` for custom configs** — models with custom config classes require `trust_remote_code=True`.
- **Config overrides in `from_pretrained()`** — keyword arguments override config values: `from_pretrained("model", num_labels=3)`.
- **`model.config` after loading** — the loaded model's config reflects the actual architecture, including any overrides applied during loading.
- **`config.update()`** — modify config in place: `config.update(num_labels=5)`.
- **`PostTrainingConfig`** — some models have separate training configs. Check for `post_training_config` attribute.
- **`rope_theta` for RoPE models** — controls the rotation frequency in rotary positional embeddings. Higher values extend context.
- **`sliding_window` for attention** — some models use sliding window attention. Check `sliding_window` attribute.
- **`multi_query_attention`/`grouped_query_attention`** — check for GQA/MQA variants which affect KV cache size.
