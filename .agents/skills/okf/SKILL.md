---
name: okf
description: Creates, validates, and manages Open Knowledge Format (OKF) bundles — directory trees of markdown concept documents with YAML frontmatter. Use when the user needs to create a knowledge bundle from PDF, Office, or web sources; write or update concept documents; validate OKF conformance; generate index files; or manage cross-links between concepts. Relies on `webfetch`, `websearch`, and `markdown` skills for document preparation.
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

Open Knowledge Format (OKF v0.2) bundle management. OKF represents knowledge as a directory of markdown files with YAML frontmatter — readable by humans, parseable by agents, diffable in version control, portable across tools.

## Overview

An OKF bundle is a directory tree of `.md` files. Each non-reserved file is a *concept* — a unit of knowledge with YAML frontmatter (type, title, description, sources, provenance, trust, lifecycle) and a markdown body. Reserved filenames (`index.md`, `log.md`) have special meaning.

The `okf.sh` script implements the document I/O functions referenced by OKF agent prompts (`list_concepts`, `read_existing_doc`, `write_concept_doc`) plus utilities for validation, index generation, and link extraction.

Document preparation is handled by other skills: `markdown` converts PDF/Office files to markdown, `webfetch` fetches URLs as markdown, `websearch` finds relevant pages. This skill operates on already-prepared markdown content.

## Bundle Structure

```
bundle/
  index.md                      # Optional: directory listing with progressive disclosure
  log.md                        # Optional: chronological update history
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

Use file-relative paths (not absolute `/` paths) for links between concepts:

- Sibling: `[budget](budget.md)`
- Parent: `[reports](../reports/overview.md)`
- Reference: `[glossary](../references/glossary.md)`

## Usage

### Create a Bundle

```bash
okf.sh create-bundle ./my-bundle --version 0.2 --name "Project Knowledge"
```

### List Concepts

```bash
okf.sh list ./bundle
okf.sh list ./bundle --json
```

### Read a Concept

```bash
okf.sh read documents/annual-report-2024 --bundle ./bundle
okf.sh read documents/annual-report-2024 --bundle ./bundle --frontmatter
okf.sh read documents/annual-report-2024 --bundle ./bundle --body
okf.sh read documents/annual-report-2024 --bundle ./bundle --json
```

### Write a Concept

```bash
# Body from stdin via --body -
cat ./annual-report-2024.md | okf.sh write documents/annual-report-2024 \
  --bundle ./bundle \
  --frontmatter "type: Document
title: Annual Report 2024
description: Q1-Q4 financial and operational results.
tags: [finance, annual-report]" \
  --body - \
 

# Piped from markdown.sh
markdown.sh to-md report.pdf | okf.sh write documents/report \
  --bundle ./bundle \
  --type Document \
  --body-stdin \
 

# Frontmatter from file, body from stdin
okf.sh write documents/product-spec \
  --bundle ./bundle \
  --frontmatter-file fm.yaml \
  --body - < body.md

# Frontmatter from JSON, body from stdin
okf.sh write documents/product-spec \
  --bundle ./bundle \
  --frontmatter '{"type":"Document","title":"Product Spec"}' \
  --json-fm \
  --body - < body.md

# Dry run (print without writing)
okf.sh write documents/whitepaper --bundle ./bundle --type "Document" --dry-run
```

### Validate

```bash
# Validate entire bundle
okf.sh validate ./bundle
okf.sh validate ./bundle --verbose

# Validate single file
okf.sh validate --file ./bundle/documents/annual-report-2024.md
```

### Generate Index

```bash
# Print to stdout
okf.sh index --bundle ./bundle

# Write to file
okf.sh index --bundle ./bundle --output ./bundle/index.md
```

### Extract Links

```bash
okf.sh extract-links --file ./bundle/documents/annual-report-2024.md
okf.sh extract-links --file ./bundle/documents/annual-report-2024.md --json
```

### Estimate Tokens

```bash
okf.sh tokens --file ./bundle/documents/annual-report-2024.md
okf.sh tokens --bundle ./bundle --verbose
```

## Typical Workflow

### Processing a PDF or Office Document

1. Convert the source file to markdown using `markdown.sh to-md`:
   ```bash
   markdown.sh to-md annual-report.pdf -o ./tmp/annual-report.md
   ```
2. Create the bundle:
   ```bash
   okf.sh create-bundle ./bundle --version 0.2
   ```
3. Write the concept, piping the converted body:
   ```bash
   markdown.sh to-md annual-report.pdf | okf.sh write documents/annual-report \
     --bundle ./bundle \
     --frontmatter "type: Document
