# Styling

## Font

```python
from openpyxl.styles import Font

# Basic font
font = Font(name="Calibri", size=12, bold=True, italic=False, color="FF000000")

# All properties
font = Font(
    name="Arial",           # Font name
    size=11,                # Font size (sz alias)
    bold=True,              # (b alias)
    italic=True,            # (i alias)
    underline="single",     # "single", "double", "singleAccounting", "doubleAccounting"
    strikethrough=False,    # (strike alias)
    color="FF0000FF",       # RGB hex color
    vertAlign="superscript", # "superscript", "subscript", "baseline"
    outline=False,
    shadow=False,
    condense=False,
    extend=False,
    charset=None,
    family=2,               # 0-14, font family
    scheme="minor"          # "major", "minor"
)

# Apply to cell
ws["A1"].font = font

# Default font: Font(name="Calibri", sz=11, family=2, color=Color(theme=1), scheme="minor")
```

## Fill (Pattern and Gradient)

```python
from openpyxl.styles import PatternFill, GradientFill, Fill, Stop, Color

# Solid fill
fill = PatternFill("solid", fgColor="FFFF00")
ws["A1"].fill = fill

# Pattern fill with background
fill = PatternFill(
    patternType="darkGray",
    fgColor="FF0000",
    bgColor="FFFFFF"
)

# Available pattern types:
# solid, none, darkDown, darkGray, darkGrid, darkHorizontal, darkTrellis,
# darkUp, darkVertical, gray0625, gray125, lightDown, lightGray, lightGrid,
# lightHorizontal, lightTrellis, lightUp, lightVertical, mediumGray

# Gradient fill — linear
fill = GradientFill(
    stop=(
        Stop(color="FFFFFF", position=0),
        Stop(color="FF0000", position=1),
    )
)

# Gradient fill — path (from edges)
fill = GradientFill(
    type="path",
    degree=90,
    stop=(Stop("FF0000"), Stop("FFFFFF"))
)

# Gradient with multiple stops (auto-positioned)
fill = GradientFill(stop=("FF0000", "FFFF00", "FF00FF"))
```

## Border

```python
from openpyxl.styles import Border, Side

# Thin border on all sides
border = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin")
)
ws["A1"].border = border

# Colored border
border = Border(
    left=Side(style="medium", color="0000FF"),
    right=Side(style="medium", color="0000FF"),
    top=Side(style="medium", color="0000FF"),
    bottom=Side(style="medium", color="0000FF")
)

# Border styles:
# none, dashDot, dashDotDot, dashed, dotted, double, hair, medium,
# mediumDashDot, mediumDashDotDot, mediumDashed, slantDashDot, thick, thin

# Diagonal border
border = Border(
    diagonal=Side(style="thin"),
    diagonalUp=True,
    diagonalDown=True
)

# Apply border to a range
from openpyxl.utils import get_column_letter
for row in ws.iter_rows(min_row=1, max_row=5, min_col=1, max_col=3):
    for cell in row:
        cell.border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin")
        )
```

## Alignment

```python
from openpyxl.styles import Alignment

align = Alignment(
    horizontal="center",     # "general", "left", "center", "right", "fill",
                             # "justify", "centerContinuous", "distributed"
    vertical="center",       # "top", "center", "bottom", "justify", "distributed"
    textRotation=0,          # 0-180 degrees, or 255 for vertical text
    wrapText=True,           # Wrap text within cell
    shrinkToFit=False,       # Shrink text to fit
    indent=0,                # 0-255
    relativeIndent=0,        # -255 to 255
    justifyLastLine=None,
    readingOrder=0
)
ws["A1"].alignment = align

# Vertical text
ws["A1"].alignment = Alignment(textRotation=255)

# Centered with wrap
ws["A1"].alignment = Alignment(horizontal="center", vertical="center", wrapText=True)
```

## Color

```python
from openpyxl.styles import Color

# RGB color (8-char with alpha, or 6-char without)
color = Color("FF0000FF")   # Blue with full alpha
color = Color("00FF00")     # Green (alpha defaults to 00)

# Indexed color (from Excel's palette)
color = Color(indexed=10)

# Theme color
color = Color(theme=1, tint=0.5)

# Auto color
color = Color(auto=True)

# Color with tint
color = Color(rgb="FF0000", tint=0.3)

# Built-in color constants
from openpyxl.styles.colors import BLACK, WHITE, BLUE, COLOR_INDEX
# COLOR_INDEX is a tuple of 64 Excel default colors
```

## NamedStyle

Reusable styles that can be applied across cells.

```python
from openpyxl.styles import NamedStyle, Font, PatternFill, Border, Side, Alignment

# Create a named style
header_style = NamedStyle(
    name="Header",
    font=Font(bold=True, size=14, color="FFFFFF"),
    fill=PatternFill("solid", fgColor="4472C4"),
    alignment=Alignment(horizontal="center", vertical="center"),
    border=Border(
        bottom=Side(style="medium", color="4472C4")
    )
)

# Register with workbook
wb.add_named_style(header_style)

# Apply to cells
ws["A1"].style = "Header"
ws["B1"].style = "Header"

# List available styles
print(wb.named_styles)  # ['Normal', 'Header', ...]

# Built-in styles available:
# Normal, Heading 1-5, Title, Default, 20% - Accent 1-6,
# 40% - Accent 1-6, 60% - Accent 1-6, Good, Bad, Neutral,
# Note, Accent 1-6, Expiration, etc.

# Modify an existing style
style = wb.named_styles["Header"]
style.font.size = 16
# Changes auto-apply to workbook's style table

# Create style from scratch
from copy import copy
from openpyxl.styles import DEFAULT_FONT, DEFAULT_BORDER

new_style = NamedStyle(
    name="Custom",
    font=copy(DEFAULT_FONT),
    border=copy(DEFAULT_BORDER),
)
wb.add_named_style(new_style)
```

## Protection

```python
from openpyxl.styles import Protection

# Cell-level protection
ws["A1"].protection = Protection(locked=True, hidden=False)

# locked=True: cell cannot be edited when sheet protection is enabled
# hidden=True: formula is hidden in formula bar when sheet protection is enabled
```

## Applying Styles to Ranges

```python
# Style a range of cells
bold_font = Font(bold=True)
yellow_fill = PatternFill("solid", fgColor="FFFFCC")

for row in ws.iter_rows(min_row=1, max_row=10, min_col=1, max_col=5):
    for cell in row:
        cell.font = bold_font
        cell.fill = yellow_fill

# Style entire row
for cell in ws[5]:
    cell.fill = PatternFill("solid", fgColor="FFCCCB")

# Style entire column
for cell in ws["A"]:
    cell.number_format = '0.00'
```

## Differential Styles (for Conditional Formatting)

```python
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.styles import Font, PatternFill

diff = DifferentialStyle(
    font=Font(bold=True, color="FF0000"),
    fill=PatternFill("solid", fgColor="FFC7CE"),
    border=Border(all=Side(style="thin", color="FF0000"))
)
# Used in conditional formatting rules
```
