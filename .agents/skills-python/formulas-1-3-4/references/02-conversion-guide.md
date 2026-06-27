# Conversion Guide

## Converting Formula-Based Workbooks to Calculated Values

The `formulas` package excels at converting Excel workbooks with formulas into "flat" versions where every cell contains its computed value. This is useful for:

- Generating reports from template spreadsheets
- Creating static snapshots of dynamic calculations
- Preparing data for systems that don't support Excel formulas
- Archiving calculated results alongside source templates

### Step-by-Step: Formula Workbook → Calculated .xlsx

```python
import formulas

# Load and calculate
model = formulas.ExcelModel().loads('template.xlsx').finish()
solution = model.calculate()

# Write calculated workbook (formulas replaced with values)
model.write(dirpath='/output')
# Output: /output/TEMPLATE.XLSX
```

The output file has identical structure (sheets, formatting from openpyxl) but all formula cells now contain their computed results as plain values.

### With Input Overrides

```python
model = formulas.ExcelModel().loads('template.xlsx').finish()
solution = model.calculate(inputs={
    "'[template.xlsx]Inputs'!B1": 500,
    "'[template.xlsx]Inputs'!B2": 15.99,
})
model.write(dirpath='/output', solution=solution)
```

### As a Reusable Function (ETL Pattern)

```python
import formulas

model = formulas.ExcelModel().loads('template.xlsx').finish()
func = model.compile(
    inputs=["'[template.xlsx]Inputs'!B1", "'[template.xlsx]Inputs'!B2"],
    outputs=["'[template.xlsx]Calc'!Total"],
)

# Process multiple records
records = [
    {'qty': 100, 'price': 10.0},
    {'qty': 200, 'price': 15.0},
    {'qty': 50, 'price': 20.0},
]

results = []
for rec in records:
    result, = func(rec['qty'], rec['price'])
    results.append({
        'qty': rec['qty'],
        'price': rec['price'],
        'total': result.value[0, 0],
    })
```

## Exporting to CSV

`formulas` does not have a built-in CSV exporter. Use `openpyxl` to read the calculated workbook and write CSV:

```python
from openpyxl import load_workbook
import csv

# After model.write(dirpath='/output')
wb = load_workbook('/output/TEMPLATE.XLSX', data_only=True)

for ws in wb.worksheets:
    with open(f'{ws.title}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        for row in ws.iter_rows(values_only=True):
            # Skip completely empty rows
            if any(v is not None for v in row):
                writer.writerow(list(row))
```

### CSV with Headers from First Row

```python
for ws in wb.worksheets:
    rows = list(ws.iter_rows(values_only=True))
    rows = [list(r) for r in rows if any(v is not None for v in r)]
    if not rows:
        continue

    headers = rows[0]
    with open(f'{ws.title}.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows[1:]:
            writer.writerow(dict(zip(headers, row)))
```

## Exporting to JSON

### Per-Sheet JSON (Array of Records)

```python
from openpyxl import load_workbook
import json

wb = load_workbook('/output/TEMPLATE.XLSX', data_only=True)
all_data = {}

for ws in wb.worksheets:
    rows = list(ws.iter_rows(values_only=True))
    rows = [list(r) for r in rows if any(v is not None for v in r)]
    if not rows:
        continue

    headers = [v if v is not None else f'col_{i}'
               for i, v in enumerate(rows[0])]
    records = []
    for row in rows[1:]:
        record = {headers[j]: row[j] for j in range(len(headers))}
        records.append(record)

    all_data[ws.title] = records

with open('output.json', 'w') as f:
    json.dump(all_data, f, indent=2)
```

### Combined JSON (All Sheets)

```python
# Single JSON file with sheet names as top-level keys
output = {
    ws.title: [
        {headers[j]: row[j] for j in range(len(headers))}
        for row in rows[1:]
    ]
    for ws in wb.worksheets
    if (rows := [list(r) for r in ws.iter_rows(values_only=True)
                 if any(v is not None for v in r)])
    and (headers := [v or f'col_{i}' for i, v in enumerate(rows[0])])
}
```

### Flat JSON (Key-Value from Cell References)

```python
import formulas

model = formulas.ExcelModel().loads('template.xlsx').finish()
solution = model.calculate()

# Export all cells as key-value pairs
flat = {}
for key, val in solution.items():
    if hasattr(val, 'value'):
        data = val.value.tolist()
        flat[key] = data[0][0] if len(data) == 1 and len(data[0]) == 1 else data

with open('flat.json', 'w') as f:
    json.dump(flat, f, indent=2)
```

## Exporting the Model Structure (JSON Model)

The `to_dict()` method exports the workbook structure including formulas:

```python
model = formulas.ExcelModel().loads('template.xlsx').finish()
model_dict = model.to_dict()

# Output:
# {
#   "'[wb.xlsx]Sheet'!A1": "Header",
#   "'[wb.xlsx]Sheet'!A2": 42,
#   "'[wb.xlsx]Sheet'!B2": "=('[wb.xlsx]Sheet'!A2 * 2)",
# }
```

This JSON model can be:
- Version-controlled (text-based, diff-friendly)
- Reloaded and recalculated independently
- Modified programmatically (change formulas or values)
- Used as input to `formulas calc` CLI

```bash
# CLI equivalent
formulas build template.xlsx --output-file model.json

# Recalculate from JSON
formulas calc model.json --output-format json
```

## Complete Conversion Pipeline

```python
import formulas
from openpyxl import load_workbook
import csv, json, os

def convert_workbook(xlsx_path, output_dir, formats=None):
    """Convert formula workbook to multiple output formats."""
    if formats is None:
        formats = ['xlsx', 'csv', 'json']

    os.makedirs(output_dir, exist_ok=True)

    # 1. Calculate
    model = formulas.ExcelModel().loads(xlsx_path).finish()
    solution = model.calculate()

    # 2. Calculated .xlsx
    if 'xlsx' in formats:
        model.write(dirpath=output_dir)

    # 3. Load calculated workbook for other formats
    src_name = os.path.basename(xlsx_path).split('.')[0].upper() + '.XLSX'
    calc_path = os.path.join(output_dir, src_name)
    wb = load_workbook(calc_path, data_only=True)

    all_sheets = {}
    for ws in wb.worksheets:
        rows = [list(r) for r in ws.iter_rows(values_only=True)
                if any(v is not None for v in r)]
        if not rows:
            continue

        headers = [v or f'col_{i}' for i, v in enumerate(rows[0])]
        records = [{headers[j]: row[j] for j in range(len(headers))}
                   for row in rows[1:]]
        all_sheets[ws.title] = {'headers': headers, 'records': records}

        # 4. CSV per sheet
        if 'csv' in formats:
            with open(os.path.join(output_dir, f'{ws.title}.csv'), 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(records)

    # 5. Combined JSON
    if 'json' in formats:
        with open(os.path.join(output_dir, 'data.json'), 'w') as f:
            json.dump(all_sheets, f, indent=2, default=str)

    return all_sheets
```
