---
name: vega-lite-6-4-3
description: >
  Vega-Lite is a high-level grammar for interactive graphics — a concise JSON syntax for creating
  data visualizations. Use this skill whenever the user mentions Vega-Lite, chart specifications,
  JSON-based charts, declarative visualization, or wants to create bar charts, line charts, scatter
  plots, heatmaps, pie charts, area charts, boxplots, trellis/facet charts, layered compositions,
  geographic maps, or any data visualization using the Vega-Lite specification format (v6.4.3).
  Also use when the user asks about encoding channels (x, y, color, size, shape, theta, radius),
  mark types, transforms, aggregations, binning, time units, selections/interactions, or embedding
  Vega-Lite charts in web applications.
metadata:
  tags:
    - visualization
    - charts
    - data-graphics
---

# vega-lite 6.4.3

## Overview

Vega-Lite is a high-level grammar of graphics that compiles to vega/vega-lite specifications. It provides a concise JSON syntax for creating interactive multi-view visualizations. A Vega-Lite spec describes *what* the chart should show — the compiler figures out *how* to render it.

Vega-Lite supports the following chart types via its mark system: **bar**, **line**, **area**, **circle**, **point**, **square**, **tick**, **trail**, **rect** (heatmaps), **arc** (pie/donut), **rule**, **text**, **geoshape** (maps), and **image** as primitive marks, plus **boxplot**, **errorbar**, and **errorband** as composite marks. These combine with encoding channels and composition operators (`layer`, `facet`, `concat`, `hconcat`, `vconcat`, `repeat`) to cover virtually any chart or visualization pattern.

### Core Concepts

- **Data** — Inline values, URL references, or external data sources
- **Mark** — Visual primitive: `bar`, `line`, `circle`, `point`, `rect`, `area`, `arc`, `text`, `rule`, `square`, `tick`, `trail`, `geoshape`, `image`. Composite marks: `boxplot`, `errorband`, `errorbar`
- **Encoding** — Map data fields to visual channels: `x`, `y`, `color`, `size`, `shape`, `theta`, `radius`, `text`, `opacity`, `detail`, `order`, `key`, `href`, `latitude`, `longitude`, `row`, `column`, `facet`
- **Transform** — Pre-processing: `filter`, `calculate`, `bin`, `aggregate`, `joinaggregate`, `window`, `flatten`, `fold`, `timeUnit`, `sequence`
- **Composition** — Combine specs: `layer`, `facet` (via row/column encoding), `concat`, `hconcat`, `vconcat`, `repeat`
- **Projection** — Geographic projections for map visualizations
- **Selection** — Interactive brushing, clicking, and parameter binding

### Data Types

Vega-Lite recognizes four data types for encoding channels:

| Type | Description | Example |
|---|---|---|
| `quantitative` | Continuous numeric values | temperature, price, count |
| `ordinal` | Ordered categories | rank, size class, binned values |
| `nominal` | Unordered categories | name, origin, category |
| `temporal` | Date/time values | date, timestamp, year-month |

### Mark Types at a Glance

| Primitive Marks | Composite Marks |
|---|---|
| `bar`, `line`, `circle`, `point`, `rect`, `area`, `arc`, `text`, `rule`, `square`, `tick`, `trail`, `geoshape`, `image` | `boxplot`, `errorband`, `errorbar` |

## Usage

### Validation

Every Vega-Lite spec you write **must** be validated with `vega-lite.sh` before it is considered final. If validation reports errors, fix them and re-validate until the spec passes cleanly. Never leave an invalid spec in a file.

`vega-lite.sh` is the **only** way to validate Vega-Lite specs. Do not use online validators, manual schema checks, or any other tool.

```bash
# Validate a markdown file (checks all ```vega-lite blocks)
vega-lite.sh validate <file.md>

# Validate a directory recursively
vega-lite.sh validate references/

# Validate from stdin
echo '{"$schema":"...","data":{"values":[]},"mark":"bar"}' | vega-lite.sh validate -
```

`vega-lite.sh` loads the local v6.4.3 JSON schema for strict validation. It extracts `vega-lite` code blocks from markdown, parses the JSON, and reports any schema violations with instance paths and error messages.

### Creating a Spec

Minimal valid spec structure:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Chart description",
  "data": {"values": [{"a": "A", "b": 28}]},
  "mark": "bar",
  "encoding": {
    "x": {"field": "a", "type": "nominal"},
    "y": {"field": "b", "type": "quantitative"}
  }
}
```

**Output context matters:**

