---
name: okf
description: Creates, validates, and manages Open Knowledge Format (OKF v0.2) bundles — directory trees of markdown concept documents with YAML frontmatter. Use with the `markdown` and `webfetch` skills to preprocess PDF, Office, and web sources into markdown; then OKF extracts concepts, writes linked documents with provenance/trust/freshness/lifecycle frontmatter, and enables querying by any frontmatter field. Uses okf.py for creating, validating, visiting, and searching OKF bundles.
allowed-tools: Bash(okf.py:*)
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

## Preprocessing

Route source material through the appropriate skill before OKF ingestion. Load the skill and follow its instructions.

| Source type | Skill to load |
|---|---|
| PDF, DOCX, PPTX, ODT, XLSX, images | `markdown` |
| Web URLs | `webfetch` |
| Plain markdown/text | none — ingest directly |

**Workflow:**

1. Load the preprocessing skill (`markdown` for documents, `webfetch` for URLs).
2. Convert or fetch the source to a markdown file.
3. Feed the resulting markdown into the OKF extraction workflow below.

## Usage

### Creating a bundle from a source

1. **Detect language** — identify the source's natural language. All produced filenames, titles, descriptions, body prose, and `index.md` entries use this language. Exception: `log.md` is always in English.
2. **Preprocess** — load the `markdown` skill (documents) or `webfetch` skill (URLs) and convert the source to markdown. Plain markdown/text feeds directly.
3. **Ingest** the converted markdown in chunks — process overlapping windows so context carries across boundaries.
4. **Extract** every concept — do not skip or summarize away details. The bundle must be sufficient to recreate the original source (lossy in format, semantically complete). Every page, slide, section must be accounted for.
5. **Write** one `.md` file per concept with frontmatter (`type` required), `coverage` tracking, and structured body.
6. **Cross-link** concepts with bundle-relative markdown links (recommended form: `/path/to/concept.md`).
7. **Verify** — run `okf.py check-coverage` to ensure no source regions are uncovered.
8. **Generate** `index.md` at bundle root.

**Chunked ingestion.** Split converted markdown into fixed 500-line chunks. Process each with a sliding window (tail of previous + full current + head of next). Record source region in `coverage` for every concept. After all chunks, deduplicate and merge.

**Coverage tracking.** Every concept must record which source regions it covers. This enables verification that nothing was missed.

```yaml
coverage:
  - source: annual-report.pdf
    region: { pages: [12-15] }
  - source: annual-report.pdf
    region: { pages: [22-23] }
```

**Extraction rules.** Do not summarize, paraphrase, or omit. Capture verbatim:

- **Tables** — every row and column, as markdown tables. Never summarize "see table above".
- **Lists** — preserve hierarchy and numbering. Every bullet, every sub-bullet.
- **Formulas** — verbatim in fenced code blocks or math notation. Never paraphrase.
- **Code blocks** — verbatim. Never truncate or summarize.
- **Footnotes** — capture as markdown footnotes linked to the claim.
- **Cross-references** — resolve to OKF concept links where possible.
- **Appendices** — same extraction treatment as body content.
- **Images/diagrams** — describe content in prose, include alt text equivalent.
- **Definitions** — exact wording, not paraphrased.
- **Numbers/metrics** — exact values with units, never rounded or approximated.

**Preprocess the source.** Convert the source to markdown by loading the appropriate skill — `markdown` for documents, `webfetch` for URLs. See the Preprocessing section.

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

### Checking source coverage

After creating a bundle, verify no source regions were missed:

```bash
# Summary of coverage
okf.py check-coverage --bundle ./bundle

# Report gaps in page coverage
okf.py check-coverage --bundle ./bundle --report gaps

# Report overlapping coverage (same pages in multiple concepts)
okf.py check-coverage --bundle ./bundle --report overlaps

# Report concepts without coverage tracking
okf.py check-coverage --bundle ./bundle --report uncovered

# Check against expected source regions (JSON file)
okf.py check-coverage --bundle ./bundle --source-regions expected-regions.json

# JSON output
okf.py check-coverage --bundle ./bundle --report json
```

Expected regions file format:

```json
{
  "annual-report.pdf": [
    {"pages": [1, 2, 3]},
    {"pages": [4-10]},
    {"pages": [11, 12, 13, 14, 15]}
  ]
}
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

### Coverage (extension)

`coverage` tracks which source regions a concept covers. Enables verification that no content was missed during extraction.

```yaml
coverage:
  - source: annual-report.pdf
    region: { pages: [12-15] }
  - source: annual-report.pdf
    region: { pages: [22-23] }
  - source: product-deck.pptx
    region: { slides: [7-9] }
  - source: financials.xlsx
    region: { sheet: "Revenue", range: "A1:D50" }
```

Each entry: `source` (required, filename or URI), `region` (required, mapping with `pages`, `slides`, `sheet`+`range`, or `section`).

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

- **Use skills for preprocessing** — load the `markdown` skill for document conversion and the `webfetch` skill for fetching URLs. OKF ingests the resulting markdown.
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
- **Always track coverage** — every concept must have `coverage` entries recording which source regions it covers. Run `okf.py check-coverage --report gaps` after extraction to find missed regions.
- **Never summarize tables** — capture every row and column verbatim. A summarized table loses data needed for reconstruction.
- **Never paraphrase formulas** — capture verbatim in fenced code blocks. Paraphrased formulas introduce errors.
- **Coverage is a known extension** — not in the OKF v0.2 spec but documented by this skill. Consumers must not reject it (spec allows unknown keys).

## References

- [01-frontmatter](references/01-frontmatter.md) — Complete field reference: core, provenance, trust, lifecycle, extensions
- [02-attested-computations](references/02-attested-computations.md) — Attested computation contract, runtimes, executor/attester flow
- [03-bundle-structure](references/03-bundle-structure.md) — index.md, log.md, cross-linking, paths, body conventions
- [04-query-language](references/04-query-language.md) — Full query expression reference with examples
- [05-conformance](references/05-conformance.md) — Conformance rules, versioning, v0.1 migration
