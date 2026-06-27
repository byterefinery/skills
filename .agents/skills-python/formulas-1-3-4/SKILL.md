---
name: formulas-1-3-4
description: Evaluate Excel formulas in Python without Excel. Use when the user needs to compute spreadsheet formulas, calculate xlsx files, convert formula-based spreadsheets to calculated values, export Excel to CSV/JSON, run batch scenarios, build JSON models from workbooks, or serve spreadsheets as a Flask API. Also triggers on mentions of formulas package, openpyxl calculation, or spreadsheet automation.
---

# formulas 1.3.4

## Overview

`formulas` is a Python package that parses, compiles, and executes Excel formulas without requiring Excel or the COM server. It supports 645+ built-in functions (90%+ coverage of standard Excel functions across Math, Statistical, Financial, Date/Time, Engineering, Text, Logical, Lookup categories), multi-sheet workbooks with cross-sheet references, named ranges, circular reference solving, JSON model export/import, and a CLI for batch computation.

Install with `pip install formulas[excel]==1.3.4` (requires `openpyxl`, `numpy`, `schedula`). The `[excel]` extra enables workbook loading via `ExcelModel`.

### Core API

- **`formulas.ExcelModel()`** — Load, calculate, and write workbooks
- **`formulas.Parser()`** — Parse standalone formula strings into callable functions
- **`formulas.get_functions()`** — Dict of 645+ Excel function implementations; extendable with custom functions
- **`formulas.Ranges`** — Represents cell/range values as numpy-backed arrays

### CLI Commands

- **`formulas calc`** — Calculate workbook(s), optionally overriding inputs and rendering outputs as JSON or Excel
- **`formulas build`** — Export a workbook to a portable JSON model (cells + formulas preserved)
- **`formulas test`** — Compare calculated results against a reference workbook
- **`formulas serve`** — Expose a workbook as a Flask HTTP API (`/api/calculate`, `/api/model`, `/api/health`)

## Usage

### Python API — Calculate a Workbook

```python
import formulas

model = formulas.ExcelModel().loads('workbook.xlsx').finish()
solution = model.calculate()

# Read a cell value
val = solution["'[workbook.xlsx]Sheet1'!A1"].value[0, 0]
```

### Python API — Overwrite Inputs, Compute Specific Outputs

```python
solution = model.calculate(
    inputs={
        "'[wb.xlsx]Inputs'!B1": 200,   # Override default input
        "'[wb.xlsx]Inputs'!B3": 0.15,  # Override tax rate
    },
    outputs=["'[wb.xlsx]Calc'!B3"],     # Only compute these cells
)
```

### Python API — Compile as Reusable Function

```python
func = model.compile(
    inputs=["'[wb.xlsx]Inputs'!B1", "'[wb.xlsx]Inputs'!B2"],
    outputs=["'[wb.xlsx]Calc'!B3"],
)
result = func(200, 30.0)  # Returns Ranges object
value = result.value[0, 0]  # Scalar value
```

### Python API — JSON Export/Import (Portable Model)

```python
# Export workbook to JSON-serializable dict
model_dict = model.to_dict()
# Save to file
import json
with open('model.json', 'w') as f:
    json.dump(model_dict, f, indent=2)

# Reload from JSON and recalculate
with open('model.json') as f:
    loaded = formulas.ExcelModel().from_dict(json.load(f))
solution = loaded.calculate()
```

### Python API — Write Calculated Workbook (Formulas Replaced with Values)

```python
model = formulas.ExcelModel().loads('workbook.xlsx').finish()
solution = model.calculate()
books = model.write(dirpath='/output/dir')  # Saves .xlsx with computed values
```

The `write()` method creates new `.xlsx` files where all formula cells are replaced with their calculated values. The output filename is the uppercase workbook name (e.g., `WORKBOOK.XLSX`).

### Python API — Extract Submodel from Output Cells

```python
xl = formulas.ExcelModel().from_ranges(
    "'[wb.xlsx]Calc'!B3",  # Start from this output cell
)
# Automatically traces all dependencies backward
solution = xl.dsp.dispatch()
```

### Python API — Parse Standalone Formulas

```python
func = formulas.Parser().ast('=(1 + 1) + B3 / A2')[1].compile()
inputs = list(func.inputs)  # ['A2', 'B3']
result = func(1, 5)          # Array(7.0, dtype=object)
```

### Python API — Add Custom Functions

```python
FUNCTIONS = formulas.get_functions()
FUNCTIONS['MYFUNC'] = lambda x, y: x + y
func = formulas.Parser().ast('=MYFUNC(1, 2)')[1].compile()
result = func()  # 3
```

### Python API — Circular References

```python
# Enable circular reference solving
model = formulas.ExcelModel().loads('wb.xlsx').finish(circular=True)
solution = model.calculate()
# Circular cells resolve to 0 (or custom iteration)
```

### CLI — Calculate with Input Override

```bash
formulas calc workbook.xlsx \
    --overwrite "'[wb.xlsx]Inputs'!B1=200" \
    --render "'[wb.xlsx]Calc'!B3=total" \
    --output-format json
```

### CLI — Batch Execution

