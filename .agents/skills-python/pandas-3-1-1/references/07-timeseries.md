# Time Series Reference

`Timestamp`, `Timedelta`, date ranges, resampling, offsets, and holiday calendars.

## Timestamp

Pandas' replacement for Python's `datetime.datetime`.

```python
# Construction
ts = pd.Timestamp("2024-01-15 14:30:00")
ts = pd.Timestamp(year=2024, month=1, day=15, hour=14)
ts = pd.Timestamp(1705330200, unit="s")   # Unix timestamp → datetime64[us] in v3.1
ts = pd.Timestamp("now")                   # Current time

# v3.1 — mixing a value to convert with date components raises ValueError
#   pd.Timestamp(datetime(2020, 12, 31), hour=5)  # raises
# Pass all components by keyword instead
ts = pd.Timestamp(year=2020, month=12, day=31, hour=5)
# A positional tzinfo (8th arg, like datetime) is now attached, not dropped

# Timezone-aware (zoneinfo, not pytz)
ts = pd.Timestamp("2024-01-15", tz="America/New_York")
ts = pd.Timestamp("2024-01-15", tz="UTC")

# Properties
ts.year, ts.month, ts.day
ts.hour, ts.minute, ts.second
ts.microsecond, ts.nanosecond
ts.day_of_week, ts.day_of_year       # v3.1 — dayofweek/dayofyear deprecated
ts.days_in_month                     # v3.1 — daysinmonth deprecated
ts.weekday_name                      # "Monday"
ts.is_month_start, ts.is_month_end
ts.is_quarter_start, ts.is_year_end
ts.is_leap_year

# Conversion
ts.to_pydatetime()                  # → datetime.datetime
ts.tz_localize("UTC")               # Attach timezone
ts.tz_convert("America/New_York")   # Convert timezone
ts.strftime("%Y-%m-%d %H:%M")       # Format as string
# v3.1 — %N formats nanoseconds (9-digit zero-padded); %f is microseconds
ts.strftime("%Y-%m-%d %H:%M:%S.%N")

# v3.1 — round/floor/ceil officially accept Timedelta arguments
ts.round(pd.Timedelta(hours=1))
```

## Timedelta

Duration/difference between two timestamps.

```python
# Construction
td = pd.Timedelta("7 days")
td = pd.Timedelta(days=7, hours=3)
td = pd.Timedelta(7, unit="D")
td = ts2 - ts1                      # Difference of timestamps

# v3.1 — strings with trailing characters raise (previously dropped):
#   pd.Timedelta("3:25:00 PM")  # ValueError — AM/PM unsupported

# Properties
td.days, td.seconds, td.microseconds
td.total_seconds()                  # v3.1 — includes the nanosecond component

# Arithmetic
ts + td                              # → Timestamp
td1 + td2                            # → Timedelta
td / 2                               # → Timedelta

# Rounding
td.round("H")                        # Round to nearest hour
td.floor("D")                        # Floor to day
td.ceil("H")                         # Ceiling to hour
```

## Date Ranges

Generate sequences of timestamps.

```python
# Fixed frequency
idx = pd.date_range("2024-01-01", "2024-12-31", freq="D")
idx = pd.date_range("2024-01-01", periods=365, freq="D")
idx = pd.date_range(start="2024-01-01", periods=100, freq="H")

# Business days
bdates = pd.bdate_range("2024-01-01", periods=252)

# Common frequencies
freq="D"      # Calendar day
freq="B"      # Business day
freq="W-SUN"  # Weekly, ending Sunday
freq="ME"     # Month end
freq="MS"     # Month start
freq="QE"     # Quarter end
freq="YE"     # Year end
freq="H"      # Hourly
freq="30min"  # Every 30 minutes
freq="min"    # Minutely
freq="S"      # Secondly

# Inferred frequency (v3.1: will return BaseOffset instead of str in a future version)
freq = pd.infer_freq(["2024-01-01", "2024-01-02", "2024-01-03"])  # "D"
```

## Timedelta Ranges

```python
idx = pd.timedelta_range("1 day", periods=10, freq="H")
idx = pd.timedelta_range(start="0 days", end="7 days", freq="6H")
```

## Period and PeriodIndex

Fixed-frequency time periods (not points in time).

```python
# Construction
periods = pd.period_range("2024-01", periods=12, freq="M")
p = pd.Period("2024-01", freq="M")

# Properties
p.year, p.month, p.day
p.start_time    # → Timestamp (start of period)
p.end_time      # → Timestamp (end of period)

# v3.1 — f-string formatting supported
f"{p:%Y-%m}"  # '2024-01'

# v3.1 — strftime uses %N for nanoseconds (%n is deprecated; %n is a newline in C strftime)
p.strftime("%Y-%m-%d %H:%M:%S.%N")

# v3.1 — constructing from integers is deprecated (future: ordinals);
# pass strings or use Period(ordinal=...)
```

## Resampling

Convert time series to different frequency.

