# Core API Reference

## ExcelModel Lifecycle

The `ExcelModel` is the primary class for working with spreadsheet workbooks. The standard lifecycle has four stages:

```python
import formulas

# 1. Create and load
model = formulas.ExcelModel().loads('workbook.xlsx')

# 2. Finish — resolves all dependencies, assembles ranges
model.finish()
# With circular references:
model.finish(circular=True)

# 3. Calculate
solution = model.calculate()

# 4. Write (optional — saves calculated values back to .xlsx)
model.write(dirpath='/output')
```

### `loads(*file_names)`

Load one or more workbook files. Returns self for chaining. Supports `.xlsx` and `.ods` formats. JSON files are loaded via `from_dict()` instead.

```python
# Single file
model = formulas.ExcelModel().loads('data.xlsx')

# Multiple files (cross-file references supported)
model = formulas.ExcelModel().loads('inputs.xlsx', 'calc.xlsx')
```

### `finish(complete=True, circular=False, assemble=True, anchors=True)`

Finalize the model after loading. Each parameter controls a resolution step:

- **`complete`** — Trace all formula dependencies recursively. If a cell references another cell that hasn't been loaded yet, it auto-discovers and loads the dependency. Disable only when you've manually loaded everything.
- **`circular`** — Enable circular reference solving. Cells in cycles get replaced with `#CIRC!` (evaluates to 0). This is not iterative numerical solving; it breaks cycles with a sentinel value.
- **`assemble`** — Group adjacent cells into range objects (e.g., `A1:A10`). Improves performance for range operations.
- **`anchors`** — Resolve named ranges and structured references.

### `calculate(inputs=None, outputs=None)`

Execute the calculation engine. Returns a `Solution` dict mapping cell references to `Ranges` values.

```python
# Calculate everything
solution = model.calculate()

# Override specific inputs
solution = model.calculate(inputs={
    "'[wb.xlsx]Sheet'!A1": 42,
    "'[wb.xlsx]Sheet'!B1": "text",
})

# Compute only specific output cells (faster, skips unrelated cells)
solution = model.calculate(outputs=["'[wb.xlsx]Sheet'!C1"])

# Both
solution = model.calculate(
    inputs={"'[wb.xlsx]Sheet'!A1": 42},
    outputs=["'[wb.xlsx]Sheet'!C1", "'[wb.xlsx]Sheet'!D1"]
)
```

### `compile(inputs, outputs)`

Build a reusable function from the model. Returns a `DispatchPipe` callable where positional arguments map to the `inputs` list order.

```python
func = model.compile(
    inputs=["'[wb.xlsx]Inputs'!B1", "'[wb.xlsx]Inputs'!B2"],
    outputs=["'[wb.xlsx]Calc'!Total"]
)

# Call with values in same order as inputs list
result = func(100, 25.5)
value = result.value[0, 0]  # Scalar from Ranges object
```

The function is optimized: only the dependency graph between inputs and outputs is retained. Unrelated cells are pruned.

### `from_ranges(*ranges)`

Extract a submodel starting from output cell(s), automatically tracing all dependencies backward.

```python
xl = formulas.ExcelModel().from_ranges(
    "'[wb.xlsx]Calc'!B3",   # Output cell
    "'[wb.xlsx]Calc'!B4",   # Another output
)
solution = xl.dsp.dispatch()
```

### `to_dict()` / `from_dict(adict)`

Export/import the model as a JSON-serializable dictionary.

```python
# Export — formulas preserved as strings, values as scalars
model_dict = model.to_dict()
# Example output:
# {
#   "'[wb.xlsx]Sheet'!A1": 42,
#   "'[wb.xlsx]Sheet'!B1": "=('[wb.xlsx]Sheet'!A1 * 2)",
# }

# Import and recalculate
loaded = formulas.ExcelModel().from_dict(model_dict)
solution = loaded.calculate()
```

## Reference Naming Convention

Cell references in `formulas` use fully qualified names:

```
'[filename.xlsx]SheetName'!CellRef
```

- **Filename**: The workbook filename, uppercase in output (e.g., `WORKBOOK.XLSX`)
- **Sheet name**: Uppercase (e.g., `SHEET1`, `DATA`, `INPUTS`)
- **Cell ref**: Standard Excel notation (`A1`, `B2:C10`)
- **Quotes**: Single quotes around the `[filename]SheetName` part

Discover correct references using:

```python
model = formulas.ExcelModel().loads('wb.xlsx').finish()
for key in model.cells:
    print(key)  # Shows all reference strings

# Or from solution:
solution = model.calculate()
for key in solution:
    print(f"{key}: {_extract_value(solution[key])}")
```

## Ranges Object

Calculation results are `Ranges` objects wrapping numpy arrays:

```python
from formulas.ranges import Ranges

# Single cell value
val = solution["'[wb.xlsx]Sheet'!A1"].value[0, 0]

# Range values (2D array)
range_val = solution["'[wb.xlsx]Sheet'!A1:B3"].value

# Convert to Python list
list_val = solution["'[wb.xlsx]Sheet'!A1"].value.tolist()

# Helper for clean extraction
def _extract_value(value):
    import schedula as sh
    from formulas.ranges import Ranges
    if isinstance(value, Ranges):
        data = value.value.tolist()
        if len(data) == 1 and len(data[0]) == 1:
            return data[0][0]
        return data
    if value is sh.EMPTY:
        return None
    return value
```

## Parser — Standalone Formulas

Parse and compile individual formula strings without a workbook:

```python
import formulas

# Parse
result, = formulas.Parser().ast('=(1 + 1) + B3 / A2')
func = result.compile()

# Inspect inputs
print(list(func.inputs))  # ['A2', 'B3']

# Evaluate
print(func(1, 5))  # Array(7.0, dtype=object)
```

The `Parser().ast()` returns a tuple; the formula is at index `[1]`. Index `[0]` is the root node.

## write() — Save Calculated Workbook

```python
model = formulas.ExcelModel().loads('wb.xlsx').finish()
solution = model.calculate()
books = model.write(dirpath='/output')
```

Key behaviors:
- Formula cells are replaced with their computed values
- Cell `data_type` changes from `'f'` (formula) to `'s'` (string/number)
- Output filename is the uppercase workbook name
- Multiple workbooks produce multiple files in the output directory
- Returns a dict of book names → openpyxl Workbook objects (before saving)
