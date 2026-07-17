# Training Reference

## Trainer

Main class for PyTorch training. Handles training loop, evaluation, logging, checkpointing, and Hub push.

### Signature

```python
from transformers import Trainer

trainer = Trainer(
    model=None,                        # PreTrainedModel or nn.Module
    args=None,                         # TrainingArguments
    data_collator=None,                # DataCollator callable
    train_dataset=None,                # Dataset or IterableDataset
    eval_dataset=None,                 # Dataset or dict of Datasets
    tokenizer=None,                    # PreTrainedTokenizerBase (for nb training steps)
    model_init=None,                   # Callable -> model (for hyperparameter search)
    compute_metrics=None,              # Callable(EvalPrediction) -> dict
    callbacks=None,                    # list of TrainerCallback
    optimizers=(None, None),           # (optimizer, lr_scheduler) tuple
    preprocess_logits_for_metrics=None, # Callable for metric computation
    wrapped_model=False,               # bool: already wrapped model
)
```

### Basic Training

```python
from transformers import Trainer, TrainingArguments, AutoModelForSequenceClassification, AutoTokenizer
from datasets import load_dataset

model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

dataset = load_dataset("imdb")

def tokenize(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128)

tokenized = dataset.map(tokenize, batched=True)
tokenized = tokenized.rename_column("label", "labels")  # Trainer expects "labels"

args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_steps=50,
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized["train"],
    eval_dataset=tokenized["test"],
    tokenizer=tokenizer,
)

trainer.train()
trainer.evaluate()
trainer.predict(tokenized["test"])
```

### Custom Metrics

```python
import numpy as np
from sklearn.metrics import accuracy_score, f1_score

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(labels, predictions),
        "f1": f1_score(labels, predictions, average="weighted"),
    }

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    compute_metrics=compute_metrics,
)
```

### Custom Loss

```python
from transformers import Trainer

class CustomTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits

        # Custom loss
        loss_fct = nn.CrossEntropyLoss(label_smoothing=0.1)
        loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))

        return (loss, outputs) if return_outputs else loss
```

## TrainingArguments

Dataclass controlling all training hyperparameters and behavior.

### Key Parameters

#### Output & Logging
| Parameter | Default | Description |
|-----------|---------|-------------|
| `output_dir` | `./outputs` | Directory for checkpoints and logs |
| `logging_dir` | `None` | TensorBoard log directory |
| `logging_steps` | `500` | Log every N steps |
| `logging_strategy` | `"steps"` | `"steps"`, `"epoch"`, `"no"` |
| `report_to` | `"all"` | List of integrations: `"tensorboard"`, `"wandb"`, `"comet_ml"`, `"azure_ml"` |

#### Batch Size & Epochs
| Parameter | Default | Description |
|-----------|---------|-------------|
| `per_device_train_batch_size` | `8` | Batch size per device for training |
| `per_device_eval_batch_size` | `8` | Batch size per device for evaluation |
| `gradient_accumulation_steps` | `1` | Accumulate gradients over N steps |
| `num_train_epochs` | `3.0` | Number of training epochs |
| `max_steps` | `-1` | Override epochs with fixed step count |

#### Learning Rate
| Parameter | Default | Description |
|-----------|---------|-------------|
| `learning_rate` | `2e-5` | Base learning rate |
| `weight_decay` | `0.0` | Weight decay |
| `adam_beta1` | `0.9` | Adam beta1 |
| `adam_beta2` | `0.999` | Adam beta2 |
| `adam_epsilon` | `1e-8` | Adam epsilon |
| `max_grad_norm` | `1.0` | Gradient clipping norm |
| `lr_scheduler_type` | `"linear"` | Scheduler: `"linear"`, `"cosine"`, `"constant"`, etc. |
| `lr_scheduler_kwargs` | `{}` | Extra scheduler kwargs |
| `warmup_ratio` | `0.0` | Fraction of steps for warmup |
| `warmup_steps` | `0` | Fixed number of warmup steps |

#### Evaluation & Saving
| Parameter | Default | Description |
|-----------|---------|-------------|
| `evaluation_strategy` | `"no"` | `"steps"`, `"epoch"`, `"no"` |
| `eval_steps` | `500` | Evaluate every N steps |
| `save_strategy` | `"steps"` | `"steps"`, `"epoch"`, `"no"` |
| `save_steps` | `500` | Save every N steps |
| `save_total_limit` | `None` | Max number of checkpoints to keep |
| `load_best_model_at_end` | `False` | Load best checkpoint after training |
| `metric_for_best_model` | `None` | Metric to track for best model |
| `greater_is_better` | `None` | Whether higher metric is better |

#### Optimization
| Parameter | Default | Description |
|-----------|---------|-------------|
| `fp16` | `False` | Mixed precision (FP16) |
| `bf16` | `False` | Mixed precision (BF16) |
| `tf32` | `None` | Enable TF32 on Ampere+ |
| `gradient_checkpointing` | `False` | Trade speed for memory |
| `gradient_checkpointing_kwargs` | `{}` | Extra gradient checkpointing kwargs |
| `dataloader_num_workers` | `0` | DataLoader workers |
| `dataloader_pin_memory` | `True` | Pin memory for DataLoader |
| `dataloader_prefetch_factor` | `2` | Prefetch factor |

