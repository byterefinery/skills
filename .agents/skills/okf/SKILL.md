---
name: okf
description: Creates, validates, and manages Open Knowledge Format (OKF v0.2) bundles — directory trees of markdown concept documents with YAML frontmatter. Use when the user needs to create a knowledge bundle from PDF, Office, or web sources; write or update concept documents; ingest markdown into multiple linked concepts; validate OKF conformance; generate index files; manage cross-links between concepts; or query bundles by temporal validity, authorship, trust tier, lifecycle status, or any frontmatter field. Uses okf.py for creating, validating, visiting, and searching OKF bundles. OKF documents are linked so agents can traverse and analyze content without original source files.
metadata:
  tags:
    - meta
    - okf
    - knowledge
    - documentation
---

# okf

Open Knowledge Format (OKF v0.2) bundle management. OKF represents knowledge as a directory of markdown files with YAML frontmatter — readable by humans, parseable by agents, diffable in version control, portable across tools and organizations.

## Overview

OKF turns source documents into a structured, linkable knowledge corpus. The workflow:

1. **Ingest** — read PDFs, Office documents, Markdown files, or web pages.
2. **Extract** — identify concepts, definitions, metrics, and relationships.
3. **Produce** — write OKF concept documents with frontmatter recording provenance, trust, freshness, lifecycle, and attestation.
4. **Link** — connect concepts with file-relative markdown links and per-claim footnotes.
5. **Query** — find concepts by temporal validity, authorship, trust tier, status, type, tags, or any frontmatter field.

A bundle is a self-contained directory tree, distributable as a git repo, tarball, or subdirectory.

The format answers five questions that plain markdown cannot:

1. **Provenance** — what was this created from, and where in the source?
2. **Trust** — how much should I trust it?
3. **Freshness** — is it still true?
4. **Lifecycle** — is it the current version?
5. **Attestation** — was this value produced the sanctioned way?

## Usage

### Creating a bundle from a source

1. **Detect language** — identify the source's natural language. All produced filenames, titles, descriptions, body prose, and `index.md` entries use this language. Exception: `log.md` is always in English.
2. **Ingest** the source in chunks — convert or fetch incrementally, processing overlapping windows so context carries across boundaries.
3. **Extract** every concept — do not skip or summarize away details. The bundle must be sufficient to recreate the original source (lossy in format, semantically complete).
4. **Write** one `.md` file per concept with frontmatter (`type` required) and structured body.
5. **Cross-link** concepts with bundle-relative markdown links (recommended form: `/path/to/concept.md`).
6. **Generate** `index.md` at bundle root.

**Chunked ingestion.** Split converted markdown into fixed 500-line chunks. Process each with a sliding window (tail of previous + full current + head of next). Record `location` in `sources` entries for every source reference. After all chunks, deduplicate and merge.

**Ingest with direct Python scripts.** Use PEP 723 inline dependencies with `uv run`:

```python
#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.10"
# dependencies = ["docling"]
# ///
"""Convert PDF/Office documents to markdown."""
import sys
from docling.document_converter import DocumentConverter
result = DocumentConverter().convert(sys.argv[1] if len(sys.argv) > 1 else "./input.pdf")
print(result.document.export_to_markdown())
```

### Querying a bundle

Find concepts by temporal validity, authorship, trust, or any frontmatter field:

