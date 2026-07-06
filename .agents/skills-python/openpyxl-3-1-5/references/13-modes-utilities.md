# Modes and Utilities

## Read-Only Mode

Optimized for reading large files. Cells are read sequentially; no random access.

```python
from openpyxl import load_workbook

wb = load_workbook("large.xlsx", read_only=True)
ws = wb.active

# Iterate rows (sequential access only)
for row in ws.iter_rows(min_row=2, values_only=True):
    print(row)  # Tuple of values

# Access cells by coordinate (creates ReadOnlyCell)
cell = ws.cell(row=1, column=1)
print(cell.value)

# Row access
for row_idx, row in enumerate(ws.iter_rows(), 1):
    if row_idx > 1000:
        break

# Close when done
wb.close()

# Limitations:
# - Cannot modify cells
# - Cannot create new sheets
# - Cannot access styles
# - Cannot access formulas (use data_only=True for cached values)
```

## Write-Only Mode

Streams data for creating large files with minimal memory.

```python
from openpyxl import Workbook

wb = Workbook(write_only=True)
ws = wb.create_sheet()

# Append rows (list or dict)
ws.append(["Name", "Score", "Grade"])
ws.append(["Alice", 85, "A"])
ws.append({"A": "Bob", "B": 92, "C": "A+"})

# Cell objects for styling (write-only cells)
from openpyxl.cell import WriteOnlyCell
cell = WriteOnlyCell(ws, value="Styled")
cell.font = Font(bold=True)
ws.append([cell, 100, "A"])

# Save (can only save once!)
wb.save("large_output.xlsx")

# Limitations:
# - Can only append rows, no random access
# - Can only save once
# - Cannot read existing files
# - Styles must be applied before appending
```

## Data-Only Mode

Returns cached values instead of formula strings.

```python
from openpyxl import load_workbook

# Default: formula cells return formula strings
wb = load_workbook("file.xlsx")
print(ws["A1"].value)  # "=SUM(B1:B10)"

# Data-only: returns cached computed values
wb = load_workbook("file.xlsx", data_only=True)
print(ws["A1"].value)  # 450 (cached result)
```

## CellRange

Range operations and set-like comparisons.

```python
from openpyxl.worksheet.cell_range import CellRange

# Create from range string
cr = CellRange("A1:D10")
cr = CellRange("'Sheet1'!A1:D10")
cr = CellRange(min_col=1, min_row=1, max_col=4, max_row=10)

# Properties
cr.coord           # "A1:D10"
cr.bounds          # (1, 1, 4, 10)
cr.size            # {'columns': 4, 'rows': 10}
cr.title           # "Sheet1" or None

# Iterate
for row in cr.rows:
    print(row)  # [(1, 1), (1, 2), (1, 3), (1, 4)]

for col in cr.cols:
    print(col)  # [(1, 1), (2, 1), (3, 1), ...]

for cell in cr.cells:
    print(cell)  # (1, 1), (1, 2), ...

# Edges
cr.top      # [(1, 1), (1, 2), (1, 3), (1, 4)]
cr.bottom   # [(10, 1), (10, 2), (10, 3), (10, 4)]
cr.left     # [(1, 1), (2, 1), ..., (10, 1)]
cr.right    # [(1, 4), (2, 4), ..., (10, 4)]

# Shift
cr.shift(col_shift=2, row_shift=3)  # Now C4:F13

# Expand/Shrink
cr.expand(right=2, down=3, left=1, up=1)
cr.shrink(right=1, bottom=1, left=1, top=1)

# Set operations (same sheet only)
cr1 = CellRange("A1:D10")
cr2 = CellRange("C5:F15")

cr1.isdisjoint(cr2)         # False
cr1.issubset(cr2)           # False
cr1.issuperset(cr2)         # False
intersection = cr1 & cr2    # CellRange('C5:D10')
union = cr1 | cr2           # CellRange('A1:F15')

# Contains
"A5" in cr1                 # True
"D11" in cr1                # False
```

## MultiCellRange

Multiple non-contiguous ranges.

```python
from openpyxl.worksheet.cell_range import MultiCellRange

mcr = MultiCellRange("A1:B2 D4:E5")
mcr = MultiCellRange()
mcr.add("A1:B2")
mcr.add("D4:E5")

# Iterate
for cr in mcr:
    print(cr)  # CellRange('A1:B2'), CellRange('D4:E5')

# Contains
"A1" in mcr     # True
"C3" in mcr     # False

# Remove
mcr.remove(CellRange("A1:B2"))
```

## Coordinate Utilities