- **In Markdown** — always wrap the spec in a `vega-lite` fenced code block (```` ```vega-lite ````). This is how `vega-lite.sh validate` extracts specs from `.md` files.
- **In `.json` files** — write the spec as a raw JSON object. No code fences, no markdown wrapping. The file must be valid JSON when parsed.

## Gotchas

- **Markdown vs JSON output** — In markdown, always use ` ```vega-lite ` fenced blocks. In `.json` files, dump the spec as raw JSON (no fences). A `.json` file containing markdown fences is not valid JSON.
- **Always include `$schema`** — Omitting it means `vega-lite.sh validate` cannot determine the spec version. Use `https://vega.github.io/schema/vega-lite/v6.json` for v6.x compatibility.
- **Data must be accessible at runtime** — Specs using `"url"` for data need a running server or public URL. For validation and portability, use inline `"values"` arrays.
- **Mark vs mark definition** — `"mark": "bar"` is shorthand; `"mark": {"type": "bar", "tooltip": true}` is the full object form. Use the object form when customizing mark properties like `filled`, `cornerRadius`, or `aria`.
- **Encoding channels override mark properties** — If you set `color` in encoding, it overrides any `color` property in the mark definition.
- **Aggregation requires compatible types** — `aggregate: "mean"` on a nominal field is invalid. Aggregations like `sum`, `mean`, `count` work on quantitative fields; `count` works on any type.
- **Stacking is automatic for bar/area** — When a nominal/ordinal channel is mapped to `color` with `bar` or `area` marks, Vega-Lite stacks by default. Use `stack: null` to disable.
- **Time units need temporal fields** — `timeUnit: "yearmonth"` requires the field type to be `temporal`.
- **Composite marks are syntactic sugar** — `boxplot`, `errorband`, and `errorbar` compile to layered specs with multiple primitive marks. They have special mark properties (e.g., `extent`, `borders`).
- **Facet vs concat** — `row`/`column` encodings create faceted views sharing data; `concat`/`hconcat`/`vconcat` compose independent specs side-by-side.
- **`repeat` uses `{"repeat": "repeat"}` field reference** — In repeat specs, reference the repeated dimension with `{"repeat": "repeat"}` in encoding fields.
- **`vega-lite.sh validate` only extracts fenced blocks** — When validating markdown, it looks for `vega-lite` fenced code blocks. Plain JSON embedded without fences in `.md` files will be silently skipped.

## References

Each reference file covers one mark type or composition pattern with syntax rules and validated examples:

- [01-bar.md](references/01-bar.md) — Bar charts: simple, stacked, grouped, horizontal, aggregated, binned, corner radius, normalized
- [02-line.md](references/02-line.md) — Line charts: simple, multi-series, with points, temporal, time unit, dashed, slope
- [03-area.md](references/03-area.md) — Area charts: simple, stacked, y2 range, normalized, layered with line overlay
- [04-circle.md](references/04-circle.md) — Circle marks: scatter plots, colored, bubble charts, binned 2D histogram, dot plots
- [05-point.md](references/05-point.md) — Point marks: simple, shape encoding, filled, 1D distribution
- [06-rect.md](references/06-rect.md) — Rect marks: heatmaps, binned 2D histogram, with text labels, mosaic
- [07-arc.md](references/07-arc.md) — Arc marks: pie charts, donut, with labels, radial histogram
- [08-rule.md](references/08-rule.md) — Rule marks: vertical references, diagonal ranges, bar annotations, slope lines
- [09-square.md](references/09-square.md) — Square marks: scatter plots, colored with size, filled
- [10-text.md](references/10-text.md) — Text marks: labels, bar value labels, formatted colored text, scatter with labels
- [11-tick.md](references/11-tick.md) — Tick marks: 1D distribution, grouped by category, histogram, horizontal strip
- [12-trail.md](references/12-trail.md) — Trail marks: variable-width lines, comet charts, multi-series
- [13-boxplot.md](references/13-boxplot.md) — Boxplots: vertical, horizontal, with color, custom extent
- [14-errorbar.md](references/14-errorbar.md) — Error bars: auto-computed CI, with points, horizontal, custom extent (stdev)
- [15-errorband.md](references/15-errorband.md) — Error bands: auto-computed CI, with line overlay, horizontal, borders + stdev
- [16-geoshape.md](references/16-geoshape.md) — Geo shapes: choropleth, world map with projection, with circle overlay
- [17-image.md](references/17-image.md) — Image marks: simple placement, scatter, with tooltips
- [18-layer.md](references/18-layer.md) — Layered specs: bar+line overlay, scatter+regression, dual axis, histogram+mean
- [19-facet.md](references/19-facet.md) — Faceted specs: column facet, row facet, row+column grid, independent scales
- [20-concat.md](references/20-concat.md) — Concatenated specs: hconcat, vconcat, nested 2x2 grid, shared data reference
- [21-repeat.md](references/21-repeat.md) — Repeat specs: column repeat, row repeat, row+column grid, with layers
- [22-embedding.md](references/22-embedding.md) — Embedding in web apps: vega-embed CDN, options, programmatic access