#### Distributed Training
| Parameter | Default | Description |
|-----------|---------|-------------|
| `ddp_find_unused_parameters` | `None` | Find unused params in DDP |
| `deepspeed` | `None` | DeepSpeed config file path |
| `fsdp` | `""` | FSDP: `"full_shard"`, `"shard_grad_op"`, `"no_shard"` |
| `fsdp_config` | `{}` | FSDP config dict |
| `fsdp_min_num_params` | `0` | Min params for FSDP wrapping |
| `fsdp_transformer_layer_cls_to_wrap` | `None` | Layer classes to wrap |

#### Hub Integration
| Parameter | Default | Description |
|-----------|---------|-------------|
| `push_to_hub` | `False` | Push to Hub |
| `hub_model_id` | `None` | Hub model ID |
| `hub_strategy` | `None` | `"every_save"`, `"all_checkpoints"`, `"end_only"` |
| `hub_token` | `None` | Hub auth token |
| `hub_private_repo` | `True` | Private repo |

#### Other
| Parameter | Default | Description |
|-----------|---------|-------------|
| `seed` | `42` | Random seed |
| `data_seed` | `None` | Data-specific seed |
| `report_to` | `"all"` | Logging integrations |
| `disable_tqdm` | `None` | Disable progress bars |
| `include_num_input_tokens_seen` | `True` | Track input tokens |
| `include_tokens_per_second` | `False` | Track tokens/sec |
| `include_nospin` | `False` | No-spin optimization |

## Seq2SeqTrainer

Specialized Trainer for encoder-decoder models (T5, BART, etc.).

```python
from transformers import Seq2SeqTrainer, Seq2SeqTrainingArguments

args = Seq2SeqTrainingArguments(
    output_dir="./results",
    predict_with_generate=True,       # Use generate() for prediction
    generation_max_length=64,          # Max length for generation
    # All TrainingArguments params also available
)

trainer = Seq2SeqTrainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    data_collator=data_collator,
    tokenizer=tokenizer,
)
```

## Data Collators

### `DataCollatorWithPadding`

```python
from transformers import DataCollatorWithPadding

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
# Pads batches to the longest sequence in each batch
```

### `DataCollatorForLanguageModeling`

For causal/MLM pretraining:

```python
from transformers import DataCollatorForLanguageModeling

# Causal LM
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
)

# Masked LM
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=True,
    mlm_probability=0.15,
)
```

### `DataCollatorForSeq2Seq`

For encoder-decoder models:

```python
from transformers import DataCollatorForSeq2Seq

data_collator = DataCollatorForSeq2Seq(
    tokenizer=tokenizer,
    label_pad_token_id=-100,  # Ignore padding in loss
)
```

### `default_data_collator`

Default collator that handles most cases:

```python
from transformers import default_data_collator

# Automatic batching with padding
```

## Callbacks

### Built-in Callbacks

| Callback | Purpose |
|----------|---------|
| `TrainerCallback` | Base class |
| `SaveCallback` | Handle saving |
| `IRCallback` | Handle Intel Extension for PyTorch |
| `ProdOrAvgPastGradientCallback` | Prod/avg past gradient |
| `LoggingCallback` | Handle logging |
| `EvaluationCallback` | Handle evaluation |
| `CheckpointCallback` | Handle checkpointing |
| `PrinterCallback` | Print to console |
| `ProgressCallback` | Progress bar |
| `HubCallback` | Hub push |

### Custom Callback

```python
from transformers import TrainerCallback, TrainerControl, TrainerState

class MyCallback(TrainerCallback):
    def on_epoch_end(self, args, state: TrainerState, control: TrainerControl, **kwargs):
        print(f"Epoch {state.epoch} completed, loss: {state.log_history[-1].get('loss')}")
        return control

    def on_evaluate(self, args, state: TrainerState, control: TrainerControl, metrics, **kwargs):
        print(f"Evaluation metrics: {metrics}")
        return control

trainer.add_callback(MyCallback())
```

## Hyperparameter Search

```python
from transformers import Trainer

def model_init():
    return AutoModelForSequenceClassification.from_pretrained(
        "bert-base-uncased", num_labels=2
    )

def hp_space(trial):
    return {
        "learning_rate": trial.suggest_float("learning_rate", 1e-5, 1e-4),
        "per_device_train_batch_size": trial.suggest_int("per_device_train_batch_size", 8, 32),
        "num_train_epochs": trial.suggest_int("num_train_epochs", 1, 5),
    }

trainer = Trainer(
    model=model_init(),
    args=args,
    model_init=model_init,
)

best = trainer.hyperparameter_search(
    direction="maximize",
    backend="optuna",  # or "ray"
    hp_space=hp_space,
    n_trials=20,
)
```

## Evaluation

```python
# Evaluate on eval_dataset
metrics = trainer.evaluate()

# Evaluate on specific dataset
metrics = trainer.evaluate(eval_dataset=custom_dataset)

# Predict
predictions = trainer.predict(test_dataset)
# predictions.predictions — raw model outputs
# predictions.label_ids — true labels
# predictions.metrics — evaluation metrics
```

## Checkpointing

```python
# Save checkpoint
trainer.save_checkpoint("./checkpoint-dir")

# Resume from checkpoint
trainer.train(resume_from_checkpoint=True)
# Or specific checkpoint
trainer.train(resume_from_checkpoint="./checkpoint-1000")

# Save final model
trainer.save_model("./final-model")
```

## Push to Hub

```python
# Via TrainingArguments
args = TrainingArguments(
    output_dir="./results",
    push_to_hub=True,
    hub_model_id="my-username/my-model",
    hub_token="hf_...",
)

# Or manually
trainer.push_to_hub("My model is ready!")
```