```json
// batch.json
[
  {
    "name": "scenario_a",
    "overwrite": {
      "'[wb.xlsx]Inputs'!B1": 100,
      "'[wb.xlsx]Inputs'!B2": 10.0
    },
    "renders": ["'[wb.xlsx]Calc'!B3=total"]
  },
  {
    "name": "scenario_b",
    "overwrite": {
      "'[wb.xlsx]Inputs'!B1": 200,
      "'[wb.xlsx]Inputs'!B2": 5.0
    },
    "renders": ["'[wb.xlsx]Calc'!B3=total"]
  }
]
```

```bash
formulas calc workbook.xlsx \
    --batch batch.json \
    --output-format json \
    --output-dir ./results
```

### CLI — Build JSON Model

```bash
formulas build workbook.xlsx --output-file model.json
```

### CLI — List Sheet Names

```bash
formulas-1-3-4.sh sheets workbook.xlsx
# Output: ["Sheet1", "Sheet2", "Data"]
```

### CLI — List Sheet Names

```bash
formulas-1-3-4.sh sheets workbook.xlsx
# Output: ["Sheet1", "Data", "Summary"]
```

### CLI — Test Against Reference

```bash
formulas test workbook.xlsx --summary
```

### Flask API Integration

```python
from formulas.app import create_app

app = create_app(files=('workbook.xlsx',), circular=False)
# POST /api/calculate with JSON body:
# {"inputs": {"'[wb.xlsx]Sheet'!A1": 42}, "renders": ["'[wb.xlsx]Sheet'!B1=result"]}
```

### Convert Calculated Workbook to CSV/JSON

`formulas` writes calculated `.xlsx` files via `model.write()`. To export as CSV or JSON, read the calculated workbook with `openpyxl` and transform:

```python
from openpyxl import load_workbook
import csv, json

# After model.calculate() + model.write(dirpath='/out')
wb = load_workbook('/out/WORKBOOK.XLSX', data_only=True)
for ws in wb.worksheets:
    # CSV
    with open(f'{ws.title}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        for row in ws.iter_rows(values_only=True):
            writer.writerow(list(row))

    # JSON (first row as headers)
    rows = list(ws.iter_rows(values_only=True))
    headers = [v or f'col_{i}' for i, v in enumerate(rows[0])]
    data = [{headers[j]: row[j] for j in range(len(headers))}
            for row in rows[1:] if any(v is not None for v in row)]
    with open(f'{ws.title}.json', 'w') as f:
        json.dump(data, f, indent=2)
```

## Gotchas

- **`formulas[excel]` extra is required** — Base `pip install formulas` does not include `openpyxl` or workbook loading. Use `pip install formulas[excel]==1.3.4`.
- **CLI needs `click-log`** — The CLI entry point imports `click_log` which is not in the base requirements. Install with `pip install click-log` or use `pip install formulas[all]`.
- **Cell references use full qualified names** — References are `'[filename.xlsx]SheetName'!A1` (uppercase sheet, single quotes around book+sheet). Use `model.to_dict()` keys to discover correct reference strings.
- **`compile()` returns a `DispatchPipe`, not a simple function** — Call it with positional args matching the `inputs` list order. The return is a `Ranges` object; access scalar via `.value[0, 0]`.
- **`write()` replaces formulas with values** — The output workbook has no formula cells (`data_type` changed from `'f'` to `'s'`). This is the intended behavior for "calculated snapshot" exports.
- **Output filename is uppercase** — `model.write(dirpath='/out')` saves as `WORKBOOK.XLSX` (uppercase). Read back with exact case.
- **Circular references resolve to 0** — When `circular=True`, cells in cycles get `#CIRC!` which evaluates to `0`. This is not iterative solving; it breaks the cycle with a sentinel value.
- **Full-column ranges work but are slow** — Formulas like `=SUMIF(C:C, "Fruit", B:B)` resolve entire columns. On large sheets this can be expensive. Prefer explicit ranges like `C2:C100`.
- **`from_ranges()` traces dependencies automatically** — Pass output cell(s) and the engine walks backward through the dependency graph to find all required inputs. No manual input specification needed.
- **JSON model preserves formulas as strings** — `to_dict()` exports formulas as string values (e.g., `"=A1+B1"`), not computed results. Reload with `from_dict()` and call `.calculate()` to recompute.
- **Date functions return serial numbers** — `TODAY()`, `DATE()` return Excel serial dates (days since 1900-01-01). Use `datetime.datetime(1899, 12, 30) + timedelta(days=serial)` to convert.
- **`ISBLANK()` on missing cells returns `True`** — Referencing an empty/missing cell like `AZ50` in a formula creates it with value `empty`, and `ISBLANK()` correctly returns `True`.

## References

- [01-core-api](references/01-core-api.md) — ExcelModel lifecycle, calculate patterns, reference naming
- [02-conversion-guide](references/02-conversion-guide.md) — Converting formula workbooks to calculated Excel, CSV, JSON
- [03-cli-reference](references/03-cli-reference.md) — CLI commands, batch execution, Flask API
- [04-function-coverage](references/04-function-coverage.md) — Supported Excel functions by category, custom functions
- [05-troubleshooting](references/05-troubleshooting.md) — Common errors, circular references, performance tips
