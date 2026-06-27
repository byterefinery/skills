# Dates and Math

## Date/Time Functions

### Parsing

| Function | Description |
|----------|-------------|
| `now` | Current Unix timestamp (seconds since epoch) |
| `now \| strftime(fmt)` | Format current time |
| `strftime(fmt)` | Format Unix timestamp to string (UTC) |
| `strflocaltime(fmt)` | Format Unix timestamp to string (local timezone) |
| `strptime(fmt)` | Parse date string to Unix timestamp (returns `[seconds, nanoseconds]`) |
| `mktime` | Convert `[seconds, nanoseconds]` to Unix timestamp |
| `todate` | Unix timestamp → ISO 8601 string (`"2024-01-15T10:30:00Z"`) |
| `fromdate` | ISO 8601 string → Unix timestamp |
| `fromdateiso8601` | ISO 8601 with timezone → Unix timestamp |

### Format Specifiers (strftime/strptime)

Common specifiers follow C `strftime` conventions:

| Specifier | Output |
|-----------|--------|
| `%Y` | Four-digit year (2024) |
| `%m` | Zero-padded month (01-12) |
| `%d` | Zero-padded day (01-31) |
| `%H` | Hour 24h (00-23) |
| `%M` | Minute (00-59) |
| `%S` | Second (00-59) |
| `%Y-%m-%d` | ISO date: `2024-01-15` |
| `%Y-%m-%dT%H:%M:%SZ` | Full ISO 8601: `2024-01-15T10:30:00Z` |

### Examples

```
# Current time as ISO string
now | todate                          # "2024-01-15T10:30:00Z"

# Format timestamp
1705312200 | strftime("%Y-%m-%d %H:%M")   # "2024-01-15 10:30"

# Parse date string
"2024-01-15" | strptime("%Y-%m-%d") | mktime   # 1705276800

# ISO round-trip
now | todate | fromdate                  # back to timestamp

# Local time
now | strflocaltime("%Y-%m-%d %H:%M:%S %Z")
```

## Math Functions

### Basic

| Function | Description |
|----------|-------------|
| `abs` | Absolute value (preserves literal precision) |
| `fabs` | Absolute value as IEEE754 float |
| `floor` | Round down to nearest integer |
| `ceil` | Round up to nearest integer |
| `round` | Round to nearest integer |
| `sqrt` | Square root |
| `sin`, `cos`, `tan` | Trigonometric (radians) |
| `asin`, `acos`, `atan` | Inverse trigonometric |
| `atan2(y; x)` | Two-argument arctangent |
| `exp` | e^x |
| `log` | Natural logarithm |
| `log10` | Base-10 logarithm |
| `pow(x)` | Raise to power x |

### Constants

| Constant | Value |
|----------|-------|
| `pi` | π (3.14159...) |
| `e` | e (2.71828...) |

### Special Values

| Function | Description |
|----------|-------------|
| `infinite` | Positive infinity |
| `nan` | Not-a-number |
| `isinfinite` | True if value is ±infinity |
| `isnan` | True if value is NaN |
| `isfinite` | True if value is finite (not NaN/infinity) |
| `isnormal` | True if value is a normal (non-zero, non-NaN, non-infinite) number |

### Examples

```
# Trigonometry
45 | pi / 180 | sin              # sin(45°) ≈ 0.707

# Rounding
3.7 | round                       # 4
-2.3 | floor                      # -3
-2.3 | ceil                       # -2

# Powers
2 | pow(10)                       # 1024
9 | sqrt                          # 3

# Logarithms
100 | log10                       # 2
exp(1)                            # e ≈ 2.718
```

## Number Precision Notes

- jq stores number literals with original decimal precision (if built with decnum support)
- Any arithmetic operation converts to IEEE754 double precision
- Use `have_decnum` to check if arbitrary-precision decimals are available
- `fabs` always returns IEEE754 double; `abs` preserves literal form when possible
- Comparisons use full precision (decnum if available, otherwise double)
