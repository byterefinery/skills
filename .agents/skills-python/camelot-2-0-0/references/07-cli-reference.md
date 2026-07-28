# CLI Reference

Command-line interface for Camelot. Two entry points: `camelot` and `camelot-py` (alias matching the PyPI package name).

## Basic Usage

```bash
# Help
camelot --help
camelot lattice --help
camelot stream --help

# Ad-hoc (no install)
uvx camelot-py lattice --output tables.csv document.pdf
```

## Subcommands

### lattice

Parse tables with ruled grid lines:

```bash
camelot lattice [OPTIONS] FILEPATH
```

**Options:**

| Short | Long | Description |
|-------|------|-------------|
| `-q` | `--quiet` | Suppress logs and warnings |
| `-p` | `--pages` | Comma-separated page numbers (default: 1) |
| `--parallel` | | Process pages in parallel |
| `-pw` | `--password` | Encryption password |
| `-o` | `--output` | Output file path (template) |
| `-f` | `--format` | Output format: csv, excel, html, json, markdown, sqlite |
| `-z` | `--zip` | Create ZIP archive |
| `-split` | `--split_text` | Split merged text across cells |
| `-flag` | `--flag_size` | Flag superscripts/subscripts |
| `-strip` | `--strip_text` | Characters to strip |
| `-M` | `--margins` | PDFMiner char_margin, line_margin, word_margin |
| `-R` | `--table_regions` | Page regions to analyze (x1,y1,x2,y2) |
| `-T` | `--table_areas` | Table areas to process (x1,y1,x2,y2) |
| `-back` | `--process_background` | Process background lines |
| `-scale` | `--line_scale` | Line detection threshold (default: 15) |
| `-copy` | `--copy_text` | Copy spanning text: h, v |
| `-shift` | `--shift_text` | Text gravity: l, r, t, b |
| `-l` | `--line_tol` | Line merge tolerance (default: 2) |
| `-j` | `--joint_tol` | Joint proximity tolerance (default: 2) |
| `-block` | `--threshold_blocksize` | Adaptive threshold block size (default: 15) |
| `-const` | `--threshold_constant` | Adaptive threshold constant (default: -2) |
| `-I` | `--iterations` | Dilation passes |
| `-res` | `--resolution` | PDF-to-PNG DPI (default: 300) |
| `-plot` | `--plot_type` | Visual debug: text, grid, contour, joint, line |

### stream

Parse borderless tables via whitespace:

```bash
camelot stream [OPTIONS] FILEPATH
```

Same options as lattice, plus:

| Short | Long | Description |
|-------|------|-------------|
| `-C` | `--columns` | Column x-coordinates |
| `-e` | `--edge_tol` | Textedge extension tolerance (default: 50) |
| `-r` | `--row_tol` | Vertical row grouping tolerance (default: 2) |
| `-c` | `--column_tol` | Horizontal column grouping tolerance (default: 0) |

Plot types: `text`, `grid`, `contour`, `textedge`.

### network

Parse tables via text alignment connectivity:

```bash
camelot network [OPTIONS] FILEPATH
```

Same options as stream. Plot types: `text`, `grid`, `contour`, `textedge`.

### hybrid

Combined network + lattice parsing:

```bash
camelot hybrid [OPTIONS] FILEPATH
```

Same options as stream. Plot types: `text`, `grid`, `contour`, `textedge`.

## Examples

```bash
# Basic lattice extraction
camelot lattice --output tables.csv report.pdf

# Specific pages
camelot lattice -p 1,3,5 --output tables.csv report.pdf

# All pages, compressed
camelot lattice -p all -z --output tables.csv report.pdf

# Stream with column hints
camelot stream -C 72,95,209,327 --output tables.csv report.pdf

# Visual debugging
camelot lattice -plot grid report.pdf
camelot stream -plot textedge report.pdf

# Background lines
camelot lattice -back --output tables.csv report.pdf

# Custom line scale
camelot lattice -scale 40 --output tables.csv report.pdf

# Format inference from extension
camelot lattice --output tables.xlsx report.pdf
camelot lattice --output tables.json report.pdf
```

## Output Format Inference

When `--format` is omitted, Camelot infers from the `--output` extension:

| Extension | Format |
|-----------|--------|
| `.csv` | csv |
| `.xlsx`, `.xls` | excel |
| `.html`, `.htm` | html |
| `.json` | json |
| `.md`, `.markdown` | markdown |
| `.sqlite`, `.sqlite3`, `.db` | sqlite |

## Output Template

`--output` is treated as a template. Each table is written to `<stem>-page-<P>-table-<T>.<ext>`:

```bash
camelot lattice --output report.csv document.pdf
# Produces: report-page-1-table-1.csv, report-page-1-table-2.csv, ...
```

Use `-z`/`--zip` to compress into a single ZIP file.
