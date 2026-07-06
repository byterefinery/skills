---
name: openpyxl-3-1-5
description: >
  openpyxl 3.1.5 — read/write Microsoft Excel .xlsx, .xlsm, .xltx, .xltm files in Python.
  Use when creating, modifying, or reading Excel workbooks programmatically: writing data
  to cells, applying styles (fonts, fills, borders, alignment), conditional formatting,
  charts (area, bar, line, pie, scatter, bubble, radar, surface, stock, doughnut),
  data validation, tables, images, page setup, freeze panes, auto-filters, pivot tables,
  row/column grouping, merge/unmerge cells, comments, hyperlinks, headers/footers,
  or any Excel file manipulation in Python. Does NOT support legacy .xls or binary .xlsb.
  Trigger on: openpyxl, Workbook, load_workbook, .xlsx, Excel file creation, Excel styling,
  Excel charts, conditional formatting, data validation, freeze panes.
metadata:
  tags:
    - python
    - excel
    - spreadsheet
    - data-export
    - office-automation
---

# openpyxl 3.1.5

## Overview

openpyxl is the standard Python library for reading and writing Office Open XML Excel files (.xlsx, .xlsm, .xltx, .xltm). Version 3.1.5 supports Python 3.9+ and provides a complete API for workbook manipulation including cell styling, charts, conditional formatting, data validation, tables, pivot tables, images, and page layout.

### Core Objects

- **Workbook** — top-level container; create with `Workbook()` or load with `load_workbook()`
- **Worksheet** — individual sheet; access via `wb.active`, `wb["Sheet1"]`, or `wb.create_sheet()`
- **Cell** — individual cell; access via `ws["A1"]`, `ws.cell(row=1, column=1)`, or iteration
- **load_workbook** — read existing files; supports `read_only`, `data_only`, `keep_vba`, `rich_text` modes

### Supported File Formats

- `.xlsx` — standard Excel workbook
- `.xlsm` — Excel workbook with macros (VBA preserved with `keep_vba=True`)
- `.xltx` — Excel template
- `.xltm` — Excel template with macros

### Dependencies

- **Required**: `et-xmlfile>=1.1.0`
- **Optional**: `Pillow` (for image support), `lxml` or `defusedxml` (faster/safer XML parsing)
- **Python versions**: 3.9, 3.10, 3.11, 3.12, 3.13

## Usage

```python
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.worksheet.datavalidation import DataValidation

# --- Create a workbook ---
wb = Workbook()
ws = wb.active
ws.title = "Report"

# --- Write data ---
ws["A1"] = "Name"
ws["B1"] = "Score"
ws.append(["Alice", 85])
ws.append(["Bob", 92])
ws.cell(row=3, column=1, value="Charlie")
ws.cell(row=3, column=2, value=78)

# --- Style cells ---
ws["A1"].font = Font(bold=True, size=12)
ws["A1"].fill = PatternFill("solid", fgColor="4472C4")
ws["A1"].alignment = Alignment(horizontal="center", vertical="center")

# --- Column width / row height ---
ws.column_dimensions["A"].width = 20
ws.row_dimensions[1].height = 25

# --- Freeze panes ---
ws.freeze_panes = "A2"

# --- Data validation ---
dv = DataValidation(type="list", formula1='"Pass,Fail"', allow_blank=True)
dv.sqref = "B2:B3"
ws.add_data_validation(dv)

# --- Merge cells ---
ws.merge_cells("A1:B1")

# --- Auto-filter ---
ws.auto_filter.ref = "A1:B3"

# --- Chart ---
chart = BarChart()
chart.title = "Scores"
chart.style = 10
chart.add_data(Reference(ws, min_col=2, min_row=1, max_row=3))
chart.set_categories(Reference(ws, min_col=1, min_row=2, max_row=3))
chart.legend.position = "b"
ws.add_chart(chart, "D5")

# --- Save ---
wb.save("report.xlsx")

# --- Load existing workbook ---
wb = load_workbook("report.xlsx")
ws = wb.active
value = ws["A1"].value

# --- Read-only mode (large files) ---
wb = load_workbook("large.xlsx", read_only=True)
for row in wb.active.iter_rows(values_only=True):
    print(row)
wb.close()
```

