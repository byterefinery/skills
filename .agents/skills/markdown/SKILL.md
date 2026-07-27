---
name: markdown
description: Converts documents to and from Markdown. Use when the user needs to convert PDF, Word (docx), PowerPoint (pptx), OpenDocument (odt), or Excel (xlsx) files to Markdown, or convert Markdown to PDF or standalone single-file HTML. Handles formula evaluation in Excel before conversion.
allowed-tools: Bash(pandoc:*) Bash(uvx:*)
metadata:
  tags:
    - meta
    - document-conversion
    - markdown
    - pdf
    - office-documents
    - excel
---

# markdown

## Overview

Converts documents to and from Markdown format using `markdown.sh`. Supports conversion from PDF, Word (docx), PowerPoint (pptx), OpenDocument (odt), and Excel (xlsx) to Markdown, and from Markdown to PDF or standalone single-file HTML.

For Excel files, formulas are evaluated before conversion so computed values appear in the output rather than raw formula expressions.

## Usage

### To Markdown

```bash
# Convert any supported document to Markdown
markdown.sh to-md document.docx
markdown.sh to-md presentation.pptx
markdown.sh to-md report.pdf
markdown.sh to-md data.xlsx
markdown.sh to-md spreadsheet.xlsx -o out.md
```

Supported input formats: `.pdf`, `.docx`, `.pptx`, `.odt`, `.xlsx`

Output path defaults to the input filename with `.md` extension. Override with `-o`.

### To PDF

```bash
# Convert Markdown to PDF
markdown.sh to-pdf notes.md
markdown.sh to-pdf notes.md -o result.pdf
```

### To HTML

```bash
# Convert Markdown to standalone single-file HTML
markdown.sh to-html notes.md
markdown.sh to-html notes.md -o result.html
```

The HTML output is self-contained — all CSS, images, and scripts are embedded inline for portability.

## Gotchas

- **Excel: all sheets are converted** — `to-md` on xlsx produces all sheets with no option to select individual ones. Each sheet becomes a `## <sheet-name>` heading followed by a pipe table.
- **Excel: files from some tools may fail** — workbooks created by programs like openpyxl can produce `Entry not found` errors. Files from Excel or LibreOffice work correctly.
- **PDF: requires an external engine** — the default engine needs TeX Live installed. If unavailable, PDF generation will fail.
- **Conversions are not perfectly lossless** — complex formatting, custom styles, and advanced layouts may degrade. Structure is preserved, not presentation details.
- **HTML output can be large** — the standalone single-file HTML embeds all CSS and images as data URIs, increasing file size.
