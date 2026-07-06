# Page Layout

## Page Setup

```python
# Orientation
ws.page_setup.orientation = "portrait"   # "portrait", "landscape", "default"

# Paper size
ws.page_setup.paperSize = 9              # 9 = A4, 1 = Letter, see constants below

# Scale to fit
ws.page_setup.scale = 80                 # Percentage (10-400)
ws.page_setup.fitToWidth = 1             # Fit to N pages wide
ws.page_setup.fitToHeight = 0            # 0 = automatic height

# Page order
ws.page_setup.pageOrder = "overThenDown"  # "overThenDown", "downThenOver"

# Other options
ws.page_setup.blackAndWhite = False
ws.page_setup.draft = False
ws.page_setup.usePrinterDefaults = False
ws.page_setup.firstPageNumber = 1
ws.page_setup.useFirstPageNumber = True
ws.page_setup.cellComments = "asDisplayed"  # "asDisplayed", "atEnd"
ws.page_setup.errors = "NA"                 # "displayed", "blank", "dash", "NA"
ws.page_setup.copies = 1

# Fit to page (enables/disables fitToWidth/fitToHeight)
ws.page_setup.fitToPage = True

# Auto page breaks
ws.page_setup.autoPageBreaks = False
```

### Paper Size Constants

```python
ws.PAPERSIZE_LETTER = '1'
ws.PAPERSIZE_LETTER_SMALL = '2'
ws.PAPERSIZE_TABLOID = '3'
ws.PAPERSIZE_LEDGER = '4'
ws.PAPERSIZE_LEGAL = '5'
ws.PAPERSIZE_STATEMENT = '6'
ws.PAPERSIZE_EXECUTIVE = '7'
ws.PAPERSIZE_A3 = '8'
ws.PAPERSIZE_A4 = '9'
ws.PAPERSIZE_A4_SMALL = '10'
ws.PAPERSIZE_A5 = '11'
```

## Page Margins

```python
# Margins in inches
ws.page_margins.left = 0.75
ws.page_margins.right = 0.75
ws.page_margins.top = 1.0
ws.page_margins.bottom = 1.0
ws.page_margins.header = 0.5
ws.page_margins.footer = 0.5
```

## Print Options

```python
# Center page
ws.print_options.horizontalCentered = True
ws.print_options.verticalCentered = True

# Print grid lines
ws.print_options.gridLines = True
ws.print_options.gridLinesSet = True

# Print row/column headings
ws.print_options.headings = True
```

## Print Area

```python
# Set print area
ws.print_area = "A1:D20"

# Multiple print areas
ws.print_area = ["A1:D10", "F1:J10"]

# Clear print area
ws.print_area = None
ws.print_area = []
```

## Print Titles (Repeat Rows/Columns)

```python
# Repeat rows at top of each page
ws.print_title_rows = "1:3"

# Repeat columns at left of each page
ws.print_title_cols = "A:B"

# Combined
print(ws.print_titles)  # Defined name for print titles
```

## Page Breaks

```python
# Row break
ws.row_breaks.row_breaks = [(5,), (15,)]

# Column break
ws.col_breaks.col_breaks = [(3,), (8,)]
```

## Headers and Footers

```python
from openpyxl.worksheet.header_footer import HeaderFooter, HeaderFooterItem

# Create header/footer
header = HeaderFooter()
footer = HeaderFooter()

# Odd pages (default)
header.oddHeader.center.text = "Report Title"
header.oddFooter.center.text = "Page &P of &N"
header.oddFooter.left.text = "&D"          # Current date
header.oddFooter.right.text = "&T"         # Current time

# Even pages
header.differentOddEven = True
header.evenHeader.center.text = "Even Page Header"

# First page
header.differentFirst = True
header.firstHeader.center.text = "Cover Page"

# Apply to worksheet
ws.header_footer.oddHeader = header.oddHeader
ws.header_footer.oddFooter = header.oddFooter

# Scale header/footer with document
ws.header_footer.scaleWithDoc = True
ws.header_footer.alignWithMargins = True
```

### Header/Footer Codes

```
&A or &[Tab]        — Worksheet name
&B                  — Toggle bold
&D or &[Date]       — Current date
&E                  — Toggle double-underline
&F or &[File]       — Workbook name
&I                  — Toggle italic
&N or &[Pages]      — Total page count
&S                  — Toggle strikethrough
&T                  — Current time
&P or &[Page]       — Current page number
&P+n                — Page number + n
&P-n                — Page number - n
&[Path]             — Workbook path
&&                  — Literal ampersand
&"fontname"         — Select font
&nn                 — Font size (2-digit)
&KRRGGBB            — Color (hex RGB)
&G                  — Header picture
```

### Header/Footer Example

```python
# Center: "Monthly Report" in 14pt Arial, bold
# Right: page number
# Footer center: date and file name

from openpyxl.worksheet.header_footer import _HeaderFooterPart

ws.header_footer.oddHeader.center = _HeaderFooterPart(
    text="Monthly Report",
    font="Arial",
    size=14,
    color=None
)
ws.header_footer.oddHeader.right = _HeaderFooterPart(
    text="Page &P of &N"
)
ws.header_footer.oddFooter.center = _HeaderFooterPart(
    text="&D — &F"
)
```

## Sheet Properties (Page Setup)

```python
# Page setup primitives
ws.sheet_properties.pageSetUpPr = ...

# Fit to page
ws.sheet_properties.pageSetUpPr.fitToPage = True

# Auto page breaks
ws.sheet_properties.pageSetUpPr.autoPageBreaks = True

# Tab color
from openpyxl.styles import Color
ws.sheet_properties.tabColor = Color("4472C4")
```
