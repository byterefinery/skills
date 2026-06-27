# Dates and Times

## Basic Date Plotting

Matplotlib automatically handles `datetime`, `numpy.datetime64`, and pandas Timestamps:

```python
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta

# Using datetime objects
dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(365)]
values = np.random.randn(365).cumsum()

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(dates, values)
```

## Date Conversion Functions

```python
import matplotlib.dates as mdates

# Convert between formats
ordinal = mdates.date2num(datetime(2024, 6, 15))   # datetime → float
dt = mdates.num2date(ordinal)                        # float → datetime
td = mdates.num2timedelta(ordinal)                   # float → timedelta

# Generate date range
dates = mdates.drange(datetime(2024, 1, 1), datetime(2024, 12, 31),
                      timedelta(days=7))

# String to number
num = mdates.datestr2num('2024-06-15')
```

## Date Formatters

```python
from matplotlib.dates import (
    DateFormatter, ConciseDateFormatter, AutoDateFormatter,
    ConciseLocator
)
```

### DateFormatter (strftime-style)

```python
ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
ax.xaxis.set_major_formatter(DateFormatter('%b %Y'))
ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))
```

### Common format codes

| Code | Output | Example |
|------|--------|---------|
| `%Y` | 4-digit year | `2024` |
| `%y` | 2-digit year | `24` |
| `%m` | Month (zero-padded) | `06` |
| `%b` | Abbreviated month | `Jun` |
| `%B` | Full month name | `June` |
| `%d` | Day (zero-padded) | `15` |
| `%H` | Hour (24h) | `14` |
| `%M` | Minute | `30` |
| `%S` | Second | `45` |
| `%A` | Full weekday | `Monday` |
| `%a` | Abbreviated weekday | `Mon` |

### AutoDateFormatter (auto-picks format)

```python
from matplotlib.dates import AutoLocator, AutoDateFormatter

locator = AutoLocator()
formatter = AutoDateFormatter(locator)
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(formatter)
```

### ConciseDateFormatter (compact display)

```python
from matplotlib.dates import ConciseLocator, ConciseDateFormatter

locator = ConciseLocator()
formatter = ConciseDateFormatter(locator)
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(formatter)
# Shows year once, then just months/days
```

## Date Locators

```python
from matplotlib.dates import (
    YearLocator, MonthLocator, WeekdayLocator, DayLocator,
    HourLocator, MinuteLocator, SecondLocator,
    RRuleLocator, AutoDateLocator
)
import datetime
```

| Locator | Use Case | Example |
|---------|----------|---------|
| `YearLocator()` | Tick at year boundaries | Jan 1 of each year |
| `MonthLocator(bymonthday=1)` | Tick at month start | Every 1st of month |
| `MonthLocator(interval=3)` | Quarterly ticks | Every 3 months |
| `WeekdayLocator(byweekday=MO)` | Specific weekdays | Every Monday |
| `DayLocator(interval=7)` | Every N days | Weekly ticks |
| `HourLocator(byhour=[0, 12])` | Specific hours | Midnight and noon |
| `MinuteLocator(interval=30)` | Every N minutes | Half-hour ticks |
| `AutoDateLocator()` | Auto-picks intervals | Default for dates |

### Weekday constants

```python
from matplotlib.dates import MO, TU, WE, TH, FR, SA, SU

# Tick on Mondays and Fridays
ax.xaxis.set_major_locator(WeekdayLocator(byweekday=(MO, FR)))

# Tick every second Monday
ax.xaxis.set_major_locator(WeekdayLocator(byweekday=MO, interval=2))
```

### RRuleLocator (advanced recurrence)

```python
from datetime import rrule, rruleyearly, rrulemonthly

# First day of each month
locator = RRuleLocator(rrulemonthly, bymonthday=1)
ax.xaxis.set_major_locator(locator)
```

## Rotating Date Labels

Date labels often overlap — rotate them:

```python
fig.autofmt_xdate()  # Auto-rotate and right-align
# Or manually:
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
```

## Filling Gaps in Time Series

```python
# NaN values create gaps (discontinuities)
import pandas as pd
df = pd.DataFrame({'date': dates, 'value': values})
df = df.set_index('date').asfreq('D')  # Resample to daily, fills with NaN
ax.plot(df.index, df['value'])
```

## Date Range Selection

```python
# Set date limits
ax.set_xlim(datetime(2024, 1, 1), datetime(2024, 6, 30))
# Or with numpy datetime64
ax.set_xlim(np.datetime64('2024-01-01'), np.datetime64('2024-06-30'))
```

## Timezone Handling

```python
from matplotlib.dates import DateFormatter
import dateutil.tz

# Use specific timezone
tz = dateutil.tz.gettz('US/Eastern')
formatter = DateFormatter('%Y-%m-%d %H:%M', tz=tz)
ax.xaxis.set_major_formatter(formatter)
```

## Common Patterns

### Financial time series

```python
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(dates, prices, linewidth=1.5)
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_minor_locator(mdates.WeekdayLocator())
fig.autofmt_xdate()
ax.grid(True, alpha=0.3, axis='x')
```

### Intraday chart

```python
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(timestamps, prices)
ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=15))
fig.autofmt_xdate()
```

### Multi-year chart

```python
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(dates, values)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=3))
fig.autofmt_xdate()
```
