---
name: okf
description: Creates, validates, and manages Open Knowledge Format (OKF v0.2) bundles — directory trees of markdown concept documents with YAML frontmatter. Use when the user needs to create a knowledge bundle from PDF, Office, or web sources; write or update concept documents; ingest markdown into multiple linked concepts; validate OKF conformance; generate index files; or manage cross-links between concepts. Relies on `markdown` skill for PDF/Office/Excel/PPT conversion and `webfetch` for URL fetching. OKF documents are linked together so agents can traverse and analyze content without the original source files ever being present again.
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

1. **Ingest** — read PDFs, Office documents (Word, Excel, PowerPoint), Markdown files, or web pages.
2. **Extract** — identify concepts, definitions, metrics, and relationships within the source material.
3. **Produce** — write OKF concept documents with frontmatter that records what each concept is, where it came from, and how much to trust it.
4. **Link** — connect concepts to each other and back to their sources using standard markdown links and footnotes.

A bundle is a self-contained directory tree. It can be distributed as a git repo, a tarball, or a subdirectory. If you can `cat` a file, you can read OKF; if you can `git clone` a repo, you can ship it.

The format answers five questions that plain markdown cannot:

1. **Provenance** — what was this created from, and where in the source?
2. **Trust** — how much should I trust it?
3. **Freshness** — is it still true?
4. **Lifecycle** — is it the current version?
5. **Attestation** — was this value produced the sanctioned way?

## Usage

### Converting source documents with `markdown` skill

Use the `markdown` skill to convert source documents into text before extracting concepts:

```bash
# Convert PDF to markdown
markdown.sh --to md ./annual-report-2024.pdf

# Convert Word document
markdown.sh --to md ./product-spec.docx

# Convert Excel workbook (formula evaluation included)
markdown.sh --to md ./financials.xlsx

# Convert PowerPoint
markdown.sh --to md ./quarterly-deck.pptx
```

The output is structured markdown preserving headings, tables, lists, and code blocks. Track the original file path in `sources[].resource` and record page/slide/sheet locations in `sources[].location`.

### Fetching web pages with `webfetch` skill

Use the `webfetch` skill to retrieve web pages as markdown:

```bash
# Fetch as markdown to stdout
webfetch.sh https://example.com/docs/api

# Save to file
webfetch.sh --file ./api-docs.md https://example.com/docs/api
```

The output is LLM-friendly markdown. Track the fetched URL in `sources[].resource` and record the section or heading in `sources[].location`.

### Creating a bundle

1. Convert or fetch all source documents.
2. Read the converted content and identify distinct concepts.
3. For each concept, write a `.md` file with frontmatter (`type` required; `title`, `description`, `sources` recommended) and a structured body.
4. Cross-link concepts with file-relative markdown links.
5. Optionally generate `index.md` files per directory.
6. Optionally write a `log.md` with date-grouped change entries.

### Updating a bundle

When augmenting existing concept documents:

- Preserve all existing frontmatter keys — only `generated` may be dropped (it refreshes on write).
- Every existing `#` heading must appear in the updated body, in the same order, with the same wording.
- Extend prose under existing headings, add new bullets to existing lists, or add new headings **after** the existing ones.
- Merge `tags` and `sources` — never shrink existing lists.
- Add new `sources` entries for any new material incorporated.

## Frontmatter

Every concept is a UTF-8 markdown file with a YAML frontmatter block delimited by `---` at the top, followed by a markdown body.

### Required

- **`type`** — a short string identifying the kind of concept. This is the only always-required key; a concept carrying just `type` is fully conformant.

  Common values: `Document`, `Concept`, `Reference`, `Attested Computation`, `Metric`, `Playbook`. Type values are not registered centrally — producers pick descriptive names, consumers tolerate unknown types gracefully.

### Recommended

- **`title`** — human-readable display name. Used verbatim in auto-generated `index.md` files.
- **`description`** — one sentence summarizing the concept. Used in `index.md`, search snippets, and previews.
- **`resource`** — a URI or path that uniquely identifies the underlying asset. Absent for concepts that describe abstract ideas rather than physical resources.
- **`tags`** — a YAML list of short strings for cross-cutting categorization.

### Provenance: `sources` and `location`

`sources` records the materials a concept derives from. Each entry is a mapping:

- `resource` (required within entry) — the URI or path of the source.
- `id` (recommended) — a stable key used for per-claim footnote attribution.
- `title` (recommended) — human-readable label for the source.
- `location` (recommended) — where within the source the information appeared.

The `location` field is a mapping that varies by source type:

```yaml
sources:
  - id: annual-report-2024
    resource: /docs/annual-report-2024.pdf
    title: Annual Report 2024
    location: { pages: [12, 13, 15-18] }

  - id: product-deck-q3
    resource: /slides/product-deck-q3.pptx
    title: Q3 Product Deck
    location: { slides: [7-12] }

  - id: financials-sheet
    resource: /data/financials.xlsx
    title: Financial Data
    location: { sheet: "Revenue", range: "A1:D50" }

  - id: api-docs
    resource: https://example.com/docs/api
    title: API Documentation
    location: { section: "Authentication" }
```

