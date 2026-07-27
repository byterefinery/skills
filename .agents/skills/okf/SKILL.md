---
name: okf
description: Creates, validates, and manages Open Knowledge Format (OKF v0.2) bundles — directory trees of markdown concept documents with YAML frontmatter. Use when the user needs to create a knowledge bundle from PDF, Office, or web sources; write or update concept documents; ingest markdown into multiple linked concepts; validate OKF conformance; generate index files; or manage cross-links between concepts. Relies on `markdown` skill for PDF/Office conversion, `webfetch` for URL fetching, and `websearch` for online searches. OKF documents are linked together so agents can traverse and analyze content without the original source files ever being present again.
license: Apache-2.0
compatibility: Requires Python 3.9+
allowed-tools: Bash(okf.sh:*) Read Write
metadata:
  tags:
    - knowledge
    - documentation
    - okf
    - bundles
---

# okf

Open Knowledge Format (OKF v0.2) bundle management. OKF represents knowledge as a directory of markdown files with YAML frontmatter — readable by humans, parseable by agents, diffable in version control, portable across tools and organizations.

## Overview

An OKF bundle is a directory tree of `.md` files. Each non-reserved file is a *concept* — a unit of knowledge with YAML frontmatter (`type`, `title`, `description`, `sources`, provenance, trust, lifecycle) and a markdown body. Reserved filenames (`index.md`, `log.md`) have special meaning.

The `okf.sh` script implements the document I/O functions referenced by OKF agent prompts (`list-concepts`, `read-doc`, `write-doc`) plus utilities for validation, index generation, link extraction, token estimation, and multi-concept ingestion.

**Document preparation is handled by other skills:** `markdown` converts PDF/Office files to markdown, `webfetch` fetches URLs as markdown, `websearch` finds relevant pages. This skill operates on already-prepared markdown content.

### Design principle: comprehensive coverage

OKF bundles are designed to be usable **without the original source files ever being present again**. When producing content inside a bundle, cover **every aspect** from input files — all tables, numbers, financial data, definitions, procedures, examples, code blocks, lists, and structured content. Do not cover only high-level information. The OKF markdown documents are linked together, allowing agent harnesses to traverse and analyze the full content graph.

It is up to the **LLM** to summarize, format, and transform content. It is up to the **script** to organize the deterministic structure of YAML frontmatter.

### Default behavior

Unless the user specifies otherwise, assume:

- **High fidelity** — preserve all content for all concepts
- **Full coverage** — produce summaries, entity pages, concept pages, comparisons, an overview, and a synthesis. Do not stop at raw extraction; derive value from the content
- **Complete input coverage** — cover every section of the input file. Never skip sections. After producing the bundle, go back and verify every section was covered. If anything was missed, fix it. Only skip sections if the user explicitly requests specific parts
- **Auto-maintenance** — create pages, update them when new sources arrive, maintain cross-references, keep everything consistent. When a new source is added, check existing concepts for overlap and update or cross-link
- **Valid relative paths** — all output file paths are relative and valid. Cross-links and `index.md` links resolve correctly from the linking document's directory
- **Source preservation** — store converted source markdown in `src/` inside the bundle:
  - PDF/Office/Markdown/Text files: same basename (e.g., `ABC.pdf` → `src/ABC.md`)
  - URLs: semantic filename without special characters (e.g., `https://docs.example.com/api-guide` → `src/api-guide.md`)
- **Log updates** — always write and keep `log.md` updated. Record every creation, update, and deprecation with ISO 8601 date headings, newest first

## Bundle Structure

```
bundle/
  index.md                      # Optional: directory listing with progressive disclosure
  log.md                        # Optional: chronological update history
  src/                          # Converted source markdown (preserved for reference)
    ABC.md                      # From ABC.pdf
    quarterly-results.md        # From URL (semantic name, no special chars)
  documents/
    annual-report-2024.md       # Concept: extracted from PDF
    product-spec.md             # Concept: extracted from docx
  references/
    glossary.md                 # Reference: key terms across documents
    acronyms.md                 # Reference: abbreviations and expansions
```

### Concept Documents

Every concept is a UTF-8 markdown file with YAML frontmatter followed by a markdown body. Only `type` is strictly required.

