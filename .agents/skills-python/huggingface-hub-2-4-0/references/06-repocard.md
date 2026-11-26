# 06 — Repo cards

Repo cards are the README files of Hub repos, parsed as Markdown with a YAML metadata block.

## Classes

- `RepoCard` — base card (content + `CardData` metadata)
- `ModelCard`, `ModelCardData`
- `DatasetCard`, `DatasetCardData`
- `SpaceCard`, `SpaceCardData`

Each card has `.content` (markdown body) and metadata in its YAML block. Cards support (verified from `repocard.py`):

- `RepoCard.load(...)` / `ModelCard.load(...)` / `DatasetCard.load(...)` — load from local file or repo
- `card.save(filepath)` — write to a local file
- `card.push_to_hub(...)` — push the card to its repo
- `card.validate(repo_type=None)` — validate card structure
- `from_template(...)` — build a card from the built-in templates (`repocard_templates`)

## Metadata helpers

Module-level functions (signatures verified from `repocard.py`; they take **local paths**):

- `metadata_load(local_path) -> dict | None` — read the YAML metadata block
- `metadata_save(local_path, data: dict)` — write a dict into the file
- `metadata_update(local_path, ...)` — update a single key
- `metadata_eval_result(...)` — read eval results from a model card file

## Eval results

- `parse_eval_result_entries(yaml_text)` — parse the `eval_results_list` YAML block
- `eval_result_entries_to_yaml(entries)` — serialize back
- `EvalResult`, `EvalResultEntry` — typed views