title: Annual Report 2024
description: Financial and operational results.
tags: [finance]
sources:
  - id: source-pdf
    resource: annual-report.pdf
    title: Annual Report 2024" \
     --body-stdin
   ```
4. Validate:
   ```bash
   okf.sh validate ./bundle
   ```

### Processing a URL

1. Fetch the page as markdown using `webfetch`
2. Write the concept, piping the fetched content:
   ```bash
   # webfetch outputs markdown to stdout, pipe it:
   okf.sh write documents/api-guide \
     --bundle ./bundle \
     --frontmatter "type: Document
title: API Guide
description: Official API usage guide.
resource: https://docs.example.com/api-guide
sources:
  - id: api-docs
    resource: https://docs.example.com/api-guide
    title: API Guide" \
     --body-stdin
   ```

### Enriching an Existing Concept

1. Read the existing document:
   ```bash
   okf.sh read documents/annual-report --bundle ./bundle --json
   ```
2. Merge new content into the body, preserving all existing headings
3. Update with merged frontmatter (union of existing + new sources/tags):
   ```bash
   cat ./merged-body.md | okf.sh write documents/annual-report \
     --bundle ./bundle \
     --frontmatter-file ./merged-fm.yaml \
     --body-stdin
   ```

### Augmentation Rules

When updating an existing concept:
- **Frontmatter**: pass every existing key. Omitting a key drops it. Only `generated` may be dropped (tool refreshes it). Merge `tags` and `sources` (union, never shrink).
- **Body**: every existing `#` heading must appear in the new body, same order, same wording. Extend prose, add bullets, add new headings *after* existing ones. Never drop or rename existing headings.
- If you cannot honor these rules, mint a `references/<slug>` doc instead and cross-link from the primary doc.

### Cross-linking Rules

- Use file-relative paths only. Never start with `/`.
- Only link to IDs returned by `okf.sh list`.
- One link per concept mention per section.
- Do not link from headers, fenced code blocks, or schema field names.
- Do not link a doc to itself.

## Gotchas

- **`type` is the only required frontmatter field** — a concept with just `type` is conformant. All other fields are optional. Their absence carries meaning (unverified ≠ rejected).
- **`generated` is auto-filled** — leave it unset in your frontmatter and the tool records actor and timestamp. Only override if you need a specific value.
- **`sources` must not shrink** — when augmenting, always include existing sources plus new ones. The validator catches missing entries.
- **Cross-links use relative paths** — `[budget](budget.md)`, not `[budget](/documents/budget.md)`. Absolute paths break GitHub rendering.
- **Reference files need numeric prefixes for ordering** — use `01-topic.md`, `02-topic.md` etc. when a references directory has many files.
- **`index.md` and `log.md` are reserved** — they cannot be used as concept document names. The tool skips them in `list` output.
- **YAML frontmatter is parsed with a stdlib-only subset parser** — it handles mappings, lists, inline `{maps}` and `[lists]`, quoted strings, and scalars. It does NOT handle multi-line strings (`|`, `>`), anchors (`&`, `*`), or tags beyond `!!str`/`!!float`/`!!int`/`!!bool`.
- **Trust tiers are derived, not stored** — `unverified` (no `verified`), `machine-confirmed` (non-`human:` actors only), `human-reviewed` (has `human:` actor). The tool does not compute tiers; this is for the consuming agent.
- **Actor convention** — use `<producer>/<version>` for tools, `human:<id>` for people, `process:<id>` for automated processes. Trust tier derivation keys off the `human:` prefix.
- **Document conversion is not this skill's job** — use `markdown.sh to-md` for PDF/Office files, `webfetch` for URLs. This skill only manages the resulting OKF bundle.

## References

- [01-okf-spec](references/01-okf-spec.md) — OKF v0.2 specification summary
- [02-reference-agent](references/02-reference-agent.md) — Reference agent prompt and workflow details
- [03-web-ingestion](references/03-web-ingestion.md) — Web ingestion agent prompt and workflow details