```yaml
---
type: Document                    # REQUIRED
title: Annual Report 2024        # Recommended
description: Q1-Q4 financial and operational results.   # Recommended
resource: https://example.com/reports/annual-2024.pdf
tags: [finance, annual-report, 2024]
sources:
  - id: annual-pdf
    resource: https://example.com/reports/annual-2024.pdf
    title: Annual Report 2024 (PDF)
    author: company:investor-relations
    last_modified: 2025-01-15
    pages: [1, 2, 3, 5, 7-9]
  - id: quarterly-xlsx
    resource: ./data/q4-results.xlsx
    title: Q4 Results
    sheets: [Revenue, Summary]
generated: { by: okf_tool/okf.sh, at: 2025-01-20T10:00:00Z }
verified: { by: human:alice, at: 2025-01-21T09:00:00Z }
status: stable                    # draft | stable | deprecated
stale_after: 2025-12-31
---
```

### Frontmatter Families

| Family | Fields | Purpose |
|--------|--------|---------|
| Core | `type`, `title`, `description`, `resource`, `tags` | Identity and categorization |
| Provenance | `sources`, `usage_window` | Where content derives from |
| Trust | `generated`, `verified` | Who produced/confirmed the content |
| Lifecycle | `status`, `stale_after` | Current state and freshness |

### Cross-linking

Use file-relative paths only — never absolute `/` paths (those break GitHub rendering). The link must resolve from the linking document's directory:

- Sibling: `[budget](budget.md)`
- Parent: `[reports](../reports/overview.md)`
- Reference: `[glossary](../references/glossary.md)`

Only link to concept IDs returned by `okf.sh list-concepts`. One link per concept mention per section. Do not link from headers, fenced code blocks, or schema field names. Do not link a doc to itself.

## Content Processing

When ingesting source material into OKF concept documents, the LLM intelligently parses input markdown and produces clean, well-structured output. The process is lossy — meaning is preserved, verbatim copy is not required — but the result must be able to recreate the original semantically if needed.

### Page-aware processing

Source markdown from PDFs or scanned documents often carries page artifacts:
- Page numbers (`Page 3 of 15`, `— 4 —`, `| 7 |`)
- Page headers/footers repeated on every page
- Content split mid-sentence or mid-table across page boundaries
- Column layouts flattened into linear text

The LLM must:
- **Strip page indicators** — remove page numbers, repeated headers, footers, watermarks
- **Merge split content** — when a paragraph, table, or list spans pages, flow it into continuous text
- **Group coherent content** — find related sections that belong together, even across page breaks
- **Preserve structure** — headings, tables, code blocks, lists, and numbers carry the meaning

### Fidelity levels

The agent controls how much content to preserve. Three levels:

| Level | What to Keep | What to Drop |
|-------|-------------|-------------|
| **high** (default) | Everything — all text, tables, code, lists, examples, numbers | Nothing |
| **medium** | All headings, tables, code blocks, numbers, financial data, lists. Summarized prose. | Nav menus, footers, disclaimers, "read more" links, breadcrumbs, TOC sections |
| **low** | All `#` headings, tables, code blocks, financial data, key terms, standalone numbers | Examples, verbose explanations, secondary details, extra list items (keep 3 + "... and N more") |

**Always preserve** (all levels):
- All headings (document structure)
- All tables and code blocks (verbatim)
- All financial data: currency amounts (`$1.2M`), financial percentages (`revenue grew 15%`), tabular financials, fiscal periods (`FY2024`)
- All numbers that carry standalone meaning (totals, counts, prices, metrics)

**Medium level** — additionally:
- Summarize verbose prose to key sentences (keep sentences with numbers, claims, conclusions)
- Remove boilerplate: navigation, footers, cookie/legal notices, breadcrumbs, table-of-contents

**Low level** — additionally:
- Summarize each section to one sentence capturing its core point
- Remove examples and verbose explanations
- Compact long lists to 3 representative items + "... and N more"

**When in doubt, preserve the data.** Dropping important information is worse than keeping extra tokens.

### Output quality

