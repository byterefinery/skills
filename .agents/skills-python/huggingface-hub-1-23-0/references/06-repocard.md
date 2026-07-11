# RepoCard

Repo cards are README.md files with YAML frontmatter that describe models, datasets, and spaces on the Hub.

## ModelCard

```python
from huggingface_hub import ModelCard, ModelCardData

# Load from repo
card = ModelCard.load("bert-base-uncased")

# Create from scratch
card_data = ModelCardData(
    language=["en"],
    license="mit",
    library_name="pytorch_transformers",
    tags=["text-classification", "bert"],
    datasets=["glue", "squad"],
    metrics=["accuracy", "f1"],
    pipeline_tag="text-classification",
    model-index=[{
        "name": "bert-base-uncased",
        "results": [{
            "task": {"type": "text-classification", "name": "Text Classification"},
            "dataset": {"name": "GLUE", "type": "glue", "config": "sst2"},
            "metrics": [{"type": "accuracy", "value": 93.2}],
        }],
    }],
)
card = ModelCard(card_data, template=DEFAULT_MODEL_CARD_TEMPLATE)

# Save locally
card.save("README.md")

# Push to Hub
card.push_to_hub("username/my-model", token="hf_...")

# Access metadata
print(card.data.language)
print(card.data.license)
print(card.data.tags)
```

### ModelCardData fields

| Field | Type | Description |
|---|---|---|
| `language` | `str \| list[str]` | Language codes (e.g., `"en"`, `["en", "fr"]`) |
| `license` | `str \| list[str]` | SPDX license identifier(s) |
| `library_name` | `str` | Library name (e.g., `"pytorch_transformers"`) |
| `tags` | `list[str]` | Custom tags |
| `datasets` | `list[str]` | Training dataset names |
| `metrics` | `list[str]` | Evaluation metrics |
| `pipeline_tag` | `str` | Task pipeline tag |
| `model-index` | `list[dict]` | Model evaluation results |
| `widget` | `list[dict]` | Widget examples for the Hub UI |
| `inference` | `dict` | Inference parameters |
| `co2_eq_emissions` | `str` | Carbon emission estimate |
| `trainable_token_size` | `int` | Number of trainable tokens |
| `transformers_info` | `dict` | Transformers integration info |
| `dev_to_prod` | `dict` | Deployment info |
| `paperswithcode_id` | `str` | Papers With Code ID |
| `creators` | `list[str]` | Model creators |
| `end_users` | `list[str]` | Target end users |

## DatasetCard

```python
from huggingface_hub import DatasetCard, DatasetCardData

# Load
card = DatasetCard.load("glue")

# Create
card_data = DatasetCardData(
    language=["en"],
    license="mit",
    tags=["nlp", "glue"],
    task_categories=["text-classification"],
    task_ids:["sst2", "mrpc"],
    pretty_name="GLUE",
    size_categories=["1K<n<10K"],
    instance_id="glue/sst2",
)
card = DatasetCard(card_data)
card.save("README.md")
card.push_to_hub("username/my-dataset", repo_type="dataset", token="hf_...")
```

### DatasetCardData fields

| Field | Type | Description |
|---|---|---|
| `language` | `str \| list[str]` | Language codes |
| `language_alternative` | `str \| list[str]` | Alternative language codes |
| `license` | `str \| list[str]` | License |
| `tags` | `list[str]` | Tags |
| `task_categories` | `list[str]` | Task categories |
| `task_ids` | `list[str]` | Task IDs |
| `pretty_name` | `str` | Human-readable name |
| `size_categories` | `list[str]` | Size range categories |
| `instance_id` | `str` | Unique dataset identifier |
| `paperswithcode_id` | `str` | Papers With Code ID |
| `source` | `str` | Source URL |
| `train_size` | `int` | Training set size |
| `validation_size` | `int` | Validation set size |
| `test_size` | `int` | Test set size |

## SpaceCard

```python
from huggingface_hub import SpaceCard, SpaceCardData

card = SpaceCard.load("username/my-space")
card_data = SpaceCardData(
    title="My Space",
    sdk="gradio",
    app_port=7860,
    pinned=True,
)
card = SpaceCard(card_data)
card.save("README.md")
card.push_to_hub("username/my-space", repo_type="space", token="hf_...")
```

## RepoCard (base class)

```python
from huggingface_hub import RepoCard

# Load from string
card = RepoCard("---\nlicense: mit\n---\n# My Model\n")

# Load from file
card = RepoCard.load("README.md")

# Load from Hub
card = RepoCard.load("username/my-model", repo_type="model")

# Access raw content
content = str(card)

# Validate
card.validate(repo_type="model")

# Save
card.save("README.md")
```

## CardData

Generic metadata container (parent of ModelCardData, DatasetCardData, SpaceCardData).

```python
from huggingface_hub import CardData

data = CardData(
    license="mit",
    language="en",
    tags=["custom-tag"],
)
# Any key-value pair is stored; type validation is per subclass
```

## metadata_load / metadata_save / metadata_update

```python
from huggingface_hub import metadata_load, metadata_save, metadata_update

# Load metadata from a card file
data = metadata_load("README.md")

# Save metadata to a card file
metadata_save(data, "README.md")

# Update metadata on a Hub repo
metadata_update(
    repo_id="username/my-model",
    metadata={"tags": ["new-tag"]},
    repo_type="model",
    token="hf_...",
)
```

## Eval results

```python
from huggingface_hub import metadata_eval_result

# Create eval result entry
result = metadata_eval_result(
    task_type="text-classification",
    dataset_type="glue",
    dataset_name="GLUE",
    dataset_config="sst2",
    dataset_revision="...",
    metric_type="accuracy",
    metric_value=93.2,
    verified=False,
    verifies=["..."],
)

# Parse eval results from YAML
entries = parse_eval_result_entries("---\n...")

# Convert to YAML
yaml_str = eval_result_entries_to_yaml(entries)
```

## Model card templates

The library provides default templates for `ModelCard.from_template()` and `DatasetCard.from_template()`:

```python
# Model card from template
card = ModelCard.from_template(
    model_id="username/my-model",
    model_card_data=ModelCardData(
        language="en",
        license="mit",
        library_name="pytorch",
        tags=["text-classification"],
    ),
    model_description="A fine-tuned BERT model",
    datasets="glue",
    frameworks="pytorch",
    languages="en",
    inference=["text-classification"],
    integrations=[],
)

# Dataset card from template
card = DatasetCard.from_template(
    dataset_id="username/my-dataset",
    dataset_card_data=DatasetCardData(
        language="en",
        license="mit",
        pretty_name="My Dataset",
    ),
    dataset_description="A collection of text samples",
    paperswithcode_id="my-dataset",
)
```
