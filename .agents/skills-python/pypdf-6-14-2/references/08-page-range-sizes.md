# PageRange and PaperSize

## PageRange

`PageRange` provides slice-like page range parsing with a compact string syntax.

```python
from pypdf import PageRange

# Parse from string
range = PageRange("0:3")    # First 3 pages (0, 1, 2)
range = PageRange("::2")    # Every other page
range = PageRange("-1")     # Last page
range = PageRange("5:")     # From page 5 onward
range = PageRange(":")      # All pages

# From slice
range = PageRange(slice(0, 5))

# From another PageRange (copy)
range2 = PageRange(range)
```

### Syntax

| Expression | Meaning |
|---|---|
| `0` | Just page 0 |
| `0:3` | Pages 0, 1, 2 |
| `:3` | First 3 pages |
| `5:` | From page 5 to end |
| `:` | All pages |
| `-1` | Last page |
| `-2:` | Last 2 pages |
| `-3:-1` | Third and second to last |
| `::2` | Every other page (0, 2, 4, ...) |
| `1:10:2` | Pages 1, 3, 5, 7, 9 |
| `::-1` | All pages in reverse |
| `3:0:-1` | Pages 3, 2, 1 |

### Converting to Python Range

```python
from pypdf import PageRange, PdfReader

reader = PdfReader("document.pdf")
range = PageRange("0:5")

# Get indices safe for the document
indices = range.indices(len(reader.pages))
# Returns (start, stop, step) tuple

for i in range(*indices):
    text = reader.pages[i].extract_text()
    print(f"Page {i}: {len(text)} chars")
```

### Utility Methods

```python
range = PageRange("0:5")

# Convert to slice
sl = range.to_slice()

# Check validity
valid = PageRange.valid("0:5")   # True
valid = PageRange.valid("abc")   # False

# String representation
print(str(range))    # "0:5"
print(repr(range))   # "PageRange('0:5')"
```

### parse_filename_page_ranges

```python
from pypdf import parse_filename_page_ranges

# Parse filenames with embedded page ranges
# e.g., "document[0:5].pdf" → ("document.pdf", PageRange("0:5"))
filename, page_range = parse_filename_page_ranges("document[0:5].pdf")
# filename = "document.pdf"
# page_range = PageRange("0:5")

# Without page range
filename, page_range = parse_filename_page_ranges("document.pdf")
# filename = "document.pdf"
# page_range = None
```

## PaperSize

Standard paper dimensions in pixels at 72 ppi.

```python
from pypdf import PaperSize

# DIN A series
PaperSize.A0  # (2384, 3370) — 841mm x 1189mm
PaperSize.A1  # (1684, 2384)
PaperSize.A2  # (1191, 1684)
PaperSize.A3  # (842, 1191)
PaperSize.A4  # (595, 842)  — most common
PaperSize.A5  # (420, 595)  — paperback books
PaperSize.A6  # (298, 420)  — postcards
PaperSize.A7  # (210, 298)
PaperSize.A8  # (147, 210)

# Envelopes
PaperSize.C4  # (649, 918)
```

Each value is a `Dimensions(width, height)` named tuple.

### Usage

```python
from pypdf import PdfWriter, PaperSize

writer = PdfWriter()

# Use paper size for blank page
page = writer.add_blank_page(*PaperSize.A4)

# Unpack
width, height = PaperSize.A3
page = writer.add_blank_page(width, height)

# Check dimensions
print(PaperSize.A4.width)   # 595
print(PaperSize.A4.height)  # 842
```

### Calculation

Paper sizes are calculated from millimeters:
1. Get size in millimeters
2. Convert to inches (÷ 25.4)
3. Convert to pixels at 72 ppi (× 72)

A0 is defined as 1 m² with aspect ratio 1:√2. Each subsequent size halves the area.
