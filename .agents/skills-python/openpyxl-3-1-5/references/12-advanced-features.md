# Advanced Features

## Sheet Protection

```python
from openpyxl.worksheet.protection import SheetProtection

# Enable sheet protection
ws.protection.sheet = True
ws.protection.enable()

# Set password (weak hashing, not secure)
ws.protection.set_password("secret")

# Control what users can do
ws.protection.formatCells = False      # Allow formatting cells
ws.protection.formatColumns = False
ws.protection.formatRows = False
ws.protection.insertColumns = False
ws.protection.insertRows = False
ws.protection.insertHyperlinks = False
ws.protection.deleteColumns = False
ws.protection.deleteRows = False
ws.protection.selectLockedCells = True      # Allow selecting locked cells
ws.protection.selectUnlockedCells = True    # Allow selecting unlocked cells
ws.protection.sort = False
ws.protection.autoFilter = False
ws.protection.pivotTables = False

# Disable protection
ws.protection.sheet = False
ws.protection.disable()

# Note: cell-level protection (locked/hidden) only takes effect
# when sheet protection is enabled
```

## Cell-Level Protection

```python
from openpyxl.styles import Protection

# Lock a cell (default: all cells are locked)
ws["A1"].protection = Protection(locked=True, hidden=False)

# Unlock a cell (editable even with sheet protection)
ws["B1"].protection = Protection(locked=False, hidden=False)

# Hide formula (visible only without sheet protection)
ws["C1"].protection = Protection(locked=True, hidden=True)
```

## Workbook Protection

```python
from openpyxl.workbook.protection import DocumentSecurity

# Workbook structure protection
wb.security.workbookPassword = "hash"  # Hashed password
wb.security.revisionPassword = "hash"  # Hashed password

# Lock structure (prevent adding/deleting/moving sheets)
wb.security.lockStructure = True

# Lock windows (prevent resizing/moving workbook window)
wb.security.lockWindows = True
```

## Pivot Tables

Reading pivot tables from existing files:

```python
from openpyxl import load_workbook

wb = load_workbook("pivot.xlsx")
ws = wb.active

# Access pivot tables
for pivot in ws._pivots:
    print(pivot.name)
    print(pivot.cache)

# Pivot table properties
pivot = ws._pivots[0]
pivot.name              # Pivot table name
pivot.cache             # PivotCacheDefinition
pivot.location          # Location (ref, firstHeaderRow, etc.)
pivot.rowFields         # Row fields
pivot.colFields         # Column fields
pivot.pageFields        # Page/filter fields
pivot.dataFields        # Data/value fields
pivot.rowGrandTotals    # Show row grand totals
pivot.colGrandTotals    # Show column grand totals

# Note: openpyxl can READ pivot tables but cannot CREATE them programmatically
# Pivot tables must be created in Excel and then read/modified
```

## Defined Names (Named Ranges)

```python
from openpyxl.workbook.defined_name import DefinedName

# Global named range
dn = DefinedName("TotalRevenue", "'Sheet1'!$B$2:$B$100")
dn.attr_text = "'Sheet1'!$B$2:$B$100"
wb.defined_names["TotalRevenue"] = dn

# Sheet-scoped named range
dn = DefinedName("Headers", "$A$1:$D$1", scope="Sheet1")
ws.defined_names["Headers"] = dn

# Access
dn = wb.defined_names["TotalRevenue"]
print(dn.attr_text)     # "'Sheet1'!$B$2:$B$100"
print(dn.scope)         # None (global) or sheet name

# Comment on defined name
dn.comment = "Sum of all revenue"

# Iterate defined names
for name in wb.defined_names:
    print(name, wb.defined_names[name].attr_text)
```

## External Links

```python
from openpyxl.workbook.external_link import ExternalLink

# External links are preserved when loading with keep_links=True
wb = load_workbook("file.xlsx", keep_links=True)

# Access external links
for link in wb.external_links:
    print(link)
```

## Rich Text in Cells

```python
from openpyxl.cell.rich_text import CellRichText
from openpyxl.cell.text import InlineString
from openpyxl.styles import Font

# Create rich text
rt = CellRichText(
    "Regular text ",
    InlineString(text="bold text", font=Font(bold=True)),
    " and ",
    InlineString(text="red text", font=Font(color="FF0000")),
)

ws["A1"].value = rt

# Load with rich_text=True to preserve
wb = load_workbook("file.xlsx", rich_text=True)
```

## Comments

```python
from openpyxl.comments import Comment

# Add comment
comment = Comment("This cell contains important data", "Author")
comment.width = 200
comment.height = 50
ws["A1"].comment = comment

# Access comment
if ws["A1"].comment:
    print(ws["A1"].comment.text)
    print(ws["A1"].comment.author)

# Copy comment
import copy
new_comment = copy.copy(ws["A1"].comment)
ws["B1"].comment = new_comment

# Remove comment
ws["A1"].comment = None
```

## Hyperlinks

```python
from openpyxl.worksheet.hyperlink import Hyperlink

# Simple URL
ws["A1"].hyperlink = "https://example.com"
ws["A1"].value = "Example"  # Display text

# Internal link
ws["A2"].hyperlink = "Sheet2!A1"

# Full hyperlink object
hl = Hyperlink(
    ref="A3",
    target="https://example.com",
    tooltip="Visit Example",
    location="Section1"
)
ws["A3"].hyperlink = hl

# Remove hyperlink
ws["A1"].hyperlink = None
```

## Images

```python
from openpyxl.drawing.image import Image

# Requires Pillow: pip install Pillow

# Load image
img = Image("photo.png")
print(img.width, img.height)  # Original dimensions

# Resize
img.width = 300
img.height = 200

# Add to worksheet
ws.add_image(img, "A1")

# Multiple images
img1 = Image("chart.png")
ws.add_image(img1, "D1")

img2 = Image("logo.jpg")
ws.add_image(img2, "A20")
```

## Drawing Objects

```python
from openpyxl.drawing.drawing import Drawing

# Create a drawing container
drawing = Drawing()
drawing.width = 500
drawing.height = 300
drawing.left = 100
drawing.top = 50
drawing.resize_proportional = True
```

## Calculation Properties

```python
from openpyxl.workbook.properties import CalcProperties

# Workbook calculation settings
wb.calculation.calcOnSave = True       # Calculate on save
wb.calculation.fullCalcOnLoad = True   # Full calculation on load
wb.calculation.iterateCount = 100      # Iteration count
wb.calculation.refMode = "A1"          # "A1" or "R1C1"
wb.calculation.calcCompleted = 0       # Calculation completed flag
```
