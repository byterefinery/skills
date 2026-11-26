---
name: vega-lite-6-5-0
description: Vega-Lite (v6.5.0) is a concise JSON grammar for interactive data visualization that compiles to Vega specs. Covers marks, encoding channels, data sources, transforms, layered and faceted composition, and selections and parameters. Use when writing or debugging a Vega-Lite spec, embedding charts with vegaEmbed, compiling to Vega/SVG/PNG/PDF via vegaLite.compile or the vl2* CLI tools, or adding interactive selections.
license: BSD-3-Clause
compatibility: Requires the vega-lite npm package plus the vega ^6.4.0 peer dependency for rendering; the vl2* CLI tools need Node >= 22
metadata:
  tags:
    - javascript
    - data-visualization
    - vega
---

# vega-lite 6.5.0

## Overview

Vega-Lite (v6.5.0, BSD-3-Clause) is a concise, high-level JSON grammar for interactive data visualization. A Vega-Lite specification describes marks, encodings, data, transforms, and composition; the compiler turns it into a full [Vega](https://vega.github.io/vega) specification that Vega renders. The compiler automatically generates scales, axes, and legends from the mark + encoding, so specs stay succinct — but every component can be overridden.

Official docs: https://vega.github.io/vega-lite/docs/ · examples: https://vega.github.io/vega-lite/examples/ · try it in the [Vega Editor](https://vega.github.io/editor/#/examples/vega-lite/bar)

## Usage

### Spec anatomy

```js
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A simple bar chart with embedded data.",
  "data": {
    values: [
      {a: 'A', b: 28}, {a: 'B', b: 55}, {a: 'C', b: 43},
      {a: 'D', b: 91}, {a: 'E', b: 81}, {a: 'F', b: 53},
      {a: 'G', b: 19}, {a: 'H', b: 87}, {a: 'I', b: 52}
    ]
  },
  "mark": "bar",
  "encoding": {
    x: {field: 'a', type: 'ordinal'},
    y: {field: 'b', type: 'quantitative'}
  }
}
```

Property scope:

- **All view specs** — `name`, `description`, `title`, `data`, `transform`, `params`. Composition specs additionally take `resolve`; layout compositions (`facet`, `concat`, `repeat`) also take `align`, `bounds`, `center`, `spacing`.
- **Top-level only** — `$schema`, `background`, `padding`, `autosize`, `config`, `usermeta`.
- **Single views** — `width`, `height`, `mark`, `encoding`, `view` (view background), `projection`.

### Marks

Primitive marks: `area`, `bar`, `circle`, `line`, `point`, `rect`, `rule`, `text`, `tick`, `geoshape`. Composite marks (macros of layered primitives): `boxplot`, `errorband`, `errorbar`. `mark` is either a type string or a definition object (`{type, ...properties}`); mark properties set in encoding channels override the definition.

### Encoding channels

`encoding` maps data fields, constant visual values, or constant data values (datum) onto channels:

- **Position** — `x`, `y`, `x2`, `y2`, `xError`, `yError`, `xError2`, `yError2` (+ offset channels `xOffset`, `yOffset`)
- **Polar** — `theta`, `theta2`, `radius`, `radius2` (for `arc`, `text`)
- **Geographic** — `longitude`, `latitude`, `longitude2`, `latitude2`
- **Mark properties** — `angle`, `color` (and `fill`/`stroke`), `opacity`, `fillOpacity`, `strokeOpacity`, `shape`, `size`, `strokeDash`, `strokeWidth`
- **Text and tooltip** — `text`, `tooltip`
- **Others** — `href` (hyperlinks), `description` (ARIA), `detail` (grouping), `key` (object constancy), `order` (stack/line/zorder), `facet`/`row`/`column` (faceting)

Each channel definition is a **field definition** (`{field, type, ...}`), a **value definition** (`{value}` — constant visual value), or a **datum definition** (`{datum}` — constant data value through the scale). Full per-channel properties in [01-encoding-channels](references/01-encoding-channels.md).

### Data

`data` accepts inline `values`, a `url` (format inferred from extension; `json`, `csv`, `tsv`, `dsv`, `topojson`), a `name` (empty source bound at runtime via the Vega View API), or generators (`sequence`, `graticule`, `sphere`). A top-level `datasets` map lets one inline table feed several named sources. Details in [02-data-and-transforms](references/02-data-and-transforms.md).

### Transforms

View-level `transform` is an array executed in order; inline field transforms inside `encoding` run after, in the fixed order `bin` → `timeUnit` → `aggregate` → `sort` → `stack`. Supported ops: `aggregate`, `bin`, `calculate`, `density`, `extent`, `filter`, `flatten`, `fold`, `impute`, `joinaggregate`, `lookup`, `pivot`, `quantile`, `regression`, `loess`, `sample`, `stack`, `timeunit`, `window`. New in 6.5.0 — parameterized **`exponential` / `exponentialb`** (exponential moving average) aggregate ops, written as objects like `{"exponential": 0.5}`.

### Composition

- **`layer`** — stack views; scale domains are unioned, axes/legends combined. Operands are restricted to single or layered views.
- **`facet`** — partition data into small multiples (shortcut: `row`/`column` encoding channels).
- **`hconcat` / `vconcat`** — side-by-side views.
- **`repeat`** — replicate a view per field in an array (unlike `facet`, each view gets the full dataset).

Composition is hierarchical — dashboards are single specs. The compiler infers data reuse and whether scale domains are unioned; override with `resolve`.

### Parameters and selections

`params` is the grammar of interaction: **variable parameters** (`name`, `value`, optional `expr`, optional `bind` to a slider/dropdown) and **selection parameters** (`select` with `type: "point" | "interval"`), which map user input to data queries. Parameters are used in expression strings, as predicates in `condition`, and to drive data extents (bin extents, scale domains). Details in [03-parameters-and-selection](references/03-parameters-and-selection.md).

### Embedding and compiling

```sh
npm install vega vega-lite vega-embed
```

```html
<div id="vis"></div>
```

```js
vegaEmbed('#vis', yourVlSpec);
```

For programmatic access to the compiled Vega spec:

```js
const vgSpec = vegaLite.compile(vlSpec, { config, logger, fieldTitle }).spec;
```

CLI tools ship with the package — `vl2vg`, `vl2png`, `vl2svg`, `vl2pdf` (spec as first argument or via stdin; `npx -p vega -p vega-lite vl2png spec.vl.json` works without pre-installing). Details in [04-usage-and-cli](references/04-usage-and-cli.md).

## Gotchas

- **`$schema` must match the major** — v6 specs use `https://vega.github.io/schema/vega-lite/v6.json`.
- **`vega` is a peer dependency** — install it alongside `vega-lite` (and `vega-embed` for embedding); vega-lite alone only compiles.
- **CLI needs Node >= 22**, and Node rendering of PNG/SVG needs the `canvas` package when you hit `Error: CanvasRenderer is missing a valid canvas or context`.
- **Transform execution order** — view-level `transform`s run first, in array order; then inline field transforms in the fixed order `bin`, `timeUnit`, `aggregate`, `sort`, `stack`.
- **`x2`/`y2` (and `theta2`, `radius2`, geo `*2`) have no own `scale`/`axis`/`sort`/`stack`** — they share the base channel's.
- **Aggregation grouping** — unaggregated fields encoded in an aggregated plot become `GROUP BY` fields; use `detail` for grouping without a visual mapping (also groups `line`/`area` into multiple paths).
- **`layer` operands** must be single or layered views — you cannot layer a `facet`/`concat` on top of another view.
- **Empty selections contain all data by default** — set the `empty` property on the predicate to flip this.
- **Reserved parameter names** — `datum`, `item`, `event`, `parent` cannot be user-defined; `width`/`height`/`padding`/`autosize`/`background` are auto-defined and merged with top-level spec values.
- **Config precedence** — the spec's own `config` property overrides the `config` passed to `vegaLite.compile(spec, {config})`.
- **6.5.0 changes** — `exponential`/`exponentialb` aggregate ops take object parameters (`{"exponential": 0.5}`), and tooltip field-definition arrays support a `filter` predicate to omit individual fields at runtime.

## References

- [01-encoding-channels](references/01-encoding-channels.md) — channel groups, field/value/datum definitions, per-channel properties, conditions, tooltips
- [02-data-and-transforms](references/02-data-and-transforms.md) — data source types, formats, generators, datasets, and all view-level transforms
- [03-parameters-and-selection](references/03-parameters-and-selection.md) — variables, point/interval selections, expressions, predicates, data extents, built-in names
- [04-usage-and-cli](references/04-usage-and-cli.md) — vegaEmbed, `vegaLite.compile` options, `vl2*` CLI tools
