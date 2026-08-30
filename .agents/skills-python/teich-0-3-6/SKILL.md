---
name: teich-0-3-6
description: >
  Teich 0.3.6, agent data infrastructure that turns raw coding-agent traces
  (Codex, Pi, Claude Code, Hermes, Cursor, local sessions), chat datasets,
  local JSONL, and Hugging Face datasets into auditable SFT training data.
  Use when generating new agent traces with teich init or teich generate;
  extracting and anonymizing local agent sessions with teich extract;
  preparing data for a target tokenizer with prepare_data; applying
  response-only labels with mask_data in TRL SFTTrainer or Unsloth flows;
  normalizing traces to OpenAI-style messages and tools with load_traces or
  teich convert; configuring config.yaml, prompt files, and providers; or
  using the teich studio browser UI. Covers per-model chat-template
  contracts for Gemma 4, Granite 4.2, Qwen 3.6, and Qwen 3.8.
license: Apache-2.0
compatibility: >
  Python 3.10+. pip install teich or run without installing via uvx teich.
  Docker and a provider API key are needed only for agent-trace generation
  (codex, pi, claude-code, hermes); the chat provider, extract, convert, and
  prepare_data need neither. teich studio needs the teich[studio] extra.
metadata:
  tags:
    - python
    - ml
    - llm
    - sft
    - agent-traces
    - data-pipeline
---

# teich 0.3.6

Teich turns raw agent sessions, chat datasets, local JSONL, Hugging Face datasets, and in-memory `datasets.Dataset` objects into auditable SFT data. It keeps data structured — `messages`, `tools`, reasoning, metadata, provenance — until the last practical moment, renders through the target tokenizer's chat template, records typed supervision spans before tokenization, and applies response-only labels after trainer tokenization. It reports dropped, oversized, trimmed, malformed, and fully masked rows instead of silently losing them.

Use it as a trace generator, a dataset loader, a chat-template renderer, a masking layer, or the whole pipeline.

## Overview

| Part | What it does |
|---|---|
| `teich init` / `teich generate` | Runs agent CLIs (codex, pi, claude-code, hermes) in Docker, or an OpenAI-compatible chat API directly, to create new trace datasets |
| `teich extract` | Stages existing local sessions (claude, codex, cursor, pi, hermes) as an anonymized dataset, optionally uploaded to Hugging Face |
| `teich convert` | Writes standalone OpenAI-style training JSONL (`prompt`, `messages`, `tools`, `metadata`) consumable without Teich at training time |
| `teich anonymize` | Scrubs secrets, PII, usernames, and embedded media from a directory |
| `prepare_data()` | Loads any source, normalizes to messages + tools, renders the target chat template, attaches typed supervision spans, enforces `max_length` |
| `mask_data()` | Converts Teich spans into exact token-level labels after trainer tokenization; everything else stays `-100` |
| `teich studio` | Local browser UI for config, prompts, batches, extraction, and interactive agent sessions |

Typical paths:

- Already have data: `prepare_data() -> SFTTrainer -> mask_data() -> trainer.train()`
- Need new data: `teich init -> edit prompts.jsonl/config.yaml -> teich generate -> prepare_data()`
- Have local agent sessions: `teich extract claude --model fable-5 -> optional HF upload -> prepare_data()`
- Want OpenAI-style JSONL for another trainer: `teich extract ... --out data -> teich convert data --out teich-training.jsonl`
- Full control: `load_traces() -> validate_tool_calls() -> tokenizer.apply_chat_template() -> custom trainer`

## Usage

### Prepare existing data and train

```python
from teich import mask_data, prepare_data
from trl import SFTConfig, SFTTrainer

train_dataset = prepare_data(
    "TeichAI/Claude-Opus-4.6-Reasoning-887x",  # local path, folder, HF id, Dataset, or source mix
    tokenizer,
    max_length=32768,
    oversized_policy="trim_followups",
    tokenize=True,
    chat_template_kwargs={"enable_thinking": True, "preserve_thinking": True},
)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_dataset,
    args=SFTConfig(dataset_text_field="text", max_length=32768, packing=False, output_dir="outputs"),
)

trainer = mask_data(
    trainer,
    tokenizer=tokenizer,
    train_on_reasoning=True,
    train_on_final_answers=True,
    train_on_tools=True,
)

trainer.train()
```

