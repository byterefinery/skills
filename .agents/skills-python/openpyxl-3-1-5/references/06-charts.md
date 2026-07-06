# Charts

## Chart Types

```python
from openpyxl.chart import (
    AreaChart, AreaChart3D,
    BarChart, BarChart3D,
    LineChart, LineChart3D,
    PieChart, PieChart3D, DoughnutChart,
    ScatterChart, BubbleChart,
    RadarChart, RadarChart3D,
    SurfaceChart, SurfaceChart3D,
    StockChart
)
from openpyxl.chart.series_factory import SeriesFactory as Series
from openpyxl.chart.reference import Reference
```

## Basic Chart Creation

```python
from openpyxl.chart import BarChart, Reference

# Create chart
chart = BarChart()
chart.title = "Sales by Region"
chart.style = 10  # Built-in style (1-48)
chart.width = 15  # cm
chart.height = 7.5

# Add data series (columns by default)
data = Reference(ws, min_col=2, max_col=5, min_row=1, max_row=10)
chart.add_data(data, titles_from_data=True)

# Set categories (x-axis labels)
cats = Reference(ws, min_col=1, max_col=1, min_row=2, max_row=10)
chart.set_categories(cats)

# Add to worksheet at anchor position
ws.add_chart(chart, "E5")
```

## Reference Object

```python
from openpyxl.chart.reference import Reference

# Reference to a range
ref = Reference(ws, min_col=1, min_row=1, max_col=3, max_row=10)
str(ref)  # "'Sheet1'!$A$1:$C$10"

# Reference from string
ref = Reference(range_string="'Sheet1'!$A$1:$C$10")

# Iterate rows/columns
for row_ref in ref.rows:
    print(row_ref)  # "'Sheet1'!$A$2:$C$2"

for col_ref in ref.cols:
    print(col_ref)  # "'Sheet1'!$A$1:$A$10"

# Pop first cell (useful for title_from_data)
label = ref.pop()  # Returns "A1", advances reference
```

## Chart Properties

```python
chart.title = "Monthly Sales"       # Chart title (string or Title object)
chart.style = 10                     # Built-in style 1-48
chart.width = 15                     # Width in cm
chart.height = 7.5                   # Height in cm
chart.roundedCorners = True          # Rounded corners
chart.display_blanks = 'gap'         # 'span', 'gap', 'zero'
chart.visible_cells_only = True      # Only plot visible cells
chart.anchor = "E15"                 # Default anchor position
```

## Legend

```python
from openpyxl.chart.legend import Legend

chart.legend = Legend()
chart.legend.position = "r"    # "b" (bottom), "tr" (top-right),
                               # "l" (left), "r" (right), "t" (top)
chart.legend.overlay = True    # Overlay on chart area
chart.legend.position = "b"
```

## Axes Configuration

```python
# X-axis (category axis)
chart.x_axis.title = "Months"
chart.x_axis.tickLblPos = "low"       # "high", "low", "nextTo"
chart.x_axis.numFmt = 'mmm-yy'        # Number format
chart.x_axis.majorTickMark = "in"     # "cross", "in", "out"
chart.x_axis.minorTickMark = "none"
chart.x_axis.label_alignment = "ctr"  # "ctr", "l", "r"

# Y-axis (value axis)
chart.y_axis.title = "Revenue ($)"
chart.y_axis.scaling.min = 0
chart.y_axis.scaling.max = 1000
chart.y_axis.scaling.orientation = "minMax"  # or "maxMin"
chart.y_axis.majorUnit = 100
chart.y_axis.minorUnit = 20
chart.y_axis.crossBetween = "midCat"  # "between", "midCat"
chart.y_axis.numFmt = '$#,##0'

# Hide an axis
chart.y_axis.delete = True
```

## Series Customization