```bash
# What was valid on a specific date
okf.py visit --bundle ./bundle --query "valid-on:2022-03-15"

# What was valid for a date range
okf.py visit --bundle ./bundle --query "valid-between:2020-01-01,2024-06-30"

# What did a human write (not AI)
okf.py visit --bundle ./bundle --query "written-by:human"

# What did AI write
okf.py visit --bundle ./bundle --query "written-by:ai"

# What has been reviewed by a human
okf.py visit --bundle ./bundle --query "reviewed-by:human"

# Trust tier queries
okf.py visit --bundle ./bundle --query "trust-tier:human-reviewed"
okf.py visit --bundle ./bundle --query "trust-tier:machine-confirmed"
okf.py visit --bundle ./bundle --query "trust-tier:unverified"

# Lifecycle queries
okf.py visit --bundle ./bundle --query "status:stable AND not-stale"
okf.py visit --bundle ./bundle --query "status:deprecated"

# Type, tags, presence
okf.py visit --bundle ./bundle --query 'type:"Attested Computation"'
okf.py visit --bundle ./bundle --query "tag:finance"
okf.py visit --bundle ./bundle --query "has:sources"

# Date comparisons
okf.py visit --bundle ./bundle --query "generated.after:2024-01-01"
okf.py visit --bundle ./bundle --query "source-modified.after:2024-01-01"

# Source author
okf.py visit --bundle ./bundle --query "source-author:human"

# Text search
okf.py visit --bundle ./bundle --query "title~:revenue"
okf.py visit --bundle ./bundle --query "body~:recognition policy"

# Combined queries
okf.py visit --bundle ./bundle --query "status:stable AND not-stale AND trust-tier:human-reviewed"
okf.py visit --bundle ./bundle --query "written-by:human OR reviewed-by:human"
okf.py visit --bundle ./bundle --query "NOT status:deprecated"
okf.py visit --bundle ./bundle --query "(valid-on:2022-03-15 AND tag:finance) OR tag:legal"

# Output modes
okf.py visit --bundle ./bundle --query "tag:finance" --output paths       # default: file paths
okf.py visit --bundle ./bundle --query "tag:finance" --output json        # JSON with frontmatter
okf.py visit --bundle ./bundle --query "tag:finance" --output frontmatter # YAML frontmatter only
okf.py visit --bundle ./bundle --query "tag:finance" --output summary     # detailed table

# Structured search (always table or JSON)
okf.py search --bundle ./bundle --query "status:stable"
okf.py search --bundle ./bundle --query "status:stable" --json
```

### Inspecting a concept

```bash
okf.py info --bundle ./bundle concepts/revenue.md
okf.py info --bundle ./bundle --json concepts/revenue.md
okf.py info --bundle ./bundle --validity concepts/revenue.md
okf.py info --bundle ./bundle --trust-tier concepts/revenue.md
```

### Validating a bundle

```bash
okf.py validate --bundle ./my-bundle
okf.py validate --bundle ./my-bundle concepts/revenue.md
```

### Scaffolding

```bash
okf.py create --bundle ./bundle --init                              # root index.md
okf.py create --bundle ./bundle --type Metric --title "MAU" --description "..."
okf.py create --bundle ./bundle --type "Attested Computation" --runtime python --param "year:integer:true"
okf.py create --bundle ./bundle --type Policy --title "Revenue Policy" --tags "finance,policy" --status draft --stale-after 2026-12-31
```

### Generating index files

```bash
okf.py generate-index --bundle ./bundle
okf.py generate-index --bundle ./bundle --dir tables/
okf.py generate-index --bundle ./bundle --query "status:stable"
```

### Listing concepts

```bash
okf.py list --bundle ./bundle
okf.py list --bundle ./bundle --json
```

### Updating a bundle

When augmenting existing concept documents:

- Preserve all existing frontmatter keys — only `generated` may be dropped (refreshes on write).
- Every existing `#` heading must appear in the updated body, same order, same wording.
- Extend prose under existing headings, add new bullets, or add new headings **after** existing ones.
- Merge `tags` and `sources` — never shrink existing lists.

## Frontmatter

Every concept is a UTF-8 markdown file with YAML frontmatter delimited by `---`, followed by a markdown body.

### Required

- **`type`** — short string identifying the concept kind. The only always-required field. Common values: `Concept`, `Reference`, `Metric`, `Playbook`, `Policy`, `Attested Computation`, `Skill`, `Table`, `Dataset`, `API Endpoint`, `Document`. Type values are not registered centrally.