Keep `packing=False` — packed datasets merge row boundaries before masking. Verify labels before a long run with `print(trainer.train_dataset.preview(0, tokenizer))`.

### Generate new traces

```bash
teich init my-project && cd my-project
# edit prompts.jsonl (prompt, system, github_repo, follow_up_prompts) and config.yaml
export OPENAI_API_KEY=sk-...
teich generate -c config.yaml          # --resume skips completed prompts
```

Outputs land under `output/` (raw traces + converted rows + compact dataset card), `sandbox/` (workspace snapshots), and `failures/`. Agent providers need Docker; `agent.provider: chat` does not.

### Extract local sessions

```bash
teich extract claude --model fable-5              # providers: claude, codex, cursor, pi, hermes
teich convert data --out teich-training.jsonl     # standalone OpenAI-style rows
```

Anonymization runs by default; pass `--no-anon` for raw local exports. Review staged data before any Hugging Face upload.

## Gotchas

- `mask_data()` raises if packing is enabled, if every row would be fully masked, or if the supervised-token cap drops every row — silent empty training is impossible by design.
- Masking is not removal: `mask_data(train_on_reasoning=False)` keeps gold reasoning in the causal context; only `prepare_data(reasoning_policy="strip")` removes it before rendering.
- Keep the live model's chat template. Do not replace `tokenizer.chat_template` unless intentionally testing a maintained fork. Per-model contracts (Gemma 4 auto mode, Granite 4.2, Qwen 3.6, Qwen 3.8) are in [05-training](references/05-training.md).
- Do not inject protocol tokens into source messages (Gemma 4 `<|think|>` / `<turn|>`, Qwen/Granite `think` tags). Teich derives them from the live template and supervises or masks them itself.
- Codex never exposes raw chain-of-thought — only human-readable summaries. Codex's default summary setting can yield empty `summary: []`; set `model.reasoning_summary: detailed` plus `reasoning_summaries_enabled: true` to capture rich reasoning.
- Codex host auth (ChatGPT subscription) invalidates your host `codex login` on the first token rotation. Run `codex login` again afterward; `auth_dir` holds live credentials and is kept out of uploaded dirs.
- Claude Code subscription auth: Claude Code silently prefers an API key over subscription credentials, so Teich withholds `ANTHROPIC_API_KEY` when a `claude setup-token` OAuth token is active. Subscription request starts are paced 45 seconds apart by default.
- `teich extract` anonymizes staged traces by default, but anonymization is a best-effort safety pass, not a guarantee — review data before uploading or publishing.
- Rows ending on a tool result are incomplete and dropped by default in `load_traces()` / `prepare_data()`; pass `drop_incomplete_traces=False` only for inspection or repair.
- Pass `tokenize=True` to `prepare_data()` so the trainer treats the dataset as already tokenized; Teich span metadata survives until `mask_data()` runs.
- For Gemma 4, leave `enable_thinking` unset to get per-row auto mode (thinking vs non-thinking resolved independently per row); explicit contradictions fail closed with an error.
- `teich pool upload` is a reserved no-op for a future community backend; publish via the `teich generate` / `teich extract` upload prompt instead.

## References

- [01-cli](references/01-cli.md) — CLI reference for init, generate, extract, convert, anonymize, capture-context, studio, pool, and env vars
- [02-generation](references/02-generation.md) — generation workflows, config.yaml, prompt files, providers (codex, pi, claude-code, hermes, chat), subscription host auth, local endpoints, outputs
- [03-data-format](references/03-data-format.md) — normalized messages and tools shape, metadata, native Claude context, structured chat rows, incomplete traces, dataset cards
- [04-prepare-data](references/04-prepare-data.md) — prepare_data sources, reports, oversized policies, mixed sources, tool validation, load_traces manual flow, preflight helpers, ShareGPT export
- [05-training](references/05-training.md) — TRL/Unsloth patterns, mask_data policy and guarantees, per-model contracts for Gemma 4, Granite 4.2, Qwen 3.6, Qwen 3.8
- [06-studio](references/06-studio.md) — teich studio browser UI: launch, interactive sessions, batch, extraction, dataset preview
