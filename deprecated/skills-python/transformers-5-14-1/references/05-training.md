# Training

The `Trainer` class provides a feature-complete training and evaluation loop optimized for Transformers models. It handles device placement, mixed precision, gradient accumulation, logging, and checkpointing.

## Basic Training

```python
from transformers import Trainer, TrainingArguments
from datasets import Dataset

# Define training arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    learning_rate=2e-5,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=50,
    save_steps=500,
    evaluation_strategy="steps",
    eval_steps=500,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
)

# Initialize trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    processing_class=tokenizer,
)

# Train
trainer.train()

# Evaluate
results = trainer.evaluate()

# Predict
predictions = trainer.predict(test_dataset)
```

## TrainingArguments

### Key Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `output_dir` | str | `./tmp_trainer` | Output directory for checkpoints/logs |
| `num_train_epochs` | float | 3.0 | Number of training epochs |
| `max_steps` | int | -1 | Override epochs with exact step count |
| `per_device_train_batch_size` | int | 8 | Batch size per device |
| `per_device_eval_batch_size` | int | 8 | Eval batch size per device |
| `gradient_accumulation_steps` | int | 1 | Accumulate grads before optimizer step |
| `learning_rate` | float | 5e-5 | Base learning rate |
| `weight_decay` | float | 0.0 | Weight decay (adamw decoupled) |
| `adam_beta1` | float | 0.9 | Adam beta1 |
| `adam_beta2` | float | 0.999 | Adam beta2 |
| `adam_epsilon` | float | 1e-8 | Adam epsilon |
| `max_grad_norm` | float | 1.0 | Gradient clipping norm |
| `warmup_steps` | int | 0 | Linear warmup steps |
| `warmup_ratio` | float | 0.0 | Warmup as fraction of total steps |
| `logging_steps` | int | 50 | Steps between log entries |
| `save_steps` | int | 500 | Steps between checkpoints |
| `save_total_limit` | int | None | Max checkpoints to keep |
| `evaluation_strategy` | str | "no" | "no", "steps", "epoch" |
| `eval_steps` | int | None | Steps between evals |
| `load_best_model_at_end` | bool | False | Restore best checkpoint after training |
| `metric_for_best_model` | str | None | Metric to track for best model |
| `greater_is_better` | bool | None | Whether higher metric is better |
| `fp16` | bool | False | FP16 mixed precision |
| `bf16` | bool | False | BF16 mixed precision |
| `gradient_checkpointing` | bool | False | Trade speed for memory |
| `dataloader_num_workers` | int | 0 | DataLoader workers |
| `remove_unused_columns` | bool | True | Drop columns not in forward() |
| `report_to` | str/list | "all" | Logging integrations |
| `seed` | int | 42 | Random seed |
| `dataseeds` | int | None | Dataset-specific seeds |
| `optim` | str | "adamw_torch" | Optimizer type |
| `lr_scheduler_type` | str | "linear" | LR scheduler |
| `gradient_accumulation_steps` | int | 1 | Grad accumulation |
| `max_steps` | int | -1 | Total training steps (overrides epochs) |

### Mixed Precision

```python
training_args = TrainingArguments(
    output_dir="./results",
    bf16=True,              # BF16 (Ampere+ GPUs)
    # fp16=True,           # FP16 (older GPUs)
    fp16_full_eval=True,    # Run eval in FP16
)
```

### Optimizer Selection

```python
training_args = TrainingArguments(
    output_dir="./results",
    optim="adamw_torch",          # Default PyTorch AdamW
    # optim="adamw_torch_fused",  # Fused AdamW (faster)
    # optim="adamw_apex_fused",   # Apex fused (requires apex)
    # optim="adafactor",          # Adafactor (memory efficient)
)

# Custom optimizer
def create_optimizer():
    return torch.optim.AdamW(model.parameters(), lr=2e-5)

trainer = Trainer(
    model=model,
    args=training_args,
    optimizers=(create_optimizer(), None),  # (optimizer, scheduler)
)
```