Location formats by source type:

| Source type | Location format |
|---|---|
| PDF | `{ pages: [3] }` or `{ pages: [3-5, 8] }` |
| PowerPoint | `{ slides: [12-15] }` |
| Excel | `{ sheet: "Revenue", range: "A1:D50" }` |
| Word | `{ pages: [4-6] }` or `{ section: "Introduction" }` |
| Web / Markdown | `{ section: "## Authentication" }` or `{ heading: "API Keys" }` |

When the location is unknown, omit `location` entirely.

`usage_window` may appear as a sibling of `sources` to frame `usage_count` values with a `{ from, to }` date range. Per-source credibility signals (`author`, `usage_count`, `last_modified`) may also appear on individual `sources` entries.

**Per-claim attribution** — to attribute a specific claim in the body, end the sentence with a markdown footnote whose label matches a `sources[].id`:

```markdown
Revenue recognized per the finance policy.[^rev-policy]

[^rev-policy]: Revenue recognition policy
```

The footnote label is the join key into `sources`; consumers resolve attribution through the matching entry, not by parsing the footnote prose.

### Trust: `generated` and `verified`

`generated` records how the current content was produced. `verified` records who or what has confirmed it. They are kept distinct because who *wrote* a concept need not be who *confirmed* it.

```yaml
generated: { by: okf_agent/claude-sonnet-4-5, at: 2025-07-15T14:30:00Z }
```

- `generated.by` — the actor that produced the content.
- `generated.at` — ISO 8601 datetime of the last meaningful change.

```yaml
verified:
  - { by: human:alice, at: 2025-07-16T09:00:00Z }
  - { by: process:nightly-check, at: 2025-07-17T02:00:00Z }
```

A single verifier may be written as a bare mapping without the list dash:

```yaml
verified: { by: human:alice, at: 2025-07-16T09:00:00Z }
```

**Trust tiers** are derived from `verified`:

- No `verified` key → **unverified**
- `verified` by non-`human:` actors only → **machine-confirmed**
- `verified` by a `human:<id>` actor → **human-reviewed**

**Actor convention** for `generated.by` and `verified[].by`:

- `<producer>/<version>` for agents and tools — e.g., `okf_agent/claude-sonnet-4-5`
- `human:<id>` for people — e.g., `human:alice`
- `process:<id>` for automated processes — e.g., `process:nightly-check`

### Lifecycle: `status` and `stale_after`

```yaml
status: stable        # draft | stable | deprecated
stale_after: 2025-12-31
```

- `draft` — not yet reviewed; possibly incomplete.
- `stable` — default when `status` is absent; ready for consumption.
- `deprecated` — kept for links and history; no longer current.

`stale_after` is an absolute date (`YYYY-MM-DD`). A concept is stale when `today >= stale_after`.

### Attested Computation

An Attested Computation concept carries not just what a value *means* but a sanctioned way to *compute* it. The contract lives in frontmatter:

- `runtime` (required) — how to run the computation. Example values: `python`, `javascript`, `typescript`, `bash`, `sqlite`, `html`, `css`, `json`, `yaml`, `toml`.
- `parameters` — a list of typed, named holes: `{ name, type, required }`.
- `computation` — optional path to an external file holding the computation. Absent → inline body fence under `# Computation`.
- `executor` — `resource` names run instructions; `receipt` declares fields a run must return.
- `attester` — `resource` names deterministic (no-LLM) code that inspects a receipt and returns a verdict.

Example — a Python computation that computes active users:

```yaml
---
type: Attested Computation
title: Monthly active users
description: Distinct users with at least one event in the month.
runtime: python
parameters:
  - { name: month, type: string, required: true }
  - { name: data_path, type: string, required: true }
executor:
  resource: references/executors/run-python.sh
  receipt: [exit_code, stdout, stderr]
attester:
  resource: references/attesters/mau-check.py
---

# Computation

    import json

    def compute(month: str, data_path: str) -> int:
        with open(data_path) as f:
            events = json.load(f)
        users = {e["user_id"] for e in events if e["ts"].startswith(month)}
        return len(users)
```

Example — a SQLite query:

```yaml
---
type: Attested Computation
title: Revenue by category
description: Total revenue grouped by product category.
runtime: sqlite
parameters:
  - { name: db_path, type: string, required: true }
---

# Computation

    SELECT category, SUM(amount) AS revenue
    FROM orders
    GROUP BY category
    ORDER BY revenue DESC
```

Example — a Bash script:

```yaml
---
type: Attested Computation
title: Disk usage summary
description: Top directories by disk usage in a given path.
runtime: bash
parameters:
  - { name: target_dir, type: string, required: true }
  - { name: top_n, type: integer, required: false }
---

# Computation

    du -sh "${target_dir}"/*/ 2>/dev/null | sort -rh | head -n "${top_n:-10}"
```

Example — a JavaScript computation:

