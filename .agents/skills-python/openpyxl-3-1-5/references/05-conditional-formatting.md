# Conditional Formatting

## Adding Rules

```python
from openpyxl.formatting.rule import (
    CellIsRule, FormulaRule, ColorScaleRule,
    DataBarRule, IconSetRule, FormatObject
)

# Add to worksheet
ws.conditional_formatting.add("A1:A10", rule)

# Rules auto-assign priority (incrementing)
# Multiple rules on same range are evaluated by priority (lowest first)
```

## CellIsRule — Value-Based Rules

```python
# Greater than
ws.conditional_formatting.add("A1:A10",
    CellIsRule(operator="greaterThan", formula=["100"],
               fill=PatternFill("solid", fgColor="FFC7CE"),
               font=Font(color="FF0000")))

# Between
ws.conditional_formatting.add("A1:A10",
    CellIsRule(operator="between", formula=["50", "100"],
               fill=PatternFill("solid", fgColor="C6EFCE")))

# Contains text
ws.conditional_formatting.add("A1:A10",
    CellIsRule(operator="containsText", formula=["'error'"],
               fill=PatternFill("solid", fgColor="FFC7CE")))

# Duplicate values
ws.conditional_formatting.add("A1:A10",
    CellIsRule(type="duplicateValues",
               fill=PatternFill("solid", fgColor="FFC7CE")))

# Unique values
ws.conditional_formatting.add("A1:A10",
    CellIsRule(type="uniqueValues",
               fill=PatternFill("solid", fgColor="C6EFCE")))

# Contains blanks
ws.conditional_formatting.add("A1:A10",
    CellIsRule(type="containsBlanks",
               fill=PatternFill("solid", fgColor="FFC7CE")))

# Contains errors
ws.conditional_formatting.add("A1:A10",
    CellIsRule(type="containsErrors",
               fill=PatternFill("solid", fgColor="FFC7CE")))

# Above/below average
ws.conditional_formatting.add("A1:A10",
    CellIsRule(type="aboveAverage", aboveAverage=True,
               fill=PatternFill("solid", fgColor="C6EFCE")))

# Operators: lessThan, lessThanOrEqual, equal, notEqual,
# greaterThanOrEqual, greaterThan, between, notBetween,
# containsText, notContains, beginsWith, endsWith

# Convenience operators (expanded internally):
# ">" -> "greaterThan", ">=" -> "greaterThanOrEqual",
# "<" -> "lessThan", "<=" -> "lessThanOrEqual",
# "=" -> "equal", "==" -> "equal", "!=" -> "notEqual"
```

## FormulaRule — Custom Formula Rules

```python
# Highlight entire row based on a column value
ws.conditional_formatting.add("A1:C10",
    FormulaRule(formula=["=$B1>100"],
                fill=PatternFill("solid", fgColor="D9E1F2")))

# Alternating row colors
ws.conditional_formatting.add("A1:C10",
    FormulaRule(formula=["MOD(ROW(),2)=0"],
                fill=PatternFill("solid", fgColor="D9E1F2")))

# Stop after first matching rule
ws.conditional_formatting.add("A1:A10",
    FormulaRule(formula=["A1>100"], stopIfTrue=True,
                fill=PatternFill("solid", fgColor="FFC7CE")))

# With font, border, and fill
from openpyxl.styles import Border, Side
ws.conditional_formatting.add("A1:A10",
    FormulaRule(
        formula=["A1<0"],
        font=Font(bold=True, color="FF0000"),
        border=Border(left=Side(style="thin", color="FF0000")),
        fill=PatternFill("solid", fgColor="FFC7CE")
    ))
```

## ColorScaleRule — Gradient Color Scales

```python
# Two-color scale (min to max)
ws.conditional_formatting.add("A1:A10",
    ColorScaleRule(
        min_type="min", min_color="FFFF00",
        max_type="max", max_color="FF0000"
    ))

# Three-color scale (min, mid, max)
ws.conditional_formatting.add("A1:A10",
    ColorScaleRule(
        min_type="min", min_color="FFFF00",
        mid_type="percentile", mid_value=50, mid_color="FFFFFF",
        max_type="max", max_color="FF0000"
    ))

# Type options: num, percent, max, min, formula, percentile
```

## DataBarRule — Data Bars

```python
# Green data bar
ws.conditional_formatting.add("A1:A10",
    DataBarRule(
        min_type="min", max_type="max",
        color="638EC6",
        showValue=True
    ))

# Red data bar with specific range
ws.conditional_formatting.add("A1:A10",
    DataBarRule(
        min_type="num", min_value=0,
        max_type="num", max_value=100,
        color="FF0000",
        showValue=False
    ))
```

## IconSetRule — Icon Sets

```python
# 3-arrow icons
ws.conditional_formatting.add("A1:A10",
    IconSetRule(
        icon_style="3Arrows",
        type="num",
        values=[0, 50, 100],
        showValue=True,
        percent=False,
        reverse=False
    ))

# Icon styles:
# 3Arrows, 3ArrowsGray, 3Flags, 3TrafficLights1, 3TrafficLights2,
# 3Signs, 3Symbols, 3Symbols2, 4Arrows, 4ArrowsGray, 4RedToBlack,
# 4Rating, 4TrafficLights, 5Arrows, 5ArrowsGray, 5Rating, 5Quarters
```

## Time Period Rules

```python
# Today
ws.conditional_formatting.add("A1:A10",
    CellIsRule(type="timePeriod", timePeriod="today",
               fill=PatternFill("solid", fgColor="C6EFCE")))

# Time periods: today, yesterday, tomorrow, last7Days,
# thisMonth, lastMonth, nextMonth, thisWeek, lastWeek, nextWeek
```

## Top/Bottom Rules

```python
# Top 10
ws.conditional_formatting.add("A1:A10",
    CellIsRule(type="top10", rank=10,
               fill=PatternFill("solid", fgColor="C6EFCE")))

# Bottom 10%
ws.conditional_formatting.add("A1:A10",
    CellIsRule(type="top10", rank=10, percent=True, bottom=True,
               fill=PatternFill("solid", fgColor="FFC7CE")))
```

## Managing Rules

```python
# Access rules
for cf in ws.conditional_formatting:
    print(cf.cells)     # Cell range
    for rule in cf.rules:
        print(rule.type, rule.priority)

# Delete rules for a range
del ws.conditional_formatting["A1:A10"]

# Check if range has rules
if "A1:A10" in ws.conditional_formatting:
    print("Has conditional formatting")

# Check if a cell is covered
if "B5" in ws.conditional_formatting["A1:A10"]:
    print("B5 is covered")
```