## DataCollator

```python
from transformers import DataCollatorWithPadding, DataCollatorForLanguageModeling

# Padding collator (for classification, QA, etc.)
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# Language modeling collator (MLM)
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=True,                  # Masked language modeling
    mlm_probability=0.15,
)

# Language modeling collator (causal)
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,                 # Causal language modeling
)

# Use with Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    data_collator=data_collator,
)
```

### Available DataCollators

| Collator | Use Case |
|---|---|
| `DataCollatorWithPadding` | Dynamic padding for variable-length sequences |
| `DataCollatorForLanguageModeling` | MLM or causal LM with automatic masking |
| `DataCollatorForTokenClassification` | NER with padding and label alignment |
| `DataCollatorForSeq2Seq` | Sequence-to-sequence (T5, BART) |
| `DataCollatorForWholeWordMask` | Whole-word masking for MLM |
| `DefaultDataCollator` | Default behavior (no padding) |

## Custom Training Loop

```python
# Override training_step for custom behavior
class CustomTrainer(Trainer):
    def training_step(self, model, inputs):
        model.train()
        inputs = self._prepare_inputs(inputs)

        outputs = model(**inputs)
        loss = outputs.loss

        # Custom loss or gradient computation
        loss = loss + self.custom_regularization(model)

        if self.args.n_gpu > 1:
            loss = loss.mean()

        if self.use_apex:
            with amp.scale_loss(loss, self.optimizer) as scaled_loss:
                scaled_loss.backward()
        else:
            self.accelerator.backward(loss)

        return loss.detach() / self.args.gradient_accumulation_steps
```

## Callbacks

```python
from transformers import TrainerCallback, TrainerControl, TrainerState

class MyCallback(TrainerCallback):
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs:
            print(f"Step {state.global_step}: loss={logs.get('loss', '?')}")

    def on_epoch_end(self, args, state, control, **kwargs):
        print(f"Epoch {state.epoch} completed")

    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        if metrics:
            print(f"Eval loss: {metrics.get('eval_loss')}")

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    callbacks=[MyCallback()],
)
```

### Built-in Callbacks

- `PrinterCallback` — prints logs
- `ProgressCallback` — tqdm progress bar
- `EarlyStoppingCallback` — early stopping based on metric
- `SaveCallback` — handles checkpoint saving
- `LogCallback` — base logging callback

```python
from transformers import EarlyStoppingCallback

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=3)],
)
```

## compute_metrics

```python
import numpy as np
from seqeval.metrics import classification_report

def compute_metrics(eval_pred):
    predictions, labels = eval_pred

    # For classification: argmax
    predictions = np.argmax(predictions, axis=1)

    # For NER: decode and compute metrics
    true_labels = [[labels[i][j] for j in range(len(labels[i])) if labels[i][j] != -100]
                   for i in range(len(labels))]
    true_predictions = [
        [label_list[p] for p, l in zip(prediction, label)
         if l != -100]
        for prediction, label in zip(predictions, true_labels)
    ]

    return classification_report(true_labels, true_predictions, output_dict=True)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    compute_metrics=compute_metrics,
)
```

## Gradient Checkpointing

```python
# Enable via model config
model.config.use_cache = False  # Required for gradient checkpointing
model.gradient_checkpointing_enable()

# Or via TrainingArguments
training_args = TrainingArguments(
    output_dir="./results",
    gradient_checkpointing=True,
)
```

## Hyperparameter Search