```yaml
---
type: Attested Computation
title: Parse JSONL events
description: Filter and aggregate events from a JSONL stream.
runtime: javascript
parameters:
  - { name: input_file, type: string, required: true }
  - { name: event_type, type: string, required: false }
---

# Computation

    const fs = require('fs');
    const lines = fs.readFileSync(input_file, 'utf8').trim().split('\n');
    const events = lines
      .map(l => JSON.parse(l))
      .filter(e => !event_type || e.type === event_type);
    console.log(JSON.stringify({ count: events.length, events }, null, 2));
```

A concept that *uses* a computation links to it with a normal markdown link — the computation is its own concept, reusable across multiple consumers.

### Extensions

Producers may include any additional keys. Consumers must not reject documents with unrecognized fields and should preserve unknown keys when round-tripping.

## Body Conventions

The body is standard markdown. There are no required body sections. The following headings have conventional meaning:

| Heading | Purpose |
|---|---|
| `# Schema` | Structured description of fields, columns, or properties. |
| `# Examples` | Concrete usage examples, often as fenced code blocks. |
| `# Computation` | The sanctioned computation of an Attested Computation. |
| `# Metrics` | Metrics derived from this concept, linked to reference docs. |
| `# Joins` | Relationships to other concepts, linked to reference docs. |
| `# Dimensions` | Groupable or filterable attributes. |

Producers should favor structural markdown (headings, lists, tables, fenced code blocks) over freeform prose — structure aids both human reading and agent retrieval.

Do not add a `# Citations` section; provenance lives in the `sources` frontmatter with per-claim footnotes.

## Bundle Structure

A bundle is a directory tree of markdown files:

```
path/to/bundle/
  index.md                      # Optional. Directory listing for progressive disclosure.
  log.md                        # Optional. Chronological history of updates.
  <concept>.md                  # A concept at the bundle root.
  <subdirectory>/
    index.md
    <concept>.md
    references/                 # Optional. External material, run instructions, code.
      <reference>.md
```

**Reserved filenames** — `index.md` and `log.md` have defined meaning and must not be used for concept documents.

**`index.md`** — enumerates directory contents for progressive disclosure. Contains no frontmatter (except bundle-root `index.md` which may carry `okf_version: "0.2"`). Body uses sections with bulleted lists:

```markdown
# Documents

* [Annual Report 2024](annual-report-2024.md) — Financial and operational summary for FY2024.
* [Product Roadmap](product-roadmap.md) — Q3-Q4 product planning document.

# References

* [Revenue computation](references/metrics/revenue.md) — Sanctioned revenue calculation.
```

**`log.md`** — flat list of date-grouped entries, newest first:

```markdown
# Directory Update Log

## 2025-07-15
* **Update**: Added location metadata to [Annual Report](annual-report-2024.md) sources.
* **Creation**: Established [Revenue computation](references/metrics/revenue.md).

## 2025-07-10
* **Initialization**: Created foundational directory structure.
```

## Cross-linking

Concepts link to each other using file-relative markdown links. Always use paths relative to the current document's directory — never absolute paths beginning with `/`.

```markdown
See the [revenue computation](../references/metrics/revenue.md).
```

Rules:
- One link per concept mention per section is enough.
- Do not link from headers, fenced code blocks, or schema field-name listings.
- Do not link a document to itself.
- Consumers must tolerate broken links — a missing target is not malformed.

## Gotchas

- **Always use file-relative paths for cross-links** — never use absolute paths beginning with `/`. A link like `(../references/metrics/revenue.md)` resolves correctly when browsing the bundle as plain files on GitHub or locally. An absolute path like `(/references/metrics/revenue.md)` breaks local file browsing.
- **`type` is the only required frontmatter field** — a concept with just `type: Concept` is fully conformant. All other fields are optional, and their absence carries meaning (e.g., unverified vs verified).
- **`location` varies by source type** — there is no single schema. Use the format that matches the source: `pages` for PDFs, `slides` for PPTX, `sheet` + `range` for XLSX, `section` or `heading` for web/markdown. Omit entirely when unknown.
- **`sources` lives in frontmatter, not the body** — do not write a `# Citations` or `# References` body section for provenance. Use `sources` frontmatter + per-claim markdown footnotes.
- **Footnote labels must match `sources[].id`** — the label is a join key, not free text. `[^ga4-schema]` must resolve to a `sources` entry with `id: ga4-schema`.
- **`generated` and `verified` are distinct** — who *wrote* a concept is not who *confirmed* it. Content can change without re-confirmation, and facts can be re-confirmed without regeneration.
- **Actor convention keys off `human:` prefix** — trust tiers derive from whether `verified` contains a `human:<id>` actor. Use `human:alice`, not `alice` or `Alice`.
- **`status` absent means `stable`** — only set `status` for `draft` or `deprecated` concepts.
- **Attested Computations are standalone concepts** — do not embed computations in other concept types. Make the computation its own `type: Attested Computation` document and link to it.
- **`index.md` has no frontmatter** — except at bundle root, where `okf_version: "0.2"` is permitted.
- **Producers may add arbitrary frontmatter keys** — consumers must not reject unknown fields. Preserve them when round-tripping.
- **Bundles are consumed without source files** — the entire point of OKF is that agents can traverse and analyze content using only the bundle. `sources` records provenance, but the original PDF, XLSX, or URL need not be present at consumption time.
