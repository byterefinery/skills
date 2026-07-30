# Generic Types

## PDF Object Model

pypdf represents PDF objects as Python classes. All inherit from `PdfObject`.

### Base Types

```python
from pypdf.generic import (
    PdfObject,           # Base class
    BooleanObject,       # True/False
    NumberObject,        # Integer numbers
    FloatObject,         # Floating-point numbers
    NameObject,          # PDF names (e.g., "/Title")
    TextStringObject,    # Decoded text strings
    ByteStringObject,    # Raw byte strings
    NullObject,          # null/None
    ArrayObject,         # Lists/arrays
    DictionaryObject,    # Dicts/dictionaries
    StreamObject,        # Data streams
    IndirectObject,      # References to other objects
)
```

### NameObject

```python
from pypdf.generic import NameObject

# PDF names start with /
name = NameObject("/Title")
name = NameObject("/Pages")
name = NameObject("/MediaBox")

# String representation includes the /
print(str(name))  # "/Title"
```

### TextStringObject vs ByteStringObject

```python
from pypdf.generic import TextStringObject, ByteStringObject

# TextStringObject — decoded Unicode text
text = TextStringObject("Hello World")

# ByteStringObject — raw bytes
raw = ByteStringObject(b"\xff\xfe")
```

### ArrayObject

```python
from pypdf.generic import ArrayObject, NumberObject

# PDF arrays
arr = ArrayObject([NumberObject(0), NumberObject(100), NumberObject(0), NumberObject(792)])
# Represents: [0, 100, 0, 792]
```

### DictionaryObject

```python
from pypdf.generic import DictionaryObject, NameObject, TextStringObject

# PDF dictionaries
d = DictionaryObject()
d[NameObject("/Title")] = TextStringObject("My Document")
d[NameObject("/Author")] = TextStringObject("Author Name")
```

Most pypdf objects (PageObject, PdfReader, PdfWriter) inherit from DictionaryObject.

## RectangleObject

```python
from pypdf.generic import RectangleObject

# Create rectangle [x1, y1, x2, y2]
rect = RectangleObject([0, 0, 612, 792])

# Access corners
print(rect.lower_left)   # (0, 0)
print(rect.upper_right)  # (612, 792)
print(rect.lower_right)  # (612, 0)
print(rect.upper_left)   # (0, 792)

# Dimensions
width = rect.width    # 612
height = rect.height  # 792

# Modify
rect.lower_left = (10, 10)
rect.upper_right = (600, 780)
```

### Usage with pages

```python
page = reader.pages[0]

# Set media box
page.mediabox = RectangleObject([0, 0, 612, 792])

# Set crop box
page.cropbox = [50, 50, 562, 742]  # Also accepts list

# Read dimensions
width = float(page.mediabox.width)
height = float(page.mediabox.height)
```

## Destination and Fit

```python
from pypdf.generic import Destination, Fit

# Create destination
dest = Destination(
    "chapter1",           # title
    writer.pages[0],      # page
    Fit.fit(),            # fit type
)

# Fit types
Fit.fit()                # Fit page to window
Fit.fit_horizontal(100)  # Fit horizontal at Y
Fit.fit_vertical(100)    # Fit vertical at X
Fit.fit_rectangle(0, 0, 100, 100)  # Fit rectangle
Fit.fit_width(100)       # Fit width at Y
Fit.fit_height(100)      # Fit height at X
```

## EmbeddedFile

```python
from pypdf.generic import EmbeddedFile

# Returned by writer.add_attachment()
embedded = writer.add_attachment("data.txt", "content")

print(embedmed.filename)
print(embedmed.data)
```

## Utility Functions

```python
from pypdf.generic import (
    create_string_object,    # Auto-detect string type
    is_null_or_none,         # Check for null/None
    extract_links,           # Extract links from content
    hex_to_rgb,              # Convert hex color to RGB
    read_object,             # Read PDF object from stream
)

# Create string object (auto-detects text vs bytes)
obj = create_string_object("Hello")
obj = create_string_object(b"\xff\xfe")

# Check for null
if is_null_or_none(obj):
    print("Object is null or None")

# Hex to RGB
rgb = hex_to_rgb("#FF0000")  # (1.0, 0.0, 0.0)
```

## ContentStream

```python
from pypdf.generic import ContentStream

# Parse page content stream
content = page.get_contents()

if content:
    # Iterate operations
    for operation in content:
        print(operation)
```

## Field

```python
from pypdf.generic import Field

# Form field object
# Access via reader.get_form_text_fields() or AcroForm traversal
```

## TreeObject

```python
from pypdf.generic import TreeObject

# Hierarchical tree structure (used for outlines, etc.)
```

## ViewerPreferences

```python
from pypdf.generic import ViewerPreferences

# Control PDF viewer behavior
prefs = ViewerPreferences()
prefs.RotatePages = True
prefs.HideToolbar = True
prefs.HideMenubar = True
prefs.HideWindowUI = True
prefs.FitWindow = True
prefs.CenterWindow = True
prefs.NonFullScreenPageMode = "UseNone"
```
