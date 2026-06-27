# CLI Reference

## Prerequisites

The `formulas` CLI requires the `[excel]` extra plus `click-log`:

```bash
pip install formulas[excel]==1.3.4 click-log
```

For the Flask API (`serve` command), also install `flask`:

```bash
pip install flask
```

## Commands Overview

| Command   | Description                                    |
|-----------|------------------------------------------------|
| `calc`    | Calculate workbook, override inputs, render output |
| `build`   | Export workbook to portable JSON model         |
| `test`    | Compare calculated results against reference   |
| `serve`   | Start Flask HTTP API server                    |
| `sheets`  | List sheet names as JSON array                 |

## `formulas calc`

Calculate a workbook and output results as JSON or Excel files.

```bash
formulas calc FILE... [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--overwrite REF=VALUE` | Override a cell value (repeatable) |
| `--batch FILE` | JSON file with multiple run definitions |
| `--out REF` | Limit computation to specific cells (repeatable) |
| `--outs FILE` | JSON file with list of output refs |
| `--render REF=KEY` | Render cell as named key in output (repeatable) |
| `--renders FILE` | JSON file with render specifications |
| `--output-format json\|excel` | Output format (required) |
| `--output-dir DIR` | Output directory for results |
| `--output-file FILE` | Output file for single JSON result |
| `--processes N` | Worker processes for batch (default: 1) |
| `--circular` | Enable circular reference solving |

### Examples

```bash
# Simple calculation, table output
formulas calc workbook.xlsx --output-format json

# Override input and render specific cell
formulas calc workbook.xlsx \
    --overwrite "'[wb.xlsx]Inputs'!B1=200" \
    --render "'[wb.xlsx]Calc'!B3=total" \
    --output-format json

# Save JSON result to file
formulas calc workbook.xlsx \
    --render "'[wb.xlsx]Calc'!B3=total" \
    --output-format json \
    --output-file result.json

# Write calculated Excel file
formulas calc workbook.xlsx \
    --batch batch.json \
    --output-format excel \
    --output-dir ./results

# String value override (use quotes)
formulas calc workbook.xlsx \
    --overwrite "'[wb.xlsx]Sheet'!A1=\"hello\"" \
    --output-format json

# Date override (YYYY-MM-DD format)
formulas calc workbook.xlsx \
    --overwrite "'[wb.xlsx]Sheet'!A1=2024-01-15" \
    --output-format json
```

### Batch Execution

Batch file (`batch.json`):

```json
[
  {
    "name": "base_case",
    "overwrite": {
      "'[wb.xlsx]Inputs'!B1": 100,
      "'[wb.xlsx]Inputs'!B2": 10.0
    },
    "renders": ["'[wb.xlsx]Calc'!B3=total"]
  },
  {
    "name": "stress_test",
    "overwrite": {
      "'[wb.xlsx]Inputs'!B1": 10000,
      "'[wb.xlsx]Inputs'!B2": 50.0
    },
    "renders": ["'[wb.xlsx]Calc'!B3=total"]
  }
]
```

```bash
formulas calc workbook.xlsx \
    --batch batch.json \
    --output-format json \
    --output-dir ./results \
    --processes 4
```

Each run produces a file like `run-0001-base_case.json` in the output directory.

## `formulas build`

Export a workbook to a portable JSON model preserving formulas and values.

```bash
formulas build FILE... [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--out REF` | Keep only specific cells and their dependencies (repeatable) |
| `--outs FILE` | JSON file with list of refs to keep |
| `--output-file FILE` | Write to file instead of stdout |
| `--circular` | Enable circular reference solving |

### Example

```bash
# Full model export
formulas build workbook.xlsx --output-file model.json

# Export only specific outputs and their dependencies
formulas build workbook.xlsx \
    --out "'[wb.xlsx]Calc'!B3" \
    --output-file partial_model.json
```

## `formulas test`

Compare calculated results against a reference workbook.

```bash
formulas test FILE... [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--against FILE` | Reference workbook to compare against (repeatable) |
| `--overwrite REF=VALUE` | Override cells before testing |
| `--out REF` | Limit comparison to specific outputs |
| `--tolerance FLOAT` | Relative tolerance (default: 0.0) |
| `--absolute-tolerance FLOAT` | Absolute tolerance (default: 0.000001) |
| `--summary` | Print summary table before report |
| `--circular` | Enable circular reference solving |

### Example

```bash
# Test workbook against itself
formulas test workbook.xlsx --summary

# Test with tolerance
formulas test model.json \
    --against reference.xlsx \
    --tolerance 0.001 \
    --summary
```

## `formulas serve`

Start a Flask HTTP API server for a workbook.

```bash
formulas serve FILE... [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--host HOST` | Bind address (default: 127.0.0.1) |
| `--port PORT` | Port number (default: 5000) |
| `--circular` | Enable circular reference solving |

### API Endpoints

```
GET  /api/health          — Health check
GET  /api/model           — Model info (files, books, node count)
POST /api/calculate       — Calculate with inputs
```

### Calculate Request

```json
{
  "inputs": {
    "'[wb.xlsx]Sheet'!A1": 42
  },
  "outputs": ["'[wb.xlsx]Sheet'!B1"],
  "renders": ["'[wb.xlsx]Sheet'!C1=result"]
}
```

### Calculate Response

```json
{
  "inputs": {"'[wb.xlsx]Sheet'!A1": 42},
  "outputs": {"result": 84.0},
  "warnings": []
}
```

### Python Integration

```python
from formulas.app import create_app

app = create_app(files=('workbook.xlsx',), circular=False)
# Mount in existing Flask app or run standalone
```

## `formulas-1-3-4.sh sheets`

List sheet names in a workbook as a JSON array of strings. Uses `openpyxl` directly (no formulas calculation needed).

```bash
formulas-1-3-4.sh sheets workbook.xlsx
# Output: ["Sheet1", "Sheet2", "Data"]
```

Useful for discovering sheet names before building cell references or piping into other tools:

```bash
# Pipe to jq for filtering
formulas-1-3-4.sh sheets workbook.xlsx | jq '.[]'

# Use in shell scripts
SHEETS=$(formulas-1-3-4.sh sheets workbook.xlsx)
echo "Workbook has $(echo $SHEETS | jq length) sheets"
```

## Custom Script Commands

The skill's `formulas-1-3-4.sh` wrapper provides additional convenience commands:

```bash
# List sheet names as JSON array
formulas-1-3-4.sh sheets workbook.xlsx
# Output: ["Sheet1", "Data", "Summary"]

# Parse a standalone formula
formulas-1-3-4.sh parse '=SUM(A1:A10)*2' --values 1 2 3

# Show workbook structure
formulas-1-3-4.sh info workbook.xlsx

# Convert calculated workbook to CSV/JSON
formulas-1-3-4.sh convert workbook.xlsx --csv --json --output ./exports

# Build JSON model
formulas-1-3-4.sh build workbook.xlsx --output model.json

# Calculate with overrides
formulas-1-3-4.sh calc workbook.xlsx \
    --overwrite "'[wb.xlsx]Sheet'!A1=42" \
    --format json
```
