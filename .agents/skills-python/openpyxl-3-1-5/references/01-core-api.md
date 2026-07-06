# Core API

## Workbook

The top-level container for all document information.

### Creation

```python
from openpyxl import Workbook

# Default: creates one blank worksheet
wb = Workbook()

# Write-only mode: for large files, streams data, no random access
wb = Workbook(write_only=True)

# ISO dates: use 1904 epoch (Mac) instead of 1900 (Windows)
wb = Workbook(iso_dates=True)
```

### Loading

```python
from openpyxl import load_workbook

# Normal mode: full read/write access
wb = load_workbook("file.xlsx")

# Read-only: optimized for reading large files, cells are read sequentially
wb = load_workbook("file.xlsx", read_only=True)

# Data-only: formula cells return cached values, not formula strings
wb = load_workbook("file.xlsx", data_only=True)

# Keep VBA: preserve macro content (does NOT make macros usable)
wb = load_workbook("file.xlsm", keep_vba=True)

# Rich text: preserve rich text formatting in cells
wb = load_workbook("file.xlsx", rich_text=True)

# Keep external links: preserve links to other workbooks (default True)
wb = load_workbook("file.xlsx", keep_links=True)
```

### Workbook Properties

```python
wb.active              # Currently active sheet (Worksheet)
wb.active = 1          # Set active sheet by index
wb.active = ws         # Set active sheet by Worksheet object
wb.sheetnames          # List of sheet names
wb["Sheet1"]           # Get sheet by name
wb["Sheet1"] is wb[0]  # Sheets are iterable
wb.defined_names       # DefinedNameDict of named ranges
wb.properties          # DocumentProperties (author, title, subject, etc.)
wb.custom_doc_props    # CustomPropertyList
wb.security            # DocumentSecurity
wb.epoch               # WINDOWS_EPOCH (1900) or MAC_EPOCH (1904)
wb.encoding            # Character encoding (default "utf-8")
wb.template            # True if workbook is a template
wb.vba_archive         # VBA archive (when keep_vba=True)
wb.mime_type           # MIME type based on template/macro status
wb.calculation         # CalcProperties (calculation settings)
wb.views               # BookView list
wb.named_styles        # List of available named style names
```

### Sheet Management

```python
# Create a new sheet (appended at end)
ws = wb.create_sheet(title="Data")

# Insert at specific position (0 = first)
ws = wb.create_sheet(title="Summary", index=0)

# Get sheets
ws = wb["Sheet1"]
for sheet in wb.worksheets:
    print(sheet.title)

# Chartsheets
cs = wb.create_chartsheet(title="Charts")
for cs in wb.chartsheets:
    print(cs.title)

# Remove a sheet
wb.remove(ws)
del wb["Sheet1"]

# Move a sheet
wb.move_sheet(ws, offset=-1)  # Move one position left

# Copy a sheet (within same workbook only)
ws_copy = wb.copy_worksheet(ws)
```

### Saving

```python
wb.save("output.xlsx")
wb.save("output.xlsm")  # If vba_archive is set
wb.save("output.xltx")  # If template=True
```

### Document Properties

```python
from openpyxl.packaging.core import DocumentProperties, CreatorProperty

wb.properties.title = "Quarterly Report"
wb.properties.subject = "Sales Data"
wb.properties.creator = "My Application"
wb.properties.description = "Q4 2024 sales figures"
wb.properties.keywords = "sales, quarterly, 2024"
wb.properties.lastModifiedBy = "Updated by Script"
wb.properties.category = "Reports"

# Custom properties
from openpyxl.packaging.custom import CustomProperty
wb.custom_doc_props.append(CustomProperty("Dept", "Sales", "vtString"))
```

## Worksheet

The second-level container, representing a single sheet.

### Creation and Access

```python
# Via workbook
ws = wb.create_sheet("Data")
ws = wb.active
ws = wb["Sheet1"]

# Worksheet properties
ws.title = "New Name"
ws.sheet_state = "visible"        # "visible", "hidden", "veryHidden"
ws.dimensions                    # "A1:M24" — bounding range of data
ws.min_row, ws.max_row           # Min/max row indices with data
ws.min_column, ws.max_column     # Min/max column indices with data
ws.calculate_dimension()         # Returns "A1:M24" string
```

### Cell Access

```python
# By coordinate string
cell = ws["A1"]
cell.value = "Hello"

# By row/column (1-based)
cell = ws.cell(row=1, column=1, value="Hello")

# Range access
row = ws[1]           # Tuple of cells in row 1
col = ws["A"]         # Tuple of cells in column A
range_cells = ws["A1:D4"]  # Tuple of rows, each row is tuple of cells

# Slice notation
ws["A1":"D4"]         # Same as ws["A1:D4"]

# Delete a cell
del ws["A1"]
```

### Iteration

```python
# All cells (generates Cell objects)
for row in ws.iter_rows():
    for cell in row:
        print(cell.value)

# Values only (no Cell objects, faster)
for row in ws.iter_rows(min_row=1, max_row=10, values_only=True):
    print(row)  # Tuple of values

# Specific range
for row in ws.iter_rows(min_row=2, max_row=5, min_col=1, max_col=3):
    for cell in row:
        print(cell.value)

# By columns
for col in ws.iter_cols(min_col=1, max_col=3):
    for cell in col:
        print(cell.value)

# Convenience properties
for row in ws.rows:       # All rows as Cell tuples
    pass
for col in ws.columns:    # All columns as Cell tuples
    pass
for row in ws.values:     # All rows as value tuples
    pass

# Direct iteration
for row in ws:            # Same as ws.iter_rows()
    pass
```

### Append

```python
# Append a row from a list (fills from column A)
ws.append(["Name", "Age", "Score"])
ws.append(["Alice", 30, 85])

# Append from dict (keys are column letters or numbers)
ws.append({"A": "Bob", "C": 92})
ws.append({1: "Charlie", 3: 78})

# Append from generator
ws.append((x * 2 for x in range(5)))
```

### Insert and Delete Rows/Columns

```python
# Insert rows before row 3 (shifts content down)
ws.insert_rows(3, amount=2)

# Insert columns before column 2
ws.insert_cols(2, amount=1)

# Delete rows starting at row 3
ws.delete_rows(3, amount=2)

# Delete columns starting at column 2
ws.delete_cols(2, amount=1)

# Move a range of cells
from openpyxl.worksheet.cell_range import CellRange
ws.move_range("B2:D4", rows=2, cols=1)
ws.move_range("B2:D4", rows=2, translate=True)  # Update formula references
```

### Defined Names (Named Ranges)

```python
# Global named range
from openpyxl.workbook.defined_name import DefinedName
dn = DefinedName("Total", "'Sheet1'!$B$1:$B$10")
wb.defined_names["Total"] = dn

# Sheet-scoped named range
ws.defined_names["Subtotal"] = DefinedName("Subtotal", "$C$1:$C$5", scope="Sheet1")

# Access
dn = wb.defined_names["Total"]
print(dn.attr_text)  # "'Sheet1'!$B$1:$B$10"
```
