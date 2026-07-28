# Date and Time Functions

## Table of Contents

- [Overview](#overview)
- [Time Value Formats](#time-value-formats)
- [Functions](#functions)
- [Modifiers](#modifiers)
- [strftime Format Specifiers](#strftime-format-specifiers)
- [Examples](#examples)
- [Caveats](#caveats)

## Overview

SQLite has no dedicated DATE/DATETIME type. Dates/times are stored as:
- **TEXT** — ISO-8601 strings: `'YYYY-MM-DD HH:MM:SS'`
- **REAL** — Julian day numbers (days since 4714 BC)
- **INTEGER** — Unix timestamps (seconds since 1970-01-01)

All seven date/time functions accept these formats and can convert between them.

## Time Value Formats

| Format | Example |
|---|---|
| `YYYY-MM-DD` | `'2024-01-15'` |
| `YYYY-MM-DD HH:MM` | `'2024-01-15 10:30'` |
| `YYYY-MM-DD HH:MM:SS` | `'2024-01-15 10:30:00'` |
| `YYYY-MM-DD HH:MM:SS.SSS` | `'2024-01-15 10:30:00.123'` |
| `YYYY-MM-DDTHH:MM` (with T separator) | `'2024-01-15T10:30'` |
| `HH:MM` / `HH:MM:SS` | `'10:30'` (assumes date 2000-01-01) |
| `now` | Current date/time |
| Julian day number | `2460310.5` (REAL or INTEGER) |

Timezone indicators: `Z` (UTC) or `+HH:MM` / `-HH:MM`.

## Functions

| Function | Returns |
|---|---|
| `date(t, mod, ...)` | `'YYYY-MM-DD'` |
| `time(t, mod, ...)` | `'HH:MM:SS'` |
| `datetime(t, mod, ...)` | `'YYYY-MM-DD HH:MM:SS'` |
| `julianday(t, mod, ...)` | Julian day number (REAL) |
| `unixepoch(t, mod, ...)` | Unix timestamp (INTEGER seconds) |
| `strftime(fmt, t, mod, ...)` | Formatted string |
| `timediff(A, B)` | Human-readable time difference string |

All functions except `timediff()` accept modifiers. If no time value is given, `'now'` is assumed.

## Modifiers

Modifiers are applied left to right:

| Modifier | Description |
|---|---|
| `NNN days` / `NNN hours` / `NNN minutes` / `NNN seconds` | Add time |
| `NNN months` / `NNN years` | Add months/years |
| `±HH:MM` / `±HH:MM:SS` | Time shift |
| `±YYYY-MM-DD` / `±YYYY-MM-DD HH:MM:SS` | Date/time shift |
| `ceiling` / `floor` | Resolve ambiguous dates (after month/year shift) |
| `start of month` / `start of year` / `start of day` | Shift to beginning |
| `weekday N` | Advance to weekday N (0=Sunday) |
| `unixepoch` | Interpret numeric value as Unix timestamp |
| `julianday` | Force interpretation as Julian day |
| `auto` | Auto-detect Unix timestamp vs Julian day |
| `localtime` | Convert UTC to local time |
| `utc` | Convert local time to UTC |
| `subsec` | Include millisecond precision in output |

## strftime Format Specifiers

| Specifier | Output |
|---|---|
| `%d` | Day of month: 00-31 |
| `%m` | Month: 01-12 |
| `%Y` | Year: 0000-9999 |
| `%H` | Hour: 00-23 |
| `%M` | Minute: 00-59 |
| `%S` | Seconds: 00-59 |
| `%f` | Fractional seconds: SS.SSS |
| `%F` | ISO 8601 date: YYYY-MM-DD |
| `%T` | ISO 8601 time: HH:MM:SS |
| `%R` | ISO 8601 time: HH:MM |
| `%w` | Day of week: 0=Sunday |
| `%W` | Week of year (Monday start) |
| `%j` | Day of year: 001-366 |
| `%s` | Seconds since 1970-01-01 |
| `%J` | Julian day number |
| `%p` / `%P` | AM/PM or am/pm |
| `%%` | Literal % |

Equivalents:
- `date(...) ≡ strftime('%F', ...)`
- `time(...) ≡ strftime('%T', ...)`
- `datetime(...) ≡ strftime('%F %T', ...)`
- `julianday(...) ≡ CAST(strftime('%J', ...) AS REAL)`
- `unixepoch(...) ≡ CAST(strftime('%s', ...) AS INT)`

## Examples

```sql
-- Current date/time
SELECT date('now');              -- '2024-01-15'
SELECT datetime('now');          -- '2024-01-15 10:30:00'
SELECT strftime('%Y-%m-%d %H:%M:%S', 'now');

-- Unix timestamp
SELECT unixepoch();              -- current Unix timestamp
SELECT datetime(1705312200, 'unixepoch');
SELECT datetime(1705312200, 'unixepoch', 'localtime');

-- Date arithmetic
SELECT date('now', '+1 month', '-1 day');  -- last day of current month
SELECT date('now', 'start of month');      -- first day of current month
SELECT date('now', 'weekday 1');           -- next Monday

-- Time differences
SELECT julianday('now') - julianday('2024-01-01');  -- days between
SELECT unixepoch() - unixepoch('2024-01-01');        -- seconds between
SELECT timediff('now', '2024-01-01');                -- human-readable span

-- Millisecond precision
SELECT datetime('now', 'subsec');    -- '2024-01-15 10:30:00.123'
SELECT unixepoch('subsec');          -- fractional Unix timestamp

-- Timezone conversion
SELECT datetime('now', 'localtime');
SELECT datetime('2024-01-15 10:30:00', 'utc');
```

## Caveats

- Only works for dates between 0000-01-01 and 9999-12-31
- `localtime` conversion uses the C library's `localtime_r()` — limited to years 1970-2037 on some platforms
- No leap seconds are incorporated (each day is exactly 86400 seconds)
- DST handling on Windows is limited (historical DST rules may be incorrect)
- `timediff()` gives a human-friendly span; for precise calculations, use `julianday()` or `unixepoch()` differences
