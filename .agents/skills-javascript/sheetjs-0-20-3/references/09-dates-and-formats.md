# Dates and Number Formats

## Date Handling

### How Excel Stores Dates

Excel stores dates as serial numbers (days since epoch). The number format determines display:

- `42785` with format `d-mmm-yy` → `19-Feb-17`
- `0.25` → `6:00 AM` (fractional part = time)

### Default Behavior

By default, dates are stored as numbers (type `"n"`). Use `cellDates: true` to get Date objects:

```js
// Default: dates as numbers
const wb = XLSX.read(data);
console.log(ws["A1"].v); // 44927 (number)

// With cellDates: dates as Date objects
const wb = XLSX.read(data, { cellDates: true });
console.log(ws["A1"].v); // Date object
```

### UTC vs Local Time (v0.20.0+)

Since v0.20.0, SheetJS uses UTC interpretation for Date objects by default:

```js
// Reading: UTC interpretation (default)
const wb = XLSX.read(data, { cellDates: true, UTC: true });

// Reading: local time interpretation
const wb = XLSX.read(data, { cellDates: true, UTC: false });

// Writing: export as date strings
XLSX.writeFile(wb, "out.xlsx", { cellDates: true });

// sheet_to_json: UTC dates
const data = XLSX.utils.sheet_to_json(ws, { UTC: true });

// sheet_to_json: local time dates
const data = XLSX.utils.sheet_to_json(ws, { UTC: false });
```

### 1900 vs 1904 Date System

```js
// Check which date system a workbook uses
const is1904 = wb?.Workbook?.WBProps?.date1904;
if (is1904) {
  // Epoch: January 1, 1904
} else {
  // Epoch: December 30, 1899 (default)
}
```

The 1904 system exists because Lotus 1-2-3 incorrectly treated 1900 as a leap year. Excel extends this tradition in the default (1900) system.

## Number Formats

### Setting Number Formats

```js
ws["B1"].z = "$0.00";         // currency
ws["B2"].z = "#,##0";         // thousands separator
ws["B3"].z = "0.00%";         // percentage
ws["B4"].z = "yyyy-mm-dd";    // date
ws["B5"].z = "0.00E+00";      // scientific notation
```

### Reading Number Formats

```js
const wb = XLSX.read(data, { cellNF: true });
console.log(ws["B1"].z); // format string
```

### Built-in Format IDs

| ID | Format |
|---|---|
| 0 | `General` |
| 1 | `0` |
| 2 | `0.00` |
| 3 | `#,##0` |
| 4 | `#,##0.00` |
| 9 | `0%` |
| 10 | `0.00%` |
| 11 | `0.00E+00` |
| 12 | `# ?/?` |
| 13 | `# ??/??` |
| 14 | `m/d/yy` (localized) |
| 15 | `d-mmm-yy` |
| 16 | `d-mmm` |
| 17 | `mmm-yy` |
| 18 | `h:mm AM/PM` |
| 19 | `h:mm:ss AM/PM` |
| 20 | `h:mm` |
| 21 | `h:mm:ss` |
| 22 | `m/d/yy h:mm` |
| 45 | `mm:ss` |
| 46 | `[h]:mm:ss` |
| 49 | `@` |

### Date Format Tokens

| Token | Meaning |
|---|---|
| `yy` | 2-digit year |
| `yyyy` | 4-digit year |
| `m` | Month (1-digit) or minutes (context-dependent) |
| `mm` | Month (2-digit) or minutes (context-dependent) |
| `mmm` | 3-letter month name |
| `mmmm` | Full month name |
| `d` | Day (1-digit) |
| `dd` | Day (2-digit) |
| `ddd` | 3-letter day of week |
| `dddd` | Full day of week |
| `h` | Hours (1-digit) |
| `hh` | Hours (2-digit) |
| `s` | Seconds (1-digit) |
| `ss` | Seconds (2-digit) |
| `AM/PM` | Meridiem |
| `[h]` / `[hh]` | Absolute hours (duration) |
| `[m]` / `[mm]` | Absolute minutes (duration) |

### SSF Library

SheetJS includes the SSF (SpreadSheet Format) library for standalone number formatting:

```js
XLSX.SSF.format("#,##0.00", 1234.5);    // "1,234.50"
XLSX.SSF.format("0.00%", 0.0219);        // "2.19%"
XLSX.SSF.format("yyyy-mm-dd", 44927);    // "2023-01-01" (date code)
XLSX.SSF.is_date("yyyy-mm-dd");          // true
XLSX.SSF.is_date("0.00");                // false
```

### Percentage Formatting

Percentages scale values by 100:

```js
// Value 0.0219 with format "0.00%" → displays as "2.19%"
ws["B1"].z = "0.00%";
ws["B1"].v = 0.0219;
ws["B1"].w = "2.19%";
```

### Fraction Formatting

```js
ws["B1"].z = "# ?/?";    // up to one digit denominator
ws["B2"].z = "# ??/??";  // up to two digits denominator
```

## Date Conversion Utilities

### Date to Excel Serial Number

```js
function dateToExcelSerial(date) {
  const epoch = new Date(1899, 11, 30); // Dec 30, 1899
  return (date - epoch) / (1000 * 60 * 60 * 24);
}
```

### Excel Serial Number to Date

```js
function excelSerialToDate(serial) {
  const epoch = new Date(1899, 11, 30);
  return new Date(epoch.getTime() + serial * 24 * 60 * 60 * 1000);
}
```

### Parsing ISO Date Strings

When data comes from APIs as ISO strings, convert before creating sheets:

```js
const rows = data.map(row => ({
  ...row,
  birthday: new Date(row.birthday)  // convert string to Date
}));
const ws = XLSX.utils.json_to_sheet(rows);
```

## Special Values

### NaN and Infinity

v0.20.0+ maps special JS values to Excel errors:

| JS Value | Excel Error |
|---|---|
| `NaN` | `#NUM!` |
| `Infinity` | `#DIV/0!` |
| `-Infinity` | `#DIV/0!` |

### null and undefined

- `undefined` — skipped by default (cell not created)
- `null` — skipped by default, or becomes stub cell with `sheetStubs: true`, or `#NULL!` with `nullError: true`
