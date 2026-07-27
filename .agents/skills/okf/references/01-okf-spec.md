# OKF v0.2 Specification

## Core Concepts

- **Knowledge Bundle** (or **bundle**): A self-contained, hierarchical collection of knowledge documents. The unit of distribution.
- **Concept**: A single unit of knowledge within a bundle, represented as one markdown document. It may describe a tangible asset (a table, an API), an abstract idea (a metric, a business process), or anything in between.
- **Concept ID**: The path of the concept's file within the bundle, with the `.md` suffix removed.
- **Frontmatter**: A YAML metadata block delimited by `---` at the top of a markdown file.
- **Body**: Everything in the file after the frontmatter.
- **Link**: A standard markdown link from one concept to another, used to express relationships beyond the implicit parent/child hierarchy.
- **Source**: A material a concept derives from, external or internal to the bundle, recorded in the `sources` frontmatter field.
- **Provenance**: The set of sources a concept derives from.
- **Credibility signal**: An objective, per-source fact (`author`, `usage_count`, `last_modified`) used to infer trust; OKF records the signals, not a verdict.
- **Actor**: A string identifying who or what performed an action, using the convention `<producer>/<version>` for agents, `human:<id>` for people, and `process:<id>` for automated processes.
- **Trust tier**: A level derived from a concept's `verified` field: unverified, machine-confirmed, or human-reviewed.

## Bundle Structure

A bundle is a directory tree of markdown files. The directory structure is independent of the domain:

```
path/to/bundle/
  index.md                      # Optional: directory listing for progressive disclosure
  log.md                        # Optional: chronological history of updates
  <concept>.md                  # A concept at the bundle root
  <subdirectory>/               # Subdirectories organize concepts into groups
    index.md
    <concept>.md
```

A bundle MAY be distributed as:
- A git repository (recommended)
- A tarball or zip archive
- A subdirectory within a larger repository

### Reserved Filenames

| Filename   | Purpose                          |
|------------|----------------------------------|
| `index.md` | Directory listing. No frontmatter (except bundle root may carry `okf_version`) |
| `log.md`   | Update history. Date-grouped entries, newest first |

These MUST NOT be used for concept documents.

## Concept Documents

Every concept is a UTF-8 markdown file with two parts:
1. A **YAML frontmatter block**, delimited by `---`
2. A **markdown body**, containing free-form content

### Frontmatter

**Required:**
- `type`: A short string identifying the kind of concept. Example values: `Document`, `Report`, `Reference`, `Playbook`, `Metric`, `API Endpoint`, `Attested Computation`. Type values are **not** registered centrally. Consumers MUST tolerate unknown types gracefully.

`type` is the only always-required key; a concept carrying just `type` is fully conformant.

**Recommended:**
- `title`: Human-readable display name
- `description`: A single sentence summarizing the concept
- `resource`: A URI that uniquely identifies the underlying asset
- `tags`: A YAML list of short strings for cross-cutting categorization

**Optional families:**

### Provenance: `sources`

```yaml
sources:
  - id: source-key
    resource: https://example.com/source
    title: Source Title
    author: team:author-name
    usage_count: 5000
    last_modified: 2026-05-30
usage_window: { from: 2026-06-01, to: 2026-06-30 }
```

Each `sources` entry:
- `resource` (required): URL, bundle-relative path, or scope descriptor
- `id` (optional): Stable key for per-claim attribution via markdown footnotes
- `title` (optional): Human-readable label
- `author` (optional): Who produced the source (actor convention)
- `usage_count` (optional): Exercise count over `usage_window`
- `last_modified` (optional): When the source last changed (`YYYY-MM-DD`)

**Per-claim attribution** uses markdown footnotes keyed to `sources[].id`:
```markdown
Revenue grew 15% year-over-year.[^annual-report]

[^annual-report]: Annual Report 2024
```

### Trust: `generated` and `verified`

```yaml
generated: { by: okf_tool/okf.sh, at: 2026-06-20T22:53:05Z }
verified:
  - { by: human:alice, at: 2026-06-25T09:00:00Z }
  - { by: process:finance-nightly, at: 2026-06-26T02:00:00Z }
```

- `generated.by` (required within `generated`): Actor who produced the content
- `generated.at`: ISO 8601 datetime of last meaningful change
- `verified`: List of verification events with `by` and `at`
- A single verifier may be written as a bare mapping without the list dash

### Trust Tiers

Derived from `verified`:
- No `verified` key → **unverified**
- Only non-`human:` actors → **machine-confirmed**
- Has `human:` actor → **human-reviewed**

### Lifecycle: `status` and `stale_after`

```yaml
status: stable        # draft | stable | deprecated
stale_after: 2026-09-23
```

- `draft`: not yet reviewed; possibly incomplete
- `stable`: default; ready for consumption
- `deprecated`: kept for links and history; no longer current
- Absent `status` → `stable`
- `stale_after`: absolute date (`YYYY-MM-DD`); concept is stale when `today >= stale_after`

## Cross-linking

Two forms of links between concepts:
- **Absolute (bundle-relative)**: begins with `/`, stable when documents move within subdirectory
- **Relative**: standard markdown relative path

Consumers MUST tolerate broken links.

### The `references/` Convention

A `references/` subdirectory conventionally mirrors external material, run instructions, or code as first-class concepts within the bundle.

## Actor Convention

- `<producer>/<version>` for agents and tools (e.g., `okf_tool/okf.sh`)
- `human:<id>` for people (e.g., `human:alice`)
- `process:<id>` for automated processes (e.g., `process:finance-nightly`)

Consumers that classify trust key off the `human:` prefix, so producers MUST use it for hand-authored or human-confirmed content.

## Index Files

`index.md` enumerates directory contents for progressive disclosure. No frontmatter (except bundle root may carry `okf_version`). Body uses sections with bulleted lists. All links use file-relative paths that resolve from the index's directory:

```markdown
# Documents

* [Annual Report 2024](documents/annual-report-2024.md) - Q1-Q4 financial and operational results.
* [Product Specification](documents/product-spec.md) - Technical requirements and design.
```

Never use absolute `/` paths in `index.md` — they break GitHub rendering.

## Log Files

`log.md` records change history. Flat list of date-grouped entries, newest first:

```markdown
# Directory Update Log

## 2026-05-22
* **Update**: Added a reference for [Customer Metrics](/tables/customer-metrics.md).
* **Creation**: Established the [Product Playbook](/playbooks/product.md).

## 2026-05-15
* **Initialization**: Created foundational directory structure.
```

Date headings MUST use ISO 8601 `YYYY-MM-DD` form.

## Conformance

A bundle is **conformant** with OKF v0.2 if:
1. Every non-reserved `.md` file contains a parseable YAML frontmatter block
2. Every frontmatter block contains a non-empty `type` field
3. Every reserved filename follows its specified structure when present

Consumers MUST NOT reject a bundle because of:
- Missing optional frontmatter fields
- Unknown `type` values
- Unknown additional frontmatter keys
- Broken cross-links
- Missing `index.md` files

## Versioning

OKF uses `<major>.<minor>` versioning. Bundles may declare version with `okf_version: "0.2"` in bundle-root `index.md` frontmatter (the only place frontmatter is permitted in an `index.md`).
