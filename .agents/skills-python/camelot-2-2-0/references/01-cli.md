# camelot CLI (v2.2.0)

The console script is `camelot` (PyPI package name `camelot-py`; a `camelot-py` alias also works). Run ad-hoc without installing via `uvx camelot-py <command> ...`. Print help with `camelot --help` and `camelot <command> --help`.

## Commands

One subcommand per flavor: `lattice`, `stream`, `hybrid`, `network`. Each takes a positional `filepath` (must exist) plus the options below. There is no `ml` or `auto` CLI command — those are Python-API-only flavors.

## Common options (all commands)

| Option | Description |
|---|---|
| `-q, --quiet` | Suppress logs and warnings |
| `--pages` | Comma-separated page numbers; example `1,3,4`, `1,4-end`, or `all` |
| `--parallel` | Read PDF pages in parallel using all CPU cores |
| `-pw, --password` | Password for decryption |
| `-o, --output` | Output file path. Treated as a **template** — each detected table is written to `<stem>-page-<P>-table-<T>.<ext>` |
| `-f, --format` | Output format (`csv`, `json`, `excel`, `html`, `markdown`, `sqlite`). Optional — inferred from the `--output` extension when omitted |
| `-z, --zip` | Create a ZIP archive of all output files |

### Format inference table

| Extension | Format |
|---|---|
| `.csv` | csv |
| `.xlsx` / `.xls` | excel |
| `.html` / `.htm` | html |
| `.json` | json |
| `.md` / `.markdown` | markdown |
| `.sqlite` / `.sqlite3` / `.db` | sqlite |

## `lattice` options

For ruled tables. Lattice-specific tuning:

| Option | Description |
|---|---|
| `-back, --process_background` | Process background lines (flag) |
| `--line_scale` | Line size scaling factor; larger → smaller detected lines |
| `--copy_text` | Direction in which text in a spanning cell is copied over (`v`, `h`) |
| `--shift_text` | Direction in which text in a spanning cell flows (`l`, `r`, `t`, `b`) |
| `--line_tol` | Tolerance to merge close vertical/horizontal lines (default 2) |
| `--joint_tol` | Tolerance for detected lines/points lying close together (default 2) |
| `--threshold_blocksize` | OpenCV adaptiveThreshold neighborhood size (default 15) |
| `--threshold_constant` | OpenCV adaptiveThreshold constant (default -2) |
| `--iterations` | Number of dilation passes to close line gaps (default 0) |
| `--resolution` | Resolution for PDF→PNG conversion (default 300) |

Also accepts the stream-side options (`-T/--table_areas`, `-C/--columns`, `--split_text`, `--flag_size`, `--strip_text`) where applicable, plus `--margins` (PDFMiner char/line/word margins).

## `stream` options

For borderless whitespace-aligned tables:

| Option | Description |
|---|---|
| `-T, --table_areas` | Table areas to process; `x1,y1,x2,y2` where (x1,y1) → left-top, (x2,y2) → right-bottom (PDF coordinate space). Repeatable/multiple |
| `-C, --columns` | X coordinates of column separators (comma-separated). Repeatable/multiple |
| `-e, --edge_tol` | Tolerance for extending textedges vertically (default 50) |
| `-r, --row_tol` | Tolerance to combine text vertically into rows (default 2) |
| `-c, --column_tol` | Tolerance to combine text horizontally into columns (default 0) |
| `--split_text` | Split text spanning multiple cells |
| `--flag_size` | Flag super/subscripts by font size (adds `<s></s>`) |
| `--strip_text` | Characters to strip from each cell |
| `--margins` | PDFMiner char_margin, line_margin, word_margin |
| `-R, --table_regions` | Page regions to analyze; `x1,y1,x2,y2` |

## `hybrid` / `network` options

Same option surface as stream plus the lattice tuning options (`--process_background`, `--line_scale`, `--copy_text`, `--shift_text`, `--line_tol`, `--joint_tol`, `--iterations`, `--resolution`) — hybrid accepts both kwarg families.

## Visual debugging flag

`-plot, --plot_type` (also `--plot_type`) plots detected elements instead of exporting. Choices: `text`, `grid`, `contour`, `line`, `joint`, `textedge`. (`line`/`joint` lattice-only; `textedge` stream-only.)

## Examples

```bash
# Basic lattice extraction to CSV (format inferred from .csv)
camelot --format csv --output foo.csv lattice foo.pdf

# Specific pages, parallel
camelot --pages 1,2,3 lattice your.pdf

# Encrypted PDF
camelot --password userpass lattice foo.pdf

# Stream with explicit table area and column separators
camelot stream -T 316,499,566,337 table_areas.pdf
camelot stream -C 72,95,209,327,442,529,566,606,683 column_separators.pdf

# Lattice with table region and plot for debugging
camelot lattice -R 170,370,560,270 table_regions.pdf
camelot lattice -plot grid foo.pdf

# ZIP all outputs
camelot -z --output out.zip lattice big.pdf
```
