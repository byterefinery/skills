# Sheets and Views

## Sheet Visibility

```python
# Show/hide sheets
ws.sheet_state = "visible"       # Normal display
ws.sheet_state = "hidden"        # Hidden (user can unhide via UI)
ws.sheet_state = "veryHidden"    # Hidden (can only be unhidden programmatically)
```

## Freeze Panes

```python
# Freeze top row
ws.freeze_panes = "A2"

# Freeze first column
ws.freeze_panes = "B1"

# Freeze both top row and first column
ws.freeze_panes = "B2"

# Freeze top 3 rows and first 2 columns
ws.freeze_panes = "C4"

# Remove freeze panes
ws.freeze_panes = None
ws.freeze_panes = "A1"  # A1 is treated as no freeze

# Check current freeze
print(ws.freeze_panes)  # "A2" or None
```

## Sheet View

```python
# Access the active sheet view
view = ws.sheet_view

# Gridlines
view.showGridLines = True

# Show formulas instead of values
view.showFormulas = True

# Show row/column headers
view.showRowColHeaders = True

# Show zeros
view.showZeros = True

# Right-to-left
view.rightToLeft = False

# Tab selected
view.tabSelected = True

# Show outline symbols (grouping buttons)
view.showOutlineSymbols = True

# Show ruler
view.showRuler = False

# View mode
view.view = "normal"           # "normal", "pageBreakPreview", "pageLayout"

# Zoom
view.zoomScale = 75            # Percentage (0-400, None = 100%)
view.zoomScaleNormal = 100     # Normal view zoom
view.zoomScaleSheetLayoutView = 100
view.zoomScalePageLayoutView = 100

# Top-left cell
view.topLeftCell = "A1"

# Window protection
view.windowProtection = False

# Default grid color
view.defaultGridColor = False

# Show whitespace
view.showWhiteSpace = True
```

## Split Panes

```python
from openpyxl.worksheet.views import Pane, Selection

# Split at specific position
pane = Pane(
    xSplit=2,           # Split after 2 columns
    ySplit=3,           # Split after 3 rows
    topLeftCell="D4",   # Active cell in bottom-right pane
    activePane="bottomRight",
    state="split"
)

view = ws.sheet_view
view.pane = pane
```

## Selection

```python
from openpyxl.worksheet.views import Selection

# Set selected cell
ws.selected_cell = "A1"

# Set active cell
ws.active_cell = "A1"

# Multiple selections
view = ws.sheet_view
view.selection = [
    Selection(sqref="A1:D10", activeCell="A1"),
    Selection(sqref="F1:F5", activeCell="F1"),
]
```

## Tab Color

```python
from openpyxl.styles import Color

# Set sheet tab color
ws.sheet_properties.tabColor = Color("4472C4")
ws.sheet_properties.tabColor = Color(theme=1)
ws.sheet_properties.tabColor = Color(indexed=10)

# Remove tab color
ws.sheet_properties.tabColor = None
```

## Code Name (VBA Compatibility)

```python
# Set code name for VBA reference
ws.code_name = "Sheet1"
```

## Moving and Copying Sheets

```python
# Move sheet
wb.move_sheet(ws, offset=-1)   # Move one position left
wb.move_sheet(ws, offset=2)    # Move two positions right

# Copy sheet (within same workbook only)
ws_copy = wb.copy_worksheet(ws)
# Note: does NOT work in read-only or write-only mode
```

## Right-to-Left

```python
# Enable RTL layout
ws.sheet_view.rightToLeft = True
```

## Page Break Preview

```python
# Switch to page break preview
ws.sheet_view.view = "pageBreakPreview"

# Switch to page layout view
ws.sheet_view.view = "pageLayout"

# Normal view
ws.sheet_view.view = "normal"
```

## Workbook Views

```python
from openpyxl.workbook.views import BookView

# Workbook-level view settings
view = BookView()
view.xWindow = 0
view.yWindow = 0
view.windowWidth = 14000
view.windowHeight = 6000
view.firstSheet = 0
view.activeSheet = 0
view.autoFilter = True
view.showHorizontalScroller = True
view.showVerticalScroller = True
view.showWorkbookTabs = True
view.tabRatio = 500
view.visibility = "visible"  # "visible", "hidden", "veryHidden", "readOnly"

wb.views.append(view)
```
