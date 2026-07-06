# Filters and Sorting

## AutoFilter

```python
from openpyxl.worksheet.filters import AutoFilter

# Enable auto-filter on a range
ws.auto_filter.ref = "A1:D10"

# Or create explicitly
ws.auto_filter = AutoFilter(ref="A1:D10")

# Disable
ws.auto_filter.ref = None
```

## Column Filters

```python
# Filter by specific values
ws.auto_filter.add_filter_column(col_id=0, vals=["Alice", "Bob"])

# Include blanks
ws.auto_filter.add_filter_column(col_id=0, vals=["Alice"], blank=True)

# col_id is zero-based: 0 = first column in the filter range
```

## Sort Conditions

```python
# Add sort condition
ws.auto_filter.add_sort_condition("A2:A10", descending=False)
ws.auto_filter.add_sort_condition("B2:B10", descending=True)

# Sort by multiple columns
ws.auto_filter.sortState.sortCondition.append(
    SortCondition(ref="A2:A10", descending=False)
)
ws.auto_filter.sortState.sortCondition.append(
    SortCondition(ref="B2:B10", descending=True)
)
```

## Custom Filters

```python
from openpyxl.worksheet.filters import (
    CustomFilter, CustomFilters, FilterColumn
)

# Greater than
flt = CustomFilter(operator="greaterThan", val="100")
cf = CustomFilters(customFilter=(flt,))
ws.auto_filter.filterColumn.append(FilterColumn(colId=1, customFilters=cf))

# Between
flt1 = CustomFilter(operator="greaterThanOrEqual", val="50")
flt2 = CustomFilter(operator="lessThanOrEqual", val="100")
cf = CustomFilters(_and=True, customFilter=(flt1, flt2))
ws.auto_filter.filterColumn.append(FilterColumn(colId=1, customFilters=cf))

# Operators: equal, lessThan, lessThanOrEqual, notEqual,
# greaterThanOrEqual, greaterThan
```

## String Filters

```python
from openpyxl.worksheet.filters import StringFilter

# Contains
flt = StringFilter(operator="contains", val="Smith")

# Starts with
flt = StringFilter(operator="startswith", val="A")

# Ends with
flt = StringFilter(operator="endswith", val=".com")

# Wildcard
flt = StringFilter(operator="wildcard", val="A*")

# Exclude
flt = StringFilter(operator="contains", val="error", exclude=True)
```

## Dynamic Filters

```python
from openpyxl.worksheet.filters import DynamicFilter

# Today
df = DynamicFilter(type="today")

# This month
df = DynamicFilter(type="thisMonth")

# Above average
df = DynamicFilter(type="aboveAverage")

# Available types: null, aboveAverage, belowAverage,
# tomorrow, today, yesterday, nextWeek, thisWeek, lastWeek,
# nextMonth, thisMonth, lastMonth, nextQuarter, thisQuarter,
# lastQuarter, nextYear, thisYear, lastYear, yearToDate,
# Q1-Q4, M1-M12
```

## Top 10 Filter

```python
from openpyxl.worksheet.filters import Top10

# Top 10 values
top = Top10(top=True, val=10, percent=False)
ws.auto_filter.filterColumn.append(FilterColumn(colId=1, top10=top))

# Top 10%
top = Top10(top=True, val=10, percent=True)

# Bottom 5
top = Top10(top=False, val=5, percent=False)
```

## Color Filter

```python
from openpyxl.worksheet.filters import ColorFilter

# Filter by cell color (dxfId references a differential format)
cf = ColorFilter(dxfId=1, cellColor=True)
ws.auto_filter.filterColumn.append(FilterColumn(colId=1, colorFilter=cf))
```

## Icon Filter

```python
from openpyxl.worksheet.filters import IconFilter

# Filter by icon
icon = IconFilter(iconSet="3TrafficLights1", iconId=0)
ws.auto_filter.filterColumn.append(FilterColumn(colId=1, iconFilter=icon))
```

## Date Grouping

```python
from openpyxl.worksheet.filters import DateGroupItem, Filters

# Group by year and month
date_group = DateGroupItem(
    year=2024,
    month=1,
    dateTimeGrouping="month"
)

flt = Filters(
    blank=False,
    filter=["Jan 2024"],
    dateGroupItem=[date_group]
)

ws.auto_filter.filterColumn.append(FilterColumn(colId=0, filters=flt))

# dateTimeGrouping: "year", "month", "day", "hour", "minute", "second"
```

## Sort State

```python
from openpyxl.worksheet.filters import SortState, SortCondition

# Create sort state
sort = SortState(
    ref="A1:D10",
    caseSensitive=False,
    columnSort=False,
    sortMethod="pinYin"  # "stroke", "pinYin"
)

# Add sort conditions
sort.sortCondition.append(SortCondition(ref="A2:A10", descending=False))
sort.sortCondition.append(SortCondition(ref="B2:B10", descending=True))

# Sort by cell color
sort.sortCondition.append(SortCondition(
    ref="C2:C10",
    sortBy="cellColor",
    descending=False
))

# Sort by icon
sort.sortCondition.append(SortCondition(
    ref="D2:D10",
    sortBy="icon",
    iconSet="3Arrows",
    iconId=0,
    descending=False
))

ws.auto_filter.sortState = sort
```

## Filter Column Properties

```python
from openpyxl.worksheet.filters import FilterColumn

fc = FilterColumn(
    colId=0,              # Zero-based column index
    hiddenButton=False,   # Hide filter button
    showButton=True,      # Show filter button
)
```
