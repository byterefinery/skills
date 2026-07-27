# CLI Reference

`--bundle` is always the first argument of each subcommand when used. `--body -` reads from stdin.

## Create a Bundle

```bash
okf.sh create-bundle --bundle ./my-bundle --version 0.2 --name "Project Knowledge"
```

## List Concepts

```bash
okf.sh list-concepts --bundle ./bundle
okf.sh list-concepts --bundle ./bundle --json
```

## Read a Concept

```bash
okf.sh read-doc --bundle ./bundle --concept documents/annual-report-2024
okf.sh read-doc --bundle ./bundle --concept documents/annual-report-2024 --frontmatter
okf.sh read-doc --bundle ./bundle --concept documents/annual-report-2024 --body
okf.sh read-doc --bundle ./bundle --concept documents/annual-report-2024 --json
```

## Write a Concept

```bash
# Body from stdin via --body -
cat ./annual-report-2024.md | okf.sh write-doc --bundle ./bundle \
  --concept documents/annual-report-2024 \
  --frontmatter "type: Document
title: Annual Report 2024
description: Q1-Q4 financial and operational results.
tags: [finance, annual-report]" \
  --body -

# Piped from markdown conversion
markdown.sh to-md report.pdf | okf.sh write-doc --bundle ./bundle \
  --concept documents/report \
  --type Document \
  --body -

# Frontmatter from file, body from stdin
okf.sh write-doc --bundle ./bundle \
  --concept documents/product-spec \
  --frontmatter-file fm.yaml \
  --body - < body.md

# Frontmatter from JSON, body from stdin
okf.sh write-doc --bundle ./bundle \
  --concept documents/product-spec \
  --frontmatter '{"type":"Document","title":"Product Spec"}' \
  --json-fm \
  --body - < body.md

# Dry run (print without writing)
okf.sh write-doc --bundle ./bundle --concept documents/whitepaper --type "Document" --dry-run
```

## Ingest Markdown (multi-concept)

Split a large markdown document into multiple OKF concepts based on its heading structure:

```bash
# From file
okf.sh ingest --bundle ./bundle --file ./large-doc.md --type Document

# From stdin
cat ./large-doc.md | okf.sh ingest --bundle ./bundle --body - --type Document

# With output directory prefix
okf.sh ingest --bundle ./bundle --file ./report.md --type Report --output-dir documents

# Dry run
okf.sh ingest --bundle ./bundle --file ./report.md --type Document --dry-run
```

The ingest command:
- Splits the document at `#` (H1) headings into separate concepts
- Generates concept IDs from heading text (lowercase, hyphenated slugs)
- Creates deterministic frontmatter with `type`, `title`, `description`, `sources`
- Cross-links sibling concepts within the bundle
- Preserves all content (tables, numbers, code blocks, lists)

## Validate

```bash
# Validate entire bundle
okf.sh validate --bundle ./bundle
okf.sh validate --bundle ./bundle --verbose

# Validate single file
okf.sh validate --file ./bundle/documents/annual-report-2024.md
```

## Generate Index

```bash
# Print to stdout
okf.sh index --bundle ./bundle

# Write to file
okf.sh index --bundle ./bundle --output ./bundle/index.md
```

## Extract Links

```bash
okf.sh extract-links --file ./bundle/documents/annual-report-2024.md
okf.sh extract-links --file ./bundle/documents/annual-report-2024.md --json
```

## Estimate Tokens

```bash
okf.sh tokens --file ./bundle/documents/annual-report-2024.md
okf.sh tokens --bundle ./bundle --verbose
```

## Piping from webfetch and websearch

`--body -` accepts stdin from any source — pipe directly from `webfetch.sh` and `websearch.sh`:

```bash
# Fetch a URL and ingest directly into bundle
webfetch.sh fetch https://example.com | okf.sh ingest --bundle ./bundle --body - --type Document --output-dir documents --resource "https://example.com" --title "Example"

# Fetch a GitHub repo page
webfetch.sh fetch https://github.com/user/repo | okf.sh write-doc --bundle ./bundle --concept references/repo --type Reference --body -

# Search the web and ingest results
websearch.sh "search query" | okf.sh write-doc --bundle ./bundle --concept references/search-results --type Reference --body -

# Multiple URLs into one bundle
for url in https://example.com https://docs.example.com; do
  webfetch.sh fetch "$url" | okf.sh ingest --bundle ./bundle --body - --type Document --output-dir documents --resource "$url"
done

# Chain: search → fetch top results → ingest
websearch.sh "documentation" --format json | \
  python3 -c "import json,sys; [print(r['url']) for r in json.load(sys.stdin)[:3]]" | \
  while read url; do
    webfetch.sh fetch "$url" | okf.sh ingest --bundle ./bundle --body - --type Document --output-dir documents --resource "$url"
  done
```
