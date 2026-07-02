# Path Tools — Kaleido 1.3.0

## Path resolution

Kaleido accepts three forms of path input:

### 1. Full file path

```python
kaleido.write_fig_sync(fig, path="/tmp/output/chart.png")
# Writes to /tmp/output/chart.png
```

Parent directory must exist. If not, `RuntimeError` is raised.

### 2. Directory path

```python
kaleido.write_fig_sync(fig, path="/tmp/output/")
# Auto-generates filename from figure title
# e.g., /tmp/output/My_Chart.png
```

### 3. No path (None)

```python
kaleido.write_fig_sync(fig)
# Defaults to current directory
# Auto-generates filename
```

## Auto-generated filenames

When path is a directory (or None), the filename is derived from the figure title:

### Algorithm

1. Extract `fig.layout.title.text` (or `"fig"` if no title)
2. Replace spaces and dashes with underscores: `" "` → `_`, `"-"` → `_`
3. Strip non-alphanumeric characters (keep `a-z`, `A-Z`, `0-9`, `_`)
4. Truncate to 80 characters
5. Append the format extension (e.g., `.png`)
6. If file exists, append `-N` suffix (incrementing number)

### Examples

| Figure title | Generated filename |
|-------------|-------------------|
| `"Sales Dashboard"` | `Sales_Dashboard.png` |
| `"My (2024) Report!"` | `My_2024_Report.png` |
| `"A" * 100` | `AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA.png` (80 chars) |
| *(no title)* | `fig.png` |

### Numbering for collisions

```python
# First render
kaleido.write_fig_sync(fig, path="./output/")  # → My_Chart.png

# Second render (file exists)
kaleido.write_fig_sync(fig, path="./output/")  # → My_Chart-2.png

# Third render
kaleido.write_fig_sync(fig, path="./output/")  # → My_Chart-3.png
```

The algorithm scans existing files matching the pattern `prefix-*.ext` and finds the highest number.

## URI path support

Paths can be specified as `file://` URIs:

```python
kaleido.write_fig_sync(fig, path="file:///tmp/output/chart.png")
```

The path is parsed with `urllib.parse.urlparse` and converted via `url2pathname`.

## Format detection from path

When `opts["format"]` is not specified, the format is inferred from the path extension:

```python
kaleido.write_fig_sync(fig, path="chart.svg")     # format: svg
kaleido.write_fig_sync(fig, path="chart.pdf")     # format: pdf
kaleido.write_fig_sync(fig, path="chart.jpg")     # format: jpeg
kaleido.write_fig_sync(fig, path="chart")         # format: png (default, no extension)
```

## Path validation

| Condition | Result |
|-----------|--------|
| Path is a file | Used as-is |
| Path is a directory | Auto-generate filename inside it |
| Path has no suffix | Treated as directory |
| Path doesn't exist and isn't a file | `ValueError` if treated as directory |
| Parent of path doesn't exist | `RuntimeError` |

## Path claiming

When writing, Kaleido creates the output file with `Path.touch()` before rendering. This "claims" the filename to prevent race conditions in batch rendering. If rendering fails, the empty file is removed with `Path.unlink()`.
