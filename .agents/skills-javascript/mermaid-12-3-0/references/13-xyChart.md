# XY charts (bar and line)

Keyword: `xychart` (optionally `xychart horizontal`).

Sources: `docs/syntax/xyChart.md` at mermaid@12.3.0.

## Syntax

- `title "..."` — quote multi-word titles.
- `x-axis` — categorical `["jan", "feb", …]` or numeric `min --> max`.
- `y-axis` — numeric range `"label" min --> max` or just a label (range auto from data).
- `bar [values]` / `line [values]` — plots; `bar "series name" [values]` adds a legend entry (v11.17.0+). Named line/bar series appear in a legend automatically.
- Both axes are optional — ranges are inferred from data.

```mermaid
xychart
    title "Sales Revenue"
    x-axis [jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec]
    y-axis "Revenue (in $)" 4000 --> 11000
    bar [5000, 6000, 7500, 8200, 9500, 10500, 11000, 10200, 9200, 8500, 7000, 6000]
    line [5000, 6000, 7500, 8200, 9500, 10500, 11000, 10200, 9200, 8500, 7000, 6000]
```

## Verified examples

Legend example (docs):

```mermaid
xychart
  title "An Example Chart"
  x-axis ["90d", "60d", "30d", "7d", "1d", "Current"]
  y-axis "Seconds" 0 --> 198.2
  line "avg" [48.1, 41.5, 45.7, 72.8, 67.7, 59.9]
  line "p50" [38.2, 36.8, 39.7, 54.5, 49.0, 38.4]
  line "p95" [112.2, 75.3, 103.0, 177.0, 180.2, 109.4]
```

Sales revenue and sign-ups-vs-churn examples — see all-examples "XY Chart" section for the full verified blocks.
