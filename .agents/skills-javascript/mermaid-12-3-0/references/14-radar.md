# Radar charts

Keyword: `radar-beta` (beta — the plain keyword may change before stable).

Sources: `docs/syntax/radar.md` at mermaid@12.3.0.

## Syntax

```
radar-beta
  title <optional title>
  axis <id>["label"], <id>["label"], ...
  curve <id>["label"]{v1, v2, ...}
  graticule polygon
  max <n>
  min <n>
```

- `axis` defines spokes; multiple axes per line. Labels optional (bare id or `id["Label"]`).
- `curve` plots one series per line; values align to the axes in order.
- `max`/`min` bound the scale.
- `graticule polygon` renders a polygon grid (verified form; other graticule values, if any, are not documented here).

```mermaid
---
title: "Grades"
---
radar-beta
  axis m["Math"], s["Science"], e["English"]
  axis h["History"], g["Geography"], a["Art"]
  curve a["Alice"]{85, 90, 80, 70, 75, 90}
  curve b["Bob"]{70, 75, 85, 80, 90, 85}

  max 100
  min 0
```

Restaurant comparison (docs):

```mermaid
radar-beta
  title Restaurant Comparison
  axis food["Food Quality"], service["Service"], price["Price"]
  axis ambiance["Ambiance"]

  curve a["Restaurant A"]{4, 3, 2, 4}
  curve b["Restaurant B"]{3, 4, 3, 3}
  curve c["Restaurant C"]{2, 3, 4, 2}
  curve d["Restaurant D"]{2, 2, 4, 3}

  graticule polygon
  max 5
```
