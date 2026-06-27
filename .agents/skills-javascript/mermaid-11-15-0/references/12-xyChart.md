# XY Charts

XY charts render bar and line charts on two axes.

## Declaration

```mermaid
xychart-beta
```

## Bar Chart

Define title, axis labels, and bar data.

```mermaid
xychart-beta
    title "Monthly Revenue"
    x-axis [Jan, Feb, Mar, Apr, May, Jun]
    y-axis "Revenue ($)" 0 --> 10000
    bar [3500, 4200, 3800, 5100, 6200, 7500]
```

## Line Chart

Replace `bar` with `line`.

```mermaid
xychart-beta
    title "Temperature Trend"
    x-axis [Mon, Tue, Wed, Thu, Fri, Sat, Sun]
    y-axis "Temp (°C)" 0 --> 35
    line [22, 24, 21, 28, 30, 27, 25]
```

## Multiple Series

Add multiple `bar` or `line` entries.

```mermaid
xychart-beta
    title "Sales Comparison"
    x-axis [Q1, Q2, Q3, Q4]
    y-axis "Units" 0 --> 500
    bar [120, 200, 180, 350]
    line [100, 190, 200, 300]
```

## Stacked Bar Chart

Use multiple `bar` entries for stacked visualization.

```mermaid
xychart-beta
    title "Budget Breakdown"
    x-axis [Q1, Q2, Q3, Q4]
    y-axis "Amount ($K)" 0 --> 200
    bar [50, 60, 55, 80]
    bar [30, 40, 35, 50]
```
