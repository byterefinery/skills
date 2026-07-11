# Date Handling

## Date Formats

The World Bank API accepts dates in three frequency formats:

| Frequency | Format | Example |
|---|---|---|
| Yearly (`Y`) | `%Y` | `"2020"` |
| Monthly (`M`) | `%YM%m` | `"2020M06"` |
| Quarterly (`Q`) | `%YQ%q` | `"2020Q1"` |

## Input Flexibility

wbdata accepts dates as:

1. **Strings in WB format** — `"2020"`, `"2020M06"`, `"2020Q1"`
2. **`datetime.datetime` objects** — `datetime(2020, 6, 1)`
3. **Natural language strings** — parsed by `dateparser`, e.g. `"last year"`, `"2020-06-15"`
4. **Date ranges** — tuples of two dates: `("2015", "2020")`

The `freq` parameter tells wbdata how to format the parsed date for the API.

## `parse_dates` Parameter

When `parse_dates=True` in `get_data()` or `get_series()`, date strings in the response are converted to `datetime.datetime` objects in-place.

Special values `"MRV"` and `"-"` are left as strings (they represent missing/revised data).

## Common Patterns

```python
# Single year
wbdata.get_data("NY.GDP.PCAP.CD", country="USA", date="2020")

# Year range
wbdata.get_data("NY.GDP.PCAP.CD", country="USA", date=("2015", "2020"))

# Monthly data
wbdata.get_data("indicator", country="USA", date=("2020M01", "2020M06"), freq="M")

# Natural language with dateparser
wbdata.get_data("NY.GDP.PCAP.CD", country="USA", date="2020-01-01")

# datetime objects
import datetime
wbdata.get_data("NY.GDP.PCAP.CD", country="USA", date=(datetime.datetime(2015, 1, 1), datetime.datetime(2020, 12, 31)))
```
