# Row and Column Operations

## Column Dimensions

```python
# Access column dimensions
col = ws.column_dimensions["A"]

# Set width (in character units, not pixels)
ws.column_dimensions["A"].width = 20
ws.column_dimensions["B"].width = 15.5

# Hide a column
ws.column_dimensions["C"].hidden = True

# Set best-fit (auto-size)
ws.column_dimensions["A"].bestFit = True

# Outline level for grouping
ws.column_dimensions["A"].outlineLevel = 1
ws.column_dimensions["A"].collapsed = True

# Style a column dimension
ws.column_dimensions["A"].style = "Currency"

# Default column width for the sheet
ws.sheet_format.defaultColWidth = 12
```

### Column Range Grouping

```python
# Group columns B through D
ws.column_dimensions.group("B", "D", outline_level=1, hidden=False)

# Access grouped columns
for col_range in ws.column_groups:
    print(col_range)  # "B:D"

# Individual column properties
col = ws.column_dimensions["A"]
col.min      # Minimum column index in group
col.max      # Maximum column index in group
col.range    # "A:C" — range string
col.width    # Column width
col.hidden   # True if hidden
col.outlineLevel  # Outline level (0-7)
col.collapsed    # True if group is collapsed
```

## Row Dimensions

```python
# Access row dimensions
row = ws.row_dimensions[1]

# Set height (in points)
ws.row_dimensions[1].height = 30

# Hide a row
ws.row_dimensions[2].hidden = True

# Outline level for grouping
ws.row_dimensions[5].outlineLevel = 1
ws.row_dimensions[5].collapsed = True

# Style a row dimension
ws.row_dimensions[1].style = "Heading 1"

# Default row height for the sheet
ws.sheet_format.defaultRowHeight = 15
```

### Row Grouping

```python
# Group rows 2 through 10
ws.row_dimensions.group(2, 10, outline_level=1, hidden=False)

# Row dimension properties
row = ws.row_dimensions[1]
row.ht             # Row height
row.hidden         # True if hidden
row.outlineLevel   # Outline level (0-7)
row.collapsed      # True if group is collapsed
row.customHeight   # True if height is explicitly set
row.thickTop       # Thick top border
row.thickBottom    # Thick bottom border
```

## Sheet Format Properties

```python
# Global sheet formatting
ws.sheet_format.baseColWidth = 8           # Base column width (default 8)
ws.sheet_format.defaultColWidth = 10       # Default column width override
ws.sheet_format.defaultRowHeight = 15      # Default row height (default 15)
ws.sheet_format.zeroHeight = True          # Allow zero-height rows (for hidden rows)
ws.sheet_format.thickTop = True            # Thick top border
ws.sheet_format.thickBottom = True         # Thick bottom border
ws.sheet_format.outlineLevelRow = 2        # Maximum row outline level
ws.sheet_format.outlineLevelCol = 1        # Maximum column outline level
```

## Hiding Rows/Columns

```python
# Hide individual
ws.column_dimensions["C"].hidden = True
ws.row_dimensions[5].hidden = True

# Hide via grouping (can be toggled by user)
ws.column_dimensions.group("D", "F", outline_level=1, hidden=True)
ws.row_dimensions.group(10, 20, outline_level=1, hidden=True)

# Zero-height row (completely hidden, no toggle)
ws.row_dimensions[5].height = 0
ws.sheet_format.zeroHeight = True
```

## Outline Levels

```python
# Column outlines
for col in "ABC":
    ws.column_dimensions[col].outlineLevel = 1
ws.column_dimensions["D"].outlineLevel = 2

# Row outlines
for row in range(2, 11):
    ws.row_dimensions[row].outlineLevel = 1
ws.row_dimensions[11].outlineLevel = 2

# Collapse groups
ws.column_dimensions["A"].collapsed = True
ws.row_dimensions[1].collapsed = True

# Toggle outline symbols visibility
ws.sheet_view.showOutlineSymbols = True
```

## Column Width Best Practices

```python
# Default width is ~9.14 character units
# 1 character unit ≈ width of '0' in default font

# Common widths
ws.column_dimensions["A"].width = 10    # Short text
ws.column_dimensions["B"].width = 20    # Medium text
ws.column_dimensions["C"].width = 40    # Long text / URLs
ws.column_dimensions["D"].width = 5     # Numbers / IDs

# Auto-size columns (estimate based on content)
from openpyxl.utils import get_column_letter

def auto_size worksheet(ws):
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
```