```python
from openpyxl.chart.series import Series
from openpyxl.chart.label import DataLabelList

# Create series manually
series = Series()
series.title = "Q1 Sales"
series.val = ...  # NumDataSource
series.cat = ...  # AxDataSource (categories)

# Add to chart
chart.series.append(series)

# Data labels
series.dLbls = DataLabelList(showVal=True, showCat=True, showSer=True)

# Marker (for line/scatter charts)
from openpyxl.chart.marker import Marker
series.marker = Marker(symbol="circle", size=8)

# Error bars
from openpyxl.chart.error_bar import ErrorBars, ErrorBar
series.errBars = ErrorBars(val=ErrorBar(type="stdDev"))

# Trendline
from openpyxl.chart.trendline import Trendline, TrendLineOption
series.trendline = Trendline(
    name="Trend",
    trendlineType="linear",
    displayEq=True,
    displayR=True
)
# trendlineType: linear, logarithmic, polyOrder, power, exponential, movingAvg

# Data points (individual point formatting)
from openpyxl.chart.marker import DataPoint, GraphicalProperties, LineProperties
dp = DataPoint(idx=0, spPr=GraphicalProperties(ln=LineProperties(w=12700)))
series.dPt = [dp]
```

## Chart Types — Specific Usage

### Bar Chart

```python
chart = BarChart()
chart.barDir = "col"       # "col" (vertical), "bar" (horizontal)
chart.grouping = "clustered"  # "clustered", "stacked", "percentStacked", "standard"
chart.gapWidth = 150       # 0-500
chart.overlap = None       # -100 to 100
```

### Line Chart

```python
chart = LineChart()
chart.grouping = "standard"  # "standard", "stacked", "percentStacked"

# Smooth lines
for series in chart.series:
    series.smooth = True

# Drop lines (connect lines across gaps)
chart.dropLines = ChartLines()
```

### Pie / Doughnut Chart

```python
chart = PieChart()
chart.variation = 1  # 0 or 1 for pie variation

# Explode a slice
for series in chart.series:
    series.explosion = 20  # Percentage

chart = DoughnutChart()
chart.varyColors = True
```

### Scatter Chart

```python
chart = ScatterChart()

# Scatter needs x and y data
from openpyxl.chart.data_source import NumDataSource, NumRef, AxDataSource

xdata = Reference(ws, min_col=1, min_row=2, max_row=10)
ydata = Reference(ws, min_col=2, min_row=2, max_row=10)
series = Series(xvalues=xdata, yvalues=ydata)
chart.series.append(series)

# Or use add_data with from_rows
data = Reference(ws, min_col=1, max_col=2, min_row=2, max_row=10)
chart.add_data(data, from_rows=True)
```

### Bubble Chart

```python
chart = BubbleChart()

# Bubble needs x, y, and size data
xdata = Reference(ws, min_col=1, min_row=2, max_row=10)
ydata = Reference(ws, min_col=2, min_row=2, max_row=10)
size = Reference(ws, min_col=3, min_row=2, max_row=10)
series = Series(xvalues=xdata, yvalues=ydata, zvalues=size)
chart.series.append(series)
```

### Radar Chart

```python
chart = RadarChart()
chart.style = 2

# Markers on radar
for series in chart.series:
    series.marker = Marker(symbol="diamond", size=8)
```

### Stock Chart

```python
chart = StockChart()
# Uses OHLC (Open, High, Low, Close) or Volume data
# Add three data series: high-low, open-close, volume
```

### 3D Charts

```python
chart = BarChart3D()
chart.view3D.rotation = 20
chart.view3D.ratio = 3/4
chart.view3D.height = 150
chart.gapDepth = 150
chart.shape = "cone"  # "cone", "coneToMax", "box", "cylinder", "pyramid", "pyramidToMax"

chart = AreaChart3D()
chart = LineChart3D()
chart = PieChart3D()
chart = SurfaceChart3D()
chart = RadarChart3D()
```

## Combining Charts

```python
# Overlay one chart on another
chart1 = BarChart()
chart1.add_data(data1)

chart2 = LineChart()
chart2.add_data(data2)
chart2.y_axis.axPos = "r"  # Right axis

chart1 += chart2  # Combine
ws.add_chart(chart1, "E5")
```

## Chart Styles

```python
# Built-in styles (1-48)
chart.style = 10

# Rounded corners
chart.roundedCorners = True
```