```python
from transformers import Trainer, TrainingArguments

def model_init(trial):
    learning_rate = trial.suggest_float("learning_rate", 1e-5, 1e-4, log=True)
    per_device_train_batch_size = trial.suggest_int("batch_size", 8, 32)
    model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)
    return model

training_args = TrainingArguments(
    output_dir="./results",
    learning_rate=2e-5,  # Will be overridden by model_init
    per_device_train_batch_size=16,  # Will be overridden
    evaluation_strategy="epoch",
    load_best_model_at_end=True,
    report_to="none",
)

trainer = Trainer(
    model_init=model_init,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    compute_metrics=compute_metrics,
)

# Run search
best_trial = trainer.hyperparameter_search(direction="max", n_trials=20)
print(best_trial)
```

## Saving and Loading Checkpoints

```python
# Save
trainer.save_model("./checkpoint")
tokenizer.save_pretrained("./checkpoint")

# Load
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model = AutoModelForSequenceClassification.from_pretrained("./checkpoint")
tokenizer = AutoTokenizer.from_pretrained("./checkpoint")

# Resume training from checkpoint
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)
trainer.train(resume_from_checkpoint=True)
```

## Push to Hub

```python
training_args = TrainingArguments(
    output_dir="./results",
    push_to_hub=True,
    hub_model_id="username/my-model",
    # hub_token="hf_...",  # Or use huggingface-cli login
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

trainer.train()
# Model is pushed to Hub automatically at each save
```

## Gotchas

- **`output_dir` is mandatory** — always set explicitly. Default `tmp_trainer` is lost on exit.
- **`per_device_train_batch_size` vs global** — actual global batch = `per_device × num_gpus × gradient_accumulation_steps`.
- **`remove_unused_columns=True`** — drops columns not in `forward()` signature. Set `False` for custom forward methods.
- **`gradient_checkpointing` requires `use_cache=False`** — the model's cache must be disabled.
- **`compute_metrics` receives numpy arrays** — not tensors. Use `np.argmax()` not `.argmax()`.
- **`-100` label ignore index** — CrossEntropyLoss ignores `-100`. DataCollators pad labels with `-100`, not the pad token ID.
- **`eval_dataset` as dict** — pass `{"test": test_ds, "valid": valid_ds}` for multiple eval sets. Metrics are prefixed with the key.
- **`logging_first_step=True`** — log the first step immediately. Useful for verifying setup.
- **`max_steps` overrides `num_train_epochs`** — if both are set, `max_steps` takes precedence.
- **`seed` affects everything** — data shuffling, weight init, dropout. Set for reproducibility.
- **`dataloader_drop_last`** — drop incomplete last batch. Set `True` for consistent batch sizes.
- **`evaluation_strategy="epoch"`** — evaluates once per epoch. `"steps"` evaluates every N steps.
- **`load_best_model_at_end` needs `evaluation_strategy`** — won't work with `"no"`.
- **`metric_for_best_model` must match `compute_metrics` output** — e.g., `"eval_accuracy"` if metrics return `{"accuracy": ...}`.
- **`Trainer` wraps the model** — after init, `trainer.model` may be DDP-wrapped. Use `trainer.model.module` to access the raw model.
- **`optimizers` tuple** — `(optimizer, scheduler)`. Pass `(None, None)` for defaults.
- **`create_optimizer` vs `optimizers`** — `optimizers` takes actual instances. `optim` string selects built-in types.
- **`push_to_hub` needs authentication** — call `huggingface-cli login` first or pass `hub_token`.
- **`resume_from_checkpoint`** — pass a checkpoint path string, or `True` to auto-detect latest.
- **`report_to`** — `"all"` enables all available integrations. Use `"none"` to disable, or `["wandb"]` for specific.
- **`bf16` requires Ampere+** — RTX 30xx+ or A100+. Use `fp16` for older GPUs.
- **`gradient_accumulation_steps` requires loss scaling** — Trainer handles this automatically. The loss is divided by accumulation steps before backward.
- **`eval_accumulation_steps`** — for large eval datasets, accumulate predictions in chunks to avoid OOM.
- **`predict_with_generate`** — set to `True` for seq2seq models to use `generate()` during prediction instead of `forward()`.