### Recommended

- **`title`** — human-readable display name.
- **`description`** — one sentence summarizing the concept.
- **`resource`** — URI or path identifying the underlying asset. Absent for abstract concepts.
- **`tags`** — YAML list of short strings.

### Provenance

```yaml
sources:
  - id: rev-policy
    resource: https://wiki.acme/finance/revenue-recognition
    title: Revenue recognition policy
    author: human:jsmith@acme
    last_modified: 2026-06-15
usage_window: { from: 2026-06-01, to: 2026-06-30 }
```

Each `sources` entry: `resource` (required), `id`, `title`, `author`, `usage_count`, `last_modified`. `usage_window` is a sibling of `sources`. Per-claim attribution uses markdown footnotes keyed to `sources[].id`.

### Trust

```yaml
generated: { by: okf_agent/claude-sonnet-4-5, at: 2025-07-15T14:30:00Z }
verified:
  - { by: human:alice, at: 2025-07-16T09:00:00Z }
  - { by: process:nightly-check, at: 2025-07-17T02:00:00Z }
```

Trust tiers: no `verified` → **unverified**; only non-`human:` actors → **machine-confirmed**; any `human:<id>` → **human-reviewed**.

Actor convention: `<producer>/<version>` for agents, `human:<id>` for people, `process:<id>` for automated processes.

### Lifecycle

```yaml
status: stable        # draft | stable | deprecated (default: stable)
stale_after: 2026-12-31
```

Concept is stale when `today >= stale_after`.

### Attested Computation

```yaml
type: Attested Computation
runtime: python
parameters:
  - { name: month, type: string, required: true }
executor:
  resource: references/executors/run-python.sh
  receipt: [exit_code, stdout, stderr]
attester:
  resource: references/attesters/mau-check.py
```

## Gotchas

- **Use direct Python scripts, not skill scripts** — document conversion uses PEP 723 inline dependencies with `uv run`, not external scripts.
- **PEP 723 block is mandatory** — every Python script must include the `# /// script ... # ///` metadata block.
- **Bundle-relative paths recommended** — use `/path/to/concept.md` (bundle-relative) for cross-links, not relative paths. Both forms are valid; bundle-relative is stable when documents move.
- **`type` is the only required field** — `type: Concept` alone is fully conformant.
- **`sources` lives in frontmatter** — no `# Citations` body sections. Use `sources` + per-claim footnotes.
- **Footnote labels must match `sources[].id`** — the label is a join key.
- **`generated` and `verified` are distinct** — who *wrote* need not be who *confirmed*.
- **Actor convention keys off `human:` prefix** — trust tiers derive from `human:<id>` in `verified`.
- **`status` absent means `stable`** — only set for `draft` or `deprecated`.
- **Attested Computations are standalone** — do not embed in other types.
- **`index.md` has no frontmatter** — except bundle root may carry `okf_version: "0.2"`.
- **`log.md` is always in English** — all other bundle files follow the source's detected language.
- **YAML auto-parses dates** — `stale_after: 2026-12-31` becomes a `datetime.date` object, not a string. `okf.py` handles both string and native types.
- **`okf.py visit` requires `--query`** — always provide a query expression. Use `status:stable` to match all stable concepts.
- **Quotes for multi-word values** — use `type:"Attested Computation"` (quotes) not `type:Attested Computation`.

## References

- [01-frontmatter](references/01-frontmatter.md) — Complete field reference: core, provenance, trust, lifecycle, extensions
- [02-attested-computations](references/02-attested-computations.md) — Attested computation contract, runtimes, executor/attester flow
- [03-bundle-structure](references/03-bundle-structure.md) — index.md, log.md, cross-linking, paths, body conventions
- [04-query-language](references/04-query-language.md) — Full query expression reference with examples
- [05-conformance](references/05-conformance.md) — Conformance rules, versioning, v0.1 migration