Every OKF document must be:
- **Non-empty body** — every concept needs body content. If you cannot produce meaningful content, do not create the concept.
- **Language preservation** — each section keeps its source language. Never translate. For filenames: pick the dominant language. If undetermined, fallback to English.
- **Valid markdown** — correct syntax for headings, lists, tables, code blocks, links, footnotes
- **Concise** — no filler, no preamble, no reasoning narration in the body
- **Clean** — no page artifacts, no repeated headers, no boilerplate
- **Well-structured** — logical heading hierarchy, consistent formatting, readable flow
- **Right-sized** — not too long (split via `ingest`), not too short (merge related content)

## CLI Reference

`--bundle` is always the first argument. `--body -` reads from stdin.

```bash
okf.sh create-bundle --bundle ./bundle --version 0.2
okf.sh list-concepts --bundle ./bundle
okf.sh read-doc --bundle ./bundle --concept documents/report --json
okf.sh write-doc --bundle ./bundle --concept documents/report --type Document --body -
okf.sh ingest --bundle ./bundle --file ./large-doc.md --type Document --output-dir documents
okf.sh validate --bundle ./bundle
okf.sh index --bundle ./bundle --output ./bundle/index.md
okf.sh tokens --bundle ./bundle --verbose
```

Full CLI reference with all options and piping examples: [04-cli-reference](references/04-cli-reference.md).

## Typical Workflow

### Processing a PDF or Office Document

1. Convert source to markdown: `markdown.sh to-md ABC.pdf -o ./bundle/src/ABC.md`
2. Create bundle: `okf.sh create-bundle --bundle ./bundle --version 0.2`
3. Read the converted markdown, strip page artifacts, compose clean concept body
4. Write concepts or use `ingest` for large documents:
   ```bash
   cat ./bundle/src/ABC.md | okf.sh ingest --bundle ./bundle --body - --type Document --output-dir documents
   ```
5. Generate overview, synthesis, entity pages, comparisons as needed
6. Validate: `okf.sh validate --bundle ./bundle`

### Processing a URL

1. Fetch the page as markdown: `webfetch.sh fetch https://docs.example.com/api-guide -o ./bundle/src/api-guide.md`
2. Agent reads content, composes concepts
3. Write: `okf.sh write-doc --bundle ./bundle --concept documents/api-guide --type Document --resource "https://docs.example.com/api-guide"`
4. Generate overview, synthesis, entity pages, comparisons as needed

### Piping from webfetch and websearch

```bash
webfetch.sh fetch https://example.com | okf.sh ingest --bundle ./bundle --body - --type Document --output-dir documents --resource "https://example.com"
websearch.sh "query" | okf.sh write-doc --bundle ./bundle --concept references/search --type Reference --body -
```

Always save the fetched source markdown to `src/` before processing. Full piping examples: [04-cli-reference](references/04-cli-reference.md).

### Log files

`log.md` records chronological change history. Always write it and keep it updated — every creation, update, and deprecation goes in. Flat list of date-grouped entries, newest first:

```markdown
# Directory Update Log

## 2025-07-27
* **Update**: Added [Annual Report 2024](documents/annual-report-2024.md) from PDF source.
* **Creation**: Established bundle structure for project knowledge.

## 2025-07-20
* **Initialization**: Created bundle with `okf.sh create-bundle`.
```

Date headings MUST use ISO 8601 `YYYY-MM-DD` form. Leading bold words (`**Update**`, `**Creation**`, `**Deprecation**`) are convention, not requirement. All links in `log.md` use relative paths.

### Enriching an Existing Concept

1. Read: `okf.sh read-doc --bundle ./bundle --concept documents/report --json`
2. Merge new content into the body, preserving all existing headings
3. Update with merged frontmatter (union of existing + new sources/tags):
   ```bash
   cat ./merged-body.md | okf.sh write-doc --bundle ./bundle --concept documents/report --frontmatter-file ./merged-fm.yaml --body -
   ```

### Augmentation Rules

When updating an existing concept:
- **Frontmatter**: pass every existing key. Omitting a key drops it. Only `generated` may be dropped (tool refreshes it). Merge `tags` and `sources` (union, never shrink).
- **Body**: every existing `#` heading must appear in the new body, same order, same wording. Extend prose, add bullets, add new headings *after* existing ones. Never drop or rename existing headings.
- If you cannot honor these rules, mint a `references/<slug>` doc instead and cross-link from the primary doc.

### Sources and per-claim attribution