## Gotchas

- **Cells are created on access** — `ws["A1"]` creates the cell in memory even if empty. Use `iter_rows()` or `iter_cols()` to avoid creating unnecessary cells.
- **`ws.append()` adds to the next empty row** — it does not insert; existing rows are not shifted. Use `ws.insert_rows()` to shift content.
- **Styles are shared** — identical style objects are deduplicated internally. Creating many unique `Font()`/`Fill()` objects bloats the file. Reuse style objects.
- **`merge_cells` keeps only the top-left cell's value** — all other cells in the range become `MergedCell` with `value=None`. Unmerge with `unmerge_cells()`.
- **`load_workbook` with `data_only=True`** — returns cached values of formulas instead of the formula strings. Without it, formula cells return the formula text.
- **Row/column indices are 1-based** — `ws.cell(row=1, column=1)` is A1, not row=0, column=0.
- **`ws.values` / `ws.iter_rows(values_only=True)`** — returns raw values without Cell objects. Use when you only need data, not styling.
- **Charts reference cell ranges as strings** — use `Reference(ws, min_col=1, min_row=1, max_col=3, max_row=10)` to build safe references with sheet names.
- **Image support requires Pillow** — `from openpyxl.drawing.image import Image` will raise `ImportError` if Pillow is not installed.
- **`.xls` and `.xlsb` are NOT supported** — openpyxl only handles Open XML formats (.xlsx, .xlsm, .xltx, .xltm).
- **`ws.column_dimensions["A"].width`** — width is in character units (approximate). Default column width is ~9.14.
- **Conditional formatting rules auto-assign priority** — `ws.conditional_formatting.add()` increments priority automatically.
- **`ws.freeze_panes = "A1"` disables freezing** — setting to A1 is treated as no freeze. Use `"A2"` to freeze the first row.
- **`wb.save()` can only be called once in write-only mode** — subsequent saves raise `WorkbookAlreadySaved`.
- **Formula strings must start with `=`** — openpyxl auto-detects formulas starting with `=` and sets `cell.data_type = 'f'`.
- **Date values are stored as floats internally** — Excel stores dates as days since epoch. Use `datetime` objects and set `number_format` for display.
- **Named styles must be unique per workbook** — adding a `NamedStyle` with a duplicate name raises `ValueError`.
- **`ws.copy_worksheet()` copies within workbook only** — cannot copy worksheets between different workbooks.
- **`CellRange` operations require same sheet** — comparing or intersecting ranges from different worksheets raises `ValueError`.

## References

- [01-core-api](references/01-core-api.md) — Workbook, Worksheet, Cell constructors and core operations
- [02-cell-operations](references/02-cell-operations.md) — Cell types, values, formulas, data binding, iteration
- [03-styling](references/03-styling.md) — Font, Fill, Border, Alignment, Color, NamedStyle, style application
- [04-row-column](references/04-row-column.md) — Dimensions, width/height, grouping, hiding, outline levels
- [05-conditional-formatting](references/05-conditional-formatting.md) — Rule types, ColorScale, DataBar, IconSet, CellIs, FormulaRule
- [06-charts](references/06-charts.md) — Chart types, Series, Reference, axes, legend, title, styles
- [07-data-validation](references/07-data-validation.md) — DataValidation types, operators, error styles, prompts
- [08-tables](references/08-tables.md) — Table, TableColumn, TableStyleInfo, calculated columns, totals
- [09-page-layout](references/09-page-layout.md) — Page setup, margins, print options, headers/footers, print area
- [10-sheets-views](references/10-sheets-views.md) — Sheet creation, freeze panes, zoom, gridlines, tab color, visibility
- [11-filters-sorting](references/11-filters-sorting.md) — AutoFilter, FilterColumn, sort conditions, custom filters
- [12-advanced-features](references/12-advanced-features.md) — Comments, hyperlinks, images, pivot tables, protection, defined names
- [13-modes-utilities](references/13-modes-utilities.md) — Read-only, write-only, data-only modes; CellRange; coordinate utilities; number formats