```python
# Set DatetimeIndex first
df = df.set_index("date").sort_index()

# Downsample (high → low frequency)
monthly = df.resample("ME").sum()
weekly = df.resample("W-SUN").max()

# Upsample (low → high frequency)
daily = df.resample("D").ffill()          # Forward fill
daily = df.resample("D").interpolate()    # Linear interpolation
hourly = df.resample("H").asfreq()        # NA for missing

# Multiple aggregations
monthly = df.resample("ME").agg(
    {"sales": "sum", "price": "mean", "quantity": "count"}
)

# OHLC (open, high, low, close)
ohlc = df["price"].resample("D").ohlc()

# Rolling within resample
df.resample("ME").apply(lambda x: x.rolling(7).mean().iloc[-1])

# Labeling control
df.resample("ME", label="left")           # Label by period start
df.resample("ME", closed="right")         # Include right edge in bin
```

## DateOffsets

Add/subtract time-aware increments.

```python
from pandas.tseries.offsets import *

# Basic offsets
ts + Day(5)
ts + Hour(3)
ts + BusinessDay(5)                      # 5 business days
ts + MonthEnd()                          # End of current month
ts + MonthBegin()                        # Start of current month
ts + YearEnd()                           # End of current year
ts + Week(weekday=6)                     # Next Sunday

# Rolling offsets (n > 1 repeats the offset)
ts + MonthEnd(3)                         # End of month, 3 months ahead
ts + BusinessDay(2)                      # 2 business days

# Half-year offsets
ts + HalfYearBegin()                     # Start of half-year
ts + HalfYearEnd()                       # End of half-year
ts + BHalfYearBegin()                    # Business day at start
ts + BHalfYearEnd()                      # Business day at end

# Easter offset
easter = Easter()                        # Western Easter
orthodox_easter = Easter(method="orthodox")  # Orthodox Easter

# Custom holidays
holiday = Holiday(
    "CompanyHoliday", month=7, day=4,
    start_date="2020", end_date="2030",
    days_of_week=("Mon", "Tue", "Wed", "Thu", "Fri"),
    exclude_dates=["2025-07-04"]          # Exclude specific dates
)

# v3.1 — offset .name property deprecated; use .rule_code
```

## Time Zone Handling

Pandas uses the standard library `zoneinfo` module (not pytz).

```python
# Create timezone-aware series
s = pd.to_datetime(["2024-01-01", "2024-06-15"], utc=True)

# Localize naive timestamps
s = s.tz_localize("UTC")

# Convert between timezones
s_ny = s.tz_convert("America/New_York")
s_tokyo = s.tz_convert("Asia/Tokyo")

# zoneinfo objects work directly
from zoneinfo import ZoneInfo
s = s.tz_localize(ZoneInfo("America/New_York"))

# Fixed offset
s = pd.to_datetime(["2024-01-01"], utc=True).tz_convert("Etc/GMT-5")

# v3.1 — non-ISO strings with zero UTC offset ("Jan 15 2004 03:00 GMT")
# return stdlib datetime.timezone.utc (repr tz='UTC')
```

## Shifting and Lagging

```python
# Shift values forward/backward
df["lag_1"] = df["value"].shift(1)           # Previous row
df["lead_1"] = df["value"].shift(-1)         # Next row
df["lag_7d"] = df["value"].shift(7)          # 7 rows back

# v3.1 — passing both suffix= and integer periods raises ValueError

# Shift by time (reindex, not shift values)
df.shift(periods=1, freq="D")                # Shift index by 1 day
df.shift(periods=-1, freq="ME")              # Shift to previous month end

# Pct change
df["pct_change"] = df["value"].pct_change()
df["pct_7d"] = df["value"].pct_change(periods=7)
```

## Diff

```python
df["diff_1"] = df["value"].diff()            # Current - previous
df["diff_7"] = df["value"].diff(periods=7)   # Current - 7 rows ago
```

## Rolling Time Windows

See [08-window-rolling](08-window-rolling.md) for details.

```python
# Time-based rolling (not row-based)
df.rolling("7D").mean()                      # 7-day window
df.rolling("24H").sum()                      # 24-hour window
```

## Gotchas

- **`zoneinfo`, not `pytz`** — use string tz names or `zoneinfo.ZoneInfo()`.
- **Use `ME`/`MS` frequencies** — bare `"M"`/`"H"`-style month aliases are superseded by `ME` (month end) / `MS` (month start) for clarity.
- **Resampling requires sorted DatetimeIndex** — sort first with `df.sort_index()`.
- **`shift(freq=)` shifts the index, not values** — use `shift(periods=n)` to lag/lead values.
- **`pd.infer_freq` returns `None` for irregular series** — and will return `BaseOffset` instead of a string in a future version (opt in with `future.infer_freq_returns_offset=True`).
- **`Timestamp("now")` uses local time** — use `Timestamp.now(tz="UTC")` for UTC.
- **Period arithmetic preserves frequency** — adding days to a monthly Period still gives a monthly Period.
- **Quarter-start freq inference (v3.1)** — `infer_freq` on quarter-start data reports the equivalent anchor from the first calendar quarter (e.g., `QS-JAN` instead of `QS-OCT`).
- **AM/PM time strings** — `"3:25:00 PM"` (space before AM/PM) is now recognized by `to_datetime` and `between_time`/`at_time`, but `Timedelta` parsing rejects trailing characters including AM/PM.
