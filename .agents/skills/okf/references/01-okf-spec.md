# OKF v0.2 Specification Summary

## Core Concepts

- **Knowledge Bundle**: A self-contained, hierarchical collection of knowledge documents. The unit of distribution.
- **Concept**: A single unit of knowledge, represented as one markdown document.
- **Concept ID**: The path of the concept's file within the bundle, with `.md` suffix removed.
- **Frontmatter**: YAML metadata block at the top of a markdown file.
- **Body**: Everything after the frontmatter.

## Bundle Structure

```
bundle/
  index.md              # Optional: directory listing
  log.md                # Optional: update history
  <concept>.md          # Concept document
  <subdirectory>/
    index.md
    <concept>.md
```

A bundle may be distributed as a git repository (recommended), tarball, zip archive, or subdirectory.

## Reserved Filenames

| Filename | Purpose |
|----------|---------|
| `index.md` | Directory listing for progressive disclosure |
| `log.md` | Chronological update history |

These MUST NOT be used for concept documents.

## Concept Document Format

Every concept is a UTF-8 markdown file with:
1. YAML frontmatter block (delimited by `---`)
2. Markdown body (free-form content)

### Frontmatter Fields

**Required:**
- `type` — A short string identifying the kind of concept. Examples: `BigQuery Table`, `API Endpoint`, `Metric`, `Playbook`, `Reference`, `Attested Computation`. Not centrally registered; consumers must tolerate unknown types.

**Recommended:**
- `title` — Human-readable display name
- `description` — One-sentence summary
- `resource` — URI of the underlying asset
- `tags` — List of short categorization strings

**Optional families:**

### Provenance (`sources`)

Records materials a concept derives from:

```yaml
sources:
  - id: ga4-schema
    resource: https://developers.google.com/analytics/bigquery/export-schema
    title: GA4 BigQuery Export schema
    author: team:ga4-docs
    usage_count: 5000
    last_modified: 2026-05-30
usage_window: { from: 2026-06-01, to: 2026-06-30 }
```

Each source entry:
- `resource` (required): URL, bundle-relative path, or scope descriptor
- `id` (optional): Stable key for per-claim attribution via markdown footnotes
- `title` (optional): Human-readable label
- `author` (optional): Actor who produced the source
- `usage_count` (optional): Exercise count over `usage_window`
- `last_modified` (optional): When the source last changed

Per-claim attribution uses markdown footnotes keyed to `sources[].id`:
```markdown
The table is sharded daily.[^ga4-schema]

[^ga4-schema]: GA4 BigQuery Export schema
```

### Trust (`generated`, `verified`)

```yaml
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-20T22:53:05Z }
verified:
  - { by: human:alice, at: 2026-06-25T09:00:00Z }
  - { by: process:finance-nightly, at: 2026-06-26T02:00:00Z }
```

- `generated.by` (required within `generated`): Actor who produced the content
- `generated.at`: ISO 8601 datetime of last meaningful change
- `verified`: List of verification events with `by` and `at`
- A single verifier may be written as a bare mapping (not a list)

### Trust Tiers

Derived from `verified`:
- No `verified` key → **unverified**
- Only non-`human:` actors → **machine-confirmed**
- Has `human:` actor → **human-reviewed**

### Lifecycle (`status`, `stale_after`)

```yaml
status: stable        # draft | stable | deprecated
stale_after: 2026-09-23
```

- `draft`: not yet reviewed; possibly incomplete
- `stable`: default; ready for consumption
- `deprecated`: kept for links and history; no longer current
- Absent `status` → `stable`
- `stale_after`: absolute date; concept is stale when `today >= stale_after`

## Cross-linking

Two forms of links between concepts:
- **Absolute (bundle-relative)**: begins with `/`, stable when documents move within subdirectory
- **Relative**: standard markdown relative path

Consumers must tolerate broken links.

## Actor Convention

- `<producer>/<version>` for agents and tools (e.g., `reference_agent/gemini-2.5-pro`)
- `human:<id>` for people (e.g., `human:alice`)
- `process:<id>` for automated processes (e.g., `process:finance-nightly`)

## Index Files

`index.md` enumerates directory contents for progressive disclosure. No frontmatter (except bundle root may carry `okf_version`). Body uses sections with bulleted lists:

```markdown
# Tables

* [Customer Orders](orders.md) - One row per completed order.
* [Customers](customers.md) - Customer dimension table.
```

## Log Files

`log.md` records change history. Flat list of date-grouped entries, newest first:

```markdown
# Directory Update Log

## 2026-05-22
* **Update**: Added a BigQuery table reference.
* **Creation**: Established the Dataplex Playbook.
```

## Attested Computation

A standalone concept (`type: Attested Computation`) carrying a sanctioned way to compute a value:

```yaml
type: Attested Computation
runtime: bigquery
parameters:
  - { name: year, type: integer, required: true }
executor:
  resource: references/skills/run-on-bq.md
  receipt: [job_id, executed_sql, result]
attester:
  resource: references/attesters/revenue.py
```

- `runtime` (required): How to run the computation (`bigquery`, `postgres`, `dbt`, `python`, `Looker`)
- `parameters`: Typed, named holes the agent may fill
- `computation`: Path to computation file (or inline in body `# Computation`)
- `executor`: How the computation is run; `receipt` declares evidence fields
- `attester`: Deterministic code that inspects a receipt and returns a verdict

## Conformance

A bundle is conformant if:
1. Every non-reserved `.md` file has parseable YAML frontmatter
2. Every frontmatter has a non-empty `type` field
3. Reserved filenames follow their specified structure when present

Consumers MUST NOT reject a bundle for:
- Missing optional frontmatter fields
- Unknown `type` values
- Unknown additional frontmatter keys
- Broken cross-links
- Missing `index.md` files

## Versioning

OKF uses `<major>.<minor>` versioning. Bundles may declare version with `okf_version: "0.2"` in bundle-root `index.md` frontmatter.
