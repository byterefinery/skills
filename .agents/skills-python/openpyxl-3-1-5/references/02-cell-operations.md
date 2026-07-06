# Cell Operations

## Cell Object

Individual cells with value, type, style, and address.

### Properties

```python
cell = ws["A1"]

cell.value           # Get/set the value
cell.row             # Row number (1-based)
cell.column          # Column number (1-based)
cell.coordinate      # "A1" — Excel-style coordinate
cell.column_letter   # "A" — letter representation
cell.col_idx         # Same as column (1-based index)
cell.data_type       # 'n' (numeric), 's' (string), 'b' (bool), 'd' (date),
                     # 'f' (formula), 'e' (error), 'inlineStr', 'str'
cell.comment         # Comment object or None
cell.hyperlink       # Hyperlink object or None
cell.is_date         # True if formatted as date
cell.internal_value  # Raw value as stored for Excel
```

### Cell Types

```python
# Numeric — int, float
ws["A1"].value = 42
ws["A2"].value = 3.14
ws["A1"].data_type  # 'n'

# String
ws["A3"].value = "Hello"
ws["A3"].data_type  # 's'
# Strings are truncated to 32,767 characters
# Control characters 0x00-0x0D and 0x0E-0x1F are illegal

# Boolean
ws["A4"].value = True
ws["A4"].data_type  # 'b'

# Date/time — datetime, date, time, timedelta
import datetime
ws["A5"].value = datetime.datetime(2024, 1, 15, 10, 30, 0)
ws["A5"].data_type  # 'd'
# Automatic number format is applied based on type:
#   datetime -> 'yyyy-mm-dd h:mm:ss'
#   date     -> 'yyyy-mm-dd'
#   time     -> 'h:mm:ss'
#   timedelta -> '[hh]:mm:ss'

# Formula — string starting with '='
ws["A6"].value = "=SUM(B1:B10)"
ws["A6"].data_type  # 'f'

# Error codes
ws["A7"].value = "#N/A"
ws["A7"].data_type  # 'e'
# Valid error codes: #NULL!, #DIV/0!, #VALUE!, #REF!, #NAME?, #NUM!, #N/A
```

### Number Format

```python
from openpyxl.styles import numbers

# Built-in format constants
ws["A1"].number_format = numbers.FORMAT_GENERAL          # 'General'
ws["A2"].number_format = numbers.FORMAT_NUMBER_00         # '0.00'
ws["A3"].number_format = numbers.FORMAT_PERCENTAGE        # '0%'
ws["A4"].number_format = numbers.FORMAT_DATE_YYYYMMDD2    # 'yyyy-mm-dd'
ws["A5"].number_format = numbers.FORMAT_CURRENCY_USD      # '$#,##0_-'

# Custom format
ws["A6"].number_format = '#,##0.00'
ws["A7"].number_format = '"$"#,##0.00_);[Red]("$"#,##0.00)'

# Check if a format represents a date
from openpyxl.styles import is_date_format, is_builtin
is_date_format('yyyy-mm-dd')  # True
is_builtin('0.00')            # True (built-in format)

# Built-in format lookup
from openpyxl.styles.numbers import BUILTIN_FORMATS, builtin_format_code, builtin_format_id
builtin_format_code(14)       # 'mm-dd-yy'
builtin_format_id('0.00')     # 2
```

### Cell Offset

```python
# Get a cell relative to the current cell
current = ws["B5"]
right = current.offset(column=1)      # C5
below = current.offset(row=2)         # B7
diag = current.offset(row=1, column=1)  # C6
```

### Cell Style (Inline)

```python
# Direct style access on cell (proxy to cell style)
cell.font = Font(bold=True, size=12, color="FF0000")
cell.fill = PatternFill("solid", fgColor="FFFF00")
cell.border = Border(bottom=Side(style="thin"))
cell.alignment = Alignment(horizontal="center")
cell.number_format = '0.00'
cell.protection = Protection(locked=True)

# Or set individual properties
cell.font.bold = True
cell.font.size = 14
cell.fill.start_color.rgb = "FF0000FF"
```

### Rich Text

```python
from openpyxl.cell.rich_text import CellRichText
from openpyxl.cell.text import InlineString, Text

# Rich text in cells (requires rich_text=True when loading)
from openpyxl.styles import Font
rt = CellRichText(
    "Bold ",
    InlineString(text=" and ", font=Font(italic=True)),
    InlineString(text="red", font=Font(color="FF0000"))
)
ws["A1"].value = rt
```

## Merged Cells

```python
# Merge a range
ws.merge_cells("A1:E1")
ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=5)

# Access merged cells collection
for merged_range in ws.merged_cells.ranges:
    print(merged_range)  # CellRange('A1:E1')

# Unmerge
ws.unmerge_cells("A1:E1")
ws.unmerge_cells(start_row=1, start_column=1, end_row=1, end_column=5)

# Note: only the top-left cell retains its value after merge
# Other cells become MergedCell objects with value=None
```

## Array Formulas

```python
from openpyxl.worksheet.formula import ArrayFormula

# Array formula spanning multiple cells
ws["A1"].value = ArrayFormula(formula="{=SUM(B1:B10*C1:C10)}", ref="A1:A2")
```

## Data Tables (Formulas)

```python
from openpyxl.worksheet.formula import DataTableFormula

# Data table formula
ws["A1"].value = DataTableFormula(
    formula="=PRICE($B$2,$B$3,$B$4,$B$5,$B$6,$B$7)",
    ref="C2:C11",
    row_input="A2:A11",
    col_input="B1:J1"
)
```

## Comments

```python
from openpyxl.comments import Comment

comment = Comment("This is a note", "Author Name")
comment.width = 200
comment.height = 50
ws["A1"].comment = comment

# Access comment
if ws["A1"].comment:
    print(ws["A1"].comment.text)
    print(ws["A1"].comment.author)

# Remove comment
ws["A1"].comment = None
```

## Hyperlinks

```python
# Simple hyperlink
ws["A1"].hyperlink = "https://example.com"
# Automatically sets cell value to the URL

# Custom display text
ws["A1"].value = "Click here"
ws["A1"].hyperlink = "https://example.com"

# Internal link (to another sheet/cell)
ws["A2"].hyperlink = "Sheet2!A1"

# With tooltip
from openpyxl.worksheet.hyperlink import Hyperlink
hl = Hyperlink(ref="A3", target="https://example.com", tooltip="Example Site")
ws["A3"].hyperlink = hl

# Remove hyperlink
ws["A1"].hyperlink = None
```

## Images

```python
from openpyxl.drawing.image import Image

# Requires Pillow: pip install Pillow
img = Image("photo.png")
img.width = 300
img.height = 200
ws.add_image(img, "A1")

# Multiple images at different positions
img1 = Image("chart.png")
ws.add_image(img1, "D1")
img2 = Image("logo.png")
ws.add_image(img2, "A20")
```
