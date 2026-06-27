# Accessors Reference

`.str`, `.dt`, `.cat` accessor methods, and the `.array` property.

## String Accessor (`.str`)

Vectorized string operations on Series/Index. Works with `object`, `string`, and Arrow-backed string dtypes.

```python
s = pd.Series(["Hello World", "foo bar", None, "TEST case"])
```

### Case Conversion

```python
s.str.lower()         # "hello world"
s.str.upper()         # "HELLO WORLD"
s.str.title()         # "Hello World"
s.str.capitalize()    # "hello world" → "Hello world"
s.str.swapcase()      # "hELLO wORLD"
```

### Cleaning and Padding

```python
s.str.strip()             # Remove whitespace from both ends
s.str.lstrip()            # Remove from left
s.str.rstrip()            # Remove from right
s.str.replace("old", "new")
s.str.replace({"old": "new", "foo": "bar"})  # v3.0: dict of replacements
s.str.pad(10, side="left")           # Pad to length 10
s.str.center(10)                     # Center in width 10
s.str.zfill(10)                      # Zero-fill to length 10
```

### Splitting and Joining

```python
# Split → list per element
s.str.split()                    # Split on whitespace
s.str.split(",")                 # Split on comma
s.str.split(",", n=1)            # Max 1 split
s.str.split(r"\s+", regex=True)  # Regex split

# Split to columns (DataFrame)
s.str.split(",", expand=True)    # Each part → separate column

# Join
s.str.join("-")                   # Join list elements with "-"
```

### Substring and Extraction

```python
# Get character(s) by position
s.str[0]                          # First character
s.str[-1]                         # Last character
s.str.slice(0, 5)                 # Characters 0-4
s.str.slice(start=0, stop=5, step=2)

# Extract with regex
s.str.extract(r"([A-Z]+)")        # Extract first capture group
s.str.extract(r"(?P<word>\w+)")   # Named groups → column names
s.str.extractall(r"(\d+)")        # All matches (MultiIndex result)

# Find
s.str.find("hello")               # Start index of substring (-1 if not found)
s.str.rfind("hello")              # Last occurrence
s.str.contains("hello", regex=True)  # Boolean mask
s.str.match(r"^\d+")              # Match from start
s.str.fullmatch(r"\d{3}")         # Full string match
```

### Counting and Length

```python
s.str.len()                       # String length (NA for missing)
s.str.count("o")                  # Count occurrences of "o"
```

### Replacement

```python
s.str.replace("old", "new")
s.str.replace(r"\d+", "NUM", regex=True)
s.str.replace({"a": "1", "b": "2"})  # v3.0: dict mapping
s.str.replace(r"\s+", "-", regex=True, n=0)  # All occurrences
```

### v3.0 Additions

```python
# isascii check
s.str.isascii()                   # Boolean mask: all ASCII characters?

# get_dummies with dtype parameter
s.str.get_dummies(sep=",", dtype="uint8")
```

### Other String Methods

```python
s.str.startswith("Hello")         # Boolean mask
s.str.endswith("World")
s.str.isalnum()                   # Alphanumeric
s.str.isalpha()                   # Alphabetic
s.str.isdigit()                   # Digits
s.str.isspace()                   # Whitespace
s.str.islower(), s.str.isupper()  # Case checks
s.str.isnumeric(), s.str.isdecimal()

# Encode/decode
s.str.encode("utf-8")             # → bytes
s.str.decode("utf-8")             # From bytes

# Translate
s.str.translate(str.maketrans("ae", "12"))  # Character mapping
```

## Datetime Accessor (`.dt`)

Access datetime components from Series with datetime-like dtype.

```python
s = pd.to_datetime(["2024-01-15 14:30:45", "2024-06-20 09:15:00"])
```

### Components

```python
s.dt.year            # 2024
s.dt.month           # 1, 6
s.dt.day             # 15, 20
s.dt.hour            # 14, 9
s.dt.minute          # 30, 15
s.dt.second          # 45, 0
s.dt.microsecond
s.dt.nanosecond

# Calendar
s.dt.dayofweek       # 0=Monday, 6=Sunday
s.dt.day_of_week     # Alias
s.dt.weekday_name    # "Monday", "Thursday"
s.dt.dayofyear       # Day of year (1-366)
s.dt.weekofyear      # Week number
s.dt.quarter         # 1-4

# Boolean flags
s.dt.is_month_start
s.dt.is_month_end
s.dt.is_quarter_start
s.dt.is_quarter_end
s.dt.is_year_start
s.dt.is_year_end
s.dt.is_leap_year
```

### Timezone Operations

```python
s.dt.tz               # Current timezone
s.dt.tz_localize("UTC")       # Attach timezone (to naive)
s.dt.tz_convert("America/New_York")  # Convert timezone
```

### Rounding

```python
s.dt.round("H")      # Round to nearest hour
s.dt.floor("D")      # Floor to day
s.dt.ceil("ME")      # Ceiling to month end
s.dt.snap(freq="H")  # Snap to nearest frequency
```

### Date Offset Operations

```python
s.dt + pd.DateOffset(days=7)
s.dt.to_period("M")       # → PeriodIndex
s.dt.to_pydatetime()      # → list of datetime objects
s.dt.strftime("%Y-%m-%d") # → formatted strings
```

## Categorical Accessor (`.cat`)

Operations on categorical Series.

```python
s = pd.Series(["low", "med", "high"], dtype="category")
```

### Properties

```python
s.cat.categories          # Index of category names
s.cat.ordered             # Whether categories are ordered
s.cat.codes               # Integer codes (-1 for NA)
```

### Operations

```python
# Modify categories
s.cat.add_categories(["critical"])
s.cat.remove_categories(["low"])
s.cat.rename_categories({"low": "Low", "med": "Medium"})
s.cat.reorder_categories(["low", "high", "med"])  # New order

# Ordered/unordered conversion
s.cat.as_ordered()
s.cat.as_unordered()

# Remove unused categories
s.cat.remove_unused_categories()
```

## `.array` Property

Access the underlying ExtensionArray.

```python
arr = df["col"].array
type(arr)  # e.g., StringArray, IntegerArray, ArrowExtensionArray

# Operations on the array
arr.dtype
arr.isna()
arr.copy()
```

## Gotchas

- **`.str` works on `object`, `string`, and Arrow-backed strings** — but behavior may differ slightly between backends.
- **`.str` methods return NA for missing values** — they don't raise errors.
- **`.str.contains()` uses regex by default** — pass `regex=False` for literal string matching (faster).
- **`.str.split(expand=True)` returns a DataFrame** — column names are integers (0, 1, 2...). Rename with `.rename(columns={...})`.
- **`.dt` accessor requires datetime-like dtype** — convert first with `pd.to_datetime()` if needed.
- **`.cat.codes` uses -1 for NA** — not the typical NA sentinel.
- **v3.0: `.str.isascii()` added** — checks if all characters are ASCII (code points 0-127).
- **v3.0: `.str.replace()` accepts dict** — maps patterns to replacements in one call.
- **Arrow-backed strings may have different `.str` behavior** — some methods are implemented via PyArrow and may handle edge cases differently.
