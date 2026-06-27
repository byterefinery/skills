# Troubleshooting

## Installation Issues

### ModuleNotFoundError: No module named 'openpyxl'

The base `formulas` package does not include `openpyxl`. Install the `[excel]` extra:

```bash
pip install formulas[excel]==1.3.4
```

### ModuleNotFoundError: No module named 'click_log'

The CLI requires `click-log` which is not in the base requirements:

```bash
pip install click-log
```

Or install everything at once:

```bash
pip install formulas[all]==1.3.4
```

### Flask Import Error for `serve` Command

The `formulas serve` command and `formulas.app` module require Flask:

```bash
pip install flask
```

## Reference Naming Errors

### "Missing output reference" or "Missing overwrite reference"

Cell references must use the exact qualified format. Discover correct names programmatically:

```python
import formulas

model = formulas.ExcelModel().loads('workbook.xlsx').finish()
for key in sorted(model.cells):
    print(key)
```

Common mistakes:
- Wrong sheet name case (use uppercase: `'[wb.xlsx]DATA'!A1` not `'[wb.xlsx]Data'!A1`)
- Missing single quotes around the `[filename]SheetName` part
- Using lowercase filename (output uses uppercase: `WORKBOOK.XLSX`)
- Forgetting the `!` separator between sheet and cell

### Reference Format

```
'[filename.xlsx]SheetName'!CellRef
```

Examples:
- `'[my-file.xlsx]DATA'!A1`
- `'[my-file.xlsx]DATA'!A1:B10`
- `'inputs.xlsx'!INPUT_A` (named range)

## Calculation Errors

### Circular References

When a formula creates a cycle (A1 references B1, B1 references A1):

```python
# Without circular=True — may hang or error
model = formulas.ExcelModel().loads('wb.xlsx').finish()

# With circular=True — cycles resolve to 0
model = formulas.ExcelModel().loads('wb.xlsx').finish(circular=True)
solution = model.calculate()
```

Circular cells get the value `#CIRC!` which evaluates to `0`. This is not iterative numerical solving — it's a cycle-breaking sentinel. For true iterative solving, restructure the workbook to avoid cycles.

### #REF! Errors

Broken references (deleted sheets, renamed ranges) produce `#REF!`:

```python
solution = model.calculate()
for key, val in solution.items():
    if hasattr(val, 'value'):
        v = val.value[0, 0]
        if str(v).startswith('#'):
            print(f"Error in {key}: {v}")
```

### Full-Column Range Performance

Formulas referencing entire columns (`A:A`, `B:B`) load every cell in the column:

```python
# Slow on large sheets
ws['F1'] = '=SUMIF(C:C, "Fruit", B:B)'

# Prefer explicit ranges
ws['F1'] = '=SUMIF(C2:C1000, "Fruit", B2:B1000)'
```

## Common Value Extraction Mistakes

### Accessing Solution Values

```python
# WRONG — solution values are Ranges objects, not scalars
val = solution["'[wb.xlsx]Sheet'!A1"]  # This is a Ranges object

# CORRECT — extract scalar
val = solution["'[wb.xlsx]Sheet'!A1"].value[0, 0]

# For ranges (multi-cell)
range_val = solution["'[wb.xlsx]Sheet'!A1:B3"].value.tolist()
```

### compile() Return Value

```python
func = model.compile(
    inputs=["'[wb.xlsx]Inputs'!B1"],
    outputs=["'[wb.xlsx]Calc'!Total"]
)

# With single output — returns Ranges directly
result = func(100)
value = result.value[0, 0]  # NOT result[0].value[0, 0]

# With multiple outputs — still returns a single Ranges for last output
# Use calculate() with outputs list for multiple results
```

## write() Gotchas

### Output Filename is Uppercase

```python
model.write(dirpath='/output')
# Saves as /output/WORKBOOK.XLSX (not workbook.xlsx)
```

Read back with the correct case:

```python
from openpyxl import load_workbook
wb = load_workbook('/output/WORKBOOK.XLSX', data_only=True)
```

### Formulas Are Replaced with Values

The output workbook has no formula cells. All `data_type` values change from `'f'` (formula) to `'s'` (string/number). This is intentional — the output is a "calculated snapshot."

If you need to preserve formulas, keep the original file. The `to_dict()` JSON export preserves formulas as strings.

## Performance Tips

### Limit Computation Scope

```python
# Calculate only needed cells
solution = model.calculate(
    outputs=["'[wb.xlsx]Calc'!B3", "'[wb.xlsx]Calc'!B4"]
)
```

### Use compile() for Repeated Calls

```python
# Build function once, call many times
func = model.compile(
    inputs=["'[wb.xlsx]Inputs'!B1"],
    outputs=["'[wb.xlsx]Calc'!Total"]
)

for value in [100, 200, 300]:
    result = func(value)
```

### Avoid from_ranges() for Full Models

`from_ranges()` is for extracting submodels. For full workbook calculation, use `loads()` + `finish()`:

```python
# Use this for full workbooks
model = formulas.ExcelModel().loads('wb.xlsx').finish()

# Use this only when you need a specific output and its dependencies
xl = formulas.ExcelModel().from_ranges("'[wb.xlsx]Calc'!B3")
```

## Debugging

### Inspect the Dependency Graph

```python
import formulas

model = formulas.ExcelModel().loads('wb.xlsx').finish()

# List all cells in the model
for key, cell in sorted(model.cells.items()):
    print(f"{key}: {cell}")

# List dispatcher nodes
print(f"Data nodes: {len(model.dsp.data_nodes)}")
print(f"Function nodes: {len(model.dsp.function_nodes)}")

# Check for errors in solution
solution = model.calculate()
for key, val in solution.items():
    if hasattr(val, 'value'):
        v = val.value[0, 0]
        if isinstance(v, str) and v.startswith('#'):
            print(f"ERROR in {key}: {v}")
```

### Test Against Reference

Use the CLI `test` command to verify calculations match a reference workbook:

```bash
formulas test model.json --against reference.xlsx --summary
```

This compares calculated values cell-by-cell and reports additions, deletions, and changes.
