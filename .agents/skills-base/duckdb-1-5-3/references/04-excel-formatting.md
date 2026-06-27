# Excel Formatting — text() and excel_text()

The Excel extension provides `text()` and `excel_text()` scalar functions that format numbers using Excel-compatible number format strings. These are the same formatting rules used by Microsoft Excel's `TEXT()` function.

## Functions

```sql
-- Both names are aliases for the same function
SELECT text(1234567.897, '$#,##0.00') AS formatted;
SELECT excel_text(1234567.897, '$#,##0.00') AS formatted;
-- Result: $1,234,567.90
```

**Signature**: `text(DOUBLE, VARCHAR) → VARCHAR`

- First argument: the number to format
- Second argument: Excel number format string
- Returns: formatted string representation

## Format String Syntax

Excel number formats follow the pattern: `[Negative]Positive;Negative;Zero;Text`

### Basic Components

| Element | Meaning | Example |
|---------|---------|---------|
| `0` | Digit placeholder (shows zero if no digit) | `0.00` → `1.50` |
| `#` | Digit placeholder (hides leading/trailing zeros) | `#.##` → `1.5` |
| `.` | Decimal separator | `0.00` |
| `,` | Thousands separator | `#,##0` → `1,234` |
| `$` | Literal currency symbol | `$#,##0` → `$1,234` |
| `%` | Multiply by 100 and append % | `0%` → `50%` |
| `E+` / `E-` | Scientific notation | `0.E+0` → `1.2E+3` |
| `;` | Section separator (positive;negative;zero;text) | `0;(-0);0;@"N/A"` |

### Common Format Patterns

```sql
-- Currency with 2 decimal places
SELECT text(1234.5, '$#,##0.00');          -- $1,234.50
SELECT text(-1234.5, '$#,##0.00;($#,##0.00)');  -- ($1,234.50)

-- Percentage
SELECT text(0.1234, '0%');                 -- 12%
SELECT text(0.1234, '0.00%');              -- 12.34%

-- Phone number style
SELECT text(1234567890, '(000) 000-0000'); -- (123) 456-7890

-- Date-like serial formatting
SELECT text(45292.0, 'mm/dd/yyyy');        -- Format applied to serial date

-- Scientific notation
SELECT text(1234567, '0.E+0');             -- 1.E+6

-- Fixed decimal places
SELECT text(3.14159, '0.000');             -- 3.142
SELECT text(3.14159, '#.###');             -- 3.142

-- With leading zeros
SELECT text(42, '00000');                  -- 00042
```

## Implementation Details

The formatting engine is based on LibreOffice's number format parser (`nf_zformat.cpp`, `nf_localedata.cpp`, `nf_calendar.cpp`). It implements the Excel/LibreOffice subset of number format specifications.

### Supported Features
- Digit placeholders (`0`, `#`)
- Decimal and thousands separators
- Literal text (quoted or escaped)
- Conditional sections (positive;negative;zero;text)
- Percentage formatting
- Scientific notation
- Date/time serial number formatting
- Currency symbols

### Limitations
- Does not support all Excel format codes (e.g., custom color codes `[Red]`)
- Locale-dependent separators use system defaults
- Date/time formatting expects Excel serial numbers (days since 1900-01-01)

## Practical Use Cases

### Formatting Financial Reports
```sql
SELECT
    product,
    text(revenue, '$#,##0') AS revenue,
    text(profit_margin, '0.0%') AS margin
FROM financial_data;
```

### Normalizing Phone Numbers
```sql
SELECT text(phone_number, '(000) 000-0000') AS formatted_phone
FROM contacts;
```

### ID Padding
```sql
SELECT text(id, '000000') AS padded_id
FROM items;
```

## Conversion Helpers (Internal)

The Excel extension internally uses these conversion functions when writing XLSX files:

| Function | Purpose |
|----------|---------|
| `date_to_excel_number(DATE) → DOUBLE` | Convert DATE to Excel serial number |
| `time_to_excel_number(TIME) → DOUBLE` | Convert TIME to fractional day |
| `timestamp_to_excel_number(TIMESTAMP) → DOUBLE` | Convert TIMESTAMP to serial + fraction |

These are internal implementation details and not exposed as user-facing functions. The conversion constants used:
- Days between 1900-01-01 and Unix epoch (1970-01-01): **25569**
- Seconds per day: **86400**

Example manual conversion:
```sql
-- Convert a DATE to Excel serial number
SELECT EXTRACT(EPOCH FROM my_date) / 86400.0 + 25569 AS excel_serial
FROM my_table;
```