Record materials a concept derives from in the `sources` frontmatter list. Each entry needs `resource` (required), a stable `id`, and a human-readable `title`. Do not invent URLs.

Always record **where in the source** the content was located — this lets users and agents verify later that the content was really there:
- **PDF/Word**: `pages` — page numbers (e.g., `[1, 2, 3, 5, 7-9]`)
- **Excel**: `sheets` — sheet names (e.g., `[Revenue, Summary]`)
- **URLs**: `resource` is enough (whole page is the source)
- **Local files**: `resource` with path, plus `pages`/`sheets` when applicable

To attribute a specific claim in the body, use a markdown footnote whose label matches a `sources[].id`:

```markdown
Revenue grew 15% year-over-year.[^annual-report]

[^annual-report]: Annual Report 2024
```

The footnote label is the join key into `sources`; consumers resolve attribution through the matching entry. Labels are keyed (not positional) because agents constantly rewrite documents — a stable `id` survives reordering.

### Cross-linking rules

- Use file-relative paths only. Never start with `/` (breaks GitHub rendering).
- Only link to IDs returned by `okf.sh list-concepts`.
- One link per concept mention per section. Do not over-link.
- Do not link from headers, fenced code blocks, or schema field names.
- Do not link a doc to itself.

## Gotchas

- **`type` is the only required frontmatter field** — a concept with just `type` is conformant.
- **Body must never be empty** — if you cannot produce meaningful body content, do not create the concept.
- **Language follows input** — each section keeps its source language. Never translate. For filenames: pick the dominant language. If undetermined, fallback to English.
- **`generated` is auto-filled** — leave it unset and the tool records actor and timestamp.
- **`sources` must not shrink** — when augmenting, merge tags and sources (union, never shrink).
- **Always record source locations** — `pages` for PDF/Word, `sheets` for Excel, `resource` for URLs.
- **Cross-links use relative paths** — `[budget](budget.md)`, not `[budget](/documents/budget.md)`. All output paths must be relative and valid.
- **Footnote labels must match `sources[].id`** — the label `[^my-source]` must correspond to a `sources` entry with `id: my-source`.
- **Reference files need numeric prefixes** — use `01-topic.md`, `02-topic.md` etc.
- **`index.md` and `log.md` are reserved** — cannot be used as concept document names.
- **Always save source markdown to `src/`** — PDF/Office/Text: same basename (`ABC.pdf` → `src/ABC.md`). URLs: semantic name, no special chars (`src/api-guide.md`).
- **URL filenames must be filesystem-safe** — strip special characters, use hyphens, lowercase.
- **Default is high fidelity with full coverage** — produce summaries, entity pages, concept pages, comparisons, overview, and synthesis.
- **Always cover every input section** — never skip. After producing the bundle, verify every section was covered; if anything was missed, fix it. Only skip if the user requests specific parts.
- **Auto-maintain the bundle** — when new sources arrive, check existing concepts for overlap. Update or cross-link.
- **Always write and update `log.md`** — record every creation, update, and deprecation. Date-grouped, newest first.
- **`index.md` uses relative paths** — all links resolve from the index's directory. Never use absolute `/` paths.
- **Page artifacts must be stripped** — page numbers, repeated headers/footers, watermarks. Merge split content across page boundaries.
- **Content is split intelligently** — OKF is lossy but preserves meaning. Result must recreate the original semantically if needed.
- **Documents should be right-sized** — not too long (split via `ingest`), not too short (merge related sections).
- **Always produce valid markdown** — correct heading hierarchy, proper list syntax, well-formed tables, fenced code blocks with language hints, working links and footnotes.
- **`--bundle` is always first argument** — every subcommand takes `--bundle` before other options.
- **`--body -` reads from stdin** — use `-` as the body value to pipe content.
- **`ingest` splits at H1 headings** — each `# Heading` becomes a separate concept.

## References

- [01-okf-spec](references/01-okf-spec.md) — OKF v0.2 specification summary
- [02-reference-agent](references/02-reference-agent.md) — Reference agent prompt and workflow details
- [03-web-ingestion](references/03-web-ingestion.md) — Web ingestion agent prompt and workflow details
- [04-cli-reference](references/04-cli-reference.md) — Full CLI reference with all options and piping examples
