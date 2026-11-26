# Training with Trainer (v5.24.1)

`Trainer` is a complete training and evaluation loop for PyTorch models. It handles batching, shuffling, padding, the forward/backward/update loop, evaluation, checkpointing, mixed precision, distributed training, and Hub integration. You provide a model, dataset, preprocessor, and data collator.

## Canonical fine-tuning flow

```python
from transformers import (
    AutoModelForSequenceClassification, AutoTokenizer, Trainer,
    TrainingArguments, DataCollatorWithPadding,
)
from datasets import load_dataset

model = AutoModelForSequenceClassification.from_pretrained("distilbert/distilbert-base-uncased")
tokenizer = AutoTokenizer.from_pretrained("distilbert/distilbert-base-uncased")
dataset = load_dataset("cornell-movie-review-data/rotten_tomatoes")

# Tokenize the whole dataset
dataset = dataset.map(lambda batch: tokenizer(batch["text"]), batched=True)

training_args = TrainingArguments(
    output_dir="distilbert-rotten-tomatoes",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=2,
    push_to_hub=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    processing_class=tokenizer,  # v5 name — `tokenizer=` was removed
    data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
)

trainer.train()
trainer.push_to_hub()  # uploads weights, generation config, tokenizer, and model config
```

## TrainingArguments — common arguments

- `output_dir` — set it explicitly (default creates a throwaway `tmp_trainer`)
- `num_train_epochs`, `per_device_train_batch_size`, `per_device_eval_batch_size`
- `learning_rate` — initial optimizer learning rate
- `bf16=True` — mixed precision on Ampere+ GPUs; `fp16=True` on older hardware
- `gradient_accumulation_steps` — simulates a larger effective batch (effective batch = `per_device_train_batch_size × num_gpus × gradient_accumulation_steps`)
- `warmup_step` — v5 replacement for the removed `warmup_ratio`; accepts a float ratio too
- `push_to_hub=True` + `hub_model_id` (v5 name; was `push_to_hub_model_id`/`push_to_hub_organization`) + `hub_token` (was `push_to_hub_token`)
- `use_cache` — Trainer sets `use_cache=False` in the model config by default (new v5 default); pass `use_cache=True` to keep KV-cache behavior
- `use_torch_compile` — replacement for removed `jit_mode_eval`
- `use_cpu` — replacement for removed `no_cuda`
- `fsdp_config` — replaces removed `fsdp_min_num_params` + `fsdp_transformer_layer_cls_to_wrap`
- `include_for_metrics` — replaces removed `include_inputs_for_metrics`

## v5 argument renames (quick map)

| v4 | v5 |
|---|---|
| `push_to_hub_token` | `hub_token` |
| `push_to_hub_model_id`, `push_to_hub_organization` | `hub_model_id` |
| `warmup_ratio` | `warmup_step` (float accepted) |
| `per_gpu_train_batch_size` | `per_device_train_batch_size` |
| `per_gpu_eval_batch_size` | `per_device_eval_batch_size` |
| `no_cuda` | `use_cpu` |
| `jit_mode_eval` | `use_torch_compile` |
| `tpu_metrics_debug` | `debug` |
| `include_inputs_for_metrics` | `include_for_metrics` |
| `include_tokens_per_second` | `include_num_input_tokens_seen` |
| `Trainer(tokenizer=...)` | `Trainer(processing_class=...)` |
| `Trainer.train(model_path=...)` | `resume_from_checkpoint` |

Removed entirely: `mp_parameters`, `_n_gpu`, `overwrite_output_dir`, `logging_dir` (use `TENSORBOARD_LOGGING_DIR` env var), `tpu_num_cores` (env var `TPU_NUM_CORES`), `past_index`, `ray_scope` (env var `RAY_SCOPE`), `use_mps_device` (MPS auto-detected), `fp16_backend`/`half_precision_backend` (torch.amp only), `use_legacy_prediction_loop`. Sigopt hyperparameter search integration is gone; minimum accelerate is 1.1.0.

## Customization

- **Subclassing Trainer methods** — override `compute_loss`, `evaluation_loop`, training steps, etc. (docs: `trainer_customize.md`)
- **Callbacks** — hook training events (docs: `trainer_callbacks.md`)
- **Data collators** — custom batch assembly (docs: `data_collators.md`); `DataCollatorWithPadding` requires the tokenizer to have a `pad_token`
- **Optimizers and schedulers** — custom optimizer/scheduler via `create_optimizer`/`create_scheduler` (docs: `optimizers.md`)
- **Hyperparameter search** — via integrations (optuna) — docs: `hpo_train.md`
- **Recipes** — `trainer_recipes.md`, `grad_accumulation.md`, `grad_checkpointing.md`, `mixed_precision_training.md`, `padding_free.md`

## PEFT integration (LoRA and friends)

v5 integrates PEFT directly through `PeftAdapterMixin` on all `PreTrainedModel` classes — no wrapping in `peft.PeftModel` needed (requires `peft >= 0.20.0`).

```python
from peft import LoraConfig, TaskType
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("google/gemma-2-2b")

lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    inference_mode=False,
    r=8,
    lora_alpha=32,
    lora_dropout=0.1,
)
model.add_adapter(lora_config, adapter_name="my_adapter")
```

- `modules_to_save=["lm_head"]` fully fine-tunes listed modules alongside the adapter
- `target_modules` — explicit list or regex when the architecture has no predefined targets (common architectures like Llama/Gemma/Qwen have defaults)
- Adapters can be added, switched, and deleted without re-wrapping the model
- Prompt-based PEFT methods (prompt tuning, prefix tuning) require the PEFT library directly

## Notes

- The repo no longer ships task fine-tuning example scripts — `examples/` in v5.24.1 contains only `generate` (continuous batching), `quantization` (custom quantization), and `scheduler` (greedy run). Follow the docs tutorials (`training.md`, `quicktour.md`) instead of old `examples/pytorch/...` scripts.
- Run a small test before a full job: check the model receives expected inputs, loss is finite, and evaluation completes (docs `training.md`).
- Knowledge distillation for LLMs has its own recipe (docs: `tasks/knowledge_distillation_for_image_classification.md` and the LLM distillation material under `training.md`).