```python
from openpyxl.utils import (
    get_column_letter,
    column_index_from_string,
    coordinate_to_tuple,
    range_boundaries,
    rows_from_range,
    cols_from_range,
    quote_sheetname,
    absolute_coordinate,
    coordinate_from_string,
    get_column_interval,
)

# Column letter ↔ index
get_column_letter(1)           # "A"
get_column_letter(26)          # "Z"
get_column_letter(27)          # "AA"
get_column_letter(16384)       # "XFD"

column_index_from_string("A")  # 1
column_index_from_string("Z")  # 26
column_index_from_string("AA") # 27

# Coordinate parsing
coordinate_to_tuple("A1")      # (1, 1)
coordinate_to_tuple("Z100")    # (100, 26)
coordinate_from_string("B12")  # ("B", 12)

# Absolute coordinate
absolute_coordinate("A1:D10")  # "$A$1:$D$10"
absolute_coordinate("B5")      # "$B$5"

# Range boundaries
range_boundaries("A1:D10")     # (1, 1, 4, 10) — (min_col, min_row, max_col, max_row)
range_boundaries("B5")         # (2, 5, 2, 5)
range_boundaries("A:D")        # (1, None, 4, None)
range_boundaries("1:10")       # (None, 1, None, 10)

# Iterate cells in range
for row in rows_from_range("A1:D3"):
    print(row)  # ('A1', 'B1', 'C1', 'D1'), ...

for col in cols_from_range("A1:D3"):
    print(col)  # ('A1', 'A2', 'A3'), ...

# Column interval
get_column_interval("A", "D")  # ["A", "B", "C", "D"]
get_column_interval(1, 4)      # ["A", "B", "C", "D"]

# Quote sheet name (for formulas)
quote_sheetname("Sheet 1")     # "'Sheet 1'"
quote_sheetname("Sheet1")      # "'Sheet1'"
```

## Number Formats

```python
from openpyxl.styles import numbers
from openpyxl.styles.numbers import (
    BUILTIN_FORMATS,
    BUILTIN_FORMATS_REVERSE,
    builtin_format_code,
    builtin_format_id,
    is_date_format,
    is_builtin,
    is_datetime,
    is_timedelta_format,
)

# Built-in format codes
builtin_format_code(0)   # 'General'
builtin_format_code(14)  # 'mm-dd-yy'
builtin_format_code(22)  # 'm/d/yy h:mm'

# Reverse lookup
builtin_format_id('0.00')     # 2
builtin_format_id('General')  # 0

# Check format type
is_date_format('yyyy-mm-dd')      # True
is_date_format('0.00')            # False
is_builtin('0.00')                # True
is_builtin('custom-format')       # False
is_datetime('yyyy-mm-dd h:mm')    # 'datetime'
is_datetime('yyyy-mm-dd')         # 'date'
is_datetime('h:mm')               # 'time'
is_timedelta_format('[hh]:mm:ss') # True

# Format constants
numbers.FORMAT_GENERAL                      # 'General'
numbers.FORMAT_TEXT                         # '@'
numbers.FORMAT_NUMBER                       # '0'
numbers.FORMAT_NUMBER_00                    # '0.00'
numbers.FORMAT_NUMBER_COMMA_SEPARATED1      # '#,##0.00'
numbers.FORMAT_PERCENTAGE                   # '0%'
numbers.FORMAT_PERCENTAGE_00                # '0.00%'
numbers.FORMAT_DATE_YYYYMMDD2               # 'yyyy-mm-dd'
numbers.FORMAT_DATE_DATETIME                # 'yyyy-mm-dd h:mm:ss'
numbers.FORMAT_DATE_TIMEDELTA               # '[hh]:mm:ss'
numbers.FORMAT_CURRENCY_USD_SIMPLE          # '"$"#,##0.00_-'
numbers.FORMAT_CURRENCY_EUR_SIMPLE          # '[$EUR ]#,##0.00_-'

# Apply to cell
ws["A1"].number_format = '0.00%'
ws["A2"].number_format = 'yyyy-mm-dd'
ws["A3"].number_format = '"$"#,##0.00_);[Red]("$"#,##0.00_)'
```

## Units

```python
from openpyxl.utils.units import (
    pixels_to_EMU,
    EMU_to_pixels,
    points_to_EMU,
    inches_to_EMU,
    DEFAULT_COLUMN_WIDTH,
)

# EMU = English Metric Units (1/914400 of an inch)
pixels_to_EMU(100)
EMU_to_pixels(914400)  # 100
points_to_EMU(72)      # 1 inch in EMU
inches_to_EMU(1)
```

## Exceptions

```python
from openpyxl.utils.exceptions import (
    IllegalCharacterError,   # Invalid characters in cell string
    InvalidFileException,    # Unsupported file format
    CellCoordinatesException, # Invalid cell coordinate
    ReadOnlyWorkbookException, # Modification on read-only workbook
)
```

## Constants

```python
import openpyxl.constants as constants

constants.ROWS_EXCEL       # 1048576
constants.COLUMNS_EXCEL    # 16384
constants.MAX_COLUMN       # 'XFD'
constants.MAX_ROW          # 1048576
constants.ILLEGAL_CHARACTERS_RE  # Regex for illegal characters
```
