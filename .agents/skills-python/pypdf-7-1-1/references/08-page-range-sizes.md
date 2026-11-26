# PageRange and PaperSize

## PageRange

Slice-like page ranges, zero-based. Construct from a slice, a `PageRange`
(copy), or a string `"int"` / `"[int]:[int]"` / `"[int]:[int]:[int]"`.

```python
from pypdf import PageRange

PageRange("0:3")     # first three pages
PageRange("3")       # ONLY the fourth page (bare int = single page!)
PageRange(slice(3))  # first three pages (slice semantics)
PageRange("-1")      # last page
PageRange(":-1")     # all but the last
PageRange("-2:")     # last two
PageRange("5:")      # from the sixth page onward
PageRange("::2")     # every second page
PageRange("1:10:2")  # 1 3 5 7 9
PageRange("::-1")    # all pages reversed
```

A zero step is rejected — `PageRange("::0")` raises `ParseError` (7.1.1).

```python
pr = PageRange("0:3")
pr.valid("0:3")      # True — class method checking parseability
pr.to_slice()        # slice(0, 3, None)
pr.indices(10)       # (0, 3, 1) — start, stop, step for range()
pr + PageRange("5")  # PageRange concatenation (7.x)

for i in range(*pr.indices(len(reader.pages))):
    ...
```

Use in `PdfWriter.append`/`merge` `pages=` directly:

```python
writer.append("doc.pdf", pages=PageRange("0:10"))
writer.append("doc.pdf", pages=(0, 10))     # (start, stop[, step]) tuple
writer.append("doc.pdf", pages=[0, 2, 4])   # explicit list
```

## parse_filename_page_ranges

Pair filenames with page-range expressions in a flat argument list — the
first argument must be a filename; each following argument is either a new
filename or a page range for the preceding one:

```python
from pypdf import parse_filename_page_ranges

# -> [("doc.pdf", PageRange("0:5")), ("other.pdf", all-pages)]
pairs = parse_filename_page_ranges(["doc.pdf", "0:5", "other.pdf"])
for filename, page_range in pairs:
    writer.append(filename, pages=page_range)
```

A filename not followed by a range means all pages. Useful for bulk
splitting/merging scripts driven by CLI arguments.

## PaperSize

Standard paper dimensions in points (1/72 inch):

```python
from pypdf import PaperSize

PaperSize.A4   # Dimensions(595, 842) — the most common
PaperSize.A0   # Dimensions(2384, 3370)
PaperSize.A8   # Dimensions(147, 210)
# A1, A2, A3, A5, A6, A7 in between
```

Each is a `Dimensions(width, height)` namedtuple — unpack with
`w, h = PaperSize.A4` or use `.width`/`.height`.

```python
writer.add_blank_page(width=PaperSize.A4.width, height=PaperSize.A4.height)
```

Note the A-series is defined so A0 has an area of 1 m²; each step halves
one dimension.
