# Metadata and YAML Reference

Pandoc extracts metadata from documents and makes it available to templates, filters, and output formats.

## YAML Metadata Blocks

Place a YAML block at the beginning (or end) of the document, delimited by `---`:

```yaml
---
title: "My Document"
author:
  - "Jane Doe"
  - "John Smith"
date: "2024-01-15"
abstract: |
  This is a multi-line abstract.
  It preserves line breaks.
subtitle: "A Comprehensive Guide"
keywords:
  - pandoc
  - markdown
  - documentation
---

# Document Content

The body starts here...
```

### Metadata Block Position

- **Beginning**: Must be at the very start of the file, preceded only by optional BOM
- **End**: Can also appear at the end of the document (useful for appending metadata)
- Both positions can be used simultaneously; they are merged

### Supported Formats

YAML metadata blocks are supported in: `markdown`, `rst`, `latex`, `html`, `org`, `ipynb`.

## Common Metadata Fields

### Document Identification

| Field | Type | Description |
|---|---|---|
| `title` | String | Document title |
| `subtitle` | String | Subtitle |
| `author` | String or list | Author name(s) |
| `date` | String | Document date (ISO 8601: `YYYY-MM-DD`) |
| `lang` | String | Document language (`en`, `de`, `fr`) |
| `abstract` | String | Abstract/summary |
| `keywords` | List | Search keywords |
| `identifier` | String | Document ID (e.g., DOI, ISBN) |
| `rights` | String | Copyright notice |

### Formatting Variables

| Field | Type | Description |
|---|---|---|
| `documentclass` | String | LaTeX document class |
| `classoption` | String or list | Class options |
| `fontsize` | String | Base font size (`10pt`, `11pt`, `12pt`) |
| `mainfont` | String | Main serif font (xelatex/lualatex) |
| `sansfont` | String | Sans-serif font |
| `monofont` | String | Monospace font |
| `geometry` | String or list | Page geometry options |
| `linestretch` | Number | Line spacing multiplier |
| `colorlinks` | Boolean | Colored hyperlinks |
| `linkcolor` | String | Internal link color |
| `urlcolor` | String | URL color |
| `toc` | Boolean | Table of contents |
| `toc-depth` | Number | TOC heading depth |
| `number-sections` | Boolean | Numbered sections |
| `number-lines` | Boolean | Line numbers (code blocks) |

### Citation/Bibliography

| Field | Type | Description |
|---|---|---|
| `bibliography` | String or list | Bibliography file path(s) |
| `csl` | String | CSL style file path/URL |
| `citation-abbreviations` | String | Abbreviations JSON file |
| `references` | List | Inline bibliography entries (CSL-JSON format) |
| `nocite` | String | Include all citations (`@*`) or specific ones |

### HTML-Specific

| Field | Type | Description |
|---|---|---|
| `header-includes` | List | Raw HTML for `<head>` |
| `footer-includes` | List | Raw HTML before `</body>` |
| `css` | String or list | CSS file paths/URLs |
| `highlight-style` | String | Syntax highlighting theme |
| `theme` | String | Beamer/reveal.js theme |

### Complete Example

```yaml
---
title: "Annual Report 2024"
author:
  - "Jane Doe"
  - "John Smith"
date: "2024-12-31"
lang: en
abstract: |
  This report summarizes our findings
  from the fiscal year 2024.
subtitle: "Fiscal Year Summary"
documentclass: report
fontsize: 11pt
geometry: margin=1in
linestretch: 1.5
toc: true
toc-depth: 3
number-sections: true
colorlinks: true
linkcolor: "#0066cc"
bibliography:
  - references.bib
  - online-sources.json
csl: https://zotero.org/styles/apa
header-includes: |
  <style>
    .highlight { background-color: #ffffcc; }
  </style>
---
```

## Metadata via Command Line

### `-M` / `--metadata`

Set individual metadata variables:

```bash
# Single variable
pandoc -M title="My Title" input.md -o output.html

# Multiple variables
pandoc -M title="Report" -M author="Jane" -M date="2024-01-15" input.md

# Boolean
pandoc -M toc=true input.md

# Overriding document metadata
pandoc -M title="Override Title" input.md  # overrides YAML block
```

### `-m` / `--metadata-file`

Load metadata from a YAML file:

```yaml
# meta.yaml
title: "My Document"
author: "Jane Doe"
date: "2024-01-15"
```

```bash
pandoc -m meta.yaml input.md -o output.html
```

### `-V` / `--variable`

Set template variables (similar to `-M` but for templates specifically):

```bash
# Template variable
pandoc -V documentclass=report input.md -o output.tex

# With spaces (quote the value)
pandoc -V geometry:"margin=1in,landscape" input.md

# Multiple values
pandoc -V classoption="11pt,a4paper" input.md
```

## Metadata Merging Priority

When metadata comes from multiple sources, the priority is:

1. **Command-line `-M`** (highest priority)
2. **Command-line `-V`**
3. **Metadata file (`-m`)**
4. **YAML metadata block in document**
5. **Defaults file metadata**
6. **Automatic defaults** (lowest priority)

Later sources override earlier ones for scalar values. List values are appended unless overridden completely.

## Automatic Variables

Pandoc sets some variables automatically:

| Variable | Source |
|---|---|
| `title` | First top-level heading or YAML `title` |
| `author` | YAML `author` or inferred |
| `date` | YAML `date` or file modification date |
| `source` | Input filename |
| `output-file` | Output filename |
| `mainlang` | Primary language from `lang` |
| `title-prefix` | From `-T` option |
| `doc-css` | Default document CSS |
| `highlight-macro` | Syntax highlighting setup |

## TOML and JSON Metadata

Besides YAML, pandoc supports TOML and JSON metadata blocks:

### TOML

```toml
+++
title = "My Document"
author = ["Jane Doe", "John Smith"]
date = "2024-01-15"
+++
```

### JSON

```json
{
  "title": "My Document",
  "author": ["Jane Doe", "John Smith"],
  "date": "2024-01-15"
}
```

Enable with extensions: `+toml_metadata_block` or `+json_metadata_block`.

## Metadata in Filters

Access metadata in Lua filters:

```lua
function Pandoc(doc)
  local title = doc.meta.title
  local author = doc.meta.author
  -- Modify metadata
  doc.meta.custom_field = "value"
  return doc
end
```

Access in JSON filters (root of AST):

```json
{
  "type": "Pandoc",
  "meta": {
    "title": {"t": "Str", "c": ["My Document"]},
    "author": [...]
  },
  "blocks": [...]
}
```

## Gotchas

- **YAML indentation matters** — use 2 spaces, not tabs
- **Multiline strings**: use `|` (literal, preserves newlines) or `>` (folded, newlines become spaces)
- **Date format**: ISO 8601 (`YYYY-MM-DD`) is most portable; other formats depend on output format
- **Boolean values**: `true`/`false` in YAML, not `"true"`/`"false"` strings
- **List vs. string**: `author: "Jane Doe"` (string) vs. `author: [Jane, John]` (list) affects template rendering
- **Command-line `-M` overrides document metadata** — use this intentionally for batch processing
